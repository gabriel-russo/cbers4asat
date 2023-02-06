#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .collection import Collections
from .itemCollection import ItemCollection
from requests import Session, get


class Search(object):
    """Simple class to search INPE STAC Catalog"""

    # INPE STAC Catalog
    base_url = "http://www2.dgi.inpe.br/inpe-stac"
    collection_endpoint = "/collections"
    search_endpoint = "/search"

    # http
    # timeout = 12

    def __init__(self, **default_search_keys):
        """
        Simple class to search INPE STAC Catalog.

            Parameters:
                str1 (str):The string which is to be reversed.

            Returns:
                reverse(str1):The string which gets reversed.
        """
        self.session = Session()
        self._default_search_keys = default_search_keys
        self.search_keys = dict()
        self.update(**default_search_keys)

    def __call__(self, **search_keys):
        """
        docstring
        """
        query_keys = search_keys.pop("query", None)
        if query_keys is not None:
            self.query(**query_keys)
        self.update(**search_keys)
        if "ids" in self.search_keys:
            features = []
            for id_ in self.search_keys["ids"]:
                r = self.session.get(
                    self.base_url + self.collection_endpoint + "/X/items/" + id_
                )
                r.raise_for_status()
                if r.status_code == 200:
                    feat = r.json()
                    if feat["type"] == "Feature":
                        features.append(feat)
            return ItemCollection({"type": "FeatureCollection", "features": features})
        else:
            r = self.session.post(
                self.base_url + self.search_endpoint, json=self.search_keys
            )
            r.raise_for_status()
            if r.status_code == 200:
                return ItemCollection(r.json())

    def update(self, **search_keys):
        """
        docstring
        """
        self.search_keys.update(search_keys)

    def defaults(self):
        """
        docstring
        """
        self.update(**self._default_search_keys)

    def clear(self):
        """
        docstring
        """
        self.search_keys = dict()

    def close(self):
        """
        docstring
        """
        self.session.close()
        self.session = None

    def query(self, **properties_keys):
        """
        docstring
        """
        if "query" in self.search_keys:
            self.search_keys["query"].update(properties_keys)
        else:
            self.search_keys.update({"query": properties_keys})

    def bbox(self, bbox: list) -> None:
        """
        Only features that have a geometry that intersects the bounding box are selected

            Parameters:
                bbox (list): The bounding box provided as a list of four floats,
                minimum longitude, minimum latitude, maximum longitude and maximum latitude.
        """
        self.update(bbox=bbox)

    def interval(self, interval):
        """
        docstring
        """
        self.update(datetime=interval)

    def date(self, start, end):
        """
        docstring
        """
        self.update(datetime=f"{start}T00:00:00Z/{end}T23:59:00Z")

    def intersects(self, intersects):
        """
        Only for future. Today, INPE-STAC does not support this feature.
        """
        self.update(intersects=intersects)

    def collections(self, collections):
        """
        docstring
        """
        self.update(collections=collections)

    def ids(self, ids):
        """
        docstring
        """
        self.update(ids=ids)

    def limit(self, limit):
        """
        docstring
        """
        self.update(limit=limit)

    def path_row(self, path, row):
        """
        docstring
        """
        self.query(path={"eq": path}, row={"eq": row})

    def cloud_cover(self, op, cloud_cover):
        """
        docstring
        """
        stac_op = {">=": "gte", "<=": "lte", "=": "eq", ">": "gt", "<": "lt"}
        try:
            self.query(cloud_cover={stac_op[op]: cloud_cover})
        except KeyError:
            pass

    @property
    def closed(self):
        """
        docstring
        """
        return self.session is None

    @staticmethod
    def get_collections():
        """
        docstring
        """
        with get(url=Search.base_url + Search.collection_endpoint) as res:
            if res.status_code == 200:
                return Collections(res.json())
