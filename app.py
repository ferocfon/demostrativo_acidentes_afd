import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# UPLOAD DO ARQUIVO
# ======================
st.sidebar.title("📂 Upload do Arquivo")
uploaded_file = st.sidebar.file_uploader("Envie o arquivo de acidentes", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Carregar conforme o tipo
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8-sig")
    else:
        df = pd.read_excel(uploaded_file)
    
    # Ajustes
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df['ano'] = df['data'].dt.year

    # ======================
    # KPIs
    # ======================
    st.title("🚛 Dashboard de Acidentes - Fernão Dias")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total de Acidentes", f"{len(df)}")
    col2.metric("Mortos", int(df['mortos'].sum()))
    col3.metric("Feridos", int(df[['levemente_feridos','moderadamente_feridos','gravemente_feridos']].sum().sum()))
    col4.metric("Ilesos", int(df['ilesos'].sum()))

    # ======================
    # GRÁFICOS
    # ======================

    # Evolução Anual
    st.subheader("📊 Evolução Anual de Acidentes")
    acidentes_ano = df.groupby("ano").size().reset_index(name="Acidentes")
    fig1 = px.line(acidentes_ano, x="ano", y="Acidentes", markers=True, title="Evolução de Acidentes por Ano")
    st.plotly_chart(fig1, use_container_width=True)

    # Tipos de Acidente
    st.subheader("🚦 Distribuição por Tipo de Acidente")
    acidentes_tipo = df['tipo_de_acidente'].value_counts().reset_index()
    acidentes_tipo.columns = ["Tipo", "Quantidade"]
    fig2 = px.pie(acidentes_tipo, values="Quantidade", names="Tipo", hole=0.4,
                  title="Distribuição dos Tipos de Acidente")
    st.plotly_chart(fig2, use_container_width=True)

    # Perfil das Vítimas
    st.subheader("🧍 Perfil das Vítimas")
    vitimas = df[['ilesos','levemente_feridos','moderadamente_feridos','gravemente_feridos','mortos']].sum().reset_index()
    vitimas.columns = ["Condição", "Quantidade"]
    fig3 = px.bar(vitimas, x="Condição", y="Quantidade", color="Condição", text="Quantidade",
                  title="Perfil das Vítimas")
    st.plotly_chart(fig3, use_container_width=True)

    # Tabela
    st.subheader("📑 Amostra dos Dados")
    st.dataframe(df.head(20))

else:
    st.warning("⬅️ Faça o upload de um arquivo (.xlsx ou .csv) para visualizar os dados.")
