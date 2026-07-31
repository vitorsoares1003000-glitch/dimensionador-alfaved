import streamlit as st
import json
import math

# Configuração da página Web com layout expandido e responsivo
st.set_page_config(page_title="AlfaVed Engenharia", page_icon="▲", layout="wide")

# --- INJEÇÃO DE DESIGN E APARÊNCIA CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
        .main-hdr { font-size: 32px; font-weight: bold; color: #0d1b2a; margin-bottom: 2px; }
        .sub-hdr { font-size: 15px; color: #555555; margin-bottom: 20px; }
        div.stButton > button:first-child {
            background-color: #0d1b2a !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 10px 24px !important;
            font-weight: bold !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button:first-child:hover {
            background-color: #d90429 !important;
            transform: scale(1.02) !important;
        }
        div[data-testid="stMetricSimpleValue"] { font-size: 24px !important; font-weight: bold !important; color: #003049 !important; }
        .datasheet-box { background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 15px; }
        .datasheet-title { font-size: 22px; font-weight: bold; color: #0d1b2a; border-bottom: 2px solid #d90429; padding-bottom: 8px; margin-bottom: 20px; text-align: center; }
        .datasheet-sec { font-size: 14px; font-weight: bold; color: #003049; margin-top: 20px; margin-bottom: 10px; border-bottom: 1px solid #eeeeee; padding-bottom: 3px; }
    </style>
""", unsafe_allow_html=True)

BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "viscosidade": 0.89},
    "Leite Integral": {"cp": 3.89, "viscosidade": 2.1},
    "Suco de Laranja": {"cp": 3.75, "viscosidade": 3.5},
    "Oleo Vegetal": {"cp": 1.97, "viscosidade": 50.0}
}

BANCO_SERVICOS = {
    "Agua Industrial": {"cp": 4.18, "latente": 0.0, "tipo": "sensivel"},
    "Glicol 20%": {"cp": 3.85, "latente": 0.0, "tipo": "sensivel"},
    "Glicol 30%": {"cp": 3.65, "latente": 0.0, "tipo": "sensivel"},
    "Vapor Saturado": {"cp": 0.0, "latente": 2200.0, "tipo": "latente"},
    "Amonia Anidra (R717)": {"cp": 0.0, "latente": 1260.0, "tipo": "latente"}
}

BANCO_MODELOS = {
    "Alfa Laval M3": {"area_placa": 0.03, "U_base": 3800},
    "Alfa Laval TL3": {"area_placa": 0.06, "U_base": 3900},
    "Alfa Laval M6": {"area_placa": 0.14, "U_base": 4200},
    "Alfa Laval M6-M": {"area_placa": 0.16, "U_base": 4250},
    "Alfa Laval TL6": {"area_placa": 0.21, "U_base": 4300},
    "Alfa Laval M10": {"area_placa": 0.24, "U_base": 4500},
    "Alfa Laval M10-M": {"area_placa": 0.34, "U_base": 4550},
    "Alfa Laval TL10": {"area_placa": 0.46, "U_base": 4600},
    "Alfa Laval M15": {"area_placa": 0.61, "U_base": 4700}
}

# --- TOPBANE VISUAL CUSTOMIZADO ---
st.markdown('<div class="main-hdr">▲ AlfaVed Soluções Industriais</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-hdr">Dashboard de Engenharia Térmica Avançada e Dimensionamento Hidrodinâmico</div>', unsafe_allow_html=True)

# Barra Lateral Otimizada
st.sidebar.header("Configurações do Projeto")
modelo = st.sidebar.selectbox("Modelo do Equipamento (Alfa Laval)", list(BANCO_MODELOS.keys()))
tag = st.sidebar.text_input("Tag do Equipamento", "TC-101")
projeto = st.sidebar.text_input("Número do Projeto", "PRJ-ALFAVED-2026")

st.sidebar.markdown("---")
st.sidebar.subheader("Parâmetros do Lado do Produto")
produto = st.sidebar.selectbox("Fluido do Produto", list(BANCO_FLUIDOS.keys()))
t_in_prod = st.sidebar.number_input("Temp. Entrada Produto (°C)", value=90.0)
t_out_prod = st.sidebar.number_input("Temp. Saída Produto (°C)", value=8.0)
vazao_prod = st.sidebar.number_input("Vazão do Produto (kg/h)", value=5000.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Parâmetros do Lado do Serviço")
servico_sel = st.sidebar.selectbox("Fluido do Serviço (Utilidade)", list(BANCO_SERVICOS.keys()))

dados_serv_sel = BANCO_SERVICOS[servico_sel]
if dados_serv_sel["tipo"] == "latente":
    t_in_serv = st.sidebar.number_input("Temp. Sat. do Serviço (°C)", value=120.0 if servico_sel == "Vapor Saturado" else -10.0)
    t_out_serv = t_in_serv
    st.sidebar.caption(f"💡 {servico_sel} opera de forma isotérmica por mudança de fase latente.")
else:
    t_in_serv = st.sidebar.number_input("Temp. Entrada Serviço (°C)", value=0.0)
    t_out_serv = st.sidebar.number_input("Temp. Saída Serviço (°C)", value=12.0)

st.sidebar.markdown("---")
disparar_calculo = st.sidebar.button("Executar Cálculo Térmico Rigoroso", type="primary")

if disparar_calculo:
    dados_fluido = BANCO_FLUIDOS[produto]
    dados_modelo = BANCO_MODELOS[modelo]
    cp_prod = dados_fluido["cp"]
    area_por_placa = dados_modelo["area_placa"]

    fator_viscosidade = 1.0 if produto == "Agua" else (1.0 / math.isqrt(int(dados_fluido["viscosidade"])))
    U_adotado = dados_modelo["U_base"] * fator_viscosidade

    dT_prod = abs(t_in_prod - t_out_prod)
    carga_kw = (vazao_prod * cp_prod * dT_prod) / 3600.0

    if dados_serv_sel["tipo"] == "latente":
        vazao_serv = (carga_kw * 3600.0) / dados_serv_sel["latente"]
    else:
        dT_serv = abs(t_out_serv - t_in_serv)
        vazao_serv = (carga_kw * 3600.0) / (dados_serv_sel["cp"] * dT_serv) if dT_serv > 0 else 0
        
    dt1 = t_in_prod - t_out_serv
    dt2 = t_out_prod - t_in_serv

    if dt1 > 0 and dt2 > 0 and dt1 != dt2:
        lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
    else:
        lmtd = (abs(dt1) + abs(dt2)) / 2
        
    area_m2 = (carga_kw * 1000.0) / (U_adotado * lmtd) if lmtd > 0 else 0
    placas = math.ceil(area_m2 / area_por_placa) + 2
    if placas % 2 != 0: placas += 1

    # Regras de Memorial Comercial
    gaxeta_material = "EPDM" if produto != "Oleo Vegetal" else "NBR"
    if servico_sel == "Vapor Saturado": gaxeta_material = "Viton de Alta Densidade"
    if servico_sel == "Amonia Anidra (R717)": gaxeta_material = "Cloroprene Criogenico"

    parecer_ia = f"O dimensionamento para o fluido {produto} operando com o utilitário {servico_sel} no modelo {modelo} indica uma demanda térmica de {carga_kw:.2f} kW. Para conter esse processo com total estanqueidade, a engenharia especifica o uso de gaxetas em {gaxeta_material}. Arranjo final homologado com {placas} placas paralelas (área unitária de {area_por_placa} m²) e coeficiente global de {U_adotado:.0f} W/m².K."

    # RENDERIZAÇÃO DIRETA EM TELA ÚNICA CONTINUA
    st.markdown("### 📊 Indicadores Hidro-Térmicos Rápidos")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Carga Térmica Total", f"{carga_kw:.2f} kW")
    m_col2.metric("Área Efetiva Requerida", f"{area_m2:.2f} m²")
    m_col3.metric("Quantidade de Placas", f"{placas} un")
    m_col4.metric(f"Vazão de {servico_sel}", f"{vazao_serv:.1f} kg/h")
    
    st.markdown('<div class="datasheet-box">', unsafe_allow_html=True)
    st.markdown('<div class="datasheet-title">FOLHA DE DADOS TÉCNICOS - ALFAVED</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="datasheet-sec">1. INFORMAÇÕES GERAIS DO PROJETO</div>', unsafe_allow_html=True)
    g_col1, g_col2, g_col3 = st.columns(3)
    g_col1.write(f"**Modelo Equipamento:** {modelo}")
    g_col2.write(f"**Tag Equipamento:** {tag}")
    g_col3.write(f"**Número do Projeto:** {projeto}")
    
    st.markdown('<div class="datasheet-sec">2. PARÂMETROS OPERACIONAIS DO PROCESSO</div>', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    p_col1.write(f"**LADO DO PRODUTO (PROCESSO):**")
    p_col1.write(f"• **Fluido de Trabalho:** {produto}")
    p_col1.write(f"• **Temperatura de Entrada:** {t_in_prod:.1f} °C")
    p_col1.write(f"• **Temperatura de Saída:** {t_out_prod:.1f} °C")
    p_col1.write(f"• **Vazão de Processo:** {vazao_prod:.0f} kg/h")
    
    p_col2.write(f"**LADO DO SERVIÇO (UTILIDADE):**")
    p_col2.write(f"• **Fluido de Utilidade:** {servico_sel}")
    p_col2.write(f"• **Temperatura de Entrada:** {t_in_serv:.1f} °C")
    p_col2.write(f"• **Temperatura de Saída:** {t_out_serv:.1f} °C")
    p_col2.write(f"• **Vazão Massica Requerida:** {vazao_serv:.1f} kg/h")
    
    st.markdown('<div class="datasheet-sec">3. RESULTADOS DO DIMENSIONAMENTO HIDRO-TÉRMICO</div>', unsafe_allow_html=True)
    r_col1, r_col2 = st.columns(2)
    r_col1.write(f"• **Carga Térmica de Troca:** {carga_kw:.2f} kW")
    r_col1.write(f"• **Área Efetiva Requerida:** {area_m2:.2f} m²")
    r_col1.write(f"• **Quantidade Final de Placas:** {placas} un")
    
    r_col2.write(f"• **Área por Placa Geometria:** {area_por_placa} m²")
    r_col2.write(f"• **Média Logarítmica (LMTD):** {lmtd:.1f} °C")
    r_col2.write(f"• **Coeficiente de Troca Adotado (U):** {U_adotado:.0f} W/m².K")
    
    st.markdown('<div class="datasheet-sec">4. MEMORIAL DESCRITIVO E PARECER DE ENGENHARIA</div>', unsafe_allow_html=True)
    st.info(parecer_ia)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("💡 Insira as especificações operacionais na barra lateral esquerda e clique em 'Executar Cálculo Térmico Rigoroso' para visualizar o Datasheet completo.")
