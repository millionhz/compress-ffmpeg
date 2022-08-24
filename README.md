# Compress-FFMPEG

Compress video directories with ffmpeg

## Installation

- Download [ffmpeg binaries](https://www.ffmpeg.org/download.html).
- Add binaries to PATH.

## Usage

```shell
usage: compress.py [-h] [-c CRF] [-s SCALE] [-i [INCLUDE ...]] dir

Compress video directory

positional arguments:
  dir                   directory to compress

options:
  -h, --help            show this help message and exit
  -c CRF, --crf CRF     ffmpeg crf argument (default: 24)
  -s SCALE, --scale SCALE
                        height for scaling resolution
  -i [INCLUDE ...], --include [INCLUDE ...]
                        files to copy into the compressed directory (example: *.html *.pdf)
```

## Example

```shell
 python .\compress.py ".\Videos" --crf 24 -s 720
```