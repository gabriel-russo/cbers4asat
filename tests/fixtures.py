from rasterio import open as rasterio_open
import pytest
from pathlib import Path
from os import remove

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.fixture
def rgb_assert_metadata(datafiles):
    with rasterio_open(datafiles / "BAND3.tif") as raster:
        metadata = raster.meta.copy()

    metadata.update(count=3)

    yield metadata


@pytest.fixture
def pansharp_assert_metadata(datafiles):
    with rasterio_open(f"{datafiles}/PANSHARP.tif") as raster:
        metadata = raster.meta.copy()

    remove(f"{datafiles}/PANSHARP.tif")
    yield metadata
