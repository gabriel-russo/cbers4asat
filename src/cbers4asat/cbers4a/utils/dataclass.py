# -*- coding: utf-8 -*-
from dataclasses import dataclass, asdict as dataclass_as_dict
from typing import Any


def ignore_extras(cls):
    """
    Decorator to Ignore extra arguments inside dataclass constructor.

    This will prevent this exception to raise. Example:
    - TypeError: __init__() got an unexpected keyword argument 'stac_version'

    """
    __original__init__ = cls.__init__

    def filter_extras(self, **kwargs) -> None:
        """
        docstring
        """
        __original__init__(
            self, **{k: v for k, v in kwargs.items() if k in self.__annotations__}
        )

    cls.__init__ = filter_extras
    return cls


@dataclass
class SerializationCapabilities:
    """
    Serialization methods to dataclass.
    """

    def __del_none(self, value: dict) -> list[dict] | dict[Any, dict] | dict:
        """
        Delete keys with the value None in a dictionary, recursively.
        """
        if isinstance(value, list):
            return [self.__del_none(x) for x in value if x is not None]
        elif isinstance(value, dict):
            return {
                key: self.__del_none(val)
                for key, val in value.items()
                if val is not None
            }
        else:
            return value

    def asdict(self, exclude_none: bool = False) -> dict:
        """
        Dataclass to dictionary serialization. With exclude none values option.
        """
        if exclude_none:
            return self.__del_none(dataclass_as_dict(self).copy())
        return dataclass_as_dict(self).copy()
