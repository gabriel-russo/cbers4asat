# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from os import cpu_count, getcwd
from os.path import isdir, join
from typing import Any, List, Optional, Union

from geopandas import GeoDataFrame
from shapely.geometry import Polygon

from .cbers4a import (
    Bands,
    Collections,
    Download,
    FeatureCollectionDict,
    Search,
    SearchItem,
    band_url,
    get_features_assets,
    has_band,
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
    ) -> FeatureCollectionDict:
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
                - e.g. `["AMAZONIA1_WFI_L2_DN"]` or `[col.AMAZONIA1_WFI_L2_DN, col.CBERS4A_WPM_L4_DN]` etc.

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
            raise ValueError(
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
    ) -> FeatureCollectionDict:
        """
        Search a product by id

        Args:
            scene_id: One or more scene's id
            collection: Collection's name

        Returns:
            dict: Dict with GeoJSON-like format
        """
        search = SearchItem()
        search.ids(scene_id if isinstance(scene_id, list) else list([scene_id]))
        search.collection(collection)
        return search()

    def __download(
        self,
        products: FeatureCollectionDict,
        bands: list[Bands],
        threads: int,
        outdir: str,
        with_folder: bool,
        with_metadata: bool,
    ):
        if threads == -1:
            nproc = cpu_count()
            threads = nproc if nproc is not None else 4

        tasks = []
        root = outdir

        for product in products["features"]:
            if with_folder:
                outdir = join(root, product["id"])

            for band in bands:
                if not has_band(product, band):
                    raise ValueError(f"Band {band} does not exist in this item!")

                url = band_url(product, band)

                tasks.append((url, self.email, outdir))

                if with_metadata:
                    url_xml = url.replace(".tif", ".xml")
                    tasks.append((url_xml, self.email, outdir))

        with ThreadPoolExecutor(max_workers=threads) as t_pool:
            for task in tasks:
                f = t_pool.submit(Download().download, *task)

                exc = f.exception()

                if exc is not None:
                    raise exc

    def download(
        self,
        products: Union[FeatureCollectionDict, GeoDataFrame],
        bands: list[Bands],
        threads: int = -1,
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
            raise ValueError("Choose bands to download.")

        if not isdir(outdir):
            raise NotADirectoryError("Choose a valid output directory.")

        if not self.email:
            raise ValueError("Credentials not provided!")

        if isinstance(products, GeoDataFrame):
            if products.empty:  # Check if data frame is empty
                raise Exception("No product to download.")

            try:
                features: FeatureCollectionDict = {
                    "type": "FeatureCollection",
                    "features": [],
                }

                search = SearchItem()

                for _, row in products.iterrows():
                    search.ids([row.id])
                    search.collection(row.collection)
                    feat = search()
                    features["features"].extend(feat["features"])

                self.__download(
                    features,
                    bands,
                    threads,
                    outdir,
                    with_folder,
                    with_metadata,
                )
            except Exception as err:
                raise Exception(f"Check your product structure. Error: {err}")

            return None

        if not isinstance(products, dict):
            raise ValueError("Bad Arguments.")

        try:
            # INPE'S API returns only the footprint image asset
            # so, to download the bands we need to search individually
            # and then fill the feature's assets

            get_features_assets(products)

            self.__download(
                products, bands, threads, outdir, with_folder, with_metadata
            )

        except Exception as err:
            raise Exception(f"Check your product structure. Error: {err}")

    @staticmethod
    def to_geodataframe(products: FeatureCollectionDict) -> GeoDataFrame:
        """
        Transform products list to a GeoDataFrame.

        Args:
            products: GeoJSON-like dictionary returned from API.
        Returns:
            GeoDataFrame of products.
        """
        if not isinstance(products, dict):
            raise ValueError("Provide a valid product structure.")

        features: list[dict[str, Any]] = []

        for item in products.get("features", []):
            # Flattening the feature info to load as columns
            new_properties = {
                **item["properties"],
                "id": item.get("id"),
                "bbox": item.get("bbox"),
                "collection": item.get("collection"),
                "thumbnail": item["assets"]["thumbnail"]["href"],
            }

            features.append(
                {
                    "type": "Feature",
                    "geometry": item.get("geometry"),
                    "properties": new_properties,
                }
            )

        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
        }

        gdf = GeoDataFrame.from_features(features=feature_collection, crs="EPSG:4326")

        if not gdf.empty and "id" in gdf.columns:
            gdf = GeoDataFrame(gdf.set_index("id", drop=False), crs=gdf.crs)

        return gdf
