import streamlit as st
from google import genai
from datetime import date
import time

# ── API KEY — hardcodeada, no necesitas ingresarla cada vez ──────────────────
GEMINI_API_KEY = "AIzaSyDqLAODMX1RqN2ZBTMPfxdVhcqtaGsv3tM"


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

/* ── Global reset ── */
html, body, [class*="css"], .stApp {
    background-color: #0d0d0d !important;
    color: #e0e0e0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 1400px; }

/* ── Top bar ── */
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

/* ── Ticker tape ── */
.bb-ticker {
    background: #111;
    border-bottom: 1px solid #222;
    padding: 6px 2rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #444;
    letter-spacing: 1px;
    overflow: hidden;
    white-space: nowrap;
}
.bb-ticker span { color: #ff6600; margin-right: 4px; }
.bb-ticker .up { color: #00d084; }
.bb-ticker .dn { color: #ff4444; }
.bb-ticker .sep { color: #333; margin: 0 16px; }

/* ── Section headers ── */
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

/* ── Tabs ── */
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
    transition: all 0.15s !important;
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

/* ── Input areas ── */
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
    resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: #333 !important;
    border-left-color: #ff6600 !important;
    box-shadow: none !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #333 !important; }

/* ── Output area (resultado) ── */
.output-area textarea {
    background: #070707 !important;
    border: 1px solid #1e1e1e !important;
    border-left: 3px solid #ff6600 !important;
    color: #d4d4d4 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    line-height: 1.8 !important;
}

/* ── Buttons ── */
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
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #e55a00 !important;
    color: #000 !important;
}
.stButton > button:active {
    background: #cc4f00 !important;
}

/* ── Sidebar (collapsed, not needed) ── */
section[data-testid="stSidebar"] { display: none; }

/* ── Labels ── */
.bb-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: #444;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* ── Info pills ── */
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
.bb-pill span { color: #ff6600; }

/* ── Copy hint ── */
.bb-copy-hint {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #333;
    margin-top: 6px;
    letter-spacing: 0.5px;
}
.bb-copy-hint::before { content: "▶ "; color: #ff6600; }

/* ── Expander (BMV cards) ── */
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

/* ── Divider ── */
hr { border-color: #1e1e1e !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #ff6600 !important; }

/* ── Alert / error / warning ── */
.stAlert { border-radius: 0 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.78rem !important; }

/* ── Progress bar ── */
.stProgress > div > div { background-color: #ff6600 !important; }

/* ── Success ── */
.element-container .stSuccess {
    background: #0a1a0a !important;
    border-left: 3px solid #00d084 !important;
    color: #00d084 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Prompts ───────────────────────────────────────────────────────────────────
PROMPT_INTL = """Eres un redactor financiero experto para clientes institucionales.
Recibirás noticias financieras internacionales. Cada noticia puede estar separada por bullets de cualquier tipo: •, -, *, >, números seguidos de punto o paréntesis, o simplemente saltos de línea.
Reglas ESTRICTAS:
- Detecta cada noticia/ítem individual.
- Para CADA noticia escribe UN resumen en español de MENOS DE 40 PALABRAS.
- Inicia cada resumen con "•" seguido de espacio.
- Lenguaje claro, directo y profesional, estilo bloomberg.
- NO añadas introducción, títulos ni conclusión. SOLO los bullets resumidos, uno por línea.

Noticias:
"""

PROMPT_MOVERS = """Eres un redactor financiero experto para clientes institucionales en México.
Recibirás texto en inglés sobre movers de CNBC. Tradúcelo aplicando EXACTAMENTE estas reglas:
1. Cada bloque inicia con el TICKER en negritas markdown (**TICKER**), coma, nombre de empresa, luego si subió o bajó con su variación porcentual.
2. Máximo 30 palabras por bloque.
3. Cifras de moneda inician con "US$".
4. En variaciones porcentuales reemplaza "," por ".".
5. SOLO el ticker va en negritas (**TICKER**), nada más en negritas.
6. Separa cada empresa con una línea en blanco.
7. Sin encabezados ni texto extra. Solo los bloques.

Texto CNBC:
"""

PROMPT_BMV = """Eres un redactor financiero experto para clientes institucionales en México.
Recibirás UNA noticia de una empresa de la BMV o BIVA.
Escribe un resumen en español, claro y directo, de MENOS DE 50 PALABRAS, estilo Bloomberg.
Menciona el ticker si aparece en el texto.
Sin introducción ni texto extra. Solo el resumen.

Noticia:
"""

# ── Gemini call con retry automático ─────────────────────────────────────────
# Nombres de modelo a intentar en orden (el SDK nuevo es sensible al nombre exacto)
MODEL_CANDIDATES = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "models/gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-2.0-flash-lite",   # alternativa si 1.5 no está disponible
]

def _try_models(client, full_prompt: str) -> str:
    """Intenta cada nombre de modelo hasta encontrar uno que funcione."""
    last_err = None
    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
            )
            # Guarda el modelo que funcionó para futuras llamadas
            st.session_state["working_model"] = model_name
            return response.text.strip()
        except Exception as e:
            err_str = str(e)
            if "404" in err_str or "NOT_FOUND" in err_str:
                last_err = e
                continue   # prueba el siguiente
            raise          # otro error → propagar
    raise last_err

def call_gemini(prompt: str, content: str, retries: int = 3) -> str:
    import re as _re
    client = genai.Client(api_key=GEMINI_API_KEY)
    full_prompt = prompt + content

    # Usa el modelo que ya funcionó antes si está guardado
    working = st.session_state.get("working_model")

    for attempt in range(retries):
        try:
            if working:
                response = client.models.generate_content(
                    model=working,
                    contents=full_prompt,
                )
                return response.text.strip()
            else:
                return _try_models(client, full_prompt)
        except Exception as e:
            err_str = str(e)
            if "404" in err_str or "NOT_FOUND" in err_str:
                # El modelo guardado ya no funciona, resetea y busca de nuevo
                st.session_state.pop("working_model", None)
                working = None
                if attempt < retries - 1:
                    continue
                raise Exception(
                    "No se encontró un modelo Gemini disponible. "
                    "Verifica tu API Key en [aistudio.google.com](https://aistudio.google.com)."
                )
            elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                wait = 60
                m = _re.search(r"'retryDelay':\s*'(\d+)s'", err_str)
                if m:
                    wait = int(m.group(1)) + 5
                if attempt < retries - 1:
                    with st.spinner(f"⏳ Cuota alcanzada — reintentando en {wait}s ({attempt+1}/{retries})..."):
                        time.sleep(wait)
                    continue
                else:
                    raise Exception(
                        f"Cuota agotada. Espera {wait}s e intenta de nuevo, "
                        f"o crea una nueva API Key en [aistudio.google.com](https://aistudio.google.com)."
                    )
            else:
                raise

# ── TOP BAR ──────────────────────────────────────────────────────────────────
today = date.today()
days_es = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
months_es = ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"]
day_name  = days_es[today.weekday()]
month_str = months_es[today.month - 1]
date_str  = f"{day_name} {today.day:02d} {month_str} {today.year}"

st.markdown(f"""
<div class="bb-topbar">
    <div class="bb-logo">▶ BRIEF</div>
    <div class="bb-title">MORNING BRIEF &nbsp;·&nbsp; RENTA VARIABLE</div>
    <div class="bb-date">{date_str} &nbsp;|&nbsp; CDMX</div>
</div>
<div class="bb-ticker">
    <span>INDICES</span>
    S&P 500 <span class="up">▲</span>&nbsp;
    <span class="sep">|</span>
    NASDAQ <span class="up">▲</span>&nbsp;
    <span class="sep">|</span>
    DOW <span class="up">▲</span>&nbsp;
    <span class="sep">|</span>
    IPC <span class="up">▲</span>&nbsp;
    <span class="sep">|</span>
    VIX <span class="dn">▼</span>&nbsp;
    <span class="sep">|</span>
    DXY <span class="dn">▼</span>&nbsp;
    <span class="sep">|</span>
    WTI <span class="up">▲</span>&nbsp;
    <span class="sep">|</span>
    GOLD <span class="up">▲</span>&nbsp;
    <span class="sep">|</span>
    MXN/USD &nbsp;
    <span class="sep">||</span>
    <span>MODELO</span> GEMINI 1.5 FLASH &nbsp;·&nbsp; FREE TIER
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Pills de info ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-bottom:20px'>
    <span class="bb-pill">MODELO <span>GEMINI 1.5 FLASH</span></span>
    <span class="bb-pill">LÍMITE <span>15 REQ/MIN</span></span>
    <span class="bb-pill">CUOTA DIARIA <span>1,500</span></span>
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

    st.markdown('<div class="bb-label">INPUT — PEGA LAS NOTICIAS (con bullets •, -, *, números, o una por línea)</div>', unsafe_allow_html=True)

    intl_input = st.text_area(
        "intl_in",
        height=220,
        placeholder="• Fed mantiene tasas sin cambio tras reunión de marzo...\n• El oro alcanza nuevo máximo histórico por encima de US$3,000...\n- Apple reporta ganancias por encima de lo esperado en Q1...\n1. Nvidia supera estimaciones de Wall Street en resultados...",
        key="intl_input",
        label_visibility="collapsed",
    )

    col1, col2, col3 = st.columns([1.2, 1, 6])
    with col1:
        gen_intl = st.button("▶ GENERAR", key="btn_intl", use_container_width=True)
    with col2:
        if st.button("✕ LIMPIAR", key="clr_intl", use_container_width=True):
            st.session_state.pop("intl_result", None)
            st.rerun()

    if gen_intl:
        if not intl_input.strip():
            st.warning("Pega al menos una noticia.")
        else:
            with st.spinner("Procesando noticias internacionales..."):
                try:
                    st.session_state["intl_result"] = call_gemini(PROMPT_INTL, intl_input)
                except Exception as e:
                    st.error(str(e))

    if st.session_state.get("intl_result"):
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="bb-label">OUTPUT — RESULTADO (clic → Ctrl+A → Ctrl+C)</div>', unsafe_allow_html=True)
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

    col1, col2, col3 = st.columns([1.2, 1, 6])
    with col1:
        gen_movers = st.button("▶ GENERAR", key="btn_movers", use_container_width=True)
    with col2:
        if st.button("✕ LIMPIAR", key="clr_movers", use_container_width=True):
            st.session_state.pop("movers_result", None)
            st.rerun()

    if gen_movers:
        if not movers_input.strip():
            st.warning("Pega el texto de movers CNBC.")
        else:
            with st.spinner("Procesando movers CNBC..."):
                try:
                    st.session_state["movers_result"] = call_gemini(PROMPT_MOVERS, movers_input)
                except Exception as e:
                    st.error(str(e))

    if st.session_state.get("movers_result"):
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        col_prev, col_copy = st.columns(2)

        with col_prev:
            st.markdown('<div class="bb-label">PREVIEW — VISTA CON FORMATO</div>', unsafe_allow_html=True)
            # Render con fondo oscuro
            preview_html = st.session_state["movers_result"].replace("\n", "<br>")
            st.markdown(f"""
            <div style="
                background:#070707;
                border:1px solid #1e1e1e;
                border-left:3px solid #ff6600;
                padding:16px 20px;
                font-family:'IBM Plex Mono',monospace;
                font-size:0.8rem;
                line-height:1.9;
                color:#d4d4d4;
                min-height:200px;
            ">{preview_html}</div>
            """, unsafe_allow_html=True)

        with col_copy:
            st.markdown('<div class="bb-label">OUTPUT — PARA COPIAR (Ctrl+A → Ctrl+C)</div>', unsafe_allow_html=True)
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
            <span class="bb-pill">SLOTS ACTIVOS <span>{st.session_state['bmv_count']}/10</span></span>
            <span class="bb-pill">MAX <span>10 NOTICIAS</span></span>
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

    col1, col2, col3 = st.columns([1.5, 1, 5.5])
    with col1:
        gen_bmv = st.button("▶ GENERAR TODOS", key="btn_bmv", use_container_width=True)
    with col2:
        if st.button("✕ LIMPIAR", key="clr_bmv", use_container_width=True):
            for i in range(10):
                st.session_state.pop(f"bmv_result_{i}", None)
            st.rerun()

    if gen_bmv:
        filled = [(i, t) for i, t in enumerate(bmv_texts) if t.strip()]
        if not filled:
            st.warning("Pega al menos una noticia.")
        else:
            progress = st.progress(0, text="")
            for idx, (i, text) in enumerate(filled):
                pct = (idx + 1) / len(filled)
                progress.progress(pct, text=f"Procesando noticia {i+1}/{len(filled)}...")
                try:
                    st.session_state[f"bmv_result_{i}"] = call_gemini(PROMPT_BMV, text)
                except Exception as e:
                    st.session_state[f"bmv_result_{i}"] = f"ERROR: {e}"
            progress.empty()

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

        if len(all_summaries) >= 1:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="bb-label">TODOS LOS RESÚMENES JUNTOS (Ctrl+A → Ctrl+C)</div>', unsafe_allow_html=True)
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
    margin-top: 40px;
    padding: 12px 0;
    border-top: 1px solid #1a1a1a;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #2a2a2a;
    letter-spacing: 1px;
    display: flex;
    justify-content: space-between;
">
    <span>MORNING BRIEF · USO INTERNO · NO DISTRIBUIR</span>
    <span>POWERED BY GEMINI 1.5 FLASH · FREE TIER</span>
</div>
""", unsafe_allow_html=True)
