import sys
import requests
import os.path
import csv
import pandas as pd

def get_proposicoes(anoInicial, anoFinal):
    """
    Obtém todas as proposições da Câmara dos Deputados dentro do intervalo de tempo desejado;
    O anoFinal não é incluído na pesquisa.
    """
    print('Obtendo Proposições...')
    directory = './proposicoes/'

    for ano in range(anoInicial, anoFinal):
        url = 'http://dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-'+str(ano)+'.csv'
        r = requests.get(url, allow_redirects=True)
        if url.find('/'):
            filename = url.rsplit('/', 1)[1]
            file_path = os.path.join(directory, filename)
            open(file_path, 'wb').write(r.content)

def get_temas(anoInicial, anoFinal):
    """
    Obtém todas os temas da Câmara dos Deputados dentro do intervalo de tempo desejado;
    O anoFinal não é incluído na pesquisa.
    """
    print('Obtendo Temas...')
    directory = './temas/'

    for ano in range(anoInicial, anoFinal):
        url = 'http://dadosabertos.camara.leg.br/arquivos/proposicoesTemas/csv/proposicoesTemas-'+str(ano)+'.csv'
        r = requests.get(url, allow_redirects=True)
        if url.find('/'):
            filename = url.rsplit('/', 1)[1]
            file_path = os.path.join(directory, filename)
            open(file_path, 'wb').write(r.content)

def fix_proposicoes(anoInicial, anoFinal):
    """Corrige o delimitador para importação correta no Pandas"""
    for ano in range(anoInicial, anoFinal):
        reader = csv.reader(open("./proposicoes/proposicoes-"+str(ano)+".csv", "r", encoding="utf8"), delimiter=';')
        writer = csv.writer(open("./proposicoes/proposicoes-"+str(ano)+"-fix.csv", 'w', encoding="utf8"), delimiter=',')
        writer.writerows(reader)

def join_proposicoes_temas(anoInicial, anoFinal):
    """Concatena todas os arquivos e faz limpeza de dados"""
    print('Unindo Proposições a Temas...')
    fix_proposicoes(anoInicial, anoFinal)

    dfs = []

    for ano in range(anoInicial, anoFinal):
        df = pd.read_csv('./proposicoes/proposicoes-'+str(ano)+'-fix.csv', dtype="object")
        dfs.append(df)

    temas_dfs = []

    for ano in range(anoInicial, anoFinal):
        df = pd.read_csv('./temas/proposicoesTemas-'+str(ano)+'.csv', sep=";", dtype="object")
        temas_dfs.append(df)
    
    proposicoes = pd.concat(dfs, axis=0, ignore_index=True)
    temas = pd.concat(temas_dfs, axis=0, ignore_index=True)

    proposicoes = proposicoes.rename(columns={'uri':'uriProposicao'})
    proposicoes_classificadas = pd.merge(proposicoes, temas, on='uriProposicao', how='left')
    proposicoes_classificadas = proposicoes_classificadas.drop(columns=['\ufeff"id"','siglaTipo_y', 'numero_y', 'ano_y'])
    proposicoes_classificadas = proposicoes_classificadas.rename(columns={'siglaTipo_x': 'siglaTipo', 'numero_x': 'numero', 'ano_x': 'ano'})
    
    return proposicoes_classificadas

def make_csv(df, anoInicial, anoFinal):
    """Exporta um CSV com o resultado final"""
    print('Exportando CSV...')
    df.to_csv('proposicoes_'+str(anoInicial)+'_'+str(anoFinal-1)+'.csv', index=False)

def main(anoInicial, anoFinal):
    """
    Principal função a ser executada chamando pela linha de comando como, por exemplo:
    python main.py 1988 2023
    """
    get_proposicoes(anoInicial, anoFinal)
    get_temas(anoInicial, anoFinal)
    df = join_proposicoes_temas(anoInicial, anoFinal)
    make_csv(df, anoInicial, anoFinal)
    print('Extração do dataset concluída.')

main(int(sys.argv[1]), int(sys.argv[2]))
