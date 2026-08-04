import streamlit as st
import math
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# 
# BANCO DE DADOS TÉCNICO - DIMENSÕES REAIS (mm)
# 
BANCO_MODELOS = {
    "M3": {"area": 0.03, "width": 200, "height": 480, "v_dist": 354, "h_dist": 104, "port": 32, "frame": 15, "min_L": 100, "max_L": 400, "bolt": "M16", "w_plate": 0.2, "cat": "Gaxetado", "dh": 0.003, "U": 4000},<br/>
    "M6-B": {"area": 0.15, "width": 320, "height": 920, "v_dist": 640, "h_dist": 140, "port": 50, "frame": 20, "min_L": 200, "max_L": 1200, "bolt": "M20", "w_plate": 0.8, "cat": "Gaxetado", "dh": 0.005, "U": 4200},<br/>
    "TS6M": {"area": 0.26, "width": 350, "height": 1050, "v_dist": 720, "h_dist": 160, "port": 65, "frame": 25, "min_L": 300, "max_L": 1500, "bolt": "M24", "w_plate": 1.2, "cat": "Gaxetado", "dh": 0.006, "U": 4600},<br/>
    "M10-B": {"area": 0.24, "width": 470, "height": 1080, "v_dist": 719, "h_dist": 235, "port": 100, "frame": 30, "min_L": 400, "max_L": 2000, "bolt": "M30", "w_plate": 1.5, "cat": "Gaxetado", "dh": 0.006, "U": 4500},<br/>
    "M15-B": {"area": 0.36, "width": 610, "height": 1550, "v_dist": 1050, "h_dist": 310, "port": 150, "frame": 40, "min_L": 500, "max_L": 3000, "bolt": "M36", "w_plate": 2.5, "cat": "Gaxetado", "dh": 0.008, "U": 4700},<br/>
    "T20-B": {"area": 0.85, "width": 780, "height": 1900, "v_dist": 1270, "h_dist": 410, "port": 200, "frame": 50, "min_L": 800, "max_L": 4500, "bolt": "M48", "w_plate": 4.0, "cat": "Gaxetado", "dh": 0.009, "U": 4800},<br/>
    "TS20": {"area": 0.95, "width": 780, "height": 2100, "v_dist": 1450, "h_dist": 410, "port": 200, "frame": 60, "min_L": 800, "max_L": 5000, "bolt": "M48", "w_plate": 4.5, "cat": "Gaxetado", "dh": 0.009, "U": 4950},<br/>
    "MA30-S": {"area": 1.38, "width": 1150, "height": 2850, "v_dist": 1950, "h_dist": 650, "port": 300, "frame": 80, "min_L": 1000, "max_L": 6000, "bolt": "M52", "w_plate": 8.0, "cat": "WideGap", "dh": 0.012, "U": 3800},<br/>
    "WideGap 350": {"area": 1.80, "width": 1250, "height": 3200, "v_dist": 2200, "h_dist": 750, "port": 350, "frame": 100, "min_L": 1200, "max_L": 7000, "bolt": "M56", "w_plate": 10.5, "cat": "WideGap", "dh": 0.015, "U": 3700},<br/>
    "M10-BW": {"area": 0.24, "width": 470, "height": 1080, "v_dist": 719, "h_dist": 235, "port": 100, "frame": 35, "min_L": 400, "max_L": 2000, "bolt": "M30", "w_plate": 1.6, "cat": "Semi-Soldado", "dh": 0.005, "U": 4600},<br/>
    "MK15-BW": {"area": 0.42, "width": 610, "height": 1550, "v_dist": 1050, "h_dist": 310, "port": 150, "frame": 45, "min_L": 500, "max_L": 3000, "bolt": "M36", "w_plate": 2.8, "cat": "Semi-Soldado", "dh": 0.006, "U": 4650},<br/>
    "TK20-BW": {"area": 0.68, "width": 780, "height": 1900, "v_dist": 1270, "h_dist": 410, "port": 200, "frame": 55, "min_L": 800, "max_L": 4500, "bolt": "M48", "w_plate": 4.2, "cat": "Semi-Soldado", "dh": 0.006, "U": 4700},<br/>
    "T20-W": {"area": 0.85, "width": 780, "height": 1900, "v_dist": 1270, "h_dist": 410, "port": 200, "frame": 55, "min_L": 800, "max_L": 4500, "bolt": "M48", "w_plate": 4.2, "cat": "Semi-Soldado", "dh": 0.009, "U": 4800},<br/>
    "MA30-W": {"area": 1.40, "width": 1150, "height": 2850, "v_dist": 1950, "h_dist": 650, "port": 300, "frame": 85, "min_L": 1000, "max_L": 6000, "bolt": "M52", "w_plate": 8.5, "cat": "Semi-Soldado", "dh": 0.010, "U": 4900},
}

BANCO_FLUIDOS = {
    "Agua": {"cp": 4180, "visc": 0.00089, "dens": 1000, "cond": 0.60, "tipo": "base"},<br/>
    "Leite Integral": {"cp": 3890, "visc": 0.00210, "dens": 1030, "cond": 0.55, "tipo": "alimento"},<br/>
    "Suco de Laranja": {"cp": 3750, "visc": 0.00350, "dens": 1040, "cond": 0.54, "tipo": "alimento"},<br/>
    "Oleo Vegetal": {"cp": 1970, "visc": 0.0500, "dens": 920, "cond": 0.17, "tipo": "oleo"},<br/>
    "Cerveja": {"cp": 4100, "visc": 0.00150, "dens": 1010, "cond": 0.58, "tipo": "alimento"},
}

BANCO_SERVICOS = {
    "Agua Fria": {"cp": 4180, "visc": 0.00089, "dens": 1000, "cond": 0.60, "tipo": "base"},<br/>
    "Agua Quente": {"cp": 4180, "visc": 0.00035, "dens": 960, "cond": 0.68, "tipo": "base"},<br/>
    "Vapor Saturado": {"cp": 2000, "visc": 0.000015, "dens": 0.60, "cond": 0.025, "tipo": "vapor"},<br/>
    "Glicol 30%": {"cp": 3700, "visc": 0.00350, "dens": 1040, "cond": 0.50, "tipo": "base"},
}

CONTATOS = [
    {"nome": "Vitor Soares", "cargo": "Responsável de Projeto", "email": "engenharia@alfaved.com.br", "tel": "(18) 9.9669-7330"},<br/>
    {"nome": "Jhonatan Dias Dejato", "cargo": "Diretor de Engenharia", "email": "jhonatan@alfaved.com.br", "tel": "(18) 9.9628-8714"}
]

# 
# FUNÇÕES DE CÁLCULO E UTILITÁRIOS
# 
def calc_lmtd(t1_ent, t1_sai, t2_ent, t2_sai, fluxo="contra"):
    dt1 = abs(t1_ent - t2_sai) if fluxo == "contra" else abs(t1_ent - t2_ent)
    dt2 = abs(t1_sai - t2_ent) if fluxo == "contra" else abs(t1_sai - t2_sai)
    if dt1 == dt2: return dt1<br/>
    if dt1 <= 0 or dt2 <= 0: return 0.1
    return (dt1 - dt2) / math.log(dt1 / dt2)

def generate_dimensional_svg(modelo, d, n_placas):
    total_L = d['frame'] * 2 + (n_placas * 2.5) # 2.5mm por placa aprox
    svg = f"""
    <svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
        <rect width="800" height="400" fill="#f8f9fa" rx="10"/>
        <text x="400" y="30" font-family="Arial" font-size="18" font-weight="bold" fill="#003049" text-anchor="middle">DIAGRAMA DIMENSIONAL - ALFA LAVAL {modelo}</text>
        
        <!-- VISTA FRONTAL -->
        <g transform="translate(50, 60)">
            <rect width="140" height="280" fill="none" stroke="black" stroke-width="2"/>
            <circle cx="35" cy="40" r="15" fill="none" stroke="blue" stroke-width="1.5"/>
            <circle cx="105" cy="40" r="15" fill="none" stroke="blue" stroke-width="1.5"/>
            <circle cx="35" cy="240" r="15" fill="none" stroke="blue" stroke-width="1.5"/>
            <circle cx="105" cy="240" r="15" fill="none" stroke="blue" stroke-width="1.5"/>
            <line x1="70" y1="0" x2="70" y2="280" stroke="gray" stroke-dasharray="4"/>
            <line x1="0" y1="140" x2="140" y2="140" stroke="gray" stroke-dasharray="4"/>
            <text x="70" y="300" font-family="Arial" font-size="12" text-anchor="middle">VISTA FRONTAL</text>
            <text x="-10" y="140" font-family="Arial" font-size="10" transform="rotate(-90, -10, 140)" text-anchor="middle">H: {d['height']}mm</text>
            <text x="70" y="-10" font-family="Arial" font-size="10" text-anchor="middle">W: {d['width']}mm</text>
        </g>

        <!-- VISTA LATERAL -->
        <g transform="translate(350, 60)">
            <rect width="20" height="280" fill="#333"/> <!-- Fixo -->
            <rect x="20" y="20" width="120" height="240" fill="url(#corrugado)"/> <!-- Placas -->
            <rect x="140" y="0" width="20" height="280" fill="#333"/> <!-- Movel -->
            <line x1="0" y1="10" x2="160" y2="10" stroke="black" stroke-width="3"/> <!-- Tirante -->
            <line x1="0" y1="270" x2="160" y2="270" stroke="black" stroke-width="3"/>
            <text x="80" y="300" font-family="Arial" font-size="12" text-anchor="middle">VISTA LATERAL</text>
            <text x="80" y="320" font-family="Arial" font-size="10" text-anchor="middle">L Total: {total_L:.1f}mm</text>
        </g>

        <defs>
            <pattern id="corrugado" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 0 5 L 10 5" stroke="#999" stroke-width="1"/>
                <path d="M 5 0 L 5 10" stroke="#999" stroke-width="1"/>
            </pattern>
        </defs>
    </svg>
    """
    return svg

# 
# INTERFACE STREAMLIT
# 
def main():
    st.set_page_config(page_title="AlfaVed - Dimensionador Alfa Laval", layout="wide")
    
    st.markdown("""<style>
        .main-header { background: #003049; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }<br/>
        .stMetric { background: #f1f3f5; padding: 10px; border-radius: 5px; }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="main-header"><h1>AlfaVed Engenharia Térmica</h1><h3>Dimensionador de Trocadores Alfa Laval v3.0</h3></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Dimensionador", "Datasheet Técnico"])

    with st.sidebar:
        st.header("Parâmetros de Entrada")
        tag = st.text_input("Tag", "TC-101")
        modelo_nome = st.selectbox("Modelo Alfa Laval", list(BANCO_MODELOS.keys()))
        angulo = st.selectbox("Ângulo da Placa", ["Automático", "H (45°)", "L (60°)", "Mista"])
        arranjo_sel = st.selectbox("Arranjo de Passes", ["Automático", "Single Pass (1/1)", "Two Pass (2/2)"])
        fluxo = st.selectbox("Fluxo", ["Contra-corrente", "Co-corrente"])
        
        st.divider()
        prod_nome = st.selectbox("Produto", list(BANCO_FLUIDOS.keys()))
        vazao_p = st.number_input("Vazão Produto (kg/h)", 100, 500000, 5000)
        t_in_p = st.number_input("T. Entrada Prod (°C)", 0.0, 200.0, 85.0)
        t_out_p = st.number_input("T. Saída Prod (°C)", 0.0, 200.0, 40.0)
        
        st.divider()
        serv_nome = st.selectbox("Serviço", list(BANCO_SERVICOS.keys()))
        t_in_s = st.number_input("T. Entrada Serv (°C)", -20.0, 250.0, 25.0)
        t_out_s = st.number_input("T. Saída Serv (°C)", -20.0, 250.0, 35.0)

    # CÁLCULOS
    dp = BANCO_FLUIDOS[prod_nome]
    ds = BANCO_SERVICOS[serv_nome]
    dm = BANCO_MODELOS[modelo_nome]
    
    carga_w = (vazao_p * dp['cp'] * abs(t_in_p - t_out_p)) / 3600.0
    lmtd = calc_lmtd(t_in_p, t_out_p, t_in_s, t_out_s, fluxo="contra" if "Contra" in fluxo else "co")
    
    # Simplificação de U e Área para o exemplo
    U_calc = dm['U']
    area_req = carga_w / (U_calc * lmtd)
    n_placas = math.ceil(area_req / dm['area'])
    if n_placas % 2 == 0: n_placas += 1
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        col1.metric("Carga Térmica", f"{carga_w/1000:.1f} kW")<br/>
        col2.metric("LMTD", f"{lmtd:.1f} °C")
        col3.metric("Nº Placas", n_placas)
        
        st.subheader("Diagnóstico de Projeto")
        if n_placas > 500: st.error("⚠️ Número de placas excessivo para este modelo. Considere um modelo maior.")<br/>
        else: st.success("✅ Dimensionamento dentro dos limites operacionais.")
        
        st.subheader("Contatos Técnicos")
        c1, c2 = st.columns(2)
        for i, c in enumerate(CONTATOS):<br/>
            with (c1 if i==0 else c2):
                st.info(f"**{c['nome']}**

{c['cargo']}

{c['email']}

{c['tel']}")

    with tab2:
        st.subheader(f"Datasheet Técnico - {modelo_nome}")
        
        col_a, col_b = st.columns([1, 1.5])
        
        with col_a:
            st.markdown(f"""
            | Especificação | Valor |
            | :--- | :--- |
            | **Largura (W)** | {dm['width']} mm |
            | **Altura (H)** | {dm['height']} mm |
            | **Dist. Portas V** | {dm['v_dist']} mm |
            | **Dist. Portas H** | {dm['h_dist']} mm |
            | **Diâm. Porta** | {dm['port']} mm |
            | **Parafuso** | {dm['bolt']} |
            | **Peso/Placa** | {dm['w_plate']} kg |
            """)
            
        with col_b:
            svg_code = generate_dimensional_svg(modelo_nome, dm, n_placas)
            st.write(svg_code, unsafe_allow_html=True)
            
        st.divider()
        st.markdown("### Dados de Processo")
        st.table({
            "Parâmetro": ["Fluido", "Vazão (kg/h)", "Temp. Entrada (°C)", "Temp. Saída (°C)"],<br/>
            "Lado Quente": [prod_nome, f"{vazao_p:,.0f}", t_in_p, t_out_p],<br/>
            "Lado Frio": [serv_nome, "Calc...", t_in_s, t_out_s]
        })

if __name__ == "__main__":
    main()
