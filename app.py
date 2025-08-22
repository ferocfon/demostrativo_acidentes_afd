# =======================
# Converte horário de forma robusta
# =======================
if "horario" in df_filtered.columns:
    # Tenta converter diferentes formatos
    df_filtered["horario"] = pd.to_datetime(df_filtered["horario"], errors="coerce").dt.hour
    
    # Remove linhas com horário inválido
    df_filtered = df_filtered[df_filtered["horario"].notna()]
    
    # Converte para inteiro
    df_filtered["horario"] = df_filtered["horario"].astype(int)
    
    # Determina faixa mínima e máxima para slider
    hora_min = df_filtered["horario"].min()
    hora_max = df_filtered["horario"].max()
    
    # Slider na sidebar
    hora_range = st.sidebar.slider(
        "Faixa de Horário (h):",
        min_value=int(hora_min),
        max_value=int(hora_max),
        value=(int(hora_min), int(hora_max))
    )
    
    # Filtra o dataframe conforme o slider
    df_filtered = df_filtered[
        (df_filtered["horario"] >= hora_range[0]) &
        (df_filtered["horario"] <= hora_range[1])
    ]
