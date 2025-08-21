import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =====================
# Configuração inicial
# =====================
st.set_page_config(page_title="Dashboard de Acidentes 🚛", layout="wide")

# Tema global Plotly
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = px.colors.qualitative.Set2

# =====================
# Upload do arquivo
# =====================
st.title("📊 Dashboard de Acidentes Veiculares")
uploaded_file = st.file_uploader("Carregue seu arquivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="utf-8-sig")

    # Conversão da data
    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # =====================
    # Filtros
    # =====================
    st.sidebar.header("🔎 Filtros")
    anos = st.sidebar.multiselect("Ano", sorted(df["data"].dt.year.unique()), default=sorted(df["data"].dt.year.unique()))
    veiculos = st.sidebar.multiselect("Veículo", df["veiculo"].unique(), default=df["veiculo"].unique())

    df_filtered = df[df["data"].dt.year.isin(anos) & df["veiculo"].isin(veiculos)]

    # =====================
    # KPIs em cards
    # =====================
    total_acidentes = len(df_filtered)
    tipo_mais_comum = df_filtered["tipo_de_acidente"].mode()[0] if not df_filtered.empty else "N/A"
    veiculo_mais_env = df_filtered["veiculo"].mode()[0] if not df_filtered.empty else "N/A"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:#FFB703;padding:20px;border-radius:15px;text-align:center'>"
                    f"<h3>Total Acidentes</h3><h2>{total_acidentes}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:#8ECAE6;padding:20px;border-radius:15px;text-align:center'>"
                    f"<h3>Tipo mais comum</h3><h2>{tipo_mais_comum}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:#219EBC;padding:20px;border-radius:15px;text-align:center'>"
                    f"<h3>Veículo mais envolvido</h3><h2>{veiculo_mais_env}</h2></div>", unsafe_allow_html=True)

    # =====================
    # Abas do dashboard
    # =====================
    aba1, aba2, aba3, aba4, aba5 = st.tabs(
        ["📌 Acidentes por Tipo", "📈 Tendência", "🚛 Por Veículo", "🗓️ Dias da Semana", "🏆 Rankings"]
    )

    with aba1:
        st.subheader("Distribuição por Tipo de Acidente")
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(df_filtered, x="tipo_de_acidente", title="Frequência por Tipo")
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.pie(df_filtered, names="tipo_de_acidente", title="Proporção por Tipo")
            st.plotly_chart(fig2, use_container_width=True)

    with aba2:
        st.subheader("Evolução ao Longo do Tempo")
        df_trend = df_filtered.groupby(df_filtered["data"].dt.to_period("M")).size().reset_index(name="contagem")
        df_trend["data"] = df_trend["data"].dt.to_timestamp()
        fig = px.line(df_trend, x="data", y="contagem", markers=True, title="Tendência Mensal")
        st.plotly_chart(fig, use_container_width=True)

    with aba3:
        st.subheader("Distribuição por Veículo")
        fig = px.bar(df_filtered, x="veiculo", title="Acidentes por Veículo")
        st.plotly_chart(fig, use_container_width=True)

    with aba4:
        st.subheader("Acidentes por Dia da Semana")
        df_filtered["dia_semana"] = df_filtered["data"].dt.day_name(locale="pt_BR")
        fig = px.bar(df_filtered, x="dia_semana", title="Distribuição Semanal")
        st.plotly_chart(fig, use_container_width=True)

    with aba5:
        st.subheader("Top 5 Rankings")
        col1, col2 = st.columns(2)

        top_veiculos = df_filtered["veiculo"].value_counts().head(5).reset_index()
        top_veiculos.columns = ["Veículo", "Qtd"]
        fig1 = px.bar(top_veiculos, x="Veículo", y="Qtd", title="Top 5 Veículos")
        col1.plotly_chart(fig1, use_container_width=True)

        top_tipos = df_filtered["tipo_de_acidente"].value_counts().head(5).reset_index()
        top_tipos.columns = ["Tipo", "Qtd"]
        fig2 = px.bar(top_tipos, x="Tipo", y="Qtd", title="Top 5 Tipos de Acidente")
        col2.plotly_chart(fig2, use_container_width=True)

    # =====================
    # Exportação de dados
    # =====================
    st.sidebar.download_button(
        label="📥 Exportar CSV filtrado",
        data=df_filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="acidentes_filtrado.csv",
        mime="text/csv"
    )
