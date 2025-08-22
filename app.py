import pandas as pd
import plotly.express as px
import streamlit as st

# --- Configuração da página ---
st.set_page_config(layout="wide", page_title="Dashboard de Acidentes")
st.title("📊 Dashboard de Acidentes - Versão Executiva")

# --- Função para carregar CSV com tratamento de codificação ---
def carregar_csv(uploaded_file) -> pd.DataFrame:
    """Tenta carregar CSV como UTF-8, se falhar usa Latin-1."""
    try:
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='latin-1')
    return df

# --- Upload do CSV ---
uploaded_file = st.file_uploader("📥 Faça upload do CSV de acidentes", type="csv")

if uploaded_file is not None:
    df = carregar_csv(uploaded_file)

    # --- Validação mínima ---
    col_necessarias = ["horario", "trecho", "tipo_acidente", "tipo_ocorrencia", "sentido"]
    if not all(col in df.columns for col in col_necessarias):
        st.error(f"O CSV precisa conter as colunas: {col_necessarias}")
        st.stop()

    # --- Filtros ---
    st.sidebar.header("Filtros")
    horarios = st.sidebar.multiselect("Horário", sorted(df["horario"].unique()), default=sorted(df["horario"].unique()))
    trechos = st.sidebar.multiselect("Trecho", sorted(df["trecho"].unique()), default=sorted(df["trecho"].unique()))
    tipos_acidente = st.sidebar.multiselect("Tipo de Acidente", sorted(df["tipo_acidente"].unique()), default=sorted(df["tipo_acidente"].unique()))
    tipos_ocorrencia = st.sidebar.multiselect("Tipo de Ocorrência", sorted(df["tipo_ocorrencia"].unique()), default=sorted(df["tipo_ocorrencia"].unique()))

    df_filtered = df[
        (df["horario"].isin(horarios)) &
        (df["trecho"].isin(trechos)) &
        (df["tipo_acidente"].isin(tipos_acidente)) &
        (df["tipo_ocorrencia"].isin(tipos_ocorrencia))
    ].copy()

    if df_filtered.empty:
        st.warning("⚠️ Nenhum dado corresponde aos filtros selecionados.")
        st.stop()

    # --- Ordenação por sentido ---
    ordem_sentido = ["Norte", "Sul"]
    df_filtered["sentido_ord"] = pd.Categorical(df_filtered["sentido"], categories=ordem_sentido, ordered=True)

    # --- KPIs ---
    total_acidentes = df_filtered.shape[0]
    acidentes_norte = df_filtered[df_filtered["sentido"] == "Norte"].shape[0]
    acidentes_sul = df_filtered[df_filtered["sentido"] == "Sul"].shape[0]

    st.subheader("KPIs principais")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Acidentes", total_acidentes)
    col2.metric("Acidentes Norte", acidentes_norte)
    col3.metric("Acidentes Sul", acidentes_sul)

    # --- Função para criar gráfico de barras ordenado ---
    def grafico_barras(df_grouped, eixo_x, eixo_y, titulo, cor_col, cores_dict):
        """Cria gráfico de barras Plotly ordenado pelo valor do eixo_y"""
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

    # --- Gráfico 1: Acidentes por Horário e Sentido ---
    df_hora = df_filtered.groupby(["horario", "sentido_ord"]).size().reset_index(name="Quantidade")
    df_hora["sentido"] = df_hora["sentido_ord"]
    fig_hora = grafico_barras(df_hora, "horario", "Quantidade", "Acidentes por Horário e Sentido", "sentido", {"Norte":"#1f77b4","Sul":"#ff7f0e"})
    st.plotly_chart(fig_hora, use_container_width=True)

    # --- Gráfico 2: Acidentes por Trecho ---
    df_trecho = df_filtered.groupby(["trecho", "sentido_ord"]).size().reset_index(name="Quantidade")
    df_trecho["sentido"] = df_trecho["sentido_ord"]
    fig_trecho = grafico_barras(df_trecho, "trecho", "Quantidade", "Acidentes por Trecho", "sentido", {"Norte":"#1f77b4","Sul":"#ff7f0e"})
    st.plotly_chart(fig_trecho, use_container_width=True)

    # --- Tabela detalhada ---
    df_table = df_filtered.sort_values(["sentido_ord", "horario"])
    st.subheader("📋 Lista detalhada de acidentes")
    st.dataframe(df_table)

    # --- Download CSV filtrado ---
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV Filtrado",
        data=csv,
        file_name='acidentes_filtrados.csv',
        mime='text/csv'
    )

else:
    st.info("⏳ Por favor, faça o upload de um arquivo CSV para visualizar o dashboard.")
