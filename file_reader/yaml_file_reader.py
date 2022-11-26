from typing import Dict

import yaml

from file_reader.file_reader import FileReader


class YAMLFileReader(FileReader):
    def read_file(self, path: str) -> Dict:
        with open(path, 'r') as file:
            body = yaml.safe_load(file)
        return body
