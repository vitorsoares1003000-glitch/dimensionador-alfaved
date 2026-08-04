import io
import math
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

st.set_page_config(page_title="AlfaVed Engenharia - Dimensionador", page_icon="▲", layout="wide")

# ============================================================================
# BANCO DE DADOS - MODELOS ALFA LAVAL
# ============================================================================

BANCO_MODELOS = {
    "Alfa Laval M3 (Gaxetado)": {"tipo": "Gaxetado", "linha": "BaseLine", "area_placa": 0.030, "U_base": 3800, "pressao_max": 16, "temp_max": 180, "dh": 0.003, "conexao": 'DN32 (1.25")', "material": "AISI 316 / Ti"},
    "Alfa Laval M6-B (Gaxetado)": {"tipo": "Gaxetado", "linha": "BaseLine", "area_placa": 0.150, "U_base": 4200, "pressao_max": 10, "temp_max": 180, "dh": 0.005, "conexao": 'DN50 (2")', "material": "AISI 304 / 316 / Ti"},
    "Alfa Laval TS6M (Gaxetado)": {"tipo": "Gaxetado", "linha": "M-line", "area_placa": 0.260, "U_base": 4600, "pressao_max": 25, "temp_max": 180, "dh": 0.006, "conexao": 'DN65 (2.5")', "material": "AISI 316 / Ti"},
    "Alfa Laval M10-B (Gaxetado)": {"tipo": "Gaxetado", "linha": "BaseLine", "area_placa": 0.240, "U_base": 4500, "pressao_max": 10, "temp_max": 180, "dh": 0.006, "conexao": 'DN100 (4")', "material": "AISI 304 / 316 / Ti"},
    "Alfa Laval TS20M (Gaxetado)": {"tipo": "Gaxetado", "linha": "M-line", "area_placa": 0.950, "U_base": 4950, "pressao_max": 25, "temp_max": 180, "dh": 0.009, "conexao": 'DN200 (8")', "material": "AISI 316 / 254 SMO / Ti"},
    "Alfa Laval T20-B (Gaxetado)": {"tipo": "Gaxetado", "linha": "BaseLine", "area_placa": 0.850, "U_base": 4800, "pressao_max": 10, "temp_max": 180, "dh": 0.009, "conexao": 'DN200 (8")', "material": "AISI 304 / 316 / Ti"},
    "Alfa Laval MA30-S WideGap (Gaxetado)": {"tipo": "Gaxetado", "linha": "WideGap", "area_placa": 1.380, "U_base": 3800, "pressao_max": 25, "temp_max": 180, "dh": 0.012, "conexao": 'DN300 (12")', "material": "AISI 316 / 254 SMO / Ti"},
    "Alfa Laval M10-BW (Semi-Soldado)": {"tipo": "Semi-Soldado", "linha": "Semi-Welded", "area_placa": 0.240, "U_base": 4600, "pressao_max": 55, "temp_max": 250, "dh": 0.005, "conexao": 'DN100 (4")', "material": "316/316L / Ti"},
    "Alfa Laval MK15-BW (Semi-Soldado)": {"tipo": "Semi-Soldado", "linha": "Semi-Welded", "area_placa": 0.420, "U_base": 4650, "pressao_max": 41, "temp_max": 200, "dh": 0.006, "conexao": 'DN150 (6")', "material": "316/316L / Ti"},
}

BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "viscosidade": 0.89, "densidade": 1000},
    "Leite Integral": {"cp": 3.89, "viscosidade": 2.1, "densidade": 1030},
    "Suco de Laranja": {"cp": 3.75, "viscosidade": 3.5, "densidade": 1040},
    "Oleo Vegetal": {"cp": 1.97, "viscosidade": 50.0, "densidade": 920},
    "Cerveja": {"cp": 4.10, "viscosidade": 1.5, "densidade": 1010},
}

BANCO_SERVICOS = {
    "Agua Fria": {"cp": 4.18, "viscosidade": 0.89, "densidade": 1000},
    "Agua Quente": {"cp": 4.18, "viscosidade": 0.35, "densidade": 960},
    "Vapor Saturado": {"cp": 2.0, "viscosidade": 0.015, "densidade": 0.6, "is_vapor": True},
    "Glicol 30%": {"cp": 3.70, "viscosidade": 3.5, "densidade": 1040},
}

# ============================================================================
# CONFIGURACAO DOS ANGULOS DE PLACA
# ============================================================================

CONFIG_ANGULOS = {
    "H (45°)": {"multiplicador_u": 1.4, "descricao": "Alta turbulencia, alta transferencia, maior queda de pressao"},
    "L (60°)": {"multiplicador_u": 1.0, "descricao": "Menor queda de pressao, eficiencia balanceada"},
    "Mista (HL = 52.5°)": {"multiplicador_u": 1.2, "descricao": "Compromisso entre transferencia e queda de pressao"}
}

# ============================================================================
# ESTILOS PDF
# ============================================================================

styles_doc = getSampleStyleSheet()
st_tit = ParagraphStyle('T1', parent=styles_doc['Heading1'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor('#0d1b2a'))
st_sub = ParagraphStyle('T2', parent=styles_doc['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#d90429'), spaceAfter=15)
st_h2 = ParagraphStyle('T3', parent=styles_doc['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#003049'), spaceBefore=10, spaceAfter=5)
st_tc = ParagraphStyle('T6', parent=styles_doc['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#333333'))
st_th = ParagraphStyle('T5', parent=styles_doc['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.setFont('Helvetica', 9)
            self.setFillColor(colors.HexColor('#666666'))
            self.drawString(54, 25, 'AlfaVed Solucoes Industriais - Engenharia Termica')
            largura_real = letter[0]
            self.drawRightString(largura_real - 54, 25, f'Pagina {self._pageNumber} de {num_pages}')
            super().showPage()
        super().save()

# ============================================================================
# FUNCOES DE CALCULO
# ============================================================================

def calculate_reynolds(vazao_kg_h, viscosidade, densidade, dh):
    if vazao_kg_h <= 0 or viscosidade <= 0 or densidade <= 0:
        return 0
    vazao_m3_s = (vazao_kg_h / 3600.0) / densidade
    area_canal = 0.0001
    u = vazao_m3_s / area_canal
    viscosidade_pa_s = viscosidade * 0.001
    return (densidade * u * dh) / viscosidade_pa_s

def get_calor_latente(temp_c):
    if temp_c >= 120:
        return 2200.0
    if temp_c >= 100:
        return 2257.0
    if temp_c >= 80:
        return 2308.0
    return 2358.0

def calculate_lmtd(dt1, dt2):
    dt1, dt2 = abs(dt1), abs(dt2)
    if dt1 < 1e-6 or dt2 < 1e-6:
        return max(dt1, dt2, 1.0)
    if abs(dt1 - dt2) < 1e-6:
        return dt1
    return (dt1 - dt2) / math.log(dt1 / dt2)

def dimensionar(produto, servico, modelo, vazao_p, t_in_p, t_out_p, t_in_s, t_out_s, angulo_manual):
    d_p = BANCO_FLUIDOS[produto]
    d_s = BANCO_SERVICOS[servico]
    d_m = BANCO_MODELOS[modelo]

    # Carga Termica
    carga_kw = (vazao_p * d_p['cp'] * abs(t_in_p - t_out_p)) / 3600.0

    # Vazao Servico
    is_vapor = d_s.get('is_vapor', False)
    if is_vapor:
        hfg = get_calor_latente(t_in_s)
        vazao_s = (carga_kw * 3600.0) / hfg
        t_out_s_calc = t_in_s
    else:
        dt_s = abs(t_in_s - t_out_s)
        vazao_s = (carga_kw * 3600.0) / (d_s['cp'] * dt_s) if dt_s > 0 else 0
        t_out_s_calc = t_out_s

    # Reynolds
    re_p = calculate_reynolds(vazao_p, d_p['viscosidade'], d_p['densidade'], d_m['dh'])
    re_s = calculate_reynolds(vazao_s, d_s['viscosidade'], d_s['densidade'], d_m['dh'])

    # Angulo e Multiplicador
    if angulo_manual == "Automatico (Recomendado)":
        re_min = min(re_p, re_s)
        if re_min < 500:
            angulo, mult = "H (45°)", 1.4
        elif re_min > 2000:
            angulo, mult = "L (60°)", 1.0
        else:
            angulo, mult = "H (45°)", 1.4
    elif angulo_manual == "H (45°)":
        angulo, mult = "H (45°)", 1.4
    elif angulo_manual == "L (60°)":
        angulo, mult = "L (60°)", 1.0
    else:
        angulo, mult = "Mista (HL = 52.5°)", 1.2

    # Area e Placas
    fator_visc = 1.0 / math.sqrt(d_p['viscosidade']) if d_p['viscosidade'] > 1 else 1.0
    u_final = d_m['U_base'] * mult * fator_visc
    lmtd = calculate_lmtd(t_in_p - t_out_s_calc, t_out_p - t_in_s)
    area_req = (carga_kw * 1000.0) / (u_final * lmtd) if lmtd > 0 else 0
    num_placas = math.ceil(area_req / d_m['area_placa']) + 2
    if num_placas % 2 != 0:
        num_placas += 1

    return {
        "carga_kw": carga_kw,
        "vazao_s": vazao_s,
        "re_p": re_p,
        "re_s": re_s,
        "lmtd": lmtd,
        "area_req": area_req,
        "num_placas": num_placas,
        "u_final": u_final,
        "angulo": angulo,
        "mult_u": mult,
        "is_vapor": is_vapor,
        "t_out_s_calc": t_out_s_calc,
        "hfg": hfg if is_vapor else 0
    }

def build_pdf(res, modelo, tag, projeto, produto, servico, t_in_p, t_out_p, t_in_s, t_out_s, vazao_p, angulo_sel):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = [
        Paragraph('AlfaVed Solucoes Industriais', st_tit),
        Paragraph('DATASHEET TECNICO - DIMENSIONAMENTO DE TROCADOR DE CALOR', st_sub),
        Spacer(1, 10)
    ]

    story.append(Paragraph('1. Informacoes Gerais do Projeto', st_h2))
    t1 = Table([
        [Paragraph('Item', st_th), Paragraph('Especificacao', st_th)],
        ['Modelo', modelo],
        ['Tag', tag],
        ['Projeto', projeto],
        ['Linha', BANCO_MODELOS[modelo]['linha']],
        ['Material Placa', BANCO_MODELOS[modelo]['material']],
        ['Conexao', BANCO_MODELOS[modelo]['conexao']],
    ])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1b2a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t1)

    story.append(Paragraph('2. Dados de Processo', st_h2))
    data_proc = [
        [Paragraph('Parametro', st_th), Paragraph('Lado Produto', st_th), Paragraph('Lado Servico', st_th)],
        ['Fluido', produto, servico],
        ['Vazao (kg/h)', f'{vazao_p:.1f}', f'{res["vazao_s"]:.1f}'],
        ['Temp. Entrada (C)', f'{t_in_p:.1f}', f'{t_in_s:.1f}'],
        ['Temp. Saida (C)', f'{t_out_p:.1f}', f'{res["t_out_s_calc"]:.1f}'],
        ['Reynolds', f'{res["re_p"]:.0f}', f'{res["re_s"]:.0f}'],
    ]
    t2 = Table(data_proc)
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1b2a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t2)

    story.append(Paragraph('3. Resultados do Dimensionamento', st_h2))
    res_data = [
        [Paragraph('Grandeza', st_th), Paragraph('Valor', st_th)],
        ['Carga Termica', f'{res["carga_kw"]:.2f} kW'],
        ['LMTD', f'{res["lmtd"]:.2f} C'],
        ['Coeficiente U Final', f'{res["u_final"]:.0f} W/m2K'],
        ['Area Requerida', f'{res["area_req"]:.2f} m2'],
        ['Total de Placas', f'{res["num_placas"]}'],
        ['Angulo da Placa', res['angulo']],
        ['Multiplicador U', f'{res["mult_u"]:.2f}x'],
    ]
    if res['is_vapor']:
        res_data.append(['Consumo de Vapor', f'{res["vazao_s"]:.2f} kg/h'])
        res_data.append(['Calor Latente (hfg)', f'{res["hfg"]:.1f} kJ/kg'])

    t3 = Table(res_data)
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1b2a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t3)

    story.append(Paragraph('4. Responsaveis Tecnicos', st_h2))
    story.append(Paragraph('Vitor Soares - Responsavel pelo Projeto', st_tc))
    story.append(Paragraph('E-mail: engenharia@alfaved.com.br | Tel: (18) 99669-7330', st_tc))
    story.append(Spacer(1, 5))
    story.append(Paragraph('Jhonatan Dias Dejato - Diretor de Engenharia', st_tc))
    story.append(Paragraph('E-mail: jhonatan@alfaved.com.br | Tel: (18) 99628-8714', st_tc))

    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def main():
    st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #0d1b2a 0%, #003049 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
    .metric-box { background: linear-gradient(135deg, #003049 0%, #1f5a6f 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
    .section-card { background-color: #f8f9fa; border-left: 4px solid #0d1b2a; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .vapor-box { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; }
    .contact-card { background: #f0f4f8; border-left: 4px solid #003049; padding: 15px; border-radius: 5px; margin: 5px 0; }
    .angulo-badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: bold; background: #e3f2fd; color: #1565c0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1>AlfaVed Engenharia Termica</h1>
        <h3>Dimensionador Inteligente de Trocadores de Calor</h3>
        <p>TS6M / TS20M | Vapor kg/h | Angulo Manual H/L/Mista</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.markdown('### DADOS DE ENTRADA')

        with st.expander('Identificacao do Projeto', expanded=True):
            tag = st.text_input('Tag do Equipamento', 'TC-101', key='tag')
            projeto = st.text_input('Nome do Projeto', 'PRJ-ALFAVED-2026', key='projeto')

        with st.expander('Selecao do Modelo', expanded=True):
            modelo = st.selectbox('Modelo Alfa Laval', list(BANCO_MODELOS.keys()), key='modelo')
            d_mod = BANCO_MODELOS[modelo]
            st.caption(f"Linha: {d_mod['linha']} | Pmax: {d_mod['pressao_max']} bar | Tmax: {d_mod['temp_max']} C")

            # NOVO: SELECAO MANUAL DO ANGULO DA PLACA
            angulo_sel = st.selectbox(
                'Angulo da Placa',
                ['Automatico (Recomendado)', 'H (45°)', 'L (60°)', 'Mista (HL = 52.5°)'],
                key='angulo',
                help='Automatico: baseado no numero de Reynolds. H=alta turbulencia, L=baixa queda de pressao, Mista=compromisso.'
            )
            if angulo_sel != 'Automatico (Recomendado)':
                cfg = CONFIG_ANGULOS[angulo_sel]
                st.info(f"{cfg['descricao']} | Multiplicador U: {cfg['multiplicador_u']}x")

        with st.expander('Lado do Produto', expanded=True):
            produto = st.selectbox('Fluido do Produto', list(BANCO_FLUIDOS.keys()), key='produto')
            vazao_p = st.number_input('Vazao (kg/h)', value=5000.0, min_value=1.0, key='vazao_p')
            c1, c2 = st.columns(2)
            with c1:
                t_in_p = st.number_input('Temp. Entrada (C)', value=90.0, key='t_in_p')
            with c2:
                t_out_p = st.number_input('Temp. Saida (C)', value=8.0, key='t_out_p')

        with st.expander('Lado do Servico', expanded=True):
            servico = st.selectbox('Fluido de Servico', list(BANCO_SERVICOS.keys()), key='servico')
            c1, c2 = st.columns(2)
            with c1:
                t_in_s = st.number_input('Temp. Entrada Serv. (C)', value=0.0, key='t_in_s')
            with c2:
                t_out_s = st.number_input('Temp. Saida Serv. (C)', value=12.0, key='t_out_s')

        btn = st.button('CALCULAR DIMENSIONAMENTO', type='primary', use_container_width=True)

        if btn:
            res = dimensionar(produto, servico, modelo, vazao_p, t_in_p, t_out_p, t_in_s, t_out_s, angulo_sel)
            st.session_state.res = res
            st.session_state.inputs = {
                'modelo': modelo, 'tag': tag, 'projeto': projeto, 'produto': produto,
                'servico': servico, 't_in_p': t_in_p, 't_out_p': t_out_p,
                't_in_s': t_in_s, 't_out_s': t_out_s, 'vazao_p': vazao_p,
                'angulo_sel': angulo_sel
            }

    with col2:
        if 'res' in st.session_state:
            res = st.session_state.res
            inp = st.session_state.inputs

            st.markdown('### RESULTADOS DO DIMENSIONAMENTO')

            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric('Carga Termica', f'{res["carga_kw"]:.2f} kW')
                st.markdown('</div>', unsafe_allow_html=True)
            with k2:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric('Area Requerida', f'{res["area_req"]:.2f} m²')
                st.markdown('</div>', unsafe_allow_html=True)
            with k3:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric('Total de Placas', f'{res["num_placas"]}')
                st.markdown('</div>', unsafe_allow_html=True)

            if res['is_vapor']:
                st.markdown('<div class="vapor-box">', unsafe_allow_html=True)
                st.metric('Consumo de Vapor', f'{res["vazao_s"]:.2f} kg/h', f'hfg = {res["hfg"]:.1f} kJ/kg')
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

            st.markdown('#### Configuracao da Placa')
            ang_col1, ang_col2 = st.columns(2)
            with ang_col1:
                st.markdown(f"<span class='angulo-badge'>{res['angulo']}</span>", unsafe_allow_html=True)
                if inp['angulo_sel'] == 'Automatico (Recomendado)':
                    st.caption('Selecionado automaticamente via Reynolds')
                else:
                    st.caption('Selecao manual do usuario')
            with ang_col2:
                st.write(f"**Multiplicador U:** {res['mult_u']:.2f}x")
                st.write(f"**U Final:** {res['u_final']:.0f} W/m²K")

            st.divider()

            st.markdown('#### Analise de Turbulencia')
            t1, t2 = st.columns(2)
            with t1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.write('**Lado Produto**')
                st.metric('Reynolds', f'{res["re_p"]:.0f}')
                st.markdown('</div>', unsafe_allow_html=True)
            with t2:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.write('**Lado Servico**')
                st.metric('Reynolds', f'{res["re_s"]:.0f}')
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

            st.markdown('#### Datasheet Tecnico')

            with st.expander('Visualizar Datasheet na Tela', expanded=False):
                st.write(f"**Modelo:** {inp['modelo']}")
                st.write(f"**Tag:** {inp['tag']} | **Projeto:** {inp['projeto']}")
                st.write(f"**Angulo da Placa:** {res['angulo']} (Multiplicador: {res['mult_u']}x)")
                st.write(f"**Carga Termica:** {res['carga_kw']:.2f} kW")
                st.write(f"**LMTD:** {res['lmtd']:.2f} C")
                st.write(f"**Area Requerida:** {res['area_req']:.2f} m2")
                st.write(f"**Numero de Placas:** {res['num_placas']}")
                if res['is_vapor']:
                    st.write(f"**Consumo de Vapor:** {res['vazao_s']:.2f} kg/h")
                    st.write(f"**Calor Latente:** {res['hfg']:.1f} kJ/kg")
                st.write('---')
                st.write('**Responsaveis Tecnicos:**')
                st.write('Vitor Soares - engenharia@alfaved.com.br - (18) 99669-7330')
                st.write('Jhonatan Dias Dejato - jhonatan@alfaved.com.br - (18) 99628-8714')

            pdf_bytes = build_pdf(res, inp['modelo'], inp['tag'], inp['projeto'],
                                  inp['produto'], inp['servico'], inp['t_in_p'],
                                  inp['t_out_p'], inp['t_in_s'], inp['t_out_s'],
                                  inp['vazao_p'], inp['angulo_sel'])
            st.download_button(
                label='📥 Download Datasheet PDF',
                data=pdf_bytes,
                file_name=f'AlfaVed_{inp["tag"]}.pdf',
                mime='application/pdf',
                use_container_width=True
            )

            st.divider()
            st.markdown('#### Responsaveis Tecnicos')
            st.markdown('<div class="contact-card"><strong>Vitor Soares</strong> - Responsavel pelo Projeto<br>E-mail: engenharia@alfaved.com.br | Tel: (18) 99669-7330</div>', unsafe_allow_html=True)
            st.markdown('<div class="contact-card"><strong>Jhonatan Dias Dejato</strong> - Diretor de Engenharia<br>E-mail: jhonatan@alfaved.com.br | Tel: (18) 99628-8714</div>', unsafe_allow_html=True)

        else:
            st.info('Preencha os dados de entrada e clique em CALCULAR DIMENSIONAMENTO')

if __name__ == '__main__':
    main()
