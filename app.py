import streamlit as st
import json
import math
import io
import google.genai as genai

# Configuração da página Web com layout expandido e responsivo
st.set_page_config(page_title="AlfaVed Engenharia", page_icon="▲", layout="wide")

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# --- INJEÇÃO DE DESIGN E APARÊNCIA CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
        .main-hdr { font-size: 32px; font-weight: bold; color: #0d1b2a; margin-bottom: 2px; }
        .sub-hdr { font-size: 15px; color: #555555; margin-bottom: 20px; }
        div.stButton > button:first-child {
            background-color: #0d1b2a !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 10px 24px !important;
            font-weight: bold !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button:first-child:hover {
            background-color: #d90429 !important;
            transform: scale(1.02) !important;
        }
        div.stDownloadButton > button:first-child {
            background-color: #2b7a78 !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 12px 24px !important;
            font-weight: bold !important;
            width: 100% !important;
        }
        div.stDownloadButton > button:first-child:hover {
            background-color: #17252a !important;
        }
        div[data-testid="stMetricSimpleValue"] { font-size: 24px !important; font-weight: bold !important; color: #003049 !important; }
    </style>
""", unsafe_allow_html=True)

# BANCO DE DADOS DE PRODUTOS/FLUIDOS (LADO QUENTE OU FRIO DE PROCESSO)
BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "viscosidade": 0.89},
    "Leite Integral": {"cp": 3.89, "viscosidade": 2.1},
    "Suco de Laranja": {"cp": 3.75, "viscosidade": 3.5},
    "Oleo Vegetal": {"cp": 1.97, "viscosidade": 50.0}
}

# BANCO DE DADOS DE SERVIÇOS (UTILIDADES TÉRMICAS COMPLETO 2026)
BANCO_SERVICOS = {
    "Agua Industrial": {"cp": 4.18, "latente": 0, "tipo": "sensivel"},
    "Glicol 20%": {"cp": 3.85, "latente": 0, "tipo": "sensivel"},
    "Glicol 30%": {"cp": 3.65, "latente": 0, "tipo": "sensivel"},
    "Vapor Saturado": {"cp": 0, "latente": 2200.0, "tipo": "latente"},
    "Amonia Anidra (R717)": {"cp": 0, "latente": 1260.0, "tipo": "latente"}
}

# BANCO DE DADOS DE MODELOS DE PLACAS ALFA LAVAL
BANCO_MODELOS = {
    "Alfa Laval M3": {"area_placa": 0.03, "U_base": 3800},
    "Alfa Laval TL3": {"area_placa": 0.06, "U_base": 3900},
    "Alfa Laval M6": {"area_placa": 0.14, "U_base": 4200},
    "Alfa Laval M6-M": {"area_placa": 0.16, "U_base": 4250},
    "Alfa Laval TL6": {"area_placa": 0.21, "U_base": 4300},
    "Alfa Laval M10": {"area_placa": 0.24, "U_base": 4500},
    "Alfa Laval M10-M": {"area_placa": 0.34, "U_base": 4550},
    "Alfa Laval TL10": {"area_placa": 0.46, "U_base": 4600},
    "Alfa Laval M15": {"area_placa": 0.61, "U_base": 4700}
}

styles_doc = getSampleStyleSheet()
st_tit = ParagraphStyle('T1', parent=styles_doc['Heading1'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor("#0d1b2a"))
st_sub = ParagraphStyle('T2', parent=styles_doc['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#d90429"), spaceAfter=15)
st_h2 = ParagraphStyle('T3', parent=styles_doc['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#003049"), spaceBefore=10, spaceAfter=5)
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
            largura_real = letter if isinstance(letter, (list, tuple)) else letter
            self.drawRightString(largura_real - 54, 25, f"Pagina {self._pageNumber} de {num_pages}")
            super().showPage()
        super().save()

# --- TOPBANE VISUAL CUSTOMIZADO ---
st.markdown('<div class="main-hdr">▲ AlfaVed Soluções Industriais</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-hdr">Dashboard de Engenharia Térmica Avançada e Dimensionamento Hidrodinâmico</div>', unsafe_allow_html=True)

# Barra Lateral Otimizada
st.sidebar.header("Configurações do Projeto")
modelo = st.sidebar.selectbox("Modelo do Equipamento (Alfa Laval)", list(BANCO_MODELOS.keys()))
tag = st.sidebar.text_input("Tag do Equipamento", "TC-101")
projeto = st.sidebar.text_input("Número do Projeto", "PRJ-ALFAVED-2026")

st.sidebar.markdown("---")
st.sidebar.subheader("Parâmetros do Lado do Produto")
produto = st.sidebar.selectbox("Fluido do Produto", list(BANCO_FLUIDOS.keys()))
t_in_prod = st.sidebar.number_input("Temp. Entrada Produto (°C)", value=90.0)
t_out_prod = st.sidebar.number_input("Temp. Saída Produto (°C)", value=8.0)
vazao_prod = st.sidebar.number_input("Vazão do Produto (kg/h)", value=5000.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Parâmetros do Lado do Serviço")
servico_sel = st.sidebar.selectbox("Fluido do Serviço (Utilidade)", list(BANCO_SERVICOS.keys()))

dados_serv_sel = BANCO_SERVICOS[servico_sel]
if dados_serv_sel["tipo"] == "latente":
    t_in_serv = st.sidebar.number_input("Temp. Sat. do Serviço (°C)", value=120.0 if servico_sel == "Vapor Saturado" else -10.0)
    t_out_serv = t_in_serv
    st.sidebar.caption(f"💡 {servico_sel} opera de forma isotérmica por mudança de fase latente.")
else:
    t_in_serv = st.sidebar.number_input("Temp. Entrada Serviço (°C)", value=0.0)
    t_out_serv = st.sidebar.number_input("Temp. Saída Serviço (°C)", value=12.0)

st.sidebar.markdown("---")
disparar_calculo = st.sidebar.button("Executar Cálculo Térmico Rigoroso", type="primary")

if disparar_calculo:
    dados_fluido = BANCO_FLUIDOS[produto]
    dados_modelo = BANCO_MODELOS[modelo]
    
    cp_prod = dados_fluido["cp"]
    area_por_placa = dados_modelo["area_placa"]
    
    fator_viscosidade = 1.0 if produto == "Agua" else (1.0 / math.isqrt(int(dados_fluido["viscosidade"])))
    U_adotado = dados_modelo["U_base"] * fator_viscosidade
    
    # PROCESSAMENTO FÍSICO-MATEMÁTICO DO PRODUTO
    dT_prod = abs(t_in_prod - t_out_prod)
    carga_kw = (vazao_prod * cp_prod * dT_prod) / 3600.0
    
    # CÁLCULO DO LADO DO SERVIÇO (Sensível vs Latente)
    if dados_serv_sel["tipo"] == "latente":
        vazao_serv = (carga_kw * 3600.0) / dados_serv_sel["latente"]
    else:
        dT_serv = abs(t_out_serv - t_in_serv)
        vazao_serv = (carga_kw * 3600.0) / (dados_serv_sel["cp"] * dT_serv) if dT_serv > 0 else 0
        
    # CÁLCULO DO LMTD
    dt1 = t_in_prod - t_out_serv
    dt2 = t_out_prod - t_in_serv
    
    if dt1 > 0 and dt2 > 0 and dt1 != dt2:
        lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
    elif dt1 == dt2 and dt1 > 0:
        lmtd = dt1
    else:
        lmtd = (abs(dt1) + abs(dt2)) / 2
        
    area_m2 = (carga_kw * 1000.0) / (U_adotado * lmtd) if lmtd > 0 else 0
    
    placas = math.ceil(area_m2 / area_por_placa) + 2
    if placas % 2 != 0: placas += 1

    # EXIBIÇÃO IMEDIATA DOS CARDS DE MÉTRICAS
    st.markdown("### 1. Indicadores Hidro-Térmicos Garantidos")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Carga Térmica Total", f"{carga_kw:.2f} kW")
    m_col2.metric("Área Efetiva Requerida", f"{area_m2:.2f} m²")
    m_col3.metric("Quantidade de Placas", f"{placas} un")
    m_col4.metric(f"Vazão de {servico_sel}", f"{vazao_serv:.1f} kg/h")

    # DEFINE PARECER TÉCNICO DE FORMA LINEAR E SEGURA
    parecer_ia = f"Parecer tecnico AlfaVed. O processamento para {produto} utilizando {servico_sel} no equipamento {modelo} indica uma demanda termica de {carga_kw:.2f} kW. Para operacoes com {servico_sel}, a engenharia especifica o arranjo de {placas} placas de canal. Recomenda-se o uso de gaxetas em EPDM para fluidos aquosos, Viton para vapor de alta temperatura ou elastomeros especiais para Amonia Anidra refrataria."
    
    try:
        contexto_json = f'{{"modelo": "{modelo}", "produto": "{produto}", "carga_kw": {carga_kw:.1f}, "placas": {placas}, "servico": "{servico_sel}", "vazao_serv": {vazao_serv:.1f}}}'
        prompt = f"Atue como Engenheiro Quimico Senior Especialista da AlfaVed. Analise os resultados: {contexto_json}. Escreva um Parecer Tecnico Descritivo (maximo 150 palavras) focando no material das gaxetas adequado (NBR, EPDM, ou gaxetas especiais para Vapor/Amonia), avalie o risco de incrustacao/congelamento do produto, e explique a vantagem deste utilitario específico no processo. Retorne APENAS o texto corrido, sem markdown e sem asteriscos."
        chave_segura = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=chave_segura)
        response = client.models.generate_content(model='gemini-flash-latest', contents=prompt, config=dict(temperature=0.2))
        parecer_ia = response.text.strip().replace("*", "")
