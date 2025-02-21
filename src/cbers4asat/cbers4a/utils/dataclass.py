# -*- coding: utf-8 -*-


def ignore_extras(cls):
    """
    Ignore extra fields in dataclass decorator.
    """
    __original__init__ = cls.__init__

    def filter(self, **kwargs):
        __original__init__(
            self, **{k: v for k, v in kwargs.items() if k in self.__annotations__}
        )

    cls.__init__ = filter
    return cls
