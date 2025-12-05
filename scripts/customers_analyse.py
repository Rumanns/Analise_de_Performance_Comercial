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
    #Caminho dos dados
    path_data()
    
    #Cria o dataframe de cada arquivo
    orders = pd.read_csv(f'{diretorio}\\olist_orders_dataset.csv')
    order_items = pd.read_csv(f'{diretorio}\\olist_order_items_dataset.csv')
    order_payments = pd.read_csv(f'{diretorio}\\olist_order_payments_dataset.csv')
    products = pd.read_csv(f'{diretorio}\\olist_products_dataset.csv')
    customers = pd.read_csv(f'{diretorio}\\olist_customers_dataset.csv')
    
    #Merge dos dados
    
    df = order_items.merge(orders[['order_id', 'customer_id', 'order_purchase_timestamp']],
                           on='order_id', how='left')
    df = df.merge(order_payments[['order_id', 'payment_value']],
                  on='order_id', how='left')
    df = df.merge(products[['product_id', 'product_category_name']],
                  on='product_id', how='left')
    df = df.merge(customers[['customer_id', 'customer_state']],
                  on ='customer_id', how='left')
    
    # Converter datas
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_purchase_date'] = df['order_purchase_timestamp'].dt.date
    df['order_purchase_year_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    
    return(df)

le_dados()



































