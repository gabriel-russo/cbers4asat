# -*- coding: utf-8 -*-
# Standard Libraries
from os import makedirs
from os.path import join, basename, exists

# PyPi Packages
from requests import Session, HTTPError
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class Download:
    """
    Class to download assets from INPE STAC Catalog.
    """

    def __init__(self):
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
        self.session = Session()
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def download(self, url: str, credential: str, outdir: str) -> None | Exception:
        """
        Download the asset.

        Args:
            url: URL pointing to asset/band .TIFF
            credential: e-mail used in the explorer inpe platform.
            outdir: Output directory
        Raise:
            ``Exception`` if any http error occurs.
        """
        if not exists(outdir):
            makedirs(outdir, exist_ok=True)

        geotiff = basename(url)

        outfile = join(outdir, geotiff)

        with self.session as session:
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
