import pandas as pd
import plotly.express as px
import streamlit as st

# --- Dados ---
df = pd.read_csv("seu_arquivo.csv")  # Ajuste para o caminho do seu CSV

# --- Filtros ---
st.sidebar.header("Filtros")
horarios = st.sidebar.multiselect("Horário", df["horario"].unique(), default=df["horario"].unique())
trechos = st.sidebar.multiselect("Trecho", df["trecho"].unique(), default=df["trecho"].unique())
tipos_acidente = st.sidebar.multiselect("Tipo de Acidente", df["tipo_acidente"].unique(), default=df["tipo_acidente"].unique())
tipos_ocorrencia = st.sidebar.multiselect("Tipo de Ocorrência", df["tipo_ocorrencia"].unique(), default=df["tipo_ocorrencia"].unique())

df_filtered = df[
    (df["horario"].isin(horarios)) &
    (df["trecho"].isin(trechos)) &
    (df["tipo_acidente"].isin(tipos_acidente)) &
    (df["tipo_ocorrencia"].isin(tipos_ocorrencia))
]

# --- Ordenação por sentido ---
ordem_sentido = ["Norte", "Sul"]
df_filtered["sentido_ord"] = pd.Categorical(df_filtered["sentido"], categories=ordem_sentido, ordered=True)

# --- KPIs ---
total_acidentes = df_filtered.shape[0]
acidentes_norte = df_filtered[df_filtered["sentido"]=="Norte"].shape[0]
acidentes_sul = df_filtered[df_filtered["sentido"]=="Sul"].shape[0]

st.title("📊 Dashboard de Acidentes - Versão Executiva")
st.subheader("KPIs principais")
st.metric("Total de Acidentes", total_acidentes)
st.metric("Acidentes Norte", acidentes_norte)
st.metric("Acidentes Sul", acidentes_sul)

# --- Gráfico: Acidentes por Horário e Sentido ---
df_hora = df_filtered.groupby(["horario", "sentido_ord"]).size().reset_index(name="Quantidade")
df_hora["sentido"] = df_hora["sentido_ord"]  # Para colorir corretamente

# Ordena pelo valor de quantidade dentro de cada sentido
df_hora = df_hora.sort_values(["Quantidade"], ascending=False)

fig_hora = px.bar(
    df_hora,
    x="horario",
    y="Quantidade",
    color="sentido",
    barmode="group",
    text="Quantidade",
    title="Acidentes por Horário e Sentido",
    color_discrete_map={"Norte":"#1f77b4","Sul":"#ff7f0e"}
)
fig_hora.update_layout(
    xaxis=dict(categoryorder="array", categoryarray=df_hora["horario"].tolist()),
    title_font=dict(size=24),
    legend_title_font=dict(size=16),
    legend_font=dict(size=14)
)
st.plotly_chart(fig_hora, use_container_width=True)

# --- Gráfico: Acidentes por Trecho ---
df_trecho = df_filtered.groupby(["trecho", "sentido_ord"]).size().reset_index(name="Quantidade")
df_trecho = df_trecho.sort_values("Quantidade", ascending=False)

fig_trecho = px.bar(
    df_trecho,
    x="trecho",
    y="Quantidade",
    color="sentido",
    barmode="group",
    text="Quantidade",
    title="Acidentes por Trecho",
    color_discrete_map={"Norte":"#1f77b4","Sul":"#ff7f0e"}
)
st.plotly_chart(fig_trecho, use_container_width=True)

# --- Tabela detalhada ---
df_table = df_filtered.sort_values(["sentido_ord","horario"])
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
