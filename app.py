import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =======================
# Carregamento do arquivo
# =======================
@st.cache_data
def carregar_dados(caminho):
    # Lê CSV com encoding do Windows
    df = pd.read_csv(caminho, sep=";", encoding="latin1")

    # Remove espaços extras nos nomes das colunas
    df.columns = df.columns.str.strip()

    # Converte coluna de data
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")

    # Converte km para numérico (substitui vírgula por ponto)
    if "km" in df.columns:
        df["km"] = (
            df["km"].astype(str)
            .str.replace(",", ".", regex=False)
            .str.extract(r"(\d+\.?\d*)")[0]
        )
        df["km"] = pd.to_numeric(df["km"], errors="coerce")

    # Remove aspas extras em tipo_de_acidente
    if "tipo_de_acidente" in df.columns:
        df["tipo_de_acidente"] = df["tipo_de_acidente"].astype(str).str.replace('"', "")

    return df


# =======================
# App Streamlit
# =======================
st.title("📊 Demonstrativo de Acidentes - AFD")

# Upload do arquivo
arquivo = st.file_uploader("Carregue o arquivo CSV", type=["csv"])

if arquivo is not None:
    df = carregar_dados(arquivo)

    st.subheader("Prévia dos Dados")
    st.dataframe(df.head())

    # Gráfico de acidentes por tipo
    if "tipo_de_acidente" in df.columns:
        st.subheader("Distribuição por Tipo de Acidente")
        fig, ax = plt.subplots()
        df["tipo_de_acidente"].value_counts().plot(kind="bar", ax=ax)
        st.pyplot(fig)

    # Gráfico de acidentes por mês
    if "data" in df.columns:
        st.subheader("Acidentes por Mês")
        df["mes"] = df["data"].dt.to_period("M")
        fig, ax = plt.subplots()
        df["mes"].value_counts().sort_index().plot(kind="bar", ax=ax)
        st.pyplot(fig)

    # Estatísticas descritivas
    st.subheader("📌 Estatísticas")
    st.write(df.describe(include="all"))

else:
    st.info("Faça upload de um arquivo CSV para começar.")
