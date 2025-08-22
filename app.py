import streamlit as st
import pandas as pd
import plotly.express as px

# =======================
# Função robusta para carregar dados
# =======================
def carregar_dados(caminho):
    # Tenta ler com diferentes separadores
    for sep in [";", ",", "\t"]:
        try:
            df = pd.read_csv(caminho, sep=sep, encoding="latin1")
            if any(col.lower() == "data" for col in df.columns):
                break
        except:
            continue
    else:
        raise ValueError("Não foi possível identificar o separador correto ou coluna 'data' não encontrada.")

    # Normaliza nomes de colunas
    df.columns = df.columns.str.strip().str.lower()

    # Converte data
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    else:
        raise KeyError("Coluna 'data' não encontrada no CSV.")

    # Converte horário
    if "horario" in df.columns:
        df["horario"] = pd.to_datetime(df["horario"], format="%H:%M", errors="coerce").dt.hour
    else:
        raise KeyError("Coluna 'horario' não encontrada no CSV.")

    # Colunas numéricas: km
    if "km" in df.columns:
        df["km"] = df["km"].astype(str).str.replace(",", ".", regex=False)
        df["km"] = pd.to_numeric(df["km"], errors="coerce")

    # Veículos
    veiculos = ["automovel","bicicleta","caminhao","moto","onibus","outros",
                "tracao_animal","transporte_de_cargas_especiais","trator_maquinas","utilitarios"]
    for v in veiculos:
        if v in df.columns:
            df[v] = pd.to_numeric(df[v], errors="coerce").fillna(0)

    # Vítimas
    vitimas = ["ilesos","levemente_feridos","moderadamente_feridos","gravemente_feridos","mortos"]
    for v in vitimas:
        if v in df.columns:
            df[v] = pd.to_numeric(df[v], errors="coerce").fillna(0)

    return df, veiculos, vitimas

# =======================
# Configuração do app
# =======================
st.set_page_config(page_title="Dashboard de Acidentes", layout="wide")
st.title("🚨 Dashboard de Acidentes - BI")

arquivo = st.file_uploader("📂 Carregue o arquivo CSV/TSV", type=["csv","tsv"])

if arquivo is not None:
    df, veiculos, vitimas = carregar_dados(arquivo)
    df_filtered = df.copy()

    # =======================
    # Sidebar com filtros
    # =======================
    st.sidebar.header("Filtros")

    # Tipo de ocorrência
    if "tipo_de_ocorrencia" in df_filtered.columns:
        tipos_ocorrencia = df_filtered["tipo_de_ocorrencia"].unique()
        filtro_tipo_ocorrencia = st.sidebar.multiselect("Tipo de Ocorrência:", tipos_ocorrencia, default=tipos_ocorrencia)
        df_filtered = df_filtered[df_filtered["tipo_de_ocorrencia"].isin(filtro_tipo_ocorrencia)]

    # Tipo de acidente
    if "tipo_de_acidente" in df_filtered.columns:
        tipos_acidente = df_filtered["tipo_de_acidente"].unique()
        filtro_tipo_acidente = st.sidebar.multiselect("Tipo de Acidente:", tipos_acidente, default=tipos_acidente)
        df_filtered = df_filtered[df_filtered["tipo_de_acidente"].isin(filtro_tipo_acidente)]

    # Trecho
    if "trecho" in df_filtered.columns:
        trechos = df_filtered["trecho"].unique()
        filtro_trecho = st.sidebar.multiselect("Trecho:", trechos, default=trechos)
        df_filtered = df_filtered[df_filtered["trecho"].isin(filtro_trecho)]

    # Sentido
    if "sentido" in df_filtered.columns:
        sentidos = df_filtered["sentido"].unique()
        filtro_sentido = st.sidebar.multiselect("Sentido:", sentidos, default=sentidos)
        df_filtered = df_filtered[df_filtered["sentido"].isin(filtro_sentido)]

    # Faixa de horário
    if "horario" in df_filtered.columns:
        hora_min = int(df_filtered["horario"].min())
        hora_max = int(df_filtered["horario"].max())
        hora_range = st.sidebar.slider("Faixa de Horário (h):", hora_min, hora_max, (hora_min, hora_max))
        df_filtered = df_filtered[(df_filtered["horario"] >= hora_range[0]) & (df_filtered["horario"] <= hora_range[1])]

    # =======================
    # KPIs
    # =======================
    st.subheader("📌 KPIs Principais")
    col1, col2, col3, col4, col5 = st.columns(5)

    total_acidentes = len(df_filtered)
    acidentes_com_vitimas = df_filtered[vitimas[1:]].sum().sum()
    total_mortos = df_filtered["mortos"].sum()
    total_feridos = df_filtered[["levemente_feridos","moderadamente_feridos","gravemente_feridos"]].sum().sum()
    tipo_mais_freq = df_filtered["tipo_de_acidente"].mode()[0] if "tipo_de_acidente" in df_filtered.columns else "N/A"

    col1.metric("Total de Acidentes", f"{total_acidentes}")
    col2.metric("Acidentes com Vítimas", f"{int(acidentes_com_vitimas)}")
    col3.metric("Total de Feridos", f"{int(total_feridos)}")
    col4.metric("Total de Mortos", f"{int(total_mortos)}")
    col5.metric("Tipo mais Frequente", tipo_mais_freq)

    # =======================
    # Abas de gráficos
    # =======================
    abas = st.tabs(["Acidentes por Tipo", "Acidentes por Mês", "Acidentes por Tipo de Veículo",
                    "Acidentes por Horário e Sentido", "Acidentes por Trecho"])

    # Aba 1: Acidentes por Tipo
    with abas[0]:
        df_tipo = df_filtered.groupby("tipo_de_acidente").size().reset_index(name="Quantidade")
        fig = px.bar(df_tipo, x="tipo_de_acidente", y="Quantidade",
                     title="Acidentes por Tipo", text="Quantidade",
                     color="Quantidade", color_continuous_scale="Viridis")
        fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
        st.plotly_chart(fig, use_container_width=True)

    # Aba 2: Acidentes por Mês/Ano
    with abas[1]:
        df_filtered["mes_ano"] = df_filtered["data"].dt.to_period("M").astype(str)
        df_mes = df_filtered.groupby("mes_ano").size().reset_index(name="Quantidade")
        fig = px.bar(df_mes, x="mes_ano", y="Quantidade",
                     title="Acidentes por Mês/Ano", text="Quantidade",
                     color="Quantidade", color_continuous_scale="Plasma")
        fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
        st.plotly_chart(fig, use_container_width=True)

    # Aba 3: Acidentes por Tipo de Veículo
    with abas[2]:
        df_veiculos = df_filtered[veiculos].sum().reset_index()
        df_veiculos.columns = ["Veículo", "Quantidade"]
        fig = px.bar(df_veiculos, x="Veículo", y="Quantidade",
                     title="Acidentes por Tipo de Veículo", text="Quantidade",
                     color="Quantidade", color_continuous_scale="Inferno")
        fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
        st.plotly_chart(fig, use_container_width=True)

    # Aba 4: Acidentes por Horário e Sentido
    with abas[3]:
        df_hora = df_filtered.groupby(["horario","sentido"]).size().reset_index(name="Quantidade")
        fig = px.bar(df_hora, x="horario", y="Quantidade", color="sentido",
                     barmode="group", text="Quantidade",
                     title="Acidentes por Horário e Sentido")
        fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
        st.plotly_chart(fig, use_container_width=True)

    # Aba 5: Acidentes por Trecho
    with abas[4]:
        df_trecho = df_filtered.groupby("trecho").size().reset_index(name="Quantidade")
        fig = px.bar(df_trecho, x="trecho", y="Quantidade",
                     title="Acidentes por Trecho da Rodovia", text="Quantidade",
                     color="Quantidade", color_continuous_scale="Cividis")
        fig.update_layout(title_font_size=22, xaxis_title_font_size=16, yaxis_title_font_size=16)
        st.plotly_chart(fig, use_container_width=True)

    # =======================
    # Lista detalhada
    # =======================
    st.subheader("📄 Lista Detalhada de Acidentes")
    df_sorted = df_filtered.sort_values(by="data", ascending=False)
    st.dataframe(df_sorted, use_container_width=True)

    # =======================
    # Download CSV
    # =======================
    st.download_button("📥 Baixar CSV filtrado", df_filtered.to_csv(index=False).encode('utf-8-sig'), "dados_filtrados.csv")

else:
    st.info("Faça upload de um arquivo CSV ou TSV para começar.")
