elif mode == "Seleção de Modelo":
    st.header("🎯 Seleção Automática")
    area = st.number_input("Área (m2)", 1.0, 500.0, 20.0)
    flow = st.number_input("Vazão (m3/h)", 1.0, 1000.0, 50.0)
    pres = st.number_input("Pressão (bar)", 1.0, 50.0, 10.0)
    gas = st.checkbox("Aplicação para Gás")
    if st.button("Selecionar"):
        m, r = ModelSelector.select(area, flow, pres, 100, "gas" if gas else "liquid")
        if m: st.success(f"Modelo: {m.model_code} - {r}")<br/>
        else: st.error(r)

elif mode == "Comparação H vs L":
    st.header("⚖️ Comparação H (45°) vs L (60°)")
    m_code = st.selectbox("Modelo", [m.model_code for m in AlfaLavalDatabase.
