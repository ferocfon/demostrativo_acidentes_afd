import pandas as pd
import streamlit as st
import chardet

uploaded_file = st.file_uploader("📂 Envie seu arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Lê os primeiros bytes para detectar encoding
    rawdata = uploaded_file.read(100000)  # lê 100kb do arquivo
    result = chardet.detect(rawdata)
    encoding_detected = result['encoding']

    # Volta o ponteiro do arquivo para o início (senão fica vazio)
    uploaded_file.seek(0)

    # Tenta abrir automaticamente
    try:
        # Detecta se separador é , ou ;
        try:
            df = pd.read_csv(uploaded_file, encoding=encoding_detected)
        except Exception:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=";", encoding=encoding_detected)

        st.success(f"✅ Arquivo carregado com sucesso! Encoding detectado: {encoding_detected}")
        st.write("Pré-visualização dos dados:")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
