from requests import Session
from os.path import basename, join
from os import getcwd


def grid_download(
    satellite: str = "cbers4a", sensor: str = "mux", outdir: str = getcwd()
):
    """
    Download tiling grid from CBERS-04A and AMAZONIA1

    Args:
        satellite: "cbers4a" or "amazonia1"
        sensor: "mux" or "wfi"
        outdir: Output path
    Examples:
        - grid_download("cbers4a", "mux")
        - grid_download(satellite="amazonia1", "wfi", outdir="./downloads")
    Returns:
        .zip file
    """
    grids = {
        "cbers4a": {
            "mux": "http://www.dgi.inpe.br/documentacao/arquivos/grid_cbers4a_mux.zip/@@download/file/grid_cbers4a_mux.zip",
            "wfi": "http://www.dgi.inpe.br/documentacao/arquivos/grid_cbers4a_wfi.zip/@@download/file/grid_cbers4a_wfi.zip",
        },
        "amazonia1": {
            "wfi": "http://www.dgi.inpe.br/documentacao/arquivos/grid_amazonia1_wfi_sa.zip/@@download/file/grid_amazonia1_wfi_sa.zip"
        },
    }

    get_satellite = grids.get(satellite.lower(), None)

    if get_satellite:
        get_sensor = get_satellite.get(sensor.lower(), None)

        if get_sensor:
            req = Session().get(url=get_sensor, stream=True, allow_redirects=True)

            filename = basename(get_sensor)

            if req.status_code == 200:
                with open(join(outdir, filename), "wb") as f:
                    for chunk in req.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
        else:
            raise ValueError("Sensors available: mux and wfi")
    else:
        raise ValueError("Satellites available: cbers4a and amazonia1")
