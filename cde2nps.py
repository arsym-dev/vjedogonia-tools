from __future__ import annotations

import argparse
import glob
import shutil
from pathlib import Path


def decode_data(data: bytes) -> tuple[bytearray, bool]:
    if len(data) == 0:
        raise ValueError("data is empty")

    if data[0] != 2:
        raise ValueError("Invalid file format")

    checksum = data[1]
    payload = data[2:]

    out = bytearray()
    local_10 = 11  # Initial key
    local_14 = 0   # Checksum accumulator

    for byte in payload:
        if byte - 10 < 4:  # Bytes 10-13 -> CR (original logic preserved)
            out.append(13)
        elif byte - 32 < 224:  # Range 32-255 gets XOR'd
            decoded = byte ^ local_10
            local_10 = (local_10 + decoded) & 0x8000001F
            if local_10 < 0:
                local_10 = (local_10 - 1 | 0xFFFFFFE0) + 1
            out.append(decoded)
            local_14 += decoded
        else:  # Pass through
            out.append(byte)

    local_14 &= 0x800000FF
    if local_14 < 0:
        local_14 = (local_14 - 1 | 0xFFFFFF00) + 1

    checksum_ok = (checksum == local_14)
    return out, checksum_ok


def output_path_for(input_path: Path) -> Path:
    if input_path.suffix.lower() == ".cde":
        return input_path.with_suffix(".nps")
    return Path(str(input_path) + ".nps")


def expand_inputs(inputs: list[str]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()

    for item in inputs:
        matches = glob.glob(item, recursive=True)
        if not matches:
            matches = [item]

        for match in matches:
            path = Path(match)

            if path.is_dir():
                candidates = path.rglob("*.cde")
            elif path.is_file():
                candidates = [path]
            else:
                print(f"Skipping missing path/pattern: {item}")
                continue

            for candidate in candidates:
                resolved = candidate.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                files.append(candidate)

    return files


def maybe_backup_once(target: Path, backed_up: set[Path]) -> None:
    if target in backed_up:
        return

    backup_path = target.with_suffix(target.suffix + ".bak")
    if backup_path.exists():
        print(f"Backup already exists, leaving as-is: {backup_path}")
    else:
        shutil.copy2(target, backup_path)
        print(f"Created backup: {backup_path}")

    backed_up.add(target)


def decode_file(input_path: Path, create_backups: bool, backed_up: set[Path]) -> bool:
    with input_path.open("rb") as f:
        data = f.read()

    try:
        out, checksum_ok = decode_data(data)
    except ValueError as exc:
        print(f"Skipping {input_path}: {exc}")
        return False

    output_path = output_path_for(input_path)

    if create_backups and output_path.exists():
        maybe_backup_once(output_path, backed_up)

    with output_path.open("wb") as f:
        f.write(out)

    if not checksum_ok:
        print(f"Decoded {input_path} -> {output_path} (warning: checksum mismatch)")
    else:
        print(f"Decoded {input_path} -> {output_path}")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Decode .cde files to .nps, with directory and glob support."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input files, directories, or glob patterns (for example: *.cde, data/**/*.cde)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_false",
        dest="create_backups",
        default=True,
        help="If output .nps exists, do not create a .bak backup before overwrite.",
    )

    args = parser.parse_args()
    files = expand_inputs(args.inputs)

    if not files:
        print("No input files found.")
        return 1

    backed_up: set[Path] = set()
    ok_count = 0
    for file_path in files:
        if decode_file(file_path, args.create_backups, backed_up):
            ok_count += 1

    return 0 if ok_count > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
