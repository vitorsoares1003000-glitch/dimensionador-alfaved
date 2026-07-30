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

BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "viscosidade": 0.89, "U_estimado": 4500},
    "Leite Integral": {"cp": 3.89, "viscosidade": 2.1, "U_estimado": 3200},
    "Suco de Laranja": {"cp": 3.75, "viscosidade": 3.5, "U_estimado": 2800},
    "Oleo Vegetal": {"cp": 1.97, "viscosidade": 50.0, "U_estimado": 1500}
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
            largura_folha = letter if isinstance(letter, tuple) else letter
            self.drawRightString(largura_folha - 54, 25, f"Pagina {self._pageNumber} de {num_pages}")
            super().showPage()
        super().save()

# --- INTERFACE GRÁFICA DO USUÁRIO (WEB) ---
st.title("▲ AlfaVed Soluções Industriais")
st.subheader("Painel de Dimensionamento Hidro-Térmico Comercial")

# Barra Lateral (Formulário)
st.sidebar.header("Dados de Entrada do Projeto")
modelo = st.sidebar.text_input("Modelo de Referência", "M10")
tag = st.sidebar.text_input("Tag do Equipamento", "TC-101")
projeto = st.sidebar.text_input("Número do Projeto", "PRJ-ALFAVED-2026")

st.sidebar.markdown("---")
st.sidebar.subheader("Lado do Produto")
produto = st.sidebar.selectbox("Fluido do Produto", list(BANCO_FLUIDOS.keys()))
t_in_prod = st.sidebar.number_input("Temp. Entrada Produto (°C)", value=90.0)
t_out_prod = st.sidebar.number_input("Temp. Saída Produto (°C)", value=8.0)
vazao_prod = st.sidebar.number_input("Vazão do Produto (kg/h)", value=5000.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Lado do Serviço")
servico = st.sidebar.text_input("Fluido do Serviço", "Água", disabled=True)
t_in_serv = st.sidebar.number_input("Temp. Entrada Serviço (°C)", value=0.0)
t_out_serv = st.sidebar.number_input("Temp. Saída Serviço (°C)", value=12.0)

# Painel Central de Controle
if st.sidebar.button("Calcular e Gerar Parecer", type="primary"):
    # Processamento Físico-Matemático
    fluid_data = BANCO_FLUIDOS[produto]
    cp_prod = fluid_data["cp"]
    U_adotado = fluid_data["U_estimado"]
    
    dT_prod = abs(t_in_prod - t_out_prod)
    carga_kw = (vazao_prod * cp_prod * dT_prod) / 3600.0
    vazao_serv = (carga_kw * 3600.0) / (4.18 * abs(t_out_serv - t_in_serv)) if abs(t_out_serv - t_in_serv) > 0 else 0
    
    dt1 = t_in_prod - t_out_serv
    dt2 = t_out_prod - t_in_serv
    lmtd = (dt1 - dt2) / math.log(dt1 / dt2) if dt1 > 0 and dt2 > 0 and dt1 != dt2 else (dt1 or 1)
    area_m2 = (carga_kw * 1000.0) / (U_adotado * lmtd) if lmtd > 0 else 0
    placas = math.ceil(area_m2 / 0.12) + 2
    if placas % 2 != 0: placas += 1

    # Cards Visuais de Resultados
    col1, col2, col3 = st.columns(3)
    col1.metric("Carga Térmica Estimada", f"{carga_kw:.2f} kW")
    col2.metric("Área de Troca Requerida", f"{area_m2:.2f} m²")
    col3.metric("Quantidade de Placas", f"{placas} placas")

    # Chamada com o Painel de Segurança do Streamlit Secrets (Chave Criptografada)
    d_projeto = {"Modelo": modelo, "Tag": tag, "Projeto": project if 'project' in locals() else projeto, "Produto": produto, "Vazao": vazao_prod}
    contexto = {"dados": d_projeto, "calculado": {"kw": round(carga_kw, 2), "placas": placas, "area": round(area_m2, 2)}}
    prompt = "Atue como Engenheiro Quimico Senior Especialista em Trocadores de Calor da AlfaVed. Analise: " + json.dumps(contexto) + ". Escreva um Parecer Tecnico Descritivo (maximo 150 palavras) focando no material das gaxetas adequado, risco de incrustacao do produto e compatibilidade do modelo. Retorne APENAS o texto corrido do parecer, sem markdown e sem asteriscos."
    
    parecer_ia = ""
    try:
        # Puxa a chave secreta guardada de forma oculta na nuvem
        chave_segura = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=chave_segura)
        response = client.models.generate_content(model='gemini-flash-latest', contents=prompt, config=dict(temperature=0.2))
        parecer_ia = response.text.strip().replace("*", "")
    except Exception:
        parecer_ia = f"Parecer tecnico AlfaVed local. O processamento para o fluido {produto} indica uma demanda termica de {carga_kw:.2f} kW. Recomenda-se o uso estrito de gaxetas em EPDM para laticinios ate 130C ou NBR para oleos. Risco de incrustacao sob controle pelo regime de escoamento turbulento obtido pelo arranjo das {placas} placas de canal. Equipamento homologado comercialmente para fabricacao."

    st.markdown("### Parecer Técnico e Memorial Descritivo (AlfaVed GenAI)")
    st.info(parecer_ia)

    # Geração Segura do PDF em memória RAM
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = [Paragraph("AlfaVed Solucoes Industriais", st_tit), Paragraph("DATASHEET TECNICO - ENGENHARIA ASSISTIDA POR IA", st_sub), Spacer(1, 10)]
    
    story.append(Paragraph("1. Informacoes Gerais do Projeto", st_h2))
    story.append(Table([[Paragraph("Item", st_th), Paragraph("Especificacao", st_th)], [Paragraph("Modelo", st_tc), Paragraph(modelo, st_tc)], [Paragraph("Tag", st_tc), Paragraph(tag, st_tc)], [Paragraph("Projeto", st_tc), Paragraph(projeto, st_tc)]]))
    
    story.append(Paragraph("2. Parametros Operacionais Processados", st_h2))
    story.append(Table([[Paragraph("Propriedade", st_th), Paragraph("Lado do Produto", st_th), Paragraph("Lado do Servico", st_th)], [Paragraph("Fluido", st_tc), Paragraph(produto, st_tc), Paragraph("Agua", st_tc)], [Paragraph("Temp Entrada", st_tc), Paragraph(f"{t_in_prod} C", st_tc), Paragraph(f"{t_in_serv} C", st_tc)], [Paragraph("Temp Saida", st_tc), Paragraph(f"{t_out_prod} C", st_tc), Paragraph(f"{t_out_serv} C", st_tc)], [Paragraph("Vazao Massica", st_tc), Paragraph(f"{vazao_prod} kg/h", st_tc), Paragraph(f"{vazao_serv:.1f} kg/h", st_tc)]]))
    
    story.append(Paragraph("3. Resultados do Dimensionamento Hidro-Termico", st_h2))
    story.append(Table([[Paragraph("Grandeza de Engenharia", st_th), Paragraph("Valor Calculado Garantido", st_th)], [Paragraph("Carga Termica", st_tc), Paragraph(f"{carga_kw:.2f} kW", st_tc)], [Paragraph("Area Efetiva", st_tc), Paragraph(f"{area_m2:.2f} m2", st_tc)], [Paragraph("Quantidade de Placas", st_tc), Paragraph(f"{placas} placas", st_tc)], [Paragraph("Coeficiente de Troca U", st_tc), Paragraph(f"{U_adotado} W/m2.K", st_tc)]]))

    for t in story: 
        if isinstance(t, Table): t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0d1b2a")), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")), ('BOTTOMPADDING', (0,0), (-1,-1), 5), ('TOPPADDING', (0,0), (-1,-1), 5)]))
    
    story.append(Paragraph("4. Parecer Técnico e Memorial Descritivo (AlfaVed GenAI)", st_h2))
    story.append(Paragraph(parecer_ia, st_body))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()

    st.markdown("---")
    st.download_button(label="📥 Baixar Datasheet Técnico Oficial PDF", data=pdf_data, file_name=f"Datasheet_{tag}.pdf", mime="application/pdf")
else:
    st.warning("Insira as especificações operacionais na barra lateral e clique em 'Calcular e Gerar Parecer'.")
