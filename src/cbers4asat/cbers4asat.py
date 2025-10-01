# -*- coding: utf-8 -*-
# Standard Libraries
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from os import getcwd, cpu_count
from os.path import isdir, join
from typing import List, Dict, Union, Optional

# PyPi Packages
from geopandas import GeoDataFrame
from pandas import concat
from shapely.geometry import Polygon

# Local Modules
from .cbers4a import (
    Search,
    Download,
    SearchItem,
    ItemCollection,
    Item,
    Collections,
)


class Cbers4aAPI:
    """
    The CBERS4A API class. Query, download or transform data from CBERS-4A STAC API.

    Args:
        email: Sign-in e-mail used at https://www.dgi.inpe.br/catalogo/explore
    """

    def __init__(self, email: Optional[str] = None):
        self._email = email

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email: str):
        self._email = email

    @staticmethod
    def query(
        location: Union[list[float], Polygon, tuple],
        initial_date: date,
        end_date: date,
        cloud: int,
        limit: int,
        collections: Union[list[str], list[Collections]],
    ) -> dict:
        """
        Query Images from INPE's catalog

        Args:
            location: Bounding box, Polygon shape or Path and Row Tuple
            initial_date: Images from this date
            end_date: Images to this date
            cloud: Percentage of cloud coverage
            limit: Limit of returned images
            collections: Collection's name(s)
        Notes:
            Location:
                - Bounding box: `location=[-0.5, 1.0, 0.5, -0.5]`
                - Polygon shape from shapely
                - Path and row respectively: `location=(225,75)`
            Initial and end dates:
                - Use date object from datetime library: `datetime.date(2021,05,25)`
                - Caution to end date always be bigger than initial date
                - e.g. `initial_date=datetime.date(2021,08,15)`
            Cloud coverage:
                - Search for scenes less or equal (<=) cloud coverage percentage.
                - e.g. `cloud=70`
                - Must be between 0 and 100.
            Limit:
                - Values greater than 0.
                - e.g. `limit=500`.
            Collections:
                - Use the collections enum via `from cbers4asat import Collections as col`
                - Available collections from INPE catalog <https://www.dgi.inpe.br/catalogo/explore>
                - Always an array of collections name.
                - e.g. `[col.AMAZONIA1_WFI_L2_DN]` or `[col.AMAZONIA1_WFI_L2_DN, col.CBERS4A_WPM_L4_DN]` etc.

        Returns:
            dict: Dict with GeoJSON-like format
        Raises:
            Exception: If any input is invalid.
        """
        search = Search()

        if isinstance(location, list):
            search.bbox(location)
        elif isinstance(location, Polygon):
            search.bbox(list(location.bounds))
        elif isinstance(location, tuple):
            search.path_row(*location)
        else:
            raise Exception(
                "Provide a Bouding box, Polygon shape or path and row tuple"
            )

        search.date_interval(initial_date, end_date)
        search.cloud_cover(cloud)
        search.limit(limit)
        search.collections(collections)

        return search()

    @staticmethod
    def query_by_id(
        scene_id: Union[List[str], str], collection: Union[str, Collections]
    ):
        """
        Search a product by id

        Args:
            scene_id: One or more scene's id
            collection: Collection's name
        Returns:
            dict: Dict with GeoJSON-like format
        """
        search = SearchItem()
        search.ids(
            scene_id if isinstance(scene_id, list) else list([scene_id]),
            collection=collection,
        )
        return search()

    def __download(
        self,
        products: Dict,
        bands: List[str],
        threads: int = cpu_count(),
        outdir: str = getcwd(),
        with_folder: bool = False,
        with_metadata: bool = False,
    ):
        try:
            products = ItemCollection(**products)
        except TypeError:
            raise Exception(
                "Check your product structure. It must be a GeoJSON like dictionary."
            )

        products.get_features_assets()

        tasks = list()
        root = outdir
        for product in products:
            if with_folder:
                outdir = join(root, product.id)

            for band in bands:
                tasks.append(
                    (Download().download, product.band_url(band), self.email, outdir)
                )
                if with_metadata:
                    url_xml = product.band_url(band).replace('.tif', '.xml')
                    tasks.append(
                        (Download().download, url_xml, self.email, outdir)
                    )

        with ThreadPoolExecutor(max_workers=threads) as t_pool:
            for task in tasks:
                f = t_pool.submit(*task)
                if f.exception():
                    raise f.exception()

    def __download_gdf(
        self,
        products: GeoDataFrame,
        bands: List[str],
        threads: int = cpu_count(),
        outdir: str = getcwd(),
        with_folder: bool = False,
        with_metadata: bool = False,
    ):
        features = list()
        for index, row in products.iterrows():
            features.append(Item.from_search(row.id, row.collection))

        # GeoDataFrame is not needed anymore
        products = ItemCollection(type="FeatureCollection", features=features)

        tasks = list()
        root = outdir
        for product in products:
            if with_folder:
                outdir = join(root, product.id)
            for band in bands:
                tasks.append(
                    (Download().download, product.band_url(band), self.email, outdir)
                )
                if with_metadata:
                    url_xml = product.band_url(band).replace('.tif', '.xml')
                    tasks.append(
                        (Download().download, url_xml, self.email, outdir)
                    )


        with ThreadPoolExecutor(max_workers=threads) as t_pool:
            for task in tasks:
                f = t_pool.submit(*task)
                if f.exception():
                    raise f.exception()

    def download(
        self,
        products: Union[dict, GeoDataFrame],
        bands: list[str],
        threads: int = cpu_count(),
        outdir: str = getcwd(),
        with_folder: bool = False,
        with_metadata: bool = False,
    ):
        """
        Download bands from all given scenes

        Args:
            products: Data returned from API
            bands: List of band color's name. "red", "green", "blue", "nir", "pan"
            threads: Max of cpu threads
            outdir: Output path
            with_folder: Group scene bands in a sub folder
            with_metadata: Download band's metadata (XML)
        Examples:
            - download(my_query_result, ['red', 'green'], 3, './downlaods', true)
            - download(my_query_result, ['red'], outdir='./downloads', with_folder=true)
            - download(my_query_result, ['blue'], with_metadata=True)
        Returns:
            GeoTIFF files
        """
        if not len(bands):
            raise TypeError("Choose bands to download.")
        elif not isdir(outdir):
            raise NotADirectoryError("Choose a valid output directory.")
        elif not self.email:
            raise Exception("Credentials not provided!")

        if isinstance(products, dict):
            if not products:  # Check if dictionary is empty
                raise Exception("No product to download.")
            return self.__download(products, bands, threads, outdir, with_folder, with_metadata)
        elif isinstance(products, GeoDataFrame):
            if products.empty:  # Check if data frame is empty
                raise Exception("No product to download.")
            return self.__download_gdf(products, bands, threads, outdir, with_folder, with_metadata)
        else:
            raise Exception("Bad Arguments.")

    @staticmethod
    def to_geodataframe(products: dict) -> GeoDataFrame:
        """
        Transform products list to a GeoDataFrame

        Args:
            products: GeoJSON-like dictionary returned from API
        Returns:
            GeoDataFrame of products.
        """
        if not products or not isinstance(products, dict):
            raise Exception("Provide a valid product structure.")

        item_collection = ItemCollection(**products)
        processed = list()
        for item in item_collection:
            extras = {
                "properties": {
                    **item.properties.asdict(),
                    "id": item.id,
                    "bbox": item.bbox,
                    "collection": item.collection,
                    "thumbnail": item.assets.thumbnail.href,
                }
            }
            gdf = GeoDataFrame.from_features(
                {
                    "type": "FeatureCollection",
                    "features": [item.asdict() | extras],
                },
                crs="EPSG:4326",
            )
            processed.append(gdf)

        return concat(processed, ignore_index=True).set_index("id", drop=False)
