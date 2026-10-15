from rasterio import open as rasterio_open
from shapely.geometry import Polygon

from cbers4asat.tools import (
    clip,
    grid_download,
    pansharpening,
    read_geojson,
    rgbn_composite,
)


class TestTools:
    def test_rgbn_composite(self, rgb_assert_metadata, data_dir, tmp_path):
        rgbn_composite(
            red=(data_dir / "BAND3.tif").as_posix(),
            green=(data_dir / "BAND2.tif").as_posix(),
            blue=(data_dir / "BAND1.tif").as_posix(),
            outdir=tmp_path.as_posix(),
            filename="RGBN_COMPOSITE_TEST.tif",
        )

        with rasterio_open(tmp_path / "RGBN_COMPOSITE_TEST.tif") as raster:
            assert rgb_assert_metadata == raster.meta

    def test_grid_download(self, mock_grid_response, tmp_path):
        grid_download(satellite="amazonia1", sensor="wfi", outdir=tmp_path.as_posix())

        with open(tmp_path / "grid_amazonia1_wfi_sa.kmz", "rb") as f:
            assert f.read() == b"dummydata"

    def test_pansharp(self, pansharp_assert_metadata, data_dir, tmp_path):
        pansharpening(
            panchromatic=(data_dir / "BAND0.tif").as_posix(),
            multispectral=(data_dir / "MULTISPECTRAL.tif").as_posix(),
            filename="PANSHARP_TEST.tif",
            outdir=tmp_path.as_posix(),
        )

        with rasterio_open(tmp_path / "PANSHARP_TEST.tif") as raster:
            assert raster.meta == pansharp_assert_metadata

    def test_read_geojson(self, geojson_object, data_dir):
        data = read_geojson(data_dir / "test.geojson")

        assert data == geojson_object

    def test_crop_geojson(
        self, crop_assert_metadata, crop_geojson_mask, data_dir, tmp_path
    ):
        clip(
            (data_dir / "BAND3.tif").as_posix(),
            crop_geojson_mask,
            outdir=tmp_path.as_posix(),
            filename="CLIP_TEST.tif",
        )

        with rasterio_open(tmp_path / "CLIP_TEST.tif") as raster:
            assert raster.meta == crop_assert_metadata

    def test_crop_geometry(self, crop_assert_metadata, data_dir, tmp_path):
        geom = Polygon(
            [
                [808075.915309446281753, 8605496.975895769894123],
                [808075.915309446281753, 8607398.786970686167479],
                [811660.09771986969281, 8607398.786970686167479],
                [811660.09771986969281, 8605496.975895769894123],
                [808075.915309446281753, 8605496.975895769894123],
            ]
        )

        clip((data_dir / "BAND3.tif").as_posix(), geom, outdir=tmp_path.as_posix())

        with rasterio_open(tmp_path / "raster_clip.tif") as raster:
            assert raster.meta == crop_assert_metadata
