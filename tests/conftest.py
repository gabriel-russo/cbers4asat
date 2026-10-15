from pathlib import Path
from unittest.mock import patch

import pytest
from rasterio import open as rasterio_open

from cbers4asat import Cbers4aAPI
from cbers4asat.tools import read_geojson
from mocks import (
    MockResponse,
    MockStacFeatureCollectionEmptyResponse,
    MockStacFeatureCollectionResponse,
    MockStacFeatureResponse,
)

DATA_DIR = Path(__file__).parent.resolve() / "data"


@pytest.fixture
def data_dir() -> Path:
    """Read-only directory with the reference data shipped with the tests."""
    return DATA_DIR


@pytest.fixture
def api() -> Cbers4aAPI:
    return Cbers4aAPI("test@test.com")


@pytest.fixture
def mock_collection_response():
    with patch(
        "requests.Session.post",
        return_value=MockStacFeatureCollectionResponse(),
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_empty_collection_response():
    with patch(
        "requests.Session.post",
        return_value=MockStacFeatureCollectionEmptyResponse(),
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_item_response():
    with patch(
        "requests.Session.get",
        return_value=MockStacFeatureResponse(),
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_grid_response():
    with patch("requests.Session.get", return_value=MockResponse()) as mocked:
        yield mocked


@pytest.fixture
def rgb_assert_metadata(data_dir):
    with rasterio_open(data_dir / "BAND3.tif") as raster:
        metadata = raster.meta.copy()

    metadata.update(count=3)

    return metadata


@pytest.fixture
def pansharp_assert_metadata(data_dir):
    with rasterio_open(data_dir / "PANSHARP.tif") as raster:
        return raster.meta.copy()


@pytest.fixture
def crop_assert_metadata(data_dir):
    with rasterio_open(data_dir / "CLIP.tif") as raster:
        return raster.meta.copy()


@pytest.fixture
def geojson_object():
    return {
        "features": [
            {
                "geometry": {
                    "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
                    "type": "Polygon",
                },
                "properties": {},
                "type": "Feature",
            }
        ],
        "type": "FeatureCollection",
    }


@pytest.fixture
def crop_geojson_mask(data_dir: Path):
    return read_geojson(data_dir / "MASK.geojson")
