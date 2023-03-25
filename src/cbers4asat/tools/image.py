from rasterio import open as rasterio_open
from os import getcwd, makedirs
from os.path import isfile, join, exists
from numpy import stack, float32
from skimage.transform import resize
from skimage.color import rgb2hsv, hsv2rgb


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


def pansharpening(
    panchromatic: str = None,
    multispectral: str = None,
    outdir: str = getcwd(),
    filename: str = "pansharp.tif",
):
    """
    Pansharpen multispectral file

    Args:
        panchromatic: Panchromatic band (Band 0)
        multispectral: Multispectral band
        outdir: Output Directory (default Current working directory)
        filename: Output file name (default pansharpened_$(datetime))
    Returns:
        GeoTIFF file
    """

    if isfile(panchromatic) and isfile(multispectral):
        if not exists(outdir):
            makedirs(outdir)

        BIT_DEPTH = 65535

        with rasterio_open(multispectral) as multispectral_file:
            multispectral_array = multispectral_file.read().astype(
                dtype=float32, copy=False
            )

        # Normalize RGB to 0..1 interval
        multispectral_array = multispectral_array / BIT_DEPTH

        multispectral_hsv = rgb2hsv(multispectral_array, channel_axis=0)

        del multispectral_array

        with rasterio_open(panchromatic) as panchromatic_file:
            # Create metadata copy and add expected output data
            panchromatic_metadata = panchromatic_file.meta.copy()
            panchromatic_metadata.update(count=3, dtype="float32")

            # Get matrix data
            panchromatic_array = panchromatic_file.read(1).astype(
                dtype=float32, copy=False
            )

        height, width = panchromatic_array.shape

        # Resizing all bands to pansharp dimensions
        multispectral_hsv = resize(
            multispectral_hsv, (3, height, width), anti_aliasing=False
        )

        # normalize pan to 0..1 interval
        panchromatic_array = panchromatic_array / BIT_DEPTH

        # Replacing Value component by Panchromatic
        multispectral_hsv[2, :, :] = panchromatic_array

        del panchromatic_array

        with rasterio_open(
            join(outdir, filename), "w", **panchromatic_metadata
        ) as raster:
            raster.write(hsv2rgb(multispectral_hsv, channel_axis=0))

    else:
        raise FileNotFoundError("Invalid files")
