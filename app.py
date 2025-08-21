import pandas as pd
import streamlit as st

st.title("📊 Dashboard de Acidentes AFD")

colunas = [
    "data", "horario", "n_da_ocorrencia", "tipo_de_ocorrencia", "km",
    "trecho", "sentido", "tipo_de_acidente",
    "automovel","bicicleta","caminhao","moto","onibus","outros",
    "tracao_animal","transporte_de_cargas_especiais","trator_maquinas","utilitarios",
    "ilesos","levemente_feridos","moderadamente_feridos","gravemente_feridos","mortos"
]

def load_csv(file):
    try:
        # Lê CSV sem header e tenta detectar separador automaticamente
        df = pd.read_csv(file, sep=None, engine="python", decimal=',', header=None, encoding_errors='replace')
        df.columns = colunas
        # Limpeza
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.strip().str.replace('"', '')
        return df
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")
        return None

uploaded_file = st.file_uploader("📂 Envie seu arquivo CSV", type=["csv", "txt"])

if uploaded_file is not None:
    df = load_csv(uploaded_file)
    if df is not None:
        st.success("✅ Arquivo carregado com sucesso!")
        st.dataframe(df.head())
    else:
        st.error("❌ Não foi possível ler o CSV. Tente salvar o arquivo como CSV padrão com vírgulas ou ponto e vírgula.")
