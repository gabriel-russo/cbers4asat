# Exemplos

* [Buscando produtos com bounding box](#buscando-produtos-com-bounding-box)
* [Buscando produtos com órbita e ponto](#buscando-produtos-com-orbita-e-ponto)
* [Buscando produto(s) por ID](#buscando-produtos-por-id)
* [Download de produtos](#download-de-produtos)
* [Converter coleção de produtos para GeoDataFrame](#converter-colecao-de-produtos-para-geodataframe)
* [Download de produtos no GeoDataFrame ](#download-de-produtos-no-geodataframe)

## Buscando produtos com Bounding Box:

```python
# Importar biblioteca do cbers4asat e datetime
from cbers4asat import Cbers4aAPI
from datetime import date

# (Requisito apenas para download) 
# Login utilizado no http://www2.dgi.inpe.br/catalogo/explore
# Pode ser adicionado depois com o setter: api.user('meu@email.com')
api = Cbers4aAPI('seu.login@email.com')

# Bouding Box escolhido
bbox = [-63.92944335937501,
        -8.819260401678381,
        -63.79211425781251,
        -8.722218306198739]

# Intervalo de data para a busca
data_inicial = date(2021, 8, 25)
data_final = date(2021, 9, 25)

# Fazer uma busca no catálogo e exibir resultados
produtos = api.query(location=bbox,
                     initial_date=data_inicial,
                     end_date=data_final,
                     cloud=100,
                     limit=100,
                     collections=['AMAZONIA1_WFI_L2_DN', 'CBERS4A_WPM_L4_DN'])  # Opcional

print(produtos)
# {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'id': 'AMAZONIA1_WFI03901620210911CB11', ...
```

## Buscando produtos com órbita e ponto:

```python
from cbers4asat import Cbers4aAPI
from datetime import date

api = Cbers4aAPI('seu.login@email.com')

# Órbita ponto (respectivamente) escolhida
path_row = (229, 124)

data_inicial = date(2021, 8, 25)
data_final = date(2021, 9, 25)

produtos = api.query(location=path_row,
                     initial_date=data_inicial,
                     end_date=data_final,
                     cloud=100,
                     limit=100,
                     collections=['AMAZONIA1_WFI_L2_DN', 'CBERS4A_WPM_L4_DN'])

print(produtos)
# {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'id': 'CBERS4A_WPM22912420210830', ...
```

## Buscando produtos por ID

```python
from cbers4asat import Cbers4aAPI

api = Cbers4aAPI('meu@email.com')

# Buscando pelo ID de uma cena
produto = api.query_by_id('CBERS4A_WPM22912420210830')

print(produto)

# Para mais de um produto:

produtos = api.query_by_id(['CBERS4A_WPM22912420210830', 'AMAZONIA1_WFI03901620210911CB11'])

print(produtos)

```

## Download de produtos:

```python
from cbers4asat import Cbers4aAPI
from datetime import date

api = Cbers4aAPI('seu.login@email.com')

path_row = (229, 124)

data_inicial = date(2021, 8, 25)
data_final = date(2021, 9, 25)

produtos = api.query(location=path_row,
                     initial_date=data_inicial,
                     end_date=data_final,
                     cloud=100,
                     limit=1,
                     collections=['CBERS4A_WPM_L4_DN'])

# Bandas escolhidas: vermelha, verde e azul
# Output do download é opcional e caso omitido será usado o diretório atual
api.download(products=produtos,
             bands=['red', 'green', 'blue'],
             threads=3,  # Numero de downloads simultâneos
             outdir='./downloads',
             with_folder=True)  # Agrupar bandas de uma cena(s) em subpasta(s) no diretório ./downloads

# O diretório downloads ficará assim com o with_folder=true :
# downloads/
# +- CBERS4A_WPM22912420210830/
# ++- CBERS_4A_WPM_20210830_229_124_L4_BAND3.tif
# ++- CBERS_4A_WPM_20210830_229_124_L4_BAND2.tif
# ++- CBERS_4A_WPM_20210830_229_124_L4_BAND1.tif
```

## Converter coleção de produtos para GeoDataFrame:

```python
from cbers4asat import Cbers4aAPI
from datetime import date
import geopandas as gpd

api = Cbers4aAPI('seu.login@email.com')

path_row = (229, 124)

data_inicial = date(2021, 8, 25)
data_final = date(2021, 9, 25)

produtos = api.query(location=path_row,
                     initial_date=data_inicial,
                     end_date=data_final,
                     cloud=100,
                     limit=3,
                     collections=['CBERS4A_WPM_L4_DN'])

# Converter os produtos para GeoDataFrame
gdf = api.to_geodataframe(produtos, 'EPSG:4674')

print(gdf.to_string())
```

## Download de produtos no GeoDataFrame:

```python
from cbers4asat import Cbers4aAPI
from datetime import date
import geopandas as gpd

api = Cbers4aAPI('seu.login@email.com')

bbox = [-63.92944335937501,
        -8.819260401678381,
        -63.79211425781251,
        -8.722218306198739]

data_inicial = date(2021, 8, 25)
data_final = date(2021, 9, 25)

produtos = api.query(location=bbox,
                     initial_date=data_inicial,
                     end_date=data_final,
                     cloud=100,
                     limit=3,
                     collections=['CBERS4A_WPM_L4_DN'])

gdf = api.to_geodataframe(produtos)

# Utiliza a mesma lógica que o download de produtos no formato dicionário
api.download(products=gdf, bands=['red'], outdir='./downloads', with_folder=False)
```