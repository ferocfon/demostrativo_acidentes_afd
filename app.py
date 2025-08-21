import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# ======================
# CARREGAR OS DADOS
# ======================
@st.cache_data
def carregar_dados(arquivo):
    if arquivo.endswith(".csv"):
        df = pd.read_csv(arquivo, sep=";", encoding="utf-8-sig")
    else:
        df = pd.read_excel(arquivo)
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df['ano'] = df['data'].dt.year
    return df

arquivo = "demostrativo_acidentes_afd.xlsx"
df = carregar_dados(arquivo)

# ======================
# FILTROS
# ======================
st.sidebar.title("🔎 Filtros")
anos = sorted(df['ano'].dropna().unique())
ano_sel = st.sidebar.multiselect("Ano", anos, default=anos)

df_filtrado = df[df['ano'].isin(ano_sel)]

# ======================
# KPIs
# ======================
st.title("🚛 Acidentes na Fernão Dias - Dashboard")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de Acidentes", f"{len(df_filtrado)}")
col2.metric("Mortos", int(df_filtrado['mortos'].sum()))
col3.metric("Feridos", int(df_filtrado[['levemente_feridos','moderadamente_feridos','gravemente_feridos']].sum().sum()))
col4.metric("Ilesos", int(df_filtrado['ilesos'].sum()))

# ======================
# GRÁFICOS
# ======================

# Acidentes por ano (linha interativa)
st.subheader("📊 Evolução Anual de Acidentes")
acidentes_ano = df_filtrado.groupby("ano").size().reset_index(name="Acidentes")
fig1 = px.line(acidentes_ano, x="ano", y="Acidentes", markers=True, title="Evolução de Acidentes por Ano")
st.plotly_chart(fig1, use_container_width=True)

# Tipos de acidente (pizza)
st.subheader("🚦 Distribuição por Tipo de Acidente")
acidentes_tipo = df_filtrado['tipo_de_acidente'].value_counts().reset_index()
acidentes_tipo.columns = ["Tipo", "Quantidade"]
fig2 = px.pie(acidentes_tipo, values="Quantidade", names="Tipo", title="Distribuição dos Tipos de Acidente", hole=0.4)
st.plotly_chart(fig2, use_container_width=True)

# Perfil das vítimas (barra colorida)
st.subheader("🧍 Perfil das Vítimas")
vitimas = df_filtrado[['ilesos','levemente_feridos','moderadamente_feridos','gravemente_feridos','mortos']].sum().reset_index()
vitimas.columns = ["Condição", "Quantidade"]
fig3 = px.bar(vitimas, x="Condição", y="Quantidade", color="Condição", title="Perfil das Vítimas", text="Quantidade")
st.plotly_chart(fig3, use_container_width=True)

# ======================
# TABELA
# ======================
st.subheader("📑 Amostra dos Dados")
st.dataframe(df_filtrado.head(20))
