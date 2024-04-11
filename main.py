import sys
import requests
import os.path
import csv
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO
import time
from tqdm import tqdm

def get_proposicoes(anoInicial, anoFinal):
    """
    Obtém todas as proposições da Câmara dos Deputados dentro do intervalo de tempo desejado;
    O anoFinal não é incluído na pesquisa.
    """
    print('Obtendo Proposições...')
    directory = './proposicoes/'

    for ano in tqdm(range(anoInicial, anoFinal)):
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

    for ano in tqdm(range(anoInicial, anoFinal)):
        url = 'http://dadosabertos.camara.leg.br/arquivos/proposicoesTemas/csv/proposicoesTemas-'+str(ano)+'.csv'
        r = requests.get(url, allow_redirects=True)
        if url.find('/'):
            filename = url.rsplit('/', 1)[1]
            file_path = os.path.join(directory, filename)
            open(file_path, 'wb').write(r.content)

def fix_proposicoes(anoInicial, anoFinal):
    """Corrige o delimitador para importação correta no Pandas"""
    for ano in tqdm(range(anoInicial, anoFinal)):
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


def get_inteiro_teor(anoInicial, anoFinal):
    """Retorna o inteiro teor das proposições"""
    
    df = join_proposicoes_temas(anoInicial, anoFinal)

    print('Obtendo Inteiro Teor...')

    # Add a new column 'inteiro_teor' to the DataFrame with empty strings
    df['inteiro_teor'] = ''

    # Iterate through the column 'urlInteiroTeor' and download the PDFs
    for _, row in tqdm(df[:100].iterrows()):
        url = row['urlInteiroTeor']
        if pd.notna(url):
            try:
                # Download the PDF
                response = requests.get(url)
                response.raise_for_status()

                # Load the PDF into a PdfReader object
                pdf = PdfReader(BytesIO(response.content))

                # Extract the text from the PDF
                text = ""
                for page in range(len(pdf.pages)):
                    page_text = pdf.pages[page].extract_text()
                    text += page_text

                # Append the text to the 'inteiro_teor' column
                df.at[row.name, 'inteiro_teor'] = text

            except Exception as e:
                print(f"An error occurred with URL {url}: {e}")
    
    return df


def make_csv(df, anoInicial, anoFinal):
    """Exporta um CSV com o resultado final"""
    print('Exportando CSV...')
    df.to_csv('proposicoes_inteiroteor_'+str(anoInicial)+'_'+str(anoFinal-1)+'.csv', index=False)

def main(anoInicial, anoFinal):
    """
    Principal função a ser executada chamando pela linha de comando como, por exemplo:
    python main.py 1988 2023
    """
    start_time = time.time()
    get_proposicoes(anoInicial, anoFinal)
    get_temas(anoInicial, anoFinal)
    df = get_inteiro_teor(anoInicial, anoFinal)
    make_csv(df, anoInicial, anoFinal)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Extração do dataset concluída em {elapsed_time/60} minutos.')

main(int(sys.argv[1]), int(sys.argv[2]))
