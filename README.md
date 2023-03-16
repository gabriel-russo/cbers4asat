# Cbers4asat

## Descrição

Biblioteca Python para consultar o catálogo e realizar operações com dados do CBERS4A e AMAZONIA1.

A biblioteca `cbers4asat` surgiu da necessidade de automatizar a busca e manipulação de imagens do satélite
sino-brasileiro CBERS-04A utilizando linguagens de programação.

O design do projeto foi inspirado no [sentinelsat](https://github.com/sentinelsat/sentinelsat), onde é possível de forma
intuitiva, pesquisar por imagens e realizar o download com poucas linhas de código, além de poder ser integrado com
outras bibiliotecas como o geopandas.

---
[![Latest Version](https://img.shields.io/pypi/v/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)
[![Latest Version](https://img.shields.io/pypi/l/cbers4asat?style=plastic)](https://github.com/gabriel-russo/cbers4asat/blob/master/LICENSE)
[![Latest Version](https://img.shields.io/pypi/pyversions/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)
[![Latest Version](https://img.shields.io/pypi/dm/cbers4asat?style=plastic)](https://pypi.python.org/pypi/cbers4asat/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
![GitHub Workflow Status](https://github.com/gabriel-russo/cbers4asat/actions/workflows/build-cbers4asat.yml/badge.svg)
![GitHub Workflow Status](https://github.com/gabriel-russo/cbers4asat/actions/workflows/test-cbers4asat.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/cbers4asat/badge/?version=latest)](https://cbers4asat.readthedocs.io/pt_BR/latest/?badge=latest)
> [Read this README in english (old version of docs)](https://github.com/gabriel-russo/cbers4asat/blob/master/en-US_README.md)
> 🇺🇸

## Busque imagens com poucas linhas de código

```python
from cbers4asat import Cbers4aAPI
from datetime import date

# Inicializando a biblioteca
api = Cbers4aAPI('email@mail.com')

# Área de interesse (bbox, path row ou polígono)
path_row = (229, 124)

# Buscando metadados
produtos = api.query(location=path_row,
                     initial_date=date(2021, 6, 1),
                     end_date=date(2021, 7, 1),
                     cloud=100,
                     limit=10,
                     collections=['AMAZONIA1_WFI_L2_DN', 'CBERS4A_WPM_L4_DN'])

# Exibindo os resultados
print(produtos)
```

## Utilize a caixa de ferramenta para os trabalhos mais comuns

```python
# Para ver todas as ferramentas disponíveis, verifique a documentação
from cbers4asat.tools import rgbn_composite
import rasterio as rio
from rasterio.plot import show

# Criando a composição cor verdadeira
rgbn_composite(red='./CBERS4A_WPM22812420210704/CBERS_4A_WPM_20210704_228_124_L4_BAND3.tif',
               green='./CBERS4A_WPM22812420210704/CBERS_4A_WPM_20210704_228_124_L4_BAND2.tif',
               blue='./CBERS4A_WPM22812420210704/CBERS_4A_WPM_20210704_228_124_L4_BAND1.tif',
               nir='./CBERS4A_WPM22812420210704/CBERS_4A_WPM_20210704_228_124_L4_BAND4.tif',
               filename='CBERS4A_WPM22812420210704_TRUE_COLOR.tif',
               outdir='./STACK')

# Plotando a imagem
raster = rio.open("./STACK/CBERS4A_WPM22812420210704_TRUE_COLOR.tif")

show(raster.read(), transform=raster.transform)
```

## Download da biblioteca com pip

`pip install cbers4asat`

Instalação com a caixa de ferramentas

`pip install cbers4asat[tools]`

## Documentação

Você pode ler a documentação da biblioteca no link abaixo

> https://cbers4asat.readthedocs.io/

## Contribuição

Convido qualquer pessoa a participar contribuindo com código, relatando bugs,
escrevendo documentação, tutoriais e discutindo o futuro deste projeto.

Para mais informações de como contribuir ao projeto,
leia [ao manual de contribuição](https://github.com/gabriel-russo/cbers4asat/blob/master/CONTRIBUTING.md)

## Progresso do projeto

Você pode acompanhar todo o progresso do desenvolvimento
no [painel de projetos](https://github.com/gabriel-russo/cbers4asat/projects)

# Licença

Copyright (c) 2022 Gabriel Russo

Copyright (c) 2020 Sandro Klippel

O uso é fornecido sob a Licença do MIT. Veja
em [LICENSE](https://github.com/gabriel-russo/cbers4asat/blob/master/LICENSE)
para mais detalhes.