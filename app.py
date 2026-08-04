"""
AlfaVed Engenharia Térmica - Dimensionador PHE
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
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# ============================================================================
# BANCO DE DADOS TÉCNICO
# ============================================================================

BANCO_MODELOS = {
    "M3": {"area": 0.03, "U": 3800, "Pmax": 16, "Tmax": 180, "dh": 0.003, "conn": "1.25\"", "cat": "Gaxetado"},
    "M6-B": {"area": 0.15, "U": 4200, "Pmax": 10, "Tmax": 180, "dh": 0.005, "conn": "2\"", "cat": "Gaxetado"},
    "TS6M": {"area": 0.26, "U": 4600, "Pmax": 25, "Tmax": 180, "dh": 0.006, "conn": "2.5\"", "cat": "Gaxetado"},
    "M10-B": {"area": 0.24, "U": 4500, "Pmax": 10, "Tmax": 180, "dh": 0.006, "conn": "4\"", "cat": "Gaxetado"},
    "TS20M": {"area": 0.95, "U": 4950, "Pmax": 25, "Tmax": 180, "dh": 0.009, "conn": "8\"", "cat": "Gaxetado"},
    "T20-B": {"area": 0.85, "U": 4800, "Pmax": 10, "Tmax": 180, "dh": 0.009, "conn": "8\"", "cat": "Gaxetado"},
    "M15-B": {"area": 0.36, "U": 4700, "Pmax": 10, "Tmax": 180, "dh": 0.008, "conn": "6\"", "cat": "Gaxetado"},
    "MA30-S WideGap": {"area": 1.38, "U": 3800, "Pmax": 25, "Tmax": 180, "dh": 0.012, "conn": "12\"", "cat": "WideGap"},
    "WideGap 350": {"area": 1.80, "U": 3700, "Pmax": 10, "Tmax": 180, "dh": 0.015, "conn": "14\"", "cat": "WideGap"},
    "M6-M": {"area": 0.15, "U": 4250, "Pmax": 25, "Tmax": 180, "dh": 0.005, "conn": "2\"", "cat": "M-Line"},
    "M10-M": {"area": 0.24, "U": 4550, "Pmax": 40, "Tmax": 180, "dh": 0.006, "conn": "4\"", "cat": "M-Line"},
    "M15-M": {"area": 0.36, "U": 4750, "Pmax": 25, "Tmax": 180, "dh": 0.008, "conn": "6\"", "cat": "M-Line"},
    "T20-M": {"area": 0.85, "U": 4900, "Pmax": 30, "Tmax": 180, "dh": 0.009, "conn": "8\"", "cat": "M-Line"},
    "M10-BW": {"area": 0.24, "U": 4600, "Pmax": 55, "Tmax": 250, "dh": 0.005, "conn": "4\"", "cat": "Semi-Soldado"},
    "MK15-BW": {"area": 0.42, "U": 4650, "Pmax": 41, "Tmax": 200, "dh": 0.006, "conn": "6\"", "cat": "Semi-Soldado"},
    "TK20-BW": {"area": 0.68, "U": 4700, "Pmax": 63, "Tmax": 200, "dh": 0.006, "conn": "8\"", "cat": "Semi-Soldado"},
    "T20-W": {"area": 0.85, "U": 4800, "Pmax": 30, "Tmax": 180, "dh": 0.009, "conn": "8\"", "cat": "Semi-Soldado"},
    "MA30-W": {"area": 1.40, "U": 4900, "Pmax": 40, "Tmax": 180, "dh": 0.010, "conn": "12\"", "cat": "Semi-Soldado"},
}

BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "visc": 0.89, "dens": 1000, "tipo": "base"},
    "Leite Integral": {"cp": 3.89, "visc": 2.1, "dens": 1030, "tipo": "alimento"},
    "Leite Desnatado": {"cp": 3.95, "visc": 1.5, "dens": 1020, "tipo": "alimento"},
    "Suco de Laranja": {"cp": 3.75, "visc": 3.5, "dens": 1040, "tipo": "alimento"},
    "Suco de Maca": {"cp": 3.70, "visc": 2.8, "dens": 1035, "tipo": "alimento"},
    "Oleo Vegetal": {"cp": 1.97, "visc": 50.0, "dens": 920, "tipo": "oleo"},
    "Oleo Mineral": {"cp": 1.88, "visc": 100.0, "dens": 880, "tipo": "oleo"},
    "Melado": {"cp": 2.80, "visc": 150.0, "dens": 1380, "tipo": "viscoso"},
    "Cerveja": {"cp": 4.10, "visc": 1.5, "dens": 1010, "tipo": "alimento"},
    "Vinho": {"cp": 3.85, "visc": 1.2, "dens": 1000, "tipo": "alimento"},
    "Chocolate Quente": {"cp": 3.50, "visc": 8.0, "dens": 1050, "tipo": "alimento"},
    "Polpa de Fruta": {"cp": 3.60, "visc": 5.0, "dens": 1050, "tipo": "alimento"},
    "Soro de Leite": {"cp": 3.95, "visc": 1.2, "dens": 1025, "tipo": "alimento"},
    "Creme de Leite": {"cp": 3.50, "visc": 12.0, "dens": 980, "tipo": "alimento"},
    "Iogurte": {"cp": 3.70, "visc": 25.0, "dens": 1060, "tipo": "alimento"},
    "Nata": {"cp": 3.40, "visc": 15.0, "dens": 970, "tipo": "alimento"},
    "Manteiga Derretida": {"cp": 2.10, "visc": 40.0, "dens": 910, "tipo": "oleo"},
}

BANCO_SERVICOS = {
    "Agua Fria": {"cp": 4.18, "visc": 0.89, "dens": 1000, "tipo": "base"},
    "Agua Gelada": {"cp": 4.18, "visc": 1.3, "dens": 1000, "tipo": "base"},
    "Agua Morna": {"cp": 4.18, "visc": 0.65, "dens": 995, "tipo": "base"},
    "Agua Quente": {"cp": 4.18, "visc": 0.35, "dens": 960, "tipo": "base"},
    "Vapor Saturado": {"cp": 2.0, "visc": 0.015, "dens": 0.6, "tipo": "vapor"},
    "Oleo Termico": {"cp": 2.50, "visc": 5.0, "dens": 850, "tipo": "oleo"},
    "Refrigerante R22": {"cp": 1.45, "visc": 0.018, "dens": 450, "tipo": "gas"},
    "R410A": {"cp": 1.60, "visc": 0.020, "dens": 480, "tipo": "gas"},
    "R134a": {"cp": 1.52, "visc": 0.019, "dens": 470, "tipo": "gas"},
    "R717 (NH3)": {"cp": 4.70, "visc": 0.25, "dens": 682, "tipo": "gas"},
    "R744 (CO2)": {"cp": 3.50, "visc": 0.07, "dens": 1100, "tipo": "gas"},
    "Ar Comprimido": {"cp": 1.01, "visc": 0.018, "dens": 1.2, "tipo": "gas"},
    "Glicol 30%": {"cp": 3.70, "visc": 3.5, "dens": 1040, "tipo": "base"},
    "Glicol 50%": {"cp": 3.50, "visc": 6.0, "dens": 1070, "tipo": "base"},
}

# ============================================================================
# FUNÇÕES DE ENGENHARIA
# ============================================================================

def get_calor_latente(temp):
    if temp >= 150:
        return 2114.0
    if temp >= 130:
        return 2174.0
    if temp >= 110:
        return 2230.0
    if temp >= 100:
        return 2257.0
    if temp >= 80:
        return 2308.0
    return 2358.0

def calc_reynolds(vazao_kgh, visc_cp, dens_kgm3, dh_m):
    """Calcula Reynolds aproximado."""
    if vazao_kgh <= 0 or visc_cp <= 0 or dens_kgm3 <= 0:
        return 0.0
    vazao_kgs = vazao_kgh / 3600.0
    area_canal = 0.0001  # simplificação para estimativa inicial
    u = vazao_kgs / (dens_kgm3 * area_canal)
    visc_pas = visc_cp * 0.001
    re = (dens_kgm3 * u * dh_m) / visc_pas
    return max(0.0, re)

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

def calc_press_drop(re, n_placas, angulo):
    factor = 1.5 if "H" in angulo else 1.0
    if re == 0:
        return 0.0
    dp = 0.5 * factor * (1000.0 / re) * (n_placas / 10.0)
    return dp

def get_pass_arrangement(vazao_kgh, lmtd):
    if vazao_kgh > 20000 or lmtd < 2.0:
        return "2/2", "Two Pass", "Necessário para aproximar temperaturas ou gerenciar alta vazão."
    return "1/1", "Single Pass", "Arranjo padrão para eficiência máxima e manutenção facilitada."

def determinar_conexoes(arranjo_passe):
    """
    Define onde os fluidos entram e saem.
    - Single Pass (1/1): Todas as 4 conexões no cabeçote FIXO.
    - Two Pass (2/2): Cada fluido precisa de conexões em LADOS OPOSTOS
      para permitir a reversão de fluxo no segundo passe.
    """
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
        # TWO PASS: conexões obrigatoriamente em lados opostos
        return {
            "produto_entrada": "Cabeçote Fixo (Frame Plate)",
            "produto_saida": "Prato de Pressão (Pressure Plate)",
            "servico_entrada": "Prato de Pressão (Pressure Plate)",
            "servico_saida": "Cabeçote Fixo (Frame Plate)",
            "descricao": (
                "Arranjo 2/2: Conexões em lados opostos obrigatoriamente. "
                "Cada fluido entra de um lado, percorre o 1º passe, "
                "chega ao cabeçote oposto e retorna no 2º passe. "
                "Port Arrangement alternado (U-type ou Z-type)."
            ),
            "port_arrangement": "Pass 1: Fixo -> Móvel | Pass 2: Móvel -> Fixo",
        }

def calc_lmtd(t1, t2, t3, t4):
    """LMTD para contracorrente."""
    dt1 = abs(t1 - t4)
    dt2 = abs(t2 - t3)
    if dt1 <= 0 or dt2 <= 0:
        return 0.1
    lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
    return lmtd

def calc_nusselt(re, pr):
    if re <= 0 or pr <= 0:
        return 5.0
    if re < 2000:
        return 0.664 * (re ** 0.5) * (pr ** 0.33)
    return 0.037 * (re ** 0.8) * (pr ** 0.33)

def calc_h(nu, k, dh):
    if dh <= 0:
        return 0.0
    return (nu * k) / dh

def calc_area(Q_kw, U, lmtd, F=0.95):
    if U <= 0 or lmtd <= 0:
        return 0.0
    Q_w = Q_kw * 1000.0
    A = Q_w / (U * lmtd * F)
    return A

def calc_vazao_servico(Q_kw, cp, dt):
    if cp <= 0 or dt <= 0:
        return 0.0
    Q_kcal_h = Q_kw * 860.0
    vazao = Q_kcal_h / (cp * dt)
    return vazao

def calc_num_placas(area_total, area_placa):
    if area_placa <= 0:
        return 0
    n = math.ceil(area_total / area_placa)
    # garantir paridade mínima e canais
    if n < 3:
        n = 3
    return n

# ============================================================================
# GERAÇÃO DE PDF TÉCNICO
# ============================================================================

def gerar_pdf(
    tag, projeto, modelo, angulo, arranjo, conexoes,
    prod, vazao_p, t_in_p, t_out_p,
    serv, vazao_s_calc, t_in_s, t_out_s,
    carga_kw, area_req, n_placas, lmtd, re_p, re_s,
    dp_p, dp_s, gaxeta, gaxeta_desc,
    data_str,
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "TitleCustom",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#003049"),
        spaceAfter=12,
        alignment=1,
    )
    style_heading2 = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#003049"),
        spaceAfter=8,
        spaceBefore=10,
    )
    style_normal = styles["Normal"]
    style_normal.fontSize = 10
    style_normal.leading = 12

    story = []

    # Cabeçalho
    story.append(Paragraph("<b>AlfaVed Soluções Industriais</b>", style_title))
    story.append(Paragraph("Relatório Técnico de Dimensionamento - Trocador de Calor a Placas", style_normal))
    story.append(Paragraph(f"<b>Data:</b> {data_str}", style_normal))
    story.append(Spacer(1, 12))

    # Info geral
    story.append(Paragraph("<b>1. Informações do Projeto</b>", style_heading2))
    dados_geral = [
        ["Tag do Equipamento", tag],
        ["Projeto", projeto],
        ["Modelo Selecionado", modelo],
        ["Ângulo da Placa", angulo],
        ["Arranjo de Passes", arranjo],
    ]
    t_geral = Table(dados_geral, colWidths=[8 * cm, 8 * cm])
    t_geral.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t_geral)
    story.append(Spacer(1, 10))

    # Conexões
    story.append(Paragraph("<b>2. Configuração de Conexões (Cabeçotes)</b>", style_heading2))
    story.append(Paragraph(f"<b>Descrição:</b> {conexoes['descricao']}", style_normal))
    story.append(Paragraph(f"<b>Port Arrangement:</b> {conexoes['port_arrangement']}", style_normal))
    dados_conn = [
        ["", "Entrada", "Saída"],
        ["Produto", conexoes["produto_entrada"], conexoes["produto_saida"]],
        ["Serviço", conexoes["servico_entrada"], conexoes["servico_saida"]],
    ]
    t_conn = Table(dados_conn, colWidths=[5 * cm, 5.5 * cm, 5.5 * cm])
    t_conn.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003049")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f0f4f8")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t_conn)
    story.append(Spacer(1, 10))

    # Dados operacionais
    story.append(Paragraph("<b>3. Dados Operacionais</b>", style_heading2))
    dados_op = [
        ["Parâmetro", "Produto", "Serviço"],
        ["Fluido", prod, serv],
        ["Vazão (kg/h)", f"{vazao_p:,.0f}", f"{vazao_s_calc:,.0f}"],
        ["Temp. Entrada (°C)", f"{t_in_p:.1f}", f"{t_in_s:.1f}"],
        ["Temp. Saída (°C)", f"{t_out_p:.1f}", f"{t_out_s:.1f}"],
    ]
    t_op = Table(dados_op, colWidths=[6 * cm, 5 * cm, 5 * cm])
    t_op.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003049")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f0f4f8")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t_op)
    story.append(Spacer(1, 10))

    # Resultados térmicos
    story.append(Paragraph("<b>4. Resultados do Dimensionamento</b>", style_heading2))
    dados_res = [
        ["Carga Térmica (kW)", f"{carga_kw:.2f}"],
        ["LMTD (°C)", f"{lmtd:.2f}"],
        ["Área Requerida (m²)", f"{area_req:.2f}"],
        ["Número de Placas", f"{n_placas}"],
        ["Reynolds - Produto", f"{re_p:,.0f}"],
        ["Reynolds - Serviço", f"{re_s:,.0f}"],
        ["ΔP Estimado - Produto (kPa)", f"{dp_p:.2f}"],
        ["ΔP Estimado - Serviço (kPa)", f"{dp_s:.2f}"],
        ["Gaxeta Recomendada", gaxeta],
        ["Observação Gaxeta", gaxeta_desc],
    ]
    t_res = Table(dados_res, colWidths=[8 * cm, 8 * cm])
    t_res.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t_res)
    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "<i>Este relatório foi gerado automaticamente pelo Dimensionador Técnico AlfaVed. "
            "Os valores são estimados e devem ser validados pelo departamento de engenharia.</i>",
            style_normal,
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer

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
            margin-bottom: 10px;
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
        '<h3>Dimensionador de Trocadores Alfa Laval</h3>'
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

    # CÁLCULOS
    d_p = BANCO_FLUIDOS[prod]
    d_s = BANCO_SERVICOS[serv]
    d_m = BANCO_MODELOS[modelo]

    carga_kw = (vazao_p * d_p["cp"] * abs(t_in_p - t_out_p)) / 3600.0

    is_vapor = d_s["tipo"] == "vapor"
    if is_vapor:
        hfg = get_calor_latente(t_in_s)
        vazao_s_calc = (carga_kw * 3600.0) / hfg if hfg > 0 else 0.0
    else:
        dt_s = abs(t_out_s - t_in_s)
        if dt_s > 0:
            vazao_s_calc = calc_vazao_servico(carga_kw, d_s["cp"], dt_s)
        else:
            vazao_s_calc = 0.0

    lmtd = calc_lmtd(t_in_p, t_out_p, t_in_s, t_out_s)

    arranjo, nome_arranjo, desc_arranjo = get_pass_arrangement(vazao_p, lmtd)
    conexoes = determinar_conexoes(arranjo)

    # Estimativa de U
    U_est = d_m["U"]

    # Ajuste U pelo ângulo
    if "L" in angulo_sel:
        U_est *= 1.05
    elif "Mista" in angulo_sel:
        U_est *= 1.02

    area_req = calc_area(carga_kw, U_est, lmtd)
    n_placas = calc_num_placas(area_req, d_m["area"])

    # Reynolds
    re_p = calc_reynolds(vazao_p, d_p["visc"], d_p["dens"], d_m["dh"])
    if is_vapor:
        re_s = 15000.0  # estimativa para vapor
    else:
        re_s = calc_reynolds(vazao_s_calc, d_s["visc"], d_s["dens"], d_m["dh"])

    # Queda de pressão
    dp_p = calc_press_drop(re_p, n_placas, angulo_sel)
    dp_s = calc_press_drop(re_s, n_placas, angulo_sel)

    # Gaxeta
    t_max = max(t_in_p, t_out_p, t_in_s, t_out_s)
    gaxeta, gaxeta_desc = recomendar_gaxeta(prod, serv, t_max)

    with col_out:
        st.subheader("Resultados do Dimensionamento")

        m1, m2, m3 = st.columns(3)
        m1.metric("Carga Térmica", f"{carga_kw:.1f} kW")
        m2.metric("LMTD", f"{lmtd:.1f} °C")
        m3.metric("Área Req.", f"{area_req:.2f} m²")

        m4, m5, m6 = st.columns(3)
        m4.metric("Nº Placas", f"{n_placas}")
        m5.metric("Re Produto", f"{re_p:,.0f}")
        m6.metric("Re Serviço", f"{re_s:,.0f}")

        st.markdown("#### Arranjo de Passes")
        st.info(f"**{nome_arranjo}** ({arranjo}) — {desc_arranjo}")

        st.markdown("#### Configuração de Conexões (Cabeçotes)")
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
        st.json(
            {
                "Modelo": modelo,
                "Categoria": d_m["cat"],
                "Área/Placa": f"{d_m['area']} m²",
                "P Máx": f"{d_m['Pmax']} bar",
                "T Máx": f"{d_m['Tmax']} °C",
                "Diâm. Hidráulico": f"{d_m['dh']*1000:.1f} mm",
                "Conexão": d_m["conn"],
            }
        )

        st.markdown("#### Recomendação de Vedação")
        st.success(f"**{gaxeta}** — {gaxeta_desc}")

        st.markdown("#### Estimativa de Queda de Pressão")
        col_dp1, col_dp2 = st.columns(2)
        col_dp1.metric("ΔP Produto", f"{dp_p:.2f} kPa")
        col_dp2.metric("ΔP Serviço", f"{dp_s:.2f} kPa")

        # PDF
        data_str = datetime.now().strftime("%d/%m/%Y")
        pdf_buffer = gerar_pdf(
            tag, projeto, modelo, angulo_sel, nome_arranjo, conexoes,
            prod, vazao_p, t_in_p, t_out_p,
            serv, vazao_s_calc, t_in_s, t_out_s,
            carga_kw, area_req, n_placas, lmtd, re_p, re_s,
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
