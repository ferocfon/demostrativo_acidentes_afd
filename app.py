import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="📊 Dashboard de Acidentes", layout="wide")
st.title("📊 Demonstrativo de Acidentes AFD")

# Upload do arquivo
uploaded_file = st.file_uploader("📂 Envie seu arquivo CSV", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        # Carrega CSV, detecta separador, trata decimal
        df = pd.read_csv(uploaded_file, sep=None, engine="python", decimal=',', encoding="utf-8-sig")

        # Limpeza: remove espaços e aspas extras
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.strip().str.replace('"', '')

        st.success("✅ Arquivo carregado com sucesso!")
        st.subheader("🔍 Pré-visualização dos Dados")
        st.dataframe(df.head())

        # Definição de colunas de veículos e vítimas
        veiculos_cols = [
            "automovel","bicicleta","caminhao","moto","onibus","outros",
            "tracao_animal","transporte_de_cargas_especiais","trator_maquinas","utilitarios"
        ]
        vitimas_cols = ["ilesos","levemente_feridos","moderadamente_feridos","gravemente_feridos","mortos"]

        # Criar abas
        aba1, aba2, aba3, aba4 = st.tabs([
            "📌 Visão Geral",
            "📈 Indicadores por Tipo",
            "📅 Evolução Temporal",
            "🚛 Análise por Veículo/Frota"
        ])

        # ===== ABA 1 - Visão Geral =====
        with aba1:
            st.subheader("📌 Visão Geral")
            col1, col2, col3, col4 = st.columns(4)

            total_acidentes = len(df)
            tipos_unicos = df["tipo_de_acidente"].nunique() if "tipo_de_acidente" in df else 0
            total_veiculos = df[veiculos_cols].sum().sum()
            total_vitimas = df[vitimas_cols].sum().sum()

            col1.metric("Total de Acidentes", total_acidentes)
            col2.metric("Tipos de Acidente", tipos_unicos)
            col3.metric("Veículos Envolvidos", total_veiculos)
            col4.metric("Total de Vítimas", total_vitimas)

        # ===== ABA 2 - Indicadores por Tipo =====
        with aba2:
            st.subheader("📈 Distribuição por Tipo de Acidente")
            if "tipo_de_acidente" in df:
                fig, ax = plt.subplots(figsize=(8,4))
                df["tipo_de_acidente"].value_counts().plot(kind="bar", ax=ax, color='skyblue')
                ax.set_ylabel("Qtd. Acidentes")
                ax.set_xlabel("Tipo de Acidente")
                ax.set_title("Acidentes por Tipo")
                st.pyplot(fig)
            else:
                st.warning("⚠️ A coluna 'tipo_de_acidente' não foi encontrada.")

        # ===== ABA 3 - Evolução Temporal =====
        with aba3:
            st.subheader("📅 Evolução Temporal")
            if "data" in df:
                df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)
                df_filtrado = df.dropna(subset=["data"])
                if not df_filtrado.empty:
                    evolucao = df_filtrado.groupby(df_filtrado["data"].dt.to_period("M")).size()
                    fig, ax = plt.subplots(figsize=(10,4))
                    evolucao.plot(ax=ax, marker='o', color='green')
                    ax.set_ylabel("Qtd. Acidentes")
                    ax.set_xlabel("Mês")
                    ax.set_title("Evolução de Acidentes ao Longo do Tempo")
                    st.pyplot(fig)
                else:
                    st.warning("⚠️ Nenhuma data válida encontrada.")
            else:
                st.warning("⚠️ A coluna 'data' não foi encontrada.")

        # ===== ABA 4 - Análise por Veículo/Frota =====
        with aba4:
            st.subheader("🚛 Acidentes por Veículo/Frota")
            if all(col in df.columns for col in veiculos_cols):
                veiculos_sum = df[veiculos_cols].sum().sort_values(ascending=False)
                fig, ax = plt.subplots(figsize=(8,4))
                veiculos_sum.plot(kind="bar", ax=ax, color='orange')
                ax.set_ylabel("Qtd. Acidentes")
                ax.set_xlabel("Tipo de Veículo")
                ax.set_title("Acidentes por Tipo de Veículo")
                st.pyplot(fig)
            else:
                st.warning("⚠️ Algumas colunas de veículos não foram encontradas.")

    except Exception as e:
        st.error(f"❌ Erro ao carregar o arquivo: {e}")
