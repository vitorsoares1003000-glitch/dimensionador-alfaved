import math
import io
from typing import Dict, Tuple

# Optional imports for PDF generation and web UI
try:
    import streamlit as st
except Exception:
    st = None

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# --- Simple placeholder databases and constants ---
BANCO_MODELOS = {
    "M10": {"tipo": "gaxetado", "pressao_max": 25, "area_placa": 0.1, "U_base": 500.0, "dh": 0.005},
    "S20": {"tipo": "semi-soldado", "pressao_max": 16, "area_placa": 0.08, "U_base": 450.0, "dh": 0.006}
}

BANCO_FLUIDOS = {
    "Agua": {"cp": 4.18, "densidade": 1000.0, "viscosidade": 1.0},
    "Oleo": {"cp": 2.0, "densidade": 860.0, "viscosidade": 10.0}
}

BANCO_SERVICOS = BANCO_FLUIDOS

ANGULOS_PLACA = {
    "30 H": {"descricao": "Alta turbulência, queda de pressão maior", "turbulencia": "Alta", "queda_pressao": "Alta", "fator_placas": 1.2, "fator_placas": 1.2, "fator_placas": 1.2},
    "45 HT": {"descricao": "Muito turbulento", "turbulencia": "Muito Alta", "queda_pressao": "Muito Alta", "fator_placas": 1.3}
}

# Fallback default plate
DEFAULT_PLACA = "30 H"

# Constants
PLACAS_LIMITE_MULTI_PASSE = 80
PLACAS_LIMITE_MULTI_SECAO = 120
VAZAO_RATIO_LIMITE = 2.0
FATOR_SEGURANCA_AREA = 1.1
COEFICIENTE_FOULING = 1.05
PLACA_MINIMA = 4
PLACA_MAXIMA_GAXETADA = 500
PLACA_MAXIMA_SEMI_SOLDADO = 300
TEMP_MIN_VALIDA = -50.0
TEMP_MAX_VALIDA = 300.0

CONTATOS_ALFAVED = {
    "vitor_soares": {"nome": "Vitor Soares", "cargo": "Engenheiro", "email": "vitor@example.com", "telefone": "+55 11 99999-0000"},
    "jhonatan_dias": {"nome": "Jhonatan Dias", "cargo": "Tecnico", "email": "jhonatan@example.com", "telefone": "+55 11 98888-0000"}
}

# --- Utility functions (simple, safe implementations) ---

def calculate_reynolds(vazao_kg_h: float, viscosidade_mPa_s: float, densidade_kg_m3: float, dh: float) -> float:
    """Rough Reynolds number estimation using mass flow -> velocity conversion with assumed area.
    This is a simplified placeholder for demo/testing purposes."""
    if vazao_kg_h <= 0 or viscosidade_mPa_s <= 0:
        return 0.0
    # assume characteristic area = dh (not physical) -> just to produce numbers
    vazao_m3_s = vazao_kg_h / (densidade_kg_m3 * 3600.0)
    area = max(dh * 0.1, 1e-4)
    velocity = vazao_m3_s / area
    # viscosity convert mPa.s to Pa.s (approx): 1 mPa.s = 0.001 Pa.s
    nu = viscosidade_mPa_s * 1e-3 / densidade_kg_m3
    if nu <= 0:
        return 0.0
    return abs(velocity * dh / nu)


def classificar_turbulencia(re: float) -> Tuple[str, str]:
    if re <= 0:
        return "Desconhecido", "Reynolds não calculado"
    if re < 2300:
        return "Laminar", "Fluxo laminar"
    if re < 10000:
        return "Transitorio", "Regime de transição"
    return "Turbulento", "Fluxo turbulento"


def recomendar_angulo_placa(re_prod: float, re_serv: float, pressao_max: float, visc_prod: float, visc_serv: float) -> Tuple[str, float, str]:
    # Simple rule: se qualquer lado for turbulento, escolha placa mais turbulenta
    if re_prod > 10000 or re_serv > 10000:
        return DEFAULT_PLACA, 1.0, "Placa para alto regime de turbulência"
    return DEFAULT_PLACA, 1.0, "Placa padrão"


def get_viscosity_factor(dados_fluido: dict) -> float:
    # Placeholder: retorna 1.0 (no correction)
    return 1.0


def calculate_lmtd(dt1: float, dt2: float) -> float:
    dt1_abs = abs(dt1)
    dt2_abs = abs(dt2)
    if dt1_abs < 1e-6 and dt2_abs < 1e-6:
        return 1.0
    if abs(dt1_abs - dt2_abs) < 1e-6:
        return max(dt1_abs, dt2_abs, 1.0)
    if dt1_abs > 0 and dt2_abs > 0:
        try:
            return abs((dt1_abs - dt2_abs) / math.log(dt1_abs / dt2_abs))
        except Exception:
            return max(dt1_abs, dt2_abs, 1.0)
    return max(dt1_abs, dt2_abs, 1.0)


# --- Configuração de passe e cabeçotes (simplificada e corrigida) ---

def calcular_tipo_passe(placas: int, vazao_prod: float, vazao_serv: float, tipo_modelo: str) -> dict:
    vazao_ratio = (max(vazao_prod, vazao_serv) / min(vazao_prod, vazao_serv)) if min(vazao_prod, vazao_serv) > 0 else 1.0
    tipo_passe = "Simples"
    passes_produto = 1
    passes_servico = 1
    justificativa_passe = "Configuração simples adequada para este dimensionamento"

    if placas > PLACAS_LIMITE_MULTI_PASSE:
        if vazao_ratio > VAZAO_RATIO_LIMITE:
            tipo_passe = "Multi Passe"
            passes_produto = 2 if vazao_prod > vazao_serv else 1
            passes_servico = 2 if vazao_serv > vazao_prod else 1
            justificativa_passe = f"Ratio de vazão elevado ({vazao_ratio:.1f}) com {placas} placas. Multi passe recomendado."
        elif placas > PLACAS_LIMITE_MULTI_SECAO:
            tipo_passe = "Multi Seção"
            passes_produto = 2
            passes_servico = 2
            justificativa_passe = f"Quantidade de placas ({placas}) muito elevada. Multi seção recomendada."
        else:
            tipo_passe = "Multi Passe"
            passes_produto = 2
            passes_servico = 2
            justificativa_passe = f"Quantidade de placas ({placas}) indica benefício em multi passe."

    if tipo_modelo == "semi-soldado" and tipo_passe == "Multi Seção":
        tipo_passe = "Multi Passe"
        justificativa_passe = "Modelo semi-soldado tem limitações para multi seção. Multi passe adotado."

    return {
        "tipo_passe": tipo_passe,
        "passes_produto": passes_produto,
        "passes_servico": passes_servico,
        "vazao_ratio": vazao_ratio,
        "justificativa_passe": justificativa_passe,
    }


def calcular_configuracao_cabecotes(placas: int, tipo_passe: str, passes_produto: int, passes_servico: int, tipo_modelo: str, tipo_placa: str) -> dict:
    entrada_prod = "Cabeçote Fixo"
    saida_prod = "Cabeçote Móvel"
    entrada_serv = "Cabeçote Móvel"
    saida_serv = "Cabeçote Fixo"
    configuracao = "Contra-corrente Padrão"
    justificativa_cabecotes = "Configuração padrão contra-corrente"

    placas_turbulentas = ["30 H", "45 HT"]
    is_turbulento = tipo_placa in placas_turbulentas

    if tipo_passe == "Simples":
        if is_turbulento:
            entrada_prod = "Cabeçote Fixo"
            saida_prod = "Cabeçote Móvel"
            entrada_serv = "Cabeçote Móvel"
            saida_serv = "Cabeçote Fixo"
            configuracao = "1 Passe Turbulento (Cruzado)"
            justificativa_cabecotes = "Entrada/saída opostas para placas turbulentas"
        else:
            entrada_prod = "Cabeçote Fixo"
            saida_prod = "Cabeçote Fixo"
            entrada_serv = "Cabeçote Fixo"
            saida_serv = "Cabeçote Fixo"
            configuracao = "1 Passe Padrão (Fixo)"
            justificativa_cabecotes = "Passe simples com cabeçotes fixos"

    if tipo_passe == "Multi Passe":
        if passes_produto == 2 and passes_servico == 2:
            entrada_prod = "Cabeçote Fixo"
            saida_prod = "Cabeçote Fixo"
            entrada_serv = "Cabeçote Móvel"
            saida_serv = "Cabeçote Móvel"
            configuracao = "Multi Passe Simétrico"
            justificativa_cabecotes = "Multi passe simétrico para melhor distribuição"
        elif passes_produto == 2:
            entrada_prod = "Cabeçote Fixo"
            saida_prod = "Cabeçote Fixo"
            entrada_serv = "Cabeçote Móvel"
            saida_serv = "Cabeçote Fixo"
            configuracao = "Multi Passe Assimétrico"
            justificativa_cabecotes = "Produto em 2 passes, serviço simples"
        elif passes_servico == 2:
            entrada_prod = "Cabeçote Fixo"
            saida_prod = "Cabeçote Móvel"
            entrada_serv = "Cabeçote Móvel"
            saida_serv = "Cabeçote Móvel"
            configuracao = "Multi Passe Assimétrico"
            justificativa_cabecotes = "Serviço em 2 passes, produto simples"

    if tipo_passe in ("Multi Seção", "Multi Secao"):
        entrada_prod = "Cabeçote Fixo"
        saida_prod = "Cabeçote Móvel"
        entrada_serv = "Cabeçote Móvel"
        saida_serv = "Cabeçote Fixo"
        configuracao = "Multi Seção em Paralelo"
        justificativa_cabecotes = "Multi seção para manutenção e disponibilidade"

    if placas > 150:
        configuracao = "Contra-corrente com Distribuidor"
        justificativa_cabecotes = f"Grande número de placas ({placas}), recomenda distribuidores de fluxo"
        if is_turbulento:
            configuracao = "1 Passe Turbulento com Distribuidor"

    if tipo_modelo == "semi-soldado" and tipo_passe == "Multi Passe":
        configuracao = "Multi Passe Semi-Soldado"
        justificativa_cabecotes = "Otimizado para semi-soldado"

    return {
        "entrada_produto": entrada_prod,
        "saida_produto": saida_prod,
        "entrada_servico": entrada_serv,
        "saida_servico": saida_serv,
        "configuracao": configuracao,
        "justificativa_cabecotes": justificativa_cabecotes,
    }


# --- Main calculation function (simplified but consistent) ---
def calculate_dimensionamento(produto: str, dados_fluido: dict, modelo: str, dados_modelo: dict,
                               t_in_prod: float, t_out_prod: float, t_in_serv: float, t_out_serv: float,
                               vazao_prod: float, dados_servico: dict) -> Dict:
    cp_prod = dados_fluido["cp"]
    cp_serv = dados_servico["cp"]
    densidade_prod = dados_fluido.get("densidade", 1000)
    densidade_serv = dados_servico.get("densidade", 1000)
    viscosidade_prod = dados_fluido.get("viscosidade", 1.0)
    viscosidade_serv = dados_servico.get("viscosidade", 1.0)
    area_por_placa = dados_modelo.get("area_placa", 0.1)
    pressao_max = dados_modelo.get("pressao_max", 25)
    dh = dados_modelo.get("dh", 0.005)
    tipo_modelo = dados_modelo.get("tipo", "gaxetado")

    reynolds_prod = calculate_reynolds(vazao_prod, viscosidade_prod, densidade_prod, dh)

    dT_prod = abs(t_in_prod - t_out_prod)
    carga_kw = (vazao_prod * cp_prod * dT_prod) / 3600.0
    delta_t_serv = abs(t_out_serv - t_in_serv)
    vazao_serv = (carga_kw * 3600.0) / (cp_serv * delta_t_serv) if delta_t_serv > 0 else 0.0

    reynolds_serv = calculate_reynolds(vazao_serv, viscosidade_serv, densidade_serv, dh)

    regime_prod, desc_prod = classificar_turbulencia(reynolds_prod)
    regime_serv, desc_serv = classificar_turbulencia(reynolds_serv)

    tipo_placa, multiplicador_u, justificativa_angulo = recomendar_angulo_placa(
        reynolds_prod, reynolds_serv, pressao_max, viscosidade_prod, viscosidade_serv
    )

    fator_viscosidade = get_viscosity_factor(dados_fluido)

    U_adotado = dados_modelo.get("U_base", 500.0) * fator_viscosidade * multiplicador_u * COEFICIENTE_FOULING

    dt1 = t_in_prod - t_out_serv
    dt2 = t_out_prod - t_in_serv
    lmtd = calculate_lmtd(dt1, dt2)

    area_teorica_m2 = (carga_kw * 1000.0) / (U_adotado * lmtd) if lmtd > 0 else 0.0

    fator_placa = ANGULOS_PLACA.get(tipo_placa, {}).get("fator_placas", 1.0)
    area_segura_m2 = area_teorica_m2 * FATOR_SEGURANCA_AREA * fator_placa

    placas_teoricas = area_segura_m2 / area_por_placa if area_por_placa > 0 else 0
    placas = math.ceil(placas_teoricas) + 2
    if placas < PLACA_MINIMA:
        placas = PLACA_MINIMA
    if placas % 2 != 0:
        placas += 1

    limite_max = PLACA_MAXIMA_GAXETADA if tipo_modelo == "gaxetado" else PLACA_MAXIMA_SEMI_SOLDADO
    aviso_limite = None
    if placas > limite_max:
        aviso_limite = f"AVISO: Quantidade de placas ({placas}) excede limite para {tipo_modelo} ({limite_max})."
        placas = limite_max

    area_efetiva_m2 = max((placas - 2) * area_por_placa, 0.0)
    folga_area = ((area_efetiva_m2 - area_teorica_m2) / area_teorica_m2 * 100) if area_teorica_m2 > 0 else 0

    tipo_passe_info = calcular_tipo_passe(placas, vazao_prod, vazao_serv, tipo_modelo)

    cabecotes_info = calcular_configuracao_cabecotes(
        placas, tipo_passe_info["tipo_passe"], tipo_passe_info["passes_produto"], tipo_passe_info["passes_servico"], tipo_modelo, tipo_placa
    )

    resultados = {
        "carga_kw": carga_kw,
        "vazao_serv": vazao_serv,
        "lmtd": lmtd,
        "area_teorica_m2": area_teorica_m2,
        "area_segura_m2": area_segura_m2,
        "area_efetiva_m2": area_efetiva_m2,
        "area_m2": area_efetiva_m2,
        "placas": placas,
        "placas_teoricas": placas_teoricas,
        "area_por_placa": area_por_placa,
        "folga_area": folga_area,
        "passes": cabecotes_info.get("configuracao"),
        "U_adotado": U_adotado,
        "U_base": dados_modelo.get("U_base", 500.0),
        "fator_viscosidade": fator_viscosidade,
        "multiplicador_placa": multiplicador_u,
        "fator_seguranca": FATOR_SEGURANCA_AREA,
        "fator_placa": fator_placa,
        "reynolds_prod": reynolds_prod,
        "reynolds_serv": reynolds_serv,
        "regime_prod": regime_prod,
        "regime_serv": regime_serv,
        "desc_prod": desc_prod,
        "desc_serv": desc_serv,
        "tipo_placa": tipo_placa,
        "justificativa_placa": justificativa_angulo,
        "aviso_limite": aviso_limite,
        "tipo_passe": tipo_passe_info["tipo_passe"],
        "passes_produto": tipo_passe_info["passes_produto"],
        "passes_servico": tipo_passe_info["passes_servico"],
        "vazao_ratio": tipo_passe_info["vazao_ratio"],
        "justificativa_passe": tipo_passe_info["justificativa_passe"],
        "entrada_produto": cabecotes_info["entrada_produto"],
        "saida_produto": cabecotes_info["saida_produto"],
        "entrada_servico": cabecotes_info["entrada_servico"],
        "saida_servico": cabecotes_info["saida_servico"],
        "configuracao_cabecotes": cabecotes_info["configuracao"],
        "justificativa_cabecotes": cabecotes_info["justificativa_cabecotes"],
    }

    return resultados


# --- Minimal PDF builder (optional) ---
def build_pdf(*args, **kwargs):
    if not REPORTLAB_AVAILABLE:
        return None
    # For brevity, not implementing full PDF here in minimal fix
    return None


# --- Simple Streamlit UI entrypoint ---
if __name__ == "__main__":
    if st is None:
        print("Streamlit not available. Run this file with Streamlit: streamlit run app.py")
    else:
        st.set_page_config(page_title="AlfaVed - Dimensionador", layout="wide")
        st.markdown("""
        # AlfaVed Engenharia Termica
        Dimensionador Inteligente de Trocadores de Calor (versão mínima)
        """)

        with st.form("form_dimensionamento"):
            modelo = st.selectbox("Modelo Alfa Laval", list(BANCO_MODELOS.keys()))
            produto = st.selectbox("Fluido do Produto", list(BANCO_FLUIDOS.keys()))
            vazao_prod = st.number_input("Vazão (kg/h)", value=5000.0, min_value=0.1)
            t_in_prod = st.number_input("Temp. Entrada Produto (°C)", value=90.0)
            t_out_prod = st.number_input("Temp. Saída Produto (°C)", value=8.0)

            servico = st.selectbox("Fluido de Serviço", list(BANCO_SERVICOS.keys()))
            t_in_serv = st.number_input("Temp. Entrada Serviço (°C)", value=0.0)
            t_out_serv = st.number_input("Temp. Saída Serviço (°C)", value=12.0)

            submitted = st.form_submit_button("CALCULAR DIMENSIONAMENTO")

        if submitted:
            dados_fluido = BANCO_FLUIDOS[produto]
            dados_modelo = BANCO_MODELOS[modelo]
            dados_servico = BANCO_SERVICOS[servico]

            resultados = calculate_dimensionamento(
                produto, dados_fluido, modelo, dados_modelo,
                t_in_prod, t_out_prod, t_in_serv, t_out_serv,
                vazao_prod, dados_servico
            )

            st.success("Cálculo realizado com sucesso")
            st.write(resultados)
