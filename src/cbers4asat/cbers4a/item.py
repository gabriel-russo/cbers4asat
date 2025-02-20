# -*- coding: utf-8 -*-
# Standard Libraries
from dataclasses import dataclass
from os.path import join, basename
from typing import Union, Optional

# PyPi Packages
from requests import Session, HTTPError
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Local Modules
from .search import SearchItem


def ignore_extras(cls):
    """
    Ignore extra fields in dataclass decorator.
    """
    __original__init__ = cls.__init__

    def filter(self, **kwargs):
        __original__init__(
            self, **{k: v for k, v in kwargs.items() if k in self.__annotations__}
        )

    cls.__init__ = filter
    return cls


@ignore_extras
@dataclass
class Geometry:
    type: str
    coordinates: list[list[list[float]]]


@ignore_extras
@dataclass
class Properties:
    datetime: str
    path: int
    row: int
    satellite: str
    sensor: str
    cloud_cover: Union[float, int]


@ignore_extras
@dataclass
class Asset:
    href: str
    type: str


@ignore_extras
@dataclass
class Assets:
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


@ignore_extras
@dataclass
class Item:
    """Class to parse items from INPE STAC Catalog"""

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

    def get_assets(self):
        """
        docstring
        """
        search = SearchItem()
        search.ids(
            list([self.id]),
            collection=self.collection,
        )
        self.assets = Item(**search().get("features")[0]).assets

    def download(self, band: str, credential: str, outdir: str) -> None | Exception:
        """
        Download the asset.
        """
        asset: Asset = getattr(self.assets, band, None)

        if not asset:
            raise Exception(f"Band {band} does not exist in this asset!")

        url = asset.href

        filename = basename(url)
        outfile = join(outdir, filename)

        retries = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            other=3,
            backoff_factor=1,
            status_forcelist=[500, 501, 502, 503, 504],
            allowed_methods={"GET"},
        )

        with Session() as session:
            session.mount("http://", HTTPAdapter(max_retries=retries))
            try:
                response = session.get(
                    url,
                    params={"email": credential},
                    stream=True,
                    allow_redirects=True,
                )
                response.raise_for_status()
                with open(outfile, "wb") as f:
                    for chunk in response.iter_content(chunk_size=4096):
                        if chunk:
                            f.write(chunk)
            except HTTPError as err:
                raise Exception(
                    f"{response.status_code} - ERROR in {url}. Reason: {response.reason}. Exception: {err}"
                )
