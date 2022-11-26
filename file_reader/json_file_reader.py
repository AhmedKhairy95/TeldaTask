import json
from typing import Dict

from file_reader.file_reader import FileReader


class JsonFileReader(FileReader):
    def read_file(self, path: str) -> Dict:
        with open(path, 'r') as file:
            body = json.load(file)
        return body
