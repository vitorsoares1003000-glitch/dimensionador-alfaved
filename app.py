import io
import math
import streamlit as st
st.set_page_config(page_title="AlfaVed Engenharia - Dimensionador", page_icon="▲", layout="wide")
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

BANCO_MODELOS_GAXETADOS = {
    "Alfa Laval M3 (Gaxetado)": {"tipo": "gaxetado", "linha": "BaseLine", "area_placa": 0.030, "U_base": 3800, "pressao_max": 16, "temp_max": 180, "dh": 0.003, "conexao": '1.25" (DN32)', "material": "AISI 316 / Ti"},
    "Alfa Laval M6-B (Gaxetado)": {"tipo": "gaxetado", "linha": "BaseLine", "area_placa": 0.150, "U_base": 4200, "pressao_max": 10, "temp_max": 180, "dh": 0.005, "conexao": "DN50 (2\")", "material": "AISI 304 / 316 / Ti"},
    "Alfa Laval M10-B (Gaxetado)": {"tipo": "gaxetado", "linha": "BaseLine", "area_placa": 0.240, "U_base": 4500, "pressao_max": 10, "temp_max": 180, "dh": 0.006, "conexao": "DN100 (4\")", "material": "AISI 304 / 316 / Ti"},
    "Alfa Laval M15-B (Gaxetado)": {"tipo": "gaxetado", "linha": "BaseLine", "area_placa": 0.360, "U_base": 4700, "pressao_max": 10, "temp_max": 180, "dh": 0.008, "conexao": "DN150 (6\")", "material": "AISI 304 / 316 / Ti"},
    "Alfa Laval T20-B (Gaxetado)": {"tipo": "gaxetado", "linha": "BaseLine", "area_placa": 0.850, "U_base": 4800, "pressao_max": 10, "temp_max": 180, "dh": 0.009, "conexao": "DN200 (8\")", "material": "AISI 304 / 316 / Ti"},
    "Alfa Laval M6-M (Gaxetado)": {"tipo": "gaxetado", "linha": "M-line", "area_placa": 0.150, "U_base": 4250, "pressao_max": 25, "temp_max": 180, "dh": 0.005, "conexao": "DN50 (2\")", "material": "AISI 316 / Ti", "fda": True, "cip": True},
    "Alfa Laval M10-M (Gaxetado)": {"tipo": "gaxetado", "linha": "M-line", "area_placa": 0.240, "U_base": 4550, "pressao_max": 40, "temp_max": 180, "dh": 0.006, "conexao": "DN100 (4\")", "material": "AISI 316 / 254 SMO / Ti", "fda": True, "cip": True},
    "Alfa Laval M15-M (Gaxetado)": {"tipo": "gaxetado", "linha": "M-line", "area_placa": 0.360, "U_base": 4750, "pressao_max": 25, "temp_max": 180, "dh": 0.008, "conexao": "DN150 (6\")", "material": "AISI 316 / 254 SMO / Ti", "fda": True, "cip": True},
    "Alfa Laval T20-M (Gaxetado)": {"tipo": "gaxetado", "linha": "M-line", "area_placa": 0.850, "U_base": 4900, "pressao_max": 30, "temp_max": 180, "dh": 0.009, "conexao": "DN200 (8\")", "material": "AISI 316 / Ti", "fda": True, "cip": True},
    "Alfa Laval MA30-S WideGap (Gaxetado)": {"tipo": "gaxetado", "linha": "WideGap", "area_placa": 1.380, "U_base": 3800, "pressao_max": 25, "temp_max": 180, "dh": 0.012, "conexao": "DN300 (12\")", "material": "AISI 316 / 254 SMO / Ti", "canal": "8/8 mm ou 11/5 mm"},
    "Alfa Laval WideGap 350 (Gaxetado)": {"tipo": "gaxetado", "linha": "WideGap", "area_placa": 1.800, "U_base": 3700, "pressao_max": 10, "temp_max": 180, "dh": 0.015, "conexao": "DN350 (14\")", "material": "AISI 316 / 254 SMO / Ti", "canal": "11/5, 17/5, 8/8 ou 11/11 mm"},
}

BANCO_MODELOS_SEMI_SOLDADOS = {
    "Alfa Laval M10-BW (Semi-Soldado)": {"tipo": "semi-soldado", "linha": "Semi-Welded", "area_placa": 0.240, "U_base": 4600, "pressao_max": 55, "temp_max": 250, "dh": 0.005, "conexao": "DN100 (4\")", "material": "316/316L / 254 SMO / C-276 / Ti", "canal_soldado": "2.4 mm", "aplicacao": "NH3, CO2, refrigerantes"},
    "Alfa Laval MK15-BW (Semi-Soldado)": {"tipo": "semi-soldado", "linha": "Semi-Welded", "area_placa": 0.420, "U_base": 4650, "pressao_max": 41, "temp_max": 200, "dh": 0.006, "conexao": "DN150 (6\")", "material": "316/316L / 254 SMO / Ti", "canal_soldado": "2.5 mm", "aplicacao": "Evaporadores/condensadores NH3/CO2"},
    "Alfa Laval TK20-BW (Semi-Soldado)": {"tipo": "semi-soldado", "linha": "Semi-Welded", "area_placa": 0.680, "U_base": 4700, "pressao_max": 63, "temp_max": 200, "dh": 0.006, "conexao": "DN150/200 (6\"/8\")", "material": "316/316L / 254 SMO / Ti", "canal_soldado": "2.5 mm", "aplicacao": "Heat pumps, refrigeracao industrial alta pressao"},
    "Alfa Laval T20-W (Semi-Soldado)": {"tipo": "semi-soldado", "linha": "Semi-Welded", "area_placa": 0.850, "U_base": 4800, "pressao_max": 30, "temp_max": 180, "dh": 0.009, "conexao": "DN200 (8\")", "material": "AISI 316 / Ti", "canal_soldado": "4.0 mm", "aplicacao": "Condensadores a vacuo, evaporadores grande porte"},
    "Alfa Laval MA30-W (Semi-Soldado)": {"tipo": "semi-soldado", "linha": "Semi-Welded", "area_placa": 1.400, "U_base": 4900, "pressao_max": 40, "temp_max": 180, "dh": 0.010, "conexao": "DN300 (12\")", "material": "AISI 316 / 254 SMO / Ti", "canal_soldado": "4.5 mm", "aplicacao": "Condensadores de turbinas, refrigeracao pesada"},
}

BANCO_MODELOS = {**BANCO_MODELOS_GAXETADOS, **BANCO_MODELOS_SEMI_SOLDADOS}

BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "viscosidade": 0.89, "densidade": 1000},
    "Leite Integral": {"cp": 3.89, "viscosidade": 2.1, "densidade": 1030},
    "Leite Desnatado": {"cp": 3.95, "viscosidade": 1.5, "densidade": 1020},
    "Suco de Laranja": {"cp": 3.75, "viscosidade": 3.5, "densidade": 1040},
    "Suco de Maca": {"cp": 3.70, "viscosidade": 2.8, "densidade": 1035},
    "Oleo Vegetal": {"cp": 1.97, "viscosidade": 50.0, "densidade": 920},
    "Oleo Mineral": {"cp": 1.88, "viscosidade": 100.0, "densidade": 880},
    "Melado": {"cp": 2.80, "viscosidade": 150.0, "densidade": 1380},
    "Cerveja": {"cp": 4.10, "viscosidade": 1.5, "densidade": 1010},
    "Vinho": {"cp": 3.85, "viscosidade": 1.2, "densidade": 1000},
    "Chocolate Quente": {"cp": 3.50, "viscosidade": 8.0, "densidade": 1050},
    "Polpa de Fruta": {"cp": 3.60, "viscosidade": 5.0, "densidade": 1050},
    "Soro de Leite": {"cp": 3.95, "viscosidade": 1.2, "densidade": 1025},
    "Creme de Leite": {"cp": 3.50, "viscosidade": 12.0, "densidade": 980},
}

BANCO_SERVICOS = {
    "Agua Fria": {"cp": 4.18, "viscosidade": 0.89, "densidade": 1000},
    "Agua Gelada": {"cp": 4.18, "viscosidade": 1.3, "densidade": 1000},
    "Agua Morna": {"cp": 4.18, "viscosidade": 0.65, "densidade": 995},
    "Agua Quente": {"cp": 4.18, "viscosidade": 0.35, "densidade": 960},
    "Vapor Saturado": {"cp": 2.0, "viscosidade": 0.015, "densidade": 0.6},
    "Oleo Termico": {"cp": 2.50, "viscosidade": 5.0, "densidade": 850},
    "Refrigerante R22": {"cp": 1.45, "viscosidade": 0.018, "densidade": 450},
    "Refrigerante R410A": {"cp": 1.60, "viscosidade": 0.020, "densidade": 480},
    "Refrigerante R134a": {"cp": 1.52, "viscosidade": 0.019, "densidade": 470},
    "Refrigerante R717 (NH3)": {"cp": 4.70, "viscosidade": 0.25, "densidade": 682},
    "Refrigerante R744 (CO2)": {"cp": 3.50, "viscosidade": 0.07, "densidade": 1100},
    "Ar Comprimido": {"cp": 1.01, "viscosidade": 0.018, "densidade": 1.2},
    "Glicol 30%": {"cp": 3.70, "viscosidade": 3.5, "densidade": 1040},
    "Glicol 50%": {"cp": 3.50, "viscosidade": 6.0, "densidade": 1070},
}

ANGULOS_PLACA = {
    "H (45)": {
        "descricao": "H = 45 graus - Alta turbulencia, alta transferencia termica",
        "multiplicador_u": 1.4,
        "turbulencia": "Alta",
        "queda_pressao": "Alta",
        "reynolds_min": 0,
        "aplicacao": "Maxima transferencia termica, vazoes menores, pressao baixa aceitavel",
        "combinacoes": "HH=45 | HL=52.5 | LL=60"
    },
    "L (60)": {
        "descricao": "L = 60 graus - Menor queda de pressao, eficiencia balanceada",
        "multiplicador_u": 1.0,
        "turbulencia": "Moderada",
        "queda_pressao": "Baixa",
        "reynolds_min": 1500,
        "aplicacao": "Eficiencia balanceada, vazoes maiores, pressao critica",
        "combinacoes": "HH=45 | HL=52.5 | LL=60"
    }
}

styles_doc = getSampleStyleSheet()
st_tit = ParagraphStyle('T1', parent=styles_doc['Heading1'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor('#0d1b2a'))
st_sub = ParagraphStyle('T2', parent=styles_doc['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#d90429'), spaceAfter=15)
st_h2 = ParagraphStyle('T3', parent=styles_doc['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#003049'), spaceBefore=10, spaceAfter=5)
st_body = ParagraphStyle('T4', parent=styles_doc['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#222222'), leading=12)
st_th = ParagraphStyle('T5', parent=styles_doc['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)
st_tc = ParagraphStyle('T6', parent=styles_doc['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#333333'))

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

def calculate_reynolds(vazao_kg_h, viscosidade, densidade, dh):
    if vazao_kg_h <= 0 or viscosidade <= 0 or densidade <= 0:
        return 0
    vazao_m3_s = (vazao_kg_h / 3600.0) / densidade
    area_canal = 0.0001
    u = vazao_m3_s / area_canal
    viscosidade_pa_s = viscosidade * 0.001
    return (densidade * u * dh) / viscosidade_pa_s

def classificar_turbulencia(reynolds):
    if reynolds < 500:
        return ('Laminar', 'Regime laminar - Transferencia de calor limitada')
    elif reynolds < 2000:
        return ('Transicional', 'Transicao laminar-turbulento - Eficiencia moderada')
    else:
        return ('Turbulento', 'Regime turbulento - Otima eficiencia de transferencia')

def recomendar_angulo_placa(reynolds_prod, reynolds_serv, pressao_max):
    reynolds_min = min(reynolds_prod, reynolds_serv)
    if reynolds_min < 500:
        return ('H (45)', ANGULOS_PLACA['H (45)']['multiplicador_u'], 'Reynolds baixo detectado. Placa H (45) recomendada para maxima turbulencia.')
    elif reynolds_min > 2000:
        return ('L (60)', ANGULOS_PLACA['L (60)']['multiplicador_u'], 'Reynolds alto (turbulento). Placa L (60) recomendada para menor queda de pressao.')
    else:
        return ('H (45)', ANGULOS_PLACA['H (45)']['multiplicador_u'], 'Reynolds transicional. Placa H (45) recomendada para otimizar transferencia.')

def get_viscosity_factor(dados_fluido):
    viscosidade = dados_fluido.get('viscosidade', 1.0)
    if viscosidade <= 0 or viscosidade == BANCO_FLUIDOS['Agua']['viscosidade']:
        return 1.0
    return 1.0 / math.sqrt(viscosidade)

def calculate_lmtd(dt1, dt2):
    dt1_abs, dt2_abs = abs(dt1), abs(dt2)
    if dt1_abs < 1e-6 and dt2_abs < 1e-6:
        return 1.0
    if abs(dt1_abs - dt2_abs) < 1e-6:
        return max(dt1_abs, dt2_abs, 1.0)
    if dt1_abs > 0 and dt2_abs > 0:
        return abs((dt1_abs - dt2_abs) / math.log(dt1_abs / dt2_abs))
    return max(dt1_abs, dt2_abs, 1.0)

def calculate_dimensionamento(produto, dados_fluido, modelo, dados_modelo, t_in_prod, t_out_prod, t_in_serv, t_out_serv, vazao_prod, dados_servico):
    cp_prod, cp_serv = dados_fluido['cp'], dados_servico['cp']
    densidade_prod = dados_fluido.get('densidade', 1000)
    densidade_serv = dados_servico.get('densidade', 1000)
    viscosidade_prod = dados_fluido.get('viscosidade', 1.0)
    viscosidade_serv = dados_servico.get('viscosidade', 1.0)
    area_por_placa = dados_modelo['area_placa']
    pressao_max = dados_modelo.get('pressao_max', 25)
    dh = dados_modelo.get('dh', 0.005)
    reynolds_prod = calculate_reynolds(vazao_prod, viscosidade_prod, densidade_prod, dh)
    dT_prod = abs(t_in_prod - t_out_prod)
    carga_kw = (vazao_prod * cp_prod * dT_prod) / 3600.0
    delta_t_serv = abs(t_out_serv - t_in_serv)
    vazao_serv = (carga_kw * 3600.0) / (cp_serv * delta_t_serv) if delta_t_serv > 0 else 0.0
    reynolds_serv = calculate_reynolds(vazao_serv, viscosidade_serv, densidade_serv, dh)
    regime_prod, desc_prod = classificar_turbulencia(reynolds_prod)
    regime_serv, desc_serv = classificar_turbulencia(reynolds_serv)
    tipo_placa, multiplicador_u, justificativa_angulo = recomendar_angulo_placa(reynolds_prod, reynolds_serv, pressao_max)
    fator_viscosidade = get_viscosity_factor(dados_fluido)
    U_adotado = dados_modelo['U_base'] * fator_viscosidade * multiplicador_u
    dt1 = t_in_prod - t_out_serv
    dt2 = t_out_prod - t_in_serv
    lmtd = calculate_lmtd(dt1, dt2)
    area_m2 = (carga_kw * 1000.0) / (U_adotado * lmtd) if lmtd > 0 else 0.0
    placas = math.ceil(area_m2 / area_por_placa) + 2
    if placas % 2 != 0:
        placas += 1
    return {
        'carga_kw': carga_kw, 'vazao_serv': vazao_serv, 'lmtd': lmtd,
        'area_m2': area_m2, 'placas': placas, 'area_por_placa': area_por_placa,
        'U_adotado': U_adotado, 'U_base': dados_modelo['U_base'],
        'fator_viscosidade': fator_viscosidade, 'multiplicador_placa': multiplicador_u,
        'reynolds_prod': reynolds_prod, 'reynolds_serv': reynolds_serv,
        'regime_prod': regime_prod, 'regime_serv': regime_serv,
        'desc_prod': desc_prod, 'desc_serv': desc_serv,
        'tipo_placa': tipo_placa, 'justificativa_placa': justificativa_angulo,
        'linha_modelo': dados_modelo.get('linha', 'N/A'),
        'conexao': dados_modelo.get('conexao', 'N/A'),
        'material_modelo': dados_modelo.get('material', 'N/A'),
    }

def build_pdf(modelo, tag, projeto, produto, servico, t_in_prod, t_out_prod, t_in_serv, t_out_serv, vazao_prod, vazao_serv, resultados, tipo_modelo):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = [
        Paragraph('AlfaVed Solucoes Industriais', st_tit),
        Paragraph('DATASHEET TECNICO - DIMENSIONAMENTO DE TROCADOR DE CALOR', st_sub),
        Spacer(1, 10)
    ]
    story.append(Paragraph('1. Informacoes Gerais do Projeto', st_h2))
    story.append(Table([
        [Paragraph('Item', st_th), Paragraph('Especificacao', st_th)],
        [Paragraph('Modelo Selecionado', st_tc), Paragraph(modelo, st_tc)],
        [Paragraph('Tipo de Modelo', st_tc), Paragraph(tipo_modelo, st_tc)],
        [Paragraph('Linha de Produto', st_tc), Paragraph(resultados.get('linha_modelo', 'N/A'), st_tc)],
        [Paragraph('Tag', st_tc), Paragraph(tag, st_tc)],
        [Paragraph('Projeto', st_tc), Paragraph(projeto, st_tc)],
        [Paragraph('Material Placa', st_tc), Paragraph(resultados.get('material_modelo', 'N/A'), st_tc)],
        [Paragraph('Conexao', st_tc), Paragraph(resultados.get('conexao', 'N/A'), st_tc)],
    ]))
    story.append(Paragraph('2. Parametros Operacionais Processados', st_h2))
    story.append(Table([
        [Paragraph('Propriedade', st_th), Paragraph('Lado do Produto', st_th), Paragraph('Lado do Servico', st_th)],
        [Paragraph('Fluido', st_tc), Paragraph(produto, st_tc), Paragraph(servico, st_tc)],
        [Paragraph('Temp Entrada', st_tc), Paragraph(f'{t_in_prod} C', st_tc), Paragraph(f'{t_in_serv} C', st_tc)],
        [Paragraph('Temp Saida', st_tc), Paragraph(f'{t_out_prod} C', st_tc), Paragraph(f'{t_out_serv} C', st_tc)],
        [Paragraph('Vazao Massica', st_tc), Paragraph(f'{vazao_prod} kg/h', st_tc), Paragraph(f'{vazao_serv:.1f} kg/h', st_tc)],
    ]))
    story.append(Paragraph('3. Analise de Turbulencia - Numero de Reynolds', st_h2))
    story.append(Table([
        [Paragraph('Parametro', st_th), Paragraph('Lado Produto', st_th), Paragraph('Lado Servico', st_th)],
        [Paragraph('Numero de Reynolds', st_tc), Paragraph(f'{resultados["reynolds_prod"]:.0f}', st_tc), Paragraph(f'{resultados["reynolds_serv"]:.0f}', st_tc)],
        [Paragraph('Regime Escoamento', st_tc), Paragraph(resultados['regime_prod'], st_tc), Paragraph(resultados['regime_serv'], st_tc)],
        [Paragraph('Descricao', st_tc), Paragraph(resultados['desc_prod'], st_tc), Paragraph(resultados['desc_serv'], st_tc)],
    ]))
    story.append(Paragraph('4. Configuracao de Placa Alfa Laval Recomendada', st_h2))
    placa_info = ANGULOS_PLACA[resultados['tipo_placa']]
    story.append(Table([
        [Paragraph('Especificacao', st_th), Paragraph('Valor', st_th)],
        [Paragraph('Tipo de Placa', st_tc), Paragraph(resultados['tipo_placa'], st_tc)],
        [Paragraph('Descricao', st_tc), Paragraph(placa_info['descricao'], st_tc)],
        [Paragraph('Turbulencia', st_tc), Paragraph(placa_info['turbulencia'], st_tc)],
        [Paragraph('Queda de Pressao', st_tc), Paragraph(placa_info['queda_pressao'], st_tc)],
        [Paragraph('Combinacoes de Canal', st_tc), Paragraph(placa_info.get('combinacoes', 'HH=45 | HL=52.5 | LL=60'), st_tc)],
        [Paragraph('Justificativa', st_tc), Paragraph(resultados['justificativa_placa'], st_tc)],
    ]))
    story.append(Paragraph('5. Resultados do Dimensionamento Hidro-Termico', st_h2))
    story.append(Table([
        [Paragraph('Grandeza de Engenharia', st_th), Paragraph('Valor Calculado', st_th)],
        [Paragraph('Carga Termica', st_tc), Paragraph(f'{resultados["carga_kw"]:.2f} kW', st_tc)],
        [Paragraph('LMTD', st_tc), Paragraph(f'{resultados["lmtd"]:.2f} C', st_tc)],
        [Paragraph('Coeficiente U Base', st_tc), Paragraph(f'{resultados["U_base"]:.0f} W/m2K', st_tc)],
        [Paragraph('Fator Viscosidade', st_tc), Paragraph(f'{resultados["fator_viscosidade"]:.3f}', st_tc)],
        [Paragraph('Multiplicador Placa', st_tc), Paragraph(f'{resultados["multiplicador_placa"]:.2f}x', st_tc)],
        [Paragraph('Coeficiente U Adotado', st_tc), Paragraph(f'{resultados["U_adotado"]:.0f} W/m2K', st_tc)],
        [Paragraph('Area Efetiva Requerida', st_tc), Paragraph(f'{resultados["area_m2"]:.2f} m2', st_tc)],
        [Paragraph('Area por Placa', st_tc), Paragraph(f'{resultados["area_por_placa"]} m2', st_tc)],
        [Paragraph('Quantidade de Placas', st_tc), Paragraph(f'{resultados["placas"]} placas', st_tc)],
    ]))
    story.append(Paragraph('6. Responsaveis Tecnicos', st_h2))
    story.append(Table([
        [Paragraph('Nome', st_th), Paragraph('Cargo', st_th), Paragraph('E-mail', st_th), Paragraph('Telefone', st_th)],
        [Paragraph('Vitor Soares', st_tc), Paragraph('Responsavel pelo Projeto', st_tc), Paragraph('engenharia@alfaved.com.br', st_tc), Paragraph('(18) 9.9669-7330', st_tc)],
        [Paragraph('Jhonatan Dias Dejato', st_tc), Paragraph('Diretor de Engenharia', st_tc), Paragraph('jhonatan@alfaved.com.br', st_tc), Paragraph('(18) 9.9628-8714', st_tc)],
    ]))
    for item in story:
        if isinstance(item, Table):
            item.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1b2a')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()
    return pdf_data

def main():
    st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #0d1b2a 0%, #003049 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
    .section-card { background-color: #f8f9fa; border-left: 4px solid #0d1b2a; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .metric-box { background: linear-gradient(135deg, #003049 0%, #1f5a6f 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
    .result-success { background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; }
    .result-warning { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; }
    .linha-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-baseline { background: #e3f2fd; color: #1565c0; }
    .badge-mline { background: #e8f5e9; color: #2e7d32; }
    .badge-widegap { background: #fff3e0; color: #e65100; }
    .badge-semiwelded { background: #fce4ec; color: #c62828; }
    .contact-card { background: #f0f4f8; border-left: 4px solid #003049; padding: 15px; border-radius: 5px; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1>AlfaVed Engenharia Termica</h1>
        <h3>Dimensionador Inteligente de Trocadores de Calor</h3>
        <p>Banco Alfa Laval | B/M Variants | H=45 L=60 | Semi-Soldadas | WideGap</p>
    </div>
    """, unsafe_allow_html=True)
    input_col, result_col = st.columns([1, 1.2], gap='large')
    with input_col:
        st.markdown('### DADOS DE PROJETO')
        with st.form('form_dimensionamento', clear_on_submit=False):
            st.markdown('#### Informacoes do Projeto')
            tag = st.text_input('Tag do Equipamento', 'TC-101', key='tag_input')
            projeto = st.text_input('Numero do Projeto', 'PRJ-ALFAVED-2026', key='proj_input')
            st.divider()
            st.markdown('#### Selecao do Modelo')
            filtro_cat = st.selectbox('Filtrar por Categoria', ['Todos', 'Gaxetados (Simplis)', 'Semi-Soldados (Gases)'], key='filtro_cat')
            if filtro_cat == 'Gaxetados (Simplis)':
                modelos_filtrados = list(BANCO_MODELOS_GAXETADOS.keys())
            elif filtro_cat == 'Semi-Soldados (Gases)':
                modelos_filtrados = list(BANCO_MODELOS_SEMI_SOLDADOS.keys())
            else:
                modelos_filtrados = list(BANCO_MODELOS.keys())
            modelo = st.selectbox('Modelo Alfa Laval', modelos_filtrados, key='modelo_input')
            dados_mod = BANCO_MODELOS[modelo]
            tipo_modelo = dados_mod['tipo'].upper()
            linha_mod = dados_mod.get('linha', 'N/A')
            badge_class = {'BaseLine': 'badge-baseline', 'M-line': 'badge-mline', 'WideGap': 'badge-widegap', 'Semi-Welded': 'badge-semiwelded'}.get(linha_mod, 'badge-baseline')
            st.markdown(f"<span class='linha-badge {badge_class}'>{linha_mod}</span> | Tipo: <strong>{tipo_modelo}</strong> | P Max: <strong>{dados_mod['pressao_max']} bar</strong> | T Max: <strong>{dados_mod['temp_max']}C</strong>", unsafe_allow_html=True)
            if dados_mod.get('canal_soldado'):
                st.caption(f"Canal soldado: {dados_mod['canal_soldado']} | Aplicacao: {dados_mod.get('aplicacao', 'N/A')}")
            if dados_mod.get('canal'):
                st.caption(f"Configuracoes de canal: {dados_mod['canal']}")
            st.divider()
            st.markdown('#### Lado do Produto')
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
            st.markdown('#### Lado do Servico')
            servico = st.selectbox('Fluido de Servico', list(BANCO_SERVICOS.keys()), key='serv_input')
            col_temp_serv1, col_temp_serv2 = st.columns(2)
            with col_temp_serv1:
                t_in_serv = st.number_input('Temp. Entrada (C)', value=0.0, key='t_in_serv_input')
            with col_temp_serv2:
                t_out_serv = st.number_input('Temp. Saida (C)', value=12.0, key='t_out_serv_input')
            st.divider()
            submitted = st.form_submit_button('CALCULAR DIMENSIONAMENTO', use_container_width=True, type='primary')
        if submitted:
            resultados = calculate_dimensionamento(
                produto, BANCO_FLUIDOS[produto], modelo, dados_mod,
                t_in_prod, t_out_prod, t_in_serv, t_out_serv,
                vazao_prod, BANCO_SERVICOS[servico]
            )
            pdf_bytes = build_pdf(
                modelo, tag, projeto, produto, servico,
                t_in_prod, t_out_prod, t_in_serv, t_out_serv,
                vazao_prod, resultados['vazao_serv'],
                resultados, tipo_modelo
            )
            st.session_state.resultados = resultados
            st.session_state.pdf_bytes = pdf_bytes
            st.session_state.modelo_res = modelo
            st.session_state.tipo_modelo_res = tipo_modelo
            st.session_state.tag_res = tag
            st.session_state.projeto_res = projeto
            st.session_state.produto_res = produto
            st.session_state.servico_res = servico
            st.session_state.t_in_prod_res = t_in_prod
            st.session_state.t_out_prod_res = t_out_prod
            st.session_state.t_in_serv_res = t_in_serv
            st.session_state.t_out_serv_res = t_out_serv
            st.session_state.vazao_prod_res = vazao_prod
            st.success('Calculo e relatorios estruturados com sucesso!')
            st.rerun()
    with result_col:
        if 'resultados' in st.session_state:
            resultados = st.session_state.resultados
            st.markdown('### RESULTADOS DO DIMENSIONAMENTO')
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            with kpi_col1:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric('Carga Termica', f'{resultados["carga_kw"]:.2f} kW')
                st.markdown('</div>', unsafe_allow_html=True)
            with kpi_col2:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric('Area Requerida', f'{resultados["area_m2"]:.2f} m2')
                st.markdown('</div>', unsafe_allow_html=True)
            with kpi_col3:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric('Quantidade Placas', f'{resultados["placas"]}')
                st.markdown('</div>', unsafe_allow_html=True)
            st.divider()
            st.markdown('#### Analise de Turbulencia')
            turb_col1, turb_col2 = st.columns(2)
            with turb_col1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('**Lado Produto**')
                st.metric('Reynolds', f'{resultados["reynolds_prod"]:.0f}', resultados['regime_prod'])
                st.caption(resultados['desc_prod'])
                st.markdown('</div>', unsafe_allow_html=True)
            with turb_col2:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('**Lado Servico**')
                st.metric('Reynolds', f'{resultados["reynolds_serv"]:.0f}', resultados['regime_serv'])
                st.caption(resultados['desc_serv'])
                st.markdown('</div>', unsafe_allow_html=True)
            st.divider()
            st.markdown('#### Configuracao Recomendada')
            placa_info = ANGULOS_PLACA[resultados['tipo_placa']]
            placa_col1, placa_col2 = st.columns(2)
            with placa_col1:
                st.markdown(
                    f'<div class="result-success">'
                    f'<h4>Tipo de Placa: <strong>{resultados["tipo_placa"]}</strong></h4>'
                    f'<p>{placa_info["descricao"]}</p><hr>'
                    f'<p><strong>Turbulencia:</strong> {placa_info["turbulencia"]}</p>'
                    f'<p><strong>Queda Pressao:</strong> {placa_info["queda_pressao"]}</p>'
                    f'<p><strong>Combinacoes:</strong> {placa_info.get("combinacoes", "HH/HL/LL")}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with placa_col2:
                st.markdown(
                    f'<div class="result-warning">'
                    f'<p><strong>Multiplicador U:</strong> {resultados["multiplicador_placa"]:.2f}x</p>'
                    f'<p><strong>U Adotado:</strong> {resultados["U_adotado"]:.0f} W/m2K</p>'
                    f'<p><strong>LMTD:</strong> {resultados["lmtd"]:.2f} C</p>'
                    f'<p><strong>Linha:</strong> {resultados.get("linha_modelo", "N/A")}</p>'
                    f'<p><strong>Material:</strong> {resultados.get("material_modelo", "N/A")}</p>'
                    f'<p><strong>Conexao:</strong> {resultados.get("conexao", "N/A")}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.info(f"{resultados['justificativa_placa']}")
            st.divider()
            st.markdown('#### Datasheet Tecnico')
            st.download_button(
                label='📥 Download Datasheet PDF',
                data=st.session_state.pdf_bytes,
                file_name=f'datasheet_{st.session_state.get("tag_res", "TC")}.pdf',
                mime='application/pdf',
                use_container_width=True
            )
            with st.expander('📄 Visualizar Datasheet na Tela'):
                st.markdown('#### 1. Informacoes Gerais do Projeto')
                st.write(f"**Modelo:** {st.session_state.get('modelo_res', 'N/A')}")
