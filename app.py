import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="📊 Dashboard de Acidentes", layout="wide")

st.title("📊 Demonstrativo de Acidentes AFD")

# ================= Upload e leitura =================
@st.cache_data
def load_csv(uploaded_file):
    encodings = ["utf-8-sig", "latin1", "windows-1252"]
    for enc in encodings:
        try:
            df = pd.read_csv(uploaded_file, sep=None, engine="python", encoding=enc)
            return df, enc
        except Exception:
            continue
    return None, None

uploaded_file = st.file_uploader("📂 Envie seu arquivo CSV", type=["csv"])

if uploaded_file:
    df, enc = load_csv(uploaded_file)

    if df is None:
        st.error("❌ Não foi possível ler o CSV. Tente salvar em UTF-8 no Excel.")
    else:
        st.success(f"✅ Arquivo carregado com sucesso! Encoding detectado: {enc}")

        # ================= Pré-visualização =================
        st.subheader("🔍 Pré-visualização dos Dados")
        st.dataframe(df.head())

        # Normalização de colunas (caso não sigam padrão)
        colunas = {c.lower(): c for c in df.columns}
        tipo_col = colunas.get("tipo")
        veiculo_col = colunas.get("veiculo")
        data_col = colunas.get("data")

        # ================= Filtros globais =================
        with st.expander("🎛️ Filtros"):
            tipo_selec = st.multiselect("Tipo de Acidente", df[tipo_col].unique() if tipo_col else [])
            veiculo_selec = st.multiselect("Veículo", df[veiculo_col].unique() if veiculo_col else [])
            periodo = st.date_input("Período", [])

        if tipo_col:
            if tipo_selec:
                df = df[df[tipo_col].isin(tipo_selec)]
        if veiculo_col:
            if veiculo_selec:
                df = df[df[veiculo_col].isin(veiculo_selec)]
        if data_col and periodo:
            df[data_col] = pd.to_datetime(df[data_col], errors="coerce")
            if len(periodo) == 2:
                df = df[(df[data_col] >= periodo[0]) & (df[data_col] <= periodo[1])]

        # ================= Criar abas =================
        aba1, aba2, aba3, aba4 = st.tabs([
            "📌 Visão Geral",
            "📈 Indicadores por Tipo",
            "📅 Evolução Temporal",
            "🚛 Análise por Frota"
        ])

        # ===== Aba 1 - Visão Geral =====
        with aba1:
            st.subheader("📌 Visão Geral")
            col1, col2, col3 = st.columns(3)

            total_acidentes = len(df)
            tipos_unicos = df[tipo_col].nunique() if tipo_col else 0
            veiculos_unicos = df[veiculo_col].nunique() if veiculo_col else 0

            col1.metric("Total de Acidentes", total_acidentes)
            col2.metric("Tipos de Acidente", tipos_unicos)
            col3.metric("Veículos Envolvidos", veiculos_unicos)

        # ===== Aba 2 - Indicadores por Tipo =====
        with aba2:
            st.subheader("📈 Distribuição por Tipo de Acidente")
            if tipo_col:
                fig = px.bar(df[tipo_col].value_counts().reset_index(),
                             x="index", y=tipo_col, text=tipo_col,
                             labels={"index": "Tipo", tipo_col: "Qtd. Acidentes"},
                             title="Acidentes por Tipo")
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ A coluna 'Tipo' não foi encontrada no CSV.")

        # ===== Aba 3 - Evolução Temporal =====
        with aba3:
            st.subheader("📅 Evolução Temporal")
            if data_col:
                df[data_col] = pd.to_datetime(df[data_col], errors="coerce")
                df_filtrado = df.dropna(subset=[data_col])
                evolucao = df_filtrado.groupby(df_filtrado[data_col].dt.to_period("M")).size().reset_index(name="Qtd")
                evolucao[data_col] = evolucao[data_col].astype(str)

                fig = px.line(evolucao, x=data_col, y="Qtd", markers=True,
                              title="Evolução de Acidentes ao Longo do Tempo")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ A coluna 'Data' não foi encontrada no CSV.")

        # ===== Aba 4 - Análise por Frota =====
        with aba4:
            st.subheader("🚛 Acidentes por Veículo/Frota")
            if veiculo_col:
                top_veiculos = df[veiculo_col].value_counts().head(10).reset_index()
                fig = px.bar(top_veiculos, x="index", y=veiculo_col, text=veiculo_col,
                             labels={"index": "Veículo", veiculo_col: "Qtd. Acidentes"},
                             title="Top 10 Veículos com Mais Acidentes")
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ A coluna 'Veiculo' não foi encontrada no CSV.")
