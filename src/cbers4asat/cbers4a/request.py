# -*- coding: utf-8 -*-
"""
This dataclasses inside this file will generate something like this when requesting data
to STAC API in Search class:

{
  "providers":[
    {
      "name": "LGI-CDSR",
      "collections": [
        {
          "name": "CBERS4A_WPM_L4_DN"
        },
      ],
      "method": "POST",
      "query": {"cloud_cover": {"lte": 100}}
    }
  ],
  "datetime": "2024-12-18T00:00:00/2025-01-18T23:59:00",
  "limit": 100,
  "bbox": [
    -63.93905639648438,
    -9.00445156167208,
    -63.44879150390626,
    -8.733077421211563
  ],
  "fromCatalog": "yes"
}
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Union, Any
from .collections import Collections


@dataclass
class Collection:
    """
    Represents the collection inside collection list (providers.collections)
    """

    name: Union[str, Collections] = None


@dataclass
class Query:
    """
    Represents the values to query inside the LGI-CDSR provider. (providers.query)
    """

    cloud_cover: dict[str, int] = field(default_factory=lambda: {"lte": 100})
    path: Optional[dict[str, int]] = None
    row: Optional[dict[str, int]] = None


@dataclass
class Providers:
    """
    Represents the LGI-CDSR provider. The only provider supported by cbers4asat (by choice).
    """

    method: str = field(default="POST")
    name: str = field(default="LGI-CDSR")
    collections: list[Collection] = None
    query: Query = field(default_factory=Query)


@dataclass
class STACRequestBody:
    """
    Represents the STAC API request. This object will be send inside POST request body to INPE STAC API.
    """

    bbox: list[float] = None
    datetime: str = None
    fromCatalog: str = field(default="yes")
    limit: int = 100
    providers: List[Providers] = field(default_factory=list)

    def __del_none(self, value: dict) -> list[dict] | dict[Any, dict] | dict:
        """
        Delete keys with the value None in a dictionary, recursively.
        """
        if isinstance(value, list):
            return [self.__del_none(x) for x in value if x is not None]
        elif isinstance(value, dict):
            return {
                key: self.__del_none(val)
                for key, val in value.items()
                if val is not None
            }
        else:
            return value

    def as_dict(self) -> dict:
        return self.__del_none(asdict(self).copy())


@dataclass
class STACItemRequestBody:
    """
    Represents the STAC API request to get single/multiple item(s) full metadata.
    """

    ids: list[str] = None
    collection: Union[str, Collections] = None

    @property
    def empty(self):
        return self.collection is None and self.ids is None
