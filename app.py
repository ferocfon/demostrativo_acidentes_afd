import streamlit as st
import pandas as pd
import plotly.express as px

# =======================
# Carregamento do arquivo
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
        df["km"] = (
            df["km"].astype(str)
            .str.replace(",", ".", regex=False)
            .str.extract(r"(\d+\.?\d*)")[0]
        )
        df["km"] = pd.to_numeric(df["km"], errors="coerce")

    # Coluna tipo_de_acidente
    if "tipo_de_acidente" in df.columns:
        df["tipo_de_acidente"] = df["tipo_de_acidente"].astype(str).str.replace('"', "")

    # Coluna veículo (opcional)
    if "veiculo" in df.columns:
        df["veiculo"] = df["veiculo"].astype(str)

    # Garantir que todas as colunas de objeto sejam strings
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)

    return df

# =======================
# Configuração do app
# =======================
st.set_page_config(page_title="Dashboard de Acidentes Premium", layout="wide")
st.title("🚛 Dashboard de Acidentes Premium - AFD")

arquivo = st.file_uploader("Carregue o arquivo CSV", type=["csv"])

if arquivo is not None:
    df = carregar_dados(arquivo)
    df_filtered = df.copy()

    # -----------------------
    # Sidebar com filtros
    # -----------------------
    st.sidebar.header("Filtros Avançados")

    if "tipo_de_acidente" in df_filtered.columns:
        tipos = df_filtered["tipo_de_acidente"].unique()
        filtro_tipo = st.sidebar.multiselect("Tipo de acidente:", tipos, default=tipos)
        df_filtered = df_filtered[df_filtered["tipo_de_acidente"].isin(filtro_tipo)]

    if "veiculo" in df_filtered.columns:
        veiculos = df_filtered["veiculo"].unique()
        filtro_veiculo = st.sidebar.multiselect("Veículo:", veiculos, default=veiculos)
        df_filtered = df_filtered[df_filtered["veiculo"].isin(filtro_veiculo)]

    if "data" in df_filtered.columns:
        data_min = df_filtered["data"].min().date()
        data_max = df_filtered["data"].max().date()
        periodo = st.sidebar.date_input("Período:", [data_min, data_max])
        df_filtered = df_filtered[(df_filtered["data"] >= pd.to_datetime(periodo[0])) &
                                  (df_filtered["data"] <= pd.to_datetime(periodo[1]))]

    if "km" in df_filtered.columns:
        km_min = int(df_filtered["km"].min())
        km_max = int(df_filtered["km"].max())
        km_range = st.sidebar.slider("Faixa de KM percorrido:", km_min, km_max, (km_min, km_max))
        df_filtered = df_filtered[(df_filtered["km"] >= km_range[0]) & (df_filtered["km"] <= km_range[1])]

    # -----------------------
    # KPIs com análise
    # -----------------------
    st.subheader("📌 Indicadores Principais")
    col1, col2, col3, col4, col5 = st.columns(5)

    total_acidentes = len(df_filtered)
    media_mensal = df_filtered.groupby(df_filtered["data"].dt.to_period("M")).size().mean() if "data" in df_filtered.columns else 0
    tipo_mais_freq = df_filtered["tipo_de_acidente"].mode()[0] if "tipo_de_acidente" in df_filtered.columns else "N/A"
    acidentes_por_tipo = df_filtered["tipo_de_acidente"].value_counts(normalize=True).max() if "tipo_de_acidente" in df_filtered.columns else 0
    acidentes_por_veiculo = df_filtered["veiculo"].value_counts().max() if "veiculo" in df_filtered.columns else 0

    col1.metric("Total de Acidentes", total_acidentes)
    col2.metric("Média Mensal", f"{media_mensal:.1f}")
    col3.metric("Tipo mais Frequente", tipo_mais_freq)
    col4.metric("Maior % por Tipo", f"{acidentes_por_tipo*100:.1f}%")
    col5.metric("Veículo com mais acidentes", acidentes_por_veiculo)

    # -----------------------
    # Abas para gráficos
    # -----------------------
    abas = st.tabs([
        "📄 Prévia dos Dados", 
        "📊 Acidentes por Tipo", 
        "🗓 Acidentes por Mês", 
        "📈 Tendência Temporal", 
        "🚛 Distribuição por Veículo", 
        "📏 Análise de KM"
    ])

    # Aba 1: Prévia dos Dados
    with abas[0]:
        st.dataframe(df_filtered.head(50))

    # Aba 2: Acidentes por Tipo
    with abas[1]:
        if "tipo_de_acidente" in df_filtered.columns:
            df_tipo = df_filtered["tipo_de_acidente"].value_counts().reset_index()
            df_tipo.columns = ["Tipo de Acidente", "Quantidade"]
            fig = px.pie(df_tipo, names="Tipo de Acidente", values="Quantidade",
                         title="Distribuição por Tipo de Acidente", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'tipo_de_acidente' não encontrada no CSV.")

    # Aba 3: Acidentes por Mês
    with abas[2]:
        if "data" in df_filtered.columns:
            df_filtered["mes"] = df_filtered["data"].dt.to_period("M").astype(str)
            df_mes = df_filtered["mes"].value_counts().sort_index().reset_index()
            df_mes.columns = ["Mês", "Quantidade"]
            fig = px.bar(df_mes, x="Mês", y="Quantidade",
                         title="Acidentes por Mês", text="Quantidade")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'data' não encontrada no CSV.")

    # Aba 4: Tendência Temporal
    with abas[3]:
        if "data" in df_filtered.columns:
            df_trend = df_filtered.groupby(df_filtered["data"].dt.to_period("M")).size().reset_index(name="Quantidade")
            df_trend["data"] = df_trend["data"].dt.to_timestamp()
            fig = px.line(df_trend, x="data", y="Quantidade", title="Tendência de Acidentes ao longo do Tempo",
                          markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'data' não encontrada no CSV.")

    # Aba 5: Distribuição por Veículo
    with abas[4]:
        if "veiculo" in df_filtered.columns:
            df_veiculo = df_filtered["veiculo"].value_counts().reset_index()
            df_veiculo.columns = ["Veículo", "Quantidade"]
            fig = px.bar(df_veiculo, x="Veículo", y="Quantidade", title="Acidentes por Veículo",
                         text="Quantidade")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'veiculo' não encontrada no CSV.")

    # Aba 6: Análise de KM
    with abas[5]:
        if "km" in df_filtered.columns:
            fig = px.histogram(df_filtered, x="km", nbins=30, title="Distribuição de KM percorrido")
            st.plotly_chart(fig, use_container_width=True)
            st.write("📌 Estatísticas de KM")
            st.write(df_filtered["km"].describe())
        else:
            st.info("Coluna 'km' não encontrada no CSV.")

    # -----------------------
    # Exportar CSV filtrado
    # -----------------------
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Baixar CSV Filtrado", data=csv, file_name="acidentes_filtrado.csv", mime="text/csv")

else:
    st.info("Faça upload de um arquivo CSV para começar.")
