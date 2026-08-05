"""
AlfaVed Engenharia Térmica - Dimensionador PHE v4.0
Data: 05 de agosto de 2026<br/>
Arquivo: app.py
"""

import io
import math
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# 
# CONFIGURAÇÃO DA PÁGINA E ESTILO CSS (HTRI/ASPEN STYLE)
# 

st.set_page_config(
    page_title="AlfaVed Dimensionador PHE",
    page_icon="▲",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;<br/>
            background-color: #f8f9fa;
        }

        /* Header Gradiente */
        .main-header {
            background: linear-gradient(135deg, #0d1b2a 0%, #003049 100%);<br/>
            color: white;<br/>
            padding: 2rem;<br/>
            border-radius: 12px;<br/>
            margin-bottom: 2rem;<br/>
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        /* Sidebar Customization */
        [data-testid="stSidebar"] {
            background-color: #0d1b2a;<br/>
            color: white;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Glassmorphism Cards */
        .metric-card {
            background: rgba(255, 255, 255, 0.9);<br/>
            border-radius: 12px;<br/>
            padding: 1.5rem;<br/>
            border-left: 6px solid #003049;<br/>
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);<br/>
            margin-bottom: 1rem;
        }
        
        .metric-value {
            font-size: 1.8rem;<br/>
            font-weight: 700;<br/>
            color: #003049;
        }
        
        .metric-label {
            font-size: 0.9rem;<br/>
            color: #666;<br/>
            text-transform: uppercase;<br/>
            letter-spacing: 1px;
        }

        /* Status Badges */
        .badge {
            padding: 4px 12px;<br/>
            border-radius: 20px;<br/>
            font-size: 12px;<br/>
            font-weight: 600;<br/>
            display: inline-block;
        }
        .badge-ok { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }<br/>
        .badge-warn { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }<br/>
        .badge-crit { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

        /* Diagnóstico Cards */
        .diag-card {
            padding: 1rem;<br/>
            border-radius: 8px;<br/>
            margin-bottom: 10px;<br/>
            border-left: 4px solid;
        }
        .diag-high { background: #fff5f5; border-color: #d90429; color: #721c24; }<br/>
        .diag-med { background: #fffdf2; border-color: #f9c74f; color: #856404; }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;<br/>
            white-space: pre-wrap;<br/>
            font-weight: 600;<br/>
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

# 
# BANCO DE DADOS TÉCNICO
# 

CONTATOS_ALFAVED = {
    "vitor": {"nome": "Vitor Soares", "cargo": "Responsável de Projeto", "email": "engenharia@alfaved.com.br", "tel": "(18) 9.9669-7330"},<br/>
    "jhonatan": {"nome": "Jhonatan Dias Dejato", "cargo": "Diretor de Engenharia", "email": "jhonatan@alfaved.com.br", "tel": "(18) 9.9628-8714"}
}

BANCO_MODELOS = {
    "M3": {"area": 0.03, "Pmax": 16, "Tmax": 180, "dh": 0.003, "conn": 'DN32', "cat": "Gaxetado", "w": 180, "h": 480, "vd": 354, "hd": 60, "port": 32, "frame": 30, "weight": 0.8},<br/>
    "M6-B": {"area": 0.15, "Pmax": 10, "Tmax": 180, "dh": 0.005, "conn": 'DN50', "cat": "Gaxetado", "w": 320, "h": 920, "vd": 640, "hd": 140, "port": 50, "frame": 40, "weight": 2.5},<br/>
    "TS6M": {"area": 0.26, "Pmax": 25, "Tmax": 180, "dh": 0.006, "conn": 'DN65', "cat": "Gaxetado", "w": 400, "h": 1050, "vd": 820, "hd": 180, "port": 65, "frame": 45, "weight": 3.0},<br/>
    "M10-B": {"area": 0.24, "Pmax": 10, "Tmax": 180, "dh": 0.006, "conn": 'DN100', "cat": "Gaxetado", "w": 470, "h": 1084, "vd": 719, "hd": 225, "port": 100, "frame": 50, "weight": 4.0},<br/>
    "M15-B": {"area": 0.36, "Pmax": 10, "Tmax": 180, "dh": 0.008, "conn": 'DN150', "cat": "Gaxetado", "w": 610, "h": 1550, "vd": 1050, "hd": 298, "port": 150, "frame": 60, "weight": 7.5},<br/>
    "T20-B": {"area": 0.85, "Pmax": 10, "Tmax": 180, "dh": 0.009, "conn": 'DN200', "cat": "Gaxetado", "w": 780, "h": 2145, "vd": 1478, "hd": 353, "port": 200, "frame": 70, "weight": 12.0},<br/>
    "TS20": {"area": 0.95, "Pmax": 25, "Tmax": 180, "dh": 0.009, "conn": 'DN200', "cat": "Gaxetado", "w": 850, "h": 2250, "vd": 1580, "hd": 400, "port": 200, "frame": 75, "weight": 13.0},<br/>
    "MA30-S": {"area": 1.38, "Pmax": 25, "Tmax": 180, "dh": 0.012, "conn": 'DN300', "cat": "WideGap", "w": 1000, "h": 2400, "vd": 1800, "hd": 500, "port": 300, "frame": 80, "weight": 18.0},<br/>
    "M10-BW": {"area": 0.24, "Pmax": 55, "Tmax": 250, "dh": 0.005, "conn": 'DN100', "cat": "Semi-Soldado", "w": 470, "h": 1084, "vd": 719, "hd": 225, "port": 100, "frame": 55, "weight": 4.5},<br/>
    "MK15-BW": {"area": 0.42, "Pmax": 41, "Tmax": 200, "dh": 0.006, "conn": 'DN150', "cat": "Semi-Soldado", "w": 650, "h": 1486, "vd": 1044, "hd": 298, "port": 150, "frame": 60, "weight": 8.0},<br/>
    "TK20-BW": {"area": 0.68, "Pmax": 63, "Tmax": 200, "dh": 0.006, "conn": 'DN200', "cat": "Semi-Soldado", "w": 740, "h": 1600, "vd": 1200, "hd": 350, "port": 200, "frame": 70, "weight": 11.0},<br/>
    "T20-W": {"area": 0.85, "Pmax": 30, "Tmax": 180, "dh": 0.009, "conn": 'DN200', "cat": "Semi-Soldado", "w": 780, "h": 2145, "vd": 1478, "hd": 353, "port": 200, "frame": 70, "weight": 12.0},<br/>
    "MA30-W": {"area": 1.40, "Pmax": 40, "Tmax": 180, "dh": 0.010, "conn": 'DN300', "cat": "Semi-Soldado", "w": 1000, "h": 2400, "vd": 1800, "hd": 500, "port": 300, "frame": 80, "weight": 18.0},<br/>
    "WideGap 350": {"area": 1.80, "Pmax": 10, "Tmax": 180, "dh": 0.015, "conn": 'DN350', "cat": "WideGap", "w": 1200, "h": 2800, "vd": 2200, "hd": 600, "port": 350, "frame": 90, "weight": 25.0},
}

BANCO_FLUIDOS = {
    "Agua": {"cp": 4180, "visc": 0.00089, "dens": 1000, "cond": 0.60},<br/>
    "Leite Integral": {"cp": 3890, "visc": 0.00210, "dens": 1030, "cond": 0.55},<br/>
    "Suco de Laranja": {"cp": 3750, "visc": 0.00350, "dens": 1040, "cond": 0.54},<br/>
    "Oleo Vegetal": {"cp": 1970, "visc": 0.0500, "dens": 920, "cond": 0.17},<br/>
    "Cerveja": {"cp": 4100, "visc": 0.00150, "dens": 1010, "cond": 0.58},<br/>
    "Iogurte": {"cp": 3700, "visc": 0.02500, "dens": 1060, "cond": 0.50},
}

BANCO_SERVICOS = {
    "Agua Gelada": {"cp": 4180, "visc": 0.00130, "dens": 1000, "cond": 0.58},<br/>
    "Agua Quente": {"cp": 4180, "visc": 0.00035, "dens": 960, "cond": 0.68},<br/>
    "Vapor Saturado": {"cp": 2000, "visc": 0.000015, "dens": 0.60, "cond": 0.025},<br/>
    "Glicol 30%": {"cp": 3700, "visc": 0.00350, "dens": 1040, "cond": 0.50},<br/>
    "Oleo Termico": {"cp": 2500, "visc": 0.00500, "dens": 850, "cond": 0.13},
}

# 
# FUNÇÕES DE ENGENHARIA
# 

def calc_lmtd(t1e, t1s, t2e, t2s):
    dt1 = abs(t1e - t2s)
    dt2 = abs(t1s - t2e)
    if dt1 == dt2: return dt1<br/>
    if dt1 <= 0 or dt2 <= 0: return 0.1
    return (dt1 - dt2) / math.log(dt1 / dt2)

def calc_reynolds(vazao_kgh, visc, dens, dh, w_placa, n_placas):<br/>
    if n_placas < 2: return 0
    canais = (n_placas - 1) / 2
    v_kgs = (vazao_kgh / 3600) / canais
    area_f = w_placa * (dh / 2)
    u = v_kgs / (dens * area_f)
    return (dens * u * dh) / visc

def calc_nusselt(re, pr, angulo):
    c, m = (0.3, 0.663) if angulo == "H" else (0.15, 0.65)
    return c * (re ** m) * (pr ** 0.33)

def calc_u_global(hp, hs, k_placa=17, esp=0.0005):
    return 1 / ((1/hp) + (1/hs) + (esp/k_placa) + 0.0001)

# 
# VISUALIZAÇÃO TÉCNICA (SVG)
# 

def generate_dimensional_svg(mod, d, n):
    total_l = (n * 2.8) + (d['frame'] * 2)
    esc = 300 / d['h']
    sw, sh = d['w']*esc, d['h']*esc
    pd = d['port']*esc
    
    svg = f'''<svg width="800" height="400" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
    <rect width="800" height="400" fill="#ffffff" />
    <!-- VISTA FRONTAL -->
    <g transform="translate(50, 50)">
        <rect width="{sw}" height="{sh}" fill="none" stroke="#003049" stroke-width="2" />
        <circle cx="{sw*0.2}" cy="{sh*0.15}" r="{pd/2}" fill="#e9ecef" stroke="#003049" />
        <circle cx="{sw*0.8}" cy="{sh*0.15}" r="{pd/2}" fill="#e9ecef" stroke="#003049" />
        <circle cx="{sw*0.2}" cy="{sh*0.85}" r="{pd/2}" fill="#e9ecef" stroke="#003049" />
        <circle cx="{sw*0.8}" cy="{sh*0.85}" r="{pd/2}" fill="#e9ecef" stroke="#003049" />
        <text x="{sw/2}" y="{sh+25}" text-anchor="middle" font-size="12" font-weight="bold">VISTA FRONTAL (W={d['w']}mm)</text>
    </g>
    <!-- VISTA LATERAL -->
    <g transform="translate(450, 50)">
        <rect x="0" y="0" width="15" height="{sh}" fill="#003049" />
        <rect x="15" y="10" width="{total_l*esc*0.5}" height="{sh-20}" fill="#dee2e6" stroke="#adb5bd" />
        <rect x="{15 + total_l*esc*0.5}" y="0" width="15" height="{sh}" fill="#003049" />
        <line x1="-10" y1="30" x2="{30 + total_l*esc*0.5 + 10}" y2="30" stroke="#333" stroke-width="3" />
        <line x1="-10" y1="{sh-30}" x2="{30 + total_l*esc*0.5 + 10}" y2="{sh-30}" stroke="#333" stroke-width="3" />
        <text x="{(30 + total_l*esc*0.5)/2}" y="{sh+25}" text-anchor="middle" font-size="12" font-weight="bold">VISTA LATERAL (L={total_l:.0f}mm)</text>
    </g>
    <text x="400" y="380" text-anchor="middle" font-size="14" fill="#666">Desenho Técnico Esquemático - Alfa Laval {mod}</text>
    </svg>'''
    return svg

# 
# RELATÓRIO PDF
# 

def gerar_pdf(dados, res):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_st = ParagraphStyle("T", parent=styles["Heading1"], fontSize=18, textColor=colors.HexColor("#003049"), alignment=1, spaceAfter=20)
    h2_st = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#003049"), spaceBefore=15, spaceAfter=10)
    
    story = []
    story.append(Paragraph("RELATÓRIO TÉCNICO DE DIMENSIONAMENTO", title_st))
    story.append(Paragraph(f"Equipamento: Alfa Laval {dados['modelo']} | Tag: {dados['tag']}", styles["Normal"]))<br/>
    story.append(Paragraph(f"Data de Emissão: 05 de agosto de 2026", styles["Normal"]))
    story.append(Spacer(1, 12))
    
    # Tabela de Dados
    story.append(Paragraph("1. Parâmetros de Processo", h2_st))
    data = [
        ["Parâmetro", "Lado Quente (Produto)", "Lado Frio (Serviço)"],
        ["Fluido", dados['f_p'], dados['f_s']],
        ["Vazão (kg/h)", f"{dados['v_p']:,}", f"{res['v_s']:.0f}"],
        ["Temp. Entrada (°C)", f"{dados['t_in_p']}", f"{dados['t_in_s']}"],
        ["Temp. Saída (°C)", f"{dados['t_out_p']}", f"{dados['t_out_s']}"]
    ]
    t = Table(data, colWidths=[5*cm, 6*cm, 6*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#003049")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    
    story.append(Paragraph("2. Resultados do Dimensionamento", h2_st))
    res_data = [
        ["Carga Térmica", f"{res['carga']:.2f} kW", "LMTD", f"{res['lmtd']:.2f} °C"],<br/>
        ["U Global", f"{res['u']:.0f} W/m²K", "Área Requerida", f"{res['area']:.2f} m²"],
        ["Nº de Placas", f"{res['n_placas']}", "Modelo", dados['modelo']]
    ]
    t2 = Table(res_data, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
    t2.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('ALIGN', (0,0), (-1,-1), 'LEFT')]))
    story.append(t2)
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("3. Responsáveis Técnicos", h2_st))
    c_data = [
        [CONTATOS_ALFAVED['vitor']['nome'], CONTATOS_ALFAVED['vitor']['cargo'], CONTATOS_ALFAVED['vitor']['tel']],
        [CONTATOS_ALFAVED['jhonatan']['nome'], CONTATOS_ALFAVED['jhonatan']['cargo'], CONTATOS_ALFAVED['jhonatan']['tel']]
    ]
    story.append(Table(c_data, colWidths=[6*cm, 6*cm, 5*cm]))
    
    doc.build(story)
    buf.seek(0)
    return buf

# 
# INTERFACE PRINCIPAL (MAIN)
# 

def main():
    apply_custom_css()
    
    # SIDEBAR
    with st.sidebar:<br/>
        st.markdown("<h1 style='text-align: center;'>▲ AlfaVed</h1>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("⚙️ Configurações do Projeto")
        tag = st.text_input("Tag do Equipamento", "PHE-101")
        proj = st.text_input("Nome do Projeto", "Planta Industrial v2")
        
        st.subheader("📐 Seleção de Hardware")
        cat_sel = st.selectbox("Categoria", ["Todos", "Gaxetado", "Semi-Soldado", "WideGap"])
        modelos_filt = [m for m, d in BANCO_MODELOS.items() if cat_sel == "Todos" or d["cat"] == cat_sel]
        modelo = st.selectbox("Modelo Alfa Laval", modelos_filt)
        angulo = st.radio("Tipo de Placa", ["H (Alta Turbulência)", "L (Baixa ΔP)"], index=0)
        
        st.markdown("---")
        st.caption("v4.0.2 - Engenharia AlfaVed © 2026")

    # HEADER
    st.markdown(f"""
        <div class="main-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="margin:0;">Dimensionador PHE Profissional</h1>
                    <p style="margin:0; opacity: 0.8;">AlfaVed Soluções Industriais | Projeto: {proj}</p>
                </div>
                <div style="text-align: right;">
                    <span class="badge badge-ok">SISTEMA ONLINE</span><br>
                    <small>05/08/2026</small>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # INPUTS DE PROCESSO
    col_p, col_s = st.columns(2)
    
    with col_p:
        st.markdown("### 🌡️ Lado do Produto (Quente)")
        f_p = st.selectbox("Fluido", list(BANCO_FLUIDOS.keys()))
        v_p = st.number_input("Vazão (kg/h)", 100, 1000000, 5000)
        t_in_p = st.number_input("Temp. Entrada (°C)", 0.0, 200.0, 85.0)
        t_out_p = st.number_input("Temp. Saída (°C)", 0.0, 200.0, 45.0)

    with col_s:
        st.markdown("### 💧 Lado do Serviço (Frio)")
        f_s = st.selectbox("Fluido", list(BANCO_SERVICOS.keys()))
        t_in_s = st.number_input("Temp. Entrada Serviço (°C)", -20.0, 150.0, 25.0)
        t_out_s = st.number_input("Temp. Saída Serviço (°C)", -20.0, 150.0, 35.0)

    # CÁLCULOS
    dp, ds, dm = BANCO_FLUIDOS[f_p], BANCO_SERVICOS[f_s], BANCO_MODELOS[modelo]
    
    carga_w = (v_p * dp['cp'] * (t_in_p - t_out_p)) / 3600
    carga_kw = carga_w / 1000
    
    v_s = (carga_w * 3600) / (ds['cp'] * (t_out_s - t_in_s)) if (t_out_s - t_in_s) != 0 else 0
    lmtd = calc_lmtd(t_in_p, t_out_p, t_in_s, t_out_s)
    
    # Iteração simplificada para N de placas
    u_est = 3500
    area_req = carga_w / (u_est * lmtd)
    n_placas = math.ceil(area_req / dm['area']) + 2
    if n_placas % 2 == 0: n_placas += 1
    
    re_p = calc_reynolds(v_p, dp['visc'], dp['dens'], dm['dh'], dm['w']/1000, n_placas)
    re_s = calc_reynolds(v_s, ds['visc'], ds['dens'], dm['dh'], dm['w']/1000, n_placas)
    
    pr_p = (dp['visc'] * dp['cp']) / dp['cond']
    pr_s = (ds['visc'] * ds['cp']) / ds['cond']
    
    nu_p = calc_nusselt(re_p, pr_p, angulo[0])
    nu_s = calc_nusselt(re_s, pr_s, angulo[0])
    
    hp = (nu_p * dp['cond']) / dm['dh']
    hs = (nu_s * ds['cond']) / dm['dh']
    
    u_final = calc_u_global(hp, hs)
    area_final = carga_w / (u_final * lmtd)
    n_final = math.ceil(area_final / dm['area']) + 2
    if n_final % 2 == 0: n_final += 1

    res_dict = {"carga": carga_kw, "v_s": v_s, "lmtd": lmtd, "u": u_final, "area": area_final, "n_placas": n_final}

    # ABAS
    tab1, tab2, tab3 = st.tabs(["📊 Dimensionador", "📐 Datasheet Técnico", "📄 Relatório PDF"])

    with tab1:
        st.markdown("### ⚡ Performance do Equipamento")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:<br/>
            st.markdown(f'<div class="metric-card"><div class="metric-label">Carga Térmica</div><div class="metric-value">{carga_kw:.1f} kW</div></div>', unsafe_allow_html=True)<br/>
        with c2:<br/>
            st.markdown(f'<div class="metric-card"><div class="metric-label">LMTD</div><div class="metric-value">{lmtd:.2f} °C</div></div>', unsafe_allow_html=True)<br/>
        with c3:<br/>
            st.markdown(f'<div class="metric-card"><div class="metric-label">U Global</div><div class="metric-value">{u_final:.0f} <small>W/m²K</small></div></div>', unsafe_allow_html=True)<br/>
        with c4:<br/>
            st.markdown(f'<div class="metric-card" style="border-color:#d90429"><div class="metric-label">Nº Placas</div><div class="metric-value">{n_final}</div></div>', unsafe_allow_html=True)

        st.markdown("#### 🔍 Diagnóstico de Engenharia")
        col_diag1, col_diag2 = st.columns(2)
        
        with col_diag1:
            st.write("**Lado Produto**")
            st.info(f"Reynolds: {re_p:,.0f} | Regime: {'Turbulento' if re_p > 1000 else 'Laminar'}")<br/>
            if re_p < 500:<br/>
                st.markdown('<div class="diag-card diag-med">⚠️ <b>Baixa Turbulência:</b> Considere placas tipo H para aumentar o coeficiente de troca.</div>', unsafe_allow_html=True)
        
        with col_diag2:
            st.write("**Lado Serviço**")
            st.info(f"Reynolds: {re_s:,.0f} | Regime: {'Turbulento' if re_s > 1000 else 'Laminar'}")

    with tab2:<br/>
        st.markdown(f"### 📐 Especificações Técnicas: {modelo}")
        col_svg, col_spec = st.columns([1.5, 1])
        
        with col_svg:
            st.components.v1.html(generate_dimensional_svg(modelo, dm, n_final), height=420)
            
        with col_spec:
            st.markdown("#### Dados Mecânicos")
            st.table({
                "Propriedade": ["Conexão", "Pressão Máx", "Temp Máx", "Largura", "Altura", "Peso Est."],<br/>
                "Valor": [dm['conn'], f"{dm['Pmax']} bar", f"{dm['Tmax']} °C", f"{dm['w']} mm", f"{dm['h']} mm", f"{dm['weight']*n_final:.1f} kg"]
            })

    with tab3:
        st.markdown("### 📄 Geração de Documentação Oficial")
        st.write("Clique no botão abaixo para gerar o relatório técnico completo em formato PDF com o selo de qualidade AlfaVed.")
        
        pdf_data = {"tag": tag, "modelo": modelo, "f_p": f_p, "f_s": f_s, "v_p": v_p, "t_in_p": t_in_p, "t_out_p": t_out_p, "t_in_s": t_in_s, "t_out_s": t_out_s}
        pdf_file = gerar_pdf(pdf_data, res_dict)
        
        st.download_button(
            label="📥 Baixar Relatório Técnico (PDF)",
            data=pdf_file,
            file_name=f"AlfaVed_{tag}_Relatorio.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("#### 📞 Suporte de Engenharia")
        sc1, sc2 = st.columns(2)
        for key, col in zip(['vitor', 'jhonatan'], [sc1, sc2]):
            c = CONTATOS_ALFAVED[key]
            col.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd;">
                    <h4 style="margin:0; color:#003049;">{c['nome']}</h4>
                    <p style="margin:0; font-size: 13px; color: #666;">{c['cargo']}</p>
                    <p style="margin:5px 0 0 0; font-size: 14px;">📧 {c['email']}<br>📞 {c['tel']}</p>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
