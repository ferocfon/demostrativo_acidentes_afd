import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="📊 Dashboard de Acidentes", layout="wide")
st.title("📊 Demonstrativo de Acidentes AFD")

# Upload do arquivo
uploaded_file = st.file_uploader("📂 Envie seu arquivo CSV", type=["csv"])

def load_csv(file):
    encodings = ["utf-8-sig", "latin1", "windows-1252"]
    for enc in encodings:
        try:
            df = pd.read_csv(file, sep=None, engine="python", encoding=enc)
            return df
        except Exception:
            continue
    return None

if uploaded_file is not None:
    df = load_csv(uploaded_file)

    if df is None:
        st.error("❌ Não foi possível ler o CSV. Tente salvar em UTF-8 no Excel.")
    else:
        # Limpeza: remover espaços extras nos nomes das colunas
        df.columns = df.columns.str.strip()
        st.success("✅ Arquivo carregado com sucesso!")
        st.subheader("🔍 Pré-visualização dos Dados")
        st.dataframe(df.head())

        aba1, aba2, aba3, aba4 = st.tabs([
            "📌 Visão Geral",
            "📈 Indicadores por Tipo",
            "📅 Evolução Temporal",
            "🚛 Análise por Frota"
        ])

        # ===== ABA 1 - Visão Geral =====
        with aba1:
            st.subheader("📌 Visão Geral")
            col1, col2, col3 = st.columns(3)
            total_acidentes = len(df)
            tipos_unicos = df["Tipo"].nunique() if "Tipo" in df else 0
            veiculos_unicos = df["Veiculo"].nunique() if "Veiculo" in df else 0

            col1.metric("Total de Acidentes", total_acidentes)
            col2.metric("Tipos de Acidente", tipos_unicos)
            col3.metric("Veículos Envolvidos", veiculos_unicos)

        # ===== ABA 2 - Indicadores por Tipo =====
        with aba2:
            st.subheader("📈 Distribuição por Tipo de Acidente")
            if "Tipo" in df:
                df["Tipo"] = df["Tipo"].astype(str)
                fig, ax = plt.subplots()
                df["Tipo"].value_counts().plot(kind="bar", ax=ax)
                ax.set_ylabel("Qtd. Acidentes")
                ax.set_xlabel("Tipo")
                ax.set_title("Acidentes por Tipo")
                st.pyplot(fig)
            else:
                st.warning("⚠️ A coluna 'Tipo' não foi encontrada no CSV.")

        # ===== ABA 3 - Evolução Temporal =====
        with aba3:
            st.subheader("📅 Evolução Temporal")
            if "Data" in df:
                df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
                df_filtrado = df.dropna(subset=["Data"])
                if not df_filtrado.empty:
                    evolucao = df_filtrado.groupby(df_filtrado["Data"].dt.to_period("M")).size()
                    fig, ax = plt.subplots()
                    evolucao.plot(ax=ax, marker='o')
                    ax.set_ylabel("Qtd. Acidentes")
                    ax.set_xlabel("Data")
                    ax.set_title("Evolução de Acidentes ao Longo do Tempo")
                    st.pyplot(fig)
                else:
                    st.warning("⚠️ Nenhuma data válida encontrada.")
            else:
                st.warning("⚠️ A coluna 'Data' não foi encontrada no CSV.")

        # ===== ABA 4 - Análise por Frota =====
        with aba4:
            st.subheader("🚛 Acidentes por Veículo/Frota")
            if "Veiculo" in df:
                df["Veiculo"] = df["Veiculo"].astype(str)
                fig, ax = plt.subplots()
                df["Veiculo"].value_counts().head(10).plot(kind="bar", ax=ax)
                ax.set_ylabel("Qtd. Acidentes")
                ax.set_xlabel("Veículo")
                ax.set_title("Top 10 Veículos com Mais Acidentes")
                st.pyplot(fig)
            else:
                st.warning("⚠️ A coluna 'Veiculo' não foi encontrada no CSV.")
