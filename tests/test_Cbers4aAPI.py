# -*- coding: utf-8 -*-
from datetime import date

import pytest
from shapely.geometry import Polygon

from cbers4asat import Cbers4aAPI
from cbers4asat import Collections as col
from cbers4asat.cbers4a import FeatureCollectionDict
from mocks import feature_with_bands, feature_without_bands

EXPECTED_RESULT_FROM_EMPTY_QUERY_RESPONSE: FeatureCollectionDict = {
    "type": "FeatureCollection",
    "features": [],
}

EXPECTED_RESULT_FROM_QUERY = {
    "type": "FeatureCollection",
    "features": [feature_without_bands],
}

EXPECTED_RESULT_AFTER_QUERY_ITEM_ASSETS = {
    "type": "FeatureCollection",
    "features": [feature_with_bands],
}


class TestCbers4aAPI:
    def test_email(self, api):
        assert "test@test.com" in api.email

    def test_set_email(self, api):
        api.email = "another@test.com"
        assert api.email == "another@test.com"

    def test_empty_email(self):
        api2 = Cbers4aAPI()
        assert api2.email is None

    def test_query_bbox(self, api, mock_collection_response):
        result = api.query(
            location=[-63.9, -8.8, -63.7, -8.7],
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN"],
        )

        assert EXPECTED_RESULT_FROM_QUERY == result

    def test_query_geometry(self, api, mock_collection_response):
        bbox = Polygon(
            [
                [-63.911934, -8.738337],
                [-63.912621, -8.805859],
                [-63.912621, -8.805859],
                [-63.798294, -8.738337],
            ]
        )

        result = api.query(
            location=bbox,
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN"],
        )

        assert EXPECTED_RESULT_FROM_QUERY == result

    def test_query_pathrow(self, api, mock_collection_response):
        result = api.query(
            location=(206, 133),
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN"],
        )

        assert EXPECTED_RESULT_FROM_QUERY == result

    def test_query_collections_with_enum(self, api, mock_collection_response):
        result = api.query(
            location=(206, 133),
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=[col.CBERS4A_WPM_L4_DN, col.CBERS4A_WPM_L2_DN],
        )

        assert EXPECTED_RESULT_FROM_QUERY == result

    def test_query_collections_mix(self, api, mock_collection_response):
        result = api.query(
            location=(206, 133),
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN", col.CBERS4A_WPM_L2_DN],
        )

        assert EXPECTED_RESULT_FROM_QUERY == result

    def test_query_by_id_str(self, api, mock_item_response):
        result = api.query_by_id(scene_id="ABC123", collection="y")

        assert EXPECTED_RESULT_AFTER_QUERY_ITEM_ASSETS == result

    def test_query_by_id_list(self, api, mock_item_response):
        result = api.query_by_id(scene_id=["ABC123"], collection="y")

        assert EXPECTED_RESULT_AFTER_QUERY_ITEM_ASSETS == result

    def test_query_empty_response(self, api, mock_empty_collection_response):
        result = api.query(
            location=[-63.9, -8.8, -63.7, -8.7],
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN"],
        )

        assert EXPECTED_RESULT_FROM_EMPTY_QUERY_RESPONSE == result

    def test_to_geodataframe(self, api):
        gdf = api.to_geodataframe(EXPECTED_RESULT_FROM_QUERY)

        assert "id" in list(gdf.columns)
        assert "geometry" in list(gdf.columns)
        assert "datetime" in list(gdf.columns)
        assert "path" in list(gdf.columns)
        assert "row" in list(gdf.columns)
        assert "satellite" in list(gdf.columns)
        assert "sensor" in list(gdf.columns)
        assert "cloud_cover" in list(gdf.columns)
        assert "bbox" in list(gdf.columns)
        assert "collection" in list(gdf.columns)
        assert "thumbnail" in list(gdf.columns)

        assert type(gdf).__name__ == "GeoDataFrame"
        assert gdf.crs == "EPSG:4326"
        assert len(gdf) == 1

    def test_missing_credentials_exception(self):
        with pytest.raises(ValueError):
            api = Cbers4aAPI()
            api.download(EXPECTED_RESULT_FROM_QUERY, bands=["blue"])

    def test_empty_credentials_exception(self):
        with pytest.raises(ValueError):
            api = Cbers4aAPI("")
            api.download(EXPECTED_RESULT_FROM_QUERY, bands=["blue"])

    def test_missing_credentials_exception_geodataframe(self):
        with pytest.raises(ValueError):
            api = Cbers4aAPI("")
            gdf = api.to_geodataframe(EXPECTED_RESULT_FROM_QUERY)
            api.download(gdf, bands=["blue"])

    def test_wrong_threads_values_negative(self, api):
        with pytest.raises(ValueError):
            api.download(EXPECTED_RESULT_FROM_QUERY, bands=["blue"], threads=-10)

    def test_wrong_threads_values_zero(self, api):
        with pytest.raises(ValueError):
            api.download(EXPECTED_RESULT_FROM_QUERY, bands=["blue"], threads=0)

    def test_band_not_available_for_satellite(self, api, mock_item_response):
        with pytest.raises(ValueError):
            api.download(EXPECTED_RESULT_AFTER_QUERY_ITEM_ASSETS, bands=["pan"])

    def test_download(self, api, mock_item_response, tmp_path):
        api.download(
            products=EXPECTED_RESULT_FROM_QUERY,
            bands=["blue"],
            threads=1,
            outdir=tmp_path.as_posix(),
            with_folder=True,
        )

        with open(tmp_path / "ABC123" / "image.tif", "rb") as f:
            assert f.read() == b"dummydata"

    def test_download_gdf(self, api, mock_item_response, tmp_path):
        gdf = api.to_geodataframe(EXPECTED_RESULT_FROM_QUERY)

        api.download(
            products=gdf,
            bands=["blue"],
            threads=1,
            outdir=tmp_path.as_posix(),
            with_folder=True,
        )

        with open(tmp_path / "ABC123" / "image.tif", "rb") as f:
            assert f.read() == b"dummydata"
