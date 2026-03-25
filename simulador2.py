# simulador.py
# ----------------------------------------
# Requisitos:
#   pip install streamlit pandas
# Ejecuta:
#   streamlit run app.py
# ----------------------------------------

import streamlit as st
import math
from typing import Dict, List

# --------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------
st.set_page_config(
    page_title="Simulador de Auxilios y Beneficios | Organización Corona",
    page_icon="https://empresa.corona.co/wp-content/uploads/2023/02/coronaMain.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# PARÁMETROS BASE (editables en código)
# --------------------------
DEFAULT_SMMLV = 1_750_905  # $ 1,750,905.00


# Asegurar tipos float cuando se usa format="%.0f" para evitar warnings
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
    [
        "Alta gerencia",
        "Gerencia",
        "Jefe"
        "Coordinación",
        "Analista",
        "Asistente",
        "Operativo"
    ]
)
Hijos = st.sidebar.selectbox(
    "Hijos a cargo",
    [
        "Sí",
        "No",
    ]
)
Estudiante = st.sidebar.selectbox(
    "Estudiante de educación superior",
    [
        "Sí",
        "No",
    ]
)

Valor_semestre = st.sidebar.number_input(
    "Valor del semestre",
    min_value=0.0,
    step=100_000.0,
    value=3_000_000.0,
    format="%.0f"
)
es_estudiante = (Estudiante == "Sí")
Antiguedad = st.sidebar.selectbox(
    "Antigüedad en la compañía",
    [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30
    ]
)

tiene_hijos = (Hijos == "Sí")
antiguedad = int(Antiguedad)
# Beneficios predeterminados (COP/mes); 0 si el adjunto no traía valor numérico claro.
# Puedes modificar estos valores por defecto directamente aquí.
BENEFITS_DEFAULTS: Dict[str, Dict] = {
    # Con valor aproximado en el adjunto:
    "Alimentación": {
        "valor": 200_000,
        "nota": "Corona asume ~80% del almuerzo/día (valor promedio)."
    },
    "Rutas de transporte": {
        "valor": 125_000,
        "nota": "Rutas en diferentes localidades."
    },
    "Pólizas de salud (promedio por persona)": {
        "valor": 250_000,
        "nota": "Equivale a ~50% de la póliza (estimado promedio)."
    },
    "Plan celular corporativo": {
        "valor": 35_000,
        "nota": "Cobertura del 100% del plan."
    },
    "Incapacidades cubiertas al 100% (administrativos)": {
        "valor": 0,
        "nota": "Equivalente a 10 días por año"
    },
    "Auxilio de vivienda (subsidio tasa/interés)": {
        "valor": 333_333,
        "nota": "Puntos sobre tasa; depende de política y monto del crédito."
    },
    "Auxilio de conectividad": {
        "valor": 60_000,
        "nota": "Para trabajo en casa / plan de internet."
    },
    "Refrigerio en oficina": {
        "valor": 58_700,
        "nota": "Dotación de bebidas/refrigerios."
    },
    "Descuento en materiales (30%)": {
        "valor": 3_000_000,
        "nota": "10.000.000 COP aproximadamente en compras al año con este descuento, según consumo individual."
    },
    "Soy Corona, compro Corona (programa comercial)": {
        "valor": 0,
        "nota": "Descuentos especiales vía área comercial."
    },
    "Descuento en vajillas (30%)": {
        "valor": 60_000,
        "nota": "Aproximadamente 200.000 COP promedio por año."
    },
    "Donación de materiales (banco de materiales)": {
        "valor": 0,
        "nota": "Según y requisitos aplicacble hasta los 8SMMLV de salario"
    },
    "Horario flexible": {
        "valor": 0,
        "nota": "Franja acordada; se puede valorar en productividad."
    },
    "Jornada flexible mamá": {
        "valor": 0,
        "nota": "Aplica post-licencia de maternidad."
    },

    "Día libre de cumpleaños": {
        "valor": 0,
        "nota": "1 día/año; puedes monetizarlo si quieres."
    },
    "Día libre de la familia": {
        "valor": 0,
        "nota": "1 día/semestre contrario al cumpleaños."
    },
    "Permiso remunerado por matrimonio (3 días)": {
        "valor": 0,
        "nota": "3 días; monetízalo si deseas (salario/30 * 3)."
    },
    "Regalo por matrimonio (vajilla)": {
        "valor": 200_000,
        "nota": "Vajilla; no monetizado por defecto."
    },
    "Auxilio de educación superior": {
        "valor": 0,
        "nota": "Para empleado/hijos; según política."
    },
    "Auxilio educativo escolar (~60% SMLV adm.)": {
        "valor": 0,
        "nota": "Valor por evento"
    },
    "Mis beneficios a la carta (cupo % salario)": {
        "valor": 0,
        "nota": "Cupo variable por grado salarial."
    },
    "Leasing (Gerencias/Vice/Presidencia)": {
        "valor": 0,
        "nota": "Por evento, depende del rol"
    },
    "Prima extralegal de navidad (30 días)": {
        "valor": 0,
        "nota": "Valor por evento."
    },
    "Bonificación de vacaciones (15 días)": {
        "valor": 0,
        "nota": "Equivale al 50% del salario"
    },
    "Póliza de vida (12 salarios)": {
        "valor": 0,
        "nota": "Valor cubierto por evento"
    },
    "Auxilio de fallecimiento del empleado (4–12 SMMLV)": {
        "valor": 0,
        "nota": "Equivalente al último sueldo mensual acotado entre 4 y 12 SMMLV."
    },
    "Antigüedad en días de descanso (TTT)": {
        "valor": 0,
        "nota": "Días por hitos"
    },
    "Bonificación por pensión (2 meses)": {
        "valor": 0,
        "nota": "Valor por evento"
    },
    "Auxilio por nacimiento (~40% SMLV por evento)": {
        "valor": 0,
        "nota": "Valor por evento."
    },
    "Auxilio de visión (hasta 50% SMLV)": {
        "valor": 0,
        "nota": "Valor por evento"
    },
    "Ahorro mutuo Corona (aporte empresa)": {
        "valor": 0,
        "nota": "Aporte 2% del salario por la empresa."
    },
    "Chequeos médicos ejecutivos": {
        "valor": 0,
        "nota": "Valor por evento depende del rol"
    }
}

# --------------------------------------
# FÓRMULAS PARA BENEFICIOS CON VALOR 0 (DINÁMICOS DESDE CÓDIGO)
# --------------------------------------
# Escribe expresiones usando: salario, smmlv, salario_dia
# y funciones: min, max, round, abs
# Ejemplos: "salario*0.02", "salario/12", "salario_dia*3", "min(salario*0.1, 150000)"
BENEFITS_FORMULAS: Dict[str, str] = {
    # Días/eventos prorrateados (ejemplos):
    "Incapacidades cubiertas al 100% (administrativos)": "(salario/30)*10*0.33",  # 10 días/año, prorrateado mensual
    "Día libre de cumpleaños": "(salario/30)",                               # 1 día/año, prorrateado mensual
    "Día libre de la familia": "(salario/30)",
    "Leasing (Gerencias/Vice/Presidencia)": "120_000_000 if cargo in ['Alta gerencia', 'Gerencia'] else 0",  # 1 día/semestre aprox. (ajusta si deseas)
    "Permiso remunerado por matrimonio (3 días)": "(salario/30)*3",          # 3 días/año (si prorrateas)
    # Reglas por porcentaje / SMMLV:
    "Auxilio educativo escolar (~60% SMLV adm.)": "(0.6*smmlv) if (hijos and salario <= 9_168_000) else 0",
    "Prima extralegal de navidad (30 días)": "salario",
    # Condición por rango de SMMLV:
    "Bonificación de vacaciones (15 días)": "(salario*0.5) if 1.6 < (salario/smmlv) < 5.4 else 0",
    # Piso/techo entre 4 y 12 SMMLV:
    "Auxilio de fallecimiento del empleado (4–12 SMMLV)": "min(max(salario, 4*smmlv), 12*smmlv)",
    # Otros prorrateos referenciales:
    "Auxilio por nacimiento (~40% SMLV por evento)": "0.4*smmlv",
    "Auxilio de visión (hasta 50% SMLV)": "0.5*smmlv",
    "Chequeos médicos ejecutivos": "1_500_000 if cargo in ['Alta gerencia', 'Gerencia'] else 0",
    "Bonificación por pensión (2 meses)": "salario*2",
    # Si no quieres que alguno sea dinámico, elimínalo o déjalo en "0".
    "Donación de materiales (banco de materiales)": "0 if salario/smmlv > 8 else (10_000_000)",
    "Ahorro mutuo Corona (aporte empresa)": "salario*0.02",
    "Mis beneficios a la carta (cupo % salario)": "salario * (0.10 if 1_750_905 <= salario <= 3_960_000 else 0.07 if 3_960_000 < salario < 9_168_000 else 0)",
    "Auxilio de educación superior": "min(valor_semestre * 0.8, 4.8 * smmlv) if estudiante else 0",
    "Póliza de vida (12 salarios)" : "12 * salario if 12 * salario >= 42_000_000 else 42_000_000",
    "Jornada flexible mamá": "salario*0.3",
    "Antigüedad en días de descanso (TTT)" : "(salario / 30)*(8 if antiguedad >= 20 else 5 if antiguedad >= 10 else 4 if antiguedad >= 7 else 3 if antiguedad >= 5 else 2 if antiguedad >= 3 else 0)"


}





def safe_eval_formula(
    expr: str,
    *,
    salario: float,
    smmlv: float,
    cargo: str,
    hijos: bool,
    antiguedad: int,
    estudiante: bool,
    valor_semestre: float
) -> float:


    local_vars = {
        "salario": float(salario),
        "smmlv": float(smmlv),
        "salario_dia": float(salario / 30.0 if salario else 0.0),
        "cargo": cargo,
        "hijos": hijos,
        "antiguedad": antiguedad,
        "estudiante": estudiante,
        "valor_semestre": float(valor_semestre),
        "min": min,
        "max": max,
        "round": round,
        "abs": abs,
    }


    val = float(eval(expr, {"__builtins__": {}}, local_vars))
    return max(0.0, val)

# --------------------------
# ESTADO / SESIÓN
# --------------------------
if "beneficios" not in st.session_state:
    st.session_state.beneficios = BENEFITS_DEFAULTS.copy()
if "custom_items" not in st.session_state:
    st.session_state.custom_items: Dict[str, float] = {}

# --------------------------
# SIDEBAR (Controles)
# --------------------------
st.sidebar.image(
    "https://empresa.corona.co/wp-content/uploads/2023/02/corona.png",
    width=200
)
st.sidebar.markdown("### ⚙️ Parámetros")


modo_edicion = st.sidebar.toggle("🛠️ Editar valores de beneficios en la interfaz", value=False)

# --------------------------
# ESTILOS (neutros, sin selectores de color)
# --------------------------
st.markdown(
    """
    <style>
    :root {
        --text: #1A1A1A;
        --muted: #556070;
        --card: #FFFFFF;
        --bg: #F6F8FB;
        --border: #E9EEF5;
    }
    .stApp { background-color: var(--bg); }
    h1, h2, h3, h4, h5, h6 { color: #0B3A82; letter-spacing: 0.2px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 1rem 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
    .badge { display:inline-block; background: #FFD15E; color:#1A1A1A; border-radius:999px; padding:.2rem .7rem; font-weight:600; font-size:0.85rem; vertical-align:middle; }
    @media (min-width: 992px) { .sticky-panel { position: sticky; top: 1rem; } }
    input[type="checkbox"] { accent-color: auto; }
    [data-testid="stMetricValue"] { color: #0B3A82; }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# CABECERA
# --------------------------
st.title("Simulador de Auxilios y Beneficios")
st.markdown('<span class="badge">Ajusta salario, SMMLV y beneficios para ver el impacto total mensual. Los beneficios desmarcados no se suman.</span>', unsafe_allow_html=True)

# --------------------------
# CÁLCULOS
# --------------------------
def fmt_cop(x: float) -> str:
    try:
        return f"$ {x:,.0f}".replace(",", ".")
    except Exception:
        return f"$ {x}"

salario_smmlv = (salario / smmlv) if smmlv > 0 else 0

# --------------------------------------
# CÁLCULO DE VALORES EFECTIVOS PARA ÍTEMS EN 0
# (solo usa fórmula si el valor base es 0 y hay fórmula definida)
# --------------------------------------
beneficios_efectivos: Dict[str, float] = {}
errores_formula: Dict[str, str] = {}

for nombre, data in st.session_state.beneficios.items():
    base_val = float(data.get("valor", 0) or 0)

    if base_val == 0 and nombre in BENEFITS_FORMULAS:
        expr = BENEFITS_FORMULAS[nombre]
        try:
            if isinstance(expr, (int, float)):
                val = float(expr)
            else:
                expr_str = str(expr).strip()
                if expr_str == "" or expr_str == "0":
                    val = 0.0
                else:

                    val = round(safe_eval_formula(expr_str, salario=salario, smmlv=smmlv, cargo=cargo, hijos=tiene_hijos, antiguedad=antiguedad, estudiante=es_estudiante, valor_semestre=Valor_semestre))
            beneficios_efectivos[nombre] = round(val)
        except Exception as e:
            beneficios_efectivos[nombre] = 0.0
            errores_formula[nombre] = str(e)
    else:
        beneficios_efectivos[nombre] = base_val

# --------------------------
# LAYOUT: izquierda (beneficios) · derecha (resultados)
# --------------------------
left, right = st.columns([3, 3], vertical_alignment="top")

# ----- IZQUIERDA: selección/edición de beneficios -----
with left:
    st.subheader("Beneficios")
    st.caption("Activa/desactiva cada beneficio. Los que estén en 0 y tengan fórmula se calculan dinámicamente (no editables).")

    benef_names = list(st.session_state.beneficios.keys())
    mid = math.ceil(len(benef_names) / 2)
    cols = st.columns(2)

    # === Selección masiva ===
    c1, c2 = st.columns(2)
    if c1.button("Seleccionar todo", use_container_width=True):
        for i, _ in enumerate(benef_names):
            st.session_state[f"chk_{i}"] = True

    if c2.button("Deseleccionar todo", use_container_width=True):
        for i, _ in enumerate(benef_names):
            st.session_state[f"chk_{i}"] = False

    # Inicializa el estado de cada checkbox la primera vez
    for i, name in enumerate(benef_names):
        key = f"chk_{i}"
        if key not in st.session_state:
            base_val = float(st.session_state.beneficios[name].get("valor", 0) or 0)
            val_resuelto = float(beneficios_efectivos.get(name, base_val))
            st.session_state[key] = False

    incluidos: Dict[str, float] = {}
    excluidos: List[str] = []

    for i, name in enumerate(benef_names):
        col = cols[0] if i < mid else cols[1]
        with col:
            data = st.session_state.beneficios[name]
            base_val = float(data.get("valor", 0) or 0)
            nota = data.get("nota", "")

            # Valor ya resuelto (base o calculado por fórmula)
            val_resuelto = float(beneficios_efectivos.get(name, base_val))

            # ✅ Usa el estado (afectado por los botones)
            checked = st.checkbox(f"✔ {name}", key=f"chk_{i}")

            # Si el valor proviene de fórmula (base era 0 y existe fórmula), no permitir edición manual
            viene_de_formula = (base_val == 0 and name in BENEFITS_FORMULAS)

            if viene_de_formula:
                st.write(f"**Valor :** {fmt_cop(val_resuelto)}")
                if nota:
                    st.caption(nota)
                if name in errores_formula:
                    st.warning(f"⚠️ Error al evaluar fórmula: {errores_formula[name]}")
                val = val_resuelto
            else:
                # Manual (editable) si está en modo edición o si el valor sigue en 0
                if modo_edicion or base_val == 0:
                    val = st.number_input(
                        "Valor mensual",
                        min_value=0.0,
                        step=10_000.0,
                        value=float(val_resuelto),
                        key=f"val_{i}",
                        help=nota
                    )
                else:
                    st.write(f"**Valor :** {fmt_cop(val_resuelto)}")
                    if nota:
                        st.caption(nota)
                    val = val_resuelto

            if checked and val > 0:
                incluidos[name] = float(val)
            else:
                excluidos.append(name)

    st.markdown("### ➕ Beneficios personalizados")
    cc1, cc2, cc3 = st.columns([3, 2, 1])
    with cc1:
        custom_name = st.text_input("Nombre del beneficio")
    with cc2:
        custom_value = st.number_input("Valor mensual (COP)", min_value=0.0, step=10_000.0, value=0.0)
    with cc3:
        if st.button("Agregar"):
            if custom_name and custom_value > 0:
                st.session_state.custom_items[custom_name] = float(custom_value)
            else:
                st.warning("Ingresa un nombre y un valor > 0 para agregar.")

# Unir incluidos + personalizados
incluidos_final = incluidos.copy()
incluidos_final.update(st.session_state.custom_items)

# Totales
total_beneficios = sum(incluidos_final.values())
total_compensacion = salario + total_beneficios
total_smmlv = (total_compensacion / smmlv) if smmlv > 0 else 0

# ----- DERECHA: resultados (sticky en desktop) -----
with right:
    st.markdown('<div class="sticky-panel">', unsafe_allow_html=True)
    st.subheader("Resultados")

    # Métricas principales
    mc1, mc2 = st.columns(2)
    mc1.metric("Salario", fmt_cop(salario))
    mc2.metric("SMMLV", fmt_cop(smmlv))

    mc3, mc4 = st.columns(2)
    mc3.metric("Salario en SMMLV", f"{salario_smmlv:,.2f}")
    mc4.metric("Beneficios", fmt_cop(total_beneficios))

    mc5, mc6 = st.columns(2)
    mc5.metric("Total compensación", fmt_cop(total_compensacion))
    mc6.metric("Total en SMMLV", f"{total_smmlv:,.2f}")

    st.markdown("---")

    with st.expander("📋 Detalle de beneficios incluidos"):
        if incluidos_final:
            for k, v in sorted(incluidos_final.items()):
                st.write(f"- **{k}**: {fmt_cop(v)}")
        else:
            st.write("No hay beneficios activos.")

    with st.expander("🚫 Beneficios excluidos (no se suman)"):
        if excluidos:
            st.write(", ".join(excluidos))
        else:
            st.write("Todos los beneficios están activos.")
    st.markdown("</div>", unsafe_allow_html=True)

# Nota final
# st.caption(
#     "⚠️ Este simulador estima valores mensuales. Para beneficios que son eventos "
#     "(por ejemplo, primas o auxilios únicos), considera prorratearlos si aplica."
# )
