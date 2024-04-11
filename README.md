# dataset-proposicoes-classificadas

[![DOI](https://zenodo.org/badge/622410247.svg)](https://zenodo.org/badge/latestdoi/622410247)

Código para gerar o dataset [Proposições na Câmara dos Deputados de 1988 até 2022 classificadas por Tema](https://zenodo.org/record/7792203). 

Para reproduzir o código, informe o intervalo de anos desejado (anoInicial e anoFinal) como no exemplo abaixo: 

> python main.py 1988 2023

Cada linha do dataset corresponde a uma Proposição apresentada na Câmara dos Deputados, com informações sobre sua identificação, conteúdo e andamento no processo legislativo, além da classificação temática. Com essa estrutura, seria possível realizar análises e visualizações dos dados, identificando padrões, tendências e evolução de temas ao longo do tempo.

O código foi executado em python 3.10.8

---
## Resultado

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7792203.svg)](https://doi.org/10.5281/zenodo.7792203)

O dataset gerado ao final do processo é um arquivo csv de 587.6 MB para os anos de 1988 até 2022. O diretório de proposições precisa de pelo menos 1GB de espaço para guardar os dados brutos obtidos e suas versões tratadas. 
