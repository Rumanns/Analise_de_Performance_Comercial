# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 10:10:44 2025

@author: Rumanns
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import warnings
import os
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Olist Dashboard Comercial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título
st.title("📊 Dashboard de Performance Comercial - Olist")
st.markdown("Análise de vendas, lucro, ticket médio e desempenho geral do e-commerce")

# Carregar dados
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


def load_data():
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

# Carregar dados
#Carregar dados
try:
    df = load_data()
    
    # Sidebar com filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de período
    min_date = df['order_purchase_date'].min()
    max_date = df['order_purchase_date'].max()
    
    date_range = st.sidebar.date_input(
        "Período de Análise",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro de estado
    states = ['Todos'] + sorted(df['customer_state'].unique().tolist())
    selected_state = st.sidebar.selectbox("Estado do Cliente", states)
    
    # Filtro de categoria
    categories = ['Todas'] + sorted(df['product_category_name'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Categoria de Produto", categories)
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['order_purchase_date'] >= start_date) & 
            (filtered_df['order_purchase_date'] <= end_date)
        ]
    
    if selected_state != 'Todos':
        filtered_df = filtered_df[filtered_df['customer_state'] == selected_state]
    
    if selected_category != 'Todas':
        filtered_df = filtered_df[filtered_df['product_category_name'] == selected_category]
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vendas = filtered_df['payment_value'].sum()
        st.metric("💰 Total de Vendas", f"R$ {total_vendas:,.2f}")
    
    with col2:
        ticket_medio = filtered_df.groupby('order_id')['payment_value'].sum().mean()
        st.metric("🎫 Ticket Médio", f"R$ {ticket_medio:,.2f}")
    
    with col3:
        total_pedidos = filtered_df['order_id'].nunique()
        st.metric("📦 Total de Pedidos", f"{total_pedidos:,}")
    
    with col4:
        total_clientes = filtered_df['customer_id'].nunique()
        st.metric("👥 Clientes Únicos", f"{total_clientes:,}")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Vendas por mês
        monthly_sales = filtered_df.groupby('order_purchase_year_month')['payment_value'].sum().reset_index()
        fig1 = px.line(monthly_sales, 
                      x='order_purchase_year_month', 
                      y='payment_value',
                      title="📈 Evolução das Vendas Mensais",
                      labels={'order_purchase_year_month': 'Mês', 'payment_value': 'Valor (R$)'})
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Top categorias
        top_categories = filtered_df.groupby('product_category_name')['payment_value'].sum().reset_index()
        top_categories = top_categories.sort_values('payment_value', ascending=False).head(10)
        fig2 = px.bar(top_categories, 
                      x='product_category_name', 
                      y='payment_value',
                      title="🏆 Top 10 Categorias por Vendas",
                      labels={'product_category_name': 'Categoria', 'payment_value': 'Vendas (R$)'})
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Vendas por estado
        state_sales = filtered_df.groupby('customer_state')['payment_value'].sum().reset_index()
        fig3 = px.choropleth(state_sales,
                            locations='customer_state',
                            locationmode='Brazil-states',
                            color='payment_value',
                            scope='south america',
                            title='🗺️ Vendas por Estado (Brasil)',
                            labels={'payment_value': 'Vendas (R$)', 'customer_state': 'Estado'})
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        # Distribuição de ticket médio
        order_totals = filtered_df.groupby('order_id')['payment_value'].sum()
        fig4 = px.histogram(x=order_totals.values,
                          nbins=30,
                          title='📊 Distribuição do Valor dos Pedidos',
                          labels={'x': 'Valor do Pedido (R$)', 'y': 'Frequência'})
        st.plotly_chart(fig4, use_container_width=True)
    
    # Tabela detalhada
    st.subheader("📋 Detalhamento das Vendas")
    
    # Métricas adicionais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_items_per_order = filtered_df.groupby('order_id').size().mean()
        st.metric("🧺 Itens por Pedido (Média)", f"{avg_items_per_order:.1f}")
    
    with col2:
        repeat_customers = filtered_df.groupby('customer_id').size()
        repeat_rate = (repeat_customers > 1).sum() / len(repeat_customers) * 100
        st.metric("🔄 Taxa de Repetição", f"{repeat_rate:.1f}%")
    
    with col3:
        shipping_costs = filtered_df['freight_value'].sum() if 'freight_value' in filtered_df.columns else 0
        st.metric("🚚 Custo de Frete Total", f"R$ {shipping_costs:,.2f}")
    
    # Mostrar amostra dos dados
    st.subheader("🔍 Amostra dos Dados")
    st.dataframe(filtered_df.head(100), use_container_width=True)
    
except FileNotFoundError as e:
    st.error(f"❌ Erro ao carregar dados: {str(e)}")
    st.info("""
    Certifique-se de que:
    1. Os arquivos CSV estão na pasta 'data/'
    2. Os nomes dos arquivos estão corretos:
        - olist_orders_dataset.csv
        - olist_order_items_dataset.csv
        - olist_order_payments_dataset.csv
        - olist_products_dataset.csv
        - olist_customers_dataset.csv
    """)
    
    
    
    
    
    
    
    
    
    
    
    
    
    