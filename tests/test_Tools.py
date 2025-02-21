from os import remove
from pathlib import Path
import pytest
from cbers4asat.tools import (
    rgbn_composite,
    grid_download,
    pansharpening,
    clip,
    read_geojson,
)
from rasterio import open as rasterio_open
from shapely.geometry import Polygon
from fixtures import (
    rgb_assert_metadata,
    pansharp_assert_metadata,
    geojson_object,
    crop_assert_metadata,
    crop_geojson_mask,
)

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


class MockResponse:
    def __init__(self):
        self.status_code = 200

    def raise_for_status(self):
        pass

    @staticmethod
    def iter_content(chunk_size):
        yield b"dummydata"


class TestTools:
    @pytest.mark.datafiles(
        FIXTURE_DIR / "BAND1.tif",
        FIXTURE_DIR / "BAND2.tif",
        FIXTURE_DIR / "BAND3.tif",
        on_duplicate="ignore",
    )
    def test_rgbn_composite(self, rgb_assert_metadata, tmp_path, datafiles):
        rgbn_composite(
            red=f"{datafiles}/BAND3.tif",
            green=f"{datafiles}/BAND2.tif",
            blue=f"{datafiles}/BAND1.tif",
            outdir=tmp_path.as_posix(),
            filename="RGBN_COMPOSITE_TEST.tif",
        )

        with rasterio_open(f"{tmp_path.as_posix()}/RGBN_COMPOSITE_TEST.tif") as raster:
            assert rgb_assert_metadata == raster.meta

        remove(f"{tmp_path.as_posix()}/RGBN_COMPOSITE_TEST.tif")

    def test_grid_download(self, monkeypatch, tmp_path):
        def mock_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        grid_download(satellite="amazonia1", sensor="wfi", outdir=tmp_path.as_posix())

        with open(f"{tmp_path.as_posix()}/grid_amazonia1_wfi_sa.kmz", "rb") as f:
            assert f.read() == b"dummydata"

        remove(f"{tmp_path.as_posix()}/grid_amazonia1_wfi_sa.kmz")

    @pytest.mark.datafiles(
        FIXTURE_DIR / "MULTISPECTRAL.tif",
        FIXTURE_DIR / "BAND0.tif",
        FIXTURE_DIR / "PANSHARP.tif",
        on_duplicate="ignore",
    )
    def test_pansharp(self, pansharp_assert_metadata, tmp_path, datafiles):
        pansharpening(
            panchromatic=f"{datafiles}/BAND0.tif",
            multispectral=f"{datafiles}/MULTISPECTRAL.tif",
            filename=f"PANSHARP_TEST.tif",
            outdir=tmp_path.as_posix(),
        )

        with rasterio_open(f"{tmp_path.as_posix()}/PANSHARP_TEST.tif") as raster:
            assert raster.meta == pansharp_assert_metadata

        remove(f"{tmp_path.as_posix()}/PANSHARP_TEST.tif")

    @pytest.mark.datafiles(FIXTURE_DIR / "test.geojson", on_duplicate="ignore")
    def test_read_geojson(self, geojson_object, datafiles):
        data = read_geojson(f"{datafiles}/test.geojson")

        assert data == geojson_object

    @pytest.mark.datafiles(
        FIXTURE_DIR / "BAND3.tif",
        FIXTURE_DIR / "MASK.geojson",
        FIXTURE_DIR / "CLIP.tif",
        on_duplicate="ignore",
    )
    def test_crop_geojson(
        self, crop_assert_metadata, crop_geojson_mask, tmp_path, datafiles
    ):
        clip(
            f"{datafiles}/BAND3.tif",
            crop_geojson_mask,
            outdir=tmp_path.as_posix(),
            filename="CLIP_TEST.tif",
        )

        with rasterio_open(f"{tmp_path.as_posix()}/CLIP_TEST.tif") as raster:
            assert raster.meta == crop_assert_metadata

        remove(f"{tmp_path.as_posix()}/CLIP_TEST.tif")

    @pytest.mark.datafiles(
        FIXTURE_DIR / "BAND3.tif",
        FIXTURE_DIR / "CLIP.tif",
        on_duplicate="ignore",
    )
    def test_crop_geometry(self, crop_assert_metadata, tmp_path, datafiles):
        geom = Polygon(
            [
                [808075.915309446281753, 8605496.975895769894123],
                [808075.915309446281753, 8607398.786970686167479],
                [811660.09771986969281, 8607398.786970686167479],
                [811660.09771986969281, 8605496.975895769894123],
                [808075.915309446281753, 8605496.975895769894123],
            ]
        )

        clip(f"{datafiles}/BAND3.tif", geom, outdir=tmp_path.as_posix())

        with rasterio_open(f"{tmp_path.as_posix()}/raster_clip.tif") as raster:
            assert raster.meta == crop_assert_metadata

        remove(f"{tmp_path.as_posix()}/raster_clip.tif")
