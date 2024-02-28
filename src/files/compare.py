import os
import shutil
from pathlib import Path


def sync(src: Path, dest: Path):
    for src_file in src.iterdir():
        shutil.copy(src_file, dest)

    for dest_file in dest.iterdir():
        if not (src / dest_file.name).exists():
            os.remove(dest_file)
