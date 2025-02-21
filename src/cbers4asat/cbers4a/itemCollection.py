# -*- coding: utf-8 -*-
# Standard Libraries
from dataclasses import dataclass
from typing import Iterable

# Local Modules
from .item import Item
from .utils.dataclass import ignore_extras, SerializationCapabilities


@ignore_extras
@dataclass
class ItemCollection(SerializationCapabilities):
    """
    Class to parse GeoJSON from INPE STAC Catalog
    """

    type: str
    features: list[Item]

    def __post_init__(self):
        if len(self.features):
            theres_a_dict = any(map(lambda f: isinstance(f, dict), self.features))

            if theres_a_dict:  # If there's a dict, do conversion to Item object.
                items = list()
                for feature in self.features:
                    if isinstance(feature, dict):
                        items.append(Item(**feature))
                    elif isinstance(feature, Item):
                        items.append(feature)
                    else:
                        raise TypeError(f"{feature} is an invalid feature type!")

                self.features = items.copy()

    def __iter__(self) -> Iterable[Item]:
        """
        docstring
        """
        for feature in self.features:
            yield feature

    def get_features_assets(self) -> None:
        """
        docstring
        """
        for feature in self.features:
            feature.get_assets()
