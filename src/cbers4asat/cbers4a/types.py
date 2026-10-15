# -*- coding: utf-8 -*-

from typing import Any, Literal, NotRequired, TypedDict, Union

from .collections import Collections

# ===========================
# INPE STAC Request representation
# ===========================


class CollectionDict(TypedDict):
    """
    Represents the collection inside the collection list (providers.collections).
    """

    name: Union[str, Collections]


class ProviderDict(TypedDict):
    """
    Represents the LGI-CDSR provider. The only provider supported by cbers4asat (by choice).
    """

    method: str
    name: str
    collections: list[CollectionDict]
    query: dict[str, Any]


class STACRequestBodyDict(TypedDict):
    """
    Represents the STAC API request. This object is sent as the POST body to the INPE STAC API.
    """

    bbox: list[float]
    datetime: str
    fromCatalog: str
    limit: int
    providers: list[ProviderDict]


# ===========================
# STAC Feature representation
# ===========================


class AssetDict(TypedDict):
    """
    Represents an Asset from an Item.
    """

    href: str
    type: str


class AssetsDict(TypedDict):
    """
    Represents the assets from an Item.
    """

    thumbnail: AssetDict
    red: NotRequired[AssetDict]
    green: NotRequired[AssetDict]
    blue: NotRequired[AssetDict]
    nir: NotRequired[AssetDict]
    pan: NotRequired[AssetDict]


Bands = Literal["red", "green", "blue", "nir", "pan"]


class PolygonDict(TypedDict):
    """
    Represents the Item geometry interface.
    """

    type: Literal["Polygon"]
    coordinates: list[list[list[float]]]


class FeatureDict(TypedDict):
    type: Literal["Feature"]
    geometry: PolygonDict
    properties: dict[str, Any]
    stac_version: str
    id: str
    collection: str
    bbox: list[float]
    assets: AssetsDict


class FeatureCollectionDict(TypedDict):
    """
    Represents the outer container of a STAC response.
    """

    type: Literal["FeatureCollection"]
    features: list[FeatureDict]
