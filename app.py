import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# Configuração inicial da página
# ==============================
st.set_page_config(page_title="Painel de Acidentes", layout="wide")

st.title("🚦 Painel de Acidentes de Trânsito")
st.markdown("Dashboard interativo para análise de ocorrências")

# ==============================
# Upload do arquivo
# ==============================
uploaded_file = st.file_uploader("📂 Faça upload do arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Tentativa de leitura com diferentes encodings
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8", sep=";")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(uploaded_file, encoding="latin1", sep=";")
        except:
            df = pd.read_csv(uploaded_file, encoding="cp1252", sep=";")

    # ==============================
    # Pré-processamento
    # ==============================
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    if "horario" in df.columns:
        df["horario"] = pd.to_datetime(df["horario"], errors="coerce").dt.time

    if "data" in df.columns:
        df["ano"] = df["data"].dt.year
        df["mes"] = df["data"].dt.month

        # Dias da semana traduzidos
        dias_semana = {
            "Monday": "Segunda",
            "Tuesday": "Terça",
            "Wednesday": "Quarta",
            "Thursday": "Quinta",
            "Friday": "Sexta",
            "Saturday": "Sábado",
            "Sunday": "Domingo"
        }
        df["dia_da_semana"] = df["data"].dt.day_name().map(dias_semana)

    # ==============================
    # Indicadores principais
    # ==============================
    col1, col2, col3, col4, col5 = st.columns(5)

    total_acidentes = len(df)
    total_mortos = int(df.get("mortos", pd.Series([0])).sum())
    total_graves = int(df.get("gravemente_feridos", pd.Series([0])).sum())
    total_leves = int(df.get("levemente_feridos", pd.Series([0])).sum())
    total_ilesos = int(df.get("ilesos", pd.Series([0])).sum())

    col1.metric("🚨 Total de Acidentes", f"{total_acidentes:,}".replace(",", "."))
    col2.metric("☠️ Mortos", total_mortos)
    col3.metric("🩸 Feridos Graves", total_graves)
    col4.metric("🤕 Feridos Leves", total_leves)
    col5.metric("🙂 Ilesos", total_ilesos)

    st.markdown("---")

    # ==============================
    # Gráficos
    # ==============================
    aba1, aba2, aba3 = st.tabs(["📊 Por Tipo", "📅 Temporal", "📍 Localização"])

    with aba1:
        if "tipo_de_acidente" in df.columns:
            fig_tipo = px.bar(
                df["tipo_de_acidente"].value_counts().reset_index(),
                x="index",
                y="tipo_de_acidente",
                labels={"index": "Tipo de Acidente", "tipo_de_acidente": "Ocorrências"},
                title="Tipos de Acidente Mais Comuns"
            )
            st.plotly_chart(fig_tipo, use_container_width=True)

    with aba2:
        if "ano" in df.columns:
            fig_ano = px.line(
                df.groupby("ano")["n_da_ocorrencia"].count().reset_index(),
                x="ano",
                y="n_da_ocorrencia",
                markers=True,
                labels={"ano": "Ano", "n_da_ocorrencia": "Quantidade de Acidentes"},
                title="Evolução Anual de Acidentes"
            )
            st.plotly_chart(fig_ano, use_container_width=True)

        if "mes" in df.columns:
            fig_mes = px.histogram(
                df,
                x="mes",
                nbins=12,
                title="Distribuição Mensal de Acidentes",
                labels={"mes": "Mês", "count": "Ocorrências"}
            )
            st.plotly_chart(fig_mes, use_container_width=True)

    with aba3:
        if "uf" in df.columns:
            fig_uf = px.bar(
                df["uf"].value_counts().reset_index(),
                x="index",
                y="uf",
                labels={"index": "Estado", "uf": "Ocorrências"},
                title="Acidentes por Estado"
            )
            st.plotly_chart(fig_uf, use_container_width=True)

else:
    st.info("👆 Faça upload de um arquivo CSV para começar a análise.")
