import streamlit as st
from google import genai
from datetime import date

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Morning Brief",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 32px;
    border-left: 6px solid #c9a84c;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.main-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: #f0e6d0;
    margin: 0 0 4px 0;
}
.main-header .subtitle {
    color: #c9a84c;
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #1a1a2e;
    border-bottom: 2px solid #c9a84c;
    padding-bottom: 8px;
    margin-bottom: 16px;
}
.stButton > button {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    color: #f0e6d0;
    border: 1px solid #c9a84c;
    border-radius: 8px;
    font-weight: 500;
    padding: 10px 24px;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #c9a84c, #b8922a);
    color: #0a0a0a;
}
section[data-testid="stSidebar"] { background: #0a0a0a; }
section[data-testid="stSidebar"] * { color: #d4c9b0 !important; }
section[data-testid="stSidebar"] .stTextInput input {
    background: #1a1a2e;
    border: 1px solid #c9a84c;
    color: #f0e6d0 !important;
    border-radius: 8px;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #f0ebe0; border-radius: 10px; padding: 4px;
}
.stTabs [data-baseweb="tab"] { border-radius: 8px; font-weight: 500; }
.stTabs [aria-selected="true"] { background: #1a1a2e !important; color: #c9a84c !important; }
.copy-hint { font-size: 0.75rem; color: #999; margin-top: 4px; font-style: italic; }
.status-ok {
    display: inline-block; background: #d4edda; color: #155724;
    border-radius: 20px; padding: 2px 12px; font-size: 0.8rem; font-weight: 500;
}
.status-err {
    display: inline-block; background: #f8d7da; color: #721c24;
    border-radius: 20px; padding: 2px 12px; font-size: 0.8rem; font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ── Prompts ───────────────────────────────────────────────────────────────────
PROMPT_INTL = """Eres un redactor financiero experto para clientes institucionales.
Recibirás noticias financieras internacionales separadas por bullets (•, -, *, o números).
Reglas ESTRICTAS:
- Detecta cada bullet/ítem.
- Para CADA bullet escribe UN resumen en español de MENOS DE 40 PALABRAS.
- Usa "•" al inicio de cada resumen.
- Lenguaje claro, directo y profesional.
- NO añadas introducción, títulos ni conclusión. SOLO los bullets resumidos.

Noticias:
"""

PROMPT_MOVERS = """Eres un redactor financiero experto para clientes institucionales en México.
Recibirás texto en inglés sobre movers de CNBC. Tradúcelo aplicando EXACTAMENTE estas reglas:
1. Cada párrafo inicia con el TICKER en negritas markdown (**TICKER**), coma, nombre de empresa, luego si subió o bajó con su variación porcentual.
2. Máximo 30 palabras por párrafo.
3. Cifras de moneda inician con "US$".
4. En variaciones porcentuales reemplaza "," por ".".
5. SOLO el ticker va en negritas. Nada más.
6. Sin encabezados ni texto extra. Solo los párrafos, uno por empresa.

Texto CNBC:
"""

PROMPT_BMV = """Eres un redactor financiero experto para clientes institucionales en México.
Recibirás UNA noticia de una empresa de la BMV o BIVA.
Escribe un resumen en español, claro y directo, de MENOS DE 50 PALABRAS.
Menciona el ticker si aparece en el texto.
Sin introducción ni texto extra. Solo el resumen.

Noticia:
"""


# ── Gemini call ───────────────────────────────────────────────────────────────
def call_gemini(api_key: str, prompt: str, content: str) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt + content,
    )
    return response.text.strip()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")

    api_key_default = ""
    try:
        api_key_default = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass

    if api_key_default:
        api_key = api_key_default
        st.markdown('<span class="status-ok">✓ API Key cargada</span>', unsafe_allow_html=True)
    else:
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            placeholder="AIzaSy...",
            help="Gratis en aistudio.google.com",
        )
        if api_key:
            st.markdown('<span class="status-ok">✓ API Key ingresada</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-err">⚠ Falta API Key</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"**Fecha:** {date.today().strftime('%d %B %Y')}")
    st.markdown("**Modelo:** Gemini 1.5 Flash *(gratuito)*")
    st.markdown("---")
    st.markdown("### 🔑 Obtener API Key gratis")
    st.markdown("""
1. Ve a [aistudio.google.com](https://aistudio.google.com)
2. Inicia sesión con Google
3. **Get API Key → Create API Key**
4. Pégala arriba ↑

✅ **100% gratis · 1,500 req/día**
""")
    st.markdown("---")
    st.markdown("### 📋 Flujo diario")
    st.markdown("""
1. Abre la app  
2. Pega el contenido en cada pestaña  
3. Genera resumen  
4. Copia → pega en tu Morning Brief  
""")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <div class="subtitle">Institutional Morning Brief</div>
    <h1>📰 Morning Brief</h1>
    <div style="color:#8899aa; font-size:0.9rem; margin-top:8px;">
        {date.today().strftime('%A, %d de %B de %Y')}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🌐 Noticias Internacionales",
    "📊 Movers CNBC",
    "🇲🇽 BMV / BIVA",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Noticias Internacionales
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">🌐 Noticias Financieras Internacionales</div>', unsafe_allow_html=True)
    st.markdown("Pega las noticias con bullets (•, -, *, números). **Menos de 40 palabras** por bullet.")

    intl_input = st.text_area(
        "Noticias internacionales",
        height=260,
        placeholder="• Fed mantiene tasas sin cambio tras reunión de marzo...\n• El oro alcanza nuevo máximo histórico por encima de US$3,000...\n- Apple reporta ganancias por encima de lo esperado en Q1...",
        key="intl_input",
        label_visibility="collapsed",
    )

    col1, _ = st.columns([1, 4])
    with col1:
        gen_intl = st.button("✨ Generar resumen", key="btn_intl", use_container_width=True)

    if gen_intl:
        if not api_key:
            st.error("⚠️ Ingresa tu Gemini API Key en el panel lateral.")
        elif not intl_input.strip():
            st.warning("Pega al menos una noticia con bullet.")
        else:
            with st.spinner("Generando resúmenes..."):
                try:
                    st.session_state["intl_result"] = call_gemini(api_key, PROMPT_INTL, intl_input)
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.get("intl_result"):
        st.markdown("**Resultado — haz clic, Ctrl+A y Ctrl+C para copiar:**")
        st.text_area(
            "output_intl",
            value=st.session_state["intl_result"],
            height=300,
            key="intl_output_area",
            label_visibility="collapsed",
        )
        st.markdown('<div class="copy-hint">💡 Clic en el cuadro → Ctrl+A → Ctrl+C</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Movers CNBC
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">📊 Movers CNBC</div>', unsafe_allow_html=True)
    st.markdown("Pega el texto de movers **en inglés**. Se traduce y aplica el formato institucional automáticamente.")

    movers_input = st.text_area(
        "Movers CNBC",
        height=260,
        placeholder="Apple (AAPL) shares rose 3.2% after the company reported better-than-expected earnings...\nTesla (TSLA) fell 5,1% following a disappointing delivery report...",
        key="movers_input",
        label_visibility="collapsed",
    )

    col1, _ = st.columns([1, 4])
    with col1:
        gen_movers = st.button("✨ Generar resumen", key="btn_movers", use_container_width=True)

    if gen_movers:
        if not api_key:
            st.error("⚠️ Ingresa tu Gemini API Key en el panel lateral.")
        elif not movers_input.strip():
            st.warning("Pega el texto de movers CNBC.")
        else:
            with st.spinner("Procesando movers CNBC..."):
                try:
                    st.session_state["movers_result"] = call_gemini(api_key, PROMPT_MOVERS, movers_input)
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.get("movers_result"):
        st.markdown("**Vista previa con formato:**")
        st.markdown(st.session_state["movers_result"])
        st.markdown("**Para copiar (texto plano con markdown):**")
        st.text_area(
            "output_movers",
            value=st.session_state["movers_result"],
            height=260,
            key="movers_output_area",
            label_visibility="collapsed",
        )
        st.markdown('<div class="copy-hint">💡 Clic en el cuadro → Ctrl+A → Ctrl+C</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — BMV / BIVA
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">🇲🇽 Noticias BMV / BIVA — Resúmenes Individuales</div>', unsafe_allow_html=True)
    st.markdown("Agrega hasta **10 noticias**. Cada una se resume de forma independiente.")

    if "bmv_count" not in st.session_state:
        st.session_state["bmv_count"] = 3

    col_add, col_rem, _ = st.columns([1.3, 1.3, 5])
    with col_add:
        if st.button("➕ Agregar", key="add_bmv"):
            if st.session_state["bmv_count"] < 10:
                st.session_state["bmv_count"] += 1
    with col_rem:
        if st.button("➖ Quitar", key="rem_bmv"):
            if st.session_state["bmv_count"] > 1:
                st.session_state["bmv_count"] -= 1
                st.session_state.pop(f"bmv_result_{st.session_state['bmv_count']}", None)

    st.markdown("---")

    bmv_texts = []
    for i in range(st.session_state["bmv_count"]):
        st.markdown(f"**Noticia {i+1}**")
        text = st.text_area(
            f"noticia_{i+1}",
            height=110,
            placeholder=f"Pega aquí la noticia {i+1} de BMV/BIVA...",
            key=f"bmv_input_{i}",
            label_visibility="collapsed",
        )
        bmv_texts.append(text)

    st.markdown("---")
    col1, _ = st.columns([1, 4])
    with col1:
        gen_bmv = st.button("✨ Generar resúmenes", key="btn_bmv", use_container_width=True)

    if gen_bmv:
        if not api_key:
            st.error("⚠️ Ingresa tu Gemini API Key en el panel lateral.")
        else:
            filled = [(i, t) for i, t in enumerate(bmv_texts) if t.strip()]
            if not filled:
                st.warning("Pega al menos una noticia.")
            else:
                progress = st.progress(0, text="Procesando noticias...")
                for idx, (i, text) in enumerate(filled):
                    progress.progress((idx + 1) / len(filled), text=f"Resumiendo noticia {i+1} de {len(filled)}...")
                    try:
                        st.session_state[f"bmv_result_{i}"] = call_gemini(api_key, PROMPT_BMV, text)
                    except Exception as e:
                        st.session_state[f"bmv_result_{i}"] = f"❌ Error: {e}"
                progress.empty()
                st.success(f"✅ {len(filled)} resumen(es) generado(s).")

    any_result = any(f"bmv_result_{i}" in st.session_state for i in range(st.session_state["bmv_count"]))
    if any_result:
        st.markdown("### 📋 Resúmenes")
        all_summaries = []
        for i in range(st.session_state["bmv_count"]):
            key = f"bmv_result_{i}"
            if key in st.session_state:
                r = st.session_state[key]
                all_summaries.append(r)
                with st.expander(f"Noticia {i+1}", expanded=True):
                    st.text_area(
                        f"res_{i}",
                        value=r,
                        height=90,
                        key=f"bmv_out_{i}",
                        label_visibility="collapsed",
                    )

        if len(all_summaries) > 1:
            st.markdown("**Todos los resúmenes juntos:**")
            st.text_area(
                "bmv_all",
                value="\n\n".join(all_summaries),
                height=320,
                key="bmv_all_output",
                label_visibility="collapsed",
            )
            st.markdown('<div class="copy-hint">💡 Clic en el cuadro → Ctrl+A → Ctrl+C</div>', unsafe_allow_html=True)
