# -*- coding: utf-8 -*-
# Standard Libraries
from dataclasses import dataclass

# Local Modules
from .item import Item


@dataclass
class ItemCollection:
    """
    Class to parse GeoJSON from INPE STAC Catalog
    """

    type: str
    features: list[Item]
