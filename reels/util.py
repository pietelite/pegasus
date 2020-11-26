from typing import List
from uuid import UUID


# Helper function to put UUID into a basic string of hex characters
def uuid_to_str(uuid: UUID) -> str:
    return str(uuid).replace('-', '')


# Helper function to put a basic string of hex characters into a UUID
def str_to_uuid(s: str) -> UUID:
    return UUID('{}-{}-{}-{}-{}'.format(s[0:8], s[8:12], s[12:16], s[16:20], s[20:32]))

# === File Util ===


# Gets the file type of this file name, e.g. 'mp4'
def get_file_type(file_name: str):
    if '.' not in file_name:
        raise ValueError(f'The file "{file_name}" does not have a discernible file type')
    return file_name.split('.')[-1]


# Checks if a file is of a given type (i.e. is_file_type("output.mp4", "mp4") -> True)
def is_file_type(file_name: str, file_type: str) -> bool:
    return get_file_type(file_name) == file_type


# Checks if a file is supported from a list of supported list
def is_file_supported(file_name: str, type_list: List[str]) -> bool:
    return bool([file_type for file_type in type_list if is_file_type(file_name, file_type)])
