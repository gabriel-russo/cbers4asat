# Cbers4asat

## Description
Python library to consume data from INPE'S CBERS4A and AMAZONIA1 catalog and perform operations.

 [![Latest Version](https://img.shields.io/pypi/v/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)
 [![Latest Version](https://img.shields.io/pypi/l/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)
 [![Latest Version](https://img.shields.io/pypi/pyversions/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)
 [![Latest Version](https://img.shields.io/pypi/dm/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)

## Installation using pip

`pip install cbers4asat`

## Summary
* [Description](#description)
* [Documentation](#documentation)
* [Basic examples](#examples)
    * [Search by Bounding box](#search-by-bounding-box)
    * [Search by Path and Row](#search-by-path-and-row)
    * [Download products](#downloading-products)
    * [Convert product collection to GeoDataFrame](#convert-products-collection-to-geodataframe)
    * [Download products from GeoDataFrame ](#downloading-products-in-geodataframe)
* [License](#license)

## Documentation

- query: *Do a search on INPE's catalog*
  - Parameters:
    - **location** -> `List[float] | Tuple(int, int)` : Bounding box or Path Row of area of interest
    - **initial_date**: -> `date` : Range start date
    - **end_date** -> `date` : Range end date
    - **cloud** -> `int` : Cloud percentage
    - **limit** -> `int` : Limit of product returned by query
    - **collections** (*Optional*) -> `List[str]` : Collection dataset
----
  - download: *Download bands from query result*
    - Parameters:
      - **products** -> `Dict | GeoDataFrame` : Returned scenes from query
      - **bands** -> `List[str]` : Available bands from scenes
      - **threads** (*Optional*) -> `int` : Thread limit for parallel download
      - **outdir** (*Optional*) -> `str` : Output directory
      - **with_folder** (*Optional*) -> `bool` : Option to enable download grouping
----
  - to_geodataframe: *Convert GeoJSON-like dictionary to GeoDataFrame*
    - Parameters:
      - **products** -> `Dict` : Returned scenes from query
      - **crs** (*Optional*)-> `str` : Coordinate reference (e.g.: EPSG:4326)
----
## Examples

### Search by bounding box:

```python
# Import cbers4asat and datetime lib
from src.cbers4asat import Cbers4aAPI
from datetime import date

# (Only required for downloading) Same Login used in http://www2.dgi.inpe.br/catalogo/explore
# You can add later using a setter: api.user('my@mail.com')
api = Cbers4aAPI('my@mail.com')

# Bounding box of area of interest
bbox = [-63.92944335937501,
        -8.819260401678381,
        -63.79211425781251,
        -8.722218306198739]

# Date interval
initial_date = date(2021, 8, 25)
end_date = date(2021, 9, 25)

# Do a search on inpe's catalog
products = api.query(location=bbox,
                     initial_date=initial_date,
                     end_date=end_date,
                     cloud=100,
                     limit=100,
                     collections=['AMAZONIA1_WFI_L2_DN', 'CBERS4A_WPM_L4_DN'])  # Optional

print(products)
# {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'id': 'AMAZONIA1_WFI03901620210911CB11', ...
```

### Search by path and row:

```python
from src.cbers4asat import Cbers4aAPI
from datetime import date

api = Cbers4aAPI('my@mail.com')

# Path and row respectively
path_row = (229, 124)

initial_date = date(2021, 8, 25)
end_date = date(2021, 9, 25)

# Fazer uma busca no catálogo e exibir resultados
products = api.query(location=path_row,
                     initial_date=initial_date,
                     end_date=end_date,
                     cloud=100,
                     limit=100,
                     collections=['AMAZONIA1_WFI_L2_DN', 'CBERS4A_WPM_L4_DN'])  # Optional

print(products)
# {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'id': 'CBERS4A_WPM22912420210830', ...
```

### Downloading products:

```python
from src.cbers4asat import Cbers4aAPI
from datetime import date

api = Cbers4aAPI('my@mail.com')

path_row = (229, 124)

initial_date = date(2021, 8, 25)
end_date = date(2021, 9, 25)

products = api.query(location=path_row,
                     initial_date=initial_date,
                     end_date=end_date,
                     cloud=100,
                     limit=1,
                     collections=['CBERS4A_WPM_L4_DN'])

# Chosen bands: red, green and blue
# Output is optional, if you not fill, the current directory is used
api.download(products=products,
             bands=['red', 'green', 'blue'],
             threads=3,  # Threads for simultaneous download
             outdir='./downloads',
             with_folder=True)  # Group downloaded bands into subfolder(s) in the ./downloads directory

# ./downloads directory will be like this if with_folder=true :
# downloads/
# +- CBERS4A_WPM22912420210830/
# ++- CBERS_4A_WPM_20210830_229_124_L4_BAND3.tif
# ++- CBERS_4A_WPM_20210830_229_124_L4_BAND2.tif
# ++- CBERS_4A_WPM_20210830_229_124_L4_BAND1.tif
```

### Convert products collection to GeoDataFrame:

```python
from src.cbers4asat import Cbers4aAPI
from datetime import date
import geopandas as gpd

api = Cbers4aAPI('my@mail.com')

path_row = (229, 124)

initial_date = date(2021, 8, 25)
end_date = date(2021, 9, 25)

products = api.query(location=path_row,
                     initial_date=initial_date,
                     end_date=end_date,
                     cloud=100,
                     limit=3,
                     collections=['CBERS4A_WPM_L4_DN'])

# Convert products collection to GeoDataFrame with SIRGAS 2000 Coordinate reference
gdf = api.to_geodataframe(products, 'EPSG:4674')

print(gdf.to_string())
```
### Downloading products in GeoDataFrame:

```python
from src.cbers4asat import Cbers4aAPI
from datetime import date
import geopandas as gpd

api = Cbers4aAPI('my@mail.com')

bbox = [-63.92944335937501,
        -8.819260401678381,
        -63.79211425781251,
        -8.722218306198739]

initial_date = date(2021, 8, 25)
end_date = date(2021, 9, 25)

products = api.query(location=bbox,
                     initial_date=initial_date,
                     end_date=end_date,
                     cloud=100,
                     limit=3,
                     collections=['CBERS4A_WPM_L4_DN'])

# You can filter using Geo-Pandas methods and then downloading...
gdf = api.to_geodataframe(products)

# Same logic for downloading GeoDataFrame and GeoJSON-like dictionary
api.download(products=gdf, bands=['red'], outdir='./downloads', with_folder=False)
```

# Contributing 

We invite anyone to participate by contributing code, reporting bugs, fixing bugs, 
writing documentation and tutorials and discussing the future of this project. Please check [CONTRIBUTING.md](https://github.com/gabriel-russo/cbers4asat/blob/master/CONTRIBUTING.md)

# License
Copyright (c) 2022 Gabriel Russo

Copyright (c) 2020 Sandro Klippel

Use is provided under the MIT License. See under 
[LICENSE](https://github.com/gabriel-russo/cbers4asat/blob/master/LICENSE) for more details
