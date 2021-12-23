from enum import Enum
from mabel.errors import UnsupportedTypeError
import datetime


def coerce(var):
    """
    Relations only support a subset of types, if we know how to translate a type
    into a supported type, do it.
    """
    t = type(var)
    if t in (int, float, tuple, bool, str, datetime.datetime, dict):
        return var
    if t in (list, set):
        return tuple(var)
    if t in (datetime.date,):
        return datetime.datetime(t.year, t.month, t.day)
    if var is None:
        return var
    raise UnsupportedTypeError(
        f"Attributes of type `{t}` are not supported - the value was `{var}`"
    )


class MABEL_TYPES(str, Enum):
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    DOUBLE = "DOUBLE"
    LIST = "LIST"
    VARCHAR = "VARCHAR"
    STRUCT = "STRUCT"
    TIMESTAMP = "TIMESTAMP"
    OTHER = "OTHER"


PYTHON_TYPES = {
    "bool": MABEL_TYPES.BOOLEAN,
    "datetime": MABEL_TYPES.TIMESTAMP,
    "dict": MABEL_TYPES.STRUCT,
    "int": MABEL_TYPES.INTEGER,
    "float": MABEL_TYPES.DOUBLE,
    "str": MABEL_TYPES.VARCHAR,
    "tuple": MABEL_TYPES.LIST,
}

COERCABLE_PYTHON_TYPES = {
    "bool": MABEL_TYPES.BOOLEAN,
    "datetime": MABEL_TYPES.TIMESTAMP,
    "date": MABEL_TYPES.TIMESTAMP,
    "dict": MABEL_TYPES.STRUCT,
    "int": MABEL_TYPES.INTEGER,
    "float": MABEL_TYPES.DOUBLE,
    "str": MABEL_TYPES.VARCHAR,
    "tuple": MABEL_TYPES.LIST,
    "set": MABEL_TYPES.LIST,
    "list": MABEL_TYPES.LIST,
}


def get_coerced_type(python_type):
    if python_type in COERCABLE_PYTHON_TYPES:
        return COERCABLE_PYTHON_TYPES[python_type].name
    return f"unknown ({python_type})"
