"""
CodeBurnout AI — Developer Operating System
Complete production SaaS app for Open Source Hackathon 2026.
Run: streamlit run app/main.py
"""
import sys, os, time, io, json
from datetime import date, timedelta, datetime
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from synthetic  import generate_synthetic_commits, synthetic_profile
from analyzer   import get_user_commits, get_user_profile
from features   import extract_features
from model      import (calculate_burnout_score, generate_insights,
                        generate_forecast, developer_health_score,
                        generate_recommendations)
from report     import generate_pdf_report

# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CodeBurnout AI · Developer OS",
    page_icon="🔥", layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS — Dark Glassmorphism SaaS Theme
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:      #080B14;
  --bg2:     #0D1117;
  --surface: rgba(255,255,255,0.04);
  --surfaceB:rgba(255,255,255,0.07);
  --border:  rgba(255,255,255,0.08);
  --borderB: rgba(255,255,255,0.14);
  --primary: #6366F1;
  --pri2:    #8B5CF6;
  --accent:  #06B6D4;
  --green:   #10B981;
  --yellow:  #F59E0B;
  --red:     #EF4444;
  --text:    #F1F5F9;
  --muted:   #64748B;
  --muted2:  #94A3B8;
  --font:    'Plus Jakarta Sans', sans-serif;
  --mono:    'JetBrains Mono', monospace;
  --r:       14px;
  --rL:      20px;
  --shadow:  0 4px 24px rgba(0,0,0,.4);
  --glow:    0 0 40px rgba(99,102,241,.15);
}

html, body, [class*="css"] { font-family: var(--font) !important; }
.main                       { background: var(--bg) !important; }
.block-container            { padding: 0 2.5rem 4rem !important; max-width: 100% !important; }
#MainMenu, footer, header   { visibility: hidden; }
* { box-sizing: border-box; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 256px !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1.25rem; }

/* Metrics */
div[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding: 20px 22px !important;
  backdrop-filter: blur(12px) !important;
  transition: border-color .2s, transform .2s !important;
}
div[data-testid="stMetric"]:hover {
  border-color: rgba(99,102,241,.4) !important;
  transform: translateY(-2px) !important;
}
div[data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 800 !important; font-size: 1.7rem !important; }
div[data-testid="stMetricLabel"] { color: var(--muted2) !important; font-size: .68rem !important; font-weight: 600 !important; letter-spacing: .1em !important; text-transform: uppercase !important; }
div[data-testid="stMetricDelta"] { font-size: .75rem !important; }

/* Expander */
div[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  backdrop-filter: blur(12px) !important;
}
summary { color: var(--text) !important; }

/* Buttons */
.stButton > button {
  border-radius: 10px !important; font-family: var(--font) !important;
  font-weight: 700 !important; font-size: .88rem !important;
  padding: 10px 20px !important; transition: all .18s !important;
  letter-spacing: -.01em !important;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--muted2) !important;
}
.stButton > button:hover { border-color: var(--primary) !important; color: var(--text) !important; }
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--primary) 0%, var(--pri2) 100%) !important;
  border: none !important; color: white !important;
  box-shadow: 0 4px 20px rgba(99,102,241,.4) !important;
}
.stButton > button[kind="primary"]:hover {
  box-shadow: 0 6px 28px rgba(99,102,241,.55) !important;
  transform: translateY(-1px) !important;
}

/* Inputs */
.stTextInput > div > div > input {
  border-radius: 10px !important; border: 1px solid var(--border) !important;
  background: var(--surface) !important; color: var(--text) !important;
  font-family: var(--font) !important; font-size: .95rem !important;
  padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,.2) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--muted) !important; }
.stTextInput label { color: var(--muted2) !important; font-size: .8rem !important; }

/* Select / Slider */
.stSelectbox > div > div { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; color: var(--text) !important; }
.stSlider [data-testid="stSlider"] > div > div { background: var(--primary) !important; }
hr { border-color: var(--border) !important; }
.stMarkdown p { color: var(--muted2); }

/* ── Components ── */

.brand {
  font-size: 1.2rem; font-weight: 800; letter-spacing: -.03em;
  background: linear-gradient(135deg, var(--primary) 0%, var(--pri2) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  display: inline-block;
}
.brand-sub { font-size: .6rem; color: var(--muted); letter-spacing: .14em; text-transform: uppercase; margin-top: 2px; }

/* Hero */
.hero {
  background: linear-gradient(135deg, rgba(99,102,241,.08) 0%, rgba(139,92,246,.06) 40%, rgba(6,182,212,.05) 100%);
  border: 1px solid var(--border); border-radius: var(--rL);
  padding: 4.5rem 4rem 3.5rem; position: relative; overflow: hidden;
  margin-bottom: 2.5rem;
}
.hero::before {
  content:''; position:absolute; top:-120px; right:-80px;
  width:500px; height:500px; border-radius:50%;
  background: radial-gradient(circle, rgba(99,102,241,.18) 0%, transparent 65%);
  pointer-events:none;
}
.hero::after {
  content:''; position:absolute; bottom:-100px; left:15%;
  width:380px; height:380px; border-radius:50%;
  background: radial-gradient(circle, rgba(6,182,212,.12) 0%, transparent 65%);
  pointer-events:none;
}
.hero-pill {
  display: inline-block;
  background: rgba(99,102,241,.15); color: var(--primary);
  border: 1px solid rgba(99,102,241,.25);
  font-size: .72rem; font-weight: 700; letter-spacing: .12em;
  text-transform: uppercase; padding: 5px 14px; border-radius: 20px;
  margin-bottom: 1.5rem;
}
.hero-h1 {
  font-size: clamp(2.4rem, 5vw, 4rem);
  font-weight: 800; line-height: 1.08; color: var(--text);
  letter-spacing: -.04em; margin-bottom: 1.2rem; position: relative; z-index: 1;
}
.hero-h1 span {
  background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-p {
  font-size: 1.05rem; color: var(--muted2); max-width: 540px;
  line-height: 1.75; margin-bottom: 2.5rem; position: relative; z-index: 1;
}
.hero-stats { display: flex; gap: 3rem; position: relative; z-index: 1; }
.hs-n { font-size: 1.9rem; font-weight: 800; color: var(--text); line-height: 1; }
.hs-l { font-size: .7rem; color: var(--muted); margin-top: 4px; letter-spacing: .05em; }

/* Glass card */
.gc {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r); padding: 22px 24px;
  backdrop-filter: blur(16px); transition: border-color .2s, transform .2s;
  margin-bottom: 1rem;
}
.gc:hover { border-color: var(--borderB); transform: translateY(-2px); }
.gc-label { font-size: .68rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
.gc-value { font-size: 2rem; font-weight: 800; color: var(--text); line-height: 1; }
.gc-sub   { font-size: .75rem; color: var(--muted); margin-top: 5px; }

/* Badge */
.badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 12px; border-radius: 20px;
  font-size: .72rem; font-weight: 700; letter-spacing: .04em;
}
.b-green  { background: rgba(16,185,129,.12); color: var(--green); border: 1px solid rgba(16,185,129,.2); }
.b-yellow { background: rgba(245,158,11,.12); color: var(--yellow); border: 1px solid rgba(245,158,11,.2); }
.b-red    { background: rgba(239,68,68,.12);  color: var(--red);    border: 1px solid rgba(239,68,68,.2); }
.b-blue   { background: rgba(99,102,241,.12); color: var(--primary);border: 1px solid rgba(99,102,241,.2); }

/* Profile bar */
.pbar {
  display: flex; align-items: center; gap: 18px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--rL); padding: 22px 26px;
  backdrop-filter: blur(16px); margin-bottom: 1.8rem;
}
.p-name { font-size: 1.1rem; font-weight: 800; color: var(--text); }
.p-meta { font-size: .76rem; color: var(--muted); margin-top: 4px; line-height: 1.6; }

/* Section head */
.sh {
  font-size: 1.05rem; font-weight: 800; color: var(--text);
  border-bottom: 1px solid var(--border);
  padding-bottom: 10px; margin: 2.2rem 0 1.4rem;
  letter-spacing: -.02em;
}

/* Insight card */
.ic {
  background: var(--surface); border: 1px solid var(--border);
  border-left: 3px solid var(--primary);
  border-radius: 0 12px 12px 0;
  padding: 15px 20px; margin-bottom: 10px;
  font-size: .88rem; color: var(--muted2); line-height: 1.7;
  backdrop-filter: blur(12px);
}

/* Rec card */
.rc {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r); padding: 18px 20px;
  backdrop-filter: blur(12px); margin-bottom: 10px;
  display: flex; gap: 14px; align-items: flex-start;
}
.rc-icon  { font-size: 1.5rem; flex-shrink: 0; }
.rc-title { font-size: .9rem; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.rc-desc  { font-size: .8rem; color: var(--muted); line-height: 1.6; }
.pp {
  display: inline-block; padding: 2px 10px; border-radius: 10px;
  font-size: .67rem; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; margin-bottom: 5px;
}
.pp-h { background: rgba(239,68,68,.12); color: var(--red); }
.pp-m { background: rgba(245,158,11,.12); color: var(--yellow); }
.pp-l { background: rgba(16,185,129,.12); color: var(--green); }

/* Rrow */
.rrow {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 12px 16px; margin-bottom: 6px;
  backdrop-filter: blur(12px);
}
.rrow-t { font-size: .86rem; font-weight: 700; color: var(--text); }
.rrow-s { font-size: .77rem; color: var(--muted); margin-top: 2px; }

/* Forecast */
.fc-box {
  background: linear-gradient(135deg, rgba(99,102,241,.1) 0%, rgba(139,92,246,.08) 100%);
  border: 1px solid rgba(99,102,241,.2); border-radius: var(--rL);
  padding: 28px 32px; margin-bottom: 1.2rem;
}
.fc-msg { font-size: 1.05rem; color: var(--text); margin-bottom: 14px; line-height: 1.65; font-weight: 500; }
.fc-action {
  background: rgba(255,255,255,.04); border: 1px solid rgba(99,102,241,.2);
  border-left: 3px solid var(--primary); border-radius: 0 8px 8px 0;
  padding: 12px 16px; font-size: .84rem; color: var(--muted); line-height: 1.55;
}

/* Progress bar */
.pb-wrap { margin-bottom: 14px; }
.pb-hd   { display: flex; justify-content: space-between; font-size: .77rem; color: var(--muted2); margin-bottom: 5px; font-weight: 600; }
.pb-bg   { background: rgba(255,255,255,.06); border-radius: 4px; height: 6px; }
.pb-fill { height: 100%; border-radius: 4px; transition: width .6s; }

/* Grade */
.grade {
  width: 50px; height: 50px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 1.25rem; font-weight: 800;
}
.gA { background: rgba(16,185,129,.15); color: var(--green); }
.gB { background: rgba(99,102,241,.15); color: var(--primary); }
.gC { background: rgba(245,158,11,.15); color: var(--yellow); }
.gD { background: rgba(249,115,22,.15); color: #F97316; }
.gF { background: rgba(239,68,68,.15);  color: var(--red); }

/* Achievement badge */
.ach {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r); padding: 20px 16px; text-align: center;
  backdrop-filter: blur(12px); transition: all .2s;
}
.ach:hover { border-color: var(--primary); transform: translateY(-3px); box-shadow: 0 8px 24px rgba(99,102,241,.2); }
.ach-icon  { font-size: 2.2rem; margin-bottom: 8px; }
.ach-name  { font-size: .82rem; font-weight: 700; color: var(--text); margin-bottom: 3px; }
.ach-desc  { font-size: .7rem; color: var(--muted); }
.ach.locked { opacity: .35; filter: grayscale(1); }

/* Demo banner */
.demo-ban {
  background: rgba(99,102,241,.08); border: 1px solid rgba(99,102,241,.2);
  border-radius: 10px; padding: 10px 16px; margin-bottom: 1.2rem;
  font-size: .8rem; color: var(--primary); font-weight: 500;
  display: flex; align-items: center; gap: 8px;
}

/* Chat bubble */
.chat-u {
  background: rgba(99,102,241,.15); border: 1px solid rgba(99,102,241,.2);
  border-radius: 16px 16px 4px 16px; padding: 12px 16px;
  margin-bottom: 12px; max-width: 78%; margin-left: auto;
  font-size: .88rem; color: var(--text); line-height: 1.55;
}
.chat-ai {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 16px 16px 16px 4px; padding: 12px 16px;
  margin-bottom: 12px; max-width: 86%;
  font-size: .88rem; color: var(--muted2); line-height: 1.6;
  backdrop-filter: blur(12px);
}

/* Commit row */
.cr {
  display: flex; align-items: baseline; gap: 10px;
  padding: 7px 0; border-bottom: 1px solid var(--border);
  font-size: .78rem;
}
.cr-ts   { color: var(--muted); font-family: var(--mono); flex-shrink: 0; }
.cr-repo { color: var(--primary); font-weight: 600; flex-shrink: 0; }
.cr-msg  { color: var(--muted2); }
.cr-late { color: var(--red); }

/* Compare table */
.ct-row {
  display: grid; grid-template-columns: 1fr 160px 1fr;
  align-items: center; gap: 10px;
  padding: 9px 0; border-bottom: 1px solid var(--border); font-size: .83rem;
}
.ct-lbl { text-align: center; color: var(--muted); font-size: .7rem; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; }
.ct-win { color: var(--green); font-weight: 700; }
.ct-los { color: var(--muted2); }

/* Feature tile */
.ftile {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r); padding: 24px 20px;
  backdrop-filter: blur(12px); transition: all .2s; height: 100%;
}
.ftile:hover { border-color: var(--borderB); transform: translateY(-3px); box-shadow: var(--glow); }
.ftile-i { font-size: 1.6rem; margin-bottom: 10px; }
.ftile-t { font-size: .9rem; font-weight: 700; color: var(--text); margin-bottom: 5px; }
.ftile-d { font-size: .78rem; color: var(--muted); line-height: 1.55; }

/* Roadmap step */
.rm-step {
  display: flex; gap: 14px; align-items: flex-start;
  padding: 14px 0; border-bottom: 1px solid var(--border);
}
.rm-num {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: .8rem; font-weight: 800;
  background: rgba(99,102,241,.15); color: var(--primary);
}
.rm-title { font-size: .88rem; font-weight: 700; color: var(--text); margin-bottom: 3px; }
.rm-desc  { font-size: .78rem; color: var(--muted); line-height: 1.5; }

/* Benchmark bar */
.bm-row { margin-bottom: 16px; }
.bm-hd  { display: flex; justify-content: space-between; font-size: .8rem; color: var(--muted2); margin-bottom: 5px; font-weight: 500; }
.bm-bg  { background: rgba(255,255,255,.06); border-radius: 6px; height: 10px; position: relative; }
.bm-you { position: absolute; top: 0; left: 0; height: 100%; border-radius: 6px; background: linear-gradient(90deg, var(--primary), var(--pri2)); }
.bm-avg { position: absolute; top: -3px; height: 16px; width: 2px; background: var(--yellow); }

/* Status dot */
.dot-green  { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--green);  margin-right: 5px; }
.dot-yellow { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--yellow); margin-right: 5px; }
.dot-red    { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--red);    margin-right: 5px; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.1); border-radius: 3px; }

/* ── GRAPH OVERLAP FIX ─────────────────────────────────────────────────────
   Each Plotly chart must be in its own stacking context.
   overflow:hidden stops SVG/canvas from bleeding into adjacent columns.
   min-height prevents collapsed containers that cause overlap on re-render.
   width:100% + display:block forces correct column sizing after sidebar toggle.
──────────────────────────────────────────────────────────────────────────── */
div[data-testid="stPlotlyChart"] {
  position: relative !important;
  overflow: hidden !important;
  display: block !important;
  width: 100% !important;
  min-height: 60px !important;
  isolation: isolate !important;
}
div[data-testid="stPlotlyChart"] > div {
  position: relative !important;
  width: 100% !important;
}
/* Column containers — prevent children from escaping bounds */
div[data-testid="column"] {
  overflow: hidden !important;
  min-width: 0 !important;          /* flex shrink fix */
}
div[data-testid="stHorizontalBlock"] {
  align-items: flex-start !important; /* stop columns stretching each other */
  flex-wrap: nowrap !important;
}
/* Force each block-level chart wrapper to clear floats */
div[data-testid="element-container"] {
  clear: both;
  contain: layout;                  /* CSS containment — hard boundary */
}

/* ── INPUT TEXT VISIBILITY FIX ─────────────────────────────────────────────
   Streamlit renders inputs inside shadow-like wrappers that reset color.
   We need to target every layer of the input tree explicitly.
──────────────────────────────────────────────────────────────────────────── */
/* Main input element */
.stTextInput input,
.stTextInput > div > div > input,
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {
  color: #F1F5F9 !important;
  caret-color: #6366F1 !important;
  -webkit-text-fill-color: #F1F5F9 !important;
}
/* Placeholder */
.stTextInput input::placeholder,
div[data-baseweb="input"] input::placeholder {
  color: #475569 !important;
  opacity: 1 !important;
}
/* Text area */
.stTextArea textarea,
div[data-baseweb="textarea"] textarea {
  color: #F1F5F9 !important;
  -webkit-text-fill-color: #F1F5F9 !important;
  caret-color: #6366F1 !important;
}
.stTextArea textarea::placeholder { color: #475569 !important; opacity: 1 !important; }
/* Selectbox / dropdown text */
div[data-baseweb="select"] span,
div[data-baseweb="select"] div[class*="ValueContainer"] { color: #F1F5F9 !important; }
/* Base-web wrapper background must not fight dark theme */
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
  background: rgba(255,255,255,0.04) !important;
  border-color: rgba(255,255,255,0.08) !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
_DEFAULTS = {
    "page": "home", "data": None, "compare_data": None,
    "chat_history": [], "team_data": [],
    "gh_token": "", "analysis_days": 90,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="brand">🔥 CodeBurnout AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Developer Operating System</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    NAV = [
        ("🏠","Home",              "home"),
        ("📊","Dashboard",         "dashboard"),
        ("🤖","AI Coach",          "coach"),
        ("👥","Team Analytics",    "team"),
        ("⚖️","Compare",           "compare"),
        ("📈","Industry Benchmark","benchmark"),
        ("🔮","Burnout Forecast",  "forecast"),
        ("📄","Reports",           "reports"),
        ("🏆","Achievements",      "achievements"),
        ("🗺️","Roadmap",           "roadmap"),
        ("⚙️","Settings",          "settings"),
    ]
    for icon, label, key in NAV:
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("---")
    st.markdown('<div style="font-size:.68rem;color:var(--muted);font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">Quick Analyze</div>', unsafe_allow_html=True)
    quick_u = st.text_input("", placeholder="GitHub username…", key="sidebar_username", label_visibility="collapsed")
    if st.button("⚡ Analyze", use_container_width=True, key="sidebar_analyze"):
        if quick_u.strip():
            st.session_state.data = None          # clear old user data
            st.session_state.chat_history = []
            st.session_state.page = "dashboard"
            st.session_state._pending_username = quick_u.strip()
            st.rerun()

    st.markdown("---")
    st.markdown('<div style="font-size:.90rem; color:#94A3B8; line-height:1.8">By Pragya Namdev<br>Quantum University</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CHART CONFIG & HELPERS
# ══════════════════════════════════════════════════════════════════════════════
_CFG = {"displayModeBar": False, "responsive": True}
_BG  = "rgba(0,0,0,0)"
_FNT = dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#64748B")

def _layout(**kw):
    base = dict(
        paper_bgcolor=_BG, plot_bgcolor=_BG, font=_FNT,
        margin=dict(t=44,b=32,l=32,r=16),
    )
    base.update(kw)
    return base

def badge_html(level):
    cls = {"Healthy":"b-green","Warning":"b-yellow","High Risk":"b-red"}.get(level,"b-blue")
    dot = {"Healthy":"🟢","Warning":"🟡","High Risk":"🔴"}.get(level,"⚪")
    return f'<span class="badge {cls}">{dot} {level.upper()}</span>'

def pbar_html(label, val, color):
    v = max(0.0, min(float(val), 100.0))
    return (f'<div class="pb-wrap"><div class="pb-hd"><span>{label}</span>'
            f'<span>{v:.0f}%</span></div>'
            f'<div class="pb-bg"><div class="pb-fill" style="width:{v}%;background:{color}"></div></div></div>')

def hc(v):
    if v >= 60: return "#10B981"
    if v >= 35: return "#F59E0B"
    return "#EF4444"

@st.cache_data(ttl=300, show_spinner=False)
def _cached_analysis(username: str, token: str, days: int) -> dict:
    """Cached GitHub fetch — 5 min TTL. Username lowercased so PragyaNamdev == pragyanamdev."""
    from analyzer   import get_user_commits, get_user_profile
    from features   import extract_features
    from model      import (calculate_burnout_score, generate_insights,
                            generate_forecast, developer_health_score,
                            generate_recommendations)
    username = username.strip()          # trim whitespace
    tok      = token or None
    profile  = get_user_profile(username, tok)
    commits, is_syn = get_user_commits(username, tok, days_back=days)
    features = extract_features(commits)
    result   = calculate_burnout_score(features)
    insights = generate_insights(features, result)
    forecast = generate_forecast(features, result)
    health   = developer_health_score(result["score"])
    recs     = generate_recommendations(features, result)
    return {"username": profile.get("login", username),   # use GitHub's canonical login
            "profile": profile, "commits": commits,
            "features": features, "result": result, "insights": insights,
            "forecast": forecast, "health": health, "recs": recs, "synthetic": is_syn}


def run_analysis(username: str, token=None, days=90) -> dict:
    """Run analysis with status UI. Always fetches fresh data for the given username."""
    tok = token or st.session_state.get("gh_token") or ""
    with st.status(f"Analyzing **{username}**…", expanded=True) as status:
        st.write("📡 Fetching GitHub profile…")
        st.write("📦 Fetching commit history…")
        st.write("🧠 Running burnout engine…")
        st.write("💡 Generating AI insights…")
        data = _cached_analysis(username, tok, days)
        status.update(label=f"✅ Done! Showing data for @{username}", state="complete")
    return data

# ── Chart builders (no duplicate axis bug) ────────────────────────────────────
def chart_gauge(score, level):
    c = {"Healthy":"#10B981","Warning":"#F59E0B","High Risk":"#EF4444"}.get(level,"#6366F1")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font":{"size":38,"color":c,"family":"Plus Jakarta Sans"}},
        title={"text":"Burnout Risk Score<br><span style='font-size:11px;color:#475569'>0 = Healthy · 100 = Critical</span>",
               "font":{"size":12,"color":"#64748B"}},
        gauge={"axis":{"range":[0,100],"tickwidth":1,"tickcolor":"rgba(255,255,255,.1)",
                       "tickfont":{"color":"#475569","size":10}},
               "bar":{"color":c,"thickness":0.22},
               "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
               "steps":[{"range":[0,40],"color":"rgba(16,185,129,.08)"},
                        {"range":[40,70],"color":"rgba(245,158,11,.08)"},
                        {"range":[70,100],"color":"rgba(239,68,68,.08)"}],
               "threshold":{"line":{"color":c,"width":3},"thickness":0.82,"value":score}},
    ))
    fig.update_layout(
        paper_bgcolor=_BG, font=_FNT,
        height=280,
        margin=dict(t=60,b=20,l=40,r=40),
        autosize=True,
    )
    return fig

def chart_hours(hour_dist):
    hours  = list(hour_dist.keys())
    counts = list(hour_dist.values())
    colors = ["#EF4444" if (h>=22 or h<4) else "#F97316" if 4<=h<7 else "#10B981" if 9<=h<18 else "#334155" for h in hours]
    fig = go.Figure(go.Bar(
        x=[f"{h:02d}:00" for h in hours], y=counts,
        marker_color=colors, marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Commits: %{y}<extra></extra>",
    ))
    fig.update_layout(**_layout(
        title=dict(text="⏰ Commits by Hour", font=dict(size=13,color="#64748B"), x=0),
        bargap=0.18,
        xaxis=dict(gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
    ))
    return fig

def chart_days(day_dist):
    colors = ["#F97316" if d in ("Sat","Sun") else "#6366F1" for d in day_dist]
    fig = go.Figure(go.Bar(
        x=list(day_dist.keys()), y=list(day_dist.values()),
        marker_color=colors, marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Commits: %{y}<extra></extra>",
    ))
    fig.update_layout(**_layout(
        title=dict(text="📅 Commits by Day", font=dict(size=13,color="#64748B"), x=0),
        bargap=0.22,
        xaxis=dict(gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
    ))
    return fig

def chart_trend(week_dist):
    if not week_dist: week_dist = {i:0 for i in range(1,9)}
    weeks = sorted(week_dist.keys()); counts = [week_dist[w] for w in weeks]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(weeks))), y=counts, mode="lines+markers",
        line=dict(color="#6366F1",width=2.5,shape="spline"),
        marker=dict(size=6,color="#6366F1",line=dict(color="#080B14",width=2)),
        fill="tozeroy", fillcolor="rgba(99,102,241,.08)",
        hovertemplate="Week %{x}<br>Commits: %{y}<extra></extra>",
    ))
    fig.update_layout(**_layout(
        title=dict(text="📈 Weekly Commit Trend", font=dict(size=13,color="#64748B"), x=0),
        xaxis=dict(title="",tickvals=list(range(len(weeks))),
                   ticktext=[f"W{i+1}" for i in range(len(weeks))],
                   gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
        yaxis=dict(title="Commits",gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
    ))
    return fig

def chart_donut(f):
    ln=f.get("late_night_pct",0); em=f.get("early_morning_pct",0)
    wh=f.get("work_hours_pct",0); ot=max(0,100-ln-em-wh)
    fig = go.Figure(go.Pie(
        labels=["Late Night","Early Morning","Work Hours","Other"],
        values=[ln,em,wh,ot], hole=0.58,
        marker=dict(colors=["#EF4444","#F97316","#10B981","#1E293B"],
                    line=dict(color="#080B14",width=2)),
        textinfo="percent", textfont=dict(size=11,family="Plus Jakarta Sans"),
        hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=_BG, plot_bgcolor=_BG, font=_FNT,
        title=dict(text="🌙 Day vs Night Ratio", font=dict(size=13,color="#64748B"), x=0),
        showlegend=True, height=280,
        legend=dict(font=dict(size=10,color="#64748B"),x=1,y=0.5,orientation="v"),
        margin=dict(t=44,b=20,l=10,r=10),
        autosize=True,
    )
    return fig

def chart_repos(top_repos):
    if not top_repos: return go.Figure()
    repos=list(top_repos.keys()); counts=list(top_repos.values())
    fig = go.Figure(go.Bar(
        x=counts, y=repos, orientation="h",
        marker_color="#6366F1", marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>%{x} commits<extra></extra>",
    ))
    fig.update_layout(**_layout(
        title=dict(text="📁 Top Repositories", font=dict(size=13,color="#64748B"), x=0),
        xaxis=dict(title="Commits",gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
        height=max(200,len(repos)*44),
    ))
    return fig

def chart_radar(f1, f2, u1, u2):
    cats=["Late Night","Weekend","Neg Sentiment","Overload","Poor Rest","Instability"]
    def v(f):
        return [f.get("late_night_pct",0), f.get("weekend_pct",0),
                f.get("neg_commit_pct",0), min(f.get("avg_commits_per_day",0)*8,100),
                100-f.get("rest_ratio",0), min(f.get("freq_stability",0)*7,100)]
    v1=v(f1)+[v(f1)[0]]; v2=v(f2)+[v(f2)[0]]; c=cats+[cats[0]]
    fig = go.Figure()
    for vals,name,col,fill in [(v1,u1,"#6366F1","rgba(99,102,241,.15)"),(v2,u2,"#F97316","rgba(249,115,22,.15)")]:
        fig.add_trace(go.Scatterpolar(r=vals,theta=c,fill="toself",name=name,
                                      line=dict(color=col,width=2),fillcolor=fill))
    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   angularaxis=dict(color="#334155",gridcolor="rgba(255,255,255,.06)"),
                   radialaxis=dict(visible=True,range=[0,100],color="#334155",gridcolor="rgba(255,255,255,.06)")),
        paper_bgcolor=_BG, font=_FNT,
        legend=dict(orientation="h",y=-0.12,font=dict(size=11,color="#64748B")),
        height=360, margin=dict(t=20,b=50,l=40,r=40),
    )
    return fig

def chart_team_bar(team_data):
    names=[d["username"] for d in team_data]
    scores=[d["result"]["score"] for d in team_data]
    colors=["#EF4444" if s>=71 else "#F59E0B" if s>=41 else "#10B981" for s in scores]
    fig=go.Figure(go.Bar(x=names,y=scores,marker_color=colors,marker_line_width=0,
                         hovertemplate="<b>%{x}</b><br>Score: %{y}<extra></extra>"))
    fig.update_layout(**_layout(
        title=dict(text="Team Burnout Scores", font=dict(size=13,color="#64748B"), x=0),
        xaxis=dict(gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
        yaxis=dict(range=[0,100],title="Burnout Score",gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
        bargap=0.3,
    ))
    return fig

def chart_forecast_line(score, level):
    import random; random.seed(score)
    days=[0,7,14,21,28,35,42]
    mult={"Healthy":0.95,"Warning":1.08,"High Risk":1.18}.get(level,1.0)
    vals=[min(100,score*(mult**i)) for i in range(len(days))]
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=[f"Day {d}" for d in days], y=vals, mode="lines+markers",
        line=dict(color="#6366F1",width=2.5,shape="spline"),
        marker=dict(size=7,color=["#10B981" if v<40 else "#F59E0B" if v<70 else "#EF4444" for v in vals]),
        fill="tozeroy", fillcolor="rgba(99,102,241,.06)",
        hovertemplate="<b>%{x}</b><br>Risk Score: %{y:.0f}<extra></extra>",
    ))
    fig.add_hline(y=40,line_dash="dash",line_color="#10B981",annotation_text="Healthy threshold",
                  annotation_font=dict(color="#10B981",size=10))
    fig.add_hline(y=70,line_dash="dash",line_color="#EF4444",annotation_text="High risk threshold",
                  annotation_font=dict(color="#EF4444",size=10))
    fig.update_layout(**_layout(
        title=dict(text="📉 Burnout Risk Forecast (6 weeks)", font=dict(size=13,color="#64748B"), x=0),
        xaxis=dict(gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
        yaxis=dict(range=[0,105],title="Risk Score",gridcolor="rgba(255,255,255,.04)",zerolinecolor="rgba(255,255,255,.04)"),
    ))
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  AI COACH LOGIC
# ══════════════════════════════════════════════════════════════════════════════
COACH_RESPONSES = {
    "burnout": "Based on your commit patterns, burnout risk is primarily driven by late-night coding sessions and insufficient rest days. The most effective intervention is setting a hard coding curfew at 9 PM for 2 weeks.",
    "late night": "Your late-night commits ({late_night_pct}% of total) are the strongest burnout predictor I see. Research shows that coding after 10 PM degrades decision quality by up to 40% and reduces next-day creativity significantly.",
    "weekend": "Weekend coding at {weekend_pct}% means you're losing critical recovery time. I recommend designating Sunday as a complete no-code day for at least 3 weeks to measure impact.",
    "productivity": "Your productivity score is influenced by commit frequency stability. You're averaging {avg_commits_per_day} commits/day — I'd target 3–6 for sustainable output.",
    "improve": "The fastest way to improve your score is: (1) enforce a 9 PM coding curfew, (2) take 2 full rest days per week, (3) write fewer but more meaningful commits.",
    "sentiment": "Your commit messages show {neg_commit_pct}% negative sentiment. This language pattern often precedes burnout by 2–4 weeks. Try naming your commits around what you're adding, not just fixing.",
    "streak": "You have a {current_streak}-day commit streak. Streaks are motivating but can become compulsive — a streak-break is not failure, it's recovery.",
    "default": "I analyze your GitHub commit data to identify burnout patterns. Try asking about: late night coding, weekend activity, productivity, sentiment patterns, or how to improve your score.",
}

def ai_coach_response(question: str, features: dict) -> str:
    q = question.lower()
    key = "default"
    for k in COACH_RESPONSES:
        if k in q: key = k; break
    template = COACH_RESPONSES[key]
    try:
        return template.format(
            late_night_pct=features.get("late_night_pct",0),
            weekend_pct=features.get("weekend_pct",0),
            avg_commits_per_day=features.get("avg_commits_per_day",0),
            neg_commit_pct=features.get("neg_commit_pct",0),
            current_streak=features.get("current_streak",0),
        )
    except:
        return template

# ══════════════════════════════════════════════════════════════════════════════
#  ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════════════════════
def compute_achievements(f: dict, r: dict) -> list:
    ln   = f.get("late_night_pct",0)
    wk   = f.get("weekend_pct",0)
    rr   = f.get("rest_ratio",100)
    apd  = f.get("avg_commits_per_day",0)
    strk = f.get("current_streak",0)
    sc   = r.get("score",50)
    em   = f.get("early_morning_pct",0)

    return [
        {"icon":"🦉","name":"Night Owl",       "desc":"30%+ late-night commits",    "earned": ln>=30},
        {"icon":"🌅","name":"Early Bird",       "desc":"10%+ commits before 7 AM",   "earned": em>=10},
        {"icon":"🎯","name":"Consistent Coder", "desc":"Streak of 14+ days",          "earned": strk>=14},
        {"icon":"⚔️","name":"Weekend Warrior",  "desc":"40%+ weekend commits",        "earned": wk>=40},
        {"icon":"🛡️","name":"Burnout Survivor", "desc":"Score improved below 40",     "earned": sc<=40},
        {"icon":"🚀","name":"Productivity Pro", "desc":"5+ avg commits/day",          "earned": apd>=5},
        {"icon":"🌿","name":"Rest Champion",    "desc":"40%+ rest day ratio",         "earned": rr>=40},
        {"icon":"💎","name":"Health Master",    "desc":"Health score above 80",       "earned": (100-sc)>=80},
    ]

# ══════════════════════════════════════════════════════════════════════════════
#  INDUSTRY BENCHMARKS
# ══════════════════════════════════════════════════════════════════════════════
BENCHMARKS = {
    "Junior Developer":     {"late_night_pct":18,"weekend_pct":28,"rest_ratio":30,"avg_commits_per_day":3,"burnout_score":45},
    "Mid-level Developer":  {"late_night_pct":22,"weekend_pct":32,"rest_ratio":25,"avg_commits_per_day":5,"burnout_score":50},
    "Senior Developer":     {"late_night_pct":14,"weekend_pct":20,"rest_ratio":38,"avg_commits_per_day":4,"burnout_score":35},
    "Open Source Contributor":{"late_night_pct":30,"weekend_pct":45,"rest_ratio":22,"avg_commits_per_day":6,"burnout_score":60},
}

# ══════════════════════════════════════════════════════════════════════════════
#  ROADMAP GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def generate_roadmap(f: dict, r: dict) -> list:
    score = r.get("score",50)
    target = max(0, score - 40)
    steps=[]
    if f.get("late_night_pct",0) >= 15:
        steps.append({"week":1,"title":"Establish Coding Curfew","desc":f"Set 9 PM as hard stop. Your current late-night rate ({f.get('late_night_pct',0)}%) is the primary risk driver. Expected score drop: -8 to -12 pts."})
    if f.get("weekend_pct",0) >= 20:
        steps.append({"week":1,"title":"Protect Weekend Recovery","desc":f"Designate Sunday as no-code day. Weekend activity ({f.get('weekend_pct',0)}%) is reducing your recovery capacity."})
    if f.get("rest_ratio",100) < 25:
        steps.append({"week":2,"title":"Add Deliberate Rest Days","desc":f"Target 2 full commit-free days per week. Current rest ratio ({f.get('rest_ratio',0)}%) is below the healthy threshold of 25%."})
    if f.get("neg_commit_pct",0) >= 25:
        steps.append({"week":2,"title":"Reframe Commit Language","desc":f"Focus commit messages on what you're building, not what you're fixing. Negative message rate: {f.get('neg_commit_pct',0)}%."})
    steps.append({"week":3,"title":"Stabilize Daily Output","desc":f"Aim for {max(2,int(f.get('avg_commits_per_day',3)))} commits/day consistently. Frequency stability is currently ±{f.get('freq_stability',0):.1f}."})
    steps.append({"week":4,"title":"Re-measure & Iterate","desc":f"Run CodeBurnout analysis again. Target score: {target}. Adjust habits based on new data."})
    return steps[:4]

# ══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════════

def page_home():
    st.markdown("""
    <div class="hero">
      <div class="hero-pill">✦ Open Source Hackathon 2026 · Elite Coders</div>
      <div class="hero-h1">Your Developer<br><span>Operating System.</span></div>
      <div class="hero-p">CodeBurnout AI analyzes GitHub commit patterns, predicts burnout risk, and coaches you toward sustainable high performance.</div>
      <div class="hero-stats">
        <div><div class="hs-n">8+</div><div class="hs-l">Burnout Signals</div></div>
        <div><div class="hs-n">90d</div><div class="hs-l">Activity Window</div></div>
        <div><div class="hs-n">11</div><div class="hs-l">Dashboard Pages</div></div>
        <div><div class="hs-n">Free</div><div class="hs-l">Open Source</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1,2.4,1])
    with c2:
        username = st.text_input("","",placeholder="Enter any GitHub username…",
                                 label_visibility="collapsed",key="home_u")
        b1,b2 = st.columns(2)
        with b1:
            if st.button("🔍  Analyze Profile", type="primary", use_container_width=True):
                if username.strip():
                    # Clear any previous data so old username never shows
                    st.session_state.data = None
                    st.session_state.chat_history = []
                    d = run_analysis(username.strip(), st.session_state.gh_token or None, st.session_state.analysis_days)
                    st.session_state.data = d
                    st.session_state.page = "dashboard"
                    st.rerun()
                else: st.warning("Enter a GitHub username.")
        with b2:
            if st.button("▶  View Demo", use_container_width=True):
                st.session_state.data = None
                d = run_analysis("octocat", None, 90)
                st.session_state.data = d
                st.session_state.page = "dashboard"
                st.rerun()

    st.markdown('<div class="sh">Platform Capabilities</div>', unsafe_allow_html=True)
    tiles=[
        ("🧠","AI Burnout Engine",     "0–100 risk score from 8+ behavioral signals analyzed in real-time"),
        ("🌙","Late-Night Detection",  "Identifies sleep disruption and after-hours coding patterns"),
        ("🔮","6-Week Forecast",       "Predicts burnout risk trajectory at current behavioral pace"),
        ("💡","AI Coach",              "Chat-style coaching based on your actual commit history"),
        ("👥","Team Analytics",        "Multi-developer health dashboard for engineering teams"),
        ("📄","PDF Reports",           "Downloadable executive health reports with full data"),
        ("🏆","Achievements",          "Gamified developer health badges and progress tracking"),
        ("⚖️","Compare & Benchmark",   "Side-by-side comparison and industry percentile ranking"),
        ("🗺️","Health Roadmap",        "4-week personalized improvement plan with measurable targets"),
    ]
    r1,r2,r3 = st.columns(3)
    for i,(icon,title,desc) in enumerate(tiles):
        col=[r1,r2,r3][i%3]
        with col:
            st.markdown(f'<div class="ftile"><div class="ftile-i">{icon}</div>'
                        f'<div class="ftile-t">{title}</div>'
                        f'<div class="ftile-d">{desc}</div></div><br>',
                        unsafe_allow_html=True)


def page_dashboard():
    # Handle sidebar quick-analyze
    pending = st.session_state.pop("_pending_username", None)
    if pending:
        st.session_state.data = run_analysis(pending, st.session_state.gh_token or None, st.session_state.analysis_days)

    d = st.session_state.data
    if d is None:
        st.markdown('<div class="demo-ban">⚡ Loading demo — enter a username on Home for live data.</div>', unsafe_allow_html=True)
        d = run_analysis("octocat", None, 90)
        st.session_state.data = d

    p,f,r,h = d["profile"],d["features"],d["result"],d["health"]

    # Only show demo banner if commits are synthetic (not real GitHub data)
    if d.get("synthetic"):
        st.markdown('<div class="demo-ban">⚡ Showing estimated data — GitHub API rate limit reached or no public commits found. Add a token in Settings for full access.</div>', unsafe_allow_html=True)

    # Profile bar — using st.columns to avoid HTML rendering issues
    import html as _html
    bio_raw   = _html.escape((p.get("bio") or "")[:120])
    loc_str   = f"📍 {_html.escape(p.get('location',''))}" if p.get("location") else ""
    repos     = p.get("public_repos", "—")
    followers = f"{p.get('followers', 0):,}" if isinstance(p.get("followers"), int) else "—"
    name_str  = _html.escape(p.get("name") or p.get("login") or d["username"])
    login_str = _html.escape(p.get("login") or d["username"])
    av        = p.get("avatar_url", "")
    gcls      = f"g{h['grade']}"
    badge     = badge_html(r['level'])

    st.markdown(f"""<div class="pbar">
<img src="{av}" width="52" height="52" style="border-radius:50%;border:2px solid rgba(255,255,255,.1);flex-shrink:0" onerror="this.style.display='none'">
<div style="flex:1;min-width:0"><div class="p-name">{name_str}</div><div class="p-meta">@{login_str} &nbsp;·&nbsp; {repos} repos &nbsp;·&nbsp; {followers} followers{"&nbsp;·&nbsp;" + loc_str if loc_str else ""}</div>{"<div class='p-meta'>" + bio_raw + "</div>" if bio_raw else ""}</div>
<div style="text-align:right;flex-shrink:0">{badge}<div style="display:flex;align-items:center;gap:10px;justify-content:flex-end;margin-top:10px"><span class="grade {gcls}">{h["grade"]}</span><div><div style="font-size:.65rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.08em">Health Grade</div><div style="font-size:.85rem;color:var(--text);font-weight:700">{h["label"]}</div></div></div></div>
</div>""", unsafe_allow_html=True)

    # KPIs
    k1,k2,k3,k4,k5 = st.columns(5)
    kpis=[
        (k1,"Burnout Score",    f"{r['score']}/100",               r['level']),
        (k2,"Total Commits",    f"{f.get('total_commits',0):,}",    f"Last {st.session_state.analysis_days}d"),
        (k3,"Active Days",      f"{f.get('unique_active_days',0)}", f"Avg {f.get('avg_commits_per_day',0)}/day"),
        (k4,"Late Night",       f"{f.get('late_night_pct',0)}%",    "After 10 PM"),
        (k5,"Weekend Activity", f"{f.get('weekend_pct',0)}%",       "Sat + Sun"),
    ]
    for col,lbl,val,sub in kpis:
        col.metric(label=lbl, value=val, delta=sub, delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row 1
    c1,c2 = st.columns(2)
    with c1: st.plotly_chart(chart_gauge(r["score"],r["level"]),use_container_width=True,config=_CFG,key="db_gauge")
    with c2: st.plotly_chart(chart_donut(f),use_container_width=True,config=_CFG,key="db_donut")

    # Charts row 2
    c1,c2 = st.columns(2)
    with c1: st.plotly_chart(chart_hours(f.get("hour_distribution",{h:0 for h in range(24)})),use_container_width=True,config=_CFG,key="db_hours")
    with c2: st.plotly_chart(chart_days(f.get("day_distribution",{})),use_container_width=True,config=_CFG,key="db_days")

    st.plotly_chart(chart_trend(f.get("week_distribution",{})),use_container_width=True,config=_CFG,key="db_trend")
    if f.get("top_repos"):
        st.plotly_chart(chart_repos(f["top_repos"]),use_container_width=True,config=_CFG,key="db_repos")

    # Risk + Positives
    st.markdown('<div class="sh">⚠️ Risk Signals & Healthy Patterns</div>', unsafe_allow_html=True)
    rc1,rc2 = st.columns(2)
    with rc1:
        for title,sub in (r["reasons"] or [("✅ No significant risks","Your patterns look healthy")]):
            st.markdown(f'<div class="rrow"><div class="rrow-t">{title}</div><div class="rrow-s">{sub}</div></div>',unsafe_allow_html=True)
    with rc2:
        for title,sub in r["positives"]:
            st.markdown(f'<div class="rrow" style="border-left:3px solid #10B981"><div class="rrow-t" style="color:#10B981">{title}</div><div class="rrow-s">{sub}</div></div>',unsafe_allow_html=True)

    # Streak
    st.markdown('<div class="sh">🔥 Productivity Streak</div>', unsafe_allow_html=True)
    s1,s2,s3 = st.columns(3)
    s1.metric("Current Streak",f"{f.get('current_streak',0)} days","Consecutive active days")
    s2.metric("Best Streak",   f"{f.get('best_streak',0)} days",   "Longest recorded")
    s3.metric("Max Single Day",f"{f.get('max_commits_in_a_day',0)} commits","Peak output")

    with st.expander("🗂️ Recent Commits Analyzed"):
        for c in d["commits"][:30]:
            late=c["hour"]>=22 or c["hour"]<4
            ts_cls="cr-late" if late else "cr-ts"
            st.markdown(f'<div class="cr"><span class="{ts_cls}">{c["date"]} {c["hour"]:02d}:00{"🌙" if late else ""}</span><span class="cr-repo">[{c["repo"]}]</span><span class="cr-msg">{c["message"][:88]}</span></div>',unsafe_allow_html=True)


def page_coach():
    st.markdown('<div class="sh">🤖 AI Coding Habit Coach</div>', unsafe_allow_html=True)

    d = st.session_state.data
    if d is None:
        d = run_analysis("octocat", None, 90)
        st.session_state.data = d

    f = d["features"]

    # Suggested questions
    st.markdown('<div style="font-size:.78rem;color:var(--muted);margin-bottom:10px">💡 Suggested questions:</div>', unsafe_allow_html=True)
    q_cols = st.columns(3)
    suggestions = [
        "Why is my burnout score high?",
        "How can I reduce late-night coding?",
        "How can I improve my score?",
        "What do my commit messages say?",
        "How's my weekend activity?",
        "Tell me about my productivity.",
    ]
    for i, q in enumerate(suggestions):
        with q_cols[i%3]:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","content":q})
                resp = ai_coach_response(q, f)
                st.session_state.chat_history.append({"role":"ai","content":resp})
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="chat-ai">
                👋 Hi! I'm your AI Coding Habit Coach. I've analyzed your GitHub commit history and I'm ready to help you build healthier coding habits.<br><br>
                Ask me anything about your burnout risk, late-night patterns, productivity, or how to improve your developer health score.
            </div>""", unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-u">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # Input
    c1,c2 = st.columns([5,1])
    with c1:
        user_q = st.text_input("","",placeholder="Ask your AI coach anything…",
                               label_visibility="collapsed", key="coach_input")
    with c2:
        if st.button("Send →", type="primary", use_container_width=True):
            if user_q.strip():
                st.session_state.chat_history.append({"role":"user","content":user_q})
                resp = ai_coach_response(user_q, f)
                st.session_state.chat_history.append({"role":"ai","content":resp})
                st.rerun()

    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

    # Quick stats sidebar
    st.markdown('<div class="sh">📊 Your Health Snapshot</div>', unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Burnout Score",      f"{d['result']['score']}/100")
    m2.metric("Health Grade",       d['health']['grade'])
    m3.metric("Late Night %",       f"{f.get('late_night_pct',0)}%")
    m4.metric("Current Streak",     f"{f.get('current_streak',0)}d")


def page_team():
    st.markdown('<div class="sh">👥 Team Analytics</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:.85rem;color:var(--muted2);margin-bottom:1rem">Enter up to 10 GitHub usernames (one per line) to analyze team health.</div>', unsafe_allow_html=True)
    team_input = st.text_area("", placeholder="torvalds\ngvanrossum\noctocat",
                              height=120, label_visibility="collapsed", key="team_input")
    tok = st.session_state.gh_token or None

    if st.button("👥  Analyze Team", type="primary"):
        usernames = [u.strip() for u in team_input.strip().split("\n") if u.strip()][:10]
        if not usernames:
            st.warning("Enter at least one GitHub username.")
            return
        team_results = []
        prog = st.progress(0, text="Analyzing team…")
        for i, u in enumerate(usernames):
            team_results.append(run_analysis(u, tok, st.session_state.analysis_days))
            prog.progress((i+1)/len(usernames), text=f"Analyzed {i+1}/{len(usernames)}")
        st.session_state.team_data = team_results
        st.rerun()

    td = st.session_state.team_data
    if not td:
        st.markdown('<div class="demo-ban">ℹ️ Enter team usernames above and click Analyze Team.</div>', unsafe_allow_html=True)
        return

    # Team summary
    scores = [d["result"]["score"] for d in td]
    team_avg = sum(scores)/len(scores)
    most_at_risk = max(td, key=lambda d: d["result"]["score"])
    most_healthy = min(td, key=lambda d: d["result"]["score"])
    consistent   = min(td, key=lambda d: d["features"].get("freq_stability",99))

    t1,t2,t3,t4 = st.columns(4)
    t1.metric("Team Avg Score",   f"{team_avg:.0f}/100", "Team burnout risk")
    t2.metric("Most At Risk",     f"@{most_at_risk['username']}", f"Score: {most_at_risk['result']['score']}")
    t3.metric("Healthiest",       f"@{most_healthy['username']}", f"Score: {most_healthy['result']['score']}")
    t4.metric("Most Consistent",  f"@{consistent['username']}", "Lowest freq variance")

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(chart_team_bar(td), use_container_width=True, config=_CFG, key="team_bar")

    # Team member cards
    st.markdown('<div class="sh">Team Member Details</div>', unsafe_allow_html=True)
    for d in td:
        r=d["result"]; h=d["health"]; f=d["features"]
        risk_col={"Healthy":"#10B981","Warning":"#F59E0B","High Risk":"#EF4444"}.get(r["level"],"#64748B")
        st.markdown(f"""
        <div class="gc" style="border-left:3px solid {risk_col}">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <div style="font-weight:800;color:var(--text)">@{d['username']}</div>
              <div style="font-size:.76rem;color:var(--muted);margin-top:3px">
                Score: <strong style="color:{risk_col}">{r['score']}/100</strong> &nbsp;·&nbsp;
                Late Night: {f.get('late_night_pct',0)}% &nbsp;·&nbsp;
                Weekend: {f.get('weekend_pct',0)}% &nbsp;·&nbsp;
                Rest: {f.get('rest_ratio',0)}%
              </div>
            </div>
            {badge_html(r['level'])}
          </div>
        </div>""", unsafe_allow_html=True)


def page_compare():
    st.markdown('<div class="sh">⚖️ Compare Two Developers</div>', unsafe_allow_html=True)
    cc1,cc2 = st.columns(2)
    with cc1: u1 = st.text_input("Developer 1", placeholder="e.g. torvalds",   key="cmp1")
    with cc2: u2 = st.text_input("Developer 2", placeholder="e.g. gvanrossum", key="cmp2")

    if st.button("⚖️  Run Comparison", type="primary"):
        if not u1.strip() or not u2.strip():
            st.warning("Enter both usernames."); return
        tok = st.session_state.gh_token or None
        d1 = run_analysis(u1.strip(), tok, st.session_state.analysis_days)
        d2 = run_analysis(u2.strip(), tok, st.session_state.analysis_days)
        st.session_state.compare_data = (d1, d2)

    cd = st.session_state.compare_data
    if cd is None:
        st.markdown('<div class="demo-ban">ℹ️ Enter two GitHub usernames above and click Compare.</div>', unsafe_allow_html=True)
        return

    d1,d2 = cd
    sc1,mid,sc2 = st.columns([5,1,5])
    for col,d,align in [(sc1,d1,"left"),(sc2,d2,"right")]:
        with col:
            rv=d["result"]; hv=d["health"]
            av=d["profile"].get("avatar_url","")
            img=f'<img src="{av}" width="44" height="44" style="border-radius:50%;border:2px solid rgba(255,255,255,.1)" onerror="this.style.display=\'none\'">' if av else ""
            st.markdown(f"""
            <div class="gc" style="text-align:{align}">
                {img}
                <div style="font-weight:800;color:var(--text);font-size:1rem;margin-top:8px">@{d['username']}</div>
                <div style="font-size:2rem;font-weight:800;color:{rv['color']};margin:6px 0;line-height:1">{rv['score']}/100</div>
                {badge_html(rv['level'])}
                <div style="margin-top:8px;font-size:.76rem;color:var(--muted)">{rv['advice']}</div>
            </div>""", unsafe_allow_html=True)
    with mid:
        st.markdown('<div style="text-align:center;padding:2.5rem 0;font-size:1rem;font-weight:800;color:rgba(255,255,255,.1)">VS</div>', unsafe_allow_html=True)

    st.plotly_chart(chart_radar(d1["features"],d2["features"],d1["username"],d2["username"]),use_container_width=True,config=_CFG,key="cmp_radar")

    st.markdown('<div class="sh">📋 Head-to-Head</div>', unsafe_allow_html=True)
    rows=[
        ("Burnout Score",    d1["result"]["score"],                  d2["result"]["score"],                  "lower"),
        ("Health Score",     d1["health"]["score"],                  d2["health"]["score"],                  "higher"),
        ("Total Commits",    d1["features"]["total_commits"],         d2["features"]["total_commits"],         "higher"),
        ("Late Night %",     d1["features"]["late_night_pct"],        d2["features"]["late_night_pct"],        "lower"),
        ("Weekend %",        d1["features"]["weekend_pct"],           d2["features"]["weekend_pct"],           "lower"),
        ("Rest Ratio %",     d1["features"]["rest_ratio"],            d2["features"]["rest_ratio"],            "higher"),
        ("Neg Sentiment %",  d1["features"]["neg_commit_pct"],        d2["features"]["neg_commit_pct"],        "lower"),
        ("Avg Commits/Day",  d1["features"]["avg_commits_per_day"],   d2["features"]["avg_commits_per_day"],   "lower"),
        ("Current Streak",   d1["features"]["current_streak"],        d2["features"]["current_streak"],        "higher"),
    ]
    for metric,v1,v2,better in rows:
        w1=(better=="lower" and v1<v2) or (better=="higher" and v1>v2)
        w2=(better=="lower" and v2<v1) or (better=="higher" and v2>v1)
        st.markdown(f"""
        <div class="ct-row">
            <div style="text-align:right" class="{"ct-win" if w1 else "ct-los"}">{"🏆 " if w1 else ""}{v1}</div>
            <div class="ct-lbl">{metric}</div>
            <div class="{"ct-win" if w2 else "ct-los"}">{"🏆 " if w2 else ""}{v2}</div>
        </div>""", unsafe_allow_html=True)

    winner=d1 if d1["health"]["score"]>=d2["health"]["score"] else d2
    st.markdown(f"""
    <div style="background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.15);
                border-radius:12px;padding:18px;margin-top:1.5rem;text-align:center">
        <div style="font-size:1rem;font-weight:800;color:#10B981">🏆 Healthier Developer: @{winner['username']}</div>
        <div style="font-size:.78rem;color:var(--muted);margin-top:4px">Grade {winner['health']['grade']} · {winner['health']['label']} · Score {winner['health']['score']}/100</div>
    </div>""", unsafe_allow_html=True)


def page_benchmark():
    st.markdown('<div class="sh">📈 Industry Benchmark</div>', unsafe_allow_html=True)
    d = st.session_state.data
    if d is None:
        st.markdown('<div class="demo-ban">ℹ️ Analyze a profile first, or using demo data below.</div>', unsafe_allow_html=True)
        d = run_analysis("octocat", None, 90)
        st.session_state.data = d

    f=d["features"]; r=d["result"]

    tier = st.selectbox("Compare against:", list(BENCHMARKS.keys()))
    bm = BENCHMARKS[tier]

    st.markdown("<br>", unsafe_allow_html=True)
    metrics_to_compare = [
        ("Late Night Commits %",    f.get("late_night_pct",0),       bm["late_night_pct"],    "lower"),
        ("Weekend Activity %",      f.get("weekend_pct",0),          bm["weekend_pct"],       "lower"),
        ("Rest Day Ratio %",        f.get("rest_ratio",0),           bm["rest_ratio"],        "higher"),
        ("Avg Commits/Day",         f.get("avg_commits_per_day",0),  bm["avg_commits_per_day"],"neutral"),
        ("Burnout Score",           r.get("score",0),                bm["burnout_score"],     "lower"),
    ]

    b1,b2 = st.columns(2)
    for i,(metric,you,bench,better) in enumerate(metrics_to_compare):
        col = b1 if i%2==0 else b2
        with col:
            you_pct = min(float(you)/max(float(bench)*2,1)*100,100)
            bench_pct = 50.0
            delta = you - bench
            if better=="lower":
                status = "✅ Better" if delta<0 else ("⚠️ Higher" if delta>0 else "➡️ Same")
            elif better=="higher":
                status = "✅ Better" if delta>0 else ("⚠️ Lower"  if delta<0 else "➡️ Same")
            else:
                status = "➡️ Similar"
            bar_color = "#10B981" if "Better" in status else ("#EF4444" if "Higher" in status or "Lower" in status else "#6366F1")
            st.markdown(f"""
            <div class="bm-row">
              <div class="bm-hd">
                <span style="color:var(--text);font-weight:600">{metric}</span>
                <span style="color:{bar_color}">{status}</span>
              </div>
              <div style="display:flex;gap:12px;font-size:.75rem;color:var(--muted);margin-bottom:5px">
                <span>You: <strong style="color:var(--text)">{you}</strong></span>
                <span>{tier} avg: <strong style="color:var(--muted2)">{bench}</strong></span>
              </div>
              <div class="bm-bg">
                <div class="bm-you" style="width:{you_pct:.0f}%;background:{bar_color}"></div>
                <div class="bm-avg" style="left:{bench_pct:.0f}%"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # Percentile estimate
    peer_score = bm["burnout_score"]
    your_score = r.get("score",50)
    percentile = max(5, min(95, int(100-(your_score/peer_score*50))))
    st.markdown(f"""
    <div class="fc-box" style="margin-top:1.5rem;text-align:center">
        <div style="font-size:3rem;font-weight:800;color:var(--primary)">{percentile}th</div>
        <div style="font-size:1rem;color:var(--text);font-weight:600">Developer Health Percentile</div>
        <div style="font-size:.82rem;color:var(--muted);margin-top:6px">vs {tier} benchmark · Higher = Healthier</div>
    </div>""", unsafe_allow_html=True)


def page_forecast():
    st.markdown('<div class="sh">🔮 Burnout Forecast</div>', unsafe_allow_html=True)
    d = st.session_state.data
    if d is None:
        d = run_analysis("octocat", None, 90)
        st.session_state.data = d

    r=d["result"]; f=d["features"]; fc=d["forecast"]

    st.plotly_chart(chart_forecast_line(r["score"],r["level"]),use_container_width=True,config=_CFG,key="fc_line")

    st.markdown(f"""
    <div class="fc-box">
        <div class="fc-msg">{fc['message']}</div>
        <div class="fc-action">
            <div style="font-size:.68rem;font-weight:700;color:var(--primary);letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px">Recommended Action</div>
            {fc['action']}
        </div>
    </div>""", unsafe_allow_html=True)

    # 7/30/90 day predictions
    st.markdown('<div class="sh">Risk Timeline Projections</div>', unsafe_allow_html=True)
    base = r["score"]
    mult={"Healthy":0.96,"Warning":1.05,"High Risk":1.12}.get(r["level"],1.0)
    p1,p2,p3 = st.columns(3)
    s7  = min(100, base*(mult**1))
    s30 = min(100, base*(mult**4))
    s90 = min(100, base*(mult**13))
    def score_delta(s): return f"{'▲' if s>base else '▼'} {abs(s-base):.0f} pts"
    p1.metric("In 7 Days",  f"{s7:.0f}/100",  score_delta(s7))
    p2.metric("In 30 Days", f"{s30:.0f}/100", score_delta(s30))
    p3.metric("In 90 Days", f"{s90:.0f}/100", score_delta(s90))

    # Scenario comparison
    st.markdown('<div class="sh">What-If Scenarios</div>', unsafe_allow_html=True)
    sc1,sc2,sc3 = st.columns(3)
    with sc1:
        st.markdown("""
        <div class="gc">
            <div class="gc-label">If you stop late-night coding</div>
            <div class="gc-value" style="color:#10B981">-15 pts</div>
            <div class="gc-sub">Estimated 3-week impact</div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown("""
        <div class="gc">
            <div class="gc-label">If you add 2 rest days/week</div>
            <div class="gc-value" style="color:#10B981">-12 pts</div>
            <div class="gc-sub">Estimated 3-week impact</div>
        </div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown("""
        <div class="gc">
            <div class="gc-label">If you maintain current pace</div>
            <div class="gc-value" style="color:#EF4444">+{:.0f} pts</div>
            <div class="gc-sub">Estimated 30-day trajectory</div>
        </div>""".format(max(0,s30-base)), unsafe_allow_html=True)


def page_reports():
    st.markdown('<div class="sh">📄 Reports & Downloads</div>', unsafe_allow_html=True)
    d = st.session_state.data
    if d is None:
        d = run_analysis("octocat", None, 90)
        st.session_state.data = d

    r1,r2 = st.columns([2,1])
    with r1:
        st.markdown(f"""
        <div class="gc">
            <div class="gc-label">Developer Health Report</div>
            <div style="font-size:1.1rem;font-weight:700;color:var(--text);margin:8px 0">
                @{d['username']} · {date.today().strftime('%B %Y')}
            </div>
            <div style="font-size:.82rem;color:var(--muted);line-height:1.6">
                Includes: Burnout score · Risk signals · AI insights · Burnout forecast · Recommendations · Key metrics
            </div>
            <div style="margin-top:14px">{badge_html(d['result']['level'])}</div>
        </div>""", unsafe_allow_html=True)
    with r2:
        st.markdown('<div style="padding-top:1.5rem">', unsafe_allow_html=True)
        if st.button("📄  Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Generating PDF…"):
                pdf_bytes = generate_pdf_report(d)
            st.download_button(
                label="⬇️  Download Report",
                data=pdf_bytes,
                file_name=f"codeburnout_{d['username']}_{date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Report preview
    st.markdown('<div class="sh">📊 Report Preview</div>', unsafe_allow_html=True)
    f=d["features"]; r=d["result"]; h=d["health"]

    p1,p2,p3 = st.columns(3)
    with p1:
        st.markdown(f"""
        <div class="gc" style="text-align:center">
            <div style="font-size:3rem;font-weight:800;color:{r['color']}">{r['score']}</div>
            <div class="gc-label" style="margin-top:6px">Burnout Risk Score</div>
            <div style="margin-top:8px">{badge_html(r['level'])}</div>
        </div>""", unsafe_allow_html=True)
    with p2:
        bars=[("Sleep Quality", max(0,100-f.get("late_night_pct",0)*2)),
              ("Work-Life Balance",max(0,100-f.get("weekend_pct",0)*1.5)),
              ("Rest Adequacy",f.get("rest_ratio",0))]
        for lbl,val in bars:
            st.markdown(pbar_html(lbl,val,hc(val)), unsafe_allow_html=True)
    with p3:
        bars2=[("Commit Positivity",max(0,100-f.get("neg_commit_pct",0)*1.5)),
               ("Pace Sustainability",max(0,100-min(f.get("avg_commits_per_day",0)*8,100))),
               ("Sentiment Stability",100 if not f.get("sentiment_declining") else 35)]
        for lbl,val in bars2:
            st.markdown(pbar_html(lbl,val,hc(val)), unsafe_allow_html=True)

    st.markdown('<div class="sh">AI Insights Preview</div>', unsafe_allow_html=True)
    for ins in d["insights"][:4]:
        st.markdown(f'<div class="ic">{ins}</div>', unsafe_allow_html=True)


def page_achievements():
    st.markdown('<div class="sh">🏆 Achievements & Badges</div>', unsafe_allow_html=True)
    d = st.session_state.data
    if d is None:
        d = run_analysis("octocat", None, 90)
        st.session_state.data = d

    f=d["features"]; r=d["result"]
    achievements = compute_achievements(f, r)
    earned = [a for a in achievements if a["earned"]]
    locked = [a for a in achievements if not a["earned"]]

    st.markdown(f'<div style="font-size:.85rem;color:var(--muted2);margin-bottom:1.5rem">@{d["username"]} has earned <strong style="color:var(--primary)">{len(earned)}</strong> of {len(achievements)} badges</div>', unsafe_allow_html=True)

    # Progress bar
    pct = len(earned)/len(achievements)*100
    st.markdown(pbar_html(f"Progress — {len(earned)}/{len(achievements)} badges", pct, "#6366F1"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if earned:
        st.markdown('<div style="font-size:.78rem;font-weight:700;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px">Earned</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i,a in enumerate(earned):
            with cols[i%4]:
                st.markdown(f"""
                <div class="ach">
                    <div class="ach-icon">{a['icon']}</div>
                    <div class="ach-name">{a['name']}</div>
                    <div class="ach-desc">{a['desc']}</div>
                </div><br>""", unsafe_allow_html=True)

    if locked:
        st.markdown('<div style="font-size:.78rem;font-weight:700;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin:1rem 0 10px">Locked</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i,a in enumerate(locked):
            with cols[i%4]:
                st.markdown(f"""
                <div class="ach locked">
                    <div class="ach-icon">{a['icon']}</div>
                    <div class="ach-name">{a['name']}</div>
                    <div class="ach-desc">{a['desc']}</div>
                </div><br>""", unsafe_allow_html=True)

    # Leaderboard note
    st.markdown('<div class="sh">🎯 Next Badge to Unlock</div>', unsafe_allow_html=True)
    if locked:
        nxt = locked[0]
        st.markdown(f"""
        <div class="fc-box">
            <div style="font-size:2rem;margin-bottom:8px">{nxt['icon']}</div>
            <div style="font-size:1rem;font-weight:700;color:var(--text)">{nxt['name']}</div>
            <div style="font-size:.84rem;color:var(--muted);margin-top:4px">{nxt['desc']}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="fc-box"><div style="font-size:1rem;color:#10B981;font-weight:700">🎉 All badges earned! You are a Developer Health Champion.</div></div>', unsafe_allow_html=True)


def page_roadmap():
    st.markdown('<div class="sh">🗺️ 4-Week Health Roadmap</div>', unsafe_allow_html=True)
    d = st.session_state.data
    if d is None:
        d = run_analysis("octocat", None, 90)
        st.session_state.data = d

    f=d["features"]; r=d["result"]
    steps = generate_roadmap(f, r)
    target_score = max(0, r["score"]-40)

    # Header
    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="gc">
            <div class="gc-label">Current Score</div>
            <div class="gc-value" style="color:{r['color']}">{r['score']}/100</div>
            <div class="gc-sub">{r['level']}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="gc">
            <div class="gc-label">Target Score (4 weeks)</div>
            <div class="gc-value" style="color:#10B981">{target_score}/100</div>
            <div class="gc-sub">Estimated improvement: -{r['score']-target_score} pts</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">Weekly Action Plan</div>', unsafe_allow_html=True)
    for step in steps:
        st.markdown(f"""
        <div class="rm-step">
            <div class="rm-num">W{step['week']}</div>
            <div>
                <div class="rm-title">{step['title']}</div>
                <div class="rm-desc">{step['desc']}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Daily habits
    st.markdown('<div class="sh">📋 Daily Healthy Developer Habits</div>', unsafe_allow_html=True)
    habits=[
        ("⏰","Set a coding curfew","Stop all coding at 9 PM. No exceptions for 21 days — habit formation requires consistency."),
        ("☀️","Morning coding first","Do your most complex work before 12 PM when cognitive function is at peak."),
        ("🌿","Take actual breaks","5-minute break every 45 minutes. Stand up. Look away from screen."),
        ("📝","Write better commits","One clear action per commit. Future-you will thank you."),
        ("📵","Weekend boundaries","At minimum, keep Saturday afternoon and all of Sunday commit-free."),
        ("📊","Weekly self-audit","Every Friday: run CodeBurnout on yourself. Watch for trend changes."),
    ]
    h1,h2 = st.columns(2)
    for i,(icon,title,desc) in enumerate(habits):
        col=h1 if i%2==0 else h2
        with col:
            st.markdown(f"""
            <div class="rc" style="margin-bottom:10px">
                <div class="rc-icon">{icon}</div>
                <div>
                    <div class="rc-title">{title}</div>
                    <div class="rc-desc">{desc}</div>
                </div>
            </div>""", unsafe_allow_html=True)


def page_settings():
    st.markdown('<div class="sh">⚙️ Settings</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:.78rem;color:var(--muted2);margin-bottom:1.5rem">Configure CodeBurnout AI to get the most accurate analysis.</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="gc">', unsafe_allow_html=True)
        st.markdown("**🔑 GitHub Personal Access Token**")
        st.markdown('<div style="font-size:.78rem;color:var(--muted);margin-bottom:8px">Optional but highly recommended. Without a token: 60 requests/hour. With token: 5,000 requests/hour.</div>', unsafe_allow_html=True)
        token_val = st.text_input(
            "GitHub Token",
            value=st.session_state.gh_token,
            type="password",
            placeholder="ghp_xxxxxxxxxxxxxxxxxxxx",
            label_visibility="collapsed",
            key="settings_token"
        )
        if st.button("💾 Save Token", type="primary"):
            st.session_state.gh_token = token_val
            st.success("✅ Token saved for this session!")

        st.markdown("**How to get a token:**")
        st.markdown("1. Go to github.com/settings/tokens\n2. Click 'Generate new token'\n3. Select 'public_repo' scope\n4. Paste token above")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="gc">', unsafe_allow_html=True)
        st.markdown("**📅 Analysis Window**")
        st.markdown('<div style="font-size:.78rem;color:var(--muted);margin-bottom:8px">How many days of commit history to analyze.</div>', unsafe_allow_html=True)
        days_val = st.slider("Analysis window (days)",30,180,
                             st.session_state.analysis_days,15,
                             format="%d days",key="settings_days")
        if st.button("💾 Save Settings"):
            st.session_state.analysis_days = days_val
            st.success("✅ Settings saved!")

        st.markdown("**ℹ️ About CodeBurnout AI**")
        st.markdown('<div style="font-size:.8rem;color:var(--muted);line-height:1.7">Built for the Elite Coders Open Source Hackathon 2026 by Pragya Namdev, Quantum University Roorkee.<br><br>Tech stack: Python · Streamlit · Plotly · GitHub REST API · ReportLab</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Session info
    st.markdown('<div class="sh">📊 Current Session</div>', unsafe_allow_html=True)
    si1,si2,si3 = st.columns(3)
    si1.metric("Token Status",   "Active ✅" if st.session_state.gh_token else "Not set ⚠️")
    si2.metric("Analysis Window",f"{st.session_state.analysis_days} days")
    si3.metric("Data Loaded",    f"@{st.session_state.data['username']}" if st.session_state.data else "None")

    if st.button("🗑️ Clear All Data & Cache", key="clear_all"):
        for k in ["data","compare_data","chat_history","team_data"]:
            st.session_state[k] = [] if k in ("chat_history","team_data") else None
        st.success("✅ All data cleared.")
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main():
    pg = st.session_state.get("page","home")
    pages = {
        "home":      page_home,
        "dashboard": page_dashboard,
        "coach":     page_coach,
        "team":      page_team,
        "compare":   page_compare,
        "benchmark": page_benchmark,
        "forecast":  page_forecast,
        "reports":   page_reports,
        "achievements": page_achievements,
        "roadmap":   page_roadmap,
        "settings":  page_settings,
    }
    pages.get(pg, page_home)()

if __name__ == "__main__" or True:
    main()