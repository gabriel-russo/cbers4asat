# API Python

Documentação detalhada de todos os métodos presentes na biblioteca

----

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