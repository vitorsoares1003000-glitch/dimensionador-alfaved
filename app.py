"""
AlfaVed Engenharia Térmica - Dimensionador PHE v2.1
Arquivo: app.py
Deploy: streamlit run app.py
"""

import io
import math
import streamlit as st
from datetime import datetime

# ReportLab para PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# ============================================================================
# BANCO DE DADOS TÉCNICO
# ============================================================================

BANCO_MODELOS = {
    "M3": {"area": 0.03, "Pmax": 16, "Tmax": 180, "dh": 0.003, "conn": "1.25\"", "cat": "Gaxetado", "placa_larg": 0.08, "placa_comp": 0.25, "canal_larg": 0.07, "esp": 0.0015},
    "M6-B": {"area": 0.15, "Pmax": 10, "Tmax": 180, "dh": 0.005, "conn": "2\"", "cat": "Gaxetado", "placa_larg": 0.15, "placa_comp": 0.40, "canal_larg": 0.14, "esp": 0.0020},
    "TS6M": {"area": 0.26, "Pmax": 25, "Tmax": 180, "dh": 0.006, "conn": "2.5\"", "cat": "Gaxetado", "placa_larg": 0.18, "placa_comp": 0.52, "canal_larg": 0.17, "esp": 0.0025},
    "M10-B": {"area": 0.24, "Pmax": 10, "Tmax": 180, "dh": 0.006, "conn": "4\"", "cat": "Gaxetado", "placa_larg": 0.25, "placa_comp": 0.50, "canal_larg": 0.24, "esp": 0.0025},
    "TS20M": {"area": 0.95, "Pmax": 25, "Tmax": 180, "dh": 0.009, "conn": "8\"", "cat": "Gaxetado", "placa_larg": 0.45, "placa_comp": 0.75, "canal_larg": 0.43, "esp": 0.0030},
    "T20-B": {"area": 0.85, "Pmax": 10, "Tmax": 180, "dh": 0.009, "conn": "8\"", "cat": "Gaxetado", "placa_larg": 0.45, "placa_comp": 0.75, "canal_larg": 0.43, "esp": 0.0030},
    "M15-B": {"area": 0.36, "Pmax": 10, "Tmax": 180, "dh": 0.008, "conn": "6\"", "cat": "Gaxetado", "placa_larg": 0.35, "placa_comp": 0.60, "canal_larg": 0.33, "esp": 0.0030},
    "MA30-S WideGap": {"area": 1.38, "Pmax": 25, "Tmax": 180, "dh": 0.012, "conn": "12\"", "cat": "WideGap", "placa_larg": 0.70, "placa_comp": 1.00, "canal_larg": 0.65, "esp": 0.0050},
    "WideGap 350": {"area": 1.80, "Pmax": 10, "Tmax": 180, "dh": 0.015, "conn": "14\"", "cat": "WideGap", "placa_larg": 0.80, "placa_comp": 1.10, "canal_larg": 0.75, "esp": 0.0060},
    "M6-M": {"area": 0.15, "Pmax": 25, "Tmax": 180, "dh": 0.005, "conn": "2\"", "cat": "M-Line", "placa_larg": 0.15, "placa_comp": 0.40, "canal_larg": 0.14, "esp": 0.0020},
    "M10-M": {"area": 0.24, "Pmax": 40, "Tmax": 180, "dh": 0.006, "conn": "4\"", "cat": "M-Line", "placa_larg": 0.25, "placa_comp": 0.50, "canal_larg": 0.24, "esp": 0.0025},
    "M15-M": {"area": 0.36, "Pmax": 25, "Tmax": 180, "dh": 0.008, "conn": "6\"", "cat": "M-Line", "placa_larg": 0.35, "placa_comp": 0.60, "canal_larg": 0.33, "esp": 0.0030},
    "T20-M": {"area": 0.85, "Pmax": 30, "Tmax": 180, "dh": 0.009, "conn": "8\"", "cat": "M-Line", "placa_larg": 0.45, "placa_comp": 0.75, "canal_larg": 0.43, "esp": 0.0030},
    "M10-BW": {"area": 0.24, "Pmax": 55, "Tmax": 250, "dh": 0.005, "conn": "4\"", "cat": "Semi-Soldado", "placa_larg": 0.25, "placa_comp": 0.50, "canal_larg": 0.24, "esp": 0.0025},
    "MK15-BW": {"area": 0.42, "Pmax": 41, "Tmax": 200, "dh": 0.006, "conn": "6\"", "cat": "Semi-Soldado", "placa_larg": 0.35, "placa_comp": 0.60, "canal_larg": 0.33, "esp": 0.0030},
    "TK20-BW": {"area": 0.68, "Pmax": 63, "Tmax": 200, "dh": 0.006, "conn": "8\"", "cat": "Semi-Soldado", "placa_larg": 0.45, "placa_comp": 0.75, "canal_larg": 0.43, "esp": 0.0030},
    "T20-W": {"area": 0.85, "Pmax": 30, "Tmax": 180, "dh": 0.009, "conn": "8\"", "cat": "Semi-Soldado", "placa_larg": 0.45, "placa_comp": 0.75, "canal_larg": 0.43, "esp": 0.0030},
    "MA30-W": {"area": 1.40, "Pmax": 40, "Tmax": 180, "dh": 0.010, "conn": "12\"", "cat": "Semi-Soldado", "placa_larg": 0.70, "placa_comp": 1.00, "canal_larg": 0.65, "esp": 0.0040},
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
    """Calor latente de vaporização da água (kJ/kg) por temperatura."""
    if temp >= 150: return 2114.0
    if temp >= 130: return 2174.0
    if temp >= 110: return 2230.0
    if temp >= 100: return 2257.0
    if temp >= 80: return 2308.0
    return 2358.0

def calc_reynolds_real(vazao_kgh, visc_pas, dens_kgm3, dh_m, canal_larg_m, n_placas):
    """Cálculo real de Reynolds considerando geometria do trocador."""
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
    """Número de Prandtl."""
    if cond_wm2k <= 0 or visc_pas <= 0:
        return 0.0
    return (visc_pas * cp_jkgk) / cond_wm2k

def calc_nusselt_placa(re, pr, angulo):
    """Correlação de Nusselt para placas corrugadas."""
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
    """Coeficiente convectivo de transferência de calor (W/m²K)."""
    if dh_m <= 0:
        return 0.0
    return (nu * cond_wm2k) / dh_m

def calc_u_global(h_p, h_s, esp_placa=0.0005, k_placa=17.0, r_fp=0.0001, r_fs=0.0001):
    """Coeficiente global U considerando todas as resistências térmicas."""
    if h_p <= 0 or h_s <= 0:
        return 0.0
    r_total = (1.0 / h_p) + r_fp + (esp_placa / k_placa) + r_fs + (1.0 / h_s)
    if r_total <= 0:
        return 0.0
    return 1.0 / r_total

def calc_lmtd(t1_ent, t1_sai, t2_ent, t2_sai, fluxo="contra"):
    """LMTD para contra-corrente ou co-corrente."""
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
    """
    Fator de correção F para LMTD em arranjos multi-passe.
    Versão robusta - evita erros numéricos.
    
    Para PHE a placas:
    - 1/1 (contra-corrente puro): F = 1.0
    - 2/2: F tipicamente 0.92-0.98 para PHE bem projetados
    """
    if n_passes == 1:
        return 1.0
    
    # Limitar P e R para evitar instabilidades
    P = max(0.001, min(0.999, P))
    R = max(0.001, min(10.0, R))
    
    # Para PHE 2/2, usar aproximação simplificada robusta
    # Baseado em Shah & Sekulic (2003) - Heat Exchangers Design Handbook
    # Para arranjos 2/2 em PHE, F é geralmente > 0.9 quando bem projetado
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
    
    # Penalidade se P é muito alto (aproximação térmica excessiva)
    if P > 0.8:
        f_est *= 0.98
    
    return max(0.75, min(1.0, f_est))

def calc_area(Q_w, U, lmtd, F=1.0):
    """Área de transferência de calor (m²)."""
    if U <= 0 or lmtd <= 0 or F <= 0:
        return 0.0
    return Q_w / (U * lmtd * F)

def calc_vazao_servico(Q_w, cp_jkgk, dt):
    """Vazão mássica do serviço (kg/h)."""
    if cp_jkgk <= 0 or dt <= 0:
        return 0.0
    m_dot_kgs = Q_w / (cp_jkgk * dt)
    return m_dot_kgs * 3600.0

def calc_num_placas(area_total, area_placa):
    """Número de placas necessárias."""
    if area_placa <= 0:
        return 0
    n = math.ceil(area_total / area_placa)
    if n < 3:
        n = 3
    if n % 2 == 0:
        n += 1
    return n

def recomendar_gaxeta(fluido_p, fluido_s, t_max):
    """Recomendação de material de vedação."""
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
    """Cálculo realista de queda de pressão."""
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
    dp_canal = 4.0 * f * (comp_hidraulico / dh_m) * (dens_kgm3 * u ** 2 / 2.0)
    
    d_porta = 0.05
    area_porta = math.pi * (d_porta ** 2) / 4.0
    u_porta = vazao_kgs / (dens_kgm3 * area_porta)
    k_local = 3.0
    dp_portas = k_local * (dens_kgm3 * u_porta ** 2 / 2.0)
    
    return (dp_canal + dp_portas) / 1000.0

def get_pass_arrangement(vazao_kgh, lmtd, temp_max):
    """Determina arranjo de passes."""
    if lmtd < 3.0 or vazao_kgh > 20000:
        return "2/2", "Two Pass", "Necessário para melhor aproximação térmica ou gerenciar alta vazão."
    return "1/1", "Single Pass", "Arranjo padrão para máxima eficiência em contra-corrente."

def determinar_conexoes(arranjo_passe):
    """Define onde os fluidos entram e saem."""
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

# ============================================================================
# GERAÇÃO DE PDF TÉCNICO
# ============================================================================

def gerar_pdf(
    tag, projeto, modelo, angulo, arranjo, conexoes, fluxo_config,
    prod, vazao_p, t_in_p, t_out_p,
    serv, vazao_s_calc, t_in_s, t_out_s,
    carga_kw, carga_w, area_req, n_placas, lmtd, fator_f,
    re_p, re_s, pr_p, pr_s, h_p, h_s, U_calc,
    dp_p, dp_s, gaxeta, gaxeta_desc,
    data_str,
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
        ["Arranjo de Passes", arranjo],
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

    story.append(Paragraph("<b>2. Configuração de Conexões</b>", style_h2))
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

    story.append(Paragraph("<b>3. Dados Operacionais</b>", style_h2))
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

    story.append(Paragraph("<b>4. Resultados do Dimensionamento</b>", style_h2))
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

    story.append(
        Paragraph(
            "<i>Este relatório foi gerado automaticamente pelo Dimensionador Técnico AlfaVed. "
            "Os valores são estimados e devem ser validados pelo departamento de engenharia.</i>",
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
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-header">'
        '<h1>AlfaVed Engenharia Térmica</h1>'
        '<h3>Dimensionador de Trocadores Alfa Laval v2.1</h3>'
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

        st.divider()
        st.subheader("Lado do Produto")
        prod = st.selectbox("Fluido Produto", list(BANCO_FLUIDOS.keys()))
        vazao_p = st.number_input("Vazão Produto (kg/h)", 100.0, 500000.0, 5000.0, step=100.0)
        t_in_p = st.number_input("Temp. Entrada Produto (°C)", 0.0, 250.0, 85.0, step=0.5)
        t_out_p = st.number_input("Temp. Saída Produto (°C)", 0.0, 250.0, 10.0, step=0.5)

        st.divider()
        st.subheader("Lado do Serviço")
        serv = st.selectbox("Fluido Serviço", list(BANCO_SERVICOS.keys()))
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

    arranjo, nome_arranjo, desc_arranjo = get_pass_arrangement(vazao_p, lmtd, max(t_in_p, t_out_p))
    n_passes_int = 2 if arranjo == "2/2" else 1
    conexoes = determinar_conexoes(arranjo)

    # Fator F
    T1 = max(t_in_p, t_out_p)
    T2 = min(t_in_p, t_out_p)
    t1 = min(t_in_s, t_out_s)
    t2 = max(t_in_s, t_out_s)
    dt_hot = abs(T1 - T2)
    dt_cold = abs(t2 - t1)
    P_f = dt_cold / (T1 - t1) if (T1 - t1) > 0 else 0.5
    R_f = dt_hot / dt_cold if dt_cold > 0 else 1.0
    fator_f = calc_fator_f_corrigido(P_f, R_f, n_passes_int)

    # Iteração para número de placas e coeficientes
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

    # Recalcular com número final de placas
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

    # ============================================================================
    # PAINEL DE RESULTADOS
    # ============================================================================

    with col_out:
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
        st.info(f"**{nome_arranjo}** ({arranjo}) — {desc_arranjo}")

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
        checks = []
        if t_max > d_m["Tmax"]:
            checks.append(f"⚠️ Temperatura máxima ({t_max:.1f}°C) excede limite do modelo ({d_m['Tmax']}°C)")
        if dp_p > 150:
            checks.append(f"⚠️ ΔP do produto ({dp_p:.1f} kPa) está elevada (>150 kPa)")
        if dp_s > 150:
            checks.append(f"⚠️ ΔP do serviço ({dp_s:.1f} kPa) está elevada (>150 kPa)")
        if fator_f < 0.75:
            checks.append(f"⚠️ Fator F ({fator_f:.3f}) baixo — considere aumentar passes ou ajustar temperaturas")
        if re_p < 2000:
            checks.append(f"ℹ️ Reynolds produto ({re_p:.0f}) em regime laminar — eficiência reduzida")
        if re_s < 2000:
            checks.append(f"ℹ️ Reynolds serviço ({re_s:.0f}) em regime laminar — eficiência reduzida")
        
        if checks:
            for c in checks:
                st.warning(c)
        else:
            st.success("✅ Todos os parâmetros dentro dos limites recomendados.")

        data_str = datetime.now().strftime("%d/%m/%Y")
        pdf_buffer = gerar_pdf(
            tag, projeto, modelo, angulo_sel, nome_arranjo, conexoes, fluxo_config,
            prod, vazao_p, t_in_p, t_out_p,
            serv, vazao_s_calc, t_in_s, t_out_s,
            carga_kw, carga_w, area_req, n_placas, lmtd, fator_f,
            re_p, re_s, pr_p, pr_s, h_p, h_s, U_calc,
            dp_p, dp_s, gaxeta, gaxeta_desc,
            data_str,
        )

        st.download_button(
            label="📄 Baixar Relatório Técnico (PDF)",
            data=pdf_buffer,
            file_name=f"AlfaVed_{tag}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.markdown("---")
        st.markdown(
            '<div class="contact-card">'
            "<b>AlfaVed Soluções Industriais</b><br>"
            "Engenharia de Vedação Industrial<br>"
            "Suporte técnico: comercial@alfaved.com.br"
            "</div>",
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    main()
