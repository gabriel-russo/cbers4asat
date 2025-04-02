# -*- coding: utf-8 -*-
from datetime import date
from os import remove
import pytest
from cbers4asat import Cbers4aAPI, Collections as col
from shapely.geometry import Polygon
from mocks import (
    MockStacFeatureCollectionResponse,
    MockStacFeatureResponse,
    MockStacFeatureCollectionEmptyResponse,
    feature_without_bands,
    feature_with_bands,
)


class TestCbers4aAPI:
    api = Cbers4aAPI("test@test.com")

    expected_result_from_empty_query_response = {
        "type": "FeatureCollection",
        "features": [],
    }

    expected_result_from_query = {
        "type": "FeatureCollection",
        "features": [feature_without_bands],
    }

    expected_result_after_query_item_assets = {
        "type": "FeatureCollection",
        "features": [feature_with_bands],
    }

    def test_email(self):
        assert "test@test.com" in self.api.email

    def test_set_email(self):
        self.api.email = "another@test.com"
        assert self.api.email == "another@test.com"

    def test_empty_email(self):
        api2 = Cbers4aAPI()
        assert api2.email is None

    def test_query_bbox(self, monkeypatch):
        def mock_post(*args, **kwargs):
            return MockStacFeatureCollectionResponse()

        monkeypatch.setattr("requests.Session.post", mock_post)

        result = self.api.query(
            location=[-63.9, -8.8, -63.7, -8.7],
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN"],
        )

        assert self.expected_result_from_query == result

    def test_query_geometry(self, monkeypatch):
        def mock_post(*args, **kwargs):
            return MockStacFeatureCollectionResponse()

        monkeypatch.setattr("requests.Session.post", mock_post)

        bbox = Polygon(
            [
                [-63.911934, -8.738337],
                [-63.912621, -8.805859],
                [-63.912621, -8.805859],
                [-63.798294, -8.738337],
            ]
        )

        result = self.api.query(
            location=bbox,
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN"],
        )

        assert self.expected_result_from_query == result

    def test_query_pathrow(self, monkeypatch):
        def mock_post(*args, **kwargs):
            return MockStacFeatureCollectionResponse()

        monkeypatch.setattr("requests.Session.post", mock_post)

        result = self.api.query(
            location=(206, 133),
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN"],
        )

        assert self.expected_result_from_query == result

    def test_query_collections_with_enum(self, monkeypatch):
        def mock_post(*args, **kwargs):
            return MockStacFeatureCollectionResponse()

        monkeypatch.setattr("requests.Session.post", mock_post)

        result = self.api.query(
            location=(206, 133),
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=[col.CBERS4A_WPM_L4_DN, col.CBERS4A_WPM_L2_DN],
        )

        assert self.expected_result_from_query == result

    def test_query_collections_mix(self, monkeypatch):
        def mock_post(*args, **kwargs):
            return MockStacFeatureCollectionResponse()

        monkeypatch.setattr("requests.Session.post", mock_post)

        result = self.api.query(
            location=(206, 133),
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN", col.CBERS4A_WPM_L2_DN],
        )

        assert self.expected_result_from_query == result

    def test_query_by_id_str(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return MockStacFeatureResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        result = self.api.query_by_id(scene_id="ABC123", collection="y")

        assert self.expected_result_after_query_item_assets == result

    def test_query_by_id_list(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return MockStacFeatureResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        result = self.api.query_by_id(scene_id=["ABC123"], collection="y")

        assert self.expected_result_after_query_item_assets == result

    def test_query_empty_response(self, monkeypatch):
        def mock_post(*args, **kwargs):
            return MockStacFeatureCollectionEmptyResponse()

        monkeypatch.setattr("requests.Session.post", mock_post)

        result = self.api.query(
            location=[-63.9, -8.8, -63.7, -8.7],
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN"],
        )

        assert self.expected_result_from_empty_query_response == result

    def test_to_geodataframe(self):
        gdf = self.api.to_geodataframe(self.expected_result_from_query)

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
        with pytest.raises(Exception):
            api = Cbers4aAPI()
            api.download(self.expected_result_from_query, bands=["blue"])

    def test_empty_credentials_exception(self):
        with pytest.raises(Exception):
            api = Cbers4aAPI("")
            api.download(self.expected_result_from_query, bands=["blue"])

    def test_missing_credentials_exception_geodataframe(self):
        with pytest.raises(Exception):
            api = Cbers4aAPI("")
            gdf = api.to_geodataframe(self.expected_result_from_query)
            api.download(gdf, bands=["blue"])

    def test_download(self, monkeypatch, tmp_path):
        def mock_get(*args, **kwargs):
            return MockStacFeatureResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        self.api.download(
            products=self.expected_result_from_query,
            bands=["blue"],
            threads=1,
            outdir=tmp_path.as_posix(),
            with_folder=True,
        )

        with open(f"{tmp_path.as_posix()}/ABC123/image.tif", "rb") as f:
            assert f.read() == b"dummydata"

        remove(f"{tmp_path.as_posix()}/ABC123/image.tif")

    def test_download_gdf(self, monkeypatch, tmp_path):
        def mock_get(*args, **kwargs):
            return MockStacFeatureResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        gdf = self.api.to_geodataframe(self.expected_result_from_query)

        self.api.download(
            products=gdf,
            bands=["blue"],
            threads=1,
            outdir=tmp_path.as_posix(),
            with_folder=True,
        )

        with open(f"{tmp_path.as_posix()}/ABC123/image.tif", "rb") as f:
            assert f.read() == b"dummydata"

        remove(f"{tmp_path.as_posix()}/ABC123/image.tif")
