import io
import math
import streamlit as st

st.set_page_config(page_title="AlfaVed Engenharia - Dimensionador", page_icon="▲", layout="wide")

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# ============================================================================
# BANCO DE DADOS - MODELOS ALFA LAVAL
# ============================================================================

BANCO_MODELOS = {
    "Alfa Laval M3 (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "BaseLine", "area_placa": 0.030, "U_base": 3800,
        "pressao_max": 16, "temp_max": 180, "dh": 0.003, "conexao": 'DN32 (1.25")',
        "material": "AISI 316 / Ti", "placas_max": 60
    },
    "Alfa Laval M6-B (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "BaseLine", "area_placa": 0.150, "U_base": 4200,
        "pressao_max": 10, "temp_max": 180, "dh": 0.005, "conexao": 'DN50 (2")',
        "material": "AISI 304 / 316 / Ti", "placas_max": 120
    },
    "Alfa Laval TS6M (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "M-line", "area_placa": 0.260, "U_base": 4600,
        "pressao_max": 25, "temp_max": 180, "dh": 0.006, "conexao": 'DN65 (2.5")',
        "material": "AISI 316 / Ti", "placas_max": 140, "fda": True, "cip": True
    },
    "Alfa Laval M10-B (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "BaseLine", "area_placa": 0.240, "U_base": 4500,
        "pressao_max": 10, "temp_max": 180, "dh": 0.006, "conexao": 'DN100 (4")',
        "material": "AISI 304 / 316 / Ti", "placas_max": 200
    },
    "Alfa Laval M15-B (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "BaseLine", "area_placa": 0.360, "U_base": 4700,
        "pressao_max": 10, "temp_max": 180, "dh": 0.008, "conexao": 'DN150 (6")',
        "material": "AISI 304 / 316 / Ti", "placas_max": 240
    },
    "Alfa Laval T20-B (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "BaseLine", "area_placa": 0.850, "U_base": 4800,
        "pressao_max": 10, "temp_max": 180, "dh": 0.009, "conexao": 'DN200 (8")',
        "material": "AISI 304 / 316 / Ti", "placas_max": 280
    },
    "Alfa Laval M6-M (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "M-line", "area_placa": 0.150, "U_base": 4250,
        "pressao_max": 25, "temp_max": 180, "dh": 0.005, "conexao": 'DN50 (2")',
        "material": "AISI 316 / Ti", "placas_max": 120, "fda": True, "cip": True
    },
    "Alfa Laval M10-M (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "M-line", "area_placa": 0.240, "U_base": 4550,
        "pressao_max": 40, "temp_max": 180, "dh": 0.006, "conexao": 'DN100 (4")',
        "material": "AISI 316 / 254 SMO / Ti", "placas_max": 200, "fda": True, "cip": True
    },
    "Alfa Laval M15-M (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "M-line", "area_placa": 0.360, "U_base": 4750,
        "pressao_max": 25, "temp_max": 180, "dh": 0.008, "conexao": 'DN150 (6")',
        "material": "AISI 316 / 254 SMO / Ti", "placas_max": 240, "fda": True, "cip": True
    },
    "Alfa Laval T20-M (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "M-line", "area_placa": 0.850, "U_base": 4900,
        "pressao_max": 30, "temp_max": 180, "dh": 0.009, "conexao": 'DN200 (8")',
        "material": "AISI 316 / Ti", "placas_max": 280, "fda": True, "cip": True
    },
    "Alfa Laval TS20M (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "M-line", "area_placa": 0.950, "U_base": 4950,
        "pressao_max": 25, "temp_max": 180, "dh": 0.009, "conexao": 'DN200 (8")',
        "material": "AISI 316 / 254 SMO / Ti", "placas_max": 300, "fda": True, "cip": True
    },
    "Alfa Laval MA30-S WideGap (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "WideGap", "area_placa": 1.380, "U_base": 3800,
        "pressao_max": 25, "temp_max": 180, "dh": 0.012, "conexao": 'DN300 (12")',
        "material": "AISI 316 / 254 SMO / Ti", "placas_max": 200, "canal": "8/8 ou 11/5 mm"
    },
    "Alfa Laval WideGap 350 (Gaxetado)": {
        "tipo": "Gaxetado", "linha": "WideGap", "area_placa": 1.800, "U_base": 3700,
        "pressao_max": 10, "temp_max": 180, "dh": 0.015, "conexao": 'DN350 (14")',
        "material": "AISI 316 / 254 SMO / Ti", "placas_max": 220, "canal": "11/5, 17/5, 8/8, 11/11 mm"
    },
    "Alfa Laval M10-BW (Semi-Soldado)": {
        "tipo": "Semi-Soldado", "linha": "Semi-Welded", "area_placa": 0.240, "U_base": 4600,
        "pressao_max": 55, "temp_max": 250, "dh": 0.005, "conexao": 'DN100 (4")',
        "material": "316/316L / 254 SMO / C-276 / Ti", "placas_max": 200, "canal_soldado": "2.4 mm"
    },
    "Alfa Laval MK15-BW (Semi-Soldado)": {
        "tipo": "Semi-Soldado", "linha": "Semi-Welded", "area_placa": 0.420, "U_base": 4650,
        "pressao_max": 41, "temp_max": 200, "dh": 0.006, "conexao": 'DN150 (6")',
        "material": "316/316L / 254 SMO / Ti", "placas_max": 240, "canal_soldado": "2.5 mm"
    },
    "Alfa Laval TK20-BW (Semi-Soldado)": {
        "tipo": "Semi-Soldado", "linha": "Semi-Welded", "area_placa": 0.680, "U_base": 4700,
        "pressao_max": 63, "temp_max": 200, "dh": 0.006, "conexao": 'DN150/200 (6"/8")',
        "material": "316/316L / 254 SMO / Ti", "placas_max": 260, "canal_soldado": "2.5 mm"
    },
    "Alfa Laval T20-W (Semi-Soldado)": {
        "tipo": "Semi-Soldado", "linha": "Semi-Welded", "area_placa": 0.850, "U_base": 4800,
        "pressao_max": 30, "temp_max": 180, "dh": 0.009, "conexao": 'DN200 (8")',
        "material": "AISI 316 / Ti", "placas_max": 280, "canal_soldado": "4.0 mm"
    },
    "Alfa Laval MA30-W (Semi-Soldado)": {
        "tipo": "Semi-Soldado", "linha": "Semi-Welded", "area_placa": 1.400, "U_base": 4900,
        "pressao_max": 40, "temp_max": 180, "dh": 0.010, "conexao": 'DN300 (12")',
        "material": "AISI 316 / 254 SMO / Ti", "placas_max": 300, "canal_soldado": "4.5 mm"
    },
}

BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "viscosidade": 0.89, "densidade": 1000, "categoria": "aquoso"},
    "Leite Integral": {"cp": 3.89, "viscosidade": 2.1, "densidade": 1030, "categoria": "laticinio"},
    "Leite Desnatado": {"cp": 3.95, "viscosidade": 1.5, "densidade": 1020, "categoria": "laticinio"},
    "Suco de Laranja": {"cp": 3.75, "viscosidade": 3.5, "densidade": 1040, "categoria": "fruta"},
    "Suco de Maca": {"cp": 3.70, "viscosidade": 2.8, "densidade": 1035, "categoria": "fruta"},
    "Oleo Vegetal": {"cp": 1.97, "viscosidade": 50.0, "densidade": 920, "categoria": "oleo"},
    "Oleo Mineral": {"cp": 1.88, "viscosidade": 100.0, "densidade": 880, "categoria": "oleo"},
    "Melado": {"cp": 2.80, "viscosidade": 150.0, "densidade": 1380, "categoria": "acucar"},
    "Cerveja": {"cp": 4.10, "viscosidade": 1.5, "densidade": 1010, "categoria": "bebida"},
    "Vinho": {"cp": 3.85, "viscosidade": 1.2, "densidade": 1000, "categoria": "bebida"},
    "Chocolate Quente": {"cp": 3.50, "viscosidade": 8.0, "densidade": 1050, "categoria": "alimento"},
    "Polpa de Fruta": {"cp": 3.60, "viscosidade": 5.0, "densidade": 1050, "categoria": "fruta"},
    "Soro de Leite": {"cp": 3.95, "viscosidade": 1.2, "densidade": 1025, "categoria": "laticinio"},
    "Creme de Leite": {"cp": 3.50, "viscosidade": 12.0, "densidade": 980, "categoria": "laticinio"},
    "Iogurte": {"cp": 3.70, "viscosidade": 25.0, "densidade": 1060, "categoria": "laticinio"},
    "Nata": {"cp": 3.40, "viscosidade": 15.0, "densidade": 970, "categoria": "laticinio"},
    "Manteiga Derretida": {"cp": 2.10, "viscosidade": 40.0, "densidade": 910, "categoria": "oleo"},
}

BANCO_SERVICOS = {
    "Agua Fria": {"cp": 4.18, "viscosidade": 0.89, "densidade": 1000, "categoria": "aquoso", "is_vapor": False},
    "Agua Gelada": {"cp": 4.18, "viscosidade": 1.3, "densidade": 1000, "categoria": "aquoso", "is_vapor": False},
    "Agua Morna": {"cp": 4.18, "viscosidade": 0.65, "densidade": 995, "categoria": "aquoso", "is_vapor": False},
    "Agua Quente": {"cp": 4.18, "viscosidade": 0.35, "densidade": 960, "categoria": "aquoso", "is_vapor": False},
    "Vapor Saturado": {"cp": 2.0, "viscosidade": 0.015, "densidade": 0.6, "categoria": "vapor", "is_vapor": True},
    "Oleo Termico": {"cp": 2.50, "viscosidade": 5.0, "densidade": 850, "categoria": "oleo", "is_vapor": False},
    "Refrigerante R22": {"cp": 1.45, "viscosidade": 0.018, "densidade": 450, "categoria": "gas", "is_vapor": False},
    "Refrigerante R410A": {"cp": 1.60, "viscosidade": 0.020, "densidade": 480, "categoria": "gas", "is_vapor": False},
    "Refrigerante R134a": {"cp": 1.52, "viscosidade": 0.019, "densidade": 470, "categoria": "gas", "is_vapor": False},
    "Refrigerante R717 (NH3)": {"cp": 4.70, "viscosidade": 0.25, "densidade": 682, "categoria": "gas", "is_vapor": False},
    "Refrigerante R744 (CO2)": {"cp": 3.50, "viscosidade": 0.07, "densidade": 1100, "categoria": "gas", "is_vapor": False},
    "Ar Comprimido": {"cp": 1.01, "viscosidade": 0.018, "densidade": 1.2, "categoria": "gas", "is_vapor": False},
    "Glicol 30%": {"cp": 3.70, "viscosidade": 3.5, "densidade": 1040, "categoria": "aquoso", "is_vapor": False},
    "Glicol 50%": {"cp": 3.50, "viscosidade": 6.0, "densidade": 1070, "categoria": "aquoso", "is_vapor": False},
}

# ============================================================================
# CONFIGURACAO DE GAXETAS
# ============================================================================

BANCO_GAXETAS = {
    "EPDM": {
        "temp_max": 150, "aplicacoes": ["aquoso", "laticinio", "fruta", "bebida", "alimento"],
        "incompativel": ["oleo", "gas", "solvente"],
        "descricao": "Etileno Propileno. Excelente para agua, leite, sucos. Padrao FDA."
    },
    "NBR (Nitrilica)": {
        "temp_max": 120, "aplicacoes": ["oleo", "gas", "aquoso"],
        "incompativel": ["laticinio", "fruta"],
        "descricao": "Borracha Nitrilica. Resistente a oleos minerais e hidrocarbonetos."
    },
    "Viton (FKM)": {
        "temp_max": 200, "aplicacoes": ["oleo", "gas", "aquoso", "laticinio", "alimento"],
        "incompativel": [],
        "descricao": "Fluoroelastomero. Alta temperatura, resistencia quimica superior."
    },
    "PTFE (Teflon)": {
        "temp_max": 260, "aplicacoes": ["aquoso", "oleo", "gas", "laticinio", "fruta", "bebida", "alimento", "acucar"],
        "incompativel": [],
        "descricao": "Politetrafluoroetileno. Quimicamente inerte, temperatura extrema."
    },
    "CSM (Hypalon)": {
        "temp_max": 130, "aplicacoes": ["aquoso", "oleo", "gas"],
        "incompativel": ["laticinio"],
        "descricao": "Clorossulfonado Polietileno. Resistente a oxidantes e ozonio."
    },
    "Butyl": {
        "temp_max": 130, "aplicacoes": ["aquoso", "laticinio", "bebida"],
        "incompativel": ["oleo", "gas"],
        "descricao": "Isopreno. Baixa permeabilidade a gases, bom para agua e bebidas."
    }
}

# ============================================================================
# CONFIGURACAO DE ANGULOS DE PLACA
# ============================================================================

CONFIG_ANGULOS = {
    "H (45°)": {
        "multiplicador_u": 1.4,
        "angulo_graus": 45,
        "descricao": "Alta turbulencia, maxima transferencia de calor",
        "queda_pressao": "Alta",
        "aplicacao": "Fluidos limpos, vazoes moderadas, maxima eficiencia termica"
    },
    "L (60°)": {
        "multiplicador_u": 1.0,
        "angulo_graus": 60,
        "descricao": "Menor queda de pressao, eficiencia balanceada",
        "queda_pressao": "Baixa",
        "aplicacao": "Vazoes elevadas, fluidos viscosos, pressao limitada"
    },
    "Mista (HL = 52.5°)": {
        "multiplicador_u": 1.2,
        "angulo_graus": 52.5,
        "descricao": "Compromisso entre transferencia e queda de pressao",
        "queda_pressao": "Moderada",
        "aplicacao": "Aplicacoes gerais, eficiencia intermediaria"
    }
}

# ============================================================================
# ESTILOS PDF
# ============================================================================

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

# ============================================================================
# FUNCOES DE ENGENHARIA
# ============================================================================

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
        return 'Laminar', 'Regime laminar - Transferencia de calor limitada. Recomenda-se placa H.'
    elif reynolds < 2000:
        return 'Transicional', 'Regime transicional - Eficiencia moderada. Monitorar incrustacao.'
    else:
        return 'Turbulento', 'Regime turbulento - Otima eficiencia de transferencia termica.'

def get_calor_latente_vapor(temp_c):
    if temp_c >= 150:
        return 2114.0
    if temp_c >= 130:
        return 2174.0
    if temp_c >= 110:
        return 2230.0
    if temp_c >= 100:
        return 2257.0
    if temp_c >= 80:
        return 2308.0
    return 2358.0

def recomendar_gaxeta(produto_nome, servico_nome, temp_max, dados_prod, dados_serv):
    cat_p = dados_prod.get('categoria', 'aquoso')
    cat_s = dados_serv.get('categoria', 'aquoso')
    cats = set([cat_p, cat_s])

    # Verificar cada gaxeta por compatibilidade
    candidatas = []
    for nome_gax, props in BANCO_GAXETAS.items():
        if temp_max > props['temp_max']:
            continue
        if any(c in props['incompativel'] for c in cats):
            continue
        score = len([c for c in cats if c in props['aplicacoes']])
        candidatas.append((nome_gax, props, score))

    if not candidatas:
        return "PTFE (Teflon)", "Temperatura ou fluido agressivo. PTFE e a unica opcao segura."

    candidatas.sort(key=lambda x: (x[2], x[1]['temp_max']), reverse=True)
    melhor = candidatas[0]
    return melhor[0], melhor[1]['descricao']

def calcular_queda_pressao(reynolds, num_placas, angulo, vazao, densidade, viscosidade):
    if reynolds <= 0:
        return 0.0

    fator_angulo = 1.5 if "H" in angulo else (1.0 if "L" in angulo else 1.25)
    fator_placas = num_placas / 10.0
    fator_reynolds = max(0.1, 2000.0 / max(reynolds, 100))

    # Estimativa simplificada de queda de pressao em bar
    dp = 0.05 * fator_angulo * fator_placas * fator_reynolds
    return min(dp, 2.0)  # Limitar a valores razoaveis

def determinar_arranjo_passe(vazao_prod, lmtd, reynolds_prod, reynolds_serv, num_placas):
    """
    Determina o arranjo de passe do trocador:
    - Single Pass (1/1): Fluidos entram e saem pelo cabecote fixo
    - Two Pass (2/2): Cada fluido faz 2 passes
    - Multi-Pass (3/3 ou mais): Alta complexidade
    """
    if vazao_prod > 30000 or (reynolds_prod < 500 and reynolds_serv < 500):
        return {
            'codigo': '2/2',
            'nome': 'Two Pass',
            'descricao': 'Cada fluido percorre 2 passes no trocador. Aumenta turbulencia e aproxima temperaturas.',
            'placas_pass': max(2, num_placas // 2),
            'justificativa': 'Alta vazao ou baixo Reynolds exige multi-passe para garantir troca termica eficiente.'
        }
    if lmtd < 3.0:
        return {
            'codigo': '2/2',
            'nome': 'Two Pass',
            'descricao': 'Dois passes por lado para maximizar aproximacao de temperaturas.',
            'placas_pass': max(2, num_placas // 2),
            'justificativa': 'LMTD muito baixo (< 3C) requer multi-passe para eficiencia.'
        }
    return {
        'codigo': '1/1',
        'nome': 'Single Pass',
        'descricao': 'Fluidos percorrem uma unica vez o trocador, sentido contracorrente.',
        'placas_pass': num_placas,
        'justificativa': 'Vazao e temperaturas dentro da faixa ideal para passe unico.'
    }

def determinar_conexoes(arranjo_passe):
    """
    Define onde os fluidos entram e saem:
    - Single Pass: Entrada e saida no cabecote FIXO (frame plate)
    - Two Pass: Entrada no FIXO, saida no MOVEL (pressure plate) para um dos fluidos
    """
    if arranjo_passe['codigo'] == '1/1':
        return {
            'produto_entrada': 'Cabecote Fixo (Frame Plate)',
            'produto_saida': 'Cabecote Fixo (Frame Plate)',
            'servico_entrada': 'Cabecote Fixo (Frame Plate)',
            'servico_saida': 'Cabecote Fixo (Frame Plate)',
            'descricao': 'Arranjo 1/1: Todas as conexoes no cabecote fixo. Manutencao simplificada.',
            'port_arrangement': 'Conexoes frontais unicas'
        }
    else:
        return {
            'produto_entrada': 'Cabecote Fixo (Frame Plate)',
            'produto_saida': 'Cabecote Fixo (Frame Plate)',
            'servico_entrada': 'Cabecote Fixo (Frame Plate)',
            'servico_saida': 'Prato de Pressao (Pressure Plate)',
            'descricao': 'Arranjo multi-passe: Servico com saida no prato movel para reversao de fluxo.',
            'port_arrangement': 'Pass 1: Fixo -> Movel | Pass 2: Movel -> Fixo'
        }

def verificar_viabilidade(dados_modelo, temp_max, pressao_op, num_placas):
    alertas = []
    if temp_max > dados_modelo['temp_max']:
        alertas.append(f"Temperatura operacional ({temp_max}C) excede limite do modelo ({dados_modelo['temp_max']}C)")
    if pressao_op > dados_modelo['pressao_max']:
        alertas.append(f"Pressao operacional ({pressao_op} bar) excede limite do modelo ({dados_modelo['pressao_max']} bar)")
    placas_max = dados_modelo.get('placas_max', 300)
    if num_placas > placas_max:
        alertas.append(f"Numero de placas ({num_placas}) excede capacidade maxima do modelo ({placas_max})")
    return alertas

def calculate_lmtd(dt1, dt2):
    dt1_abs, dt2_abs = abs(dt1), abs(dt2)
    if dt1_abs < 1e-6 or dt2_abs < 1e-6:
        return max(dt1_abs, dt2_abs, 0.1)
    if abs(dt1_abs - dt2_abs) < 1e-6:
        return dt1_abs
    return (dt1_abs - dt2_abs) / math.log(dt1_abs / dt2_abs)

def calculate_dimensionamento(produto, servico, modelo, vazao_prod,
                              t_in_prod, t_out_prod, t_in_serv, t_out_serv,
                              angulo_manual):
    dados_prod = BANCO_FLUIDOS[produto]
    dados_serv = BANCO_SERVICOS[servico]
    dados_mod = BANCO_MODELOS[modelo]

    cp_prod = dados_prod['cp']
    cp_serv = dados_serv['cp']
    densidade_prod = dados_prod['densidade']
    densidade_serv = dados_serv['densidade']
    viscosidade_prod = dados_prod['viscosidade']
    viscosidade_serv = dados_serv['viscosidade']

    is_vapor = dados_serv.get('is_vapor', False)

    # Carga Termica
    carga_kw = (vazao_prod * cp_prod * abs(t_in_prod - t_out_prod)) / 3600.0

    # Vazao Servico
    if is_vapor:
        h_fg = get_calor_latente_vapor(t_in_serv)
        vazao_serv = (carga_kw * 3600.0) / h_fg
        t_out_serv_calc = t_in_serv
    else:
        dt_s = abs(t_in_serv - t_out_serv)
        vazao_serv = (carga_kw * 3600.0) / (cp_serv * dt_s) if dt_s > 0 else 0
        t_out_serv_calc = t_out_serv

    # Reynolds
    re_prod = calculate_reynolds(vazao_prod, viscosidade_prod, densidade_prod, dados_mod['dh'])
    re_serv = calculate_reynolds(vazao_serv, viscosidade_serv, densidade_serv, dados_mod['dh'])

    regime_prod, desc_reg_prod = classificar_turbulencia(re_prod)
    regime_serv, desc_reg_serv = classificar_turbulencia(re_serv)

    # Angulo da Placa
    if angulo_manual == "Automatico (Recomendado)":
        re_min = min(re_prod, re_serv)
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
    fator_visc = 1.0 / math.sqrt(viscosidade_prod) if viscosidade_prod > 1 else 1.0
    u_final = dados_mod['U_base'] * mult * fator_visc

    dt1 = t_in_prod - t_out_serv_calc
    dt2 = t_out_prod - t_in_serv
    lmtd = calculate_lmtd(dt1, dt2)

    area_req = (carga_kw * 1000.0) / (u_final * lmtd) if lmtd > 0 else 0
    num_placas = math.ceil(area_req / dados_mod['area_placa']) + 2
    if num_placas % 2 != 0:
        num_placas += 1

    # Gaxeta
    temp_max_op = max(t_in_prod, t_out_prod, t_in_serv, t_out_serv_calc)
    gaxeta, gaxeta_just = recomendar_gaxeta(produto, servico, temp_max_op, dados_prod, dados_serv)

    # Queda de Pressao
    dp_prod = calcular_queda_pressao(re_prod, num_placas, angulo, vazao_prod, densidade_prod, viscosidade_prod)
    dp_serv = calcular_queda_pressao(re_serv, num_placas, angulo, vazao_serv, densidade_serv, viscosidade_serv)

    # Arranjo de Passe
    arranjo_passe = determinar_arranjo_passe(vazao_prod, lmtd, re_prod, re_serv, num_placas)

    # Conexoes
    conexoes = determinar_conexoes(arranjo_passe)

    # Viabilidade
    alertas = verificar_viabilidade(dados_mod, temp_max_op, 5.0, num_placas)

    return {
        'carga_kw': carga_kw,
        'vazao_serv': vazao_serv,
        'vapor_kg_h': vazao_serv if is_vapor else 0.0,
        're_prod': re_prod,
        're_serv': re_serv,
        'regime_prod': regime_prod,
        'regime_serv': regime_serv,
        'desc_reg_prod': desc_reg_prod,
        'desc_reg_serv': desc_reg_serv,
        'lmtd': lmtd,
        'area_req': area_req,
        'num_placas': num_placas,
        'u_final': u_final,
        'u_base': dados_mod['U_base'],
        'angulo': angulo,
        'mult_u': mult,
        'fator_visc': fator_visc,
        'is_vapor': is_vapor,
        't_out_serv_calc': t_out_serv_calc,
        'h_fg': h_fg if is_vapor else 0,
        'gaxeta': gaxeta,
        'gaxeta_just': gaxeta_just,
        'dp_prod': dp_prod,
        'dp_serv': dp_serv,
        'arranjo_passe': arranjo_passe,
        'conexoes': conexoes,
        'alertas': alertas,
        'linha': dados_mod.get('linha', 'N/A'),
        'conexao': dados_mod.get('conexao', 'N/A'),
        'material_mod': dados_mod.get('material', 'N/A'),
        'tipo': dados_mod.get('tipo', 'N/A'),
    }

# ============================================================================
# GERACAO PDF
# ============================================================================

def build_pdf(res, modelo, tag, projeto, produto, servico,
              t_in_p, t_out_p, t_in_s, t_out_s, vazao_p, angulo_sel):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = [
        Paragraph('AlfaVed Solucoes Industriais', st_tit),
        Paragraph('DATASHEET TECNICO - DIMENSIONAMENTO DE TROCADOR DE CALOR', st_sub),
        Spacer(1, 10)
    ]

    # Secao 1: Info Geral
    story.append(Paragraph('1. Informacoes Gerais do Projeto', st_h2))
    t1 = Table([
        [Paragraph('Item', st_th), Paragraph('Especificacao', st_th)],
        ['Modelo Selecionado', modelo],
        ['Tipo / Linha', f'{res["tipo"]} / {res["linha"]}'],
        ['Tag', tag],
        ['Projeto', projeto],
        ['Material das Placas', res['material_mod']],
        ['Conexao Nominal', res['conexao']],
        ['Angulo da Placa', res['angulo']],
        ['Selecao do Angulo', 'Automatico (Reynolds)' if angulo_sel == 'Automatico (Recomendado)' else 'Manual pelo usuario'],
    ], colWidths=[180, 330])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1b2a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(t1)

    # Secao 2: Dados de Processo
    story.append(Paragraph('2. Parametros Operacionais Processados', st_h2))
    t2 = Table([
        [Paragraph('Parametro', st_th), Paragraph('Lado Produto', st_th), Paragraph('Lado Servico', st_th)],
        ['Fluido', produto, servico],
        ['Vazao (kg/h)', f'{vazao_p:.1f}', f'{res["vazao_serv"]:.1f} {"(VAPOR)" if res["is_vapor"] else ""}'],
        ['Temp. Entrada (C)', f'{t_in_p:.1f}', f'{t_in_s:.1f}'],
        ['Temp. Saida (C)', f'{t_out_p:.1f}', f'{res["t_out_serv_calc"]:.1f}'],
        ['Reynolds', f'{res["re_prod"]:.0f}', f'{res["re_serv"]:.0f}'],
        ['Regime Escoamento', res['regime_prod'], res['regime_serv']],
        ['Queda Pressao Est. (bar)', f'{res["dp_prod"]:.3f}', f'{res["dp_serv"]:.3f}'],
    ], colWidths=[170, 170, 170])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1b2a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(t2)

    # Secao 3: Configuracao Mecanica
    story.append(Paragraph('3. Configuracao Mecanica e Hidraulica', st_h2))
    t3 = Table([
        [Paragraph('Especificacao', st_th), Paragraph('Valor / Descricao', st_th)],
        ['Angulo da Placa', res['angulo']],
        ['Multiplicador U', f'{res["mult_u"]:.2f}x'],
        ['Arranjo de Passe', f'{res["arranjo_passe"]["codigo"]} - {res["arranjo_passe"]["nome"]}'],
        ['Justificativa Passe', res['arranjo_passe']['justificativa']],
        ['Entrada Produto', res['conexoes']['produto_entrada']],
        ['Saida Produto', res['conexoes']['produto_saida']],
        ['Entrada Servico', res['conexoes']['servico_entrada']],
        ['Saida Servico', res['conexoes']['servico_saida']],
        ['Port Arrangement', res['conexoes']['port_arrangement']],
        ['Material Gaxeta', res['gaxeta']],
        ['Justificativa Gaxeta', res['gaxeta_just']],
    ], colWidths=[180, 330])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1b2a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(t3)

    # Secao 4: Resultados Termicos
    story.append(Paragraph('4. Resultados do Dimensionamento Hidro-Termico', st_h2))
    res_data = [
        [Paragraph('Grandeza', st_th), Paragraph('Valor', st_th)],
        ['Carga Termica', f'{res["carga_kw"]:.2f} kW'],
        ['LMTD', f'{res["lmtd"]:.2f} C'],
        ['Coeficiente U Base', f'{res["u_base"]:.0f} W/m2K'],
        ['Coeficiente U Final', f'{res["u_final"]:.0f} W/m2K'],
        ['Fator Viscosidade', f'{res["fator_visc"]:.3f}'],
        ['Multiplicador Placa', f'{res["mult_u"]:.2f}x'],
        ['Area Requerida', f'{res["area_req"]:.2f} m2'],
        ['Area por Placa', f'{BANCO_MODELOS[modelo]["area_placa"]} m2'],
        ['Numero de Placas', f'{res["num_placas"]} placas'],
    ]
    if res['is_vapor']:
        res_data.append(['Consumo de Vapor', f'{res["vapor_kg_h"]:.2f} kg/h'])
        res_data.append(['Calor Latente (hfg)', f'{res["h_fg"]:.1f} kJ/kg'])

    t4 = Table(res_data, colWidths=[180, 330])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1b2a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(t4)

    # Alertas
    if res['alertas']:
        story.append(Paragraph('5. Alertas e Verificacoes de Viabilidade', st_h2))
        for alerta in res['alertas']:
            story.append(Paragraph(f'⚠ {alerta}', st_body))
        story.append(Spacer(1, 5))

    # Responsaveis
    story.append(Paragraph('6. Responsaveis Tecnicos', st_h2))
    story.append(Paragraph('Vitor Soares - Responsavel pelo Projeto', st_body))
    story.append(Paragraph('E-mail: engenharia@alfaved.com.br | Tel: (18) 99669-7330', st_body))
    story.append(Spacer(1, 3))
    story.append(Paragraph('Jhonatan Dias Dejato - Diretor de Engenharia', st_body))
    story.append(Paragraph('E-mail: jhonatan@alfaved.com.br | Tel: (18) 99628-8714', st_body))

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
    .result-success { background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; }
    .result-warning { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; }
    .result-danger { background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; border-radius: 5px; }
    .vapor-box { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; }
    .contact-card { background: #f0f4f8; border-left: 4px solid #003049; padding: 15px; border-radius: 5px; margin: 5px 0; }
    .linha-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-baseline { background: #e3f2fd; color: #1565c0; }
    .badge-mline { background: #e8f5e9; color: #2e7d32; }
    .badge-widegap { background: #fff3e0; color: #e65100; }
    .badge-semiwelded { background: #fce4ec; color: #c62828; }
    .angulo-badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: bold; background: #e3f2fd; color: #1565c0; }
    .gaxeta-badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: bold; background: #e8f5e9; color: #2e7d32; }
    .passe-badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: bold; background: #fff3e0; color: #e65100; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1>AlfaVed Engenharia Termica</h1>
        <h3>Dimensionador Inteligente de Trocadores de Calor</h3>
        <p>TS6M / TS20M | Vapor kg/h | Angulo H/L/Mista | Gaxeta | Passe | Conexoes</p>
    </div>
    """, unsafe_allow_html=True)

    input_col, result_col = st.columns([1, 1.2], gap='large')

    with input_col:
        st.markdown('### DADOS DE ENTRADA')

        with st.expander('Identificacao do Projeto', expanded=True):
            tag = st.text_input('Tag do Equipamento', 'TC-101', key='tag')
            projeto = st.text_input('Nome do Projeto', 'PRJ-ALFAVED-2026', key='projeto')

        with st.expander('Selecao do Modelo', expanded=True):
            cat_sel = st.selectbox('Filtrar por Categoria',
                                    ['Todos', 'BaseLine', 'M-line', 'WideGap', 'Semi-Welded'],
                                    key='cat_sel')
            if cat_sel == 'Todos':
                modelos_filt = list(BANCO_MODELOS.keys())
            else:
                modelos_filt = [m for m, d in BANCO_MODELOS.items() if d['linha'] == cat_sel]

            modelo = st.selectbox('Modelo Alfa Laval', modelos_filt, key='modelo')
            d_mod = BANCO_MODELOS[modelo]
            linha_mod = d_mod['linha']
            badge_class = {'BaseLine': 'badge-baseline', 'M-line': 'badge-mline',
                           'WideGap': 'badge-widegap', 'Semi-Welded': 'badge-semiwelded'}.get(linha_mod, 'badge-baseline')
            st.markdown(f"<span class='linha-badge {badge_class}'>{linha_mod}</span> | "
                        f"Tipo: <strong>{d_mod['tipo']}</strong> | "
                        f"Pmax: <strong>{d_mod['pressao_max']} bar</strong> | "
                        f"Tmax: <strong>{d_mod['temp_max']}C</strong>",
                        unsafe_allow_html=True)

            if d_mod.get('canal_soldado'):
                st.caption(f"Canal soldado: {d_mod['canal_soldado']}")
            if d_mod.get('canal'):
                st.caption(f"Configuracoes de canal: {d_mod['canal']}")

            angulo_sel = st.selectbox(
                'Angulo da Placa',
                ['Automatico (Recomendado)', 'H (45°)', 'L (60°)', 'Mista (HL = 52.5°)'],
                key='angulo',
                help='Automatico: baseado em Reynolds. H=alta turbulencia, L=baixa pressao, Mista=compromisso.'
            )
            if angulo_sel != 'Automatico (Recomendado)':
                cfg = CONFIG_ANGULOS[angulo_sel]
                st.info(f"{cfg['descricao']} | Multiplicador U: {cfg['multiplicador_u']}x | Queda de pressao: {cfg['queda_pressao']}")

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
            res = calculate_dimensionamento(
                produto, servico, modelo, vazao_p,
                t_in_p, t_out_p, t_in_s, t_out_s, angulo_sel
            )
            st.session_state.res = res
            st.session_state.inputs = {
                'modelo': modelo, 'tag': tag, 'projeto': projeto, 'produto': produto,
                'servico': servico, 't_in_p': t_in_p, 't_out_p': t_out_p,
                't_in_s': t_in_s, 't_out_s': t_out_s, 'vazao_p': vazao_p,
                'angulo_sel': angulo_sel
            }
            st.success('Calculo estruturado com sucesso!')
            st.rerun()

    with result_col:
        if 'res' in st.session_state:
            res = st.session_state.res
            inp = st.session_state.inputs

            st.markdown('### RESULTADOS DO DIMENSIONAMENTO')

            # Alertas de viabilidade
            if res['alertas']:
                for alerta in res['alertas']:
                    st.error(f'⚠ {alerta}')

            # KPIs
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
                st.metric('Consumo de Vapor', f'{res["vapor_kg_h"]:.2f} kg/h', f'hfg = {res["h_fg"]:.1f} kJ/kg')
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

            # Analise de Turbulencia
            st.markdown('#### Analise de Turbulencia')
            t1, t2 = st.columns(2)
            with t1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('**Lado Produto**')
                st.metric('Reynolds', f'{res["re_prod"]:.0f}', res['regime_prod'])
                st.caption(res['desc_reg_prod'])
                st.markdown('</div>', unsafe_allow_html=True)
            with t2:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('**Lado Servico**')
                st.metric('Reynolds', f'{res["re_serv"]:.0f}', res['regime_serv'])
                st.caption(res['desc_reg_serv'])
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

            # Configuracao de Placa
            st.markdown('#### Configuracao da Placa')
            cfg = CONFIG_ANGULOS[res['angulo']]
            ang_col1, ang_col2 = st.columns(2)
            with ang_col1:
                st.markdown(f"<span class='angulo-badge'>{res['angulo']}</span>", unsafe_allow_html=True)
                if inp['angulo_sel'] == 'Automatico (Recomendado)':
                    st.caption('Selecionado automaticamente via Reynolds')
                else:
                    st.caption('Selecao manual do usuario')
            with ang_col2:
                st.write(f"**Multiplicador U:** {res['mult_u']:.2f}x")
                st.write(f"**U Base:** {res['u_base']:.0f} W/m²K")
                st.write(f"**U Final:** {res['u_final']:.0f} W/m²K")
                st.write(f"**LMTD:** {res['lmtd']:.2f} C")

            st.divider()

            # Material da Gaxeta
            st.markdown('#### Material da Gaxeta Recomendado')
            st.markdown(f"<span class='gaxeta-badge'>{res['gaxeta']}</span>", unsafe_allow_html=True)
            st.caption(res['gaxeta_just'])
            st.info('A gaxeta e selecionada com base na temperatura maxima, compatibilidade quimica com os fluidos e aplicacao.')

            st.divider()

            # Arranjo de Passe
            st.markdown('#### Arranjo de Passe')
            st.markdown(f"<span class='passe-badge'>{res['arranjo_passe']['codigo']} - {res['arranjo_passe']['nome']}</span>", unsafe_allow_html=True)
            st.write(f"**Descricao:** {res['arranjo_passe']['descricao']}")
            st.write(f"**Placas por pass:** {res['arranjo_passe']['placas_pass']}")
            st.caption(res['arranjo_passe']['justificativa'])

            st.divider()

            # Conexoes
            st.markdown('#### Configuracao de Conexoes')
            st.markdown('<div class="result-success">', unsafe_allow_html=True)
            st.write(f"**Entrada Produto:** {res['conexoes']['produto_entrada']}")
            st.write(f"**Saida Produto:** {res['conexoes']['produto_saida']}")
            st.write(f"**Entrada Servico:** {res['conexoes']['servico_entrada']}")
            st.write(f"**Saida Servico:** {res['conexoes']['servico_saida']}")
            st.caption(res['conexoes']['descricao'])
            st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

            # Queda de Pressao
            st.markdown('#### Queda de Pressao Estimada')
            qp1, qp2 = st.columns(2)
            with qp1:
                st.metric('Lado Produto', f'{res["dp_prod"]:.3f} bar')
            with qp2:
                st.metric('Lado Servico', f'{res["dp_serv"]:.3f} bar')
            st.caption('Valores estimados baseados em correlacoes de engenharia. Para projeto definitivo, consulte o software oficial Alfa Laval.')

            st.divider()

            # Datasheet
            st.markdown('#### Datasheet Tecnico')

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                pdf_bytes = build_pdf(res, inp['modelo'], inp['tag'], inp['projeto'],
                                      inp['produto'], inp['servico'], inp['t_in_p'],
                                      inp['t_out_p'], inp['t_in_s'], inp['t_out_s'],
                                      inp['vazao_p'], inp['angulo_sel'])
                st.download_button(
                    label='📥 Download PDF',
                    data=pdf_bytes,
                    file_name=f'AlfaVed_{inp["tag"]}.pdf',
                    mime='application/pdf',
                    use_container_width=True
                )

            with col_btn2:
                if st.toggle('👁️ Visualizar Datasheet', key='ver_ds'):
                    pass

            if st.session_state.get('ver_ds', False):
                st.markdown('---')
                st.markdown('**DATASHEET PREVIEW**')
                st.write(f"**Modelo:** {inp['modelo']} | **Tag:** {inp['tag']}")
                st.write(f"**Angulo:** {res['angulo']} | **Passe:** {res['arranjo_passe']['codigo']}")
                st.write(f"**Gaxeta:** {res['gaxeta']}")
                st.write(f"**Carga:** {res['carga_kw']:.2f} kW | **Area:** {res['area_req']:.2f} m2 | **Placas:** {res['num_placas']}")
                if res['is_vapor']:
                    st.write(f"**Vapor:** {res['vapor_kg_h']:.2f} kg/h")
                st.write(f"**Conexoes:** Produto: {res['conexoes']['produto_entrada']} -> {res['conexoes']['produto_saida']}")
                st.write(f"**Conexoes:** Servico: {res['conexoes']['servico_entrada']} -> {res['conexoes']['servico_saida']}")
                st.write('---')

            st.divider()
            st.markdown('#### Responsaveis Tecnicos')
            st.markdown('<div class="contact-card"><strong>Vitor Soares</strong> - Responsavel pelo Projeto<br>E-mail: engenharia@alfaved.com.br | Tel: (18) 99669-7330</div>', unsafe_allow_html=True)
            st.markdown('<div class="contact-card"><strong>Jhonatan Dias Dejato</strong> - Diretor de Engenharia<br>E-mail: jhonatan@alfaved.com.br | Tel: (18) 99628-8714</div>', unsafe_allow_html=True)

        else:
            st.info('Preencha os dados de entrada e clique em CALCULAR DIMENSIONAMENTO')

if __name__ == '__main__':
    main()
