import io
import json
import math
import google.genai as genai
import streamlit as st

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA (Única e no Topo)
# ==========================================
st.set_page_config(page_title="AlfaVed Engenharia - Dimensionador", page_icon="▲", layout="wide")

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
            largura_real = letter[0] if isinstance(letter, (list, tuple)) else 612.0
            self.drawRightString(largura_real - 54, 25, f"Pagina {self._pageNumber} de {num_pages}")
            super().showPage()
        super().save()

def calculate_reynolds(vazao_kg_h: float, viscosidade: float, densidade: float, dh: float) -> float:
    if vazao_kg_h <= 0 or viscosidade <= 0 or densidade <= 0:
        return 0
    vazao_m3_s = (vazao_kg_h / 3600.0) / densidade
    area_canal = 0.0001
    u = vazao_m3_s / area_canal
    viscosidade_pa_s = viscosidade * 0.001
    reynolds = (densidade * u * dh) / viscosidade_pa_s
    return reynolds

def classificar_turbulencia(reynolds: float) -> tuple:
    if reynolds < 500:
        return ("Laminar", "Regime laminar - Transferência de calor limitada")
    elif reynolds < 2000:
        return ("Transicional", "Transição laminar-turbulento - Eficiência moderada")
    else:
        return ("Turbulento", "Regime turbulento - Ótima eficiência de transferência")

def recommending_angulo_placa(reynolds_prod: float, reynolds_serv: float, pressao_max: float) -> tuple:
    reynolds_min = min(reynolds_prod, reynolds_serv)
    if reynolds_min < 500:
        return ("45 HT", ANGULOS_PLACA["45 HT"]["multiplicador_u"], "Reynolds baixo detectado. Placa 45 HT recomendada para máxima turbulência.")
    elif reynolds_min > 2000:
        return ("60 LT", ANGULOS_PLACA["60 LT"]["multiplicador_u"], "Reynolds alto (turbulento). Placa 60 LT recomendada para menor queda de pressão.")
    else:
        return ("45 HT", ANGULOS_PLACA["45 HT"]["multiplicador_u"], "Reynolds transicional. Placa 45 HT recomendada para otimizar transferência.")

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

