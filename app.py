import streamlit as st
import io
import math
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

st.set_page_config(page_title="AlfaVed - Dimensionamento Alfa Laval", page_icon="▲", layout="wide")

CSS_STYLE = """
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
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

BANCO_MODELOS = {
    "M3": {"area": 0.03, "Pmax": 16, "Tmax": 180, "dh": 0.003, "conn": "1.25\"", "cat": "Gaxetado", "w": 200, "h": 480, "vd": 350, "hd": 120, "port": 32, "frame": 20, "weight": 45},
    "M6-B": {"area": 0.15, "Pmax": 10, "Tmax": 180, "dh": 0.004, "conn": "2\"", "cat": "Gaxetado", "w": 320, "h": 920, "vd": 700, "hd": 200, "port": 50, "frame": 30, "weight": 120},
    "TS6M": {"area": 0.18, "Pmax": 25, "Tmax": 180, "dh": 0.004, "conn": "2\"", "cat": "Gaxetado", "w": 320, "h": 950, "vd": 720, "hd": 200, "port": 50, "frame": 40, "weight": 180},
    "M10-B": {"area": 0.24, "Pmax": 10, "Tmax": 180, "dh": 0.005, "conn": "4\"", "cat": "Gaxetado", "w": 470, "h": 1080, "vd": 820, "hd": 300, "port": 100, "frame": 40, "weight": 350},
    "TS20M": {"area": 0.65, "Pmax": 21, "Tmax": 180, "dh": 0.006, "conn": "6\"", "cat": "Gaxetado", "w": 650, "h": 1650, "vd": 1250, "hd": 350, "port": 150, "frame": 50, "weight": 780},
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
    "Agua Gelada": {"cp": 4.19, "visc": 0.0015, "dens": 1000, "cond": 0.58, "h_vap": None},
    "Agua Quente": {"cp": 4.18, "visc": 0.0004, "dens": 970, "cond": 0.65, "h_vap": None},
    "Vapor Saturado (3 bar)": {"cp": 2.01, "visc": 0.000015, "dens": 1.2, "cond": 0.025, "h_vap": 2163, "T_sat": 133.5},
    "Vapor Saturado (6 bar)": {"cp": 2.01, "visc": 0.000015, "dens": 3.1, "cond": 0.025, "h_vap": 2086, "T_sat": 158.8},
    "Vapor Saturado (10 bar)": {"cp": 2.01, "visc": 0.000015, "dens": 5.1, "cond": 0.025, "h_vap": 2015, "T_sat": 179.9},
    "Glicol 30%": {"cp": 3.75, "visc": 0.0032, "dens": 1045, "cond": 0.48, "h_vap": None},
    "Oleo Termico": {"cp": 2.10, "visc": 0.012, "dens": 860, "cond": 0.13, "h_vap": None}
}


def validate_temperatures(t_in, t_out, fluid_name):
    """
    Valida se as temperaturas de entrada e saída são diferentes.
    
    Args:
        t_in: Temperatura de entrada (°C)
        t_out: Temperatura de saída (°C)
        fluid_name: Nome do fluido (para mensagem de erro)
        
    Returns:
        tuple: (is_valid, message)
    """
    if abs(t_in - t_out) < 0.1:
        return False, f"Erro: {fluid_name} - Temperatura de entrada e saída devem diferir em pelo menos 0.1°C"
    return True, ""


def calc_lmtd(t1e, t1s, t2e, t2s):
    """
    Calcula a Diferença Média Logarítmica de Temperatura (LMTD).
    Considera configuração em contracorrente.
    
    Args:
        t1e: Temperatura entrada lado 1 (°C)
        t1s: Temperatura saída lado 1 (°C)
        t2e: Temperatura entrada lado 2 (°C)
        t2s: Temperatura saída lado 2 (°C)
        
    Returns:
        float: LMTD em °C
    """
    dt1 = abs(t1e - t2s)  # Diferença entre entrada produto e saída serviço
    dt2 = abs(t1s - t2e)  # Diferença entre saída produto e entrada serviço
    
    # Evitar divisão por zero
    if abs(dt1 - dt2) < 0.001:
        return max(dt1, 0.001)
    
    try:
        if dt1 > 0 and dt2 > 0:
            return (dt1 - dt2) / math.log(dt1 / dt2)
        else:
            return 0.001
    except (ValueError, ZeroDivisionError):
        return 0.001


def calc_reynolds(vazao_kgh, visc, dens, dh, w_placa):
    """
    Calcula o número de Reynolds.
    
    Args:
        vazao_kgh: Vazão em kg/h
        visc: Viscosidade dinâmica (Pa·s)
        dens: Densidade (kg/m³)
        dh: Diâmetro hidráulico (m)
        w_placa: Largura da placa (m)
        
    Returns:
        float: Número de Reynolds
    """
    if visc <= 0 or dens <= 0 or w_placa <= 0:
        return 0
    
    try:
        v_ms = (vazao_kgh / 3600) / (dens * w_placa * 0.003)
        re = (dens * v_ms * dh) / visc
        return re if not (math.isnan(re) or math.isinf(re)) else 0
    except (ZeroDivisionError, ValueError):
        return 0


def calc_nusselt(re, pr):
    """
    Calcula o número de Nusselt usando correlação de Gnielinski.
    
    Args:
        re: Número de Reynolds
        pr: Número de Prandtl
        
    Returns:
        float: Número de Nusselt
    """
    if re <= 0 or pr <= 0:
        return 1.0
    
    try:
        nu = 0.3 * (re ** 0.67) * (pr ** 0.33)
        return nu if not (math.isnan(nu) or math.isinf(nu)) else 1.0
    except (ValueError, OverflowError):
        return 1.0


def calc_vapor_kgh(carga_kw, h_vap_kjkg):
    """
    Calcula a vazão de vapor necessária.
    
    Args:
        carga_kw: Carga térmica em kW
        h_vap_kjkg: Entalpia de vaporização em kJ/kg
        
    Returns:
        float or None: Vazão de vapor em kg/h, ou None se não aplicável
    """
    if h_vap_kjkg and h_vap_kjkg > 0:
        return (carga_kw * 3600) / h_vap_kjkg
    return None


def calc_dimensionamento(mod_key, prod_key, serv_key, v_prod, t1e, t1s, t2e, t2s):
    """
    Realiza o dimensionamento completo do trocador de calor.
    
    Args:
        mod_key: Chave do modelo
        prod_key: Chave do fluido produto
        serv_key: Chave do fluido serviço
        v_prod: Vazão do produto em kg/h
        t1e: Temperatura entrada produto (°C)
        t1s: Temperatura saída produto (°C)
        t2e: Temperatura entrada serviço (°C)
        t2s: Temperatura saída serviço (°C)
        
    Returns:
        dict: Resultados do dimensionamento ou erro
    """
    # Validações
    is_valid, msg = validate_temperatures(t1e, t1s, "Produto")
    if not is_valid:
        raise ValueError(msg)
    
    is_valid, msg = validate_temperatures(t2e, t2s, "Serviço")
    if not is_valid:
        raise ValueError(msg)
    
    if v_prod <= 0:
        raise ValueError("Vazão do produto deve ser maior que zero")
    
    m = BANCO_MODELOS[mod_key]
    p = BANCO_FLUIDOS[prod_key]
    s = BANCO_SERVICOS[serv_key]
    
    # Cálculo da carga térmica
    carga = (v_prod * p['cp'] * abs(t1e - t1s)) / 3600
    
    # Cálculo da vazão de serviço
    dt_serv = abs(t2e - t2s)
    v_serv = 0
    if dt_serv > 0.001:
        v_serv = (carga * 3600) / (s['cp'] * dt_serv)
    else:
        raise ValueError("Diferença de temperatura do serviço muito pequena")
    
    # LMTD
    lmtd = calc_lmtd(t1e, t1s, t2e, t2s)
    
    # Reynolds
    re_p = calc_reynolds(v_prod, p['visc'], p['dens'], m['dh'], m['w']/1000)
    re_s = calc_reynolds(v_serv, s['visc'], s['dens'], m['dh'], m['w']/1000)
    
    # Prandtl
    pr_p = (p['cp'] * 1000 * p['visc']) / p['cond'] if p['cond'] > 0 else 1
    pr_s = (s['cp'] * 1000 * s['visc']) / s['cond'] if s['cond'] > 0 else 1
    
    # Coeficientes de convecção
    h_p = (calc_nusselt(re_p, pr_p) * p['cond']) / m['dh']
    h_s = (calc_nusselt(re_s, pr_s) * s['cond']) / m['dh']
    
    # U global (resistências: convecção produto, convecção serviço, condução placa, resistência de fouling)
    u_global = 1 / (1/h_p + 1/h_s + 0.0005/17 + 0.0001)
    
    # Área requerida
    if (u_global * lmtd) > 0:
        area_req = (carga * 1000) / (u_global * lmtd)
    else:
        raise ValueError("Parâmetros de cálculo resultaram em área inválida")
    
    # Número de placas
    n_placas = math.ceil(area_req / m['area']) + 2
    if n_placas % 2 != 0:
        n_placas += 1
    
    # Vazão de vapor (se aplicável)
    vapor_kgh = None
    if s.get('h_vap'):
        vapor_kgh = calc_vapor_kgh(carga, s['h_vap'])
    
    return {
        "carga": carga,
        "v_serv": v_serv,
        "vapor_kgh": vapor_kgh,
        "lmtd": lmtd,
        "u": u_global,
        "area": area_req,
        "placas": n_placas,
        "re_p": re_p,
        "re_s": re_s
    }


def generate_dimensional_svg(mod_key, n_placas):
    """
    Gera um SVG com visualização dimensional do trocador.
    
    Args:
        mod_key: Chave do modelo
        n_placas: Número de placas
        
    Returns:
        str: SVG como string
    """
    m = BANCO_MODELOS[mod_key]
    w = m['w'] / 4
    h = m['h'] / 4
    vd = m['vd'] / 4
    hd = m['hd'] / 4
    p = m['port'] / 8
    l = (n_placas * 2.5) / 4
    
    svg = f"""
    <svg width="500" height="350" viewBox="0 0 500 350" xmlns="http://www.w3.org/2000/svg">
        <rect x="20" y="40" width="{w}" height="{h}" fill="#f8f9fa" stroke="#0d1b2a" stroke-width="2"/>
        <circle cx="{20+(w-hd)/2}" cy="{40+(h-vd)/2}" r="{p}" fill="white" stroke="#0d1b2a"/>
        <circle cx="{20+(w+hd)/2}" cy="{40+(h-vd)/2}" r="{p}" fill="white" stroke="#0d1b2a"/>
        <circle cx="{20+(w-hd)/2}" cy="{40+(h+vd)/2}" r="{p}" fill="white" stroke="#0d1b2a"/>
        <circle cx="{20+(w+hd)/2}" cy="{40+(h+vd)/2}" r="{p}" fill="white" stroke="#0d1b2a"/>
        <text x="{20+w/2}" y="30" font-size="12" text-anchor="middle" font-weight="bold">VISTA FRONTAL</text>
        <rect x="{w+100}" y="40" width="10" height="{h}" fill="#0d1b2a"/>
        <rect x="{w+110}" y="50" width="{l}" height="{h-20}" fill="#dee2e6" stroke="#adb5bd"/>
        <rect x="{w+110+l}" y="40" width="10" height="{h}" fill="#0d1b2a"/>
        <text x="{w+105+l/2}" y="30" font-size="12" text-anchor="middle" font-weight="bold">VISTA LATERAL</text>
        <text x="20" y="{h+70}" font-size="10">Dimensoes: {m['w']} x {m['h']} mm</text>
        <text x="20" y="{h+85}" font-size="10">Comprimento do Pacote: {n_placas*2.5:.1f} mm</text>
    </svg>
    """
    return svg


def gerar_pdf(modelo, tag, projeto, produto, servico, res):
    """
    Gera um PDF com os resultados do dimensionamento.
    
    Args:
        modelo: Modelo selecionado
        tag: Tag do equipamento
        projeto: Número do projeto
        produto: Fluido produto
        servico: Fluido serviço
        res: Dicionário com resultados
        
    Returns:
        bytes: Conteúdo do PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    elements = []
    elements.append(Paragraph(f"AlfaVed - Datasheet Tecnico: {tag}", styles['Title']))
    elements.append(Paragraph(f"Projeto: {projeto} | Data: {datetime.date.today().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    data = [
        ["Parametro", "Valor"],
        ["Modelo", modelo],
        ["Fluido Produto", produto],
        ["Fluido Servico", servico],
        ["Carga Termica", f"{res['carga']:.2f} kW"],
        ["Vazao Servico", f"{res['v_serv']:.0f} kg/h"],
    ]
    
    if res.get('vapor_kgh'):
        data.append(["Vazao Vapor", f"{res['vapor_kgh']:.1f} kg/h"])
    
    data.extend([
        ["Area de Troca", f"{res['area']:.2f} m2"],
        ["N de Placas", f"{res['placas']}"],
        ["U Global", f"{res['u']:.0f} W/m2K"],
        ["LMTD", f"{res['lmtd']:.2f} C"]
    ])
    
    t = Table(data, colWidths=[7*cm, 7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d1b2a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("Contatos Tecnicos", styles['Heading2']))
    elements.append(Paragraph("Vitor Soares - Engenharia de Aplicacao | engenharia@alfaved.com.br", styles['Normal']))
    elements.append(Paragraph("Jhonatan Dias Dejato - Diretor de Engenharia | jhonatan@alfaved.com.br", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def main():
    st.markdown("""
    <div class="main-header">
        <h1>AlfaVed Engenharia Termica</h1>
        <h3>Dimensionador Inteligente de Trocadores de Calor</h3>
        <p>Banco Alfa Laval | TS6M | TS20M | Semi-Soldadas | WideGap</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_dim, tab_ds = st.tabs(["Dimensionador", "Datasheet Tecnico"])
    
    with tab_dim:
        input_col, result_col = st.columns([1, 1.2], gap='large')
        
        with input_col:
            st.markdown("### DADOS DE PROJETO")
            with st.form('form_dimensionamento', clear_on_submit=False):
                st.markdown("#### Informacoes do Projeto")
                tag = st.text_input('Tag do Equipamento', 'TC-101', key='tag_input')
                projeto = st.text_input('Numero do Projeto', 'PRJ-ALFAVED-2026', key='proj_input')
                st.divider()
                
                st.markdown("#### Selecao do Modelo")
                filtro_cat = st.selectbox('Filtrar por Categoria', ['Todos', 'Gaxetados', 'Semi-Soldados', 'WideGap'], key='filtro_cat')
                if filtro_cat == 'Gaxetados':
                    modelos_filtrados = [k for k, v in BANCO_MODELOS.items() if v['cat'] == 'Gaxetado']
                elif filtro_cat == 'Semi-Soldados':
                    modelos_filtrados = [k for k, v in BANCO_MODELOS.items() if v['cat'] == 'Semi-Soldado']
                elif filtro_cat == 'WideGap':
                    modelos_filtrados = [k for k, v in BANCO_MODELOS.items() if v['cat'] == 'WideGap']
                else:
                    modelos_filtrados = list(BANCO_MODELOS.keys())
                
                modelo = st.selectbox('Modelo Alfa Laval', modelos_filtrados, key='modelo_input')
                dados_mod = BANCO_MODELOS[modelo]
                st.markdown(f"**Categoria:** {dados_mod['cat']} | **P Max:** {dados_mod['Pmax']} bar | **T Max:** {dados_mod['Tmax']}C | **Conexao:** {dados_mod['conn']}")
                st.divider()
                
                st.markdown("#### Lado do Produto")
                col_prod1, col_prod2 = st.columns(2)
                with col_prod1:
                    produto = st.selectbox('Fluido do Produto', list(BANCO_FLUIDOS.keys()), key='prod_input')
                with col_prod2:
                    vazao_prod = st.number_input('Vazao (kg/h)', value=5000.0, min_value=1.0, key='vazao_prod')
                
                col_temp_prod1, col_temp_prod2 = st.columns(2)
                with col_temp_prod1:
                    t_in_prod = st.number_input('Temp. Entrada (C)', value=90.0, key='t_in_prod_input')
                with col_temp_prod2:
                    t_out_prod = st.number_input('Temp. Saida (C)', value=8.0, key='t_out_prod_input')
                st.divider()
                
                st.markdown("#### Lado do Servico")
                servico = st.selectbox('Fluido de Servico', list(BANCO_SERVICOS.keys()), key='serv_input')
                col_temp_serv1, col_temp_serv2 = st.columns(2)
                with col_temp_serv1:
                    t_in_serv = st.number_input('Temp. Entrada Servico (C)', value=0.0, key='t_in_serv_input')
                with col_temp_serv2:
                    t_out_serv = st.number_input('Temp. Saida Servico (C)', value=12.0, key='t_out_serv_input')
                st.divider()
                
                submitted = st.form_submit_button('CALCULAR DIMENSIONAMENTO', use_container_width=True, type='primary')
            
            if submitted:
                try:
                    resultados = calc_dimensionamento(modelo, produto, servico, vazao_prod, t_in_prod, t_out_prod, t_in_serv, t_out_serv)
                    pdf_bytes = gerar_pdf(modelo, tag, projeto, produto, servico, resultados)
                    st.session_state.resultados = resultados
                    st.session_state.pdf_bytes = pdf_bytes
                    st.session_state.modelo_res = modelo
                    st.session_state.tag_res = tag
                    st.session_state.projeto_res = projeto
                    st.session_state.produto_res = produto
                    st.session_state.servico_res = servico
                    st.success('Calculo realizado com sucesso!')
                    st.rerun()
                except ValueError as e:
                    st.error(f'❌ Erro no cálculo: {str(e)}')
                except Exception as e:
                    st.error(f'❌ Erro inesperado: {str(e)}')
        
        with result_col:
            if 'resultados' in st.session_state:
                res = st.session_state.resultados
                st.markdown("### RESULTADOS DO DIMENSIONAMENTO")
                
                kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
                with kpi_col1:
                    st.metric('Carga Termica', f"{res['carga']:.2f} kW")
                with kpi_col2:
                    st.metric('Area Requerida', f"{res['area']:.2f} m2")
                with kpi_col3:
                    st.metric('Quantidade Placas', f"{res['placas']}")
                
                st.divider()
                st.markdown("#### Analise de Turbulencia")
                turb_col1, turb_col2 = st.columns(2)
                with turb_col1:
                    st.markdown('**Lado Produto**')
                    st.metric('Reynolds', f"{res['re_p']:.0f}")
                with turb_col2:
                    st.markdown('**Lado Servico**')
                    st.metric('Reynolds', f"{res['re_s']:.0f}")
                
                st.divider()
                st.markdown("#### Dimensoes do Trocador")
                m = BANCO_MODELOS[st.session_state.modelo_res]
                dim_col1, dim_col2, dim_col3 = st.columns(3)
                with dim_col1:
                    st.metric('Largura', f"{m['w']} mm")
                with dim_col2:
                    st.metric('Altura', f"{m['h']} mm")
                with dim_col3:
                    st.metric('Peso Est.', f"{m['weight']} kg")
                
                st.markdown("#### Vista Dimensional (Miniatura)")
                svg_mini = generate_dimensional_svg(st.session_state.modelo_res, res['placas'])
                st.markdown(svg_mini, unsafe_allow_html=True)
                
                st.divider()
                st.markdown("#### Download")
                st.download_button(
                    label='Download PDF',
                    data=st.session_state.pdf_bytes,
                    file_name=f"datasheet_{st.session_state.tag_res}.pdf",
                    mime='application/pdf',
                    use_container_width=True
                )
                
                if res.get('vapor_kgh'):
                    st.info(f"Vazao equivalente em vapor: **{res['vapor_kgh']:.1f} kg/h**")
            else:
                st.info('Preencha os dados e clique em CALCULAR DIMENSIONAMENTO')
    
    with tab_ds:
        if 'resultados' in st.session_state:
            res = st.session_state.resultados
            modelo = st.session_state.modelo_res
            m = BANCO_MODELOS[modelo]
            
            st.markdown("## Datasheet Tecnico Completo")
            st.markdown(f"**Tag:** {st.session_state.tag_res} | **Projeto:** {st.session_state.projeto_res}")
            st.markdown(f"**Modelo:** {modelo} | **Categoria:** {m['cat']}")
            
            st.markdown("### Desenho Dimensional")
            svg_full = generate_dimensional_svg(modelo, res['placas'])
            st.markdown(svg_full, unsafe_allow_html=True)
            
            st.markdown("### Especificacoes Mecanicas")
            spec_data = {
                "Largura Placa": f"{m['w']} mm",
                "Altura Placa": f"{m['h']} mm",
                "Distancia Vert. Portas": f"{m['vd']} mm",
                "Distancia Horiz. Portas": f"{m['hd']} mm",
                "Diametro Conexao": f"{m['port']} mm ({m['conn']})",
                "Espessura Frame": f"{m['frame']} mm",
                "Peso Estimado": f"{m['weight']} kg",
                "Pressao Maxima": f"{m['Pmax']} bar",
                "Temperatura Maxima": f"{m['Tmax']} C",
                "Abertura Canal": f"{m['dh']*1000:.1f} mm"
            }
            for k, v in spec_data.items():
                st.write(f"**{k}:** {v}")
            
            st.markdown("### Resultados Termicos")
            res_data = {
                "Carga Termica": f"{res['carga']:.2f} kW",
                "Vazao Servico": f"{res['v_serv']:.0f} kg/h",
                "LMTD": f"{res['lmtd']:.2f} C",
                "U Global": f"{res['u']:.0f} W/m2K",
                "Area Requerida": f"{res['area']:.2f} m2",
                "N de Placas": f"{res['placas']}",
                "Reynolds Produto": f"{res['re_p']:.0f}",
                "Reynolds Servico": f"{res['re_s']:.0f}"
            }
            if res.get('vapor_kgh'):
                res_data["Vazao Vapor"] = f"{res['vapor_kgh']:.1f} kg/h"
            for k, v in res_data.items():
                st.write(f"**{k}:** {v}")
            
            st.markdown("### Responsaveis Tecnicos")
            st.write("**Vitor Soares** - Engenharia de Aplicacao | engenharia@alfaved.com.br | (18) 99669-7330")
            st.write("**Jhonatan Dias Dejato** - Diretor de Engenharia | jhonatan@alfaved.com.br | (18) 99628-8714")
        else:
            st.warning("Execute o dimensionamento na aba 'Dimensionador' primeiro.")


if __name__ == '__main__':
    main()
