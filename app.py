import streamlit as st
import pandas as pd
import plotly.express as px

# =======================
# Carregar dados
# =======================
@st.cache_data
def carregar_dados(caminho):
    df = pd.read_csv(caminho, sep=";", encoding="latin1")
    df.columns = df.columns.str.strip()

    # Coluna de data
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")

    # Coluna km (trecho da rodovia)
    if "km" in df.columns:
        df["km"] = df["km"].astype(str).str.replace(",", ".", regex=False)
        df["km"] = pd.to_numeric(df["km"], errors="coerce")

    # Coluna tipo_de_acidente
    if "tipo_de_acidente" in df.columns:
        df["tipo_de_acidente"] = df["tipo_de_acidente"].astype(str).str.replace('"', '')

    # Coluna sentido
    if "sentido" in df.columns:
        df["sentido"] = df["sentido"].astype(str).str.upper()

    # Coluna tipo_veiculo
    if "tipo_veiculo" in df.columns:
        df["tipo_veiculo"] = df["tipo_veiculo"].astype(str)

    # Coluna hora
    if "hora" in df.columns:
        df["hora"] = pd.to_datetime(df["hora"], format="%H:%M", errors="coerce").dt.hour

    return df

# =======================
# Configuração do app
# =======================
st.set_page_config(page_title="Dashboard de Acidentes", layout="wide")
st.title("🚨 Dashboard de Acidentes - AFD")

arquivo = st.file_uploader("📂 Carregue o arquivo CSV", type=["csv"])

if arquivo is not None:
    df = carregar_dados(arquivo)
    df_filtered = df.copy()

    # =======================
    # Sidebar com filtros
    # =======================
    st.sidebar.header("Filtros")
    # Tipo de acidente
    if "tipo_de_acidente" in df_filtered.columns:
        tipos = df_filtered["tipo_de_acidente"].unique()
        filtro_tipo = st.sidebar.multiselect("Tipo de acidente:", tipos, default=tipos)
        df_filtered = df_filtered[df_filtered["tipo_de_acidente"].isin(filtro_tipo)]

    # Período
    if "data" in df_filtered.columns:
        data_min = df_filtered["data"].min().date()
        data_max = df_filtered["data"].max().date()
        periodo = st.sidebar.date_input("Período:", [data_min, data_max])
        df_filtered = df_filtered[(df_filtered["data"] >= pd.to_datetime(periodo[0])) &
                                  (df_filtered["data"] <= pd.to_datetime(periodo[1]))]

    # Trecho (KM)
    if "km" in df_filtered.columns:
        km_min = int(df_filtered["km"].min())
        km_max = int(df_filtered["km"].max())
        km_range = st.sidebar.slider("Trecho da rodovia (KM):", km_min, km_max, (km_min, km_max))
        df_filtered = df_filtered[(df_filtered["km"] >= km_range[0]) & (df_filtered["km"] <= km_range[1])]

    # Sentido
    if "sentido" in df_filtered.columns:
        sentidos = df_filtered["sentido"].unique()
        filtro_sentido = st.sidebar.multiselect("Sentido:", sentidos, default=sentidos)
        df_filtered = df_filtered[df_filtered["sentido"].isin(filtro_sentido)]

    # =======================
    # KPIs
    # =======================
    st.subheader("📌 Indicadores Principais")
    col1, col2, col3, col4 = st.columns(4)

    total_acidentes = len(df_filtered)
    media_mensal = df_filtered.groupby(df_filtered["data"].dt.to_period("M")).size().mean() if "data" in df_filtered.columns else 0
    tipo_mais_freq = df_filtered["tipo_de_acidente"].mode()[0] if "tipo_de_acidente" in df_filtered.columns else "N/A"
    acidentes_por_tipo = df_filtered["tipo_de_acidente"].value_counts(normalize=True).max() if "tipo_de_acidente" in df_filtered.columns else 0

    col1.metric("Total de Acidentes", f"{total_acidentes}", delta_color="inverse")
    col2.metric("Média Mensal", f"{media_mensal:.1f}")
    col3.metric("Tipo mais Frequente", tipo_mais_freq)
    col4.metric("Maior % por Tipo", f"{acidentes_por_tipo*100:.1f}%")

    # =======================
    # Abas de gráficos
    # =======================
    abas = st.tabs(["Acidentes por Tipo", "Acidentes por Mês", "Acidentes por Tipo de Veículo", "Acidentes por Horário e Sentido"])

    # Aba 1: Acidentes por Tipo
    with abas[0]:
        if "tipo_de_acidente" in df_filtered.columns:
            df_tipo = df_filtered["tipo_de_acidente"].value_counts().reset_index()
            df_tipo.columns = ["Tipo de Acidente", "Quantidade"]
            fig = px.bar(df_tipo, x="Tipo de Acidente", y="Quantidade",
                         title="Distribuição por Tipo de Acidente", text="Quantidade",
                         color="Quantidade", color_continuous_scale="Viridis")
            fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'tipo_de_acidente' não encontrada.")

    # Aba 2: Acidentes por Mês
    with abas[1]:
        if "data" in df_filtered.columns:
            df_filtered = df_filtered.copy()
            df_filtered["mes"] = df_filtered["data"].dt.to_period("M").astype(str)
            df_mes = df_filtered["mes"].value_counts().sort_index().reset_index()
            df_mes.columns = ["Mês", "Quantidade"]
            fig = px.bar(df_mes, x="Mês", y="Quantidade",
                         title="Acidentes por Mês", text="Quantidade",
                         color="Quantidade", color_continuous_scale="Plasma")
            fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)

    # Aba 3: Acidentes por Tipo de Veículo
    with abas[2]:
        if "tipo_veiculo" in df_filtered.columns:
            df_veiculo = df_filtered["tipo_veiculo"].value_counts().reset_index()
            df_veiculo.columns = ["Tipo de Veículo", "Quantidade"]
            fig = px.bar(df_veiculo, x="Tipo de Veículo", y="Quantidade",
                         title="Acidentes por Tipo de Veículo", text="Quantidade",
                         color="Quantidade", color_continuous_scale="Inferno")
            fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)

    # Aba 4: Acidentes por Horário e Sentido
    with abas[3]:
        if "hora" in df_filtered.columns and "sentido" in df_filtered.columns:
            df_hora = df_filtered.groupby(["hora", "sentido"]).size().reset_index(name="Quantidade")
            fig = px.bar(df_hora, x="hora", y="Quantidade", color="sentido",
                         barmode="group", text="Quantidade",
                         title="Acidentes por Horário e Sentido")
            fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)

    # =======================
    # Lista detalhada abaixo dos gráficos
    # =======================
    st.subheader("📄 Lista de Acidentes Filtrados")
    st.dataframe(df_filtered.sort_values(by="data", ascending=False), use_container_width=True)

    # =======================
    # Download do CSV filtrado
    # =======================
    st.download_button("📥 Baixar CSV filtrado", df_filtered.to_csv(index=False).encode('utf-8-sig'), "dados_filtrados.csv")

else:
    st.info("Faça upload de um arquivo CSV para começar.")
