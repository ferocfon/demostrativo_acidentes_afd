import streamlit as st
import pandas as pd
import plotly.express as px

# =======================
# Função para carregar dados
# =======================
@st.cache_data
def carregar_dados(caminho):
    df = pd.read_csv(caminho, sep=";", encoding="latin1")
    df.columns = df.columns.str.strip()

    # Coluna de data
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.floor('ms')

    # Coluna km
    if "km" in df.columns:
        df["km"] = df["km"].astype(str)
        df["km"] = df["km"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df["km"] = pd.to_numeric(df["km"], errors="coerce")

    # Coluna tipo_de_acidente
    if "tipo_de_acidente" in df.columns:
        df["tipo_de_acidente"] = df["tipo_de_acidente"].astype(str).str.replace('"', '')

    # Converte todas colunas de objeto para string
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)

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

    # KM
    if "km" in df_filtered.columns:
        km_min = int(df_filtered["km"].min())
        km_max = int(df_filtered["km"].max())
        km_range = st.sidebar.slider("Faixa de KM:", km_min, km_max, (km_min, km_max))
        df_filtered = df_filtered[(df_filtered["km"] >= km_range[0]) & (df_filtered["km"] <= km_range[1])]

    # =======================
    # KPIs destacados
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
    # Download do CSV filtrado
    # =======================
    st.download_button("📥 Baixar CSV filtrado", df_filtered.to_csv(index=False).encode('utf-8-sig'), "dados_filtrados.csv")

    # =======================
    # Abas para gráficos
    # =======================
    abas = st.tabs(["Prévia dos Dados", "Acidentes por Tipo", "Acidentes por Mês", "Análise de KM", "Tendência Temporal"])

    # Aba 1: Prévia dos Dados
    with abas[0]:
        st.dataframe(df_filtered.head(), use_container_width=True)

    # Aba 2: Acidentes por Tipo
    with abas[1]:
        if "tipo_de_acidente" in df_filtered.columns:
            df_tipo = df_filtered["tipo_de_acidente"].value_counts().reset_index()
            df_tipo.columns = ["Tipo de Acidente", "Quantidade"]
            fig = px.bar(df_tipo, x="Tipo de Acidente", y="Quantidade",
                         title="Distribuição por Tipo de Acidente", text="Quantidade",
                         color="Quantidade", color_continuous_scale="Viridis")
            fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'tipo_de_acidente' não encontrada no CSV.")

    # Aba 3: Acidentes por Mês
    with abas[2]:
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
        else:
            st.info("Coluna 'data' não encontrada no CSV.")

    # Aba 4: Análise de KM
    with abas[3]:
        if "km" in df_filtered.columns:
            fig = px.histogram(df_filtered, x="km", nbins=30,
                               title="Distribuição de KM percorrido",
                               color_discrete_sequence=["#636EFA"])
            fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)
            st.write("📌 Estatísticas de KM")
            st.write(df_filtered["km"].describe())
        else:
            st.info("Coluna 'km' não encontrada no CSV.")

    # Aba 5: Tendência Temporal
    with abas[4]:
        if "data" in df_filtered.columns:
            df_trend = df_filtered.groupby(df_filtered["data"].dt.to_period("M")).size().reset_index(name="Quantidade")
            df_trend["data"] = df_trend["data"].dt.to_timestamp()
            fig = px.line(df_trend, x="data", y="Quantidade",
                          title="Tendência de Acidentes ao longo do Tempo", markers=True,
                          line_shape="spline")
            fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'data' não encontrada no CSV.")

else:
    st.info("Faça upload de um arquivo CSV para começar.")
