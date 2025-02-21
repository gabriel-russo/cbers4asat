from os import getcwd
from os.path import basename, join
from typing import Literal
from requests import Session, HTTPError


def grid_download(
    satellite: Literal["cbers4a", "amazonia1"] = "cbers4a",
    sensor: Literal["mux", "wfi"] = "mux",
    outdir: str = getcwd(),
) -> None:
    """
    Download path and row grid from CBERS-04A and AMAZONIA1

    Args:
        satellite: "cbers4a" or "amazonia1"
        sensor: "mux" or "wfi"
        outdir: Output path
    Examples:
        - grid_download("cbers4a", "mux")
        - grid_download(satellite="amazonia1", "wfi", outdir="./downloads")
    Returns:
        .kmz file
    """
    grids = {
        "cbers4a": {
            "mux": "http://www.obt.inpe.br/OBT/assuntos/catalogo-cbers-amz-1/grid_cbers4a_mux.kmz",
            "wfi": "http://www.obt.inpe.br/OBT/assuntos/catalogo-cbers-amz-1/grid_cbers4a_wfi.kmz",
        },
        "amazonia1": {
            "wfi": "http://www.obt.inpe.br/OBT/assuntos/catalogo-cbers-amz-1/grid_amazonia1_wfi_sa.kmz"
        },
    }

    get_satellite = grids.get(satellite.lower(), None)

    if get_satellite:
        get_sensor = get_satellite.get(sensor.lower(), None)

        if get_sensor:
            with Session() as session:
                try:
                    req = session.get(url=get_sensor, stream=True, allow_redirects=True)
                    req.raise_for_status()

                    filename = basename(get_sensor)
                    with open(join(outdir, filename), "wb") as f:
                        for chunk in req.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)

                except HTTPError as err:
                    raise Exception(f"Download unavailable. Error: {err}")
        else:
            raise ValueError("Sensors available: mux and wfi")
    else:
        raise ValueError("Satellites available: cbers4a and amazonia1")
