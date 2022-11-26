import os
import shutil
from typing import List


def create_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_target_function(path: str, function_name: str):
    return getattr(__import__(path, fromlist=[None]), function_name)


def get_files_in_directory(directory: str) -> List[str]:
    files = []
    for path in os.listdir(directory):
        # check if current path is a file
        if os.path.isfile(os.path.join(directory, path)):
            files.append(os.path.join(directory, path))
    return files


def count_files_in_dir(directory: str) -> int:
    return len(get_files_in_directory(directory=directory))


def clear_directory(directory: str) -> None:
    if os.path.exists(directory):
        shutil.rmtree(directory)
