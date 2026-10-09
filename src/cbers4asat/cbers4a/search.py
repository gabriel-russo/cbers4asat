# -*- coding: utf-8 -*-
from datetime import date
from typing import Union

from requests import HTTPError, Session

from .collections import Collections
from .types import (
    CollectionDict,
    FeatureCollectionDict,
    FeatureDict,
    STACRequestBodyDict,
)


class SearchItem:
    """
    Simple class to search Item inside INPE STAC Catalog
    """

    # INPE STAC search item in collection
    BASE_URL_SEARCH_ITEM: str = "https://www.dgi.inpe.br/lgi-stac/collections"

    def __init__(self) -> None:
        self.__ids = []
        self.__collection: str = ""

    def __call__(self) -> FeatureCollectionDict:
        """
        Make request using the search parameters.

        Return:
            GeoJson-like dictionary.
        Raise:
            ``Exception`` if any http error.
        """
        features: list[FeatureDict] = []

        with Session() as session:
            session.headers.update({"User-Agent": "cbers4asat (Python)"})

            for id_ in self.__ids:
                try:
                    response = session.get(
                        f"{self.BASE_URL_SEARCH_ITEM}/{self.__collection}/items/{id_}"
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

    def ids(self, ids: list[str]) -> None:
        """
        Id(s) to search inside a collection.

        Args:
            ids: Item id String or list of item id strings.

        Raise:
            ``ValueError`` if id(s) or collection is empty.
        """
        if not len(ids):
            raise ValueError("Ids to search list cannot be empty.")

        self.__ids = ids

    def collection(self, collection: str | Collections) -> None:
        """
        Collection to search.

        Args:
            collection: Collection name to search into as string or Collections Enum.

        Raise:
            ``ValueError`` if id(s) or collection is empty.
        """

        if not collection:
            raise ValueError("Collection cannot be empty.")

        self.__collection = str(collection)


class Search:
    """
    Simple class to search INPE STAC Catalog
    """

    # INPE STAC Catalog
    BASE_URL_SEARCH: str = "https://www.dgi.inpe.br/stac-compose/stac/search/"

    def __init__(self) -> None:
        # Attributes used to build the request
        self.__date: str = ""
        self.__cloud_cover: dict[str, dict[str, int]] = {}
        self.__bbox: list[float] = [-81, -37, -30, 11]  # Trust me bro
        self.__path_row: dict[str, dict[str, int]] = {}
        self.__datetime_interval: str = ""
        self.__limit: int = 0
        self.__collections: list[CollectionDict] = []

    def get_request_body(self) -> STACRequestBodyDict:
        """
        Build and return the full STAC request body based on current search parameters.

        Return:
            Dictionary representing the STAC search request body.
        """
        return {
            "bbox": self.__bbox,
            "fromCatalog": "yes",
            "limit": self.__limit,
            "datetime": self.__datetime_interval,
            "providers": [
                {
                    "method": "POST",
                    "name": "LGI-CDSR",
                    "query": self.__cloud_cover | self.__path_row,
                    "collections": self.__collections,
                }
            ],
        }

    def __call__(self) -> FeatureCollectionDict:
        """
        Make request using the search parameters.

        Return:
            GeoJson-like dictionary.
        Raise:
            ``Exception`` if any http error.
        """
        with Session() as session:
            session.headers.update({"User-Agent": "cbers4asat (Python)"})

            try:
                response = session.post(
                    self.BASE_URL_SEARCH,
                    json=self.get_request_body(),  # ty: ignore[invalid-argument-type]
                )

                response.raise_for_status()

                # Response Root Keys are the providers, like: "LGI-CDSR', "DATA-INPE"...
                # Get the only provider that will be supported by cbers4asat lib.
                collections: dict | None = response.json().get("LGI-CDSR", None)

                # Second level of keys are the collections, like "AMAZONIA1_WFI_L2_DN".
                # Every collection will be grouped inside this variable bellow.
                feature_collection: FeatureCollectionDict = {
                    "type": "FeatureCollection",
                    "features": [],
                }

                if collections is None:
                    return feature_collection

                # For every collection...
                for _, content in collections.items():
                    if not isinstance(content, dict):
                        continue

                    if content.get("features", None) is None:
                        continue

                    # Append all collection features in one
                    feature_collection["features"].extend(content["features"])

                return feature_collection
            except HTTPError as err:
                raise HTTPError(
                    f"{response.status_code} - ERROR in query. Reason: {response.reason}. Exception: {err}"
                )

    def bbox(self, bbox: list[float]) -> None:
        """
        Only products that have a geometry/footprint that intersects the bounding box are selected.

        Args:
            bbox: The bounding box provided as a list of four floats, minimum longitude, minimum latitude, maximum longitude and maximum latitude.

        Raise:
            ``ValueError`` if bbox list is empty or bbox coordinates is not float numbers or bbox does not have 4 coordinates.
        """
        if not len(bbox):
            raise ValueError("Bounding box cannot be empty.")

        if len(bbox) != 4:
            raise ValueError(
                "Bounding box must have four float numbers representing the coordinates."
            )

        if not all(isinstance(coord, float) for coord in bbox):
            raise ValueError("Bounding box coordinates must be float numbers.")

        self.__bbox = bbox

    def date_interval(self, start: date, end: date) -> None:
        """
        Search for scenes that was taken in this interval of dates.

        Args:
            start: Initial date. The older part of interval.
            end: End date. The most recent part of interval.

        Raise:
            ``ValueError`` if the start date is more recent than end date.
        """
        if start > end:
            raise ValueError("Initial date must be older than the end date.")

        self.__datetime_interval = (
            f"{start.isoformat()}T00:00:00/{end.isoformat()}T23:59:00"
        )

    def collections(self, collections: Union[list[str], list[Collections]]) -> None:
        """
        Will search products inside these collections.

        Args:
            collections: Collections name list to search into as string or Collections Enum.

        Raise:
            ``ValueError`` if collections list is empty.
        """
        if not len(collections):
            raise ValueError("Collections cannot be empty.")

        self.__collections = [{"name": collection} for collection in collections]

    def limit(self, limit: int) -> None:
        """
        How much products will return from query.

        Args:
            limit: limit value of products that will return from query

        Raise:
            ``ValueError`` if limit value is less or equal than zero.
        """
        if limit <= 0:
            raise ValueError("Limit value must be greater than 0.")

        self.__limit = limit

    def path_row(self, path: int, row: int) -> None:
        """
        Get product by specifying the cell from grid.
        Grid can be found: http://www.obt.inpe.br/OBT/assuntos/catalogo-cbers-amz-1

        Args:
            path: Path number from grid
            row: Row number from grid

        Raise:
            ``ValueError`` if path or row is empty.
        """
        if not path or not row:
            raise ValueError("Path and/or row cannot be empty.")

        self.__path_row = {
            "path": {"eq": path},
            "row": {"eq": row},
        }

    def cloud_cover(self, cloud_cover: int) -> None:
        """
        Maximum cloud coverage on scene.

        Args:
             cloud_cover: Maximum cloud cover percentage between 0 and 100 range.

        Raise:
            ``ValueError`` if cloud cover is less than zero and greater than 100.
        """
        if cloud_cover < 0 or cloud_cover > 100:
            raise ValueError("Cloud cover must be between 0 and 100.")

        self.__cloud_cover = {"cloud_cover": {"lte": cloud_cover}}
