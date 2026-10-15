# -*- coding: utf-8 -*-
from os import makedirs
from os.path import basename, exists, join, normpath

from requests import HTTPError, Session


class Download:
    """
    Class to download assets from INPE STAC Catalog.
    """

    def __init__(self):
        self.__session = Session()
        self.__session.headers.update({"User-Agent": "cbers4asat (Python)"})

    def download(self, url: str, credential: str, outdir: str) -> None:
        """
        Download the asset.

        Args:
            url: URL pointing to asset/band .TIFF
            credential: e-mail used in the explorer inpe platform.
            outdir: Output directory

        Raise:
            ``HTTPError`` if any http error occurs.
        """
        if not exists(outdir):
            makedirs(outdir, exist_ok=True)

        geotiff = basename(url)

        outfile = normpath(join(outdir, geotiff))

        with self.__session as session:
            try:
                res = session.get(
                    url,
                    params={"email": credential},
                    stream=True,
                    allow_redirects=True,
                )

                res.raise_for_status()

                with open(outfile, "wb") as f:
                    for chunk in res.iter_content(chunk_size=4096):
                        if chunk:
                            f.write(chunk)

            except HTTPError as err:
                raise HTTPError(
                    f"{res.status_code} - ERROR in {url}. Reason: {res.reason}. Exception: {err}"
                )
