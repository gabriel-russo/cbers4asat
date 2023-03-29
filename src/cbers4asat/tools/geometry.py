from geojson import load as geojson_load


def read_geojson(geojson_file: str):
    """
    Read a GeoJSON file into a GeoJSON object.

    Args:
        geojson_file: GeoJson file path
    Returns:
        GeoJson object
    """
    with open(geojson_file) as f:
        return geojson_load(f)
