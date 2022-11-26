from typing import List


class FileReaderFactoryException(Exception):
    def __init__(self, extension: str, supported_file_extensions: List[str]):
        super(FileReaderFactoryException, self).__init__(
            f"The following extension {extension} is not supported,"
            f" the only supported extensions are {supported_file_extensions}")


class DuplicateJobIdentifier(Exception):
    def __init__(self, identifier: str):
        super(DuplicateJobIdentifier, self).__init__(f"Job identifier {identifier} is duplicated")


class InvalidStartDateFormat(Exception):
    def __init__(self):
        super(InvalidStartDateFormat, self).__init__("The valid format is yyyy-mm-dd")


class InvalidValueDefined(Exception):
    def __init__(self, field_name: str, multiple: int):
        super(InvalidValueDefined, self).__init__(
            f"The value defined for {field_name} must be a multiple of {multiple}")


class SchedulerNotInitialized(Exception):
    def __init__(self):
        super(SchedulerNotInitialized, self).__init__("The scheduler wasn't launched")


class JobFetcherNotSupported(Exception):
    def __init__(self):
        super(JobFetcherNotSupported, self).__init__("This job fetcher type is not yet supported")
