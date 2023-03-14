from rasterio import open as rasterio_open
import pytest
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent.resolve() / 'data'


@pytest.fixture
@pytest.mark.datafiles(
    FIXTURE_DIR / 'BAND3.tif'
)
def rgb_assert_metadata(datafiles):
    metadata = rasterio_open(datafiles / 'BAND3.tif').meta.copy()

    metadata.update(count=3)

    yield metadata
