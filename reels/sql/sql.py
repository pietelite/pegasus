from reels.sql.sql_handler import SqlHandlerInterface
from .postgresql import PostgreSqlHandler


def get_sql_handler() -> SqlHandlerInterface():
    return PostgreSqlHandler()
