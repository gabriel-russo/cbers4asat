#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .item import Item


class ItemCollection(object):
    """Class to parse json from INPE STAC Catalog"""

    def __init__(self, data):
        self._data = data

    @property
    def returned(self):
        return self._data["context"]["returned"]

    @property
    def matched(self):
        return self._data["context"]["matched"]

    @property
    def limit(self):
        return self._data["context"]["limit"]

    @property
    def complete(self):
        return self._data["context"]["returned"] == self._data["context"]["matched"]

    @property
    def featurescollection(
        self,
    ):  # FeaturesCollection GeoJSON ? ['type', 'id', 'geometry', 'bbox', 'properties']
        return {
            "type": "FeatureCollection",
            "features": list(
                self.features(
                    "type",
                    "id",
                    "collection",
                    "geometry",
                    "bbox",
                    "properties",
                    "assets",
                )
            ),
        }

    def items(self):
        for feat in self._data["features"]:
            yield Item(feat)

    def features(self, *keys):
        keys = list(
            filter(
                lambda k: k
                in [
                    "type",
                    "id",
                    "collection",
                    "geometry",
                    "bbox",
                    "properties",
                    "assets",
                    "links",
                ],
                keys,
            )
        )
        if keys:
            for feat in self._data["features"]:
                yield {key: feat[key] for key in keys}
        else:
            for feat in self._data["features"]:
                yield feat

    def __len__(self):
        return self._data["context"]["returned"]

    def __getitem__(self, k):
        """
        docstring
        """
        try:
            return Item(next(filter(lambda i: i["id"] == k, self._data["features"])))
        except StopIteration:
            raise KeyError(k)

    def __contains__(self, k):
        """
        docstring
        """
        if isinstance(k, Item):
            return any(i["id"] == k.id for i in self._data["features"])
        else:
            return any(i["id"] == k for i in self._data["features"])

    def __iter__(self):
        """
        docstring
        """
        return self.items()
