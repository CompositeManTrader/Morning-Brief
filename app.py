import streamlit as st
from groq import Groq
from datetime import date
import time

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
# Obtén tu key GRATIS en: console.groq.com  (crea cuenta → API Keys → Create)
GROQ_API_KEY = "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"   # ← reemplaza con tu key de Groq

# Modelo: llama-3.3-70b-versatile — el mejor en calidad/velocidad en Groq free tier
# Límites free tier: 30 req/min, 14,400 req/día → más que suficiente
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Morning Brief",
    page_icon="▶",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Bloomberg-style CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    background-color: #0d0d0d !important;
    color: #e0e0e0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 1400px; }

.bb-topbar {
    background: #0a0a0a;
    border-bottom: 2px solid #ff6600;
    padding: 0;
    margin: 0 -2rem 0 -2rem;
    display: flex;
    align-items: stretch;
}
.bb-logo {
    background: #ff6600;
    color: #000;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 1.05rem;
    padding: 10px 20px;
    letter-spacing: 1px;
    white-space: nowrap;
}
.bb-title {
    color: #ff6600;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 12px 24px;
    border-right: 1px solid #222;
}
.bb-date {
    color: #666;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    padding: 12px 20px;
    margin-left: auto;
}
.bb-ticker {
    background: #111;
    border-bottom: 1px solid #222;
    padding: 6px 2rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #444;
    letter-spacing: 1px;
}
.bb-ticker span { color: #ff6600; margin-right: 4px; }
.bb-ticker .up { color: #00d084; }
.bb-ticker .dn { color: #ff4444; }
.bb-ticker .sep { color: #333; margin: 0 16px; }

.bb-section {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 24px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #222;
}
.bb-section-label {
    background: #ff6600;
    color: #000;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.bb-section-title {
    color: #fff;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.bb-section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, #333, transparent);
}

.stTabs [data-baseweb="tab-list"] {
    background: #111 !important;
    border-bottom: 1px solid #333 !important;
    border-radius: 0 !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 0 !important;
    border-right: 1px solid #222 !important;
    color: #555 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 12px 24px !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #1a1a1a !important;
    color: #ff6600 !important;
}
.stTabs [aria-selected="true"] {
    background: #1a1a1a !important;
    color: #ff6600 !important;
    border-bottom: 2px solid #ff6600 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 0 !important;
}

.stTextArea textarea {
    background: #0f0f0f !important;
    border: 1px solid #2a2a2a !important;
    border-left: 3px solid #333 !important;
    border-radius: 2px !important;
    color: #ccc !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    line-height: 1.7 !important;
    caret-color: #ff6600 !important;
}
.stTextArea textarea:focus {
    border-left-color: #ff6600 !important;
    box-shadow: none !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #2a2a2a !important; }

.output-area textarea {
    background: #070707 !important;
    border: 1px solid #1e1e1e !important;
    border-left: 3px solid #ff6600 !important;
    color: #d4d4d4 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    line-height: 1.8 !important;
}

.stButton > button {
    background: #ff6600 !important;
    color: #000 !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 10px 28px !important;
}
.stButton > button:hover {
    background: #e55a00 !important;
    color: #000 !important;
}

.bb-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: #444;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.bb-pill {
    display: inline-block;
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    color: #666;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    padding: 3px 10px;
    margin-right: 6px;
    letter-spacing: 1px;
}
.bb-pill span { color: #00d084; }
.bb-pill span.warn { color: #ff6600; }
.bb-copy-hint {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #333;
    margin-top: 6px;
    letter-spacing: 0.5px;
}
.bb-copy-hint::before { content: "▶ "; color: #ff6600; }

.streamlit-expanderHeader {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 0 !important;
    color: #888 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
}
.streamlit-expanderContent {
    background: #0a0a0a !important;
    border: 1px solid #1a1a1a !important;
    border-top: none !important;
}
hr { border-color: #1e1e1e !important; }
.stSpinner > div { border-top-color: #ff6600 !important; }
.stProgress > div > div { background-color: #ff6600 !important; }
</style>
""", unsafe_allow_html=True)

# ── Prompts ───────────────────────────────────────────────────────────────────
PROMPT_INTL = """Eres un redactor financiero senior que escribe el Morning Brief diario para una mesa institucional de renta variable.

TAREA: Recibirás noticias separadas por bullets (•, -, *, >, números) o saltos de línea. Para CADA noticia produce UN bullet resumido en español.

REGLAS DE REDACCIÓN:
- Cada resumen debe tener entre 25 y 38 palabras. Ni más corto ni más largo.
- Inicia cada bullet con "•" seguido de espacio.
- Estructura ideal: [Sujeto/empresa/activo] + [qué pasó] + [por qué o impacto clave].
- Incluye cifras, porcentajes o datos concretos si están en la noticia original.
- Tono directo, sin adjetivos innecesarios. Estilo Bloomberg terminal.
- PROHIBIDO: introducción, conclusión, títulos, numeración, cualquier texto fuera de los bullets.

EJEMPLO DE INPUT:
• Fed holds rates steady at 4.25%-4.5%, signals two cuts in 2025 amid cooling inflation data

EJEMPLO DE OUTPUT CORRECTO:
• La Fed mantuvo tasas en 4.25%-4.50% y proyectó dos recortes en 2025, respaldada por datos de inflación en desaceleración y un mercado laboral todavía resiliente.

EJEMPLO DE OUTPUT INCORRECTO (demasiado corto):
• La Fed mantuvo tasas y proyectó recortes en 2025.

Noticias a resumir:
"""

PROMPT_MOVERS = """Eres un redactor financiero senior para una mesa institucional en México. Traduces y reformateas los movers de CNBC al formato de nuestro Morning Brief.

FORMATO EXACTO POR EMPRESA (sigue esto al pie de la letra):
TICKER, Nombre Completo de la Empresa, subió/bajó X.XX%. [Explicación del catalizador en lenguaje fluido y preciso, entre 20 y 30 palabras].

REGLAS:
1. El ticker va SIN negritas, SIN asteriscos, SIN ningún formato especial. Texto plano.
2. Coma después del ticker, luego el nombre completo de la empresa.
3. "subió" si el precio aumentó, "bajó" si disminuyó. Seguido de la variación con dos decimales y "%".
4. Usa punto decimal, no coma: 1.25% correcto, 1,25% incorrecto.
5. Cifras monetarias: "US$" antes del número. Ejemplo: US$2.40.
6. Después del porcentaje, punto y seguido: explica el catalizador con redacción fluida y rica. Menciona el banco/analista si aplica, la acción corporativa, el dato o el evento que lo mueve.
7. Una línea en blanco entre cada empresa.
8. Sin negritas, sin cursivas, sin asteriscos en ninguna parte del texto.
9. Sin encabezados, sin numeración, sin texto extra.

EJEMPLOS DE OUTPUT CORRECTO (observa: sin asteriscos, sin negritas, texto plano):
CMG, Chipotle Mexican Grill, subió 1.00%. Avanzó luego de que Mizuho mejoró su recomendación a outperform, por expectativas de mejor crecimiento comparable y mayor visibilidad en márgenes.

NVDA, Nvidia, subió 4.20%. Impulsada por la presentación de su nueva línea de chips Blackwell Ultra, que superó las expectativas del mercado en capacidad de procesamiento para inteligencia artificial.

TSLA, Tesla, bajó 3.50%. Retrocedió tras reportar entregas del primer trimestre muy por debajo de las estimaciones de Wall Street, con 336,000 unidades frente a las 390,000 esperadas por el consenso.

GS, Goldman Sachs, subió 2.10%. Rebotó luego de que la firma anunció una recompra de acciones por US$30,000 millones y reportó ingresos en banca de inversión superiores a lo previsto por los analistas.

Texto CNBC a procesar:
"""

PROMPT_BMV = """Eres un redactor financiero senior para una mesa institucional en México.

TAREA: Resume UNA noticia de empresa BMV o BIVA para el Morning Brief diario.

FORMATO:
- Si la noticia tiene ticker: inicia con el ticker SIN negritas SIN asteriscos, seguido de coma y el resumen.
- Si no hay ticker: ve directo al resumen.
- Entre 30 y 45 palabras. Ni más corto ni más largo.
- Incluye el dato o cifra más relevante de la noticia.
- Tono directo, estilo Bloomberg. Redacción fluida, una o dos oraciones cortas.
- NADA en negritas, NADA en cursivas, NADA con asteriscos. Texto plano únicamente.
- SOLO el resumen. Sin "Resumen:", sin introducción, sin texto extra.

EJEMPLO DE OUTPUT CORRECTO (observa: sin asteriscos, texto plano):
BIMBOA, Grupo Bimbo reportó ingresos del 1T25 por US$5,200 millones, un alza de 4.3% anual impulsada por mayores precios en Norteamérica, aunque el margen EBITDA se contrajo 80 puntos base por costos de trigo.

GFNORTEO, Banorte reportó una utilidad neta de MX$12,300 millones en el 1T25, crecimiento de 8.2% anual, apoyado por expansión de cartera de crédito y mejora en el margen financiero neto.

Noticia:
"""

# ── Groq call — rápido, sin reintentos largos ─────────────────────────────────
def call_groq(prompt: str, content: str) -> str:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": content},
        ],
        temperature=0.4,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()

# ── TOP BAR ───────────────────────────────────────────────────────────────────
today     = date.today()
days_es   = ["LUNES","MARTES","MIÉRCOLES","JUEVES","VIERNES","SÁBADO","DOMINGO"]
months_es = ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"]
date_str  = f"{days_es[today.weekday()]} {today.day:02d} {months_es[today.month-1]} {today.year}"

st.markdown(f"""
<div class="bb-topbar">
    <div class="bb-logo">▶ BRIEF</div>
    <div class="bb-title">MORNING BRIEF &nbsp;·&nbsp; RENTA VARIABLE</div>
    <div class="bb-date">{date_str} &nbsp;|&nbsp; CDMX</div>
</div>
<div class="bb-ticker">
    <span>INDICES</span>
    S&P 500 <span class="up">▲</span>
    <span class="sep">|</span>
    NASDAQ <span class="up">▲</span>
    <span class="sep">|</span>
    DOW <span class="up">▲</span>
    <span class="sep">|</span>
    IPC <span class="up">▲</span>
    <span class="sep">|</span>
    VIX <span class="dn">▼</span>
    <span class="sep">|</span>
    DXY <span class="dn">▼</span>
    <span class="sep">|</span>
    WTI <span class="up">▲</span>
    <span class="sep">|</span>
    GOLD <span class="up">▲</span>
    <span class="sep">||</span>
    <span>ENGINE</span> GROQ · LLAMA-3.3-70B · ~2s RESPONSE
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

st.markdown("""
<div style='margin-bottom:20px'>
    <span class="bb-pill">ENGINE <span>GROQ</span></span>
    <span class="bb-pill">MODELO <span>LLAMA-3.3-70B</span></span>
    <span class="bb-pill">VELOCIDAD <span>~2 SEG</span></span>
    <span class="bb-pill">LÍMITE <span class="warn">30 REQ/MIN</span></span>
    <span class="bb-pill">CUOTA DIARIA <span>14,400</span></span>
    <span class="bb-pill">COSTO <span>$0.00</span></span>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "  🌐  INTERNACIONALES  ",
    "  📊  MOVERS CNBC  ",
    "  🇲🇽  BMV / BIVA  ",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Noticias Internacionales
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div class="bb-section">
        <div class="bb-section-label">01</div>
        <div class="bb-section-title">Noticias Financieras Internacionales</div>
        <div class="bb-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="bb-label">INPUT — PEGA LAS NOTICIAS (bullets •  -  *  números, o una por línea)</div>', unsafe_allow_html=True)

    intl_input = st.text_area(
        "intl_in",
        height=220,
        placeholder="• Fed mantiene tasas sin cambio tras reunión de marzo...\n• El oro alcanza nuevo máximo histórico por encima de US$3,000...\n- Apple reporta ganancias por encima de lo esperado en Q1...\n1. Nvidia supera estimaciones de Wall Street en resultados trimestrales...",
        key="intl_input",
        label_visibility="collapsed",
    )

    col1, col2, _ = st.columns([1.2, 1, 6])
    with col1:
        gen_intl = st.button("▶  GENERAR", key="btn_intl", use_container_width=True)
    with col2:
        if st.button("✕  LIMPIAR", key="clr_intl", use_container_width=True):
            st.session_state.pop("intl_result", None)
            st.rerun()

    if gen_intl:
        if not intl_input.strip():
            st.warning("Pega al menos una noticia.")
        else:
            with st.spinner("Generando..."):
                try:
                    t0 = time.time()
                    st.session_state["intl_result"] = call_groq(PROMPT_INTL, intl_input)
                    st.session_state["intl_time"] = round(time.time() - t0, 1)
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.get("intl_result"):
        t = st.session_state.get("intl_time", "")
        st.markdown(f'<div class="bb-label">OUTPUT — GENERADO EN {t}s · CLIC → CTRL+A → CTRL+C</div>', unsafe_allow_html=True)
        st.markdown('<div class="output-area">', unsafe_allow_html=True)
        st.text_area(
            "out_intl",
            value=st.session_state["intl_result"],
            height=280,
            key="intl_output_area",
            label_visibility="collapsed",
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="bb-copy-hint">CLIC EN EL CUADRO · CTRL+A · CTRL+C</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Movers CNBC
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class="bb-section">
        <div class="bb-section-label">02</div>
        <div class="bb-section-title">Movers CNBC — Formato Institucional</div>
        <div class="bb-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="bb-label">INPUT — PEGA EL TEXTO DE MOVERS EN INGLÉS</div>', unsafe_allow_html=True)

    movers_input = st.text_area(
        "mov_in",
        height=220,
        placeholder="Apple (AAPL) shares rose 3.2% after the company reported better-than-expected earnings of $2.40 per share...\nTesla (TSLA) fell 5,1% following a disappointing delivery report for Q1...\nNvidia (NVDA) surged 8% after announcing new AI chip lineup...",
        key="movers_input",
        label_visibility="collapsed",
    )

    col1, col2, _ = st.columns([1.2, 1, 6])
    with col1:
        gen_movers = st.button("▶  GENERAR", key="btn_movers", use_container_width=True)
    with col2:
        if st.button("✕  LIMPIAR", key="clr_movers", use_container_width=True):
            st.session_state.pop("movers_result", None)
            st.rerun()

    if gen_movers:
        if not movers_input.strip():
            st.warning("Pega el texto de movers CNBC.")
        else:
            with st.spinner("Generando..."):
                try:
                    t0 = time.time()
                    st.session_state["movers_result"] = call_groq(PROMPT_MOVERS, movers_input)
                    st.session_state["movers_time"] = round(time.time() - t0, 1)
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.get("movers_result"):
        t = st.session_state.get("movers_time", "")
        col_prev, col_copy = st.columns(2)
        with col_prev:
            st.markdown(f'<div class="bb-label">PREVIEW — GENERADO EN {t}s</div>', unsafe_allow_html=True)
            preview_html = st.session_state["movers_result"].replace("\n", "<br>")
            st.markdown(f"""
            <div style="
                background:#070707; border:1px solid #1e1e1e;
                border-left:3px solid #ff6600; padding:16px 20px;
                font-family:'IBM Plex Mono',monospace; font-size:0.8rem;
                line-height:1.9; color:#d4d4d4; min-height:200px;
            ">{preview_html}</div>
            """, unsafe_allow_html=True)
        with col_copy:
            st.markdown('<div class="bb-label">OUTPUT — CTRL+A → CTRL+C</div>', unsafe_allow_html=True)
            st.markdown('<div class="output-area">', unsafe_allow_html=True)
            st.text_area(
                "out_movers",
                value=st.session_state["movers_result"],
                height=260,
                key="movers_output_area",
                label_visibility="collapsed",
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="bb-copy-hint">CLIC EN EL CUADRO · CTRL+A · CTRL+C</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — BMV / BIVA
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div class="bb-section">
        <div class="bb-section-label">03</div>
        <div class="bb-section-title">Noticias BMV / BIVA — Resúmenes Individuales</div>
        <div class="bb-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if "bmv_count" not in st.session_state:
        st.session_state["bmv_count"] = 3

    col_add, col_rem, col_info = st.columns([1, 1, 6])
    with col_add:
        if st.button("+ NOTICIA", key="add_bmv", use_container_width=True):
            if st.session_state["bmv_count"] < 10:
                st.session_state["bmv_count"] += 1
    with col_rem:
        if st.button("− QUITAR", key="rem_bmv", use_container_width=True):
            if st.session_state["bmv_count"] > 1:
                st.session_state["bmv_count"] -= 1
                st.session_state.pop(f"bmv_result_{st.session_state['bmv_count']}", None)
    with col_info:
        st.markdown(f"""
        <div style="padding:8px 0">
            <span class="bb-pill">SLOTS <span>{st.session_state['bmv_count']}/10</span></span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    bmv_texts = []
    for i in range(st.session_state["bmv_count"]):
        st.markdown(f'<div class="bb-label">NOTICIA {i+1:02d}</div>', unsafe_allow_html=True)
        text = st.text_area(
            f"bmv_in_{i}",
            height=100,
            placeholder=f"Pega aquí la noticia {i+1} de BMV/BIVA...",
            key=f"bmv_input_{i}",
            label_visibility="collapsed",
        )
        bmv_texts.append(text)
        if i < st.session_state["bmv_count"] - 1:
            st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col1, col2, _ = st.columns([1.5, 1, 5.5])
    with col1:
        gen_bmv = st.button("▶  GENERAR TODOS", key="btn_bmv", use_container_width=True)
    with col2:
        if st.button("✕  LIMPIAR", key="clr_bmv", use_container_width=True):
            for i in range(10):
                st.session_state.pop(f"bmv_result_{i}", None)
            st.rerun()

    if gen_bmv:
        filled = [(i, t) for i, t in enumerate(bmv_texts) if t.strip()]
        if not filled:
            st.warning("Pega al menos una noticia.")
        else:
            progress = st.progress(0)
            status   = st.empty()
            t_total  = time.time()
            for idx, (i, text) in enumerate(filled):
                status.markdown(f'<div class="bb-label">PROCESANDO NOTICIA {i+1}/{len(filled)}...</div>', unsafe_allow_html=True)
                progress.progress((idx + 1) / len(filled))
                try:
                    st.session_state[f"bmv_result_{i}"] = call_groq(PROMPT_BMV, text)
                except Exception as e:
                    st.session_state[f"bmv_result_{i}"] = f"ERROR: {e}"
            elapsed = round(time.time() - t_total, 1)
            progress.empty()
            status.markdown(f'<div class="bb-label" style="color:#00d084">✓ {len(filled)} RESÚMENES EN {elapsed}s</div>', unsafe_allow_html=True)

    any_result = any(f"bmv_result_{i}" in st.session_state for i in range(st.session_state["bmv_count"]))
    if any_result:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="bb-section">
            <div class="bb-section-label">OUT</div>
            <div class="bb-section-title">Resúmenes Generados</div>
            <div class="bb-section-line"></div>
        </div>
        """, unsafe_allow_html=True)

        all_summaries = []
        for i in range(st.session_state["bmv_count"]):
            key = f"bmv_result_{i}"
            if key in st.session_state:
                r = st.session_state[key]
                all_summaries.append(r)
                with st.expander(f"NOTICIA {i+1:02d}", expanded=True):
                    st.markdown('<div class="output-area">', unsafe_allow_html=True)
                    st.text_area(
                        f"out_bmv_{i}",
                        value=r,
                        height=85,
                        key=f"bmv_out_{i}",
                        label_visibility="collapsed",
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

        if all_summaries:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="bb-label">TODOS LOS RESÚMENES — CTRL+A → CTRL+C</div>', unsafe_allow_html=True)
            st.markdown('<div class="output-area">', unsafe_allow_html=True)
            st.text_area(
                "bmv_all",
                value="\n\n".join(all_summaries),
                height=320,
                key="bmv_all_output",
                label_visibility="collapsed",
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="bb-copy-hint">CLIC EN EL CUADRO · CTRL+A · CTRL+C</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    margin-top: 40px; padding: 12px 0;
    border-top: 1px solid #1a1a1a;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; color: #2a2a2a;
    letter-spacing: 1px;
    display: flex; justify-content: space-between;
">
    <span>MORNING BRIEF · USO INTERNO · NO DISTRIBUIR</span>
    <span>POWERED BY GROQ · LLAMA-3.3-70B · FREE TIER</span>
</div>
""", unsafe_allow_html=True)
