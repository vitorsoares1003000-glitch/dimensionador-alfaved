"""
AlfaVed Engenharia Térmica - Dimensionador PHE v3.0
Arquivo: app.py
Deploy: streamlit run app.py
"""

import io
import math
import streamlit as st
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# ============================================================================
# CONTATOS TÉCNICOS ALFAVED
# ============================================================================

CONTATOS_ALFAVED = {
    "responsavel_projeto": {
        "nome": "Vitor Soares",
        "cargo": "Responsável de Projeto",
        "email": "engenharia@alfaved.com.br",
        "telefone": "(18) 9.9669-7330",
    },
    "diretor_engenharia": {
        "nome": "Jhonatan Dias Dejato",
        "cargo": "Diretor de Engenharia",
        "email": "jhonatan@alfaved.com.br",
        "telefone": "(18) 9.9628-8714",
    },
}

# ============================================================================
# BANCO DE DADOS - MODELOS ALFA LAVAL COM DIMENSÕES REAIS (mm)
# ============================================================================

BANCO_MODELOS = {
    "M3": {
        "area": 0.03, "Pmax": 16, "Tmax": 180, "dh": 0.003, "conn": 'DN32 (1.25")',
        "cat": "Gaxetado", "placa_larg": 0.08, "placa_comp": 0.25, "canal_larg": 0.07,
        "esp": 0.0015, "width": 180, "height": 480, "v_dist": 354, "h_dist": 60,
        "port_diam": 32, "frame_thick": 30, "min_length": 200, "max_length": 500,
        "bolt_size": "M12", "weight_per_plate": 0.8
    },
    "M6-B": {
        "area": 0.15, "Pmax": 10, "Tmax": 180, "dh": 0.005, "conn": 'DN50 (2")',
        "cat": "Gaxetado", "placa_larg": 0.15, "placa_comp": 0.40, "canal_larg": 0.14,
        "esp": 0.0020, "width": 320, "height": 920, "v_dist": 640, "h_dist": 140,
        "port_diam": 50, "frame_thick": 40, "min_length": 350, "max_length": 1200,
        "bolt_size": "M16", "weight_per_plate": 2.5
    },
    "TS6M": {
        "area": 0.26, "Pmax": 25, "Tmax": 180, "dh": 0.006, "conn": 'DN65 (2.5")',
        "cat": "Gaxetado", "placa_larg": 0.18, "placa_comp": 0.52, "canal_larg": 0.17,
        "esp": 0.0025, "width": 400, "height": 1050, "v_dist": 820, "h_dist": 180,
        "port_diam": 65, "frame_thick": 45, "min_length": 400, "max_length": 1500,
        "bolt_size": "M20", "weight_per_plate": 3.0
    },
    "M10-B": {
        "area": 0.24, "Pmax": 10, "Tmax": 180, "dh": 0.006, "conn": 'DN100 (4")',
        "cat": "Gaxetado", "placa_larg": 0.25, "placa_comp": 0.50, "canal_larg": 0.24,
        "esp": 0.0025, "width": 470, "height": 1084, "v_dist": 719, "h_dist": 225,
        "port_diam": 100, "frame_thick": 50, "min_length": 500, "max_length": 2200,
        "bolt_size": "M20", "weight_per_plate": 4.0
    },
    "M15-B": {
        "area": 0.36, "Pmax": 10, "Tmax": 180, "dh": 0.008, "conn": 'DN150 (6")',
        "cat": "Gaxetado", "placa_larg": 0.35, "placa_comp": 0.60, "canal_larg": 0.33,
        "esp": 0.0030, "width": 610, "height": 1550, "v_dist": 1050, "h_dist": 298,
        "port_diam": 150, "frame_thick": 60, "min_length": 700, "max_length": 3500,
        "bolt_size": "M24", "weight_per_plate": 7.5
    },
    "T20-B": {
        "area": 0.85, "Pmax": 10, "Tmax": 180, "dh": 0.009, "conn": 'DN200 (8")',
        "cat": "Gaxetado", "placa_larg": 0.45, "placa_comp": 0.75, "canal_larg": 0.43,
        "esp": 0.0030, "width": 780, "height": 2145, "v_dist": 1478, "h_dist": 353,
        "port_diam": 200, "frame_thick": 70, "min_length": 900, "max_length": 4500,
        "bolt_size": "M27", "weight_per_plate": 12.0
    },
    "TS20": {
        "area": 0.95, "Pmax": 25, "Tmax": 180, "dh": 0.009, "conn": 'DN200 (8")',
        "cat": "Gaxetado", "placa_larg": 0.45, "placa_comp": 0.80, "canal_larg": 0.43,
        "esp": 0.0035, "width": 850, "height": 2250, "v_dist": 1580, "h_dist": 400,
        "port_diam": 200, "frame_thick": 75, "min_length": 900, "max_length": 5000,
        "bolt_size": "M27", "weight_per_plate": 13.0
    },
    "MA30-S": {
        "area": 1.38, "Pmax": 25, "Tmax": 180, "dh": 0.012, "conn": 'DN300 (12")',
        "cat": "WideGap", "placa_larg": 0.70, "placa_comp": 1.00, "canal_larg": 0.65,
        "esp": 0.0050, "width": 1000, "height": 2400, "v_dist": 1800, "h_dist": 500,
        "port_diam": 300, "frame_thick": 80, "min_length": 1200, "max_length": 5500,
        "bolt_size": "M30", "weight_per_plate": 18.0
    },
    "WideGap 350": {
        "area": 1.80, "Pmax": 10, "Tmax": 180, "dh": 0.015, "conn": 'DN350 (14")',
        "cat": "WideGap", "placa_larg": 0.80, "placa_comp": 1.10, "canal_larg": 0.75,
        "esp": 0.0060, "width": 1200, "height": 2800, "v_dist": 2200, "h_dist": 600,
        "port_diam": 350, "frame_thick": 90, "min_length": 1400, "max_length": 6000,
        "bolt_size": "M36", "weight_per_plate": 25.0
    },
    "M10-BW": {
        "area": 0.24, "Pmax": 55, "Tmax": 250, "dh": 0.005, "conn": 'DN100 (4")',
        "cat": "Semi-Soldado", "placa_larg": 0.25, "placa_comp": 0.50, "canal_larg": 0.24,
        "esp": 0.0025, "width": 470, "height": 1084, "v_dist": 719, "h_dist": 225,
        "port_diam": 100, "frame_thick": 55, "min_length": 500, "max_length": 2200,
        "bolt_size": "M20", "weight_per_plate": 4.5
    },
    "MK15-BW": {
        "area": 0.42, "Pmax": 41, "Tmax": 200, "dh": 0.006, "conn": 'DN150 (6")',
        "cat": "Semi-Soldado", "placa_larg": 0.35, "placa_comp": 0.60, "canal_larg": 0.33,
        "esp": 0.0030, "width": 650, "height": 1486, "v_dist": 1044, "h_dist": 298,
        "port_diam": 150, "frame_thick": 60, "min_length": 700, "max_length": 2800,
        "bolt_size": "M24", "weight_per_plate": 8.0
    },
    "TK20-BW": {
        "area": 0.68, "Pmax": 63, "Tmax": 200, "dh": 0.006, "conn": 'DN200 (8")',
        "cat": "Semi-Soldado", "placa_larg": 0.45, "placa_comp": 0.75, "canal_larg": 0.43,
        "esp": 0.0030, "width": 740, "height": 1600, "v_dist": 1200, "h_dist": 350,
        "port_diam": 200, "frame_thick": 70, "min_length": 850, "max_length": 3500,
        "bolt_size": "M27", "weight_per_plate": 11.0
    },
    "T20-W": {
        "area": 0.85, "Pmax": 30, "Tmax": 180, "dh": 0.009, "conn": 'DN200 (8")',
        "cat": "Semi-Soldado", "placa_larg": 0.45, "placa_comp": 0.75, "canal_larg": 0.43,
        "esp": 0.0030, "width": 780, "height": 2145, "v_dist": 1478, "h_dist": 353,
        "port_diam": 200, "frame_thick": 70, "min_length": 900, "max_length": 4500,
        "bolt_size": "M27", "weight_per_plate": 12.0
    },
    "MA30-W": {
        "area": 1.40, "Pmax": 40, "Tmax": 180, "dh": 0.010, "conn": 'DN300 (12")',
        "cat": "Semi-Soldado", "placa_larg": 0.70, "placa_comp": 1.00, "canal_larg": 0.65,
        "esp": 0.0040, "width": 1000, "height": 2400, "v_dist": 1800, "h_dist": 500,
        "port_diam": 300, "frame_thick": 80, "min_length": 1200, "max_length": 5500,
        "bolt_size": "M30", "weight_per_plate": 18.0
    },
}

BANCO_FLUIDOS = {
    "Agua": {"cp": 4180, "visc": 0.00089, "dens": 1000, "cond": 0.60, "tipo": "base"},
    "Leite Integral": {"cp": 3890, "visc": 0.00210, "dens": 1030, "cond": 0.55, "tipo": "alimento"},
    "Leite Desnatado": {"cp": 3950, "visc": 0.00150, "dens": 1020, "cond": 0.57, "tipo": "alimento"},
    "Suco de Laranja": {"cp": 3750, "visc": 0.00350, "dens": 1040, "cond": 0.54, "tipo": "alimento"},
    "Suco de Maca": {"cp": 3700, "visc": 0.00280, "dens": 1035, "cond": 0.55, "tipo": "alimento"},
    "Oleo Vegetal": {"cp": 1970, "visc": 0.0500, "dens": 920, "cond": 0.17, "tipo": "oleo"},
    "Oleo Mineral": {"cp": 1880, "visc": 0.1000, "dens": 880, "cond": 0.15, "tipo": "oleo"},
    "Melado": {"cp": 2800, "visc": 0.1500, "dens": 1380, "cond": 0.50, "tipo": "viscoso"},
    "Cerveja": {"cp": 4100, "visc": 0.00150, "dens": 1010, "cond": 0.58, "tipo": "alimento"},
    "Vinho": {"cp": 3850, "visc": 0.00120, "dens": 1000, "cond": 0.56, "tipo": "alimento"},
    "Chocolate Quente": {"cp": 3500, "visc": 0.00800, "dens": 1050, "cond": 0.52, "tipo": "alimento"},
    "Polpa de Fruta": {"cp": 3600, "visc": 0.00500, "dens": 1050, "cond": 0.53, "tipo": "alimento"},
    "Soro de Leite": {"cp": 3950, "visc": 0.00120, "dens": 1025, "cond": 0.57, "tipo": "alimento"},
    "Creme de Leite": {"cp": 3500, "visc": 0.01200, "dens": 980, "cond": 0.45, "tipo": "alimento"},
    "Iogurte": {"cp": 3700, "visc": 0.02500, "dens": 1060, "cond": 0.50, "tipo": "alimento"},
    "Nata": {"cp": 3400, "visc": 0.01500, "dens": 970, "cond": 0.42, "tipo": "alimento"},
    "Manteiga Derretida": {"cp": 2100, "visc": 0.04000, "dens": 910, "cond": 0.18, "tipo": "oleo"},
}

BANCO_SERVICOS = {
    "Agua Fria": {"cp": 4180, "visc": 0.00089, "dens": 1000, "cond": 0.60, "tipo": "base"},
    "Agua Gelada": {"cp": 4180, "visc": 0.00130, "dens": 1000, "cond": 0.58, "tipo": "base"},
    "Agua Morna": {"cp": 4180, "visc": 0.00065, "dens": 995, "cond": 0.61, "tipo": "base"},
    "Agua Quente": {"cp": 4180, "visc": 0.00035, "dens": 960, "cond": 0.68, "tipo": "base"},
    "Vapor Saturado": {"cp": 2000, "visc": 0.000015, "dens": 0.60, "cond": 0.025, "tipo": "vapor"},
    "Oleo Termico": {"cp": 2500, "visc": 0.00500, "dens": 850, "cond": 0.13, "tipo": "oleo"},
    "Refrigerante R22": {"cp": 1450, "visc": 0.000018, "dens": 450, "cond": 0.09, "tipo": "gas"},
    "R410A": {"cp": 1600, "visc": 0.000020, "dens": 480, "cond": 0.10, "tipo": "gas"},
    "R134a": {"cp": 1520, "visc": 0.000019, "dens": 470, "cond": 0.095, "tipo": "gas"},
    "R717 (NH3)": {"cp": 4700, "visc": 0.00025, "dens": 682, "cond": 0.50, "tipo": "gas"},
    "R744 (CO2)": {"cp": 3500, "visc": 0.00007, "dens": 1100, "cond": 0.12, "tipo": "gas"},
    "Ar Comprimido": {"cp": 1010, "visc": 0.000018, "dens": 1.20, "cond": 0.026, "tipo": "gas"},
    "Glicol 30%": {"cp": 3700, "visc": 0.00350, "dens": 1040, "cond": 0.50, "tipo": "base"},
    "Glicol 50%": {"cp": 3500, "visc": 0.00600, "dens": 1070, "cond": 0.46, "tipo": "base"},
}

# ============================================================================
# FUNÇÕES DE ENGENHARIA
# ============================================================================

def get_calor_latente(temp):
    if temp >= 150: return 2114.0
    if temp >= 130: return 2174.0
    if temp >= 110: return 2230.0
    if temp >= 100: return 2257.0
    if temp >= 80: return 2308.0
    return 2358.0

def calc_reynolds_real(vazao_kgh, visc_pas, dens_kgm3, dh_m, canal_larg_m, n_placas):
    if vazao_kgh <= 0 or visc_pas <= 0 or dens_kgm3 <= 0:
        return 0.0
    canais_por_lado = max(1, (n_placas - 1) // 2)
    vazao_kgs_total = vazao_kgh / 3600.0
    vazao_por_canal = vazao_kgs_total / canais_por_lado
    espacamento = dh_m / 2.0
    area_fluxo = canal_larg_m * espacamento
    if area_fluxo <= 0:
        return 0.0
    u = vazao_por_canal / (dens_kgm3 * area_fluxo)
    re = (dens_kgm3 * u * dh_m) / visc_pas
    return max(0.0, re)

def calc_prandtl(cp_jkgk, visc_pas, cond_wm2k):
    if cond_wm2k <= 0 or visc_pas <= 0:
        return 0.0
    return (visc_pas * cp_jkgk) / cond_wm2k

def calc_nusselt_placa(re, pr, angulo):
    if re <= 0 or pr <= 0:
        return 5.0
    if "H" in angulo:
        C, m = 0.3, 0.663
    elif "L" in angulo:
        C, m = 0.14, 0.651
    else:
        C, m = 0.2, 0.658
    n = 0.333
    if re < 20:
        nu = 0.55 * (re ** 0.25) * (pr ** n)
    else:
        nu = C * (re ** m) * (pr ** n)
    return max(3.0, nu)

def calc_h_coef(nu, cond_wm2k, dh_m):
    if dh_m <= 0:
        return 0.0
    return (nu * cond_wm2k) / dh_m

def calc_u_global(h_p, h_s, esp_placa=0.0005, k_placa=17.0, r_fp=0.0001, r_fs=0.0001):
    if h_p <= 0 or h_s <= 0:
        return 0.0
    r_total = (1.0 / h_p) + r_fp + (esp_placa / k_placa) + r_fs + (1.0 / h_s)
    if r_total <= 0:
        return 0.0
    return 1.0 / r_total

def calc_lmtd(t1_ent, t1_sai, t2_ent, t2_sai, fluxo="contra"):
    if fluxo == "co":
        dt1 = abs(t1_ent - t2_ent)
        dt2 = abs(t1_sai - t2_sai)
    else:
        dt1 = abs(t1_ent - t2_sai)
        dt2 = abs(t1_sai - t2_ent)
    if dt1 <= 0 or dt2 <= 0:
        return max(dt1, dt2, 0.1)
    if abs(dt1 - dt2) < 0.001:
        return dt1
    return (dt1 - dt2) / math.log(dt1 / dt2)

def calc_fator_f_corrigido(P, R, n_passes):
    if n_passes == 1:
        return 1.0
    P = max(0.001, min(0.999, P))
    R = max(0.001, min(10.0, R))
    if R < 0.2:
        f_est = 0.98
    elif R < 0.5:
        f_est = 0.95
    elif R < 1.0:
        f_est = 0.93
    elif R < 2.0:
        f_est = 0.90
    else:
        f_est = 0.88
    if P > 0.8:
        f_est *= 0.98
    return max(0.75, min(1.0, f_est))

def calc_area(Q_w, U, lmtd, F=1.0):
    if U <= 0 or lmtd <= 0 or F <= 0:
        return 0.0
    return Q_w / (U * lmtd * F)

def calc_vazao_servico(Q_w, cp_jkgk, dt):
    if cp_jkgk <= 0 or dt <= 0:
        return 0.0
    m_dot_kgs = Q_w / (cp_jkgk * dt)
    return m_dot_kgs * 3600.0

def calc_num_placas(area_total, area_placa):
    if area_placa <= 0:
        return 0
    n = math.ceil(area_total / area_placa)
    if n < 3:
        n = 3
    if n % 2 == 0:
        n += 1
    return n

def recomendar_gaxeta(fluido_p, fluido_s, t_max):
    tipos = [
        BANCO_FLUIDOS.get(fluido_p, {}).get("tipo"),
        BANCO_SERVICOS.get(fluido_s, {}).get("tipo"),
    ]
    if "oleo" in tipos or "gas" in tipos:
        if t_max > 140:
            return "Viton (FKM)", "Alta resistência térmica e química para óleos/gases."
        return "NBR", "Excelente resistência a óleos e derivados de petróleo."
    if "alimento" in tipos:
        if t_max > 140:
            return "PTFE", "Inércia química total para aplicações sanitárias severas."
        return "EPDM", "Padrão sanitário FDA para alimentos e fluidos aquosos."
    if t_max > 160:
        return "PTFE", "Resistência extrema a temperatura."
    return "EPDM", "Melhor custo-benefício para fluidos aquosos."

def calc_press_drop_real(re, n_placas, angulo, vazao_kgh, dens_kgm3, canal_larg_m, dh_m, visc_pas):
    if re <= 0 or n_placas < 2:
        return 0.0
    canais_por_lado = max(1, (n_placas - 1) // 2)
    vazao_kgs = vazao_kgh / 3600.0
    espacamento = dh_m / 2.0
    area_fluxo = canal_larg_m * espacamento
    if area_fluxo <= 0:
        return 0.0
    vazao_por_canal = vazao_kgs / canais_por_lado
    u = vazao_por_canal / (dens_kgm3 * area_fluxo)
    if "H" in angulo:
        f = 0.5 / (re ** 0.2) if re >= 2000 else 16.0 / re
    elif "L" in angulo:
        f = 0.3 / (re ** 0.2) if re >= 2000 else 16.0 / re
    else:
        f = 0.4 / (re ** 0.2) if re >= 2000 else 16.0 / re
    comp_hidraulico = 2.0 * 0.5
    dp_canal_pa = 4.0 * f * (comp_hidraulico / dh_m) * (dens_kgm3 * u ** 2 / 2.0)
    d_porta = 0.05
    area_porta = math.pi * (d_porta ** 2) / 4.0
    u_porta = vazao_kgs / (dens_kgm3 * area_porta)
    k_local = 2.5
    dp_portas_pa = k_local * (dens_kgm3 * u_porta ** 2 / 2.0)
    return (dp_canal_pa + dp_portas_pa) / 1000.0

def get_pass_arrangement(vazao_kgh, lmtd, temp_max, modo_manual="Automatico"):
    if modo_manual == "Single Pass (1/1)":
        return "1/1", "Single Pass", "Selecionado manualmente: todas as conexões no cabeçote fixo."
    if modo_manual == "Two Pass (2/2)":
        return "2/2", "Two Pass", "Selecionado manualmente: conexões em lados opostos para reversão de fluxo."
    if lmtd < 3.0 or vazao_kgh > 20000:
        return "2/2", "Two Pass", "Necessário para melhor aproximação térmica ou gerenciar alta vazão."
    return "1/1", "Single Pass", "Arranjo padrão para máxima eficiência em contra-corrente."

def determinar_conexoes(arranjo_passe):
    if arranjo_passe == "1/1":
        return {
            "produto_entrada": "Cabeçote Fixo (Frame Plate)",
            "produto_saida": "Cabeçote Fixo (Frame Plate)",
            "servico_entrada": "Cabeçote Fixo (Frame Plate)",
            "servico_saida": "Cabeçote Fixo (Frame Plate)",
            "descricao": "Arranjo 1/1: Todas as conexões no cabeçote fixo. Passagem única, manutenção simplificada.",
            "port_arrangement": "4 conexões frontais no cabeçote fixo",
        }
    else:
        return {
            "produto_entrada": "Cabeçote Fixo (Frame Plate)",
            "produto_saida": "Prato de Pressão (Pressure Plate)",
            "servico_entrada": "Prato de Pressão (Pressure Plate)",
            "servico_saida": "Cabeçote Fixo (Frame Plate)",
            "descricao": "Arranjo 2/2: Conexões em lados opostos obrigatoriamente para reversão de fluxo.",
            "port_arrangement": "Pass 1: Fixo -> Móvel | Pass 2: Móvel -> Fixo",
        }

def gerar_correcoes(alertas, dp_p, dp_s, re_p, re_s, fator_f, angulo_atual, arranjo_atual, n_placas, lmtd):
    correcoes = []
    if dp_p > 150 or dp_s > 150:
        sugestao = []
        if "H" in angulo_atual:
            sugestao.append("Mudar ângulo da placa de H (45°) para L (60°) ou Mista (52.5°)")
        if arranjo_atual == "2/2":
            sugestao.append("Considerar Single Pass (1/1) para reduzir comprimento do percurso")
        if n_placas > 50:
            sugestao.append("Verificar se o número de placas pode ser reduzido")
        if not sugestao:
            sugestao.append("Reduzir vazão ou aumentar área de troca")
        correcoes.append({
            "problema": "Queda de pressão excessiva",
            "valor": f"Produto: {dp_p:.1f} kPa | Serviço: {dp_s:.1f} kPa",
            "limite": "150 kPa",
            "acoes": sugestao,
            "prioridade": "Alta"
        })
    if re_p < 2000:
        correcoes.append({
            "problema": "Reynolds do produto baixo (regime laminar)",
            "valor": f"{re_p:.0f}",
            "limite": "> 2000",
            "acoes": [
                "Mudar ângulo da placa para H (45°) para aumentar turbulência",
                "Reduzir número de placas para aumentar velocidade por canal",
                "Verificar se a vazão está dentro da faixa do modelo"
            ],
            "prioridade": "Média"
        })
    if re_s < 2000:
        is_vapor = False
        correcoes.append({
            "problema": "Reynolds do serviço baixo (regime laminar)",
            "valor": f"{re_s:.0f}",
            "limite": "> 2000",
            "acoes": [
                "Mudar ângulo da placa para H (45°) para aumentar turbulência",
                "Reduzir número de placas para aumentar velocidade por canal"
            ],
            "prioridade": "Média"
        })
    if fator_f < 0.75:
        correcoes.append({
            "problema": "Fator F de correção baixo",
            "valor": f"{fator_f:.3f}",
            "limite": "> 0.75",
            "acoes": [
                "Aumentar diferença de temperatura (aumentar ΔT de um dos fluidos)",
                f"Ajustar arranjo para Two Pass (2/2) — atual: {arranjo_atual}",
                "Verificar se a aproximação térmica não é excessiva"
            ],
            "prioridade": "Média"
        })
    if lmtd < 2.0:
        correcoes.append({
            "problema": "LMTD muito baixo",
            "valor": f"{lmtd:.2f} °C",
            "limite": "> 2.0 °C",
            "acoes": [
                "Aumentar diferença de temperatura entre fluidos",
                "Considerar série de trocadores para aproximação térmica",
                "Verificar se as temperaturas de projeto estão corretas"
            ],
            "prioridade": "Alta"
        })
    return correcoes

# ============================================================================
# SVG DIMENSIONAL
# ============================================================================

def generate_dimensional_svg(modelo, d, n_placas):
    """
    Gera SVG técnico com vista frontal (placa com portas) e vista lateral (conjunto).
    """
    total_L = (n_placas * 2.5) + (d['frame_thick'] * 2)
    escala = min(300.0 / d['height'], 1.0)
    w = int(d['width'] * escala)
    h = int(d['height'] * escala)
    pd = int(d['port_diam'] * escala)
    f = int(d['frame_thick'] * escala)
    l_side = int(total_L * escala * 0.3)
    
    svg = f'''<svg width="850" height="420" xmlns="http://www.w3.org/2000/svg" style="background:#fafafa;border:1px solid #ddd;border-radius:8px;">
  <text x="425" y="25" font-family="Arial,sans-serif" font-size="16" font-weight="bold" fill="#003049" text-anchor="middle">DESENHO DIMENSIONAL TÉCNICO — ALFA LAVAL {modelo}</text>
  <text x="425" y="42" font-family="Arial,sans-serif" font-size="11" fill="#666" text-anchor="middle">Medidas em mm | Escala aproximada</text>
  
  <!-- VISTA FRONTAL (Placa) -->
  <g transform="translate(80, 70)">
    <rect x="0" y="0" width="{w}" height="{h}" fill="none" stroke="#000" stroke-width="2"/>
    <!-- Portas superiores -->
    <circle cx="{w//4}" cy="{h//5}" r="{pd//2}" fill="none" stroke="#003049" stroke-width="2"/>
    <circle cx="{3*w//4}" cy="{h//5}" r="{pd//2}" fill="none" stroke="#003049" stroke-width="2"/>
    <!-- Portas inferiores -->
    <circle cx="{w//4}" cy="{4*h//5}" r="{pd//2}" fill="none" stroke="#003049" stroke-width="2"/>
    <circle cx="{3*w//4}" cy="{4*h//5}" r="{pd//2}" fill="none" stroke="#003049" stroke-width="2"/>
    <!-- Linhas de centro -->
    <line x1="{w//2}" y1="0" x2="{w//2}" y2="{h}" stroke="#999" stroke-dasharray="4,4" stroke-width="1"/>
    <line x1="0" y1="{h//2}" x2="{w}" y2="{h//2}" stroke="#999" stroke-dasharray="4,4" stroke-width="1"/>
    <!-- Cruzetas centro -->
    <line x1="{w//4 - pd//3}" y1="{h//5}" x2="{w//4 + pd//3}" y2="{h//5}" stroke="#999" stroke-width="1"/>
    <line x1="{w//4}" y1="{h//5 - pd//3}" x2="{w//4}" y2="{h//5 + pd//3}" stroke="#999" stroke-width="1"/>
    <line x1="{3*w//4 - pd//3}" y1="{h//5}" x2="{3*w//4 + pd//3}" y2="{h//5}" stroke="#999" stroke-width="1"/>
    <line x1="{3*w//4}" y1="{h//5 - pd//3}" x2="{3*w//4}" y2="{h//5 + pd//3}" stroke="#999" stroke-width="1"/>
    <line x1="{w//4 - pd//3}" y1="{4*h//5}" x2="{w//4 + pd//3}" y2="{4*h//5}" stroke="#999" stroke-width="1"/>
    <line x1="{w//4}" y1="{4*h//5 - pd//3}" x2="{w//4}" y2="{4*h//5 + pd//3}" stroke="#999" stroke-width="1"/>
    <line x1="{3*w//4 - pd//3}" y1="{4*h//5}" x2="{3*w//4 + pd//3}" y2="{4*h//5}" stroke="#999" stroke-width="1"/>
    <line x1="{3*w//4}" y1="{4*h//5 - pd//3}" x2="{3*w//4}" y2="{4*h//5 + pd//3}" stroke="#999" stroke-width="1"/>
    <!-- Seta dimensão largura -->
    <line x1="0" y1="{h + 15}" x2="{w}" y2="{h + 15}" stroke="#000" stroke-width="1"/>
    <polygon points="0,{h+15} 8,{h+11} 8,{h+19}" fill="#000"/>
    <polygon points="{w},{h+15} {w-8},{h+11} {w-8},{h+19}" fill="#000"/>
    <text x="{w//2}" y="{h + 32}" font-family="Arial" font-size="11" text-anchor="middle">W = {d['width']} mm</text>
    <!-- Seta dimensão altura -->
    <line x1="{w + 15}" y1="0" x2="{w + 15}" y2="{h}" stroke="#000" stroke-width="1"/>
    <polygon points="{w+15},0 {w+11},8 {w+19},8" fill="#000"/>
    <polygon points="{w+15},{h} {w+11},{h-8} {w+19},{h-8}" fill="#000"/>
    <text x="{w + 30}" y="{h//2}" font-family="Arial" font-size="11" transform="rotate(90, {w+30}, {h//2})" text-anchor="middle">H = {d['height']} mm</text>
    <!-- Label -->
    <text x="{w//2}" y="{h + 50}" font-family="Arial" font-size="12" font-weight="bold" text-anchor="middle" fill="#003049">VISTA FRONTAL (Placa)</text>
  </g>
  
  <!-- VISTA LATERAL (Conjunto montado) -->
  <g transform="translate({120 + w + 40}, 70)">
    <!-- Cabeçote fixo -->
    <rect x="0" y="0" width="{f}" height="{h}" fill="#e0e0e0" stroke="#000" stroke-width="2"/>
    <text x="{f//2}" y="{h//2}" font-family="Arial" font-size="10" text-anchor="middle" transform="rotate(-90, {f//2}, {h//2})">FIXO</text>
    <!-- Pacote de placas -->
    <rect x="{f}" y="10" width="{l_side}" height="{h-20}" fill="#f5f5f5" stroke="#000" stroke-width="1"/>
    <!-- Linhas de placas corrugadas -->
'''
    for i in range(0, l_side, max(3, l_side // 40)):
        svg += f'    <line x1="{f + i}" y1="10" x2="{f + i}" y2="{h-10}" stroke="#333" stroke-width="0.5"/>\n'
    
    svg += f'''    <!-- Cabeçote móvel -->
    <rect x="{f + l_side}" y="0" width="{f}" height="{h}" fill="#d0d0d0" stroke="#000" stroke-width="2"/>
    <text x="{f + l_side + f//2}" y="{h//2}" font-family="Arial" font-size="10" text-anchor="middle" transform="rotate(-90, {f + l_side + f//2}, {h//2})">MÓVEL</text>
    <!-- Tirantes superiores -->
    <line x1="{-10}" y1="20" x2="{f + l_side + f + 10}" y2="20" stroke="#000" stroke-width="4"/>
    <line x1="{-10}" y1="25" x2="{f + l_side + f + 10}" y2="25" stroke="#000" stroke-width="4"/>
    <!-- Tirantes inferiores -->
    <line x1="{-10}" y1="{h-20}" x2="{f + l_side + f + 10}" y2="{h-20}" stroke="#000" stroke-width="4"/>
    <line x1="{-10}" y1="{h-25}" x2="{f + l_side + f + 10}" y2="{h-25}" stroke="#000" stroke-width="4"/>
    <!-- Porcas -->
    <circle cx="{-5}" cy="22" r="6" fill="none" stroke="#000" stroke-width="1.5"/>
    <circle cx="{-5}" cy="{h-22}" r="6" fill="none" stroke="#000" stroke-width="1.5"/>
    <circle cx="{f + l_side + f + 5}" cy="22" r="6" fill="none" stroke="#000" stroke-width="1.5"/>
    <circle cx="{f + l_side + f + 5}" cy="{h-22}" r="6" fill="none" stroke="#000" stroke-width="1.5"/>
    <!-- Seta dimensão comprimento -->
    <line x1="0" y1="{h + 15}" x2="{f + l_side + f}" y2="{h + 15}" stroke="#000" stroke-width="1"/>
    <polygon points="0,{h+15} 8,{h+11} 8,{h+19}" fill="#000"/>
    <polygon points="{f+l_side+f},{h+15} {f+l_side+f-8},{h+11} {f+l_side+f-8},{h+19}" fill="#000"/>
    <text x="{(f + l_side + f)//2}" y="{h + 32}" font-family="Arial" font-size="11" text-anchor="middle">L = {total_L:.0f} mm ({n_placas} placas)</text>
    <!-- Label -->
    <text x="{(f + l_side + f)//2}" y="{h + 50}" font-family="Arial" font-size="12" font-weight="bold" text-anchor="middle" fill="#003049">VISTA LATERAL (Conjunto)</text>
  </g>
  
  <!-- Tabela de specs -->
  <g transform="translate(80, {70 + h + 65})">
    <rect x="0" y="0" width="700" height="90" fill="white" stroke="#003049" stroke-width="1" rx="4"/>
    <text x="10" y="18" font-family="Arial" font-size="11" font-weight="bold" fill="#003049">ESPECIFICAÇÕES DO MODELO {modelo}</text>
    <text x="10" y="38" font-family="Arial" font-size="10" fill="#333">Largura (W): {d['width']} mm | Altura (H): {d['height']} mm | Porta: DN{d['port_diam']} ({d['conn']})</text>
    <text x="10" y="55" font-family="Arial" font-size="10" fill="#333">Dist. vertical portas: {d['v_dist']} mm | Dist. horizontal: {d['h_dist']} mm | Espess. placa: {d['esp']*1000:.1f} mm</text>
    <text x="10" y="72" font-family="Arial" font-size="10" fill="#333">Parafuso: {d['bolt_size']} | Peso/placa: {d['weight_per_plate']} kg | P. máx: {d['Pmax']} bar | T. máx: {d['Tmax']}°C</text>
  </g>
</svg>'''
    return svg

# ============================================================================
# GERAÇÃO DE PDF
# ============================================================================

def gerar_pdf(
    tag, projeto, modelo, angulo, arranjo, conexoes, fluxo_config, pass_manual,
    prod, vazao_p, t_in_p, t_out_p,
    serv, vazao_s_calc, t_in_s, t_out_s,
    carga_kw, carga_w, area_req, n_placas, lmtd, fator_f,
    re_p, re_s, pr_p, pr_s, h_p, h_s, U_calc,
    dp_p, dp_s, gaxeta, gaxeta_desc,
    correcoes, data_str, contatos,
):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "TitleCustom", parent=styles["Heading1"], fontSize=16,
        textColor=colors.HexColor("#003049"), spaceAfter=12, alignment=1,
    )
    style_h2 = ParagraphStyle(
        "Heading2Custom", parent=styles["Heading2"], fontSize=12,
        textColor=colors.HexColor("#003049"), spaceAfter=8, spaceBefore=10,
    )
    style_normal = styles["Normal"]
    style_normal.fontSize = 10
    style_normal.leading = 12

    story = []

    story.append(Paragraph("<b>AlfaVed Soluções Industriais</b>", style_title))
    story.append(Paragraph("Relatório Técnico de Dimensionamento - Trocador de Calor a Placas", style_normal))
    story.append(Paragraph(f"<b>Data:</b> {data_str}", style_normal))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>1. Informações do Projeto</b>", style_h2))
    t1 = Table([
        ["Tag do Equipamento", tag],
        ["Projeto", projeto],
        ["Modelo Selecionado", modelo],
        ["Ângulo da Placa", angulo],
        ["Configuração de Fluxo", fluxo_config],
        ["Arranjo de Passes", f"{arranjo} ({pass_manual})"],
    ], colWidths=[8*cm, 8*cm])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2. Contatos Técnicos</b>", style_h2))
    resp = contatos["responsavel_projeto"]
    diretor = contatos["diretor_engenharia"]
    t_cont = Table([
        ["Cargo", "Nome", "E-mail", "Telefone"],
        [resp["cargo"], resp["nome"], resp["email"], resp["telefone"]],
        [diretor["cargo"], diretor["nome"], diretor["email"], diretor["telefone"]],
    ], colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    t_cont.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003049")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f0f4f8")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_cont)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>3. Configuração de Conexões</b>", style_h2))
    story.append(Paragraph(f"<b>Descrição:</b> {conexoes['descricao']}", style_normal))
    story.append(Paragraph(f"<b>Port Arrangement:</b> {conexoes['port_arrangement']}", style_normal))
    t2 = Table([
        ["", "Entrada", "Saída"],
        ["Produto", conexoes["produto_entrada"], conexoes["produto_saida"]],
        ["Serviço", conexoes["servico_entrada"], conexoes["servico_saida"]],
    ], colWidths=[5*cm, 5.5*cm, 5.5*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003049")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f0f4f8")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>4. Dados Operacionais</b>", style_h2))
    t3 = Table([
        ["Parâmetro", "Produto", "Serviço"],
        ["Fluido", prod, serv],
        ["Vazão (kg/h)", f"{vazao_p:,.0f}", f"{vazao_s_calc:,.0f}"],
        ["Temp. Entrada (°C)", f"{t_in_p:.1f}", f"{t_in_s:.1f}"],
        ["Temp. Saída (°C)", f"{t_out_p:.1f}", f"{t_out_s:.1f}"],
    ], colWidths=[6*cm, 5*cm, 5*cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003049")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f0f4f8")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t3)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>5. Resultados do Dimensionamento</b>", style_h2))
    res_data = [
        ["Carga Térmica (kW)", f"{carga_kw:.2f}"],
        ["Carga Térmica (W)", f"{carga_w:,.0f}"],
        ["LMTD (°C)", f"{lmtd:.2f}"],
        ["Fator F de Correção", f"{fator_f:.3f}"],
        ["Área Requerida (m²)", f"{area_req:.2f}"],
        ["Número de Placas", f"{n_placas}"],
        ["Reynolds - Produto", f"{re_p:,.0f}"],
        ["Reynolds - Serviço", f"{re_s:,.0f}"],
        ["Prandtl - Produto", f"{pr_p:.2f}"],
        ["Prandtl - Serviço", f"{pr_s:.2f}"],
        ["h Convectivo - Produto (W/m²K)", f"{h_p:.1f}"],
        ["h Convectivo - Serviço (W/m²K)", f"{h_s:.1f}"],
        ["U Global Calculado (W/m²K)", f"{U_calc:.1f}"],
        ["ΔP Estimada - Produto (kPa)", f"{dp_p:.2f}"],
        ["ΔP Estimada - Serviço (kPa)", f"{dp_s:.2f}"],
        ["Gaxeta Recomendada", gaxeta],
        ["Observação Gaxeta", gaxeta_desc],
    ]
    t4 = Table(res_data, colWidths=[8*cm, 8*cm])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t4)
    story.append(Spacer(1, 10))

    if correcoes:
        story.append(Paragraph("<b>6. Diagnóstico e Correções Sugeridas</b>", style_h2))
        for corr in correcoes:
            story.append(Paragraph(f"<b>{corr['problema']}</b> — Prioridade: {corr['prioridade']}", style_normal))
            story.append(Paragraph(f"Valor: {corr['valor']} | Limite: {corr['limite']}", style_normal))
            for acao in corr['acoes']:
                story.append(Paragraph(f"• {acao}", style_normal))
            story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "<i>Este relatório foi gerado automaticamente pelo Dimensionador Técnico AlfaVed. "
            "Os valores são estimados e devem ser validados pelo departamento de engenharia. "
            f"Suporte técnico: {resp['email']} | {resp['telefone']}</i>",
            style_normal,
        )
    )

    doc.build(story)
    buf.seek(0)
    return buf

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def main():
    st.set_page_config(page_title="AlfaVed Engenharia - Dimensionador", page_icon="▲", layout="wide")
    
    st.markdown(
        """
        <style>
        .main-header {
            background: linear-gradient(135deg, #0d1b2a 0%, #003049 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: #f8f9fa;
            border-left: 5px solid #003049;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .contact-card {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
            border: 1px solid #dee2e6;
        }
        .contact-card-person {
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px 15px;
            margin-bottom: 8px;
        }
        .correcao-card {
            background: #fff8e1;
            border-left: 5px solid #ff9800;
            padding: 15px;
            border-radius: 8px;
            margin: 8px 0;
        }
        .correcao-card-alta {
            background: #ffebee;
            border-left: 5px solid #f44336;
            padding: 15px;
            border-radius: 8px;
            margin: 8px 0;
        }
        .datasheet-container {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            margin-top: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-header">'
        '<h1>AlfaVed Engenharia Térmica</h1>'
        '<h3>Dimensionador de Trocadores Alfa Laval v3.0</h3>'
        f'<p>Data: {datetime.now().strftime("%d/%m/%Y")}</p>'
        "</div>",
        unsafe_allow_html=True,
    )

    col_in, col_out = st.columns([1, 1.2], gap="large")

    with col_in:
        st.subheader("Configuração do Projeto")
        tag = st.text_input("Tag do Equipamento", "TC-101")
        projeto = st.text_input("Nome do Projeto", "EXPANSÃO PLANTA 02")

        cat_sel = st.selectbox(
            "Categoria", ["Todos", "Gaxetado", "M-Line", "Semi-Soldado", "WideGap"]
        )
        modelos_filt = [
            m for m, d in BANCO_MODELOS.items()
            if cat_sel == "Todos" or d["cat"] == cat_sel
        ]
        modelo = st.selectbox("Modelo Alfa Laval", modelos_filt)

        angulo_sel = st.selectbox(
            "Ângulo da Placa",
            ["Automatico (Recomendado)", "H (45°)", "L (60°)", "Mista (HL = 52.5°)"],
        )

        fluxo_config = st.selectbox(
            "Configuração de Fluxo",
            ["Contra-corrente (Recomendado)", "Co-corrente"],
            help="Contra-corrente: máxima eficiência. Co-corrente: usado em casos específicos de controle térmico."
        )

        pass_manual = st.selectbox(
            "Arranjo de Passes",
            ["Automatico (Recomendado)", "Single Pass (1/1)", "Two Pass (2/2)"],
            help="Single Pass: todas as conexões no cabeçote fixo. Two Pass: conexões em lados opostos."
        )

        st.divider()
        st.subheader("Lado do Produto")
        prod = st.selectbox("Fluido Produto", list(BANCO_FLUIDOS.keys()), key="prod_sel")
        vazao_p = st.number_input("Vazão Produto (kg/h)", 100.0, 500000.0, 5000.0, step=100.0)
        t_in_p = st.number_input("Temp. Entrada Produto (°C)", 0.0, 250.0, 85.0, step=0.5)
        t_out_p = st.number_input("Temp. Saída Produto (°C)", 0.0, 250.0, 10.0, step=0.5)

        st.divider()
        st.subheader("Lado do Serviço")
        serv = st.selectbox("Fluido Serviço", list(BANCO_SERVICOS.keys()), key="serv_sel")
        t_in_s = st.number_input("Temp. Entrada Serviço (°C)", -30.0, 300.0, 2.0, step=0.5)
        t_out_s = st.number_input("Temp. Saída Serviço (°C)", -30.0, 300.0, 7.0, step=0.5)

    # ============================================================================
    # CÁLCULOS DE ENGENHARIA
    # ============================================================================

    d_p = BANCO_FLUIDOS[prod]
    d_s = BANCO_SERVICOS[serv]
    d_m = BANCO_MODELOS[modelo]

    carga_w = (vazao_p * d_p["cp"] * abs(t_in_p - t_out_p)) / 3600.0
    carga_kw = carga_w / 1000.0

    is_vapor = d_s["tipo"] == "vapor"
    if is_vapor:
        hfg = get_calor_latente(t_in_s)
        vazao_s_calc = (carga_w * 3600.0) / (hfg * 1000) if hfg > 0 else 0.0
    else:
        dt_s = abs(t_out_s - t_in_s)
        if dt_s > 0:
            vazao_s_calc = calc_vazao_servico(carga_w, d_s["cp"], dt_s)
        else:
            vazao_s_calc = 0.0

    fluxo_tipo = "co" if "Co" in fluxo_config else "contra"
    lmtd = calc_lmtd(t_in_p, t_out_p, t_in_s, t_out_s, fluxo=fluxo_tipo)

    arranjo, nome_arranjo, desc_arranjo = get_pass_arrangement(
        vazao_p, lmtd, max(t_in_p, t_out_p), modo_manual=pass_manual
    )
    n_passes_int = 2 if arranjo == "2/2" else 1
    conexoes = determinar_conexoes(arranjo)

    T1 = max(t_in_p, t_out_p)
    T2 = min(t_in_p, t_out_p)
    t1_cold = min(t_in_s, t_out_s)
    t2_cold = max(t_in_s, t_out_s)
    dt_hot = abs(T1 - T2)
    dt_cold = abs(t2_cold - t1_cold)
    P_f = dt_cold / (T1 - t1_cold) if (T1 - t1_cold) > 0 else 0.5
    R_f = dt_hot / dt_cold if dt_cold > 0 else 1.0
    fator_f = calc_fator_f_corrigido(P_f, R_f, n_passes_int)

    # Iteração placas
    U_teorico = 4000.0
    area_estimada = calc_area(carga_w, U_teorico, lmtd, fator_f)
    n_placas_est = calc_num_placas(area_estimada, d_m["area"])

    re_p = calc_reynolds_real(vazao_p, d_p["visc"], d_p["dens"], d_m["dh"], d_m["canal_larg"], n_placas_est)
    re_s = calc_reynolds_real(vazao_s_calc, d_s["visc"], d_s["dens"], d_m["dh"], d_m["canal_larg"], n_placas_est)

    pr_p = calc_prandtl(d_p["cp"], d_p["visc"], d_p["cond"])
    pr_s = calc_prandtl(d_s["cp"], d_s["visc"], d_s["cond"])

    nu_p = calc_nusselt_placa(re_p, pr_p, angulo_sel)
    nu_s = calc_nusselt_placa(re_s, pr_s, angulo_sel)

    h_p = calc_h_coef(nu_p, d_p["cond"], d_m["dh"])
    h_s = calc_h_coef(nu_s, d_s["cond"], d_m["dh"])

    U_calc = calc_u_global(h_p, h_s, esp_placa=0.0005, k_placa=17.0)

    area_req = calc_area(carga_w, U_calc, lmtd, fator_f)
    n_placas = calc_num_placas(area_req, d_m["area"])

    # Recalcular com número final
    re_p = calc_reynolds_real(vazao_p, d_p["visc"], d_p["dens"], d_m["dh"], d_m["canal_larg"], n_placas)
    re_s = calc_reynolds_real(vazao_s_calc, d_s["visc"], d_s["dens"], d_m["dh"], d_m["canal_larg"], n_placas)
    nu_p = calc_nusselt_placa(re_p, pr_p, angulo_sel)
    nu_s = calc_nusselt_placa(re_s, pr_s, angulo_sel)
    h_p = calc_h_coef(nu_p, d_p["cond"], d_m["dh"])
    h_s = calc_h_coef(nu_s, d_s["cond"], d_m["dh"])
    U_calc = calc_u_global(h_p, h_s)
    area_req = calc_area(carga_w, U_calc, lmtd, fator_f)
    n_placas = calc_num_placas(area_req, d_m["area"])

    dp_p = calc_press_drop_real(re_p, n_placas, angulo_sel, vazao_p, d_p["dens"], d_m["canal_larg"], d_m["dh"], d_p["visc"])
    dp_s = calc_press_drop_real(re_s, n_placas, angulo_sel, vazao_s_calc, d_s["dens"], d_m["canal_larg"], d_m["dh"], d_s["visc"])

    t_max = max(t_in_p, t_out_p, t_in_s, t_out_s)
    gaxeta, gaxeta_desc = recomendar_gaxeta(prod, serv, t_max)

    correcoes = gerar_correcoes(
        [], dp_p, dp_s, re_p, re_s, fator_f, angulo_sel, arranjo, n_placas, lmtd
    )

    # Contatos
    resp = CONTATOS_ALFAVED["responsavel_projeto"]
    diretor = CONTATOS_ALFAVED["diretor_engenharia"]

    # ============================================================================
    # TABS: DIMENSIONADOR + DATASHEET TÉCNICO
    # ============================================================================

    tab_dim, tab_ds = st.tabs(["Dimensionador", "Datasheet Técnico"])

    with tab_dim:
        st.subheader("Resultados do Dimensionamento")

        m1, m2, m3 = st.columns(3)
        m1.metric("Carga Térmica", f"{carga_kw:.1f} kW")
        m2.metric("LMTD", f"{lmtd:.1f} °C")
        m3.metric("Fator F", f"{fator_f:.3f}")

        m4, m5, m6 = st.columns(3)
        m4.metric("Área Req.", f"{area_req:.2f} m²")
        m5.metric("Nº Placas", f"{n_placas}")
        m6.metric("U Global", f"{U_calc:.0f} W/m²K")

        st.markdown("#### Diagnóstico Térmico")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.metric("Re Produto", f"{re_p:,.0f}")
            st.metric("Pr Produto", f"{pr_p:.2f}")
            st.metric("h Produto", f"{h_p:.0f} W/m²K")
        with col_d2:
            st.metric("Re Serviço", f"{re_s:,.0f}")
            st.metric("Pr Serviço", f"{pr_s:.2f}")
            st.metric("h Serviço", f"{h_s:.0f} W/m²K")

        regime_p = "Laminar" if re_p < 2000 else ("Transição" if re_p < 10000 else "Turbulento")
        regime_s = "Laminar" if re_s < 2000 else ("Transição" if re_s < 10000 else "Turbulento")
        st.caption(f"Regime Produto: **{regime_p}** | Regime Serviço: **{regime_s}**")

        st.markdown("#### Arranjo de Passes")
        if pass_manual == "Automatico (Recomendado)":
            st.info(f"**{nome_arranjo}** ({arranjo}) — {desc_arranjo}")
        else:
            st.success(f"**{nome_arranjo}** ({arranjo}) — Seleção manual do usuário")

        st.markdown("#### Configuração de Conexões")
        st.markdown(
            f"""
            | | Entrada | Saída |
            |---|---|---|
            | **Produto** | {conexoes['produto_entrada']} | {conexoes['produto_saida']} |
            | **Serviço** | {conexoes['servico_entrada']} | {conexoes['servico_saida']} |
            """
        )
        st.caption(conexoes["descricao"])

        st.markdown("#### Dados do Modelo")
        st.json({
            "Modelo": modelo,
            "Categoria": d_m["cat"],
            "Área/Placa": f"{d_m['area']} m²",
            "P Máx": f"{d_m['Pmax']} bar",
            "T Máx": f"{d_m['Tmax']} °C",
            "Diâm. Hidráulico": f"{d_m['dh']*1000:.1f} mm",
            "Conexão": d_m["conn"],
        })

        st.markdown("#### Recomendação de Vedação")
        st.success(f"**{gaxeta}** — {gaxeta_desc}")

        st.markdown("#### Estimativa de Queda de Pressão")
        col_dp1, col_dp2 = st.columns(2)
        col_dp1.metric("ΔP Produto", f"{dp_p:.2f} kPa")
        col_dp2.metric("ΔP Serviço", f"{dp_s:.2f} kPa")

        st.markdown("#### Verificações de Projeto")
        alertas = []
        if t_max > d_m["Tmax"]:
            alertas.append(f"⚠️ Temperatura máxima ({t_max:.1f}°C) excede limite do modelo ({d_m['Tmax']}°C)")
        if dp_p > 150:
            alertas.append(f"⚠️ ΔP do produto ({dp_p:.1f} kPa) está elevada (>150 kPa)")
        if dp_s > 150:
            alertas.append(f"⚠️ ΔP do serviço ({dp_s:.1f} kPa) está elevada (>150 kPa)")
        if fator_f < 0.75:
            alertas.append(f"⚠️ Fator F ({fator_f:.3f}) baixo — considere aumentar passes ou ajustar temperaturas")
        if re_p < 2000:
            alertas.append(f"ℹ️ Reynolds produto ({re_p:.0f}) em regime laminar — eficiência reduzida")
        if re_s < 2000 and not is_vapor:
            alertas.append(f"ℹ️ Reynolds serviço ({re_s:.0f}) em regime laminar — eficiência reduzida")
        if lmtd < 2.0:
            alertas.append(f"⚠️ LMTD muito baixo ({lmtd:.2f}°C) — verificar temperaturas de projeto")

        if alertas:
            for a in alertas:
                st.warning(a)
        else:
            st.success("✅ Todos os parâmetros dentro dos limites recomendados.")

        if correcoes:
            st.markdown("---")
            st.markdown("#### 🛠️ Diagnóstico e Correções Sugeridas")
            for corr in correcoes:
                card_class = "correcao-card-alta" if corr["prioridade"] == "Alta" else "correcao-card"
                st.markdown(
                    f'<div class="{card_class}">'
                    f'<b>{corr["problema"]}</b> <span style="color:#666;font-size:12px;">(Prioridade: {corr["prioridade"]})</span><br>'
                    f'<span style="font-size:13px;">Valor atual: <b>{corr["valor"]}</b> | Limite: {corr["limite"]}</span><br><br>'
                    f'<b>Ações recomendadas:</b>',
                    unsafe_allow_html=True
                )
                for acao in corr["acoes"]:
                    st.markdown(f"• {acao}")
                st.markdown('</div>', unsafe_allow_html=True)

        data_str = datetime.now().strftime("%d/%m/%Y")
        pdf_buffer = gerar_pdf(
            tag, projeto, modelo, angulo_sel, nome_arranjo, conexoes, fluxo_config, pass_manual,
            prod, vazao_p, t_in_p, t_out_p,
            serv, vazao_s_calc, t_in_s, t_out_s,
            carga_kw, carga_w, area_req, n_placas, lmtd, fator_f,
            re_p, re_s, pr_p, pr_s, h_p, h_s, U_calc,
            dp_p, dp_s, gaxeta, gaxeta_desc,
            correcoes, data_str, CONTATOS_ALFAVED,
        )

        st.download_button(
            label="📄 Baixar Relatório Técnico (PDF)",
            data=pdf_buffer,
            file_name=f"AlfaVed_{tag}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # ============================================================================
    # ABA DATASHEET TÉCNICO
    # ============================================================================

    with tab_ds:
        st.subheader(f"Datasheet Técnico — Alfa Laval {modelo}")

        col_ds1, col_ds2 = st.columns([1, 1.5])

        with col_ds1:
            st.markdown("#### Especificações Mecânicas")
            specs = {
                "Modelo": modelo,
                "Categoria": d_m["cat"],
                "Largura (W)": f"{d_m['width']} mm",
                "Altura (H)": f"{d_m['height']} mm",
                "Dist. vertical portas": f"{d_m['v_dist']} mm",
                "Dist. horizontal portas": f"{d_m['h_dist']} mm",
                "Diâmetro da porta": f"DN{d_m['port_diam']} ({d_m['conn']})",
                "Espessura da placa": f"{d_m['esp']*1000:.1f} mm",
                "Parafuso de compressão": d_m["bolt_size"],
                "Peso por placa": f"{d_m['weight_per_plate']} kg",
                "Pressão máxima": f"{d_m['Pmax']} bar",
                "Temperatura máxima": f"{d_m['Tmax']} °C",
                "Área de troca/placa": f"{d_m['area']} m²",
                "Comprimento mínimo": f"{d_m['min_length']} mm",
                "Comprimento máximo": f"{d_m['max_length']} mm",
            }
            for k, v in specs.items():
                st.markdown(f"**{k}:** {v}")

            st.markdown("---")
            st.markdown("#### Resultados do Dimensionamento")
            st.markdown(f"**Carga Térmica:** {carga_kw:.2f} kW")
            st.markdown(f"**Área Requerida:** {area_req:.2f} m²")
            st.markdown(f"**Número de Placas:** {n_placas}")
            st.markdown(f"**LMTD:** {lmtd:.2f} °C")
            st.markdown(f"**U Global:** {U_calc:.0f} W/m²K")
            st.markdown(f"**Gaxeta:** {gaxeta}")

        with col_ds2:
            st.markdown("#### Desenho Dimensional")
            svg_code = generate_dimensional_svg(modelo, d_m, n_placas)
            st.components.v1.html(svg_code, height=440, scrolling=False)

        st.markdown("---")
        st.markdown("#### Dados de Processo")
        proc_data = {
            "Parâmetro": ["Fluido", "Vazão (kg/h)", "Temp. Entrada (°C)", "Temp. Saída (°C)"],
            "Produto": [prod, f"{vazao_p:,.0f}", f"{t_in_p:.1f}", f"{t_out_p:.1f}"],
            "Serviço": [serv, f"{vazao_s_calc:,.0f}", f"{t_in_s:.1f}", f"{t_out_s:.1f}"],
        }
        st.dataframe(proc_data, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### Contatos Técnicos AlfaVed")

        st.markdown(
            f'<div class="contact-card-person">'
            f'<b>{resp["cargo"]}</b><br>'
            f'<span style="font-size:16px;">{resp["nome"]}</span><br>'
            f'📧 <a href="mailto:{resp["email"]}">{resp["email"]}</a> | '
            f'📞 {resp["telefone"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="contact-card-person">'
            f'<b>{diretor["cargo"]}</b><br>'
            f'<span style="font-size:16px;">{diretor["nome"]}</span><br>'
            f'📧 <a href="mailto:{diretor["email"]}">{diretor["email"]}</a> | '
            f'📞 {diretor["telefone"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="contact-card">'
            "<b>AlfaVed Soluções Industriais</b><br>"
            "Engenharia de Vedação Industrial<br>"
            "Suporte técnico: engenharia@alfaved.com.br"
            "</div>",
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    main()
