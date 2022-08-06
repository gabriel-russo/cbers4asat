# Cbers4asat

## Descrição
Biblioteca Python para consultar o catálogo e realizar operações com dados do CBERS4A

## Sumário
* [Descrição](#descrio-biblioteca)
* [Build da biblioteca](#build-da-bibilioteca)
* [Documentação](#descrio-mtodos)
* [Exemplos básicos](#exemplos)
    * [Buscando um produto com Bounding box](#buscando-um-produto-com-bounding-box)
    * [Buscando um produto com Órbita ponto](#buscando-um-produto-com-orbita-ponto-path-row)
    * [Download de produtos](#download-de-produtos)
    * [Converter produtos para GeoDataFrame](#converter-para-geodataframe)
    * [Download de produtos no GeoDataFrame ](#download-de-produtos-no-geodataframe)
* [License](#license)

## Build da bibilioteca
1. Baixe o código fonte ou release do projeto
2. Extraia e entre na pasta
3. Faça a build com setuptools: 
- `python3 setup.py bdist_wheel`
4. Entre na pasta `dist/` gerada pelo comando
5. Copie o arquivo com extenção `.whl` para o seu projeto e instale com:
- `pip install <nome_do_arquivo>.whl`

## Descrição: Métodos

- query: *Fazer uma busca na API*
  - Parâmetros:
    - **location** -> `List[float] | Tuple(int, int)` : Bouding box ou Órbita ponto da área de interesse
    - **initial_date**: -> `date` : Data inicial da busca
    - **end_date** -> `date` : Data limite da busca
    - **cloud** -> `int` : Porcentagem máxima de nuvem da busca
    - **limit** -> `int` : Limite de cenas que irão retornar na busca
    - **collections** (*Opcional*) -> `List[str]` : Coleção(ões) de imagens.
----
  - download: *Baixar bandas de uma cena*
    - Parâmetros:
      - **products** -> `Dict | GeoDataFrame` : A cena escolhida retornada da API
      - **bands** -> `List[str]` : Banda(s) escolhida(s) dentre as disponíveis na cena
      - **threads** (*Opcional*) -> `int` : Limite de threads para o download paralelo
      - **outdir** (*Opcional*) -> `str` : Caminho onde irá ser salvo as bandas
      - **with_folder** (*Opcional*) -> `bool` : Chave para ativar o agrupamento das bandas baixadas em subpastas
----
  - to_geodataframe: *Transformar dicionário no formato GeoJSON em GeoDataFrame*
    - Parâmetros:
      - **products** -> `List[Dict]` : As cenas retornados da API
      - **crs** -> `str` : Sistema de referência (ex: EPSG:4326)
----
## Exemplos

### Buscando um produto com Bounding box:
```python
# Importar a API
from cbers4asat import Cbers4aAPI
from datetime import date

# Login utilizado no http://www2.dgi.inpe.br/catalogo/explore
api = Cbers4aAPI('seu.login@email.com')

# Bouding Box escolhido
bbox = [-63.92944335937501,
        -8.819260401678381,
        -63.79211425781251,
        -8.722218306198739]

# Intervalo de data
data_inicial = date(2021, 8, 25)
data_final = date(2021, 9, 25)

# Fazer uma busca no catálogo e exibir resultados
produtos = api.query(location=bbox, 
                     initial_date=data_inicial, 
                     end_date=data_final, 
                     cloud=100, 
                     limit=100,
                     collections=['AMAZONIA1_WFI_L2_DN','CBERS4A_WPM_L4_DN']) #Optional

print(produtos)
# {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'id': 'AMAZONIA1_WFI03901620210911CB11', ...
```

### Buscando um produto com Orbita ponto (path row):
```python
# Importar a API
from cbers4asat import Cbers4aAPI
from datetime import date

# Login utilizado no http://www2.dgi.inpe.br/catalogo/explore
api = Cbers4aAPI('seu.login@email.com')

# Órbita ponto escolhida
path_row = (229, 124)

# Intervalo de data
data_inicial = date(2021, 8, 25)
data_final = date(2021, 9, 25)

# Fazer uma busca no catálogo e exibir resultados
produtos = api.query(location=path_row, 
                     initial_date=data_inicial, 
                     end_date=data_final, 
                     cloud=100, 
                     limit=100,
                     collections=['AMAZONIA1_WFI_L2_DN','CBERS4A_WPM_L4_DN']) #Optional

print(produtos)
# {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'id': 'CBERS4A_WPM22912420210830', ...
```

### Download de produtos:
```python
from cbers4asat import Cbers4aAPI
from datetime import date

api = Cbers4aAPI('seu.login@email.com') # Para fazer download, o email é obrigatório
bbox = (229, 124)

data_inicial = date(2021, 8, 25)
data_final = date(2021, 9, 25)

produtos = api.query(location=bbox, 
                     initial_date=data_inicial, 
                     end_date=data_final, 
                     cloud=100, 
                     limit=1,
                     collections=['CBERS4A_WPM_L4_DN'])

# Bandas escolhidas: vermelha, verde e azul
# Output do download é opcional, caso omitido será usado o diretório atual
api.download(products=produtos, 
             bands=['red','green','blue'], 
             threads=3, # Numero de threads que irão ser usadas do processador
             outdir='./downloads',
             with_folder=True) # Agrupar bandas de uma cena(s) em subpasta(s) no diretório ./downloads

# O diretório downloads ficará assim com o with_folter=true :
 # download/
 # +- CBERS4A_WPM22912420210830/
 # ++- CBERS_4A_WPM_20210830_229_124_L4_BAND3.tif
 # ++- CBERS_4A_WPM_20210830_229_124_L4_BAND2.tif
 # ++- CBERS_4A_WPM_20210830_229_124_L4_BAND1.tif
```

### Converter para GeoDataFrame:

```python
from cbers4asat import Cbers4aAPI
from datetime import date
import geopandas as gpd

api = Cbers4aAPI('seu.login@email.com')

bbox = (229, 124)

data_inicial = date(2021, 8, 25)
data_final = date(2021, 9, 25)

produtos = api.query(location=bbox, 
                     initial_date=data_inicial, 
                     end_date=data_final, 
                     cloud=100, 
                     limit=3,
                     collections=['CBERS4A_WPM_L4_DN'])

# Converter os produtos para geopandas GeoDataFrame
gdf = api.to_geodataframe(produtos, 'EPSG:4674')

print(gdf.to_string())
```
### Download de produtos no GeoDataFrame:

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

# Converter os produtos para geopandas GeoDataFrame
gdf = api.to_geodataframe(produtos)

api.download(products=gdf, bands=['red'], outdir='./downloads', with_folder=False)
```

# License
Copyright (c) 2022 Gabriel Russo

Copyright (c) 2020 Sandro Klippel

O uso é fornecido sob a Licença do MIT. Veja em LICENSE
para mais detalhes.