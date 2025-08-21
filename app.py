import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =======================
# Carregamento do arquivo
# =======================
@st.cache_data
def carregar_dados(caminho):
    df = pd.read_csv(caminho, sep=";", encoding="latin1")
    df.columns = df.columns.str.strip()

    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.floor('ms')

    if "km" in df.columns:
        df["km"] = (
            df["km"].astype(str)
            .str.replace(",", ".", regex=False)
            .str.extract(r"(\d+\.?\d*)")[0]
        )
        df["km"] = pd.to_numeric(df["km"], errors="coerce")

    if "tipo_de_acidente" in df.columns:
        df["tipo_de_acidente"] = df["tipo_de_acidente"].astype(str).str.replace('"', "")

    # Converte todas colunas de objeto para string para evitar erros Arrow
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)

    return df

# =======================
# App Streamlit
# =======================
st.title("📊 Dashboard de Acidentes - AFD")

arquivo = st.file_uploader("Carregue o arquivo CSV", type=["csv"])

if arquivo is not None:
    df = carregar_dados(arquivo)

    # -----------------------
    # Filtros interativos
    # -----------------------
    st.sidebar.header("Filtros")
    df_filtered = df.copy()

    # Filtro por tipo de acidente
    if "tipo_de_acidente" in df_filtered.columns:
        tipos = df_filtered["tipo_de_acidente"].unique()
        filtro_tipo = st.sidebar.multiselect("Tipo de acidente:", tipos, default=tipos)
        df_filtered = df_filtered[df_filtered["tipo_de_acidente"].isin(filtro_tipo)]

    # Filtro por período
    if "data" in df_filtered.columns:
        data_min = df_filtered["data"].min().date()
        data_max = df_filtered["data"].max().date()
        periodo = st.sidebar.date_input("Período:", [data_min, data_max])
        df_filtered = df_filtered[(df_filtered["data"] >= pd.to_datetime(periodo[0])) &
                                  (df_filtered["data"] <= pd.to_datetime(periodo[1]))]

    # -----------------------
    # Abas para indicadores
    # -----------------------
    abas = st.tabs(["Prévia dos Dados", "Acidentes por Tipo", "Acidentes por Mês", "Estatísticas"])

    # Aba 1: Prévia dos Dados
    with abas[0]:
        st.subheader("Prévia do DataFrame")
        df_display = df_filtered.copy()
        if "data" in df_display.columns:
            df_display["data"] = df_display["data"].astype(str)
        st.dataframe(df_display.head())

    # Aba 2: Acidentes por Tipo
    with abas[1]:
        if "tipo_de_acidente" in df_filtered.columns:
            st.subheader("Distribuição por Tipo de Acidente")
            fig, ax = plt.subplots()
            df_filtered["tipo_de_acidente"].value_counts().plot(kind="bar", ax=ax)
            ax.set_ylabel("Quantidade")
            ax.set_xlabel("Tipo de Acidente")
            ax.set_title("Acidentes por Tipo")
            st.pyplot(fig)
        else:
            st.info("Coluna 'tipo_de_acidente' não encontrada no CSV.")

    # Aba 3: Acidentes por Mês
    with abas[2]:
        if "data" in df_filtered.columns:
            st.subheader("Acidentes por Mês")
            df_filtered["mes"] = df_filtered["data"].dt.to_period("M").astype(str)
            fig, ax = plt.subplots()
            df_filtered["mes"].value_counts().sort_index().plot(kind="bar", ax=ax)
            ax.set_ylabel("Quantidade")
            ax.set_xlabel("Mês")
            ax.set_title("Acidentes por Mês")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("Coluna 'data' não encontrada no CSV.")

    # Aba 4: Estatísticas
    with abas[3]:
        st.subheader("📌 Estatísticas Descritivas")
        st.write(df_filtered.describe(include="all"))

else:
    st.info("Faça upload de um arquivo CSV para começar.")
