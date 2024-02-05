import pathlib
from pathlib import Path
import shutil
import os


def sync(src: Path, dest: Path):

    for src_file in src.iterdir():
        shutil.copy(src_file, dest)

    for dest_file in dest.iterdir():
        if not (src / dest_file.name).exists():
            os.remove(dest_file)

