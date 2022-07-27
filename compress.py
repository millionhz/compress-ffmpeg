"""compress-ffmpeg

The script allows to compress video directories. Its mainly meant for compressing
courses that have a large number of lectures divided among many sub directories.

The script only works with absolute paths. (Relative paths only work when the script
file is in the same directory as the folder to be compressed)

Requirements:
- ffmpeg binaries (https://www.ffmpeg.org/download.html)
"""

from pathlib import Path
from subprocess import run
import argparse
from shutil import copyfile
from typing import Callable


def get_index(index_path: Path) -> int:
    """
    Retrieves and returns the index of current file form the index file.
    If the index file is not present the function makes it and returns 0.

    :param index_path: path to the index file
    :returns: current file index
    """
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            return int(f.read())
    except FileNotFoundError:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("0")
            return 0


def update_index(index_path: Path, val: int):
    """
    Updates index file with the passed value

    :param index_path: path to index file
    :param val: value to save in the index file
    """
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(str(val))


def compress_command(in_file: str, out_file: str,  crf: int, scaling: int, overwrite: bool) -> str:
    """
    Returns ffmepg compression command based on the passed in arguments

    :param in_file: path to input file
    :param out_file: path to output file
    :param crf: compression value (https://ffmpeg.org/ffmpeg-codecs.html#libx264_002c-libx264rgb)
    :returns: compression command
    """
    scaling_filter = f"-vf scale=-1:{scaling}"
    overwrite_option = "-y" if overwrite else ""

    return f"ffmpeg {overwrite_option} -i \"{in_file}\" {scaling_filter} -vcodec libx264 -crf {crf} \"{out_file}\""


def compress(file: Path, save_file_path: Path, crf: int, scaling: int, overwrite: bool):
    """
    Compresses the input file using ffmpeg binaries and subprocess module

    :param file: file to compress
    :param save_file_path: output file path
    :param crf: compression value (https://ffmpeg.org/ffmpeg-codecs.html#libx264_002c-libx264rgb)
    """
    completed_process = run(
        compress_command(str(file), str(save_file_path),
                         crf, scaling, overwrite),
        check=False
    )

    if completed_process.returncode:
        raise Exception(f"{file} failed to compress")


def _get_save_file_function(_base_path: Path, _save_path: Path) -> Callable[[Path], Path]:
    """
    Returns function that returns the output file path based on the save file directory
    and the original directory. The function ensures that the file structure of the 
    original directory and the compressed directory is the same.

    :param _base_path: file path of the base directory
    :param _save_path: file path of the save directory
    :returns: function to get the path of output file
    """
    def _function(file: Path) -> Path:
        return _save_path.joinpath(file.relative_to(_base_path))

    return _function


parser = argparse.ArgumentParser(description="Compress video directory")
parser.add_argument("dir", type=Path, help="directory to compress")
parser.add_argument("-c", "--crf", type=int, default=24,
                    help="ffmpeg crf argument (default: %(default)s)")
parser.add_argument("-s", "--scale", type=int, default=0,
                    help="height for scaling resolution")
parser.add_argument("-y", "--yes", action="store_true",
                    help="ffmpeg overwrite files")
parser.add_argument("-i", "--include", nargs="*", default=[], type=str,
                    help="files to copy into the compressed directory (example: *.html *.pdf)")
parsed_args = parser.parse_args()

base_dir = parsed_args.dir
crf = parsed_args.crf
scaling = parsed_args.scale
overwrite = parsed_args.yes
other_files = parsed_args.include

###################################################

if not base_dir.exists():
    raise FileNotFoundError(f"{base_dir} not found")

save_dir = base_dir.parent.joinpath(base_dir.name + "_compressed")
save_dir.mkdir(exist_ok=True)

get_save_file_path = _get_save_file_function(base_dir, save_dir)

files = base_dir.rglob("*")

# generate folder structure
for file in files:
    directory = get_save_file_path(file).parent

    if not directory.exists():
        directory.mkdir(parents=True)

index_file_path = base_dir.parent.joinpath("index")
index = get_index(index_file_path)
on_index_file = True

glob = list(base_dir.rglob("*.mp4"))
glob_len = len(glob)


for file in glob[index:]:
    print(f"{index+1} of {glob_len}")

    save_file = get_save_file_path(file)

    if not save_file.exists() or on_index_file:
        compress(file, save_file, crf, scaling, overwrite)
        on_index_file = False

    index += 1
    update_index(index_file_path, index)

index_file_path.unlink()

for extension in other_files:
    files = base_dir.rglob(extension)

    for file in files:
        save_file = get_save_file_path(file)

        if not save_file.exists():
            print(f"Copying {file}")
            copyfile(file, get_save_file_path(file))

# TODO: Remove overwrite from argparse and overwrite automatically on index
# TODO: Rename glob variables
