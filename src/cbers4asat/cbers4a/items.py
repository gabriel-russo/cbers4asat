# -*- coding: utf-8 -*-
"""
Dictionary helpers to work with the STAC items.

These functions replace the methods that used to live in the ``Item`` and
``ItemCollection`` classes. Items are plain dictionaries (``ItemDict``) and are
manipulated directly.
"""

# Local Modules

from .search import SearchItem
from .types import Bands, FeatureCollectionDict, FeatureDict


def get_features_assets(feature_collection: FeatureCollectionDict) -> None:
    """
    STAC API returns the items without assets, so, when needed, call this
    function to load all the assets inside every item.
    """
    search = SearchItem()

    for feature in feature_collection["features"]:
        search.ids([feature["id"]])

        search.collection(feature["collection"])

        features = search().get("features")

        if not len(features):
            raise Exception("Item not found.")

        (f,) = features

        feature["assets"] = f["assets"]


def has_band(item: FeatureDict, band: str) -> bool:
    """
    Check if an item has a band searched by its name.

    Args:
        item: Item dictionary.
        band: Band name. Ex.: red
    """

    return band in item["assets"]


def band_url(item: FeatureDict, band: Bands) -> str:
    """
    Get the asset/band URL of an item.

    Args:
        item: Item dictionary.
        band: Band name. Ex.: red
    """

    return item["assets"][band]["href"]
