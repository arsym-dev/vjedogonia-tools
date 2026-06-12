from __future__ import annotations

import argparse
import glob
import shutil
from pathlib import Path


def encode_data(data: bytes) -> bytearray:
    out = bytearray()
    out.append(2)  # Magic number
    out.append(0)  # Placeholder for checksum

    local_10 = 11  # Initial key
    local_14 = 0   # Checksum accumulator

    for byte in data:
        if byte == 13:  # CR character - encode as one of the trigger bytes
            out.append(10)
        elif 32 <= byte <= 255:  # Range that gets XOR'd
            encoded = byte ^ local_10
            local_10 = (local_10 + byte) & 0x8000001F
            if local_10 < 0:
                local_10 = (local_10 - 1 | 0xFFFFFFE0) + 1
            out.append(encoded)
            local_14 += byte
        else:  # Bytes 0-9, 14-31 - pass through
            out.append(byte)

    # Calculate final checksum
    local_14 &= 0x800000FF
    if local_14 < 0:
        local_14 = (local_14 - 1 | 0xFFFFFF00) + 1

    # Write checksum to position 1
    out[1] = local_14
    return out


def output_path_for(input_path: Path) -> Path:
    if input_path.suffix.lower() == ".nps":
        return input_path.with_suffix(".cde")
    return Path(str(input_path) + ".cde")


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
                candidates = path.rglob("*.nps")
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


def encode_file(input_path: Path, create_backups: bool, backed_up: set[Path]) -> None:
    with input_path.open("rb") as f:
        data = f.read()

    out = encode_data(data)
    output_path = output_path_for(input_path)

    if create_backups and output_path.exists():
        maybe_backup_once(output_path, backed_up)

    with output_path.open("wb") as f:
        f.write(out)

    print(f"Encoded {input_path} -> {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Encode .nps files to .cde, with directory and glob support."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input files, directories, or glob patterns (for example: *.nps, data/**/*.nps)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_false",
        dest="create_backups",
        default=True,
        help="If output .cde exists, do not create a .bak backup before overwrite.",
    )

    args = parser.parse_args()
    files = expand_inputs(args.inputs)

    if not files:
        print("No input files found.")
        return 1

    backed_up: set[Path] = set()
    for file_path in files:
        encode_file(file_path, args.create_backups, backed_up)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
