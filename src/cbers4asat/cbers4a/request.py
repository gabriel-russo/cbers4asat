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

from dataclasses import dataclass, field
from typing import List, Optional, Union
from .collections import Collections
from .utils.dataclass import SerializationCapabilities


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
class STACRequestBody(SerializationCapabilities):
    """
    Represents the STAC API request. This object will be send inside POST request body to INPE STAC API.
    """

    bbox: list[float] = field(default_factory=lambda: [-81, -37, -30, 11])
    datetime: str = None
    fromCatalog: str = field(default="yes")
    limit: int = 100
    providers: List[Providers] = field(default_factory=list)


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
