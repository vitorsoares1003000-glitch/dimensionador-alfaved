import gradio as gr
import math
import io

BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "viscosidade": 0.89},
    "Leite Integral": {"cp": 3.89, "viscosidade": 2.1},
    "Suco de Laranja": {"cp": 3.75, "viscosidade": 3.5},
    "Oleo Vegetal": {"cp": 1.97, "viscosidade": 50.0}
}

BANCO_SERVICOS = {
    "Agua Industrial": {"cp": 4.18, "latente": 0.0, "tipo": "sensivel"},
    "Glicol 20%": {"cp": 3.85, "latente": 0.0, "tipo": "sensivel"},
    "Glicol 30%": {"cp": 3.65, "latente": 0.0, "tipo": "sensivel"},
    "Vapor Saturado": {"cp": 0.0, "latente": 2200.0, "tipo": "latente"},
    "Amonia Anidra (R717)": {"cp": 0.0, "latente": 1260.0, "tipo": "latente"}
}

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

def simular_trocador(modelo, tag, projeto, produto, t_in_prod, t_out_prod, vazao_prod, servico_sel, t_in_serv, t_out_serv):
    dados_fluido = BANCO_FLUIDOS[produto]
    dados_modelo = BANCO_MODELOS[modelo]
    dados_serv_sel = BANCO_SERVICOS[servico_sel]
    
    cp_prod = dados_fluido["cp"]
    area_por_placa = dados_modelo["area_placa"]
    
    fator_viscosidade = 1.0 if produto == "Agua" else (1.0 / math.isqrt(int(dados_fluido["viscosidade"])))
    U_adotado = dados_modelo["U_base"] * fator_viscosidade
    
    # Processamento Físico-Matemático
    dT_prod = abs(t_in_prod - t_out_prod)
    carga_kw = (vazao_prod * cp_prod * dT_prod) / 3600.0
    
    if dados_serv_sel["tipo"] == "latente":
        vazao_serv = (carga_kw * 3600.0) / dados_serv_sel["latente"]
        t_out_serv_real = t_in_serv
    else:
        dT_serv = abs(t_out_serv - t_in_serv)
        vazao_serv = (carga_kw * 3600.0) / (dados_serv_sel["cp"] * dT_serv) if dT_serv > 0 else 0
        t_out_serv_real = t_out_serv
        
    dt1 = t_in_prod - t_out_serv_real
    dt2 = t_out_prod - t_in_serv
    
    if dt1 > 0 and dt2 > 0 and dt1 != dt2:
        lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
    else:
        lmtd = (abs(dt1) + abs(dt2)) / 2
        
    area_m2 = (carga_kw * 1000.0) / (U_adotado * lmtd) if lmtd > 0 else 0
    placas = math.ceil(area_m2 / area_por_placa) + 2
    if placas % 2 != 0: placas += 1

    # Regras do Memorial Técnico
    gaxeta_material = "EPDM" if produto != "Oleo Vegetal" else "NBR"
    if servico_sel == "Vapor Saturado": gaxeta_material = "Viton"
    
    relatorio = f"""▲ FOLHA DE DADOS TÉCNICOS - ALFAVED
--------------------------------------------------
1. INFORMAÇÕES GERAIS
• Modelo: {modelo} | Tag: {tag} | Projeto: {projeto}

2. PARÂMETROS OPERACIONAIS
• Lado do Produto ({produto}): {t_in_prod}°C -> {t_out_prod}°C | Vazão: {vazao_prod:.0f} kg/h
• Lado do Serviço ({servico_sel}): {t_in_serv}°C -> {t_out_serv_real}°C | Vazão Requerida: {vazao_serv:.1f} kg/h

3. RESULTADOS DO DIMENSIONAMENTO
• Carga Térmica de Troca: {carga_kw:.2f} kW
• Área Efetiva Requerida: {area_m2:.2f} m²
• Quantidade Final de Placas: {placas} unidades (Área por Placa: {area_por_placa} m²)
• Coeficiente de Troca Adotado (U): {U_adotado:.0f} W/m².K | LMTD: {lmtd:.1f}°C

4. MEMORIAL DESCRITIVO
Equipamento homologado. Especificação recomendada de gaxetas em {gaxeta_material} para contenção e estanqueidade térmica do processo."""

    return f"{carga_kw:.2f} kW", f"{area_m2:.2f} m²", f"{placas} un", f"{vazao_serv:.1f} kg/h", relatorio

# --- MONTAGEM DA INTERFACE VISUAL GRADIO ---
with gr.Blocks(title="AlfaVed Engenharia") as app:
    gr.Markdown("# ▲ AlfaVed Soluções Industriais")
    gr.Markdown("### Painel de Dimensionamento Hidro-Térmico Estável")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("#### ⚙️ Configurações Gerais")
            modelo = gr.Dropdown(choices=list(BANCO_MODELOS.keys()), value="Alfa Laval M10", label="Modelo do Equipamento")
            tag = gr.Textbox(value="TC-101", label="Tag do Equipamento")
            projeto = gr.Textbox(value="PRJ-ALFAVED-2026", label="Número do Projeto")
            
            gr.Markdown("#### 🥛 Lado do Produto")
            produto = gr.Dropdown(choices=list(BANCO_FLUIDOS.keys()), value="Leite Integral", label="Fluido do Produto")
            t_in_prod = gr.Number(value=90.0, label="Temp. Entrada Produto (°C)")
            t_out_prod = gr.Number(value=8.0, label="Temp. Saída Produto (°C)")
            vazao_prod = gr.Number(value=5000.0, label="Vazão do Produto (kg/h)")
            
            gr.Markdown("#### ❄️ Lado do Serviço")
            servico_sel = gr.Dropdown(choices=list(BANCO_SERVICOS.keys()), value="Agua Industrial", label="Fluido do Serviço")
            t_in_serv = gr.Number(value=0.0, label="Temp. Entrada Serviço (°C)")
            t_out_serv = gr.Number(value=12.0, label="Temp. Saída Serviço (°C)")
            
            btn_calcular = gr.Button("Executar Dimensionamento Mecânico", variant="primary")
            
        with gr.Column():
            gr.Markdown("#### 📊 Indicadores de Saída")
            with gr.Row():
                out_kw = gr.Textbox(label="Carga Térmica")
                out_m2 = gr.Textbox(label="Área Necessária")
            with gr.Row():
                out_placas = gr.Textbox(label="Quantidade de Placas")
                out_vazao = gr.Textbox(label="Vazão do Serviço")
                
            gr.Markdown("#### 📄 Datasheet Técnico Oficial")
            out_relatorio = gr.TextArea(label="Folha de Dados Impressa", lines=15)

    btn_calcular.click(
        fn=simular_trocador,
        inputs=[modelo, tag, projeto, produto, t_in_prod, t_out_prod, vazao_prod, servico_sel, t_in_serv, t_out_serv],
        outputs=[out_kw, out_m2, out_placas, out_vazao, out_relatorio]
    )

if __name__ == "__main__":
    app.launch()
