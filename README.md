# Compress directories with FFMPEG

## Installation

- Download [ffmpeg binaries](https://www.ffmpeg.org/download.html).
- Add binaries to PATH.

## Usage

```shell
usage: compress.py [-h] [-c CRF] [-i [INCLUDE ...]] dir

Compress video directory

positional arguments:
  dir                   directory to compress

options:
  -h, --help            show this help message and exit
  -c CRF, --crf CRF     ffmpeg crf argument
  -i [INCLUDE ...], --include [INCLUDE ...]
                        files to copy into the compressed directory
```

## Example

```shell
 python .\compress.py ".\Videos" --crf 24
```