from uuid import UUID


# Helper function to put UUID into a basic string of hex characters
def uuid_to_str(uuid: UUID) -> str:
    return str(uuid).replace('-', '')


# Helper function to put a basic string of hex characters into a UUID
def str_to_uuid(s: str) -> UUID:
    return UUID('{}-{}-{}-{}-{}'.format(s[0:8], s[8:12], s[12:16], s[16:20], s[20:32]))