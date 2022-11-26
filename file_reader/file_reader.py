from abc import abstractmethod, ABC


class FileReader(ABC):

    @abstractmethod
    def read_file(self, path: str):
        pass
