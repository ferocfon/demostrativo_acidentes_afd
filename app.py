import streamlit as st
import pandas as pd
import plotly.express as px

# =======================
# Carregamento do arquivo
# =======================
@st.cache_data
def carregar_dados(file):
    # Tentativa de leitura com encodings diferentes
    encodings = ["latin1", "utf-8-sig", "utf-8"]
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(file, sep=";", encoding=enc)
            break
        except Exception:
            continue
    if df is None:
        st.error("Não foi possível ler o arquivo CSV. Verifique o encoding.")
        return pd.DataFrame()

    # Normalização dos nomes de colunas
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w\s]", "", regex=True)
    )

    # Coluna de data
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.floor("d")
        df["ano"] = df["data"].dt.year
        df["mes"] = df["data"].dt.to_period("M").astype(str)
        df["dia_da_semana"] = df["data"].dt.day_name(locale="pt_BR")

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
        df["tipo_de_acidente"] = df["tipo_de_acidente"].astype(str).str.replace('"', "").str.strip()

    # Converte todas colunas de objeto para string
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    return df

# =======================
# Configuração do app
# =======================
st.set_page_config(page_title="Dashboard de Acidentes", layout="wide")
st.title("📊 Dashboard de Acidentes - AFD")

arquivo = st.file_uploader("Carregue o arquivo CSV", type=["csv"])

if arquivo is not None:
    df = carregar_dados(arquivo)
    if df.empty:
        st.stop()

    df_filtered = df.copy()

    # -----------------------
    # Sidebar com filtros
    # -----------------------
    st.sidebar.header("Filtros")
    if "tipo_de_acidente" in df_filtered.columns:
        tipos = sorted(df_filtered["tipo_de_acidente"].dropna().unique())
        filtro_tipo = st.sidebar.multiselect("Tipo de acidente:", tipos, default=tipos)
        df_filtered = df_filtered[df_filtered["tipo_de_acidente"].isin(filtro_tipo)]

    if "data" in df_filtered.columns:
        data_min = df_filtered["data"].min().date()
        data_max = df_filtered["data"].max().date()
        periodo = st.sidebar.date_input("Período:", [data_min, data_max])
        if len(periodo) == 2:
            df_filtered = df_filtered[
                (df_filtered["data"] >= pd.to_datetime(periodo[0]))
                & (df_filtered["data"] <= pd.to_datetime(periodo[1]))
            ]

    # -----------------------
    # KPIs no topo (em linhas grandes)
    # -----------------------
    st.subheader("📌 Indicadores Principais")

    total_acidentes = len(df_filtered)
    media_mensal = (
        df_filtered.groupby(df_filtered["data"].dt.to_period("M")).size().mean()
        if "data" in df_filtered.columns and not df_filtered.empty
        else 0
    )
    tipo_mais_freq = (
        df_filtered["tipo_de_acidente"].mode()[0]
        if "tipo_de_acidente" in df_filtered.columns and not df_filtered.empty
        else "N/A"
    )
    acidentes_por_tipo = (
        df_filtered["tipo_de_acidente"].value_counts(normalize=True).max()
        if "tipo_de_acidente" in df_filtered.columns and not df_filtered.empty
        else 0
    )

    # Exibir indicadores em linhas maiores
    st.markdown(f"""
    <div style="font-size:28px; padding:15px; border-radius:10px; background:#f0f2f6; margin-bottom:10px;">
        🚨 <b>Total de Acidentes:</b> {total_acidentes:,}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:28px; padding:15px; border-radius:10px; background:#f0f2f6; margin-bottom:10px;">
        📅 <b>Média Mensal de Acidentes:</b> {media_mensal:.1f}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:28px; padding:15px; border-radius:10px; background:#f0f2f6; margin-bottom:10px;">
        🏷️ <b>Tipo mais Frequente:</b> {tipo_mais_freq}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:28px; padding:15px; border-radius:10px; background:#f0f2f6; margin-bottom:10px;">
        📊 <b>Maior % por Tipo:</b> {acidentes_por_tipo*100:.1f}%
    </div>
    """, unsafe_allow_html=True)

    # -----------------------
    # Abas para gráficos
    # -----------------------
    abas = st.tabs(["Prévia dos Dados", "Acidentes por Tipo", "Acidentes por Mês", "Análise de KM", "Tendência Temporal"])

    # Aba 1: Prévia dos Dados
    with abas[0]:
        st.dataframe(df_filtered.head(50))

    # Aba 2: Acidentes por Tipo
    with abas[1]:
        if "tipo_de_acidente" in df_filtered.columns:
            df_tipo = df_filtered["tipo_de_acidente"].value_counts().reset_index()
            df_tipo.columns = ["Tipo de Acidente", "Quantidade"]
            fig = px.bar(df_tipo, x="Tipo de Acidente", y="Quantidade",
                         title="Distribuição por Tipo de Acidente", text="Quantidade")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'tipo_de_acidente' não encontrada no CSV.")

    # Aba 3: Acidentes por Mês
    with abas[2]:
        if "mes" in df_filtered.columns:
            df_mes = df_filtered["mes"].value_counts().sort_index().reset_index()
            df_mes.columns = ["Mês", "Quantidade"]
            fig = px.bar(df_mes, x="Mês", y="Quantidade",
                         title="Acidentes por Mês", text="Quantidade")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'data' não encontrada no CSV.")

    # Aba 4: Análise de KM
    with abas[3]:
        if "km" in df_filtered.columns:
            # Remover outliers para melhor visualização
            q_low = df_filtered["km"].quantile(0.01)
            q_high = df_filtered["km"].quantile(0.99)
            df_km = df_filtered[(df_filtered["km"] >= q_low) & (df_filtered["km"] <= q_high)]

            fig = px.histogram(df_km, x="km", nbins=30,
                               title="Distribuição de KM percorrido (sem outliers)")
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
                          title="Tendência de Acidentes ao longo do Tempo", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'data' não encontrada no CSV.")

else:
    st.info("Faça upload de um arquivo CSV para começar.")
