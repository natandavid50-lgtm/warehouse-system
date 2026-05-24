import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar as cal_lib
import io
import hashlib
import random

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    from streamlit_calendar import calendar as st_calendar
    HAS_CAL = True
except ImportError:
    HAS_CAL = False

# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="WMS • אחים כהן",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📦",
)

ADMIN_HASH = hashlib.sha256(b"1234").hexdigest()
SESSION_MINS = 60
PRIS  = ["רגיל", "דחוף", "גבוה", "נמוך"]
CATS  = ["כללי", "בטיחות", "לוגיסטיקה", "ניקיון", "תחזוקה", "ספירה"]
RECUR = ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"]
MONTHS_HE = ["ינואר","פברואר","מרץ","אפריל","מאי","יוני",
             "יולי","אוגוסט","ספטמבר","אוקטובר","נובמבר","דצמבר"]

# ═══════════════════════════════════════════════════════════════════════════════
#  SEED TASKS — ריק, הוסף משימות דרך הממשק
# ═══════════════════════════════════════════════════════════════════════════════
SEED_TASKS = []

# ═══════════════════════════════════════════════════════════════════════════════
#  PREMIUM CSS — Luxury Dark · Gold & Obsidian
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Hebrew:wght@300;400;500;600;700;800;900&family=DM+Serif+Display:ital@0;1&family=Space+Mono:wght@400;700&display=swap');

/* ════════════════════════════════════
   DESIGN TOKENS
   ════════════════════════════════════ */
:root {
  /* Surfaces */
  --ink:       #08090d;
  --void:      #0c0d12;
  --surface:   #111318;
  --raised:    #181a21;
  --float:     #1e2029;
  --overlay:   #242730;

  /* Gold palette */
  --gold:      #c9a84c;
  --gold-lt:   #e8cb7a;
  --gold-dk:   #8a6e2a;
  --gold-glow: rgba(201,168,76,.18);

  /* Semantic */
  --emerald:   #2dd4a0;
  --ember:     #f97316;
  --crimson:   #f43f5e;
  --sapphire:  #60a5fa;
  --amethyst:  #c084fc;

  /* Text */
  --t1:  #f0ece0;
  --t2:  #9a9480;
  --t3:  #5a5548;

  /* Borders */
  --rule:    rgba(201,168,76,.12);
  --rule-md: rgba(201,168,76,.28);
  --rule-hi: rgba(201,168,76,.55);

  /* Type */
  --serif: 'DM Serif Display', Georgia, serif;
  --sans:  'Noto Sans Hebrew', sans-serif;
  --mono:  'Space Mono', monospace;

  /* Geometry */
  --rad:   10px;
  --rad-lg:16px;
  --rad-xl:22px;
}

/* ════════════════════════════════════
   BASE
   ════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: var(--sans) !important;
  direction: rtl !important;
  text-align: right !important;
  -webkit-font-smoothing: antialiased;
}

/* ════════════════════════════════════
   APP BACKGROUND — noise + vignette
   ════════════════════════════════════ */
.stApp {
  background-color: var(--ink) !important;
  background-image:
    radial-gradient(ellipse 120% 60% at 50% -10%,
      rgba(201,168,76,.06) 0%, transparent 55%),
    radial-gradient(ellipse 80% 50% at 100% 100%,
      rgba(45,212,160,.03) 0%, transparent 50%),
    url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
  background-size: 100% 100%, 100% 100%, 256px 256px;
}

/* ════════════════════════════════════
   SIDEBAR
   ════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: var(--void) !important;
  border-left: 1px solid var(--rule) !important;
}
[data-testid="stSidebar"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
[data-testid="stSidebar"] * { color: var(--t1) !important; }
[data-testid="stSidebar"] .stRadio label {
  background: transparent !important;
  border: 1px solid transparent;
  border-radius: var(--rad);
  padding: 10px 14px;
  margin: 2px 0;
  transition: all .22s cubic-bezier(.4,0,.2,1);
  display: block;
  font-size: .88rem;
  font-weight: 500;
  letter-spacing: .2px;
  color: var(--t2) !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(201,168,76,.07) !important;
  border-color: var(--rule-md) !important;
  color: var(--t1) !important;
  padding-right: 18px;
}

/* ════════════════════════════════════
   STREAMLIT METRICS
   ════════════════════════════════════ */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  padding: 22px 20px !important;
  border-radius: var(--rad-lg) !important;
  border: 1px solid var(--rule) !important;
  transition: all .3s !important;
  position: relative;
  overflow: hidden;
}
[data-testid="stMetric"]::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(201,168,76,.04) 0%, transparent 60%);
  pointer-events: none;
}
[data-testid="stMetric"]:hover {
  border-color: var(--rule-md) !important;
  transform: translateY(-3px) !important;
  box-shadow: 0 12px 40px rgba(0,0,0,.5), 0 0 0 1px var(--rule-md) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--t3) !important;
  font-size: .72rem !important;
  font-weight: 600 !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  color: var(--gold-lt) !important;
  font-family: var(--serif) !important;
  font-weight: 400 !important;
  font-size: 2.2rem !important;
  letter-spacing: .5px;
}

/* ════════════════════════════════════
   BUTTONS
   ════════════════════════════════════ */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--rule-md) !important;
  color: var(--gold) !important;
  border-radius: var(--rad) !important;
  font-family: var(--sans) !important;
  font-weight: 600 !important;
  font-size: .85rem !important;
  letter-spacing: .3px;
  transition: all .22s !important;
  padding: 8px 18px !important;
}
.stButton > button:hover {
  background: var(--gold-glow) !important;
  border-color: var(--gold) !important;
  box-shadow: 0 0 28px rgba(201,168,76,.15) !important;
  transform: translateY(-1px);
}

/* ════════════════════════════════════
   FORMS & INPUTS
   ════════════════════════════════════ */
[data-testid="stForm"] {
  background: var(--surface) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--rad-xl) !important;
  padding: 28px !important;
  position: relative;
  overflow: hidden;
}
[data-testid="stForm"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-dk), transparent);
}
[data-testid="stForm"] .stButton > button {
  background: linear-gradient(135deg, var(--gold-dk) 0%, #6b5020 100%) !important;
  color: var(--ink) !important;
  border: none !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 16px rgba(201,168,76,.25) !important;
}
[data-testid="stForm"] .stButton > button:hover {
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dk) 100%) !important;
  box-shadow: 0 6px 28px rgba(201,168,76,.4) !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
  background: var(--raised) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--rad) !important;
  color: var(--t1) !important;
  font-family: var(--sans) !important;
  font-size: .88rem !important;
  transition: border-color .2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--rule-hi) !important;
  box-shadow: 0 0 0 3px rgba(201,168,76,.08) !important;
}
label[data-testid="stWidgetLabel"] p {
  color: var(--t2) !important;
  font-size: .78rem !important;
  font-weight: 600 !important;
  letter-spacing: .8px !important;
  text-transform: uppercase !important;
}

/* ════════════════════════════════════
   EXPANDER
   ════════════════════════════════════ */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--rad-lg) !important;
}
details > summary { color: var(--gold) !important; font-weight: 600 !important; }

/* ════════════════════════════════════
   TABS
   ════════════════════════════════════ */
[data-testid="stTabs"] [role="tab"] {
  color: var(--t2) !important;
  font-weight: 600 !important;
  font-size: .84rem !important;
  letter-spacing: .3px;
  transition: all .2s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--gold-lt) !important;
  border-bottom: 2px solid var(--gold) !important;
}

/* ════════════════════════════════════
   DOWNLOAD BUTTON
   ════════════════════════════════════ */
[data-testid="stDownloadButton"] > button {
  background: rgba(45,212,160,.08) !important;
  border: 1px solid rgba(45,212,160,.3) !important;
  color: var(--emerald) !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: rgba(45,212,160,.16) !important;
  box-shadow: 0 0 24px rgba(45,212,160,.12) !important;
}

/* ════════════════════════════════════
   POPOVER
   ════════════════════════════════════ */
div[data-testid="stPopover"] > button {
  width: 100% !important;
  min-height: 58px !important;
  margin-bottom: 6px !important;
  font-weight: 600 !important;
  border-radius: var(--rad) !important;
  border: 1px solid var(--rule) !important;
  background: var(--surface) !important;
  color: var(--t1) !important;
  text-align: right !important;
  transition: all .2s !important;
  font-size: .86rem !important;
}
div[data-testid="stPopover"] > button:hover {
  border-color: var(--rule-md) !important;
  background: var(--raised) !important;
}

/* ════════════════════════════════════
   SCROLLBAR
   ════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--ink); }
::-webkit-scrollbar-thumb { background: var(--rule-md); border-radius: 2px; }

/* ════════════════════════════════════
   DATAFRAME
   ════════════════════════════════════ */
[data-testid="stDataFrame"] {
  border: 1px solid var(--rule) !important;
  border-radius: var(--rad-lg) !important;
  overflow: hidden;
}

/* ════════════════════════════════════
   ── CUSTOM COMPONENTS ──
   ════════════════════════════════════ */

/* ── BANNER ── */
.banner {
  position: relative;
  background: var(--surface);
  border: 1px solid var(--rule-md);
  border-radius: var(--rad-xl);
  padding: 30px 40px;
  margin-bottom: 26px;
  text-align: center;
  overflow: hidden;
}
.banner::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg,
    transparent 0%, var(--gold-dk) 20%, var(--gold-lt) 50%, var(--gold-dk) 80%, transparent 100%);
}
.banner::after {
  content: '';
  position: absolute;
  bottom: -80px; left: 50%;
  transform: translateX(-50%);
  width: 300px; height: 160px;
  background: radial-gradient(ellipse, rgba(201,168,76,.08) 0%, transparent 70%);
  pointer-events: none;
}
.banner-wordmark {
  font-family: var(--serif);
  font-size: 2rem;
  color: var(--gold-lt);
  letter-spacing: 3px;
  margin: 0 0 4px;
  text-shadow: 0 2px 30px rgba(201,168,76,.3);
}
.banner-sub {
  font-size: .72rem;
  color: var(--t3);
  letter-spacing: 3px;
  text-transform: uppercase;
  font-weight: 500;
}
.live-pip {
  display: inline-block;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--emerald);
  box-shadow: 0 0 10px var(--emerald);
  margin-left: 8px;
  animation: pip 2.4s ease infinite;
  vertical-align: middle;
}
@keyframes pip {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:.3; transform:scale(.6); }
}

/* ── KPI CARD ── */
.kpi {
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: var(--rad-lg);
  padding: 22px 18px 18px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all .3s cubic-bezier(.4,0,.2,1);
  cursor: default;
}
.kpi::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  transition: opacity .3s;
}
.kpi-gold::before   { background: linear-gradient(90deg, transparent, var(--gold), transparent); }
.kpi-emerald::before{ background: linear-gradient(90deg, transparent, var(--emerald), transparent); }
.kpi-crimson::before{ background: linear-gradient(90deg, transparent, var(--crimson), transparent); }
.kpi-ember::before  { background: linear-gradient(90deg, transparent, var(--ember), transparent); }
.kpi:hover {
  border-color: var(--rule-md);
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0,0,0,.5);
}
.kpi-icon {
  font-size: 1.6rem;
  margin-bottom: 10px;
  display: block;
}
.kpi-num {
  font-family: var(--serif);
  font-size: 2.6rem;
  font-weight: 400;
  line-height: 1;
  margin-bottom: 6px;
  letter-spacing: 1px;
}
.kpi-label {
  font-size: .68rem;
  color: var(--t3);
  letter-spacing: 2px;
  text-transform: uppercase;
  font-weight: 600;
}
.kpi-sub {
  font-size: .72rem;
  margin-top: 6px;
  font-family: var(--mono);
  opacity: .7;
}

/* ── PROGRESS BAR ── */
.track {
  background: rgba(255,255,255,.05);
  border-radius: 99px;
  overflow: hidden;
  position: relative;
}
.fill {
  height: 100%;
  border-radius: 99px;
  transition: width .9s cubic-bezier(.4,0,.2,1);
}

/* ── SECTION HEADER ── */
.sh {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 26px 0 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--rule);
}
.sh-line {
  width: 3px;
  height: 18px;
  border-radius: 2px;
  flex-shrink: 0;
}
.sh-text {
  font-family: var(--sans);
  font-size: .72rem;
  font-weight: 700;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--t2);
}

/* ── TASK CARD ── */
.tc {
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: var(--rad);
  padding: 12px 14px 12px 18px;
  margin-bottom: 6px;
  position: relative;
  transition: all .22s;
  overflow: hidden;
}
.tc::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 3px; height: 100%;
  border-radius: 0 var(--rad) var(--rad) 0;
}
.tc-gold::before   { background: var(--gold); }
.tc-emerald::before{ background: var(--emerald); }
.tc-crimson::before{ background: var(--crimson); }
.tc-ember::before  { background: var(--ember); }
.tc-dim::before    { background: var(--t3); }
.tc:hover {
  background: var(--raised);
  border-color: var(--rule-md);
  transform: translateX(-2px);
}
.tc.done { opacity: .52; }
.tc-name {
  font-weight: 600;
  font-size: .9rem;
  color: var(--t1);
  margin-bottom: 3px;
}
.tc-meta {
  font-size: .74rem;
  color: var(--t2);
  font-family: var(--mono);
}
.tc-desc {
  font-size: .76rem;
  color: var(--t3);
  margin-top: 5px;
  line-height: 1.5;
}

/* ── BADGE ── */
.chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: .65rem;
  font-weight: 700;
  letter-spacing: .6px;
  text-transform: uppercase;
  margin: 1px;
}
.chip-gold    { background: rgba(201,168,76,.14); color: var(--gold-lt);  border: 1px solid rgba(201,168,76,.22); }
.chip-emerald { background: rgba(45,212,160,.12); color: var(--emerald);  border: 1px solid rgba(45,212,160,.2); }
.chip-crimson { background: rgba(244,63,94,.12);  color: var(--crimson);  border: 1px solid rgba(244,63,94,.2); }
.chip-ember   { background: rgba(249,115,22,.12); color: var(--ember);    border: 1px solid rgba(249,115,22,.2); }
.chip-ameth   { background: rgba(192,132,252,.12);color: var(--amethyst); border: 1px solid rgba(192,132,252,.2); }
.chip-dim     { background: rgba(255,255,255,.05);color: var(--t2);       border: 1px solid var(--rule); }

/* ── WEEK CHIP ── */
.wchip {
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: var(--rad-lg);
  padding: 12px 8px;
  margin-bottom: 10px;
  text-align: center;
  transition: all .2s;
  position: relative;
  overflow: hidden;
}
.wchip.today {
  border-color: var(--rule-md);
  background: var(--raised);
}
.wchip.today::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.wchip-name { font-size: .72rem; font-weight: 700; color: var(--gold); letter-spacing: 1px; text-transform: uppercase; }
.wchip-date { font-size: .68rem; color: var(--t3); font-family: var(--mono); margin-top: 2px; }
.wchip-count{ font-size: .65rem; color: var(--emerald); font-weight: 700; margin-top: 4px; }

/* ── ALERT ── */
.alert {
  border-radius: var(--rad);
  padding: 12px 16px;
  margin-bottom: 14px;
  font-size: .86rem;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  line-height: 1.5;
}
.alert-red     { background: rgba(244,63,94,.08);  border: 1px solid rgba(244,63,94,.25); }
.alert-gold    { background: rgba(201,168,76,.07);  border: 1px solid rgba(201,168,76,.2); }
.alert-emerald { background: rgba(45,212,160,.07);  border: 1px solid rgba(45,212,160,.2); }

/* ── STAT ROW ── */
.sr {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 0;
  border-bottom: 1px solid rgba(255,255,255,.03);
}
.sr:last-child { border-bottom: none; }
.sr-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.sr-lbl { color: var(--t2); font-size: .8rem; flex: 1; }
.sr-val { color: var(--t1); font-size: .8rem; font-weight: 700; font-family: var(--mono); }

/* ── DETAIL CARD (inventory) ── */
.dc {
  background: var(--raised);
  border: 1px solid var(--rule);
  border-radius: var(--rad-lg);
  padding: 18px 20px;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  transition: all .22s;
}
.dc::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 3px; height: 100%;
}
.dc:hover { border-color: var(--rule-md); }

/* ── LOGIN BUTTONS ── */
div[data-testid="stHorizontalBlock"] .stButton > button {
  min-height: 200px !important;
  height: 200px !important;
  width: 100% !important;
  border-radius: var(--rad-xl) !important;
  font-size: 1.3rem !important;
  font-weight: 700 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: pre-wrap !important;
  text-align: center !important;
  line-height: 1.6 !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
  border-color: var(--rule-hi) !important;
  background: rgba(201,168,76,.05) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
  border-color: rgba(45,212,160,.35) !important;
  background: rgba(45,212,160,.04) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
  border-color: rgba(96,165,250,.35) !important;
  background: rgba(96,165,250,.04) !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def init_state():
    if "tasks" not in st.session_state:
        if SEED_TASKS:
            st.session_state.tasks = pd.DataFrame([{
                "ID": t["id"], "Task_Name": t["name"], "Description": t["desc"],
                "Recurring": t["rec"], "Date": t["date"],
                "Done_Dates": "", "Priority": t["pri"], "Category": t["cat"],
            } for t in SEED_TASKS])
            st.session_state.next_id = max(t["id"] for t in SEED_TASKS) + 1
        else:
            st.session_state.tasks = pd.DataFrame(columns=[
                "ID","Task_Name","Description","Recurring","Date",
                "Done_Dates","Priority","Category"])
            st.session_state.next_id = 1
    # inventory: list of monthly records
    if "inventory" not in st.session_state:
        st.session_state.inventory = []   # each: {month, skus_total, skus_counted, locs_total, locs_counted, no_gap}
    if "user_role"   not in st.session_state: st.session_state.user_role   = None
    if "login_time"  not in st.session_state: st.session_state.login_time  = None
    if "active_page" not in st.session_state: st.session_state.active_page = None

init_state()


# ═══════════════════════════════════════════════════════════════════════════════
#  TASK LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def is_scheduled(base, rec, target):
    if target < base: return False
    diff = (target - base).days
    if rec == "לא":        return diff == 0
    if rec == "יומי":      return diff < 365
    if rec == "שבועי":     return diff % 7 == 0
    if rec == "דו-שבועי":  return diff % 14 == 0
    if rec == "חודשי":     return target.day == base.day
    return False

def tasks_for_date(df, dt, skip_weekend=True):
    d = dt.date() if isinstance(dt, datetime) else dt
    if skip_weekend and d.weekday() in [4, 5]: return []
    dstr = d.strftime("%Y-%m-%d")
    out = []
    for idx, row in df.iterrows():
        try:
            base = pd.to_datetime(row["Date"]).date()
            if is_scheduled(base, row["Recurring"], d):
                done = [x for x in str(row["Done_Dates"]).split(",") if x]
                out.append({
                    "idx": idx, "id": row["ID"], "name": row["Task_Name"],
                    "desc": str(row.get("Description", "")),
                    "priority": str(row.get("Priority", "רגיל")),
                    "category": str(row.get("Category", "כללי")),
                    "is_done": dstr in done, "date": dstr,
                    "rec": str(row.get("Recurring", "")),
                })
        except: continue
    return out

def mark_done(idx, dstr):
    existing = [x for x in str(st.session_state.tasks.at[idx, "Done_Dates"]).split(",") if x]
    if dstr not in existing: existing.append(dstr)
    st.session_state.tasks.at[idx, "Done_Dates"] = ",".join(existing)

def get_overdue(days=7):
    today = datetime.now().date()
    out = []
    for i in range(1, days + 1):
        d = today - timedelta(days=i)
        for t in tasks_for_date(st.session_state.tasks, d):
            if not t["is_done"]: out.append(t)
    return out

def week_stats(days=14):
    today = datetime.now().date()
    rows = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        ts = tasks_for_date(st.session_state.tasks, d)
        tot = len(ts); don = sum(1 for t in ts if t["is_done"])
        rows.append({
            "date": d, "תאריך": d.strftime("%d/%m"),
            "בוצע": don, "מתוכנן": tot,
            "אחוז": round(don / tot * 100) if tot else 0
        })
    return pd.DataFrame(rows)

def monthly_stats(year, month):
    _, nd = cal_lib.monthrange(year, month)
    rows = []
    for day in range(1, nd + 1):
        d = datetime(year, month, day).date()
        ts = tasks_for_date(st.session_state.tasks, d)
        if ts:
            don = sum(1 for t in ts if t["is_done"])
            rows.append({"יום": day, "בוצע": don, "מתוכנן": len(ts),
                         "אחוז": round(don / len(ts) * 100)})
    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def pbar(pct, color=None, height=8):
    c = color or ("#2dd4a0" if pct >= 80 else "#f97316" if pct >= 50 else "#f43f5e")
    return (f'<div class="track" style="height:{height}px">'
            f'<div class="fill" style="width:{min(pct,100)}%;background:{c};height:{height}px"></div>'
            f'</div>')

def badge(text, kind="dim"):
    k_map = {"blue":"gold","green":"emerald","red":"crimson","amber":"ember",
             "purple":"ameth","gray":"dim", "gold":"gold","emerald":"emerald",
             "crimson":"crimson","ember":"ember"}
    cls = k_map.get(kind, "dim")
    return f'<span class="chip chip-{cls}">{text}</span>'

def pri_badge(p):
    return badge(p, {"דחוף":"crimson","גבוה":"ember","רגיל":"gold","נמוך":"dim"}.get(p,"dim"))

def cat_badge(c):
    return badge(c, {"בטיחות":"crimson","ספירה":"gold","תחזוקה":"ember",
                     "לוגיסטיקה":"ameth","ניקיון":"emerald","כללי":"dim"}.get(c,"dim"))

def tc_color(priority, is_done):
    if is_done:     return "tc-dim"
    if priority == "דחוף": return "tc-crimson"
    if priority == "גבוה": return "tc-ember"
    return "tc-gold"

def task_card_html(t):
    col_cls = tc_color(t["priority"], t["is_done"])
    icon = "✓" if t["is_done"] else ("!" if t["priority"] == "דחוף" else "·")
    rec  = f' {badge(t["rec"],"dim")}' if t.get("rec") else ""
    desc = (f'<div class="tc-desc">{t["desc"]}</div>') if t.get("desc") else ""
    done_cls = " done" if t["is_done"] else ""
    return (f'<div class="tc {col_cls}{done_cls}">'
            f'<div class="tc-name">{icon} {t["name"]} {pri_badge(t["priority"])} {cat_badge(t["category"])}{rec}</div>'
            f'{desc}</div>')

def kpi_card(val, label, sub="", color="var(--gold-lt)", icon="◈", kind="gold"):
    return (f'<div class="kpi kpi-{kind}">'
            f'<div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-num" style="color:{color}">{val}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'{"<div class=kpi-sub style=color:"+color+";opacity:.65>"+sub+"</div>" if sub else ""}'
            f'</div>')

def sec_header(title, color="var(--gold)"):
    st.markdown(
        f'<div class="sh"><div class="sh-line" style="background:{color}"></div>'
        f'<div class="sh-text">{title}</div></div>',
        unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════════════════════════════
def check_timeout():
    lt = st.session_state.get("login_time")
    if lt and (datetime.now() - lt).total_seconds() > SESSION_MINS * 60:
        st.session_state.user_role = None
        st.session_state.login_time = None
        st.rerun()

def login_screen():
    st.markdown("""
    <div class="banner">
      <div class="banner-wordmark">אחים כהן · WMS</div>
      <div class="banner-sub">
        <span class="live-pip"></span>
        מערכת ניהול מחסן מתקדמת
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.popover("🔑\nמנהל WMS", use_container_width=True):
            st.markdown(f'<div style="color:var(--t2);font-size:.8rem;margin-bottom:14px;letter-spacing:.3px">גישה מלאה לכל מודולי המערכת</div>', unsafe_allow_html=True)
            pwd = st.text_input("סיסמה", type="password", key="lpwd")
            if st.button("כניסה למערכת", use_container_width=True):
                if hashlib.sha256(pwd.encode()).hexdigest() == ADMIN_HASH:
                    st.session_state.user_role = "מנהל WMS"
                    st.session_state.login_time = datetime.now()
                    st.rerun()
                else:
                    st.error("סיסמה שגויה")
    with c2:
        if st.button("📦\nצוות מחסן", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"
            st.session_state.login_time = datetime.now()
            st.rerun()
    with c3:
        if st.button("📊\nהנהלה", use_container_width=True):
            st.session_state.user_role = "הנהלה"
            st.session_state.login_time = datetime.now()
            st.rerun()

    st.markdown("---")
    df = st.session_state.tasks
    today_ts = tasks_for_date(df, datetime.now())
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi_card(len(df), "משימות", icon="◈", kind="gold"), unsafe_allow_html=True)
    c2.markdown(kpi_card(len(today_ts), "להיום", icon="◈", kind="emerald", color="var(--emerald)"), unsafe_allow_html=True)
    c3.markdown(kpi_card(len(get_overdue()), "פיגורים", icon="◈", kind="crimson", color="var(--crimson)"), unsafe_allow_html=True)
    c4.markdown(kpi_card(len(st.session_state.get("inventory",[])), "חודשי ספירה", icon="◈", kind="gold"), unsafe_allow_html=True)
    c5.markdown(kpi_card(datetime.now().strftime("%H:%M"), "שעה", icon="◈", kind="gold"), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    df = st.session_state.tasks
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    # ── Overdue Alert ──
    overdue = get_overdue()
    if overdue:
        st.markdown(
            f'<div class="alert alert-red">⚠ <div><b style="color:var(--crimson)">'
            f'{len(overdue)} משימות שלא בוצעו בשבוע האחרון</b>'
            f'<div style="color:var(--t2);font-size:.8rem;margin-top:2px">'
            f'לחץ להצגה וסגירה</div></div></div>',
            unsafe_allow_html=True)
        with st.expander("📋 פירוט פיגורים וסגירתם"):
            for t in overdue:
                c1, c2 = st.columns([5, 1])
                c1.markdown(task_card_html(t), unsafe_allow_html=True)
                if c2.button("✓", key=f"ov_{t['id']}_{t['date']}"):
                    mark_done(t["idx"], t["date"]); st.rerun()

    # ── Date + Live clock ──
    dc, tc, _ = st.columns([1, 1, 2])
    sel = dc.date_input("📅 תאריך", today)
    dstr = sel.strftime("%Y-%m-%d")
    tc.markdown(f"""
    <div style="padding:8px 0;color:var(--t2);font-family:var(--mono);font-size:.85rem">
      🕐 {today.strftime('%H:%M:%S')} &nbsp;|&nbsp; 
      📆 {today.strftime('%A')} &nbsp;|&nbsp;
      {'🟢 <span style="color:var(--emerald)">עסק פתוח</span>' if today.weekday() not in [4,5] else '🔴 <span style="color:var(--crimson)">סגור (סוף שבוע)</span>'}
    </div>""", unsafe_allow_html=True)

    ts = tasks_for_date(df, sel)
    tot = len(ts); don = sum(1 for t in ts if t["is_done"])
    pct = round(don / tot * 100) if tot else 0
    pct_color = "#2dd4a0" if pct >= 80 else "#f97316" if pct >= 50 else "#f43f5e"
    lbl = "היום" if sel == today.date() else sel.strftime("%d/%m")

    # ── Big KPI row ──
    k1, k2, k3, k4, k5 = st.columns(5)
    pct_color = "#2dd4a0" if pct >= 80 else "#f97316" if pct >= 50 else "#f43f5e"
    k1.markdown(kpi_card(tot, f"משימות {lbl}", icon="◈", kind="gold"), unsafe_allow_html=True)
    k2.markdown(kpi_card(don, "בוצעו", icon="◈", kind="emerald", color="var(--emerald)"), unsafe_allow_html=True)
    k3.markdown(kpi_card(tot-don, "נותרו", icon="◈",
                         kind="crimson" if tot-don > 3 else "gold",
                         color="var(--crimson)" if tot-don > 3 else "var(--gold-lt)"), unsafe_allow_html=True)
    k4.markdown(kpi_card(f"{pct}%", "ביצוע",
                         sub=("מצוין" if pct>=80 else "בינוני" if pct>=50 else "נמוך"),
                         icon="◈", kind="emerald" if pct>=80 else "crimson",
                         color="var(--emerald)" if pct>=80 else "var(--crimson)"), unsafe_allow_html=True)
    k5.markdown(kpi_card(len(overdue), "פיגורים", icon="◈", kind="crimson", color="var(--crimson)"), unsafe_allow_html=True)

    st.markdown(f'<div style="margin:8px 0 20px">{pbar(pct, pct_color, 6)}</div>', unsafe_allow_html=True)


    # ── Main content: tasks list + charts side by side ──
    col_l, col_r = st.columns([5, 4])

    with col_l:
        sec_header(f"📋 משימות ל-{lbl}")
        if ts:
            # group by category
            by_cat = {}
            for t in sorted(ts, key=lambda x: (x["is_done"], x["priority"] != "דחוף")):
                by_cat.setdefault(t["category"], []).append(t)
            for cat, cat_tasks in by_cat.items():
                don_c = sum(1 for t in cat_tasks if t["is_done"])
                p = round(don_c / len(cat_tasks) * 100)
                st.markdown(f'<div style="margin:14px 0 6px;display:flex;align-items:center;gap:8px">'
                            f'{cat_badge(cat)} '
                            f'<span style="color:var(--t2);font-size:.75rem">{don_c}/{len(cat_tasks)}</span>'
                            f'{pbar(p)}</div>', unsafe_allow_html=True)
                for t in cat_tasks:
                    ca, cb = st.columns([7, 1])
                    ca.markdown(task_card_html(t), unsafe_allow_html=True)
                    if not t["is_done"] and cb.button("✓", key=f"d_{t['id']}_{dstr}_{cat}"):
                        mark_done(t["idx"], dstr); st.rerun()
        else:
            st.markdown('<div class="al alert alert-gold">ℹ️ <b>אין משימות לתאריך זה</b></div>', unsafe_allow_html=True)

    with col_r:
        sec_header("📊 מבט מהיר")

        # Category breakdown pie
        if HAS_PLOTLY and ts:
            cat_done = {}; cat_tot = {}
            for t in ts:
                c = t["category"]
                cat_tot[c] = cat_tot.get(c, 0) + 1
                if t["is_done"]: cat_done[c] = cat_done.get(c, 0) + 1
            cat_names = list(cat_tot.keys())
            cat_vals  = [cat_tot[c] for c in cat_names]
            CMAP = {"בטיחות":"#f43f5e","ספירה":"#c9a84c","תחזוקה":"#f97316",
                    "לוגיסטיקה":"#c084fc","ניקיון":"#2dd4a0","כללי":"#8899aa"}
            colors = [CMAP.get(c, "#8899aa") for c in cat_names]
            fig_pie = go.Figure(go.Pie(
                labels=cat_names, values=cat_vals,
                hole=.6, marker_colors=colors,
                textinfo="label+percent",
                textfont=dict(size=11, color="#e2eeff"),
                hovertemplate="<b>%{label}</b><br>%{value} משימות<extra></extra>",
            ))
            fig_pie.add_annotation(
                text=f"<b>{tot}</b><br><span style='font-size:10'>סה\"כ</span>",
                x=.5, y=.5, font_size=18, font_color="#c9a84c", showarrow=False)
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", height=260,
                margin=dict(t=10, b=0, l=0, r=0),
                showlegend=True,
                legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#e2eeff", font_size=11),
                font=dict(family="Heebo"))
            st.plotly_chart(fig_pie, use_container_width=True)

        # Priority breakdown
        st.markdown("**עדיפות:**")
        for pri, clr in [("דחוף","#f43f5e"),("גבוה","#f97316"),("רגיל","#c9a84c"),("נמוך","#8899aa")]:
            cnt = sum(1 for t in ts if t["priority"] == pri)
            don_c = sum(1 for t in ts if t["priority"] == pri and t["is_done"])
            if cnt:
                p = round(don_c / cnt * 100)
                st.markdown(
                    f'<div class="stat-row"><div class="tl-dot" style="background:{clr};box-shadow:0 0 8px {clr}66"></div>'
                    f'<span class="stat-label">{pri}</span>'
                    f'<span class="stat-val" style="color:{clr}">{don_c}/{cnt}</span></div>'
                    f'{pbar(p, clr, 5)}', unsafe_allow_html=True)

    # ── Weekly chart ──
    st.markdown("---")
    sec_header("📈 מגמת ביצועים — 14 ימים אחרונים")
    wdf = week_stats(14)
    if HAS_PLOTLY:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=wdf["תאריך"], y=wdf["מתוכנן"],
            name="מתוכנן", marker_color="rgba(0,212,255,.15)",
            marker_line_color="rgba(0,212,255,.3)", marker_line_width=1))
        fig.add_trace(go.Bar(
            x=wdf["תאריך"], y=wdf["בוצע"],
            name="בוצע", marker_color="rgba(0,255,136,.65)",
            marker_line_color="rgba(0,255,136,.8)", marker_line_width=1))
        fig.add_trace(go.Scatter(
            x=wdf["תאריך"], y=wdf["אחוז"],
            name="אחוז%", yaxis="y2", mode="lines+markers",
            line=dict(color="#c9a84c", width=2.5, dash="solid"),
            marker=dict(size=8, color="#c9a84c",
                        line=dict(color="#ffffff", width=1.5)),
            fill="tozeroy", fillcolor="rgba(0,212,255,.06)"))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Heebo", color="#e2eeff"), height=340,
            barmode="overlay", margin=dict(t=10, b=40, l=0, r=0),
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                        y=1.12, font_size=12),
            yaxis=dict(gridcolor="rgba(255,255,255,.04)", title="",
                       tickfont=dict(size=11)),
            yaxis2=dict(overlaying="y", side="left", range=[0, 115],
                        gridcolor="rgba(0,212,255,.05)", showgrid=False,
                        title="", tickfont=dict(size=11)),
            xaxis=dict(gridcolor="rgba(255,255,255,.03)", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Monthly analysis ──
    st.markdown("---")
    sec_header("📅 ניתוח חודשי מעמיק")

    mc, yc, _, exp_col = st.columns([1, 1, 1, 1])
    sm = mc.selectbox("חודש", range(1, 13), index=today.month - 1,
                      format_func=lambda x: MONTHS_HE[x - 1])
    sy = yc.selectbox("שנה", [2025, 2026], index=1)

    mdf = monthly_stats(sy, sm)
    if not mdf.empty:
        avg = round(mdf["אחוז"].mean())
        best = int(mdf.loc[mdf["אחוז"].idxmax(), "יום"])
        worst = int(mdf.loc[mdf["אחוז"].idxmin(), "יום"])

        ma, mb, mc2, md = st.columns(4)
        ma.metric("ממוצע חודשי",    f"{avg}%",  delta="יעד: 85%")
        mb.metric("יום שיא",        f"{best} בחודש")
        mc2.metric("יום חלש",       f"{worst} בחודש")
        md.metric("סה\"כ בוצע",     int(mdf["בוצע"].sum()))

        if HAS_PLOTLY:
            c_bar, c_heat = st.columns([3, 2])
            with c_bar:
                colors_m = ["#2dd4a0" if v >= 80 else "#f97316" if v >= 50 else "#f43f5e"
                            for v in mdf["אחוז"]]
                fig_m = go.Figure()
                fig_m.add_trace(go.Bar(
                    x=mdf["יום"], y=mdf["אחוז"],
                    marker_color=colors_m,
                    text=[f"{v}%" for v in mdf["אחוז"]],
                    textposition="outside", textfont=dict(size=9, color="#e2eeff")))
                fig_m.add_hline(y=85, line_dash="dot", line_color="rgba(0,255,136,.4)",
                                annotation_text="יעד 85%",
                                annotation_font_color="#2dd4a0",
                                annotation_font_size=11)
                fig_m.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Heebo", color="#e2eeff"), height=300,
                    margin=dict(t=30, b=30, l=0, r=0), showlegend=False,
                    yaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,.04)"),
                    xaxis=dict(gridcolor="rgba(255,255,255,.03)"))
                st.plotly_chart(fig_m, use_container_width=True)

            with c_heat:
                # Category breakdown for month
                cat_m = {}
                _, nd = cal_lib.monthrange(sy, sm)
                for day in range(1, nd + 1):
                    for t in tasks_for_date(st.session_state.tasks,
                                            datetime(sy, sm, day).date()):
                        c = t["category"]
                        cat_m.setdefault(c, {"done": 0, "total": 0})
                        cat_m[c]["total"] += 1
                        if t["is_done"]: cat_m[c]["done"] += 1
                if cat_m:
                    cdf = pd.DataFrame([
                        {"קטגוריה": k, "אחוז": round(v["done"]/max(v["total"],1)*100),
                         "בוצע": v["done"], "מתוכנן": v["total"]}
                        for k, v in cat_m.items()]).sort_values("אחוז", ascending=True)
                    CMAP2 = {"בטיחות":"#f43f5e","ספירה":"#c9a84c","תחזוקה":"#f97316",
                             "לוגיסטיקה":"#c084fc","ניקיון":"#2dd4a0","כללי":"#8899aa"}
                    fig_c = go.Figure(go.Bar(
                        x=cdf["אחוז"], y=cdf["קטגוריה"],
                        orientation="h",
                        marker_color=[CMAP2.get(c,"#8899aa") for c in cdf["קטגוריה"]],
                        text=[f"{v}%" for v in cdf["אחוז"]],
                        textposition="outside",
                        textfont=dict(color="#e2eeff", size=11)))
                    fig_c.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Heebo", color="#e2eeff"), height=300,
                        margin=dict(t=10, b=10, l=80, r=60),
                        xaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,.04)"),
                        yaxis=dict(gridcolor="rgba(255,255,255,.03)"),
                        showlegend=False)
                    st.plotly_chart(fig_c, use_container_width=True)

        # Excel export
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            mdf.to_excel(w, index=False, sheet_name="ביצועים יומי")
            wdf.to_excel(w, index=False, sheet_name="ביצועים שבועי")
        st.download_button(
            "📥 ייצוא דוח Excel מלא", buf.getvalue(),
            f"דוח_ביצועים_{sm:02d}_{sy}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.markdown('<div class="al alert alert-gold">⚠️ אין נתוני משימות לחודש הנבחר</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: WORK ORDER — weekly board
# ═══════════════════════════════════════════════════════════════════════════════
def page_work():
    df = st.session_state.tasks
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    day_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)

    for i, name in enumerate(day_names):
        curr = start + timedelta(days=i)
        ts = tasks_for_date(df, curr)
        don = sum(1 for t in ts if t["is_done"])
        pct = round(don / len(ts) * 100) if ts else 0
        is_today = curr.date() == today.date()
        pct_color = "#2dd4a0" if pct >= 80 else "#f97316" if pct >= 50 else "#f43f5e"

        with cols[i]:
            border_color = "var(--gold-lt)" if is_today else "var(--rule-md)"
            bg = "rgba(0,212,255,.05)" if is_today else "transparent"
            st.markdown(f"""
            <div class="wchip" style="border-color:{border_color};background:linear-gradient(135deg,var(--surface),{bg})">
              {'<span style="color:var(--ember);font-size:.6rem;font-family:var(--mono)">▸ היום ◂</span><br>' if is_today else ""}
              <div class="day-name">{name}</div>
              <div class="day-date">{curr.strftime('%d/%m/%y')}</div>
              <div class="day-count">{don}/{len(ts)} ✓</div>
            </div>
            {pbar(pct, pct_color, 5)}
            """, unsafe_allow_html=True)

            # group by priority within day
            urgent = [t for t in ts if t["priority"] == "דחוף"]
            rest   = [t for t in ts if t["priority"] != "דחוף"]

            for t in urgent + rest:
                ico = "✅" if t["is_done"] else ("🚨" if t["priority"] == "דחוף" else "⏳")
                lbl = f"{ico} {t['name']}"
                with st.popover(lbl, use_container_width=True):
                    st.markdown(f"**📋 {t['name']}**")
                    st.markdown(f"**עדיפות:** {t['priority']}")
                    st.markdown(f"**קטגוריה:** {t['category']}")
                    if t["desc"]:     st.markdown(f"**📝 פירוט:** {t['desc']}")
                    if not t["is_done"]:
                        if st.button("✅ סמן כבוצע", key=f"w_{t['id']}_{i}_{curr.date()}"):
                            mark_done(t["idx"], curr.strftime("%Y-%m-%d"))
                            st.rerun()

    # end of page_work


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════
def page_calendar():
    df = st.session_state.tasks
    today = datetime.now().date()
    events = []

    for _, row in df.iterrows():
        base = pd.to_datetime(row["Date"]).date()
        for i in range(180):
            d = base + timedelta(days=i)
            if is_scheduled(base, row["Recurring"], d):
                done = d.strftime("%Y-%m-%d") in str(row["Done_Dates"])
                CMAP = {"בטיחות":"#f43f5e","ספירה":"#c9a84c","תחזוקה":"#f97316",
                        "לוגיסטיקה":"#c084fc","ניקיון":"#2dd4a0","כללי":"#8899aa"}
                base_color = CMAP.get(str(row.get("Category","")), "#388bfd")
                color = "#2dd4a0" if done else ("#f43f5e" if d < today else base_color)
                events.append({
                    "title": f"{'✅ ' if done else ''}{row['Task_Name']}",
                    "start": d.strftime("%Y-%m-%d"),
                    "color": color,
                    "allDay": True,
                })

    # Legend
    CATS_COLORS = [("בטיחות","#f43f5e"),("ספירה","#c9a84c"),("תחזוקה","#f97316"),
                   ("לוגיסטיקה","#c084fc"),("ניקיון","#2dd4a0"),("כללי","#8899aa")]
    legend_html = " &nbsp; ".join(
        f'<span style="color:{c}">⬤</span> <span style="color:var(--t2);font-size:.78rem">{n}</span>'
        for n, c in CATS_COLORS)
    st.markdown(
        f'<div style="margin-bottom:12px;padding:10px 16px;background:var(--surface);'
        f'border:1px solid var(--rule);border-radius:10px">'
        f'{legend_html} &nbsp;&nbsp; '
        f'<span style="color:#2dd4a0">⬤</span> <span style="color:var(--t2);font-size:.78rem">בוצע</span> &nbsp; '
        f'<span style="color:#f43f5e">⬤</span> <span style="color:var(--t2);font-size:.78rem">מפוגר</span>'
        f'</div>',
        unsafe_allow_html=True)

    st.markdown(f'<div style="color:var(--t2);font-size:.8rem;margin-bottom:12px;font-family:var(--mono)">'
                f'◈ {len(events)} אירועים | 6 חודשים קדימה</div>', unsafe_allow_html=True)

    if HAS_CAL:
        st_calendar(events=events,
            options={
                "direction": "rtl", "locale": "he",
                "initialView": "dayGridMonth", "height": 680,
                "headerToolbar": {
                    "right": "today prev,next",
                    "center": "title",
                    "left": "dayGridMonth,timeGridWeek,listMonth"
                }
            },
            custom_css="""
              .fc { background:#0a1c35; color:#e2eeff; border-radius:16px; padding:14px; }
              .fc-toolbar-title { font-family:'Orbitron',monospace; color:#c9a84c; font-size:1.1rem; }
              .fc-button { background:#0d2240!important; border:1px solid rgba(0,212,255,.4)!important;
                           border-radius:8px!important; color:#c9a84c!important; font-weight:700!important; }
              .fc-button:hover { background:rgba(0,212,255,.15)!important; }
              .fc-button-active { background:rgba(0,212,255,.2)!important; }
              .fc-day-today { background:rgba(0,212,255,.08)!important; border:1px solid rgba(0,212,255,.3)!important; }
              .fc-event { border-radius:5px!important; border:none!important; font-size:.72rem; font-weight:600; }
              .fc-daygrid-day-number { color:#7a90b0; font-size:.8rem; }
              .fc-col-header-cell { background:#071526; }
              .fc-col-header-cell-cushion { color:#c9a84c; font-weight:700; font-size:.8rem; }
            """)
    else:
        st.warning("💡 התקן `streamlit-calendar` לתצוגה מלאה")
        upcoming = sorted([e for e in events if e["start"] >= today.strftime("%Y-%m-%d")],
                          key=lambda x: x["start"])[:50]
        if upcoming:
            edf = pd.DataFrame(upcoming)[["start", "title"]]
            edf.columns = ["תאריך", "משימה"]
            st.dataframe(edf, use_container_width=True, height=500)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: MANAGE TASKS
# ═══════════════════════════════════════════════════════════════════════════════
def page_manage():
    df = st.session_state.tasks

    # ── Filters ──
    f1, f2, f3, f4 = st.columns(4)
    fsearch = f1.text_input("🔍 חיפוש", placeholder="שם משימה...")
    fpri    = f2.selectbox("עדיפות",   ["הכל"] + PRIS)
    fcat    = f3.selectbox("קטגוריה",  ["הכל"] + CATS)
    frec    = f4.selectbox("תדירות",   ["הכל"] + RECUR)

    filt = df.copy()
    if fsearch: filt = filt[filt["Task_Name"].str.contains(fsearch, na=False, case=False)]
    if fpri   != "הכל": filt = filt[filt["Priority"]    == fpri]
    if fcat   != "הכל": filt = filt[filt["Category"]    == fcat]
    if frec   != "הכל": filt = filt[filt["Recurring"]   == frec]

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;margin:10px 0 16px">'
        f'<span style="color:var(--t2);font-size:.82rem;font-family:var(--mono)">'
        f'◈ {len(filt)} / {len(df)} משימות</span>'
        f'<div style="flex:1">{pbar(round(len(filt)/max(len(df),1)*100), height=4)}</div>'
        f'</div>', unsafe_allow_html=True)

    # Tab view: All / By category
    tab_all, tab_cat = st.tabs(["📋 כל המשימות", "🏷️ לפי קטגוריה"])

    with tab_all:
        for idx, row in filt.iterrows():
            ci, ce, cd = st.columns([5, 1, 1])
            ci.markdown(
                f'<div class="tc">'
                f'<b style="font-size:.95rem">{row["Task_Name"]}</b> '
                f'{pri_badge(row.get("Priority","רגיל"))} '
                f'{cat_badge(row.get("Category",""))} '
                f'{badge(row.get("Recurring",""),"gray")}'
                f'{"<div style=color:var(--t2);font-size:.78rem;margin-top:4px;font-family:var(--mono)>"+str(row.get("Description",""))+"</div>" if row.get("Description") else ""}'
                f'</div>', unsafe_allow_html=True)

            with ce:
                with st.popover("✏️", use_container_width=True):
                    nn = st.text_input("שם", value=row["Task_Name"], key=f"en{row['ID']}")
                    nd = st.text_area("תיאור", value=str(row.get("Description", "")), key=f"ed{row['ID']}")
                    np = st.selectbox("עדיפות", PRIS,
                        index=PRIS.index(row.get("Priority","רגיל")) if row.get("Priority") in PRIS else 0,
                        key=f"ep{row['ID']}")
                    nc = st.selectbox("קטגוריה", CATS,
                        index=CATS.index(row.get("Category","כללי")) if row.get("Category") in CATS else 0,
                        key=f"ec{row['ID']}")
                    nr = st.selectbox("תדירות", RECUR,
                        index=RECUR.index(row.get("Recurring","יומי")) if row.get("Recurring") in RECUR else 0,
                        key=f"er{row['ID']}")
                    nd2 = st.date_input("תאריך", value=pd.to_datetime(row["Date"]).date(),
                                        key=f"edt{row['ID']}")
                    if st.button("💾 שמור שינויים", key=f"sv{row['ID']}", use_container_width=True):
                        st.session_state.tasks.at[idx, "Task_Name"]   = nn
                        st.session_state.tasks.at[idx, "Description"] = nd
                        st.session_state.tasks.at[idx, "Priority"]    = np
                        st.session_state.tasks.at[idx, "Category"]    = nc
                        st.session_state.tasks.at[idx, "Recurring"]   = nr
                        st.session_state.tasks.at[idx, "Date"]        = nd2.strftime("%Y-%m-%d")
                        st.rerun()

            with cd:
                ck = f"cfm_{row['ID']}"
                if not st.session_state.get(ck):
                    if st.button("🗑️", key=f"dl{row['ID']}", help="מחק משימה"):
                        st.session_state[ck] = True; st.rerun()
                else:
                    st.warning("בטוח?")
                    if st.button("כן", key=f"cy{row['ID']}"):
                        st.session_state.tasks = st.session_state.tasks.drop(idx).reset_index(drop=True)
                        st.session_state.pop(ck, None); st.rerun()
                    if st.button("לא", key=f"cn{row['ID']}"):
                        st.session_state.pop(ck, None); st.rerun()

    with tab_cat:
        for cat in CATS:
            cat_tasks = filt[filt["Category"] == cat]
            if cat_tasks.empty: continue
            with st.expander(f"{cat_badge(cat)} {cat} — {len(cat_tasks)} משימות", expanded=False):
                for idx, row in cat_tasks.iterrows():
                    st.markdown(
                        f'<div class="tc">'
                        f'<b>{row["Task_Name"]}</b> {pri_badge(row.get("Priority","רגיל"))} '
                        f'{badge(row.get("Recurring",""),"gray")}'
                        f'{"<br><span style=color:var(--t2);font-size:.78rem>"+str(row.get("Description",""))+"</span>" if row.get("Description") else ""}'
                        f'</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: ADD TASK
# ═══════════════════════════════════════════════════════════════════════════════
def page_add():
    c_form, c_preview = st.columns([2, 1])

    with c_form:
        with st.form("add_form", clear_on_submit=True):
            sec_header("➕ הוספת משימה חדשה")
            a, b = st.columns(2)
            name = a.text_input("שם המשימה *", placeholder="לדוגמה: בדיקת מלאי אזור D")
            freq = b.selectbox("תדירות חזרה", RECUR)
            desc = st.text_area("פירוט / הוראות ביצוע",
                                placeholder="תאר את המשימה בפירוט: מה לבדוק, איך לבצע, מה לתעד...")
            c, d = st.columns(2)
            pri  = c.selectbox("עדיפות",   PRIS)
            cat  = d.selectbox("קטגוריה",  CATS)
            sdate = st.date_input("תאריך התחלה", datetime.now())

            submitted = st.form_submit_button("🚀 שמור משימה", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("⚠️ שם משימה הוא שדה חובה")
                else:
                    new_row = {
                        "ID": st.session_state.next_id,
                        "Task_Name": name.strip(), "Description": desc,
                        "Recurring": freq, "Date": sdate.strftime("%Y-%m-%d"),
                        "Done_Dates": "", "Priority": pri, "Category": cat,
                    }
                    st.session_state.tasks = pd.concat(
                        [st.session_state.tasks, pd.DataFrame([new_row])],
                        ignore_index=True)
                    st.session_state.next_id += 1
                    st.success(f"✅ משימה '{name}' נוספה בהצלחה!")
                    st.rerun()

    with c_preview:
        sec_header("📊 סטטיסטיקת משימות")
        df = st.session_state.tasks
        total = len(df)

        # By recurring type
        st.markdown("**לפי תדירות:**")
        for rec in RECUR:
            cnt = len(df[df["Recurring"] == rec])
            if cnt:
                p = round(cnt / total * 100)
                st.markdown(
                    f'<div class="stat-row">'
                    f'<span class="stat-label">{rec}</span>'
                    f'<span class="stat-val">{cnt}</span>'
                    f'</div>{pbar(p, height=4)}', unsafe_allow_html=True)

        # By category
        st.markdown("**לפי קטגוריה:**")
        for cat in CATS:
            cnt = len(df[df["Category"] == cat])
            if cnt:
                p = round(cnt / total * 100)
                st.markdown(
                    f'<div class="stat-row">'
                    f'{cat_badge(cat)}'
                    f'<span class="stat-val">{cnt}</span>'
                    f'</div>{pbar(p, height=4)}', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: INVENTORY COUNT DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_inventory():
    sec_header("📦 דשבורד ספירות מלאי")

    inventory = st.session_state.inventory  # list of dicts

    # ── Month selector ──
    today = datetime.now()
    month_options = []
    for i in range(12):
        dt = today - timedelta(days=30 * i)
        month_options.append(f"{dt.year}-{dt.month:02d}")
    month_options = list(dict.fromkeys(month_options))  # dedupe

    col_sel, col_new = st.columns([2, 3])
    sel_month = col_sel.selectbox(
        "📅 בחר חודש לצפייה / עריכה",
        month_options,
        format_func=lambda x: f"{MONTHS_HE[int(x.split('-')[1])-1]} {x.split('-')[0]}"
    )

    # Find or create record for selected month
    rec = next((r for r in inventory if r["month"] == sel_month), None)
    if rec is None:
        rec = {"month": sel_month,
               "skus_total": 0, "skus_counted": 0,
               "locs_total": 0, "locs_counted": 0, "no_gap": 0}

    # ── Input form (admin only) ──
    if st.session_state.user_role == "מנהל WMS":
        with st.expander("✏️ הזן / עדכן נתוני ספירה לחודש זה", expanded=(rec["skus_total"] == 0)):
            with st.form("inv_form"):
                st.markdown(f"##### עדכון נתוני ספירה — "
                            f"{MONTHS_HE[int(sel_month.split('-')[1])-1]} {sel_month.split('-')[0]}")
                st.markdown("---")
                st.markdown("**מק\"טים (SKUs)**")
                c1, c2 = st.columns(2)
                skus_total   = c1.number_input('סך מק"טים במחסן',   min_value=0, value=int(rec["skus_total"]),   step=1)
                skus_counted = c2.number_input('מק"טים שנספרו',      min_value=0, value=int(rec["skus_counted"]), step=1)

                st.markdown("**איתורים (Locations)**")
                c3, c4 = st.columns(2)
                locs_total   = c3.number_input("סך איתורים במחסן",   min_value=0, value=int(rec["locs_total"]),   step=1)
                locs_counted = c4.number_input("איתורים שנספרו",      min_value=0, value=int(rec["locs_counted"]), step=1)

                st.markdown("**דיוק**")
                no_gap = st.number_input(
                    "איתורים שנספרו ללא פער (מתוך שנספרו)",
                    min_value=0, value=int(rec["no_gap"]), step=1,
                    help="מספר האיתורים שהספירה תאמה בדיוק את מה שהיה במערכת")

                if st.form_submit_button("💾 שמור נתונים", use_container_width=True):
                    new_rec = {
                        "month": sel_month,
                        "skus_total": skus_total, "skus_counted": skus_counted,
                        "locs_total": locs_total, "locs_counted": locs_counted,
                        "no_gap": no_gap,
                    }
                    # update or append
                    updated = False
                    for i, r in enumerate(st.session_state.inventory):
                        if r["month"] == sel_month:
                            st.session_state.inventory[i] = new_rec
                            updated = True
                            break
                    if not updated:
                        st.session_state.inventory.append(new_rec)
                    st.success("✅ נתונים נשמרו!")
                    st.rerun()

    # re-fetch after possible save
    rec = next((r for r in st.session_state.inventory if r["month"] == sel_month), rec)

    st.markdown("---")

    # ── KPI calculations ──
    skus_t = max(int(rec["skus_total"]),   1)
    skus_c = int(rec["skus_counted"])
    locs_t = max(int(rec["locs_total"]),   1)
    locs_c = int(rec["locs_counted"])
    no_gap = int(rec["no_gap"])

    pct_skus = round(skus_c / skus_t * 100)
    pct_locs = round(locs_c / locs_t * 100)
    pct_acc  = round(no_gap / max(locs_c, 1) * 100)

    color_skus = "#2dd4a0" if pct_skus >= 90 else "#f97316" if pct_skus >= 70 else "#f43f5e"
    color_locs = "#c9a84c" if pct_locs >= 90 else "#f97316" if pct_locs >= 70 else "#f43f5e"
    color_acc  = "#c084fc" if pct_acc  >= 98 else "#f97316" if pct_acc  >= 90 else "#f43f5e"

    # ── Big 3 KPI cards ──
    k1, k2, k3 = st.columns(3)
    k1.markdown(kpi_card(f"{pct_skus}%", 'ספירת מק"טים',
                         sub=f'{skus_c:,} / {skus_t:,} מק"טים',
                         color=color_skus, icon="🏷️", kind="blue"), unsafe_allow_html=True)
    k1.markdown(pbar(pct_skus, color_skus, 10), unsafe_allow_html=True)

    k2.markdown(kpi_card(f"{pct_locs}%", "ספירת איתורים",
                         sub=f'{locs_c:,} / {locs_t:,} איתורים',
                         color=color_locs, icon="📍", kind="blue"), unsafe_allow_html=True)
    k2.markdown(pbar(pct_locs, color_locs, 10), unsafe_allow_html=True)

    k3.markdown(kpi_card(f"{pct_acc}%", "דיוק ספירה",
                         sub=f'{no_gap:,} ללא פער מתוך {locs_c:,}',
                         color=color_acc, icon="🎯", kind="blue"), unsafe_allow_html=True)
    k3.markdown(pbar(pct_acc, color_acc, 10), unsafe_allow_html=True)

    st.markdown("---")

    # ── Detail cards + Gauge charts ──
    left_col, right_col = st.columns([3, 4])

    with left_col:
        sec_header("📊 פירוט מספרי")

        def detail_row(label, val, total, color):
            pct = round(val / max(total, 1) * 100)
            remaining = total - val
            status = "✅ הושלם" if pct >= 100 else f"⏳ נותרו {remaining:,}"
            st.markdown(
                f'<div style="background:var(--raised);border:1px solid var(--rule);'
                f'border-radius:12px;padding:16px 18px;margin-bottom:12px;'
                f'border-right:4px solid {color}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
                f'<span style="font-weight:700;font-size:.95rem;color:var(--t1)">{label}</span>'
                f'<span style="font-family:var(--mono);font-size:.8rem;color:var(--t2)">{status}</span>'
                f'</div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:8px">'
                f'<span style="font-family:var(--orb);font-size:1.8rem;font-weight:800;color:{color}'
                f';text-shadow:0 0 16px {color}66">{pct}%</span>'
                f'<div style="text-align:left">'
                f'<div style="font-size:.72rem;color:var(--t2)">נספרו</div>'
                f'<div style="font-family:var(--mono);font-size:1rem;color:{color};font-weight:700">{val:,}</div>'
                f'</div>'
                f'<div style="text-align:left">'
                f'<div style="font-size:.72rem;color:var(--t2)">סה"כ</div>'
                f'<div style="font-family:var(--mono);font-size:1rem;color:var(--t1);font-weight:700">{total:,}</div>'
                f'</div>'
                f'</div>'
                f'{pbar(pct, color, 8)}'
                f'</div>',
                unsafe_allow_html=True)

        detail_row('מק"טים שנספרו', skus_c, skus_t, color_skus)
        detail_row("איתורים שנספרו", locs_c, locs_t, color_locs)
        detail_row("איתורים ללא פער", no_gap, locs_c, color_acc)

        # Gap count
        gap_count = locs_c - no_gap
        gap_pct   = round(gap_count / max(locs_c, 1) * 100)
        gap_color = "#f43f5e" if gap_pct > 10 else "#f97316" if gap_pct > 5 else "#2dd4a0"
        st.markdown(
            f'<div style="background:var(--raised);border:1px solid rgba(255,45,85,.3);'
            f'border-radius:12px;padding:14px 18px;border-right:4px solid {gap_color}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<span style="font-weight:700;color:var(--t1)">⚡ איתורים עם פער</span>'
            f'<span style="font-family:var(--orb);font-size:1.5rem;color:{gap_color};font-weight:800">'
            f'{gap_count:,}</span>'
            f'</div>'
            f'<div style="color:var(--t2);font-size:.78rem;margin-top:4px">'
            f'{gap_pct}% מהאיתורים שנספרו — '
            f'{"⚠️ גבוה" if gap_pct > 10 else "⚡ בינוני" if gap_pct > 5 else "✅ תקין"}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True)

    with right_col:
        if HAS_PLOTLY:
            sec_header("🎯 גרפי ביצוע")

            # 3 donut gauges
            fig = make_subplots(rows=1, cols=3,
                specs=[[{"type":"pie"},{"type":"pie"},{"type":"pie"}]],
                subplot_titles=["מק\"טים","איתורים","דיוק"])

            for col_idx, (val, total, color, label) in enumerate([
                (skus_c, skus_t, color_skus, "מק\"טים"),
                (locs_c, locs_t, color_locs, "איתורים"),
                (no_gap, max(locs_c,1), color_acc, "דיוק"),
            ], start=1):
                remain = max(0, total - val)
                pct_v  = round(val / max(total, 1) * 100)
                fig.add_trace(go.Pie(
                    values=[val, remain],
                    hole=.72,
                    marker_colors=[color, "rgba(255,255,255,.05)"],
                    showlegend=False, textinfo="none",
                    hoverinfo="skip",
                ), row=1, col=col_idx)
                fig.add_annotation(
                    text=f"<b>{pct_v}%</b>",
                    x=(col_idx - 1) / 3 + 1/6,
                    y=0.5, xref="paper", yref="paper",
                    font_size=22, font_family="Orbitron",
                    font_color=color, showarrow=False)

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", height=260,
                margin=dict(t=40, b=0, l=0, r=0),
                font=dict(family="Heebo", color="#e2eeff"))
            for ann in fig.layout.annotations:
                if ann.text in ["מק\"טים", "איתורים", "דיוק"]:
                    ann.update(font=dict(color="#7a90b0", size=12, family="Heebo"))
            st.plotly_chart(fig, use_container_width=True)

            # Stacked bar: counted vs not counted
            fig2 = go.Figure()
            cats_bar = ["מק\"טים", "איתורים"]
            counted  = [skus_c, locs_c]
            remaining= [skus_t - skus_c, locs_t - locs_c]
            fig2.add_trace(go.Bar(
                name="נספרו", x=cats_bar, y=counted,
                marker_color=["#2dd4a0", "#c9a84c"],
                text=[f"{v:,}" for v in counted],
                textposition="inside", textfont=dict(color="#040d1c", size=13, family="Orbitron")))
            fig2.add_trace(go.Bar(
                name="טרם נספרו", x=cats_bar, y=remaining,
                marker_color=["rgba(0,255,136,.1)", "rgba(0,212,255,.1)"],
                marker_line_color=["rgba(0,255,136,.3)", "rgba(0,212,255,.3)"],
                marker_line_width=1,
                text=[f"{v:,}" for v in remaining],
                textposition="inside", textfont=dict(color="#7a90b0", size=11)))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Heebo", color="#e2eeff"), height=260,
                barmode="stack", margin=dict(t=10, b=30, l=0, r=0),
                legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12),
                yaxis=dict(gridcolor="rgba(255,255,255,.04)"),
                xaxis=dict(gridcolor="rgba(255,255,255,.03)"))
            st.plotly_chart(fig2, use_container_width=True)

    # ── Historical trend (if multiple months exist) ──
    if len(st.session_state.inventory) >= 2 and HAS_PLOTLY:
        st.markdown("---")
        sec_header("📈 מגמה היסטורית")
        hist = sorted(st.session_state.inventory, key=lambda x: x["month"])
        hdf = pd.DataFrame([{
            "חודש":      f"{MONTHS_HE[int(r['month'].split('-')[1])-1]} {r['month'].split('-')[0]}",
            "מק\"טים %": round(int(r["skus_counted"]) / max(int(r["skus_total"]), 1) * 100),
            "איתורים %": round(int(r["locs_counted"]) / max(int(r["locs_total"]), 1) * 100),
            "דיוק %":    round(int(r["no_gap"]) / max(int(r["locs_counted"]), 1) * 100),
        } for r in hist])

        fig_h = go.Figure()
        for col_name, color in [("מק\"טים %","#2dd4a0"),("איתורים %","#c9a84c"),("דיוק %","#c084fc")]:
            fig_h.add_trace(go.Scatter(
                x=hdf["חודש"], y=hdf[col_name],
                name=col_name, mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=9, color=color,
                            line=dict(color="#040d1c", width=2)),
                fill="tozeroy" if col_name == "דיוק %" else "none",
                fillcolor=f"{color}0d"))
        fig_h.add_hline(y=95, line_dash="dot", line_color="rgba(191,90,242,.4)",
                        annotation_text="יעד דיוק 95%",
                        annotation_font_color="#c084fc", annotation_font_size=11)
        fig_h.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Heebo", color="#e2eeff"), height=300,
            margin=dict(t=10, b=40, l=0, r=0),
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12),
            yaxis=dict(range=[0,108], gridcolor="rgba(255,255,255,.04)"),
            xaxis=dict(gridcolor="rgba(255,255,255,.03)"))
        st.plotly_chart(fig_h, use_container_width=True)

    # ── Export ──
    st.markdown("---")
    if st.session_state.inventory:
        buf = io.BytesIO()
        export_data = []
        for r in sorted(st.session_state.inventory, key=lambda x: x["month"], reverse=True):
            export_data.append({
                "חודש":               f"{MONTHS_HE[int(r['month'].split('-')[1])-1]} {r['month'].split('-')[0]}",
                'סך מק"טים':         r["skus_total"],
                'מק"טים שנספרו':      r["skus_counted"],
                'אחוז ספירת מק"טים': f"{round(int(r['skus_counted'])/max(int(r['skus_total']),1)*100)}%",
                "סך איתורים":         r["locs_total"],
                "איתורים שנספרו":     r["locs_counted"],
                "אחוז ספירת איתורים": f"{round(int(r['locs_counted'])/max(int(r['locs_total']),1)*100)}%",
                "ללא פער":            r["no_gap"],
                "אחוז דיוק":         f"{round(int(r['no_gap'])/max(int(r['locs_counted']),1)*100)}%",
            })
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            pd.DataFrame(export_data).to_excel(w, index=False, sheet_name="ספירות מלאי")
        st.download_button(
            "📥 ייצוא כל הספירות — Excel",
            buf.getvalue(), "ספירות_מלאי.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS (מנהל בלבד)
# ═══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    df = st.session_state.tasks
    today = datetime.now()
    sec_header("🔬 אנליטיקס מתקדם")

    if not HAS_PLOTLY:
        st.warning("נדרש plotly לדף זה")
        return

    # ── 4-panel overview ──
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["ביצועים שבועיים", "התפלגות קטגוריות",
                        "עומס לפי יום בשבוע", "ביצועים חודשיים"],
        specs=[[{"type":"scatter"},{"type":"pie"}],
               [{"type":"bar"},{"type":"bar"}]],
        vertical_spacing=0.15, horizontal_spacing=0.1)

    # 1. Weekly trend
    wdf = week_stats(21)
    fig.add_trace(go.Scatter(
        x=wdf["תאריך"], y=wdf["אחוז"], mode="lines+markers",
        line=dict(color="#c9a84c", width=2), marker=dict(size=7, color="#c9a84c"),
        name="אחוז"), row=1, col=1)

    # 2. Category pie
    cat_counts = df["Category"].value_counts()
    CMAP = {"בטיחות":"#f43f5e","ספירה":"#c9a84c","תחזוקה":"#f97316",
            "לוגיסטיקה":"#c084fc","ניקיון":"#2dd4a0","כללי":"#8899aa"}
    fig.add_trace(go.Pie(
        labels=cat_counts.index.tolist(),
        values=cat_counts.values.tolist(),
        hole=.5, textinfo="label+percent",
        marker_colors=[CMAP.get(c,"#8899aa") for c in cat_counts.index],
        showlegend=False, name=""), row=1, col=2)

    # 3. Load by day of week
    day_load = {d: 0 for d in range(5)}
    for _, row in df.iterrows():
        rec = row["Recurring"]
        if rec == "יומי":
            for d in range(5): day_load[d] += 1
        elif rec == "שבועי":
            try:
                base = pd.to_datetime(row["Date"]).date()
                day_load[base.weekday() % 5] += 1
            except: pass
    day_names_en = ["ראשון","שני","שלישי","רביעי","חמישי"]
    fig.add_trace(go.Bar(
        x=day_names_en, y=[day_load[i] for i in range(5)],
        marker_color=["rgba(0,212,255,.7)"]*5,
        name="עומס"), row=2, col=1)

    # 4. Monthly 6-month trend
    months_data = []
    for m in range(6, 0, -1):
        dt = today - timedelta(days=30 * m)
        mdf = monthly_stats(dt.year, dt.month)
        if not mdf.empty:
            months_data.append({
                "חודש": f"{dt.month:02d}/{dt.year}",
                "ממוצע": round(mdf["אחוז"].mean())
            })
    if months_data:
        mtrend = pd.DataFrame(months_data)
        colors_mt = ["#2dd4a0" if v >= 80 else "#f97316" if v >= 50 else "#f43f5e"
                     for v in mtrend["ממוצע"]]
        fig.add_trace(go.Bar(
            x=mtrend["חודש"], y=mtrend["ממוצע"],
            marker_color=colors_mt, name="ממוצע חודשי",
            text=[f"{v}%" for v in mtrend["ממוצע"]],
            textposition="outside", textfont=dict(color="#e2eeff", size=10)), row=2, col=2)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Heebo", color="#e2eeff"), height=700,
        margin=dict(t=60, b=40, l=20, r=20),
        showlegend=False,
        yaxis=dict(gridcolor="rgba(255,255,255,.04)"),
        yaxis3=dict(gridcolor="rgba(255,255,255,.04)"),
        yaxis4=dict(gridcolor="rgba(255,255,255,.04)"),
    )
    for ann in fig.layout.annotations:
        ann.update(font=dict(color="#c9a84c", size=13, family="Orbitron"))
    st.plotly_chart(fig, use_container_width=True)

    # ── Priority heatmap ──
    st.markdown("---")
    sec_header("🔥 מפת חום — עדיפות × קטגוריה")
    heat_data = {}
    for _, row in df.iterrows():
        p = str(row.get("Priority","רגיל"))
        c = str(row.get("Category","כללי"))
        heat_data.setdefault(p, {})
        heat_data[p][c] = heat_data[p].get(c, 0) + 1

    heat_df = pd.DataFrame(heat_data).fillna(0).T
    heat_df = heat_df.reindex(columns=PRIS, fill_value=0)
    fig_heat = go.Figure(go.Heatmap(
        z=heat_df.values, x=heat_df.columns.tolist(),
        y=heat_df.index.tolist(),
        colorscale=[[0,"rgba(0,212,255,.05)"],[0.5,"rgba(0,212,255,.4)"],[1,"#c9a84c"]],
        text=heat_df.values, texttemplate="%{text}",
        textfont=dict(size=14, color="#e2eeff"), showscale=False))
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Heebo", color="#e2eeff"), height=300,
        margin=dict(t=10, b=10, l=80, r=20),
        xaxis=dict(side="top"), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_heat, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
check_timeout()

if not st.session_state.user_role:
    login_screen()
    st.stop()

role = st.session_state.user_role
lt   = st.session_state.login_time
elapsed_min = int((datetime.now() - lt).total_seconds() / 60) if lt else 0

# ── Sidebar ──
ROLE_ICONS = {"מנהל WMS": "🔑", "צוות מחסן": "📦", "הנהלה": "📊"}
df_side = st.session_state.tasks
today_side = len(tasks_for_date(df_side, datetime.now()))
ov_side    = len(get_overdue())

st.sidebar.markdown(f"""
<div style="padding:22px 0 14px;text-align:center;border-bottom:1px solid var(--rule);margin-bottom:14px">
  <div style="font-family:var(--serif);font-size:1.4rem;color:var(--gold-lt);letter-spacing:2px;margin-bottom:4px">
    {ROLE_ICONS.get(role,'·')} {role}
  </div>
  <div style="font-size:.68rem;color:var(--t3);letter-spacing:2px;text-transform:uppercase">
    מחובר {elapsed_min} דק'
  </div>
</div>
<div style="background:var(--raised);border:1px solid var(--rule);border-radius:var(--rad);
            padding:10px 14px;margin-bottom:16px;font-size:.75rem;font-family:var(--mono)">
  <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--rule)">
    <span style="color:var(--t3)">להיום</span>
    <span style="color:var(--gold-lt);font-weight:700">{today_side}</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--rule)">
    <span style="color:var(--t3)">פיגורים</span>
    <span style="color:{'var(--crimson)' if ov_side else 'var(--emerald)'};font-weight:700">{ov_side}</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding:4px 0">
    <span style="color:var(--t3)">סה"כ משימות</span>
    <span style="color:var(--t1);font-weight:700">{len(df_side)}</span>
  </div>
</div>
""", unsafe_allow_html=True)

MENUS = {
    "מנהל WMS":  ["📊 דשבורד","📋 סידור עבודה","📅 לוח שנה",
                  "📦 ספירות מלאי","➕ הוספת משימה","⚙️ ניהול משימות","🔬 אנליטיקס"],
    "הנהלה":     ["📊 דשבורד","📅 לוח שנה","📦 ספירות מלאי","🔬 אנליטיקס"],
    "צוות מחסן": ["📊 דשבורד","📋 סידור עבודה","📦 ספירות מלאי","📅 לוח שנה"],
}
choice = st.sidebar.radio("", MENUS[role], label_visibility="collapsed")

if elapsed_min >= 50:
    st.sidebar.markdown(
        f'<div class="alert alert-gold" style="font-size:.76rem;padding:8px 12px;margin:8px 0">'
        f'⚠ הסשן יפוג בעוד {60-elapsed_min} דק\'</div>',
        unsafe_allow_html=True)
if st.sidebar.button("התנתקות", use_container_width=True):
    st.session_state.user_role = None
    st.session_state.login_time = None
    st.rerun()

# ── Header Banner ──
PAGE_TITLES = {
    "📊 דשבורד":"דשבורד בקרה","📋 סידור עבודה":"סידור עבודה שבועי",
    "📅 לוח שנה":"לוח שנה","➕ הוספת משימה":"הוספת משימה חדשה",
    "⚙️ ניהול משימות":"ניהול ועריכת משימות",
    "📦 ספירות מלאי":"דשבורד ספירות מלאי",
    "🔬 אנליטיקס":"אנליטיקס מתקדם",
}
st.markdown(
    f'<div class="banner" style="padding:18px 32px;margin-bottom:20px">'
    f'<div class="banner-wordmark" style="font-size:1.3rem;letter-spacing:2px">'
    f'{PAGE_TITLES.get(choice, choice)}</div>'
    f'<div class="banner-sub"><span class="live-pip"></span>'
    f'{datetime.now().strftime("%d/%m/%Y %H:%M")} &nbsp;·&nbsp; {role}</div>'
    f'</div>', unsafe_allow_html=True)

# ── Route ──
if   choice == "📊 דשבורד":          page_dashboard()
elif choice == "📋 סידור עבודה":     page_work()
elif choice == "📅 לוח שנה":          page_calendar()
elif choice == "📦 ספירות מלאי":     page_inventory()
elif choice == "➕ הוספת משימה":     page_add()
elif choice == "⚙️ ניהול משימות":    page_manage()
elif choice == "🔬 אנליטיקס":        page_analytics()
