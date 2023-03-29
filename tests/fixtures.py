from rasterio import open as rasterio_open
import pytest
from pathlib import Path
from os import remove
from cbers4asat.tools import read_geojson

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.fixture
def rgb_assert_metadata(datafiles):
    with rasterio_open(datafiles / "BAND3.tif") as raster:
        metadata = raster.meta.copy()

    metadata.update(count=3)

    yield metadata


@pytest.fixture
def pansharp_assert_metadata(datafiles):
    with rasterio_open(datafiles / "PANSHARP.tif") as raster:
        metadata = raster.meta.copy()

    remove(f"{datafiles}/PANSHARP.tif")
    yield metadata


@pytest.fixture
def geojson_object():
    yield {
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
def crop_assert_metadata(datafiles):
    with rasterio_open(datafiles / "CLIP.tif") as raster:
        metadata = raster.meta.copy()

    remove(f"{datafiles}/CLIP.tif")
    yield metadata


@pytest.fixture
def crop_geojson_mask(datafiles):
    yield read_geojson(f"{datafiles}/MASK.geojson")
