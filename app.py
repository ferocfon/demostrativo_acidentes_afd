import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="🚦 Dashboard de Acidentes", layout="wide")

# -----------------------
# Upload do arquivo
# -----------------------
st.title("🚦 Dashboard de Acidentes de Trânsito")

uploaded_file = st.file_uploader("📂 Carregue o arquivo CSV de acidentes", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="utf-8-sig")

    # -----------------------
    # Filtros
    # -----------------------
    st.sidebar.header("📊 Filtros")

    # Filtro por ano
    if "ano" in df.columns:
        anos = sorted(df["ano"].dropna().unique())
        ano_sel = st.sidebar.multiselect("Selecione o ano:", anos, default=anos)
        df = df[df["ano"].isin(ano_sel)]

    # Filtro por mês
    if "mes" in df.columns:
        meses = sorted(df["mes"].dropna().unique())
        mes_sel = st.sidebar.multiselect("Selecione o mês:", meses, default=meses)
        df = df[df["mes"].isin(mes_sel)]

    # -----------------------
    # KPIs principais
    # -----------------------
    st.subheader("📌 Indicadores Principais")

    total_acidentes = len(df)
    total_mortos = df["mortos"].sum() if "mortos" in df.columns else 0

    colunas_feridos = [c for c in df.columns if "ferid" in c.lower()]
    total_feridos = df[colunas_feridos].sum().sum() if colunas_feridos else 0

    tipo_mais_freq = (
        df["tipo_de_acidente"].mode()[0]
        if "tipo_de_acidente" in df.columns and not df.empty
        else "N/A"
    )

    colunas_veiculos = [
        "automovel","bicicleta","caminhao","moto","onibus",
        "outros","tracao_animal","transporte_de_cargas_especiais",
        "trator_maquinas","utilitarios"
    ]
    veiculo_mais_env = "N/A"
    if all(col in df.columns for col in colunas_veiculos):
        soma_veiculos = df[colunas_veiculos].sum().sort_values(ascending=False)
        if not soma_veiculos.empty:
            veiculo_mais_env = soma_veiculos.index[0]

    st.markdown(f"""
    <div style="font-size:28px; padding:15px; border-radius:10px; background:#f0f2f6; margin-bottom:10px;">
        🚨 <b>Total de Acidentes:</b> {total_acidentes:,}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:28px; padding:15px; border-radius:10px; background:#ffe6e6; margin-bottom:10px;">
        💀 <b>Total de Mortos:</b> {total_mortos:,}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:28px; padding:15px; border-radius:10px; background:#fff3cd; margin-bottom:10px;">
        🤕 <b>Total de Feridos:</b> {total_feridos:,}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:28px; padding:15px; border-radius:10px; background:#e6f7ff; margin-bottom:10px;">
        🚗 <b>Veículo mais Envolvido:</b> {veiculo_mais_env.capitalize()}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:28px; padding:15px; border-radius:10px; background:#f0f2f6; margin-bottom:10px;">
        📌 <b>Tipo de Acidente mais Frequente:</b> {tipo_mais_freq}
    </div>
    """, unsafe_allow_html=True)

    # -----------------------
    # Gráficos
    # -----------------------
    st.subheader("📊 Análises Detalhadas")

    col1, col2 = st.columns(2)

    # Top 5 veículos mais envolvidos
    with col1:
        if all(col in df.columns for col in colunas_veiculos):
            soma_veiculos = df[colunas_veiculos].sum().sort_values(ascending=False).head(5)
            fig, ax = plt.subplots()
            soma_veiculos.plot(kind="bar", ax=ax)
            ax.set_title("🚗 Top 5 Veículos mais Envolvidos")
            ax.set_ylabel("Quantidade")
            st.pyplot(fig)

    # Top 5 tipos de acidentes
    with col2:
        if "tipo_de_acidente" in df.columns:
            top_tipos = df["tipo_de_acidente"].value_counts().head(5)
            fig, ax = plt.subplots()
            top_tipos.plot(kind="bar", ax=ax, color="orange")
            ax.set_title("📌 Top 5 Tipos de Acidente")
            ax.set_ylabel("Quantidade")
            st.pyplot(fig)

    # -----------------------
    # Dados brutos
    # -----------------------
    st.subheader("📄 Dados Brutos")
    st.dataframe(df)

else:
    st.info("⬆️ Carregue um arquivo CSV para visualizar o dashboard.")
