# -*- coding: utf-8 -*-
"""

Análise de Performance Comercial

Created on Mon Oct 27 17:21:13 2025
@author: Rumanns
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path


def path_data():
    #Declarando variáveis globais, para usar nas outras funções
    global diretorio, arquivos

    # Caminho absoluto do arquivo atual
    caminho_atual = Path(__file__).resolve()
    
    # Pasta dois níveis acima (pasta avó)
    diretorio = caminho_atual.parent.parent
    
    # Caminho de onde a pasta onde os arquivos de dados se encontram
    diretorio = str(diretorio) + '\data'
    
    # Arquivos em 'diretorio'
    arquivos = os.listdir(diretorio)

    # for i in arquivos:
    #     print(i)
    print(f'Há {len(arquivos)} arquivos na pasta\n')


def le_dados():
    path_data()
#    df = pd.read_csv(f'{diretorio}\\olist_customers_dataset.csv')
    for arquivo in arquivos:
        print(f'{arquivo}:')
        df = pd.read_csv(f'{diretorio}\\{arquivo}')
        print(df.head())
        

le_dados()



































