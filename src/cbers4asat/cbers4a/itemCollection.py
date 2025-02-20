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

    def __post_init__(self):
        if len(self.features):
            if isinstance(self.features[0], dict):
                items = list()
                for feature in self.features:
                    items.append(Item(**feature))
                self.features = items.copy()

    def get_features_assets(self):
        for feature in self.features:
            feature.get_assets()
