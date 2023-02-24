#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from .cbers4a import Search, ItemCollection
from datetime import date
from typing import List, overload, Dict, Union, Tuple
from os.path import isdir, join
from os import getcwd, cpu_count, mkdir
from geopandas import GeoDataFrame
from pandas import json_normalize
from shapely.geometry import Polygon


class Cbers4aAPI:
    def __init__(self, user):
        self._user = user

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    @staticmethod
    def query(
        *,
        location: Union[List[float], Tuple, Polygon],
        initial_date: date,
        end_date: date,
        cloud: int,
        limit: int,
        collections: List[str] = None,
    ):
        """
        Query Images from INPE's catalog

        Args:
            location: Bounding box or Path Row
            initial_date: Images from this date
            end_date: Images to this date
            cloud: Percentage of clouds
            limit: Limit of returned images
            collections: Collection's name(s)

        Notes:
            Location:
                - Bounding box: `location=[-0.5, 1.0, 0.5, -0.5]`
                - Path and row respectively: `location=(225,75)`
            Initial and end dates:
                - Use date object from datetime library: `datetime.date(2021,05,25)`
                - Caution to end date always be bigger than initial date
                - e.g. `initial_date=datetime.date(2021,08,15)`
            Cloud coverage:
                - Search for scenes below certain cloud coverage percentage
                - e.g. `cloud=70`
            Limit:
                - Max value of returned features is 1000
                - e.g. `limit=500`
            Collections:
                - Available collections from INPE catalog <http://www2.dgi.inpe.br/catalogo/explore>
                - Always an array of collections name.
                - e.g. `['AMAZONIA1_WFI_L2_DN']` or `['AMAZONIA1_WFI_L2_DN', 'CBERS4A_WPM_L4_DN']` etc.

        Returns:
            dict: Dict with GeoJSON-like format

        """
        search = Search()

        if not location:
            raise Exception("Location cannot be empty")

        if isinstance(location, list):
            search.bbox(location)
        elif isinstance(location, tuple):
            path, row = location
            search.path_row(path, row)
        elif isinstance(location, Polygon):
            search.bbox(list(location.bounds))
        else:
            raise Exception("Provide a bbox or a path row")

        search.date(initial_date.isoformat(), end_date.isoformat())
        search.cloud_cover("<=", cloud)
        search.limit(limit)

        if collections is not None:
            search.collections(collections)

        result = search()
        return result.featurescollection

    @staticmethod
    def query_by_id(id_: Union[str, List[str]]):
        """
        Search a product by id

        Args:
            id_: One or more scene's id
        Returns:
            dict: Dict with GeoJSON-like format
        """
        search = Search()

        # search() method only works with a list of ids.
        if type(id_) is not list:
            search.ids([id_])
        else:
            search.ids(id_)

        result = search()
        return result.featurescollection

    # AUXILIARY -------Description------------------
    #
    # _check_for_exception -> Private method specialized to check for file and folders and mistakes
    # ----------------------------------------------

    def __check_for_exception(self, product, bands, outdir):
        """Search for exceptions block: empty product, empty bands, output dir does not exist"""

        # Check for empty products in different contexts
        if isinstance(product, Dict):
            if not product:  # Check if dictionary is empty
                raise TypeError("No product to download")
        elif isinstance(product, GeoDataFrame):
            if product.empty:  # Check if data frame is empty
                raise TypeError("No product to download")
        # ---
        if not bands or bands == [""]:
            raise TypeError("Choose bands to download")
        elif not isdir(outdir):
            raise NotADirectoryError("Choose a valid output directory")

    def __download(
        self,
        products: Dict,
        bands: List[str],
        threads: int = cpu_count(),
        outdir: str = getcwd(),
        with_folder: bool = False,
    ):
        self.__check_for_exception(products, bands, outdir)

        products = ItemCollection(products).items()

        with ThreadPoolExecutor(
            max_workers=threads, thread_name_prefix="cbers4a"
        ) as pool:
            if with_folder:
                root = outdir  # Save the outdir start point (to looks like a pushd and popd)
            for product in products:
                if with_folder:
                    new_path = join(root, product.id)
                    mkdir(new_path)
                    outdir = new_path
                for band in bands:
                    pool.submit(product.download, band, self._user, outdir)

    def __download_gdf(
        self,
        products: GeoDataFrame,
        bands: List[str],
        threads: int = cpu_count(),
        outdir: str = getcwd(),
        with_folder: bool = False,
    ):
        self.__check_for_exception(products, bands, outdir)

        with ThreadPoolExecutor(
            max_workers=threads, thread_name_prefix="cbers4a_gdf"
        ) as pool:
            if with_folder:
                root = outdir  # Save the outdir start point (to looks like a pushd and popd)
            for index, row in products.iterrows():
                if with_folder:
                    new_path = join(root, str(index))
                    mkdir(new_path)
                    outdir = new_path

                products_query = self.query_by_id(str(index))
                products_query = ItemCollection(products_query).items()
                for product in products_query:
                    for band in bands:
                        pool.submit(product.download, band, self._user, outdir)

    @overload
    def download(
        self,
        products: Dict,
        bands: List[str],
        threads: int = cpu_count(),
        outdir: str = getcwd(),
        with_folder: bool = False,
    ):
        ...

    @overload
    def download(
        self,
        products: GeoDataFrame,
        bands: List[str],
        threads: int = cpu_count(),
        outdir: str = getcwd(),
        with_folder: bool = False,
    ):
        ...

    def download(
        self,
        products,
        bands,
        threads=cpu_count(),
        outdir=getcwd(),
        with_folder: bool = False,
    ):
        """
        Download bands from all given scenes

        Args:
            products: Data returned from API
            bands: List of band color's name
            threads: Max of cpu threads
            outdir: Output path
            with_folder: Group scene bands in a sub folder
        Examples:
            - download(my_query_result, ['red', 'green'], 3, './downlaods', true)
            - download(my_query_result, ['red'], outdir='./downloads', with_folder=true)
        Returns:
            GeoTIFF files
        """
        if isinstance(products, dict):
            return self.__download(products, bands, threads, outdir, with_folder)
        elif isinstance(products, GeoDataFrame):
            return self.__download_gdf(products, bands, threads, outdir, with_folder)
        else:
            raise TypeError("Bad Arguments")

    @staticmethod
    def to_geodataframe(products: Dict, crs: str = "EPSG:4326"):
        """
        Transform products list to a GeoDataFrame

        Args:
            products: GeoJSON-like dictionary returned from API
            crs: Coordinate Reference System (ex: EPSG:4326)
        Returns:
            GeoDataFrame
        """
        return GeoDataFrame.from_features(products, crs=crs).set_index(
            json_normalize(products["features"])["id"].values
        )
