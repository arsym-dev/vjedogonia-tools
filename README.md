<img src="https://img.shields.io/badge/license-Apache%202.0-green"> <img src="https://img.shields.io/badge/python-v3-blue">

Tools to process files for the NITRO PLUS visual novel _[Vampirdzhija Vjedogonia](https://vndb.org/v433)_.

## Table of Contents <!-- omit in toc -->

- [Requirements](#requirements)
- [Usage](#usage)
  - [Archives (PCK)](#archives-pck)
  - [Images (NPI)](#images-npi)
  - [Scripts (CDE)](#scripts-cde)
- [File Format Headers](#file-format-headers)
  - [PCK Header](#pck-header)
    - [FileInfo entry](#fileinfo-entry)
  - [NPI Header](#npi-header)
  - [Credits](#credits)

# Requirements

- Python 3 (developed with 3.9)

# Usage

## Archives (PCK)

PCK files are the archive files containing images, audio, and/or script files.

To extract or build PCK file, open a terminal and run the following command:

```bash
# EXTRACT: If given a PCK file, it will extract data to a folder with the same name
python nitro_pck.py path/to/file.pck

# BUILD: If given a folder, it will create a PCK file using the contents of the file
python nitro_pck.py path/to/directory
```

Note that when you extract data, a file called `_list.txt` will be created. **DO NOT DELETE OR MODIFY \_list.txt** as this file is used to pack the files in the correct order within the archive.

## Images (NPI)

NPI files are bitmap images. They may or may not be compressed.

To convert NPI files to PNG images and back, use the following commands:

```bash
# NPI -> PNG
python npi2img.py path/to/file1 [path/to/file2...]

# Image -> NPI
python img2npi.py path/to/file1 [path/to/file2...]

```

## Scripts (CDE)

CDE files contain the script of the game. They control the dialogue, sprites, music, transtions, etc.

To decrypt CDE files, use the following command:

```bash
python script_decode.py path/to/script.cde
```

# File Format Headers

## PCK Header

| Offset   | Size | Type       | Description                |
| -------- | ---- | ---------- | -------------------------- |
| 0x00     | 4    | int        | File count                 |
| 0x04     | 4    | int        | (H) Size of FileInfo table |
| 0x08     | 4    | short      | Unknown                    |
| 0x0A     | 2    | short      | Unknown                    |
| 0x0C     | 2    | FileInfo[] | FileInfo table             |
| 0x0C + H | 4    | string[]   | Filename table             |

### FileInfo entry

| Offset | Size | Type | Description     |
| ------ | ---- | ---- | --------------- |
| 0x00   | 4    | int  | Address to data |
| 0x04   | 4    | int  | Data size       |
| 0x08   | 4    | int  | Unknown         |
| 0x0A   | 4    | int  | Unknown         |

## NPI Header

| Offset | Size | Type  | Description  |
| ------ | ---- | ----- | ------------ |
| 0x00   | 32   | int[] | Zeros        |
| 0x20   | 4    | int   | Unknown (1)  |
| 0x24   | 4    | int   | NPI type     |
| 0x28   | 4    | int   | Image height |
| 0x2A   | 4    | int   | Image width  |
| 0x30   | 4    | int   | Image size   |
| 0x34   | 12   | int   | Zeros        |

NPI type:

- **0x03**: 24 bit colors (RGB)
- **0x04**: 32 bit colors (RGBA)
- **0x23**: 24 bit colors (RGB) - Compressed

## Credits

This project was made in collaboration with Fernand
