# Cbers4asat

## Descrição

Biblioteca Python para consultar o catálogo e realizar operações com dados do CBERS4A e AMAZONIA1.

[![Latest Version](https://img.shields.io/pypi/v/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)
[![Latest Version](https://img.shields.io/pypi/l/cbers4asat?style=plastic)](https://github.com/gabriel-russo/cbers4asat/blob/master/LICENSE)
[![Latest Version](https://img.shields.io/pypi/pyversions/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)
[![Latest Version](https://img.shields.io/pypi/dm/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)
![PyPI - Status](https://img.shields.io/pypi/status/cbers4asat?style=plastic)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

> [Read this README in english](https://github.com/gabriel-russo/cbers4asat/blob/master/en-US_README.md) 🇺🇸

## Download da biblioteca com pip

`pip install cbers4asat`

## Sumário

* [Descrição](#descrição)
* [Documentação](#descrição-métodos)
* [Exemplos básicos](#exemplos)
    * [Buscando produtos com bounding box](#buscando-produtos-com-bounding-box)
    * [Buscando produtos com órbita e ponto](#buscando-produtos-com-órbita-e-ponto)
    * [Buscando produto(s) por ID](#buscando-produtos-por-id)
    * [Download de produtos](#download-de-produtos)
    * [Converter coleção de produtos para GeoDataFrame](#converter-coleção-de-produtos-para-geodataframe)
    * [Download de produtos no GeoDataFrame ](#download-de-produtos-no-geodataframe)
* [Contribuição](#contribuição)
* [Progresso do projeto](#progresso-do-projeto)
* [Licença](#licença)

## Descrição: Métodos

- query: *Fazer uma busca na API*
    - Parâmetros:
        - **location** -> `List[float] | Tuple(int, int)` : Bouding box ou Órbita ponto da área de interesse
        - **initial_date**: -> `date` : Data inicial da busca
        - **end_date** -> `date` : Data limite da busca
        - **cloud** -> `int` : Porcentagem máxima de nuvem da busca
        - **limit** -> `int` : Limite de quantidade de produtos que irão ser retornados na busca
        - **collections** (*Opcional*) -> `List[str]` : Coleção(ões) de imagens.

----

- query_by_id: *Fazer uma busca por ID do(s) produto(s)*
    - Parâmetros:
        - **id** -> `str | List[str]` : Um ID **ou** uma lista de IDs das cenas

----

- download: *Baixar banda(s) das cenas retornadas do método `query`*
    - Parâmetros:
        - **products** -> `Dict | GeoDataFrame` : As cenas retornadas da API
        - **bands** -> `List[str]` : Banda(s) escolhida(s) dentre as disponíveis da cena
        - **threads** (*Opcional*) -> `int` : Limite de threads para o download paralelo
        - **outdir** (*Opcional*) -> `str` : Caminho onde irá ser salvo as bandas
        - **with_folder** (*Opcional*) -> `bool` : Chave para ativar o agrupamento das bandas baixadas em subpastas

----

- to_geodataframe: *Transformar dicionário no formato GeoJSON em GeoDataFrame*
    - Parâmetros:
        - **products** -> `Dict` : Os produtos retornados da API
        - **crs** (*Opcional*)-> `str` : Sistema de referência (ex: EPSG:4326)

----

## Exemplos

### Buscando produtos com Bounding Box:

```python
# Importar biblioteca do cbers4asat e datetime
from src.cbers4asat import Cbers4aAPI
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

### Buscando produtos com órbita e ponto:

```python
from src.cbers4asat import Cbers4aAPI
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

### Buscando produtos por ID

```python
from src.cbers4asat import Cbers4aAPI

api = Cbers4aAPI('meu@email.com')

# Buscando pelo ID de uma cena
produto = api.query_by_id('CBERS4A_WPM22912420210830')

print(produto)

# Para mais de um produto:

produtos = api.query_by_id(['CBERS4A_WPM22912420210830', 'AMAZONIA1_WFI03901620210911CB11'])

print(produtos)

```

### Download de produtos:

```python
from src.cbers4asat import Cbers4aAPI
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

### Converter coleção de produtos para GeoDataFrame:

```python
from src.cbers4asat import Cbers4aAPI
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

### Download de produtos no GeoDataFrame:

```python
from src.cbers4asat import Cbers4aAPI
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

## Contribuição

Convido qualquer pessoa a participar contribuindo com código, relatando bugs,
escrevendo documentação, tutoriais e discutindo o futuro deste projeto.

Para mais informações de como contribuir ao projeto,
leia [ao manual de contribuição](https://github.com/gabriel-russo/cbers4asat/blob/master/CONTRIBUTING.md)

## Progresso do projeto

Você pode acompanhar todo o progresso do desenvolvimento no [painel de projetos](https://github.com/gabriel-russo/cbers4asat/projects):

# Licença

Copyright (c) 2022 Gabriel Russo

Copyright (c) 2020 Sandro Klippel

O uso é fornecido sob a Licença do MIT. Veja
em [LICENSE](https://github.com/gabriel-russo/cbers4asat/blob/master/LICENSE)
para mais detalhes.