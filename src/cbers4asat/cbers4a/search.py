# -*- coding: utf-8 -*-
# Standard Libraries
from datetime import date
from os.path import join
from typing import Union

# PyPi Packages
from requests import Session, HTTPError

# Local Modules
from .collections import Collections
from .request import (
    STACRequestBody,
    Providers,
    Collection,
    STACItemRequestBody,
)


class SearchItem:
    """
    Simple class to search Item inside INPE STAC Catalog
    """

    # INPE STAC search item in collection
    BASE_URL_SEARCH_ITEM: str = "https://www.dgi.inpe.br/lgi-stac/collections"

    def __init__(self):
        self.search_item_body: STACItemRequestBody = STACItemRequestBody()

    def __call__(self):
        features = list()
        with Session() as session:
            for id_ in self.search_item_body.ids:
                try:
                    response = session.get(
                        join(
                            self.BASE_URL_SEARCH_ITEM,
                            self.search_item_body.collection,
                            "items",
                            id_,
                        )
                    )
                    response.raise_for_status()
                    feature = response.json()
                    if feature.get("type") == "Feature":
                        features.append(feature)
                except HTTPError as err:
                    raise Exception(
                        f"{response.status_code} - ERROR searching {id_}. Reason: {response.reason}. Exception: {err}"
                    )

        return {"type": "FeatureCollection", "features": features}

    def ids(
        self, ids: list[str], collection: Union[str, Collections]
    ) -> None | Exception:
        """
        docstring
        """
        if not len(ids):
            raise Exception("Ids to search list cannot be empty.")
        elif not collection:
            raise Exception("Collection cannot be empty.")

        self.search_item_body.ids = ids
        self.search_item_body.collection = collection


class Search:
    """
    Simple class to search INPE STAC Catalog
    """

    # INPE STAC Catalog
    BASE_URL_SEARCH: str = "https://www.dgi.inpe.br/stac-compose/stac/search/"

    def __init__(self):
        self.stac_request_body = STACRequestBody()
        self.providers_body = Providers()

    def __call__(self) -> dict:
        """
        docstring
        """
        self.stac_request_body.providers.append(self.providers_body)
        with Session() as session:
            try:
                response = session.post(
                    self.BASE_URL_SEARCH,
                    json=self.stac_request_body.asdict(exclude_none=True),
                )
                response.raise_for_status()
                # Response Root Keys are the providers, like: "LGI-CDSR', "DATA-INPE"...
                # Get the only provider that will be supported by cbers4asat lib.
                collections = response.json().get("LGI-CDSR", None)
                # Second level of keys are the collections, like "AMAZONIA1_WFI_L2_DN".
                # Every collection will be grouped inside this variable bellow.
                feature_collection = {"type": "FeatureCollection", "features": []}

                if not collections:
                    return feature_collection

                # For every collection...
                for name, content in collections.items():
                    if not isinstance(content, dict):
                        continue

                    if not content.get("features", None):
                        continue

                    # Append all collection features in one
                    feature_collection["features"].extend(content["features"])
                return feature_collection
            except HTTPError as err:
                raise Exception(
                    f"{response.status_code} - ERROR in query. Reason: {response.reason}. Exception: {err}"
                )

    def bbox(self, bbox: list[float]) -> None | Exception:
        """
        Only features that have a geometry that intersects the bounding box are selected

            Parameters:
                bbox (list): The bounding box provided as a list of four floats,
                minimum longitude, minimum latitude, maximum longitude and maximum latitude.
        """
        if not len(bbox):
            raise Exception("Bounding box cannot be empty.")
        elif len(bbox) != 4:
            raise Exception(
                "Bounding box must have four float numbers representing the coordinates."
            )

        self.stac_request_body.bbox = bbox

    def date_interval(self, start: date, end: date) -> None:
        """
        docstring
        """
        if start > end:
            raise Exception("Initial date must be older than the end date.")

        self.stac_request_body.datetime = (
            f"{start.isoformat()}T00:00:00/{end.isoformat()}T23:59:00"
        )

    def collections(
        self, collections: Union[list[str], list[Collections]]
    ) -> None | Exception:
        """
        docstring
        """
        if not len(collections):
            raise Exception("Collections cannot be empty.")

        self.providers_body.collections = [
            Collection(name=collection) for collection in collections
        ]

    def limit(self, limit: int) -> None | Exception:
        """
        docstring
        """
        if limit <= 0:
            raise Exception("Limit value must be greater than 0.")
        self.stac_request_body.limit = limit

    def path_row(self, path: int, row: int) -> None | Exception:
        """
        docstring
        """
        if not path or not row:
            raise Exception("Path and/or row cannot be empty.")

        self.providers_body.query.path = dict(eq=path)
        self.providers_body.query.row = dict(eq=row)

    def cloud_cover(self, cloud_cover: int) -> None | Exception:
        """
        docstring
        """
        if cloud_cover < 0 or cloud_cover > 100:
            raise Exception("Cloud cover must be between 0 and 100.")
        self.providers_body.query.cloud_cover.update(lte=cloud_cover)
