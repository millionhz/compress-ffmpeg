from pathlib import Path
from subprocess import run
import argparse
from shutil import copyfile
from typing import Callable


def get_index(index_path: Path) -> int:
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            return int(f.read())
    except FileNotFoundError:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("0")
            return 0


def update_index(index_path: Path, val: int):
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(str(val))


def compress_command(in_file: str, out_file: str,  crf: int) -> str:
    return f"ffmpeg -i \"{in_file}\" -vcodec libx264 -crf {crf} \"{out_file}\""


def compress(file: Path, save_file_path: Path, crf: int):
    completed_process = run(
        compress_command(str(file), str(save_file_path), crf),
        check=False
    )

    if completed_process.returncode:
        raise Exception(f"{file} failed to compress")


def _get_save_file_function(_base_path: Path, _save_path: Path) -> Callable[[Path], Path]:
    def _function(file: Path) -> Path:
        return _save_path.joinpath(file.relative_to(_base_path))

    return _function


parser = argparse.ArgumentParser(description="Compress video directory")
parser.add_argument("dir", type=Path, help="directory to compress")
parser.add_argument("-c", "--crf", type=int, default=24,
                    help="ffmpeg crf argument")
parser.add_argument("-i", "--include", nargs="*", default=[], type=str,
                    help="files to copy into the compressed directory")
parsed_args = parser.parse_args()

base_dir = parsed_args.dir
crf = parsed_args.crf
other_files = parsed_args.include

###################################################

if not base_dir.exists():
    raise FileNotFoundError(f"{base_dir} not found")

save_dir = base_dir.parent.joinpath(base_dir.name + "_compressed")
save_dir.mkdir(exist_ok=True)

get_save_file_path = _get_save_file_function(base_dir, save_dir)

files = base_dir.rglob("*")

for file in files:
    directory = get_save_file_path(file).parent

    if not directory.exists():
        directory.mkdir(parents=True)

index_file_path = base_dir.parent.joinpath("index")
index = get_index(index_file_path)

glob = list(base_dir.rglob("*.mp4"))
glob_len = len(glob)


for file in glob[index:]:
    print(f"{index+1} of {glob_len}")

    save_file = get_save_file_path(file)

    if not save_file.exists():
        compress(file, save_file, crf)

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
