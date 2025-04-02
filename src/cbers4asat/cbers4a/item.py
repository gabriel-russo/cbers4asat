# -*- coding: utf-8 -*-
# Standard Libraries
from dataclasses import dataclass
from typing import Union, Optional, TypeVar

# Local Modules
from .search import SearchItem
from .utils.dataclass import SerializationCapabilities, ignore_extras


@ignore_extras
@dataclass
class Geometry:
    """
    Class that represents the Item geometry interface.
    """

    type: str
    coordinates: list[list[list[float]]]


@ignore_extras
@dataclass
class Properties(SerializationCapabilities):
    """
    Class that represents the Item properties.
    """

    datetime: str
    path: int
    row: int
    satellite: str
    sensor: str
    cloud_cover: Union[float, int]


@ignore_extras
@dataclass
class Asset:
    """
    Class that represents an Asset from Item.
    """

    href: str
    type: str


@ignore_extras
@dataclass
class Assets:
    """
    Class that represents the assets from Item.
    """

    thumbnail: Asset
    red: Optional[Asset] = None
    green: Optional[Asset] = None
    blue: Optional[Asset] = None
    nir: Optional[Asset] = None
    pan: Optional[Asset] = None

    def __post_init__(self):
        if isinstance(self.thumbnail, dict):
            self.thumbnail = Asset(**self.thumbnail)
        if isinstance(self.red, dict):
            self.red = Asset(**self.red)
        if isinstance(self.green, dict):
            self.green = Asset(**self.green)
        if isinstance(self.blue, dict):
            self.blue = Asset(**self.blue)
        if isinstance(self.nir, dict):
            self.nir = Asset(**self.nir)
        if isinstance(self.pan, dict):
            self.pan = Asset(**self.pan)


Item = TypeVar("Item")


@ignore_extras
@dataclass
class Item(SerializationCapabilities):
    """
    Class to parse items from INPE STAC Catalog

    This represents one image from CBERS-4/CBERS-4A/AMAZONIA-1.
    """

    type: str
    id: str
    collection: str
    geometry: Geometry
    bbox: list[float]
    properties: Properties
    assets: Assets

    def __post_init__(self):
        if isinstance(self.geometry, dict):
            self.geometry = Geometry(**self.geometry)
        if isinstance(self.properties, dict):
            self.properties = Properties(**self.properties)
        if isinstance(self.assets, dict):
            self.assets = Assets(**self.assets)

    @staticmethod
    def from_search(_id: str, collection: str) -> Item | Exception:
        """
        Create an Item by making a search by ID inside a collection.

        Args:
            _id: Item ID
            collection: Collection to search into.
        Return:
            Item object.
        Raise:
            ``Exception`` if item not found.
        """
        search = SearchItem()
        search.ids(
            list([_id]),
            collection=collection,
        )

        features = search().get("features")

        if not len(features):
            raise Exception("Item not found.")

        return Item(**features[0])

    def get_assets(self) -> None:
        """
        Get assets/bands of the object.
        """
        self.assets = Item.from_search(self.id, self.collection).assets

    def has_band(self, band: str) -> bool:
        """
        Check if Item has a band search by its name.

        Args:
            band: Band name. Ex.: red
        Return:
            True if item has band.
        """
        return getattr(self.assets, band, None) is not None

    def band_url(self, band: str) -> str | Exception:
        """
        Get asset/band URL.

        Args:
            band: Band name. Ex.: red
        Return:
            URL
        Raise:
            ``Exception`` if Item does not have band.
        """
        if not self.has_band(band):
            raise Exception(f"Band {band} does not exist in this item!")
        return getattr(self.assets, band).href
