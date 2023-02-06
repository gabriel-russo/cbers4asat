from cbers4asat import Cbers4aAPI
import pytest
from datetime import date


class MockStacfeatureCollectionResponse:
    def __init__(self):
        self.status_code = 200

    def raise_for_status(self):
        pass

    @staticmethod
    def json():
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "ABC123",
                    "collection": "y",
                    "geometry": {"type": "Polygon", "coordinates": []},
                    "bbox": [],
                    "properties": {"x": "XYZ"},
                    "assets": {"band": {"x": "y"}},
                    "links": [{"x": "y"}],
                }
            ],
        }


class MockStacfeatureResponse:
    def __init__(self):
        self.status_code = 200

    def raise_for_status(self):
        pass

    @staticmethod
    def json():
        return {
            "type": "Feature",
            "id": "ABC123",
            "collection": "y",
            "geometry": {"type": "Polygon", "coordinates": []},
            "bbox": [],
            "properties": {"x": "XYZ"},
            "assets": {"band": {"x": "y"}},
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
                "geometry": {"type": "Polygon", "coordinates": []},
                "bbox": [],
                "properties": {"x": "XYZ"},
                "assets": {"band": {"x": "y"}},
            }
        ],
    }

    def test_user(self):
        assert "test@test.com" in self.api.user

    def test_set_user(self):
        self.api.user = "another@test.com"

        assert self.api.user == "another@test.com"

    @pytest.fixture(autouse=True)
    def test_query(self, monkeypatch):
        def mock_post(*args, **kwargs):
            return MockStacfeatureCollectionResponse()

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

    @pytest.fixture(autouse=True)
    def test_query_by_id_str(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return MockStacfeatureResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        result = self.api.query_by_id("ABC123")

        assert self.expected_result == result

    @pytest.fixture(autouse=True)
    def test_query_by_id_list(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return MockStacfeatureResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        result = self.api.query_by_id(["ABC123"])

        assert self.expected_result == result
