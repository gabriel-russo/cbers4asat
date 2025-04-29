# -*- coding: utf-8 -*-
# Standard Libraries
from datetime import date
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

    def __init__(self) -> None:
        self.search_item_body: STACItemRequestBody = STACItemRequestBody()

    def __call__(self) -> dict | Exception:
        """
        Make request using the search parameters.

        Return:
            GeoJson-like dictionary.
        Raise:
            ``Exception`` if any http error.
        """
        features = list()
        with Session() as session:
            for id_ in self.search_item_body.ids:
                try:
                    response = session.get(
                        f"{self.BASE_URL_SEARCH_ITEM}/{self.search_item_body.collection}/items/{id_}"
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
        Id(s) to search inside a collection.

        Args:
            ids: Item id String or list of item id strings.
            collection: Collection name to search into as string or Collections Enum.
        Return:
            Void
        Raise:
            ``Exception`` if id(s) or collection is empty.
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

    def __init__(self) -> None:
        self.stac_request_body = STACRequestBody()
        self.providers_body = Providers()

    def __call__(self) -> dict | Exception:
        """
        Make request using the search parameters.

        Return:
            GeoJson-like dictionary.
        Raise:
            ``Exception`` if any http error.
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
        Only products that have a geometry/footprint that intersects the bounding box are selected.

        Args:
            bbox: The bounding box provided as a list of four floats, minimum longitude, minimum latitude, maximum longitude and maximum latitude.
        Return:
            Void
        Raise:
            ``Exception`` if bbox list is empty or bbox coordinates is not float numbers or bbox does not have 4 coordinates.
        """
        if not len(bbox):
            raise Exception("Bounding box cannot be empty.")
        elif not all([isinstance(coord, float) for coord in bbox]):
            raise Exception("Bounding box coordinates must be float numbers.")
        elif len(bbox) != 4:
            raise Exception(
                "Bounding box must have four float numbers representing the coordinates."
            )

        self.stac_request_body.bbox = bbox

    def date_interval(self, start: date, end: date) -> None | Exception:
        """
        Search for scenes that was taken in this interval of dates.

        Args:
            start: Initial date. The older part of interval.
            end: End date. The most recent part of interval.
        Return:
            Void
        Raise:
            ``Exception`` if the start date is more recent than end date.
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
        Will search products inside these collections.

        Args:
            collections: Collections name list to search into as string or Collections Enum.
        Return:
            Void
        Raise:
            ``Exception`` if collections list is empty.
        """
        if not len(collections):
            raise Exception("Collections cannot be empty.")

        self.providers_body.collections = [
            Collection(name=collection) for collection in collections
        ]

    def limit(self, limit: int) -> None | Exception:
        """
        How much products will return from query.

        Args:
            limit: limit value of products that will return from query
        Return:
            Void
        Raise:
            ``Exception`` if limit value is less or equal than zero.
        """
        if limit <= 0:
            raise Exception("Limit value must be greater than 0.")

        self.stac_request_body.limit = limit

    def path_row(self, path: int, row: int) -> None | Exception:
        """
        Get product by specifying the cell from grid.
        Grid can be found: http://www.obt.inpe.br/OBT/assuntos/catalogo-cbers-amz-1

        Args:
            path: Path number from grid
            row: Row number from grid
        Return:
            Void
        Raise:
            ``Exception`` if path or row is empty.
        """
        if not path or not row:
            raise Exception("Path and/or row cannot be empty.")

        self.providers_body.query.path = dict(eq=path)
        self.providers_body.query.row = dict(eq=row)

    def cloud_cover(self, cloud_cover: int) -> None | Exception:
        """
        Maximum cloud coverage on scene.

        Args:
             cloud_cover: Maximum cloud cover percentage between 0 and 100 range.
        Return:
            Void
        Raise:
            ``Exception`` if cloud cover is less than zero and greater than 100.
        """
        if cloud_cover < 0 or cloud_cover > 100:
            raise Exception("Cloud cover must be between 0 and 100.")

        self.providers_body.query.cloud_cover.update(lte=cloud_cover)
