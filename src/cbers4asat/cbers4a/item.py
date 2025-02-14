# -*- coding: utf-8 -*-
# Standard Libraries
from dataclasses import dataclass
from os.path import join, basename
from typing import Union, Optional

# PyPi Packages
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


@dataclass
class Geometry:
    type: str
    coordinates: list[list[list[float]]]


@dataclass
class Properties:
    datetime: str
    path: int
    row: int
    satellite: str
    sensor: str
    cloud_cover: Union[float, int]


@dataclass
class Asset:
    href: str
    type: str


@dataclass
class Assets:
    thumbnail: Asset
    red: Optional[Asset] = None
    green: Optional[Asset] = None
    blue: Optional[Asset] = None
    nir: Optional[Asset] = None
    pan: Optional[Asset] = None


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

    def download(self, band: str, credential: str, outdir: str) -> None | Exception:
        """
        Download the asset.
        """
        if not credential or credential == "":
            raise Exception("Credentials not provided!")

        url = self.url(band)
        print(url)
        if not url:
            raise Exception(f"Band {band} does not exist in this asset!")

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

            response = session.get(
                url,
                params={"email": credential},
                stream=True,
                allow_redirects=True,
            )

            if 200 <= response.status_code <= 299:
                with open(outfile, "wb") as f:
                    for ch in response.iter_content(chunk_size=4096):  # (page size 4Kb)
                        if ch:
                            f.write(ch)
            else:
                raise Exception(
                    f"{response.status_code} - ERROR in {url}. Reason: {response.reason}"
                )

    def url(self, band: str) -> str | None:
        return {
            "red": self.assets.red.href,
            "green": self.assets.green.href,
            "blue": self.assets.blue.href,
            "nir": self.assets.nir.href,
            "pan": self.assets.pan.href,
        }.get(band, None)
