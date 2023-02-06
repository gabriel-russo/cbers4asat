#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import requests
from os.path import join


class Item(object):
    """Class to parse items from INPE STAC Catalog"""

    def __init__(self, feature):
        self._feature = feature

    def __str__(self):
        """
        docstring
        """
        row = "{id:<25s} {date:^10s} {cloud:>15.1f}".format
        return row(id=self.id, date=self.date, cloud=self.get_property("cloud_cover"))

    def _repr_html_(self):
        """
        html representation for jupyter notebook
        """

        html = f"""
        <html>
        <body>
        <img
            style="display: block; margin-left: auto; margin-right: auto;"
            src="{self.thumbnail}" width="296" border="0"
        />
        </body>
        </html>
        """

        return html

    def repr_html(self, width=450):
        """
        html representation to generate a html catalog
        """
        html = f"""
        <div>
            <h2>{self.id}</h2>
            <span>Satelitte: {self.satellite}</span>
            <span>Sensor: {self.sensor}</span>
            <span>Collection: {self.collection}</span>
            <span>Cloud cover: {self.cloud_cover}</span>
            <span>Datetime: {self.get_datetime_fmt(fmt='%Y-%m-%d-%H:%m:%S')}</span>
            <span>bbox: {self.bbox}</span>
            <img src="{self.thumbnail}" width="{width}"/>
        </div>
        """
        return html

    def __lt__(self, other):
        """
        docstring
        """
        return self.get_property("cloud_cover", 0) < other.get_property(
            "cloud_cover", 0
        )

    @property
    def __geo_interface__(self):
        """
        Simple GeoJSON-like interface
        """
        return self._feature["geometry"]

    @property
    def id(self):
        """
        Provider identifier globally unique.
        """
        return self._feature["id"]

    @property
    def date(self):
        """
        The acquisition date of the asset.
        """
        return self.get_datetime_fmt()

    @property
    def bbox(self):
        """
        Bounding Box of the asset.
        """
        return self._feature.get("bbox")

    @property
    def collection(self):
        """
        The id of the STAC Collection this Item references to.
        """
        return self._feature.get("collection")

    @property
    def thumbnail(self):
        """
        Thumbnail image link.
        """
        return self._feature["assets"]["thumbnail"]["href"]

    @property
    def assets(self):
        """
        Unique keys of asset objects that can be downloaded.
        """
        return list(self._feature["assets"].keys())

    @property
    def cloud_cover(self):
        """
        Cloud coverage %
        """
        return self.get_property("cloud_cover")

    @property
    def path_row(self):
        """
        Return a string 'PATH_ROW'
        """
        return (
            str(self.get_property("path", "")) + "_" + str(self.get_property("row", ""))
        )

    @property
    def sensor(self):
        """
        Return the sensor
        """
        return self.get_property("sensor")

    @property
    def satellite(self):
        """
        Return the satellite
        """
        return self.get_property("satellite")

    @property
    def html(self):
        """
        Html to show image preview
        """

        return self.repr_html()

    def get_datetime(self):
        """
        The acquisition date and time of the assets
        as an object of the class datetime.datetime.
        """
        try:
            return datetime.strptime(self.get_property("datetime"), "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            return None

    def get_datetime_fmt(self, fmt="%Y-%m-%d"):
        """
        Return a string representing the acquisition date and time, controlled by a format string.
        """
        try:
            return self.get_datetime().strftime(fmt)
        except AttributeError:
            return None

    def get_property(self, p, v=None):
        """
        Get additional metadata fields.
        None if it does not exist.
        """
        return self._feature["properties"].get(p, v)

    def url(self, asset):
        """
        Get asset url
        """
        return self._feature["assets"][asset]["href"]

    def download(self, asset, credential, outdir, session=requests.Session()):
        """
        Download the asset.
        """
        url = self.url(asset)
        filename = url.split("/")[-1]
        outfile = join(outdir, filename)
        r = session.get(
            url,
            params={
                "email": credential,
                "item_id": self.id,
                "collection": self.collection,
            },
            stream=True,
            allow_redirects=True,
        )
        if r.status_code == 200:
            with open(outfile, "wb") as f:
                for ch in r.iter_content(chunk_size=4096):  # (page size 4Kb)
                    if ch:
                        f.write(ch)

            return outfile
        else:
            return "ERROR in " + url + " (" + r.reason + ")"
