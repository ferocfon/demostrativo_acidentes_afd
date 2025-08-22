import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide", page_title="Dashboard de Acidentes")
st.title("📊 Dashboard de Acidentes - Versão Executiva")

# --- Função para carregar CSV robusto ---
def carregar_csv(uploaded_file) -> pd.DataFrame:
    try:
        return pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        try:
            return pd.read_csv(uploaded_file, encoding='latin-1')
        except pd.errors.ParserError:
            return pd.read_csv(uploaded_file, sep=';', encoding='latin-1')
    except pd.errors.ParserError:
        try:
            return pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(uploaded_file, sep=';', encoding='latin-1')

uploaded_file = st.file_uploader("📥 Faça upload do CSV de acidentes", type="csv")

if uploaded_file is not None:
    df = carregar_csv(uploaded_file)

    # --- Validação mínima das colunas ---
    col_necessarias = [
        "km","trecho","sentido","tipo_de_acidente",
        "automovel","bicicleta","caminhao","moto","onibus","outros",
        "tracao_animal","transporte_de_cargas_especiais","trator_maquinas","utilitarios",
        "ilesos","levemente_feridos","moderadamente_feridos","gravemente_feridos","mortos"
    ]
    if not all(col in df.columns for col in col_necessarias):
        st.error(f"O CSV precisa conter as colunas: {col_necessarias}")
        st.stop()

    # --- Filtros ---
    st.sidebar.header("Filtros")
    trechos = st.sidebar.multiselect("Trecho", sorted(df["trecho"].unique()), default=sorted(df["trecho"].unique()))
    sentidos = st.sidebar.multiselect("Sentido", sorted(df["sentido"].unique()), default=sorted(df["sentido"].unique()))
    tipos_acidente = st.sidebar.multiselect("Tipo de Acidente", sorted(df["tipo_de_acidente"].unique()), default=sorted(df["tipo_de_acidente"].unique()))

    df_filtered = df[
        (df["trecho"].isin(trechos)) &
        (df["sentido"].isin(sentidos)) &
        (df["tipo_de_acidente"].isin(tipos_acidente))
    ].copy()

    if df_filtered.empty:
        st.warning("⚠️ Nenhum dado corresponde aos filtros selecionados.")
        st.stop()

    # --- Ordenação por sentido ---
    ordem_sentido = ["Norte", "Sul"]
    df_filtered["sentido_ord"] = pd.Categorical(df_filtered["sentido"], categories=ordem_sentido, ordered=True)

    # --- KPIs executivos ---
    st.subheader("KPIs principais")
    total_acidentes = df_filtered.shape[0]
    total_mortos = df_filtered["mortos"].sum()
    total_graves = df_filtered["gravemente_feridos"].sum()
    total_moderados = df_filtered["moderadamente_feridos"].sum()
    total_leves = df_filtered["levemente_feridos"].sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total de Acidentes", total_acidentes)
    col2.metric("Mortos", total_mortos)
    col3.metric("Gravemente Feridos", total_graves)
    col4.metric("Moderadamente Feridos", total_moderados)
    col5.metric("Levemente Feridos", total_leves)

    # --- Função modular para gráficos ---
    def grafico_barras(df_grouped, eixo_x, eixo_y, titulo, cor_col, cores_dict):
        df_grouped = df_grouped.sort_values(eixo_y, ascending=False)
        fig = px.bar(
            df_grouped,
            x=eixo_x,
            y=eixo_y,
            color=cor_col,
            barmode="group",
            text=eixo_y,
            title=titulo,
            color_discrete_map=cores_dict
        )
        fig.update_layout(
            xaxis=dict(categoryorder="array", categoryarray=df_grouped[eixo_x].tolist()),
            title_font=dict(size=24),
            legend_title_font=dict(size=16),
            legend_font=dict(size=14)
        )
        return fig

    # --- Gráfico: Acidentes por Trecho e Sentido ---
    df_trecho = df_filtered.groupby(["trecho","sentido_ord"]).size().reset_index(name="Quantidade")
    df_trecho["sentido"] = df_trecho["sentido_ord"]
    fig_trecho = grafico_barras(df_trecho,"trecho","Quantidade","Acidentes por Trecho e Sentido","sentido",{"Norte":"#1f77b4","Sul":"#ff7f0e"})
    st.plotly_chart(fig_trecho,use_container_width=True)

    # --- Gráfico: Tipo de Acidente ---
    df_tipo = df_filtered.groupby(["tipo_de_acidente","sentido_ord"]).size().reset_index(name="Quantidade")
    df_tipo["sentido"] = df_tipo["sentido_ord"]
    fig_tipo = grafico_barras(df_tipo,"tipo_de_acidente","Quantidade","Acidentes por Tipo e Sentido","sentido",{"Norte":"#1f77b4","Sul":"#ff7f0e"})
    st.plotly_chart(fig_tipo,use_container_width=True)

    # --- Tabela detalhada ---
    df_table = df_filtered.sort_values(["sentido_ord","trecho"])
    st.subheader("📋 Lista detalhada de acidentes")
    st.dataframe(df_table)

    # --- Download CSV filtrado ---
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV Filtrado", data=csv, file_name="acidentes_filtrados.csv", mime="text/csv")

else:
    st.info("⏳ Por favor, faça o upload de um arquivo CSV para visualizar o dashboard.")
