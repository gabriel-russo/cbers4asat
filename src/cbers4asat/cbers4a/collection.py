#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Collections(object):
    """Simple class to parse collections json from INPE STAC"""

    def __init__(self, data):
        """
        docstring
        """
        self._data = data

    def __getitem__(self, k):
        """
        docstring
        """
        try:
            return next(filter(lambda i: i["id"] == k, self._data["collections"]))
        except StopIteration:
            raise KeyError(k)

    def __iter__(self):
        """
        docstring
        """
        for i in [
            (collection["id"], collection["description"])
            for collection in self._data["collections"]
        ]:
            yield i

    def get_spatial_extent(self, id):
        """
        docstring
        """
        return self.__getitem__(id)["extent"]["spatial"]

    def get_temporal_extent(self, id):
        """
        docstring
        """
        return self.__getitem__(id)["extent"]["temporal"]
