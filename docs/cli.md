# CLI

Você pode utilizar a [Interface de Linha de Comando](https://www.alura.com.br/artigos/cli-interface-linha-comandos) do `cbers4asat` para
consumir o catálogo de imagens do CBERS-04A e AMAZONIA-1.

É uma maneira mais fácil e rápida de consultar e baixar cenas no catálogo sem a necessidade de escrever código em Python.


## Download

Vá até as releases e procure pelo versão mais recente de `cbers4asat-cli` e baixe o executável que mais se adeque ao seu sistema operacional.

https://github.com/gabriel-russo/cbers4asat/releases

## Opções

| Arg. Curto | Arg. Longo   | Tipo    | Obrigatório | Descrição                                                                                                                                        |
|------------|--------------|---------|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| -u         | --user       | TEXTO   | Sim         | E-mail cadastrado no site do [dgi inpe explore](http://www.dgi.inpe.br/catalogo/explore)                                                         |
| -g         | --geometry   | ARQUIVO | Sim         | Caminho até o arquivo GeoJSON com polígonos que serão utilizados como parâmetros de busca                                                        |
|            | --collection | LISTA   | Sim         | [Nome das coleções](https://cbers4asat.readthedocs.io/pt_BR/latest/quickstart/#colecoes-de-imagens) que irão ser utilizadas como fonte dos dados |
| -s         | --start      | TEXTO   | Não         | Data de início utilizando o formato YYYY-MM-DD (Padrão: HOJE - 1 SEMANA)                                                                         |
| -e         | --end        | TEXTO   | Não         | Data final utilizando o formato YYYY-MM-DD (Padrão: HOJE)                                                                                        |
| -c         | --cloud      | INTEIRO | Não         | Quantidade de cobertura de núvens máximo na imagem  (Padrão: 100)                                                                                |
| -l         | --limit      | INTEIRO | Não         | Quantidade de cenas limite retornadas por busca  (Padrão: 25)                                                                                    |
| -i         | --id         | TEXTO   | Não         | **NÃO DISPONÍVEL**                                                                                                                               |
| -d         | --download   |         |             | **NÃO DISPONÍVEL**                                                                                                                               |
| -h         | --help       |         |             | Mostra texto de ajuda para utilização                                                                                                            |
| -v         | --version    |         |             | Mostra o número da versão                                                                                                                        |


## Exemplos

### Linux

Exemplo 1: Buscando imagens das coleções `CBERS4A_WPM_L4_DN` e `AMAZONIA_WFI_L2_DN`
```commandline
cbers4asat --geometry area.geojson --user teste@gmail.com --collection CBERS4A_WPM_L4_DN AMAZONIA_WFI_L2_DN
```

Exemplo 2: Buscando imagens das coleções `CBERS4A_WPM_L4_DN` e `AMAZONIA_WFI_L2_DN` que estão intersectando 
fazenda.geojson entre as datas de 25/07/2023 e 25/08/2023, limitando 25 cenas no output.
```commandline
cbers4asat --geometry fazenda.geojson --user teste@gmail.com --collection CBERS4A_WPM_L4_DN AMAZONIA_WFI_L2_DN --start 2023-07-25 --end 2023-08-25 --limit 25
```

Exemplo 3: O mesmo do exemplo 2, porém as cenas devem possui menos de 25% de cobertura de nuvem
```commandline
cbers4asat --geometry fazenda.geojson --user teste@gmail.com --collection CBERS4A_WPM_L4_DN AMAZONIA_WFI_L2_DN --start 2023-06-25 --end 2023-08-25 --limit 25 --cloud 25
```

Output do exemplo 3:
```
2 scenes found
---
Product CBERS4A_WPM22812420230718 - Date: "2023-07-18T14:53:57", Sensor: "WPM", Satellite: "CBERS4A"
Product CBERS4A_WPM22812520230718 - Date: "2023-07-18T14:54:10", Sensor: "WPM", Satellite: "CBERS4A"
```

### Windows

Todos os comandos do exemplo de linux irão funcionar no windows, basta adicionar o sufixo ".exe" do executável.

```commandline
cbers4asat.exe --geometry area.geojson --user teste@gmail.com --collection AMAZONIA1_WFI_L4_DN AMAZONIA1_WFI_L2_DN --start 2023-07-25
```

Output:
```
4 scenes found
---
Product AMAZONIA1_WFI03901620230728CB10 - Date: "2023-07-28T15:01:40", Sensor: "WFI", Satellite: "AMAZONIA1"
Product AMAZONIA1_WFI03901720230728CB10 - Date: "2023-07-28T15:03:20", Sensor: "WFI", Satellite: "AMAZONIA1"
Product AMAZONIA1_WFI03801620230726CB10 - Date: "2023-07-26T14:41:40", Sensor: "WFI", Satellite: "AMAZONIA1"
Product AMAZONIA1_WFI03801720230726CB10 - Date: "2023-07-26T14:43:20", Sensor: "WFI", Satellite: "AMAZONIA1"
```

### MacOS

Caso você seja usuário de MacOS e gostaria de utilizar a cli do `cbers4asat` no seu sistema operacional, você pode
solicitar para que seja adicionado [abrindo uma issue](https://github.com/gabriel-russo/cbers4asat/issues) ou enviando um 
e-mail para [gabrielrusso@protonmail.com](mailto:gabrielrusso@protonmail.com)
