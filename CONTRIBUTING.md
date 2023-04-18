# Manual de Contribuição - CBERS4ASAT

Se você está interessado em contribuir para o CBERS4ASAT, este guia é para você. Nós valorizamos muito as contribuições
de nossa comunidade e estamos sempre procurando novas ideias e melhorias para o nosso projeto.

Agradecemos antecipadamente por suas contribuições!

## Sumário

- [Por quê contribuir?](#Por-quê-contribuir?)
- [Como Contribuir](#como-contribuir)
- [Diretrizes de Estilo](#diretrizes-de-estilo)
- [Fluxo de Trabalho](#fluxo-de-trabalho)
- [O que esperamos dos contribuidores?](#o-que-esperamos-dos-contribuidores)
- [Como enviar um feedback?](#como-enviar-um-feedback)

## Por quê contribuir?

Este projeto pode ampliar o acesso e o uso de dados de satélites nacionais. Estes dados são de suma importância para o monitoramento do território brasileiro e de outras partes do mundo. Existe uma serie de aplicações na área de observação da terra e que pode contribuir para o monitoramento do desflorestamento, qualidade da água, agricultura, planejamento urbano, etc.
Contribuir com este código impulsiona a operacionalização dos dados. Como exemplo da necessidade de operacionalização, este código vou desenvolvido para operacionalizar dados fusionados do sensor WPM a bordo do satélite CBERS4A para identificação de presença antrópica em áreas remotas. Processamento de correção atmosférica também é um exemplo de contribuição importante porque é considerado uma etapa fundamental na detecção de parâmetros biofísicos da superfície terrestre. 
Atualmente não existe um sistema capaz de automatizar etapas do processamento das imagens dos satélites CBERS4A e Amazônia e esta é a oportunidade.

## Como Contribuir

Existem várias maneiras pelas quais você pode contribuir para o `cbers4asat`:

- **Reportando bugs**: Caso encontre algum problema no código ou na documentação, por favor, crie uma
[issue](https://github.com/gabriel-russo/cbers4asat/issues) descrevendo o problema de forma clara e 
objetiva. Certifique-se de incluir todas as informações relevantes, como mensagens de erro, passos para reproduzir o problema, etc.

- **Requisitando recursos**: Se você tem uma ideia para um novo recurso ou funcionalidade, sinta-se à vontade para abrir
  uma [nova discussão](https://github.com/gabriel-russo/cbers4asat/discussions/categories/ideas) e compartilhar sua
  ideia conosco.

- **Resolvendo issues**: Se você é um desenvolvedor, pode contribuir resolvendo issues já existentes. Basta escolher uma
  issue que esteja aberta.

- **Adicionando documentação**: A documentação é uma parte importante de qualquer projeto de software. Se você é bom em
  escrever documentação, sinta-se à vontade para contribuir com nossos arquivos de documentação.

- **Adicionando testes**: Testes são extremamente importantes para garantir a qualidade do código. Se você é um
  desenvolvedor experiente em testes, contribua adicionando mais testes ao projeto.

- **Enviando Pull Requests**: Se você fez alguma alteração no código e gostaria de compartilhá-la com a comunidade, envie um
  Pull Request (PR). Certifique-se de que seu código siga as diretrizes de contribuição deste documento.

## Diretrizes de Estilo

### Linter e formatador de código 
Nós seguimos as diretrizes de estilo de formatação de código definidas pelo [Black code formatter](https://github.com/psf/black),
juntamente com a ferramenta de análise estática (linter) [flake8](https://github.com/PyCQA/flake8).

Essas ferramentas garantem que todo o código do projeto siga um padrão de estilo consistente, facilitando a leitura e
a manutenção do código.

### Estilos de código

- **Imports**: Os imports devem ser específicos, ou seja, devem ser feitos apenas para as funções que serão utilizadas.
  Por exemplo, ao invés de fazer:

  ```python
  import numpy
  ```

  Faça:
  ```python
  from numpy import ndarray
  ```

- **funções**: 
  - O nome das funções devem ser escritas utilizando o padrão [snake_case](https://en.wikipedia.org/wiki/Snake_case)
  - Os parâmetros das funções devem possuir tipos definidos e, se for necessário, valor padrão. Por exemplo:
    ```python
    def minha_funcao(x: int, y: float, z: str = "default"):
        pass
    ```
    Caso o parâmetro possua um tipo muito específico, deve utilizar os tipos da biblioteca [typing](https://docs.python.org/3/library/typing.html). 
    Por exemplo:
    ```python
    from typing import List
    from numpy import ndarray

    def minha_funcao(x: List[ndarray]):
        pass
    ```
    _Em caso de dúvidas, faça uma breve leitura em códigos já existentes no projeto._    

- **docstrings**: As docstrings devem ser escritas utilizando o padrão [Google Style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

[Siga a filosofia pythonista o máximo possível.](https://peps.python.org/pep-0020/)

**Certifique-se de que seu código siga essas diretrizes antes de enviar um Pull Request.**

## Fluxo de Trabalho

Para contribuir para o `cbers4asat`, siga as etapas abaixo:

### Preparando o seu ambiente de desenvolvimento

1. Faça um [fork](https://docs.github.com/pt/get-started/quickstart/github-glossary#fork) do nosso repositório no
   GitHub.

2. [Clone](https://docs.github.com/pt/get-started/quickstart/github-glossary#clone) seu fork em sua máquina local e entre no diretório.

   ```
   git clone https://github.com/seu_usuario/cbers4asat.git && cd cbers4asat
   ```

3. Faça a instalação das ferramentas de desenvolvimento do projeto

   ```
   pip install -e ".[dev]"
   ```

4. Crie uma nova [branch](https://docs.github.com/pt/get-started/quickstart/github-glossary#branch) para sua alteração.

   ```
   git checkout -b minha-alteracao
   ```

### Fluxo de desenvolvimento

O projeto utiliza uma ferramenta de gerenciamento de projetos chamada [Hatch](https://github.com/pypa/hatch). 
Essa ferramenta permite que trabalhe de forma simplificada, com scripts previamente definidos no arquivo `pyproject.toml`.

1. Faça as alterações necessárias no código e execute os testes:
    ```
    python3 -m hatch run test
    ```

2. Certifique-se de que seu código siga as diretrizes de estilo, formate com:
    ```
    python3 -m hatch run format
    ```
3. Adicione testes para seu código, se possível.

   > Obs.: Caso não seja possível adicionar testes, explique o motivo no seu Pull Request, é possível que outra pessoa 
        possa se disponibilizar para adicionar os testes.

4. Faça commit de suas alterações, explicando claramente as modificações feitas.

   ```
   git commit -m "Minha alteração"
   ```

5. Envie suas alterações para seu fork no GitHub.

   ```
   git push origin minha-alteracao
   ```

6. Abra um Pull Request em nosso repositório no GitHub e descreva suas alterações. Certifique-se de incluir informações
   detalhadas sobre o que foi alterado e por quê.

7. Aguarde pelo nosso feedback.

8. Se for necessário fazer alguma correção no código do Pull Request, é preferível que apenas refaça o commit utilizando o amend,
dessa forma não irá poluir o histórico de commits do projeto com commits de correção:

    ```
    $ git add <arquivo>
    $ git commit --amend
    $ git push origin minha-alteracao -f
    ```

## O que esperamos dos contribuidores?

Esperamos que os contribuidores sejam atenciosos, respeitosos e tolerantes com as opiniões de outros colaboradores. Além
disso, os contribuidores devem estar abertos para discussões e críticas construtivas, e devem se esforçar para melhorar a
qualidade do código e da documentação do projeto.

## Como enviar um feedback?

Caso queira enviar feedback sobre o projeto, utilize o sistema de [discussões do Github](https://github.com/gabriel-russo/cbers4asat/discussions). 
Ficaremos felizes em ouvir sugestões e críticas construtivas para melhorar o cbers4asat.
