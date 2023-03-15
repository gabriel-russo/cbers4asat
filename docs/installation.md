# Instalação

Faça a instalação do `cbers4asat` com o pip
```
pip install cbers4asat
```

Instalação com a caixa de ferramentas
```
pip install cbers4asat[tools]
```

## Testes

Para executar os testes unitários do projeto faça:
```commandline
git clone https://github.com/gabriel-russo/cbers4asat.git
cd cbers4asat
pip install -e .[dev]
python -m hatch run test
```

## Versões do python suportadas

Atualmente a biblioteca vem sendo testada com versões maiores e iguais a 3.8.
