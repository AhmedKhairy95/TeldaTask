from exceptions.custom_exceptions import FileReaderFactoryException
from file_reader.file_reader import FileReader
from file_reader.json_file_reader import JsonFileReader
from file_reader.yaml_file_reader import YAMLFileReader
from settings import Settings


class FileReaderFactory:
    @staticmethod
    def get_instance(settings: Settings, file_extension='json') -> FileReader:
        if file_extension is not None and file_extension.lower().strip() in settings.SUPPORTED_EXTENSIONS:
            if file_extension.lower().strip() == 'json':
                return JsonFileReader()
            elif file_extension.lower().strip() == 'yaml' or file_extension.lower().strip() == 'yml':
                return YAMLFileReader()
        else:
            raise FileReaderFactoryException(
                extension=file_extension.lower().strip() if file_extension is not None else None,
                supported_file_extensions=settings.SUPPORTED_EXTENSIONS)
