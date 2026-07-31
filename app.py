import streamlit as st
import json
import math
import io
import google.genai as genai

# Configuração da página Web do Software AlfaVed
st.set_page_config(page_title="AlfaVed Engenharia", page_icon="▲", layout="wide")

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# ==========================================
# BANCO COMPLETO DE MODELOS ALFA LAVAL
# ==========================================

BANCO_MODELOS_GAXETADOS = {
    "Alfa Laval M3 (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.03, "U_base": 3800, "pressao_max": 25, "temp_max": 120, "dh": 0.003},
    "Alfa Laval TL3 (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.06, "U_base": 3900, "pressao_max": 25, "temp_max": 120, "dh": 0.004},
    "Alfa Laval M6 (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.14, "U_base": 4200, "pressao_max": 25, "temp_max": 130, "dh": 0.005},
    "Alfa Laval M6-M (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.16, "U_base": 4250, "pressao_max": 30, "temp_max": 140, "dh": 0.005},
    "Alfa Laval TL6 (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.21, "U_base": 4300, "pressao_max": 30, "temp_max": 140, "dh": 0.006},
    "Alfa Laval M10 (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.24, "U_base": 4500, "pressao_max": 30, "temp_max": 160, "dh": 0.006},
    "Alfa Laval M10-M (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.34, "U_base": 4550, "pressao_max": 35, "temp_max": 170, "dh": 0.007},
    "Alfa Laval TL10 (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.46, "U_base": 4600, "pressao_max": 35, "temp_max": 170, "dh": 0.007},
    "Alfa Laval M15 (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.61, "U_base": 4700, "pressao_max": 35, "temp_max": 180, "dh": 0.008},
    "Alfa Laval M15-M (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.509, "U_base": 4700, "pressao_max": 35, "temp_max": 180, "dh": 0.008},
    "Alfa Laval T20B (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.46, "U_base": 4600, "pressao_max": 35, "temp_max": 180, "dh": 0.007},
    "Alfa Laval MA30 (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.80, "U_base": 4800, "pressao_max": 25, "temp_max": 210, "dh": 0.009},
    "Alfa Laval MA30S (Gaxetado)": {"tipo": "gaxetado", "area_placa": 0.85, "U_base": 4800, "pressao_max": 25, "temp_max": 210, "dh": 0.009},
    "Alfa Laval WideGap 350S (Gaxetado)": {"tipo": "gaxetado", "area_placa": 1.20, "U_base": 4900, "pressao_max": 25, "temp_max": 210, "dh": 0.010},
}

BANCO_MODELOS_SEMI_SOLDADOS = {
    "Alfa Laval M10BW (Semi-Soldado)": {"tipo": "semi-soldado", "area_placa": 0.24, "U_base": 4600, "pressao_max": 25, "temp_max": 150, "dh": 0.006},
    "Alfa Laval T20BW (Semi-Soldado)": {"tipo": "semi-soldado", "area_placa": 0.75, "U_base": 4900, "pressao_max": 40, "temp_max": 180, "dh": 0.008},
    "Alfa Laval M20MW (Semi-Soldado)": {"tipo": "semi-soldado", "area_placa": 0.95, "U_base": 4700, "pressao_max": 40, "temp_max": 180, "dh": 0.008},
    "Alfa Laval MK15BW (Semi-Soldado)": {"tipo": "semi-soldado", "area_placa": 0.58, "U_base": 4650, "pressao_max": 25, "temp_max": 150, "dh": 0.007},
    "Alfa Laval A15BW (Semi-Soldado)": {"tipo": "semi-soldado", "area_placa": 0.55, "U_base": 4600, "pressao_max": 30, "temp_max": 160, "dh": 0.007},
}

BANCO_MODELOS = {**BANCO_MODELOS_GAXETADOS, **BANCO_MODELOS_SEMI_SOLDADOS}

# BANCO DE DADOS DE PRODUTOS/FLUIDOS
BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "viscosidade": 0.89, "densidade": 1000},
    "Leite Integral": {"cp": 3.89, "viscosidade": 2.1, "densidade": 1030},
    "Leite Desnatado": {"cp": 3.95, "viscosidade": 1.5, "densidade": 1020},
    "Suco de Laranja": {"cp": 3.75, "viscosidade": 3.5, "densidade": 1040},
    "Suco de Maçã": {"cp": 3.70, "viscosidade": 2.8, "densidade": 1035},
    "Oleo Vegetal": {"cp": 1.97, "viscosidade": 50.0, "densidade": 920},
    "Oleo Mineral": {"cp": 1.88, "viscosidade": 100.0, "densidade": 880},
    "Melado": {"cp": 2.80, "viscosidade": 150.0, "densidade": 1380},
    "Cerveja": {"cp": 4.10, "viscosidade": 1.5, "densidade": 1010},
    "Vinho": {"cp": 3.85, "viscosidade": 1.2, "densidade": 1000},
    "Chocolate Quente": {"cp": 3.50, "viscosidade": 8.0, "densidade": 1050}
}

# BANCO DE FLUIDOS DE SERVIÇO (Resfriamento/Aquecimento)
BANCO_SERVICOS = {
    "Agua Fria": {"cp": 4.18, "viscosidade": 0.89, "densidade": 1000},
    "Agua Gelada": {"cp": 4.18, "viscosidade": 0.89, "densidade": 1000},
    "Agua Morna": {"cp": 4.18, "viscosidade": 0.65, "densidade": 995},
    "Agua Quente": {"cp": 4.18, "viscosidade": 0.35, "densidade": 960},
    "Vapor Saturado": {"cp": 2.0, "viscosidade": 0.015, "densidade": 0.6},
    "Oleo Termico": {"cp": 2.50, "viscosidade": 5.0, "densidade": 850},
    "Refrigerante R22": {"cp": 1.45, "viscosidade": 0.018, "densidade": 450},
    "Refrigerante R410A": {"cp": 1.60, "viscosidade": 0.020, "densidade": 480},
    "Refrigerante R134a": {"cp": 1.52, "viscosidade": 0.019, "densidade": 470},
    "Amonia Liquida": {"cp": 4.70, "viscosidade": 0.25, "densidade": 682},
    "Ar Comprimido": {"cp": 1.01, "viscosidade": 0.018, "densidade": 1.2}
}

# CONFIGURAÇÃO DE ÂNGULOS DE PLACA - PADRÃO ALFA LAVAL
ANGULOS_PLACA = {
    "45 HT": {
        "descricao": "45° High Theta - Alta Eficiência Térmica",
        "multiplicador_u": 1.4,
        "turbulencia": "Alta",
        "queda_pressao": "Alta",
        "reynolds_min": 0,
        "aplicacao": "Máxima transferência térmica, vazões menores, pressão baixa aceitável"
    },
    "60 LT": {
        "descricao": "60° Low Theta - Baixa Queda de Pressão",
        "multiplicador_u": 1.0,
        "turbulencia": "Moderada",
        "queda_pressao": "Baixa",
        "reynolds_min": 1500,
        "aplicacao": "Eficiência balanceada, vazões maiores, pressão crítica"
    }
}

# Constantes de engenharia
AREA_CANAL_DEFAULT = 0.0001  # m² - área transversal do canal
VISCOSIDADE_CONVERSION = 0.001  # cP para Pa·s
REYNOLDS_LAMINAR_LIMIT = 500
REYNOLDS_TURBULENT_LIMIT = 2000
TEMP_MIN_VALIDA = -50.0  # °C
TEMP_MAX_VALIDA = 300.0  # °C

styles_doc = getSampleStyleSheet()
st_tit = ParagraphStyle('T1', parent=styles_doc['Heading1'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor("#0d1b2a"))
st_sub = ParagraphStyle('T2', parent=styles_doc['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#d90429"), spaceAfter=15)
st_h2 = ParagraphStyle('T3', parent=styles_doc['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#003049"), spaceBefore=10, spaceAfter=5)
st_h3 = ParagraphStyle('T3b', parent=styles_doc['Heading3'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#003049"), spaceBefore=8, spaceAfter=4)
st_body = ParagraphStyle('T4', parent=styles_doc['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#222222"), leading=12)
st_th = ParagraphStyle('T5', parent=styles_doc['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)
st_tc = ParagraphStyle('T6', parent=styles_doc['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#333333"))

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
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.HexColor("#666666"))
            self.drawString(54, 25, "AlfaVed Solucoes Industriais - Engenharia Termica")
            largura_real = letter[0] if isinstance(letter, (list, tuple)) else letter
            self.drawRightString(largura_real - 54, 25, f"Pagina {self._pageNumber} de {num_pages}")
            super().showPage()
        super().save()


def calculate_reynolds(vazao_kg_h: float, viscosidade: float, densidade: float, dh: float) -> float:
    if vazao_kg_h <= 0 or viscosidade <= 0 or densidade <= 0:
        return 0
    vazao_m3_s = (vazao_kg_h / 3600.0) / densidade
    area_canal = AREA_CANAL_DEFAULT
    u = vazao_m3_s / area_canal
    viscosidade_pa_s = viscosidade * VISCOSIDADE_CONVERSION
    reynolds = (densidade * u * dh) / viscosidade_pa_s
    return reynolds


def classificar_turbulencia(reynolds: float) -> tuple:
    if reynolds < REYNOLDS_LAMINAR_LIMIT:
        return ("Laminar", "Regime laminar - Transferência de calor limitada")
    elif reynolds < REYNOLDS_TURBULENT_LIMIT:
        return ("Transicional", "Transição laminar-turbulento - Eficiência moderada")
    else:
        return ("Turbulento", "Regime turbulento - Ótima eficiência de transferência")


def recomendar_angulo_placa(reynolds_prod: float, reynolds_serv: float, pressao_max: float) -> tuple:
    reynolds_min = min(reynolds_prod, reynolds_serv)
    
    if reynolds_min < REYNOLDS_LAMINAR_LIMIT:
        return ("45 HT", ANGULOS_PLACA["45 HT"]["multiplicador_u"],
                "Reynolds baixo detectado. Placa 45 HT recomendada para máxima turbulência e eficiência térmica.")
    elif reynolds_min > REYNOLDS_TURBULENT_LIMIT:
        return ("60 LT", ANGULOS_PLACA["60 LT"]["multiplicador_u"],
                "Reynolds alto (turbulento). Placa 60 LT recomendada para melhor eficiência energética com menor queda de pressão.")
    else:
        return ("45 HT", ANGULOS_PLACA["45 HT"]["multiplicador_u"],
                "Reynolds transicional. Placa 45 HT recomendada para otimizar transferência térmica.")


def get_viscosity_factor(dados_fluido: dict) -> float:
    viscosidade = dados_fluido.get("viscosidade", 1.0)
    if viscosidade <= 0:
        return 1.0
    if viscosidade == BANCO_FLUIDOS["Agua"]["viscosidade"]:
        return 1.0
    return 1.0 / math.sqrt(viscosidade)


def calculate_lmtd(dt1: float, dt2: float) -> float:
    dt1_abs = abs(dt1)
    dt2_abs = abs(dt2)
    if dt1_abs < 1e-6 and dt2_abs < 1e-6:
        return 1.0
    if abs(dt1_abs - dt2_abs) < 1e-6:
        return max(dt1_abs, dt2_abs, 1.0)
    if dt1_abs > 0 and dt2_abs > 0:
        return abs((dt1_abs - dt2_abs) / math.log(dt1_abs / dt2_abs))
    return max(dt1_abs, dt2_abs, 1.0)


def calculate_dimensionamento(produto: str, dados_fluido: dict, modelo: str, dados_modelo: dict, t_in_prod: float, t_out_prod: float, t_in_serv: float, t_out_serv: float, vazao_prod: float, dados_servico: dict) -> dict:
    cp_prod = dados_fluido["cp"]
    cp_serv = dados_servico["cp"]
    densidade_prod = dados_fluido.get("densidade", 1000)
    densidade_serv = dados_servico.get("densidade", 1000)
    viscosidade_prod = dados_fluido.get("viscosidade", 1.0)
    viscosidade_serv = dados_servico.get("viscosidade", 1.0)
    area_por_placa = dados_modelo["area_placa"]
    pressao_max = dados_modelo.get("pressao_max", 25)
    dh = dados_modelo.get("dh", 0.005)
    
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
    
    U_adotado = dados_modelo["U_base"] * fator_viscosidade * multiplicador_u
    
    dt1 = t_in_prod - t_out_serv
    dt2 = t_out_prod - t_in_serv
    lmtd = calculate_lmtd(dt1, dt2)
    
    area_m2 = (carga_kw * 1000.0) / (U_adotado * lmtd) if lmtd > 0 else 0.0
    
    placas = math.ceil(area_m2 / area_por_placa) + 2
    if placas % 2 != 0:
        placas += 1
    
    return {
        "carga_kw": carga_kw,
        "vazao_serv": vazao_serv,
        "lmtd": lmtd,
        "area_m2": area_m2,
        "placas": placas,
        "area_por_placa": area_por_placa,
        "U_adotado": U_adotado,
        "U_base": dados_modelo["U_base"],
        "fator_viscosidade": fator_viscosidade,
        "multiplicador_placa": multiplicador_u,
        "reynolds_prod": reynolds_prod,
        "reynolds_serv": reynolds_serv,
        "regime_prod": regime_prod,
        "regime_serv": regime_serv,
        "desc_prod": desc_prod,
        "desc_serv": desc_serv,
        "tipo_placa": tipo_placa,
        "justificativa_placa": justificativa_angulo
    }


def generate_parecer_ia(modelo: str, tag: str, projeto: str, produto: str, servico: str, vazao_prod: float, resultados: dict, tipo_modelo: str) -> str:
    contexto = {
        "dados": {
            "Modelo": modelo,
            "Tipo": tipo_modelo,
            "Tag": tag,
            "Projeto": projeto,
            "Produto": produto,
            "Servico": servico,
            "Vazao": vazao_prod
        },
        "turbulencia": {
            "Reynolds_Produto": round(resultados["reynolds_prod"], 0),
            "Regime_Produto": resultados["regime_prod"],
            "Reynolds_Servico": round(resultados["reynolds_serv"], 0),
            "Regime_Servico": resultados["regime_serv"]
        },
        "configuracao_recomendada": {
            "Tipo_Placa": resultados["tipo_placa"]
        },
        "calculado": {
            "kw": round(resultados["carga_kw"], 2),
            "placas": resultados["placas"],
            "area": round(resultados["area_m2"], 2),
            "area_unitaria_placa": resultados["area_por_placa"]
        }
    }

    prompt = (
        "Atue como Engenheiro Quimico Senior Especialista em Trocadores de Calor da AlfaVed. "
        "Analise: " + json.dumps(contexto) +
        ". Escreva um Parecer Tecnico Descritivo (maximo 180 palavras) focando em: "
        "1) Material das gaxetas adequado para " + produto + " e " + servico + "; "
        "2) Análise do regime de turbulência (Reynolds) para eficiência térmica; "
        "3) Configuração recomendada com placa " + resultados["tipo_placa"] + "; "
        "4) Risco de incrustação e avaliação se o arranjo de " + str(resultados["placas"]) +
        " placas do modelo " + modelo + " atende com segurança. "
        "Retorne APENAS o texto corrido do parecer, sem markdown e sem asteriscos."
    )

    try:
        chave_segura = st.secrets.get("GEMINI_API_KEY")
        if not chave_segura:
            raise ValueError("Chave API Gemini não configurada")
        
        client = genai.Client(api_key=chave_segura)
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=prompt, 
            config=dict(temperature=0.2)
        )
        return response.text.strip().replace("*", "")
    except KeyError:
        return (
            f"Parecer tecnico AlfaVed local. Processamento para {produto} em {modelo} ({tipo_modelo}) "
            f"com servico {servico} indica demanda termica de {resultados['carga_kw']:.2f} kW. "
            f"Reynolds Produto: {resultados['reynolds_prod']:.0f} ({resultados['regime_prod']}). "
            f"Reynolds Servico: {resultados['reynolds_serv']:.0f} ({resultados['regime_serv']}). "
            f"Placa recomendada: {resultados['tipo_placa']} - {resultados['justificativa_placa']} "
            f"Gaxetas EPDM para laticinios ou NBR para oleos conforme compatibilidade. "
            f"Arranjo de {resultados['placas']} placas com eficiência garantida. Equipamento homologado."
        )
    except Exception as e:
        return (
            f"Erro ao gerar parecer IA: {str(e)}. "
            f"Processamento local para {produto} em {modelo} ({tipo_modelo}) "
            f"com servico {servico} indica demanda termica de {resultados['carga_kw']:.2f} kW. "
            f"Reynolds Produto: {resultados['reynolds_prod']:.0f} ({resultados['regime_prod']}). "
            f"Reynolds Servico: {resultados['reynolds_serv']:.0f} ({resultados['regime_serv']}). "
            f"Placa recomendada: {resultados['tipo_placa']} - {resultados['justificativa_placa']} "
            f"Gaxetas EPDM para laticinios ou NBR para oleos conforme compatibilidade. "
            f"Arranjo de {resultados['placas']} placas com eficiência garantida. Equipamento homologado."
        )


def build_pdf(modelo: str, tag: str, projeto: str, produto: str, servico: str, t_in_prod: float, t_out_prod: float, t_in_serv: float, t_out_serv: float, vazao_prod: float, vazao_serv: float, resultados: dict, parecer_ia: str, tipo_modelo: str) -> bytes:
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = [
        Paragraph("AlfaVed Solucoes Industriais", st_tit),
        Paragraph("DATASHEET TECNICO - ENGENHARIA ASSISTIDA POR IA", st_sub),
        Spacer(1, 10)
    ]

    story.append(Paragraph("1. Informacoes Gerais do Projeto", st_h2))
    story.append(
        Table([
            [Paragraph("Item", st_th), Paragraph("Especificacao", st_th)],
            [Paragraph("Modelo Selecionado", st_tc), Paragraph(modelo, st_tc)],
            [Paragraph("Tipo de Modelo", st_tc), Paragraph(tipo_modelo, st_tc)],
            [Paragraph("Tag", st_tc), Paragraph(tag, st_tc)],
            [Paragraph("Projeto", st_tc), Paragraph(projeto, st_tc)]
        ])
    )

    story.append(Paragraph("2. Parametros Operacionais Processados", st_h2))
    story.append(
        Table([
            [Paragraph("Propriedade", st_th), Paragraph("Lado do Produto", st_th), Paragraph("Lado do Servico", st_th)],
            [Paragraph("Fluido", st_tc), Paragraph(produto, st_tc), Paragraph(servico, st_tc)],
            [Paragraph("Temp Entrada", st_tc), Paragraph(f"{t_in_prod} °C", st_tc), Paragraph(f"{t_in_serv} °C", st_tc)],
            [Paragraph("Temp Saida", st_tc), Paragraph(f"{t_out_prod} °C", st_tc), Paragraph(f"{t_out_serv} °C", st_tc)],
            [Paragraph("Vazao Massica", st_tc), Paragraph(f"{vazao_prod} kg/h", st_tc), Paragraph(f"{vazao_serv:.1f} kg/h", st_tc)]
        ])
    )

    story.append(Paragraph("3. Analise de Turbulencia - Numero de Reynolds", st_h2))
    story.append(
        Table([
            [Paragraph("Parâmetro", st_th), Paragraph("Lado Produto", st_th), Paragraph("Lado Serviço", st_th)],
            [Paragraph("Número de Reynolds", st_tc), Paragraph(f"{resultados['reynolds_prod']:.0f}", st_tc), Paragraph(f"{resultados['reynolds_serv']:.0f}", st_tc)],
            [Paragraph("Regime Escoamento", st_tc), Paragraph(resultados['regime_prod'], st_tc), Paragraph(resultados['regime_serv'], st_tc)],
            [Paragraph("Descrição", st_tc), Paragraph(resultados['desc_prod'], st_tc), Paragraph(resultados['desc_serv'], st_tc)]
        ])
    )

    story.append(Paragraph("4. Configuracao de Placa Alfa Laval Recomendada", st_h2))
    placa_info = ANGULOS_PLACA[resultados["tipo_placa"]]
    story.append(
        Table([
            [Paragraph("Especificacao", st_th), Paragraph("Valor", st_th)],
            [Paragraph("Tipo de Placa", st_tc), Paragraph(resultados['tipo_placa'], st_tc)],
            [Paragraph("Descricao", st_tc), Paragraph(placa_info['descricao'], st_tc)],
            [Paragraph("Turbulência", st_tc), Paragraph(placa_info['turbulencia'], st_tc)],
            [Paragraph("Queda de Pressao", st_tc), Paragraph(placa_info['queda_pressao'], st_tc)],
            [Paragraph("Justificativa", st_tc), Paragraph(resultados['justificativa_placa'], st_tc)]
        ])
    )

    story.append(Paragraph("5. Resultados do Dimensionamento Hidro-Termico", st_h2))
    story.append(
        Table([
            [Paragraph("Grandeza de Engenharia", st_th), Paragraph("Valor Calculado", st_th)],
            [Paragraph("Carga Termica", st_tc), Paragraph(f"{resultados['carga_kw']:.2f} kW", st_tc)],
            [Paragraph("LMTD", st_tc), Paragraph(f"{resultados['lmtd']:.2f} °C", st_tc)],
            [Paragraph("Coeficiente U Base", st_tc), Paragraph(f"{resultados['U_base']:.0f} W/m²K", st_tc)],
            [Paragraph("Fator Viscosidade", st_tc), Paragraph(f"{resultados['fator_viscosidade']:.3f}", st_tc)],
            [Paragraph("Multiplicador Placa", st_tc), Paragraph(f"{resultados['multiplicador_placa']:.2f}x", st_tc)],
            [Paragraph("Coeficiente U Adotado", st_tc), Paragraph(f"{resultados['U_adotado']:.0f} W/m²K", st_tc)],
            [Paragraph("Area Efetiva Requerida", st_tc), Paragraph(f"{resultados['area_m2']:.2f} m²", st_tc)],
            [Paragraph("Area por Placa", st_tc), Paragraph(f"{resultados['area_por_placa']} m²", st_tc)],
            [Paragraph("Quantidade de Placas", st_tc), Paragraph(f"{resultados['placas']} placas", st_tc)]
        ])
    )

    for item in story:
        if isinstance(item, Table):
            item.setStyle(
                TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0d1b2a")),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5)
                ])
            )

    story.append(Paragraph("6. Parecer Técnico e Memorial Descritivo (AlfaVed GenAI)", st_h2))
    story.append(Paragraph(parecer_ia, st_body))

    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()
    return pdf_data


def main() -> None:
    # CSS personalizado
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #003049 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .section-card {
        background-color: #f8f9fa;
        border-left: 4px solid #0d1b2a;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .metric-box {
        background: linear-gradient(135deg, #003049 0%, #1f5a6f 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }
    .result-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
    }
    .result-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>▲ AlfaVed Engenharia Térmica</h1>
        <h3>Dimensionador Inteligente de Trocadores de Calor</h3>
        <p>Análise de Turbulência | Recomendação de Placas | Parecer Técnico com IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout: Input à esquerda, Resultados à direita
    input_col, result_col = st.columns([1, 1.2], gap="large")
    
    # ==================== COLUNA DE ENTRADA ====================
    with input_col:
        st.markdown("### 📋 DADOS DE PROJETO")
        
        with st.form("form_dimensionamento", clear_on_submit=False):
            
            # Seção Projeto
            st.markdown("#### 📌 Informações do Projeto")
            tag = st.text_input("Tag do Equipamento", "TC-101")
            projeto = st.text_input("Número do Projeto", "PRJ-ALFAVED-2026")
            
            st.divider()
            
            # Seção Modelo
            st.markdown("#### ⚙️ Seleção do Modelo")
            modelo = st.selectbox("Modelo Alfa Laval", list(BANCO_MODELOS.keys()))
            tipo_modelo = BANCO_MODELOS[modelo]["tipo"].upper()
            st.caption(f"Tipo: **{tipo_modelo}** | Pressão Máx: **{BANCO_MODELOS[modelo]['pressao_max']} bar**")
            
            st.divider()
            
            # Seção Produto
            st.markdown("#### 🔴 Lado do Produto")
            col_prod1, col_prod2 = st.columns(2)
            with col_prod1:
                produto = st.selectbox("Fluido do Produto", list(BANCO_FLUIDOS.keys()))
            with col_prod2:
                vazao_prod = st.number_input("Vazão (kg/h)", value=5000.0, min_value=1.0)
            
            col_temp_prod1, col_temp_prod2 = st.columns(2)
            with col_temp_prod1:
                t_in_prod = st.number_input("Temp. Entrada (°C)", value=90.0)
            with col_temp_prod2:
                t_out_prod = st.number_input("Temp. Saída (°C)", value=8.0)
            
            st.divider()
            
            # Seção Serviço
            st.markdown("#### 🔵 Lado do Serviço")
            servico = st.selectbox("Fluido de Serviço", list(BANCO_SERVICOS.keys()))
            
            col_temp_serv1, col_temp_serv2 = st.columns(2)
            with col_temp_serv1:
                t_in_serv = st.number_input("Temp. Entrada (°C)", value=0.0)
            with col_temp_serv2:
                t_out_serv = st.number_input("Temp. Saída (°C)", value=12.0)
            
            st.divider()
            
            # Botão de Cálculo
            submitted = st.form_submit_button("🔄 CALCULAR DIMENSIONAMENTO", use_container_width=True, type="primary")
            
        
        # ==================== PROCESSAMENTO E CÁLCULO ====================
        if submitted:
            # Validação de entrada
            try:
                # Validar temperaturas
                if not (TEMP_MIN_VALIDA <= t_in_prod <= TEMP_MAX_VALIDA):
                    st.error(f"Temperatura de entrada do produto fora de faixa válida ({TEMP_MIN_VALIDA} a {TEMP_MAX_VALIDA}°C)")
                    st.stop()
                
                if not (TEMP_MIN_VALIDA <= t_out_prod <= TEMP_MAX_VALIDA):
                    st.error(f"Temperatura de saída do produto fora de faixa válida ({TEMP_MIN_VALIDA} a {TEMP_MAX_VALIDA}°C)")
                    st.stop()
                
                if not (TEMP_MIN_VALIDA <= t_in_serv <= TEMP_MAX_VALIDA):
                    st.error(f"Temperatura de entrada do serviço fora de faixa válida ({TEMP_MIN_VALIDA} a {TEMP_MAX_VALIDA}°C)")
                    st.stop()
                
                if not (TEMP_MIN_VALIDA <= t_out_serv <= TEMP_MAX_VALIDA):
                    st.error(f"Temperatura de saída do serviço fora de faixa válida ({TEMP_MIN_VALIDA} a {TEMP_MAX_VALIDA}°C)")
                    st.stop()
                
                # Validar diferença de temperaturas
                if abs(t_in_prod - t_out_prod) < 0.1:
                    st.error("Temperaturas de entrada e saída do produto devem ser diferentes")
                    st.stop()
                
                if abs(t_in_serv - t_out_serv) < 0.1:
                    st.error("Temperaturas de entrada e saída do serviço devem ser diferentes")
                    st.stop()
                
                # Validar vazão
                if vazao_prod <= 0:
                    st.error("Vazão do produto deve ser maior que zero")
                    st.stop()
                
            except Exception as e:
                st.error(f"Erro na validação: {str(e)}")
                st.stop()
            
            dados_fluido = BANCO_FLUIDOS[produto]
            dados_modelo = BANCO_MODELOS[modelo]
            dados_servico = BANCO_SERVICOS[servico]
            
            resultados = calculate_dimensionamento(
                produto, dados_fluido, modelo, dados_modelo,
                t_in_prod, t_out_prod, t_in_serv, t_out_serv,
                vazao_prod, dados_servico
            )
            
            # Armazenar resultados na sessão com prefixos para evitar conflito
            try:
                st.session_state.calc_resultados = resultados
                st.session_state.calc_modelo = str(modelo)
                st.session_state.calc_tipo_modelo = str(tipo_modelo)
                st.session_state.calc_tag = str(tag)
                st.session_state.calc_projeto = str(projeto)
                st.session_state.calc_produto = str(produto)
                st.session_state.calc_servico = str(servico)
                st.session_state.calc_t_in_prod = float(t_in_prod)
                st.session_state.calc_t_out_prod = float(t_out_prod)
                st.session_state.calc_t_in_serv = float(t_in_serv)
                st.session_state.calc_t_out_serv = float(t_out_serv)
                st.session_state.calc_vazao_prod = float(vazao_prod)
                
                st.success("✅ Cálculo realizado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao armazenar dados na sessão: {str(e)}")
                st.stop()
    
    # ==================== COLUNA DE RESULTADOS ====================
    with result_col:
        if 'calc_resultados' in st.session_state:
            resultados = st.session_state.calc_resultados
            
            st.markdown("### 📊 RESULTADOS DO DIMENSIONAMENTO")
            
            # KPIs principais
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            
            with kpi_col1:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric("Carga Térmica", f"{resultados['carga_kw']:.2f} kW")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with kpi_col2:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric("Área Requerida", f"{resultados['area_m2']:.2f} m²")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with kpi_col3:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric("Quantidade Placas", f"{resultados['placas']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Análise de Turbulência
            st.markdown("#### 🌊 Análise de Turbulência")
            
            turb_col1, turb_col2 = st.columns(2)
            
            with turb_col1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown("**Lado Produto**")
                st.metric("Reynolds", f"{resultados['reynolds_prod']:.0f}", resultados['regime_prod'])
                st.caption(resultados['desc_prod'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with turb_col2:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown("**Lado Serviço**")
                st.metric("Reynolds", f"{resultados['reynolds_serv']:.0f}", resultados['regime_serv'])
                st.caption(resultados['desc_serv'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Recomendação de Placa
            st.markdown("#### 🎯 Configuração Recomendada")
            
            placa_info = ANGULOS_PLACA[resultados['tipo_placa']]
            
            placa_col1, placa_col2 = st.columns(2)
            
            with placa_col1:
                st.markdown(f"""
                <div class="result-success">
                <h4>Tipo de Placa: <strong>{resultados['tipo_placa']}</strong></h4>
                <p>{placa_info['descricao']}</p>
                <hr>
                <p><strong>Turbulência:</strong> {placa_info['turbulencia']}</p>
                <p><strong>Queda Pressão:</strong> {placa_info['queda_pressao']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with placa_col2:
                st.markdown(f"""
                <div class="result-warning">
                <p><strong>Multiplicador U:</strong> {resultados['multiplicador_placa']:.2f}x</p>
                <p><strong>U Adotado:</strong> {resultados['U_adotado']:.0f} W/m²K</p>
                <p><strong>LMTD:</strong> {resultados['lmtd']:.2f} °C</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.info(f"💡 {resultados['justificativa_placa']}")
            
            st.divider()
            
            # Parecer IA e PDF
            st.markdown("#### 📋 Documentação")
            
            parecer_ia = generate_parecer_ia(
                st.session_state.calc_modelo, st.session_state.calc_tag, st.session_state.calc_projeto,
                st.session_state.calc_produto, st.session_state.calc_servico,
                st.session_state.calc_vazao_prod, resultados, st.session_state.calc_tipo_modelo
            )
            
            pdf_bytes = build_pdf(
                st.session_state.calc_modelo, st.session_state.calc_tag, st.session_state.calc_projeto,
                st.session_state.calc_produto, st.session_state.calc_servico,
                st.session_state.calc_t_in_prod, st.session_state.calc_t_out_prod,
                st.session_state.calc_t_in_serv, st.session_state.calc_t_out_serv,
                st.session_state.calc_vazao_prod, resultados['vazao_serv'],
                resultados, parecer_ia, st.session_state.calc_tipo_modelo
            )
            
            st.download_button(
                label="📥 Download Datasheet PDF",
                data=pdf_bytes,
                file_name="datasheet_alfaved.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # Parecer expandível
            with st.expander("📄 Ver Parecer Técnico Completo"):
                st.markdown(f"""
                **Parecer Técnico - AlfaVed GenAI**
                
                {parecer_ia}
                """)
        else:
            st.markdown("""
            <div class="section-card">
            <p style="text-align: center; color: #999;">
            👈 Preencha os dados de entrada e clique em <strong>CALCULAR DIMENSIONAMENTO</strong>
            </p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
