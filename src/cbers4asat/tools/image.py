from rasterio import open as rasterio_open
from os import getcwd, makedirs
from os.path import isfile, join, exists
from numpy import stack


def rgbn_composite(
    red: str,
    green: str,
    blue: str,
    nir: str = None,
    outdir: str = getcwd(),
    filename: str = "rgbn_composite.tif",
):
    """
    Stack bands

    Args:
        red: Red channel
        green: Green channel
        blue: Blue channel
        nir: (Optional) Nir channel
        outdir: Output path
        filename: Output filename
    Returns:
        GeoTIFF file
    """
    if isfile(red) and isfile(green) and isfile(blue):
        bands = [
            rasterio_open(red),
            rasterio_open(green),
            rasterio_open(blue),
        ]

        if nir is not None and isfile(nir):
            bands.append(rasterio_open(nir))
        elif nir is not None and not isfile(nir):
            raise FileNotFoundError("Check band's file path")

        if not exists(outdir):
            makedirs(outdir)

        bands_metadata = bands[0].meta.copy()

        merged = stack([band.read(1) for band in bands])

        for band in bands:
            band.close()

        count, height, width = merged.shape

        bands_metadata.update(width=width, height=height, count=count, nodata=0)

        with rasterio_open(join(outdir, filename), "w", **bands_metadata) as raster:
            raster.write(merged)

    else:
        raise FileNotFoundError("Check band's file path")
