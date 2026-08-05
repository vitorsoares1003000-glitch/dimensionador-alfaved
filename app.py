import streamlit as st
import io
import math
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm

# =============================================================================
# CONFIGURACAO
# =============================================================================
st.set_page_config(page_title="AlfaVed Dimensionador PHE", page_icon="▲", layout="wide")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #003049 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-left: 5px solid #003049;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# BANCOS DE DADOS
# =============================================================================
CONTATOS_ALFAVED = [
    {"nome": "Vitor Soares", "cargo": "Engenharia de Aplicacao", "email": "engenharia@alfaved.com.br", "tel": "(18) 99669-7330"},
    {"nome": "Jhonatan Dias Dejato", "cargo": "Diretor de Engenharia", "email": "jhonatan@alfaved.com.br", "tel": "(18) 99628-8714"}
]

BANCO_MODELOS = {
    "M3": {"area": 0.03, "Pmax": 16, "Tmax": 180, "dh": 0.003, "conn": "1.25 pol", "cat": "Gaxetado", "w": 200, "h": 480, "vd": 350, "hd": 120, "port": 32, "frame": 20, "weight": 45},
    "M6-B": {"area": 0.15, "Pmax": 10, "Tmax": 180, "dh": 0.004, "conn": "2 pol", "cat": "Gaxetado", "w": 320, "h": 920, "vd": 700, "hd": 200, "port": 50, "frame": 30, "weight": 120},
    "TS6M": {"area": 0.18, "Pmax": 25, "Tmax": 180, "dh": 0.004, "conn": "2 pol", "cat": "Gaxetado", "w": 320, "h": 950, "vd": 720, "hd": 200, "port": 50, "frame": 40, "weight": 180},
    "M10-B": {"area": 0.24, "Pmax": 10, "Tmax": 180, "dh": 0.005, "conn": "4 pol", "cat": "Gaxetado", "w": 470, "h": 1080, "vd": 820, "hd": 300, "port": 100, "frame": 40, "weight": 350},
    "M15-B": {"area": 0.36, "Pmax": 10, "Tmax": 180, "dh": 0.006, "conn": "6 pol", "cat": "Gaxetado", "w": 610, "h": 1850, "vd": 1400, "hd": 400, "port": 150, "frame": 50, "weight": 850},
    "T20-B": {"area": 0.85, "Pmax": 10, "Tmax": 180, "dh": 0.008, "conn": "8 pol", "cat": "Gaxetado", "w": 780, "h": 2100, "vd": 1600, "hd": 500, "port": 200, "frame": 60, "weight": 1400},
    "MA30-S": {"area": 1.38, "Pmax": 16, "Tmax": 180, "dh": 0.010, "conn": "12 pol", "cat": "Gaxetado", "w": 1150, "h": 2900, "vd": 2200, "hd": 750, "port": 300, "frame": 80, "weight": 3200},
    "M10-BW": {"area": 0.24, "Pmax": 25, "Tmax": 200, "dh": 0.005, "conn": "4 pol", "cat": "Semi-Soldado", "w": 470, "h": 1080, "vd": 820, "hd": 300, "port": 100, "frame": 50, "weight": 420},
    "MK15-BW": {"area": 0.42, "Pmax": 25, "Tmax": 200, "dh": 0.006, "conn": "6 pol", "cat": "Semi-Soldado", "w": 610, "h": 1850, "vd": 1400, "hd": 400, "port": 150, "frame": 60, "weight": 980},
    "TK20-BW": {"area": 0.68, "Pmax": 30, "Tmax": 200, "dh": 0.007, "conn": "8 pol", "cat": "Semi-Soldado", "w": 780, "h": 2100, "vd": 1600, "hd": 500, "port": 200, "frame": 70, "weight": 1650},
    "WideGap 350": {"area": 1.80, "Pmax": 10, "Tmax": 160, "dh": 0.015, "conn": "14 pol", "cat": "WideGap", "w": 1300, "h": 3200, "vd": 2400, "hd": 850, "port": 350, "frame": 100, "weight": 4500}
}

BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "visc": 0.0008, "dens": 997, "cond": 0.6},
    "Leite Integral": {"cp": 3.89, "visc": 0.0021, "dens": 1030, "cond": 0.55},
    "Suco de Laranja": {"cp": 3.75, "visc": 0.0035, "dens": 1040, "cond": 0.52},
    "Oleo Vegetal": {"cp": 1.97, "visc": 0.045, "dens": 915, "cond": 0.17},
    "Cerveja": {"cp": 4.10, "visc": 0.0015, "dens": 1010, "cond": 0.58},
    "Iogurte": {"cp": 3.50, "visc": 0.150, "dens": 1050, "cond": 0.50}
}

BANCO_SERVICOS = {
    "Agua Gelada": {"cp": 4.19, "visc": 0.0015, "dens": 1000, "cond": 0.58},
    "Agua Quente": {"cp": 4.18, "visc": 0.0004, "dens": 970, "cond": 0.65},
    "Vapor Saturado": {"cp": 2.01, "visc": 0.000015, "dens": 1.2, "cond": 0.025},
    "Glicol 30%": {"cp": 3.75, "visc": 0.0032, "dens": 1045, "cond": 0.48},
    "Oleo Termico": {"cp": 2.10, "visc": 0.012, "dens": 860, "cond": 0.13}
}

# =============================================================================
# FUNCOES DE ENGENHARIA
# =============================================================================
def calc_lmtd(t1e, t1s, t2e, t2s):
    dt1 = abs(t1e - t2s)
    dt2 = abs(t1s - t2e)
    if dt1 == dt2:
        return max(dt1, 0.001)
    try:
        return (dt1 - dt2) / math.log(dt1 / dt2)
    except (ValueError, ZeroDivisionError):
        return 0.001

def calc_reynolds(vazao_kgh, visc, dens, dh, w_placa):
    if visc <= 0 or dens <= 0 or w_placa <= 0:
        return 0.0
    area_fluxo = w_placa * 0.003
    v_ms = (vazao_kgh / 3600.0) / (dens * area_fluxo)
    re = (dens * v_ms * dh) / visc
    if math.isnan(re) or math.isinf(re):
        return 0.0
    return re

def calc_nusselt(re, pr):
    return 0.3 * (re ** 0.67) * (pr ** 0.33)

def calc_dimensionamento(mod_key, prod_key, serv_key, v_prod, t1e, t1s, t2e, t2s):
    m = BANCO_MODELOS[mod_key]
    p = BANCO_FLUIDOS[prod_key]
    s = BANCO_SERVICOS[serv_key]
    
    carga = (v_prod * p['cp'] * abs(t1e - t1s)) / 3600.0
    
    dt_serv = abs(t2e - t2s)
    v_serv = (carga * 3600.0) / (s['cp'] * dt_serv) if dt_serv > 0 else 0.0
    
    lmtd = calc_lmtd(t1e, t1s, t2e, t2s)
    
    re_p = calc_reynolds(v_prod, p['visc'], p['dens'], m['dh'], m['w'] / 1000.0)
    re_s = calc_reynolds(v_serv, s['visc'], s['dens'], m['dh'], m['w'] / 1000.0)
    
    pr_p = (p['cp'] * 1000.0 * p['visc']) / p['cond'] if p['cond'] > 0 else 1.0
    pr_s = (s['cp'] * 1000.0 * s['visc']) / s['cond'] if s['cond'] > 0 else 1.0
    
    h_p = (calc_nusselt(re_p, pr_p) * p['cond']) / m['dh']
    h_s = (calc_nusselt(re_s, pr_s) * s['cond']) / m['dh']
    
    denom = (1.0 / h_p + 1.0 / h_s + 0.0005 / 17.0 + 0.0001)
    u_global = 1.0 / denom if denom > 0 else 0.0
    
    area_req = (carga * 1000.0) / (u_global * lmtd) if (u_global * lmtd) > 0 else 0.0
    
    n_placas = math.ceil(area_req / m['area']) + 2
    if n_placas % 2 != 0:
        n_placas += 1
    
    return {
        "carga": carga,
        "v_serv": v_serv,
        "lmtd": lmtd,
        "u": u_global,
        "area": area_req,
        "placas": n_placas,
        "re_p": re_p,
        "re_s": re_s
    }

# =============================================================================
# PDF
# =============================================================================
def gerar_pdf(modelo, tag, projeto, produto, servico, res):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    elements = []
    elements.append(Paragraph("AlfaVed - Datasheet Tecnico: " + tag, styles['Title']))
    elements.append(Paragraph("Projeto: " + projeto + " | Data: " + datetime.date.today().strftime('%d/%m/%Y'), styles['Normal']))
    elements.append(Spacer(1, 20))
    
    data = [
        ["Parametro", "Valor"],
        ["Modelo", modelo],
        ["Fluido Produto", produto],
        ["Fluido Servico", servico],
        ["Carga Termica", f"{res['carga']:.2f} kW"],
        ["Vazao Servico", f"{res['v_serv']:.0f} kg/h"],
        ["Area de Troca", f"{res['area']:.2f} m2"],
        ["N de Placas", f"{res['placas']}"],
        ["U Global", f"{res['u']:.0f} W/m2K"],
        ["LMTD", f"{res['lmtd']:.2f} C"]
    ]
    
    t = Table(data, colWidths=[7 * cm, 7 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1b2a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("Contatos Tecnicos", styles['Heading2']))
    for c in CONTATOS_ALFAVED:
        elements.append(Paragraph(f"{c['nome']} - {c['cargo']}", styles['Normal']))
        elements.append(Paragraph(f"Email: {c['email']} | Tel: {c['tel']}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# =============================================================================
# INTERFACE
# =============================================================================
st.markdown('<div class="main-header"><h1>AlfaVed Dimensionador PHE</h1><p>Engenharia Termica de Alta Performance</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Dimensionador", "Datasheet Tecnico", "Relatorio PDF"])

with st.sidebar:
    st.header("Configuracoes do Projeto")
    tag = st.text_input("Tag Equipamento", "TC-101")
    projeto = st.text_input("Projeto", "PRJ-2026-001")

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lado Quente (Produto)")
        produto = st.selectbox("Fluido Produto", list(BANCO_FLUIDOS.keys()), key="prod")
        v_prod = st.number_input("Vazao (kg/h)", value=5000.0, min_value=0.0, key="vazao_prod")
        t1e = st.number_input("Temp. Entrada (C)", value=80.0, key="t1e")
        t1s = st.number_input("Temp. Saida (C)", value=40.0, key="t1s")
    
    with col2:
        st.subheader("Lado Frio (Servico)")
        servico = st.selectbox("Fluido Servico", list(BANCO_SERVICOS.keys()), key="serv")
        t2e = st.number_input("Temp. Entrada Servico (C)", value=25.0, key="t2e")
        t2s = st.number_input("Temp. Saida Servico (C)", value=45.0, key="t2s")
        modelo = st.selectbox("Modelo Alfa Laval", list(BANCO_MODELOS.keys()), key="modelo")
    
    if st.button("Calcular Dimensionamento", type="primary", use_container_width=True):
        res = calc_dimensionamento(modelo, produto, servico, v_prod, t1e, t1s, t2e, t2s)
        
        st.session_state['res'] = res
        st.session_state['modelo'] = modelo
        st.session_state['tag'] = tag
        st.session_state['projeto'] = projeto
        st.session_state['produto'] = produto
        st.session_state['servico'] = servico
        
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Carga Termica", f"{res['carga']:.1f} kW")
        c2.metric("Area Requerida", f"{res['area']:.2f} m2")
        c3.metric("N de Placas", f"{res['placas']}")
        c4.metric("Vazao Servico", f"{res['v_serv']:.0f} kg/h")
        
        st.divider()
        st.subheader("Analise de Turbulencia")
        t1c, t2c = st.columns(2)
        with t1c:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("**Lado Produto**")
            st.metric("Reynolds", f"{res['re_p']:.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        with t2c:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("**Lado Servico**")
            st.metric("Reynolds", f"{res['re_s']:.0f}")
            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    if 'res' in st.session_state:
        res = st.session_state['res']
        mod = st.session_state['modelo']
        st.markdown(f"### Datasheet: {mod}")
        m = BANCO_MODELOS[mod]
        st.write(f"**Categoria:** {m['cat']}")
        st.write(f"**Conexao:** {m['conn']} | **Pressao Max:** {m['Pmax']} bar | **Temp Max:** {m['Tmax']} C")
        st.write(f"**Peso Estimado:** {m['weight']} kg")
        st.write(f"**Dimensoes Aproximadas:** {m['w']} x {m['h']} mm")
        st.write(f"**Numero de Placas Calculado:** {res['placas']}")
        st.write(f"**Comprimento do Pacote:** {res['placas'] * 2.5:.1f} mm")
    else:
        st.info("Realize o calculo na aba Dimensionador para visualizar o datasheet.")

with tab3:
    if 'res' in st.session_state:
        pdf_data = gerar_pdf(
            st.session_state['modelo'],
            st.session_state['tag'],
            st.session_state['projeto'],
            st.session_state['produto'],
            st.session_state['servico'],
            st.session_state['res']
        )
        st.download_button(
            label="Baixar Datasheet PDF",
            data=pdf_data,
            file_name=f"AlfaVed_{st.session_state['tag']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Realize o calculo na aba Dimensionador para gerar o PDF.")
