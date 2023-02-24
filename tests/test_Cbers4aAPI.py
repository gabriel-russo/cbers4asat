from cbers4asat import Cbers4aAPI
import pytest
from datetime import date
from os import remove
from shapely.geometry import Polygon


class MockStacFeatureCollectionResponse:
    def __init__(self):
        self.status_code = 200

    def raise_for_status(self):
        pass

    @staticmethod
    def iter_content(chunk_size):
        yield b"dummydata"

    @staticmethod
    def json():
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "ABC123",
                    "collection": "y",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-48.3106, -15.3637],
                                [-48.3106, -16.4178],
                                [-47.2492, -16.4178],
                                [-47.2492, -15.3637],
                                [-48.3106, -15.3637],
                            ]
                        ],
                    },
                    "bbox": [-48.3106, -16.4178, -47.2492, -15.3637],
                    "properties": {"x": "XYZ"},
                    "assets": {"blue": {"href": "http://test.dev/image.tif"}},
                    "links": [{"x": "y"}],
                }
            ],
        }


class MockStacFeatureResponse:
    def __init__(self):
        self.status_code = 200

    def raise_for_status(self):
        pass

    @staticmethod
    def iter_content(chunk_size):
        yield b"dummydata"

    @staticmethod
    def json():
        return {
            "type": "Feature",
            "id": "ABC123",
            "collection": "y",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-48.3106, -15.3637],
                        [-48.3106, -16.4178],
                        [-47.2492, -16.4178],
                        [-47.2492, -15.3637],
                        [-48.3106, -15.3637],
                    ]
                ],
            },
            "bbox": [-48.3106, -16.4178, -47.2492, -15.3637],
            "properties": {"x": "XYZ"},
            "assets": {"blue": {"href": "http://test.dev/image.tif"}},
            "links": [{"x": "y"}],
        }


class TestCbers4aAPI:
    api = Cbers4aAPI("test@test.com")
    expected_result = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "ABC123",
                "collection": "y",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-48.3106, -15.3637],
                            [-48.3106, -16.4178],
                            [-47.2492, -16.4178],
                            [-47.2492, -15.3637],
                            [-48.3106, -15.3637],
                        ]
                    ],
                },
                "bbox": [-48.3106, -16.4178, -47.2492, -15.3637],
                "properties": {"x": "XYZ"},
                "assets": {"blue": {"href": "http://test.dev/image.tif"}},
            }
        ],
    }

    def test_user(self):
        assert "test@test.com" in self.api.user

    def test_set_user(self):
        self.api.user = "another@test.com"
        assert self.api.user == "another@test.com"

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

        assert self.expected_result == result

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

        assert self.expected_result == result

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

        assert bbox.is_valid

        result = self.api.query(
            location=bbox,
            initial_date=date(2021, 1, 1),
            end_date=date(2021, 2, 1),
            cloud=100,
            limit=1,
            collections=["CBERS4A_WPM_L4_DN"],
        )

        assert self.expected_result == result

    def test_query_by_id_str(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return MockStacFeatureResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        result = self.api.query_by_id("ABC123")

        assert self.expected_result == result

    def test_query_by_id_list(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return MockStacFeatureResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        result = self.api.query_by_id(["ABC123"])

        assert self.expected_result == result

    def test_to_geodataframe(self):
        gdf = self.api.to_geodataframe(self.expected_result)
        assert type(gdf).__name__ == "GeoDataFrame"
        assert gdf.crs == "EPSG:4326"
        assert len(gdf) == 1

    def test_download(self, monkeypatch, tmp_path):
        def mock_get(*args, **kwargs):
            return MockStacFeatureCollectionResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        self.api.download(
            products=self.expected_result,
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

        gdf = self.api.to_geodataframe(self.expected_result)

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
