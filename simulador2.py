# simulador.py
# ----------------------------------------
# Requisitos:
#   pip install streamlit
# Ejecuta:
#   streamlit run simulador.py
# ----------------------------------------

import streamlit as st
import math
from typing import Dict, List
from collections import defaultdict

# --------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------
st.set_page_config(
    page_title="Simulador de Compensación | Corona",
    page_icon="https://empresa.corona.co/wp-content/uploads/2023/02/coronaMain.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# PARÁMETROS BASE
# --------------------------
DEFAULT_SMMLV = 1_750_905

smmlv = st.sidebar.number_input(
    "SMMLV vigente (COP)",
    min_value=100_000.0,
    step=5_000.0,
    value=float(DEFAULT_SMMLV),
    format="%.0f"
)

salario = st.sidebar.number_input(
    "Salario básico mensual (COP)",
    min_value=0.0,
    step=100_000.0,
    value=3_000_000.0,
    format="%.0f"
)

cargo = st.sidebar.selectbox(
    "Cargo / Nivel",
    ["Alta gerencia", "Gerencia", "Jefe", "Coordinación", "Analista", "Asistente", "Operativo"]
)

Hijos = st.sidebar.selectbox("Hijos a cargo", ["Sí", "No"])
Estudiante = st.sidebar.selectbox("Estudiante de educación superior", ["Sí", "No"])

Valor_semestre = st.sidebar.number_input(
    "Valor del semestre",
    min_value=0.0,
    step=100_000.0,
    value=3_000_000.0,
    format="%.0f"
)

es_estudiante = (Estudiante == "Sí")
Antiguedad = st.sidebar.selectbox("Antigüedad en la compañía", list(range(1, 31)))
tiene_hijos = (Hijos == "Sí")
antiguedad = int(Antiguedad)

# --------------------------
# BENEFITS_DEFAULTS
# --------------------------
BENEFITS_DEFAULTS: Dict[str, Dict] = {
    "Alimentación": {
        "valor": 200_000,
        "nota": "Corona asume ~80% del almuerzo/día (valor promedio).",
        "link": "https://www.google.com",
        "categoria": "🏡 Bienestar y vida laboral"
    },
    "Rutas de transporte": {
        "valor": 125_000,
        "nota": "Rutas en diferentes localidades.",
        "link": "https://orgcorona.sharepoint.com/teams/ReportedeahorrosUSC/Lists/ahorros/AllItems.aspx",
        "categoria": "🏡 Bienestar y vida laboral"
    },
    "Refrigerio en oficina": {
        "valor": 58_700,
        "nota": "Bebidas/refrigerios en calle 100 y calle 26.",
        "link": "",
        "categoria": "🏡 Bienestar y vida laboral"
    },
    "Horario flexible": {
        "valor": 0,
        "nota": "Franja acordada; se puede valorar en productividad.",
        "link": "",
        "categoria": "🏡 Bienestar y vida laboral"
    },
    "Jornada flexible mamá": {
        "valor": 0,
        "nota": "Aplica post-licencia de maternidad.",
        "link": "",
        "categoria": "🏡 Bienestar y vida laboral"
    },
    "Día libre de cumpleaños": {
        "valor": 0,
        "nota": "1 día/año - por evento",
        "link": "",
        "categoria": "🏡 Bienestar y vida laboral"
    },
    "Día libre de la familia": {
        "valor": 0,
        "nota": "1 día/semestre contrario al cumpleaños- por evento",
        "link": "",
        "categoria": "🏡 Bienestar y vida laboral"
    },
    "Auxilio de conectividad": {
        "valor": 60_000,
        "nota": "Para trabajo en casa / plan de internet.",
        "link": "",
        "categoria": "🏡 Bienestar y vida laboral"
    },
    "Plan celular corporativo": {
        "valor": 35_000,
        "nota": "Cobertura del 100% del plan.",
        "link": "",
        "categoria": "🏡 Bienestar y vida laboral"
    },
    "Pólizas de salud (promedio por persona)": {
        "valor": 250_000,
        "nota": "Equivale a ~50% de la póliza (estimado promedio) por evento",
        "link": "",
        "categoria": "❤️ Salud y protección"
    },
    "Incapacidades cubiertas al 100% (administrativos)": {
        "valor": 0,
        "nota": "Equivalente a 10 días por año por evento",
        "link": "",
        "categoria": "❤️ Salud y protección"
    },
    "Póliza de vida (12 salarios)": {
        "valor": 0,
        "nota": "Valor cubierto por evento",
        "link": "",
        "categoria": "❤️ Salud y protección"
    },
    "Auxilio de visión (hasta 50% SMLV)": {
        "valor": 0,
        "nota": "Valor por evento",
        "link": "",
        "categoria": "❤️ Salud y protección"
    },
    "Chequeos médicos ejecutivos": {
        "valor": 0,
        "nota": "Valor por evento depende del rol - por evento",
        "link": "",
        "categoria": "❤️ Salud y protección"
    },
    "Auxilio de educación superior": {
        "valor": 0,
        "nota": "Para empleado/hijos; según política por evento o semestre",
        "link": "",
        "categoria": "🎓 Educación"
    },
    "Auxilio educativo escolar (~60% SMLV adm.)": {
        "valor": 0,
        "nota": "Valor por evento",
        "link": "www.google.com",
        "categoria": "🎓 Educación"
    },
    "Auxilio de vivienda (subsidio tasa/interés)": {
        "valor": 333_333,
        "nota": "Puntos sobre tasa; depende de política y monto del crédito por evento",
        "link": "",
        "categoria": "💰 Económicos y financieros"
    },
    "Mis beneficios a la carta (cupo % salario)": {
        "valor": 0,
        "nota": "Cupo variable por grado salarial.",
        "link": "",
        "categoria": "💰 Económicos y financieros"
    },
    "Prima extralegal de navidad (30 días)": {
        "valor": 0,
        "nota": "Valor por evento.",
        "link": "",
        "categoria": "💰 Económicos y financieros"
    },
    "Bonificación de vacaciones (15 días)": {
        "valor": 0,
        "nota": "Equivale al 50% del salario - por evento",
        "link": "",
        "categoria": "💰 Económicos y financieros"
    },
    "Bonificación por pensión (2 meses)": {
        "valor": 0,
        "nota": "Valor por evento",
        "link": "",
        "categoria": "💰 Económicos y financieros"
    },
    "Ahorro mutuo Corona (aporte empresa)": {
        "valor": 0,
        "nota": "Aporte 2% del salario por la empresa.",
        "link": "",
        "categoria": "💰 Económicos y financieros"
    },
    "Leasing (Gerencias/Vice/Presidencia)": {
        "valor": 0,
        "nota": "Por evento, depende del rol - por evento",
        "link": "",
        "categoria": "💰 Económicos y financieros"
    },
    "Descuento en materiales (30%)": {
        "valor": 3_000_000,
        "nota": "10.000.000 COP aproximadamente en compras al año con este descuento, según consumo individual por evento.",
        "link": "",
        "categoria": "🛍️ Descuentos y productos"
    },
    "Soy Corona, compro Corona (programa comercial)": {
        "valor": 0,
        "nota": "Descuentos especiales vía área comercial. por evento",
        "link": "",
        "categoria": "🛍️ Descuentos y productos"
    },
    "Descuento en vajillas (30%)": {
        "valor": 60_000,
        "nota": "Aproximadamente 200.000 COP promedio por año o por por evento",
        "link": "",
        "categoria": "🛍️ Descuentos y productos"
    },
    "Donación de materiales (banco de materiales)": {
        "valor": 0,
        "nota": "Según y requisitos aplicacble hasta los 8SMMLV de salario por evento",
        "link": "",
        "categoria": "🛍️ Descuentos y productos"
    },
    "Permiso remunerado por matrimonio (3 días)": {
        "valor": 0,
        "nota": "3 días de salario - por evento).",
        "link": "",
        "categoria": "🎉 Eventos de vida"
    },
    "Regalo por matrimonio (vajilla)": {
        "valor": 200_000,
        "nota": "Vajilla apoximado - valor por evento",
        "link": "",
        "categoria": "🎉 Eventos de vida"
    },
    "Auxilio por nacimiento (~40% SMLV por evento)": {
        "valor": 0,
        "nota": "Valor por evento.",
        "link": "",
        "categoria": "🎉 Eventos de vida"
    },
    "Auxilio de fallecimiento del empleado (4–12 SMMLV)": {
        "valor": 0,
        "nota": "Equivalente al último sueldo mensual acotado entre 4 y 12 SMMLV - por evento",
        "link": "",
        "categoria": "🎉 Eventos de vida"
    },
    "Antigüedad en días de descanso (TTT)": {
        "valor": 0,
        "nota": "Días por hitos de antigüedad (3, 5, 7, 10, 20 años) - por evento",
        "link": "",
        "categoria": "🎉 Eventos de vida"
    },
}

# --------------------------
# BENEFITS_FORMULAS
# --------------------------
BENEFITS_FORMULAS: Dict[str, str] = {
    "Incapacidades cubiertas al 100% (administrativos)": "(salario/30)*10*0.33",
    "Día libre de cumpleaños": "(salario/30)",
    "Día libre de la familia": "(salario/30)",
    "Leasing (Gerencias/Vice/Presidencia)": "120_000_000 if cargo in ['Alta gerencia', 'Gerencia'] else 0",
    "Permiso remunerado por matrimonio (3 días)": "(salario/30)*3",
    "Auxilio educativo escolar (~60% SMLV adm.)": "(0.6*smmlv) if (hijos and salario <= 9_168_000) else 0",
    "Prima extralegal de navidad (30 días)": "salario",
    "Bonificación de vacaciones (15 días)": "(salario*0.5) if 1.6 < (salario/smmlv) < 5.4 else 0",
    "Auxilio de fallecimiento del empleado (4–12 SMMLV)": "min(max(salario, 4*smmlv), 12*smmlv)",
    "Auxilio por nacimiento (~40% SMLV por evento)": "0.4*smmlv",
    "Auxilio de visión (hasta 50% SMLV)": "0.5*smmlv",
    "Chequeos médicos ejecutivos": "1_500_000 if cargo in ['Alta gerencia', 'Gerencia'] else 0",
    "Bonificación por pensión (2 meses)": "salario*2",
    "Donación de materiales (banco de materiales)": "0 if salario/smmlv > 8 else (10_000_000)",
    "Ahorro mutuo Corona (aporte empresa)": "salario*0.02",
    "Mis beneficios a la carta (cupo % salario)": "salario * (0.10 if 1_750_905 <= salario <= 3_960_000 else 0.07 if 3_960_000 < salario < 9_168_000 else 0)",
    "Auxilio de educación superior": "min(valor_semestre * 0.8, 4.8 * smmlv) if estudiante else 0",
    "Póliza de vida (12 salarios)": "12 * salario if 12 * salario >= 42_000_000 else 42_000_000",
    "Jornada flexible mamá": "salario*0.3",
    "Antigüedad en días de descanso (TTT)": "(salario / 30)*(8 if antiguedad >= 20 else 5 if antiguedad >= 10 else 4 if antiguedad >= 7 else 3 if antiguedad >= 5 else 2 if antiguedad >= 3 else 0)"
}


def safe_eval_formula(expr, *, salario, smmlv, cargo, hijos, antiguedad, estudiante, valor_semestre):
    local_vars = {
        "salario": float(salario), "smmlv": float(smmlv),
        "salario_dia": float(salario / 30.0 if salario else 0.0),
        "cargo": cargo, "hijos": hijos, "antiguedad": antiguedad,
        "estudiante": estudiante, "valor_semestre": float(valor_semestre),
        "min": min, "max": max, "round": round, "abs": abs,
    }
    return max(0.0, float(eval(expr, {"__builtins__": {}}, local_vars)))

# --------------------------
# ESTADO / SESIÓN
# --------------------------
if "beneficios" not in st.session_state:
    st.session_state.beneficios = BENEFITS_DEFAULTS.copy()
if "custom_items" not in st.session_state:
    st.session_state.custom_items: Dict[str, float] = {}

# --------------------------
# SIDEBAR EXTRAS
# --------------------------
st.sidebar.image("https://empresa.corona.co/wp-content/uploads/2023/02/corona.png", width=190)
st.sidebar.markdown("---")
modo_edicion = st.sidebar.toggle("🛠️ Modo edición de valores", value=False)

# --------------------------
# ESTILOS
# --------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #F0F4F8;
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2EAF4;
}

[data-testid="stSidebar"] * {
    color: #1A2B4A !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label {
    color: #6B7FA3 !important;
    font-size: 0.78rem !important;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select,


[data-testid="stSidebar"] [data-baseweb="select"] * {
    background: #F7F9FC !important;
    color: #1A2B4A !important;
}


/* Título */
h1 { 
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    color: #0B2D5E !important;
    font-size: 1.8rem !important;
    margin-bottom: 0.2rem !important;
}
h2, h3 { 
    font-family: 'DM Sans', sans-serif !important;
    color: #0B2D5E !important;
}

/* Métricas */
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    color: #0B2D5E !important;
    font-size: 1.3rem !important;
    font-weight: 500 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #6B7FA3 !important;
    font-weight: 600 !important;
}

/* Panel de resultados */
.results-panel {
    padding-top: 0.6rem !important;
}

/* Tarjeta de total */
.total-card {
    background: linear-gradient(135deg, #0B2D5E 0%, #1A56B0 100%);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    color: white;
    margin-bottom: 1rem;
}
.total-card .label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    opacity: 0.75;
    margin-bottom: 0.2rem;
    font-weight: 600;
}
.total-card .amount {
    font-family: 'DM Mono', monospace;
    font-size: 1.9rem;
    font-weight: 500;
    letter-spacing: -0.5px;
}
.total-card .sub {
    font-size: 0.82rem;
    opacity: 0.7;
    margin-top: 0.2rem;
}

/* Alinear panel derecho con botones de la izquierda */
[data-testid="column"]:nth-child(2) > div:first-child {
    margin-top: 0 !important;
}

/* Fila de métricas chicas */
.mini-metric {
    background: #F4F7FC;
    border-radius: 12px;
    padding: 0.7rem 1rem;
    text-align: center;
}
.mini-metric .lbl { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.5px; color: #6B7FA3; font-weight: 600; }
.mini-metric .val { font-family: 'DM Mono', monospace; font-size: 1rem; color: #0B2D5E; font-weight: 500; margin-top: 0.15rem; }

/* Categoría accordion */
.cat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background: #FFFFFF;
    border-radius: 14px;
    margin-bottom: 0.4rem;
    cursor: pointer;
    border: 1.5px solid #E2EAF4;
    transition: all 0.2s;
    box-shadow: 0 1px 4px rgba(11,45,94,0.06);
}
.cat-header:hover { border-color: #A8C0E8; box-shadow: 0 3px 12px rgba(11,45,94,0.12); }
.cat-title { font-weight: 700; font-size: 0.88rem; color: #0B2D5E; }
.cat-total {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    font-weight: 500;
    background: #E8F0FB;
    color: #1A56B0;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
}
.cat-total.has-value { background: #D4EDDA; color: #155724; }

/* Evita que ciertos elementos propaguen click */
.benefit-row,
.benefit-row * {
    pointer-events: auto;
}

/* Tarjeta de beneficio */
.benefit-row {
    background: #FAFBFE;
    border: 1px solid #E8EEF8;
    border-radius: 11px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 0.4rem;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.benefit-row:hover { border-color: #BDD0F0; box-shadow: 0 2px 8px rgba(11,45,94,0.07); }
.benefit-row.active { border-color: #1A56B0; background: #F0F5FF; }

.benefit-name-text {
    font-weight: 600;
    font-size: 0.82rem;
    color: #1A2B4A;
    line-height: 1.3;
}
.benefit-name-link {
    font-weight: 600;
    font-size: 0.82rem;
    color: #1A56B0;
    text-decoration: none;
    border-bottom: 1px dotted #1A56B0;
    line-height: 1.3;
    transition: color 0.15s;
}
.benefit-name-link:hover { color: #0B2D5E; border-color: #0B2D5E; }
.benefit-val {
    font-family: 'DM Sans', sans-serif !important; /* ✅ fuente normal */
    font-size: 0.82rem;
    color: #1A2B4A !important;                      /* ✅ negro */
    background: #F4F7FC !important;
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    white-space: nowrap;
    font-weight: 600;

    /* ✅ fuerza números normales */
    font-variant-numeric: normal !important;
    font-feature-settings: "zero" 0, "tnum" 0, "lnum" 1;
}
.benefit-nota { font-size: 0.73rem; color: #7A8CA8; margin-top: 0.2rem; line-height: 1.4; }
.formula-tag {
    display: inline-block;
    font-size: 0.65rem;
    background: #FFF3CD;
    color: #856404;
    border-radius: 4px;
    padding: 0.05rem 0.35rem;
    font-weight: 600;
    margin-left: 0.3rem;
    vertical-align: middle;
}

/* Badge header */
.page-badge {
    display: inline-block;
    background: #FFD15E;
    color: #1A2B4A;
    border-radius: 999px;
    padding: 0.25rem 0.85rem;
    font-weight: 700;
    font-size: 0.78rem;
    letter-spacing: 0.3px;
    margin-bottom: 1rem;
}

/* Separador de categoría total en resultados */
.cat-result-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.4rem 0;
    border-bottom: 1px solid #F0F4F8;
    font-size: 0.82rem;
}
.cat-result-row .name { color: #4A5E80; }
.cat-result-row .val { font-family: 'DM Mono', monospace; color: #0B2D5E; font-weight: 500; }

/* Streamlit overrides */
.stButton > button {
    background: #0B2D5E !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    padding: 0.4rem 1rem !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: #1A56B0 !important; }

.stCheckbox label { font-size: 0.8rem !important; }
input[type="checkbox"] { accent-color: #1A56B0; }

.stExpander {
    border: 1px solid #E2EAF4 !important;
    border-radius: 12px !important;
    background: white !important;
}

/* Botones seleccionar/deseleccionar */
div[data-testid="column"] .stButton > button {
    width: 100%;
}
    


@media (min-width: 992px) {
    .results-panel { position: sticky; top: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# CABECERA
# --------------------------
st.markdown("""
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.5rem;">
    <div>
        <h1 style="margin:0;">Simulador de Compensación Total</h1>
        <p style="color:#6B7FA3;font-size:0.88rem;margin:0.2rem 0 0;">Organización Corona · Auxilios y Beneficios</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="page-badge">Activa los beneficios para calcular tu compensación total mensual</div>', unsafe_allow_html=True)

# --------------------------
# CÁLCULO AUXILIAR
# --------------------------
def fmt_cop(x: float) -> str:
    try:
        return f"$ {x:,.0f}".replace(",", ".")
    except Exception:
        return f"$ {x}"

salario_smmlv = (salario / smmlv) if smmlv > 0 else 0

beneficios_efectivos: Dict[str, float] = {}
errores_formula: Dict[str, str] = {}

for nombre, data in st.session_state.beneficios.items():
    base_val = float(data.get("valor", 0) or 0)
    if base_val == 0 and nombre in BENEFITS_FORMULAS:
        expr = BENEFITS_FORMULAS[nombre]
        try:
            expr_str = str(expr).strip()
            val = 0.0 if (not expr_str or expr_str == "0") else round(
                safe_eval_formula(expr_str, salario=salario, smmlv=smmlv, cargo=cargo,
                                  hijos=tiene_hijos, antiguedad=antiguedad,
                                  estudiante=es_estudiante, valor_semestre=Valor_semestre)
            )
            beneficios_efectivos[nombre] = round(float(val))
        except Exception as e:
            beneficios_efectivos[nombre] = 0.0
            errores_formula[nombre] = str(e)
    else:
        beneficios_efectivos[nombre] = base_val

# --------------------------
# LAYOUT
# --------------------------
left, right = st.columns([3, 2], vertical_alignment="top")

with left:
    benef_names = list(st.session_state.beneficios.keys())

    # Selección masiva
    c1, c2 = st.columns(2)
    if c1.button("✅ Seleccionar todo", use_container_width=True):
        for i in range(len(benef_names)):
            st.session_state[f"chk_{i}"] = True
    if c2.button("☐ Deseleccionar todo", use_container_width=True):
        for i in range(len(benef_names)):
            st.session_state[f"chk_{i}"] = False

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Inicializa checkboxes
    for i, name in enumerate(benef_names):
        if f"chk_{i}" not in st.session_state:
            st.session_state[f"chk_{i}"] = False

    incluidos: Dict[str, float] = {}
    excluidos: List[str] = []

    # Agrupar por categoría
    categorias: dict = defaultdict(list)
    for i, name in enumerate(benef_names):
        cat = st.session_state.beneficios[name].get("categoria", "Otros")
        categorias[cat].append((i, name))

    # Pre-calcular total por categoría (solo activos)
    def cat_total_activo(items_list):
        t = 0.0
        for i, name in items_list:
            if st.session_state.get(f"chk_{i}", False):
                v = float(beneficios_efectivos.get(name, 0))
                if v > 0:
                    t += v
        return t

    totales_cat: Dict[str, float] = {}
    for cat, items in categorias.items():
        totales_cat[cat] = cat_total_activo(items)

    # Renderizar categorías como expanders
    for categoria, items in categorias.items():
        total_cat = totales_cat[categoria]
        total_str = fmt_cop(total_cat) if total_cat > 0 else "$ 0"
        has_val = total_cat > 0

        label = f"{categoria}   ·   {total_str}"
        with st.expander(label, expanded=False):
            col_a, col_b = st.columns(2)
            for col_idx, (i, name) in enumerate(items):
                col = col_a if col_idx % 2 == 0 else col_b
                with col:
                    data = st.session_state.beneficios[name]
                    base_val = float(data.get("valor", 0) or 0)
                    nota = data.get("nota", "")
                    link = data.get("link", "")
                    val_resuelto = float(beneficios_efectivos.get(name, base_val))
                    viene_de_formula = (base_val == 0 and name in BENEFITS_FORMULAS)
                    val_clase = "benefit-val" if val_resuelto > 0 else "benefit-val zero"

                    # Nombre clickeable o no
                    if link:
                        nombre_html = f'<a class="benefit-name-link" href="{link}" target="_blank" rel="noopener">{name} 🔗</a>'
                    else:
                        nombre_html = f'<span class="benefit-name-text">{name}</span>'

                    formula_tag = '<span class="formula-tag">⚡ Auto</span>' if viene_de_formula else ""

                    st.markdown(
                        f"""<div class="benefit-row">
                            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;flex-wrap:wrap;">
                                <div style="flex:1;min-width:0">{nombre_html}{formula_tag}</div>
                                <span class="{val_clase}">{fmt_cop(val_resuelto)}</span>
                            </div>
                            {"<div class='benefit-nota'>" + nota + "</div>" if nota else ""}
                        </div>""",
                        unsafe_allow_html=True
                    )

                    checked = st.checkbox("Incluir en total", key=f"chk_{i}", label_visibility="visible")

                    if not viene_de_formula and (modo_edicion or base_val == 0):
                        val = st.number_input(
                            "Valor (COP)",
                            min_value=0.0, step=10_000.0,
                            value=float(val_resuelto),
                            key=f"val_{i}",
                            help=nota,
                            label_visibility="collapsed"
                        )
                    else:
                        val = val_resuelto

                    if name in errores_formula:
                        st.warning(f"⚠️ Error fórmula: {errores_formula[name]}")

                    if checked and val > 0:
                        incluidos[name] = float(val)
                    else:
                        excluidos.append(name)

    # Beneficios personalizados
    st.markdown("---")
    st.markdown("**➕ Agregar beneficio personalizado**")
    cc1, cc2, cc3 = st.columns([3, 2, 1])
    with cc1:
        custom_name = st.text_input("Nombre", placeholder="Ej: Bono especial", label_visibility="collapsed")
    with cc2:
        custom_value = st.number_input("Valor COP", min_value=0.0, step=10_000.0, value=0.0, label_visibility="collapsed")
    with cc3:
        if st.button("Agregar"):
            if custom_name and custom_value > 0:
                st.session_state.custom_items[custom_name] = float(custom_value)
            else:
                st.warning("Ingresa nombre y valor > 0.")

    if st.session_state.custom_items:
        for cname, cval in st.session_state.custom_items.items():
            st.markdown(f"<div class='benefit-row'><span class='benefit-name-text'>{cname}</span> &nbsp; <span class='benefit-val'>{fmt_cop(cval)}</span></div>", unsafe_allow_html=True)

# Totales finales
incluidos_final = incluidos.copy()
incluidos_final.update(st.session_state.custom_items)
total_beneficios = sum(incluidos_final.values())
total_compensacion = salario + total_beneficios
total_smmlv = (total_compensacion / smmlv) if smmlv > 0 else 0

# ----- DERECHA: panel de resultados -----
with right:
    st.markdown('<div class="results-panel">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="total-card">
        <div class="label">Compensación Total Mensual</div>
        <div class="amount">{fmt_cop(total_compensacion)}</div>
        <div class="sub">{total_smmlv:.2f} SMMLV · {fmt_cop(total_beneficios)} en beneficios</div>
    </div>
    """, unsafe_allow_html=True)

    # Mini métricas
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="mini-metric"><div class="lbl">Salario base</div><div class="val">{fmt_cop(salario)}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="mini-metric"><div class="lbl">Beneficios activos</div><div class="val">{fmt_cop(total_beneficios)}</div></div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f'<div class="mini-metric" style="margin-top:0.5rem"><div class="lbl">Salario / SMMLV</div><div class="val">{salario_smmlv:.2f}x</div></div>', unsafe_allow_html=True)
    with col4:
        n_activos = len(incluidos_final)
        st.markdown(f'<div class="mini-metric" style="margin-top:0.5rem"><div class="lbl">Beneficios ON</div><div class="val">{n_activos} / {len(benef_names)}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("**Subtotales por categoría**")

    # Total por categoría (solo activos)
    totales_cat_final: Dict[str, float] = {}
    for cat, items in categorias.items():
        t = sum(incluidos.get(name, 0.0) for _, name in items)
        if t > 0:
            totales_cat_final[cat] = t

    if totales_cat_final:
        for cat, t in sorted(totales_cat_final.items(), key=lambda x: -x[1]):
            st.markdown(
                f'<div class="cat-result-row"><span class="name">{cat}</span><span class="val">{fmt_cop(t)}</span></div>',
                unsafe_allow_html=True
            )
    else:
        st.caption("Activa beneficios para ver subtotales.")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    with st.expander("📋 Detalle completo"):
        if incluidos_final:
            for k, v in sorted(incluidos_final.items()):
                st.markdown(f"<div class='cat-result-row'><span class='name'>{k}</span><span class='val'>{fmt_cop(v)}</span></div>", unsafe_allow_html=True)
        else:
            st.caption("No hay beneficios activos.")

    with st.expander("🚫 Excluidos"):
        if excluidos:
            st.caption(", ".join(excluidos))
        else:
            st.caption("Todos los beneficios están activos.")

    st.markdown('</div>', unsafe_allow_html=True)