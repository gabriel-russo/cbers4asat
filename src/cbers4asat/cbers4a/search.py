#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .collection import Collections
from .itemCollection import ItemCollection
from requests import Session, get
from os.path import join


class Search(object):
    """Simple class to search INPE STAC Catalog"""

    # INPE STAC Catalog
    base_url = "https://www.dgi.inpe.br/stac-compose/stac"
    base_url_search_item = "https://www.dgi.inpe.br/lgi-stac"
    collection_endpoint = "collections"
    search_endpoint = "search"

    def __init__(self):
        """
        Simple class to search INPE STAC Catalog.

            Parameters:
                str1 (str):The string which is to be reversed.

            Returns:
                reverse(str1):The string which gets reversed.
        """
        self.session = Session()
        self.providers_body = dict(name="LGI-CDSR", method="POST")
        self.request_body = dict(
            providers=[],
            fromCatalog="yes",
        )

    def __call__(self):
        """
        docstring
        """
        if "ids" in self.request_body:
            features = []
            for id_ in self.request_body["ids"]:
                r = self.session.get(
                    join(
                        self.base_url_search_item,
                        self.collection_endpoint,
                        self.request_body["collection"],
                        "items",
                        id_,
                    )
                )
                r.raise_for_status()
                if r.status_code == 200:
                    feat = r.json()
                    if feat.get("type") == "Feature":
                        features.append(feat)
            return ItemCollection({"type": "FeatureCollection", "features": features})
        else:
            r = self.session.post(
                join(self.base_url, self.search_endpoint), json=self.request_body
            )
            r.raise_for_status()
            if r.status_code == 200:
                collections = r.json()["LGI-CDSR"]  # Enter LGI-CDSR Collections
                feature_collection = {"type": "FeatureCollection", "features": []}
                for name, content in collections.items():
                    # Append all collection features in one
                    feature_collection["features"].extend(content["features"])
                return ItemCollection(feature_collection)

    def update(self, **search_keys):
        """
        docstring
        """
        self.request_body.update(search_keys)

    def clear(self):
        """
        docstring
        """
        self.request_body = dict()

    def close(self):
        """
        docstring
        """
        self.session.close()
        self.session = None

    def providers(self, **search_keys):
        """
        docstring
        """
        self.providers_body.update(search_keys)
        self.request_body.update(providers=[self.providers_body])

    def query(self, **properties_keys):
        """
        docstring
        """
        self.providers(query=properties_keys)

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
        self.update(datetime=f"{start}T00:00:00/{end}T23:59:00")

    def intersects(self, intersects):
        """
        Only for future. Today, INPE-STAC does not support this feature.
        """
        self.update(intersects=intersects)

    def collections(self, collections):
        """
        docstring
        """
        if isinstance(collections, str):
            self.request_body.update(collection=collections)
        else:
            self.providers(
                collections=[{"name": collection} for collection in collections]
            )

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
