import streamlit as st
import io
import math
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# 1. CONFIGURACAO DA PAGINA
st.set_page_config(page_title="AlfaVed Dimensionador PHE", page_icon="▲", layout="wide")

# 2. CSS CUSTOMIZADO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #003049 100%);
        color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stSidebar { background-color: #0d1b2a !important; color: white !important; }
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border-left: 5px solid #003049;
        padding: 1.5rem; border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .metric-box {
        background: #f8f9fa; border: 1px solid #e9ecef;
        padding: 1rem; border-radius: 10px; text-align: center;
    }
    .badge {
        padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;
    }
    .badge-green { background: #d4edda; color: #155724; }
    .badge-yellow { background: #fff3cd; color: #856404; }
    .badge-red { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# 3. BANCOS DE DADOS
CONTATOS_ALFAVED = [
    {"nome": "Vitor Soares", "cargo": "Engenharia de Aplicacao", "email": "engenharia@alfaved.com.br", "tel": "(18) 99669-7330"},
    {"nome": "Jhonatan Dias Dejato", "cargo": "Diretor de Engenharia", "email": "jhonatan@alfaved.com.br", "tel": "(18) 99628-8714"}
]

BANCO_MODELOS = {
    "M3": {"area": 0.03, "Pmax": 16, "Tmax": 180, "dh": 0.003, "conn": "1.25\"", "cat": "Gaxetado", "w": 200, "h": 480, "vd": 350, "hd": 120, "port": 32, "frame": 20, "weight": 45},
    "M6-B": {"area": 0.15, "Pmax": 10, "Tmax": 180, "dh": 0.004, "conn": "2\"", "cat": "Gaxetado", "w": 320, "h": 920, "vd": 700, "hd": 200, "port": 50, "frame": 30, "weight": 120},
    "TS6M": {"area": 0.18, "Pmax": 25, "Tmax": 180, "dh": 0.004, "conn": "2\"", "cat": "Gaxetado", "w": 320, "h": 950, "vd": 720, "hd": 200, "port": 50, "frame": 40, "weight": 180},
    "M10-B": {"area": 0.24, "Pmax": 10, "Tmax": 180, "dh": 0.005, "conn": "4\"", "cat": "Gaxetado", "w": 470, "h": 1080, "vd": 820, "hd": 300, "port": 100, "frame": 40, "weight": 350},
    "M15-B": {"area": 0.36, "Pmax": 10, "Tmax": 180, "dh": 0.006, "conn": "6\"", "cat": "Gaxetado", "w": 610, "h": 1850, "vd": 1400, "hd": 400, "port": 150, "frame": 50, "weight": 850},
    "T20-B": {"area": 0.85, "Pmax": 10, "Tmax": 180, "dh": 0.008, "conn": "8\"", "cat": "Gaxetado", "w": 780, "h": 2100, "vd": 1600, "hd": 500, "port": 200, "frame": 60, "weight": 1400},
    "MA30-S": {"area": 1.38, "Pmax": 16, "Tmax": 180, "dh": 0.010, "conn": "12\"", "cat": "Gaxetado", "w": 1150, "h": 2900, "vd": 2200, "hd": 750, "port": 300, "frame": 80, "weight": 3200},
    "M10-BW": {"area": 0.24, "Pmax": 25, "Tmax": 200, "dh": 0.005, "conn": "4\"", "cat": "Semi-Soldado", "w": 470, "h": 1080, "vd": 820, "hd": 300, "port": 100, "frame": 50, "weight": 420},
    "MK15-BW": {"area": 0.42, "Pmax": 25, "Tmax": 200, "dh": 0.006, "conn": "6\"", "cat": "Semi-Soldado", "w": 610, "h": 1850, "vd": 1400, "hd": 400, "port": 150, "frame": 60, "weight": 980},
    "TK20-BW": {"area": 0.68, "Pmax": 30, "Tmax": 200, "dh": 0.007, "conn": "8\"", "cat": "Semi-Soldado", "w": 780, "h": 2100, "vd": 1600, "hd": 500, "port": 200, "frame": 70, "weight": 1650},
    "WideGap 350": {"area": 1.80, "Pmax": 10, "Tmax": 160, "dh": 0.015, "conn": "14\"", "cat": "WideGap", "w": 1300, "h": 3200, "vd": 2400, "hd": 850, "port": 350, "frame": 100, "weight": 4500}
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

# 4. FUNCOES DE ENGENHARIA
def calc_lmtd(t1e, t1s, t2e, t2s):
    dt1 = abs(t1e - t2s)
    dt2 = abs(t1s - t2e)
    if dt1 == dt2:
        return dt1
    if dt1 == 0 or dt2 == 0:
        return 1e-6
    return (dt1 - dt2) / math.log(dt1 / dt2)

def calc_reynolds(vazao_kgh, visc, dens, dh, w_placa):
    v_ms = (vazao_kgh / 3600) / (dens * w_placa * 0.003)
    return (dens * v_ms * dh) / visc

def calc_nusselt(re, pr):
    return 0.3 * (re**0.67) * (pr**0.33)

def calc_dimensionamento(mod_key, prod_key, serv_key, v_prod, t1e, t1s, t2e, t2s):
    m = BANCO_MODELOS[mod_key]
    p = BANCO_FLUIDOS[prod_key]
    s = BANCO_SERVICOS[serv_key]
    
    carga = (v_prod * p['cp'] * abs(t1e - t1s)) / 3600
    v_serv = (carga * 3600) / (s['cp'] * abs(t2e - t2s)) if abs(t2e - t2s) > 0 else 0
    lmtd = calc_lmtd(t1e, t1s, t2e, t2s)
    
    re_p = calc_reynolds(v_prod, p['visc'], p['dens'], m['dh'], m['w']/1000)
    re_s = calc_reynolds(v_serv, s['visc'], s['dens'], m['dh'], m['w']/1000)
    
    pr_p = (p['cp'] * 1000 * p['visc']) / p['cond']
    pr_s = (s['cp'] * 1000 * s['visc']) / s['cond']
    
    h_p = (calc_nusselt(re_p, pr_p) * p['cond']) / m['dh']
    h_s = (calc_nusselt(re_s, pr_s) * s['cond']) / m['dh']
    
    u_global = 1 / (1/h_p + 1/h_s + 0.0005/17 + 0.0001)
    area_req = (carga * 1000) / (u_global * lmtd)
    n_placas = math.ceil(area_req / m['area']) + 2
    if n_placas % 2 != 0:
        n_placas += 1
    
    return {
        "carga": carga, "v_serv": v_serv, "lmtd": lmtd, "u": u_global,
        "area": area_req, "placas": n_placas, "re_p": re_p, "re_s": re_s
    }

# 5. SVG TECNICO
def generate_dimensional_svg(mod_key, n_placas):
    m = BANCO_MODELOS[mod_key]
    w, h = m['w']/4, m['h']/4
    vd, hd = m['vd']/4, m['hd']/4
    p = m['port']/8
    l = (n_placas * 2.5) / 4
    
    svg = f"""<svg width="500" height="300" viewBox="0 0 500 300" xmlns="http://www.w3.org/2000/svg">
        <rect x="20" y="20" width="{w}" height="{h}" fill="#f0f0f0" stroke="#0d1b2a" stroke-width="2"/>
        <circle cx="{20+(w-hd)/2}" cy="{20+(h-vd)/2}" r="{p}" fill="white" stroke="#0d1b2a"/>
        <circle cx="{20+(w+hd)/2}" cy="{20+(h-vd)/2}" r="{p}" fill="white" stroke="#0d1b2a"/>
        <circle cx="{20+(w-hd)/2}" cy="{20+(h+vd)/2}" r="{p}" fill="white" stroke="#0d1b2a"/>
        <circle cx="{20+(w+hd)/2}" cy="{20+(h+vd)/2}" r="{p}" fill="white" stroke="#0d1b2a"/>
        <text x="{20+w/2}" y="{h+40}" font-size="10" text-anchor="middle">Vista Frontal ({m['w']}x{m['h']}mm)</text>
        <rect x="{w+80}" y="20" width="10" height="{h}" fill="#0d1b2a"/>
        <rect x="{w+90}" y="30" width="{l}" height="{h-20}" fill="#cccccc" stroke="#666" stroke-width="0.5"/>
        <rect x="{w+90+l}" y="20" width="10" height="{h}" fill="#0d1b2a"/>
        <line x1="{w+80}" y1="40" x2="{w+100+l}" y2="40" stroke="#0d1b2a" stroke-width="2"/>
        <line x1="{w+80}" y1="{h}" x2="{w+100+l}" y2="{h}" stroke="#0d1b2a" stroke-width="2"/>
        <text x="{w+90+l/2}" y="{h+40}" font-size="10" text-anchor="middle">Vista Lateral (L: {n_placas*2.5:.0f}mm)</text>
    </svg>"""
    return svg

# 6. FUNCAO PDF
def gerar_pdf(modelo, tag, projeto, produto, servico, res):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], textColor=colors.HexColor('#003049'), fontSize=18, spaceAfter=20)
    header_style = ParagraphStyle('Header', parent=styles['Heading2'], textColor=colors.HexColor('#0d1b2a'), fontSize=12, spaceBefore=10)
    
    elements = []
    elements.append(Paragraph(f"AlfaVed - Datasheet Tecnico: {tag}", title_style))
    elements.append(Paragraph(f"Projeto: {projeto} | Data: {datetime.date.today().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    data = [
        ["Especificacao", "Valor"],
        ["Modelo Alfa Laval", modelo],
        ["Fluido Produto", produto],
        ["Fluido Servico", servico],
        ["Carga Termica", f"{res['carga']:.2f} kW"],
        ["Area de Troca", f"{res['area']:.2f} m2"],
        ["N de Placas", f"{res['placas']}"],
        ["U Global", f"{res['u']:.0f} W/m2K"],
        ["LMTD", f"{res['lmtd']:.2f} C"]
    ]
    
    t = Table(data, colWidths=[6*cm, 8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d1b2a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Responsaveis Tecnicos", header_style))
    for c in CONTATOS_ALFAVED:
        elements.append(Paragraph(f"<b>{c['nome']}</b> - {c['cargo']}", styles['Normal']))
        elements.append(Paragraph(f"Email: {c['email']} | Tel: {c['tel']}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# 7. INTERFACE PRINCIPAL
def main():
    st.markdown('<div class="main-header"><h1>AlfaVed Dimensionador PHE</h1><p>Solucoes em Troca Termica Alfa Laval</p></div>', unsafe_allow_html=True)
    
    tab_dim, tab_data, tab_rel = st.tabs(["Dimensionador", "Datasheet Tecnico", "Relatorio PDF"])
    
    with tab_dim:
        col_form, col_res = st.columns([1, 1.2])
        
        with col_form:
            st.markdown('<div class="glass-card"><h3>Dados do Projeto</h3></div>', unsafe_allow_html=True)
            tag = st.text_input("Tag do Equipamento", "TC-001")
            projeto = st.text_input("Nome do Projeto", "Projeto AlfaVed")
            
            st.markdown('<div class="glass-card"><h3>Fluidos</h3></div>', unsafe_allow_html=True)
            produto = st.selectbox("Fluido do Produto", list(BANCO_FLUIDOS.keys()))
            servico = st.selectbox("Fluido do Servico", list(BANCO_SERVICOS.keys()))
            
            st.markdown('<div class="glass-card"><h3>Temperaturas (C)</h3></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                t1e = st.number_input("Produto Entrada", value=80.0)
                t1s = st.number_input("Produto Saida", value=35.0)
            with c2:
                t2e = st.number_input("Servico Entrada", value=25.0)
                t2s = st.number_input("Servico Saida", value=45.0)
            
            st.markdown('<div class="glass-card"><h3>Vazao e Modelo</h3></div>', unsafe_allow_html=True)
            v_prod = st.number_input("Vazao Produto (kg/h)", value=5000.0, min_value=0.0)
            modelo = st.selectbox("Modelo Alfa Laval", list(BANCO_MODELOS.keys()))
            
            calcular = st.button("CALCULAR DIMENSIONAMENTO", type="primary", use_container_width=True)
        
        with col_res:
            if calcular:
                res = calc_dimensionamento(modelo, produto, servico, v_prod, t1e, t1s, t2e, t2s)
                st.session_state.res = res
                st.session_state.modelo = modelo
                st.session_state.tag = tag
                st.session_state.projeto = projeto
                st.session_state.produto = produto
                st.session_state.servico = servico
                
                st.markdown("### RESULTADOS")
                k1, k2, k3 = st.columns(3)
                with k1:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Carga Termica", f"{res['carga']:.2f} kW")
                    st.markdown('</div>', unsafe_allow_html=True)
                with k2:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Area Requerida", f"{res['area']:.2f} m2")
                    st.markdown('</div>', unsafe_allow_html=True)
                with k3:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Quantidade Placas", f"{res['placas']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.divider()
                st.markdown("#### Analise de Turbulencia")
                t1, t2 = st.columns(2)
                with t1:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown("**Lado Produto**")
                    st.metric("Reynolds", f"{res['re_p']:.0f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                with t2:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown("**Lado Servico**")
                    st.metric("Reynolds", f"{res['re_s']:.0f}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Preencha os dados e clique em CALCULAR DIMENSIONAMENTO")
    
    with tab_data:
        if 'res' in st.session_state:
            res = st.session_state.res
            mod = st.session_state.modelo
            st.markdown("### Datasheet Tecnico Visual")
            st.components.v1.html(generate_dimensional_svg(mod, res['placas']), height=320)
            
            st.markdown("#### Especificacoes do Modelo")
            m = BANCO_MODELOS[mod]
            specs = {
                "Categoria": m['cat'], "Pressao Max": f"{m['Pmax']} bar",
                "Temperatura Max": f"{m['Tmax']} C", "Conexao": m['conn'],
                "Largura": f"{m['w']} mm", "Altura": f"{m['h']} mm",
                "Peso Estimado": f"{m['weight']} kg"
            }
            for k, v in specs.items():
                st.markdown(f"**{k}:** {v}")
        else:
            st.warning("Execute o dimensionamento na aba anterior primeiro.")
    
    with tab_rel:
        if 'res' in st.session_state:
            res = st.session_state.res
            pdf = gerar_pdf(
                st.session_state.modelo, st.session_state.tag,
                st.session_state.projeto, st.session_state.produto,
                st.session_state.servico, res
            )
            st.download_button(
                label="Download Datasheet PDF",
                data=pdf,
                file_name=f"datasheet_{st.session_state.tag}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.success(f"Relatorio gerado para {st.session_state.tag}")
        else:
            st.warning("Execute o dimensionamento na aba 'Dimensionador' primeiro.")

if __name__ == '__main__':
    main()
