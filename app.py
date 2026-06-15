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
    import plotly.io as pio  # 🎯 1. הוספנו את הייבוא של ה-io של פלוטלי
    
    pio.templates.default = "plotly_dark"
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
    initial_sidebar_state="collapsed",
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
#  CSS — Industrial Dark + Neon
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  --bg0:     #020810;
  --bg1:     #040d1c;
  --bg2:     #071526;
  --card:    #0a1c35;
  --card2:   #0d2240;
  --card3:   #102850;
  --b0:      rgba(0,212,255,.08);
  --b1:      rgba(0,212,255,.2);
  --b2:      rgba(0,212,255,.45);
  --b3:      rgba(0,212,255,.7);
  --cyan:    #00d4ff;
  --green:   #00ff88;
  --red:     #ff2d55;
  --amber:   #ffb800;
  --purple:  #bf5af2;
  --txt:     #e2eeff;
  --txt2:    #6b8aaa;
  --txt3:    #3d5a75;
  --mono:    'JetBrains Mono', monospace;
  --orb:     'Orbitron', monospace;
  --heb:     'Heebo', sans-serif;
  --r:       14px;
  --r2:      20px;
  --shadow:  0 8px 32px rgba(0,0,0,.6);
  --glow-c:  0 0 30px rgba(0,212,255,.25);
  --glow-g:  0 0 30px rgba(0,255,136,.2);
  --glow-r:  0 0 30px rgba(255,45,85,.25);
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: var(--heb) !important;
  direction: rtl !important;
  text-align: right !important;
}

.stApp {
  background-color: var(--bg0) !important;
  background-image:
    linear-gradient(rgba(0,212,255,.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,212,255,.03) 1px, transparent 1px),
    radial-gradient(ellipse 100% 60% at 50% 0%, rgba(0,212,255,.07) 0%, transparent 65%),
    radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,255,136,.04) 0%, transparent 60%);
  background-size: 48px 48px, 48px 48px, 100% 100%, 100% 100%;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--bg1) 0%, var(--bg0) 100%) !important;
  border-left: 1px solid var(--b1) !important;
  box-shadow: 4px 0 40px rgba(0,0,0,.5) !important;
}
[data-testid="stSidebar"] * { color: var(--txt) !important; }
[data-testid="stSidebar"] .stRadio label {
  background: transparent !important;
  border: 1px solid transparent;
  border-radius: 10px;
  padding: 10px 14px;
  margin: 3px 0;
  transition: all .2s;
  display: block;
  font-weight: 600;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(0,212,255,.08) !important;
  border-color: var(--b2) !important;
  transform: translateX(-3px);
}

[data-testid="stMetric"] {
  background: var(--card) !important;
  padding: 22px 20px !important;
  border-radius: var(--r) !important;
  border: 1px solid var(--b1) !important;
  box-shadow: var(--shadow) !important;
  transition: all .25s !important;
  position: relative;
  overflow: hidden;
}
[data-testid="stMetric"]::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 100%; height: 2px;
  background: linear-gradient(90deg, var(--cyan), var(--green));
}
[data-testid="stMetric"]:hover {
  transform: translateY(-4px) !important;
  border-color: var(--b2) !important;
  box-shadow: var(--glow-c), var(--shadow) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--txt2) !important;
  font-size: .78rem !important;
  font-weight: 600 !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  color: var(--cyan) !important;
  font-family: var(--orb) !important;
  font-weight: 800 !important;
  font-size: 2.1rem !important;
  text-shadow: 0 0 20px rgba(0,212,255,.4);
}

.stButton > button {
  background: rgba(0,212,255,.08) !important;
  border: 1px solid var(--b2) !important;
  color: var(--cyan) !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-family: var(--heb) !important;
  transition: all .2s !important;
}
.stButton > button:hover {
  background: rgba(0,212,255,.18) !important;
  box-shadow: var(--glow-c) !important;
  transform: translateY(-1px);
}

[data-testid="stForm"] {
  background: var(--card) !important;
  border: 1px solid var(--b1) !important;
  border-radius: var(--r2) !important;
  padding: 28px !important;
}
[data-testid="stForm"] .stButton > button {
  background: linear-gradient(135deg, #0088cc, #005fa3) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 4px 20px rgba(0,136,204,.4) !important;
}
[data-testid="stForm"] .stButton > button:hover {
  background: linear-gradient(135deg, #00a8ff, #0077cc) !important;
  box-shadow: 0 6px 28px rgba(0,168,255,.5) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
  background: var(--bg2) !important;
  border: 1px solid var(--b1) !important;
  border-radius: 10px !important;
  color: var(--txt) !important;
  font-family: var(--heb) !important;
  transition: border-color .2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--b3) !important;
  box-shadow: 0 0 0 2px rgba(0,212,255,.12) !important;
}
label[data-testid="stWidgetLabel"] p { color: var(--txt) !important; font-weight: 600 !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg0); }
::-webkit-scrollbar-thumb { background: var(--b2); border-radius: 3px; }

div[data-testid="stPopover"] > button {
  width: 100% !important;
  min-height: 58px !important;
  margin-bottom: 6px !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  border: 1px solid var(--b1) !important;
  background: var(--card) !important;
  color: var(--txt) !important;
  text-align: right !important;
  transition: all .2s !important;
}
div[data-testid="stPopover"] > button:hover {
  border-color: var(--b2) !important;
  background: var(--card2) !important;
}

details > summary { color: var(--cyan) !important; font-weight: 700 !important; }
[data-testid="stExpander"] {
  background: var(--card) !important;
  border: 1px solid var(--b1) !important;
  border-radius: var(--r) !important;
}

[data-testid="stTabs"] [role="tab"] {
  color: var(--txt2) !important;
  font-weight: 700 !important;
  transition: all .2s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom: 2px solid var(--cyan) !important;
}

[data-testid="stDownloadButton"] > button {
  background: linear-gradient(135deg, rgba(0,255,136,.15), rgba(0,255,136,.05)) !important;
  border: 1px solid rgba(0,255,136,.4) !important;
  color: var(--green) !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: rgba(0,255,136,.25) !important;
  box-shadow: var(--glow-g) !important;
}

[data-testid="stDataFrame"] {
  border: 1px solid var(--b1) !important;
  border-radius: var(--r) !important;
}

/* ── CUSTOM COMPONENTS ── */

.mega-banner {
  background: linear-gradient(135deg, var(--card) 0%, var(--card2) 50%, var(--card) 100%);
  border: 1px solid var(--b2);
  border-radius: var(--r2);
  padding: 32px 40px;
  margin-bottom: 28px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: var(--glow-c), var(--shadow);
}
.mega-banner::before {
  content: '';
  position: absolute;
  top: -80px; left: 50%;
  transform: translateX(-50%);
  width: 400px; height: 160px;
  background: radial-gradient(ellipse, rgba(0,212,255,.15) 0%, transparent 70%);
  pointer-events: none;
}
.mega-banner::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--cyan), transparent);
}
.mega-banner h1 {
  font-family: var(--orb) !important;
  font-size: 2rem !important;
  font-weight: 900 !important;
  color: var(--cyan) !important;
  letter-spacing: 4px !important;
  margin: 0 0 8px !important;
  text-shadow: 0 0 40px rgba(0,212,255,.5) !important;
}
.mega-banner .sub {
  color: var(--txt2);
  font-size: .85rem;
  letter-spacing: 2px;
  text-transform: uppercase;
}
.mega-banner .live-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 12px var(--green);
  margin-left: 8px;
  animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:.5; transform:scale(.7); }
}

.kpi {
  background: var(--card);
  border: 1px solid var(--b1);
  border-radius: var(--r2);
  padding: 24px 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all .3s;
  cursor: default;
}
.kpi:hover { transform: translateY(-5px); border-color: var(--b2); }
.kpi::before {
  content: '';
  position: absolute;
  top: 0; right: 0; width: 100%; height: 3px;
}
.kpi-blue::before   { background: linear-gradient(90deg, var(--cyan), #005fa3); }
.kpi-green::before  { background: linear-gradient(90deg, var(--green), #005f35); }
.kpi-red::before    { background: linear-gradient(90deg, var(--red), #6b001e); }
.kpi-amber::before  { background: linear-gradient(90deg, var(--amber), #6b4a00); }
.kpi-purple::before { background: linear-gradient(90deg, var(--purple), #3d0070); }
.kpi:hover.kpi-blue  { box-shadow: var(--glow-c); }
.kpi:hover.kpi-green { box-shadow: var(--glow-g); }
.kpi:hover.kpi-red   { box-shadow: var(--glow-r); }
.kpi-icon {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
  filter: drop-shadow(0 0 12px currentColor);
}
.kpi-val {
  font-family: var(--orb);
  font-size: 2.8rem;
  font-weight: 900;
  line-height: 1;
  margin-bottom: 8px;
}
.kpi-lbl {
  font-size: .72rem;
  color: var(--txt2);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  font-weight: 600;
}
.kpi-sub {
  font-size: .75rem;
  margin-top: 6px;
  font-weight: 700;
  font-family: var(--mono);
}

.prog {
  background: rgba(255,255,255,.06);
  border-radius: 20px;
  height: 8px;
  overflow: hidden;
  margin: 6px 0;
  position: relative;
}
.prog::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,.06) 50%, transparent 100%);
  animation: shimmer 2s ease infinite;
}
@keyframes shimmer { 0%{transform:translateX(100%)} 100%{transform:translateX(-100%)} }
.pfill {
  height: 100%;
  border-radius: 20px;
  transition: width .8s cubic-bezier(.4,0,.2,1);
}

.tc {
  background: var(--card);
  border: 1px solid var(--b0);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 7px;
  border-right: 4px solid var(--cyan);
  transition: all .2s;
  position: relative;
  overflow: hidden;
}
.tc:hover { background: var(--card2); border-color: var(--b2); transform: translateX(-3px); }
.tc.done   { border-right-color: var(--green) !important; opacity: .65; }
.tc.urgent { border-right-color: var(--red)   !important; }
.tc.high   { border-right-color: var(--amber) !important; }

.b {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 20px;
  font-size: .67rem;
  font-weight: 800;
  margin: 1px;
  letter-spacing: .3px;
}
.b-blue   { background: rgba(0,212,255,.14);  color: #5dd8ff; border: 1px solid rgba(0,212,255,.25); }
.b-green  { background: rgba(0,255,136,.12);  color: #00ff88; border: 1px solid rgba(0,255,136,.2); }
.b-red    { background: rgba(255,45,85,.14);  color: #ff5577; border: 1px solid rgba(255,45,85,.25); }
.b-amber  { background: rgba(255,184,0,.14);  color: #ffd040; border: 1px solid rgba(255,184,0,.25); }
.b-purple { background: rgba(191,90,242,.14); color: #d070ff; border: 1px solid rgba(191,90,242,.25); }
.b-gray   { background: rgba(255,255,255,.07);color: var(--txt2); border: 1px solid var(--b1); }

.wchip {
  background: linear-gradient(135deg, var(--card), var(--card2));
  border: 1px solid var(--b2);
  border-radius: 12px;
  padding: 12px 8px;
  margin-bottom: 10px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: var(--glow-c);
}
.wchip .day-name {
  font-family: var(--orb);
  font-size: .72rem;
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 1px;
}
.wchip .day-date { font-size: .68rem; color: var(--txt2); font-family: var(--mono); margin-top: 2px; }
.wchip .day-count { font-size: .62rem; color: var(--green); font-weight: 700; margin-top: 4px; }

.al { border-radius: 12px; padding: 14px 18px; margin-bottom: 14px; font-size: .9rem; display: flex; align-items: flex-start; gap: 10px; }
.al-red    { background: rgba(255,45,85,.1);   border: 1px solid rgba(255,45,85,.4); }
.al-green  { background: rgba(0,255,136,.07);  border: 1px solid rgba(0,255,136,.25); }
.al-amber  { background: rgba(255,184,0,.08);  border: 1px solid rgba(255,184,0,.3); }
.al-cyan   { background: rgba(0,212,255,.07);  border: 1px solid rgba(0,212,255,.25); }

.stat-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--b0); }
.stat-row:last-child { border-bottom: none; }
.stat-label { color: var(--txt2); font-size: .82rem; flex: 1; }
.stat-val   { color: var(--txt);  font-size: .85rem; font-weight: 700; font-family: var(--mono); }

.sec-h {
  font-family: var(--orb);
  font-size: .85rem;
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin: 24px 0 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--b1);
  position: relative;
}
.sec-h::after {
  content: '';
  position: absolute;
  bottom: -1px; right: 0;
  width: 60px; height: 2px;
  background: var(--cyan);
  box-shadow: var(--glow-c);
}

.mm { background: var(--card); border: 1px solid var(--b1); border-radius: 10px; padding: 12px 14px; display: flex; align-items: center; gap: 12px; transition: all .2s; }
.mm:hover { border-color: var(--b2); transform: translateY(-2px); }
.mm-icon { font-size: 1.5rem; }
.mm-val  { font-family: var(--orb); font-size: 1.4rem; font-weight: 700; color: var(--cyan); }
.mm-lbl  { font-size: .72rem; color: var(--txt2); letter-spacing: .5px; }

.tl-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }

div[data-testid="stHorizontalBlock"] .stButton > button {
  min-height: 220px !important;
  height: 220px !important;
  width: 100% !important;
  border-radius: var(--r2) !important;
  font-size: 1.5rem !important;
  font-weight: 900 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: pre-wrap !important;
  text-align: center !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 4px solid var(--cyan) !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 4px solid var(--green) !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 4px solid var(--amber) !important; }

/* ── Hide header/footer/toolbar only ── */
header[data-testid="stHeader"],
#MainMenu, footer,
[data-testid="stToolbar"] { display: none !important; }

.main .block-container {
  padding-top: 0.5rem !important;
  max-width: 100% !important;
}

/* ── Sidebar dark styling ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #040d1c 0%, #020810 100%) !important;
  border-left: 1px solid rgba(0,212,255,.25) !important;
  box-shadow: 4px 0 32px rgba(0,0,0,.6) !important;
}
[data-testid="stSidebar"]::before {
  content: "";
  display: block;
  height: 3px;
  background: linear-gradient(90deg, transparent, #00d4ff, #00ff88, transparent);
  box-shadow: 0 0 12px #00d4ff;
}
[data-testid="stSidebar"] * { color: var(--txt) !important; }
[data-testid="stSidebar"] .stRadio label {
  padding: 11px 16px !important;
  margin: 3px 0 !important;
  border-radius: 12px !important;
  font-size: .9rem !important;
  font-weight: 600 !important;
  min-height: 44px !important;
  display: flex !important;
  align-items: center !important;
  cursor: pointer !important;
  transition: all .18s !important;
  border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(0,212,255,.1) !important;
  border-color: rgba(0,212,255,.2) !important;
  color: var(--cyan) !important;
}
[data-testid="stSidebar"] .stButton > button {
  border-radius: 10px !important;
  font-weight: 700 !important;
  transition: all .15s !important;
}
[data-testid="stSidebar"]::-webkit-scrollbar { width: 3px; }
[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
  background: rgba(0,212,255,.3); border-radius: 3px;
}
[data-testid="collapsedControl"] button {
  background: #040d1c !important;
  color: #00d4ff !important;
  border: 1px solid rgba(0,212,255,.4) !important;
  border-radius: 0 8px 8px 0 !important;
}
</style>
""", unsafe_allow_html=True)


import sqlite3, json

DB_PATH = "wms.db"

# ═══════════════════════════════════════════════════════════════════════════════
#  DATABASE LAYER — Supabase Client
# ═══════════════════════════════════════════════════════════════════════════════
def get_conn():
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def db_init():
    """הפונקציה קיימת לצורך תאימות, ב-Supabase הטבלאות מנוהלות ישירות דרך ה-Dashboard שלהם"""
    pass

# ── Tasks ──────────────────────────────────────────────────────────────────────
def db_load_tasks() -> pd.DataFrame:
    try:
        supabase = get_conn()
        res = supabase.table("tasks").select("*").order("id").execute()
        rows = res.data
    except Exception as e:
        st.error(f"שגיאה בטעינת משימות: {e}")
        rows = []
        
    if not rows:
        return pd.DataFrame(columns=[
            "ID","Task_Name","Description","Recurring","Date","Done_Dates","Priority","Category"])
            
    return pd.DataFrame([{
        "ID":          r.get("id"),
        "Task_Name":   r.get("task_name"),
        "Description": r.get("description", ""),
        "Recurring":   r.get("recurring", "לא"),
        "Date":        r.get("start_date"),
        "Done_Dates":  r.get("done_dates", ""),
        "Priority":    r.get("priority", "רגיל"),
        "Category":    r.get("category", "כללי"),
    } for r in rows])

def db_add_task(name, desc, recurring, start_date, priority, category):
    supabase = get_conn()
    data = {
        "task_name": name,
        "description": desc,
        "recurring": recurring,
        "start_date": str(start_date),
        "priority": priority,
        "category": category
    }
    res = supabase.table("tasks").insert(data).execute()
    return res.data[0]["id"] if res.data else None

def db_update_task(task_id, name, desc, recurring, start_date, priority, category):
    supabase = get_conn()
    data = {
        "task_name": name,
        "description": desc,
        "recurring": recurring,
        "start_date": str(start_date),
        "priority": priority,
        "category": category
    }
    supabase.table("tasks").update(data).eq("id", task_id).execute()

def db_delete_task(task_id):
    supabase = get_conn()
    supabase.table("tasks").delete().eq("id", task_id).execute()

def db_mark_done(task_id, done_dates_str):
    supabase = get_conn()
    supabase.table("tasks").update({"done_dates": done_dates_str}).eq("id", task_id).execute()

# ── Inventory ──────────────────────────────────────────────────────────────────
def db_load_inventory() -> list:
    try:
        supabase = get_conn()
        res = supabase.table("inventory").select("*").order("month", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        return []

def db_save_inventory(month, skus_total, skus_counted, locs_total, locs_counted, no_gap):
    supabase = get_conn()
    data = {
        "month": month,
        "skus_total": int(skus_total),
        "skus_counted": int(skus_counted),
        "locs_total": int(locs_total),
        "locs_counted": int(locs_counted),
        "no_gap": int(no_gap)
    }
    supabase.table("inventory").upsert(data, on_conflict="month").execute()

# ── Count Plan (תוכנית ספירה) ─────────────────────────────────────────────────
def db_load_count_plan(month) -> list:
    try:
        supabase = get_conn()
        res = (supabase.table("count_plan").select("*")
               .eq("month", month).order("sort_order").execute())
        return res.data if res.data else []
    except Exception:
        return []

def db_clear_count_plan(month):
    supabase = get_conn()
    supabase.table("count_plan").delete().eq("month", month).execute()

def db_bulk_insert_count_plan(rows: list):
    if not rows:
        return
    supabase = get_conn()
    for i in range(0, len(rows), 500):
        supabase.table("count_plan").insert(rows[i:i + 500]).execute()

# ── External Storage ────────────────────────────────────────────────────────────
def db_load_external_storage() -> list:
    try:
        supabase = get_conn()
        res = supabase.table("external_storage").select("*").order("id").execute()
        return res.data if res.data else []
    except Exception:
        return []

def db_add_external_storage(warehouse_name, location, pallets, contact_name, contact_phone):
    supabase = get_conn()
    data = {
        "warehouse_name": warehouse_name,
        "location":       location,
        "pallets":        int(pallets),
        "contact_name":   contact_name,
        "contact_phone":  contact_phone,
    }
    supabase.table("external_storage").insert(data).execute()

def db_update_external_storage(record_id, warehouse_name, location, pallets, contact_name, contact_phone):
    supabase = get_conn()
    data = {
        "warehouse_name": warehouse_name,
        "location":       location,
        "pallets":        int(pallets),
        "contact_name":   contact_name,
        "contact_phone":  contact_phone,
    }
    supabase.table("external_storage").update(data).eq("id", record_id).execute()

def db_delete_external_storage(record_id):
    supabase = get_conn()
    supabase.table("external_storage").delete().eq("id", record_id).execute()

# ── External Storage Excel ──────────────────────────────────────────────────────
def db_load_excel_table():
    """טוען את הטבלה השמורה מה-Supabase. מחזיר dict או None"""
    try:
        supabase = get_conn()
        res = supabase.table("external_storage_excel").select("*").order("id", desc=True).limit(1).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception:
        return None

def db_save_excel_table(file_name, table_data, uploaded_by):
    """שומר (מחליף) את טבלת האקסל ב-Supabase — רשומה אחת בלבד"""
    supabase = get_conn()
    try:
        supabase.table("external_storage_excel").delete().neq("id", 0).execute()
    except Exception:
        pass
    supabase.table("external_storage_excel").insert({
        "file_name":   file_name,
        "uploaded_by": uploaded_by,
        "table_data":  table_data,
    }).execute()

# ── Transfers Value (ערך העברות בין מחסנים) ──────────────────────────────────
def db_load_movements(month=None) -> list:
    """טוען תנועות. אם month מצוין — רק לאותו חודש."""
    try:
        supabase = get_conn()
        q = supabase.table("transfer_movements").select("*")
        if month:
            q = q.eq("month", month)
        res = q.order("id").execute()
        return res.data if res.data else []
    except Exception:
        return []

def db_movement_months() -> list:
    """רשימת החודשים שיש להם נתונים, מהחדש לישן."""
    try:
        supabase = get_conn()
        res = supabase.table("transfer_movements").select("month").execute()
        return sorted({r["month"] for r in (res.data or []) if r.get("month")}, reverse=True)
    except Exception:
        return []

def db_clear_movements(month):
    supabase = get_conn()
    supabase.table("transfer_movements").delete().eq("month", month).execute()

def db_bulk_insert_movements(rows: list):
    if not rows:
        return
    supabase = get_conn()
    for i in range(0, len(rows), 500):
        supabase.table("transfer_movements").insert(rows[i:i + 500]).execute()

def db_load_turnover(month) -> float:
    try:
        supabase = get_conn()
        res = supabase.table("monthly_turnover").select("*").eq("month", month).limit(1).execute()
        return float(res.data[0]["turnover"]) if res.data else 0.0
    except Exception:
        return 0.0

def db_save_turnover(month, turnover):
    supabase = get_conn()
    supabase.table("monthly_turnover").upsert(
        {"month": month, "turnover": float(turnover)}, on_conflict="month").execute()

def db_load_hidden_routes() -> set:
    """מחזיר קבוצת מסלולים מוסתרים {(from_wh, to_wh)}."""
    try:
        supabase = get_conn()
        res = supabase.table("hidden_routes").select("*").execute()
        return {(r.get("from_wh") or "", r.get("to_wh") or "") for r in (res.data or [])}
    except Exception:
        return set()

def db_add_hidden_route(from_wh, to_wh):
    supabase = get_conn()
    supabase.table("hidden_routes").insert({"from_wh": from_wh, "to_wh": to_wh}).execute()

def db_remove_hidden_route(from_wh, to_wh):
    supabase = get_conn()
    supabase.table("hidden_routes").delete().eq("from_wh", from_wh).eq("to_wh", to_wh).execute()

def db_load_month_summary(month) -> dict:
    """טוען מחזור + ערכי סיכום ידניים לחודש."""
    out = {"turnover": 0.0, "destructions": None, "returns": None,
           "goods_value": 0.0, "goods_dir": "הופחת"}
    try:
        supabase = get_conn()
        res = supabase.table("monthly_turnover").select("*").eq("month", month).limit(1).execute()
        if res.data:
            d = res.data[0]
            out["turnover"]    = float(d.get("turnover") or 0)
            out["destructions"] = (None if d.get("manual_destructions") is None
                                   else float(d.get("manual_destructions")))
            out["returns"]      = (None if d.get("manual_returns") is None
                                   else float(d.get("manual_returns")))
            out["goods_value"]  = float(d.get("goods_value") or 0)
            out["goods_dir"]    = d.get("goods_dir") or "הופחת"
    except Exception:
        pass
    return out

def db_save_month_summary(month, turnover, destructions, returns, goods_value, goods_dir):
    supabase = get_conn()
    supabase.table("monthly_turnover").upsert({
        "month": month,
        "turnover": float(turnover or 0),
        "manual_destructions": None if destructions is None else float(destructions),
        "manual_returns":      None if returns is None else float(returns),
        "goods_value": float(goods_value or 0),
        "goods_dir": goods_dir,
    }, on_conflict="month").execute()

# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def init_state():
    if "user_role"  not in st.session_state: st.session_state.user_role  = None
    if "login_time" not in st.session_state: st.session_state.login_time = None
    if "theme"      not in st.session_state: st.session_state.theme      = "dark"
    if "page"       not in st.session_state: st.session_state.page       = "📊 דשבורד"

init_state()


# ── Dynamic theme CSS — pure CSS injection, no JS needed ───────────────────────
def inject_theme():
    if st.session_state.get("theme", "dark") != "light":
        return  # dark is the default static CSS — nothing to inject
    st.markdown("""<style>
:root {
  --bg0:    #f0f4f8;
  --bg1:    #e4eaf2;
  --bg2:    #d8e2ee;
  --card:   #ffffff;
  --card2:  #f5f8fc;
  --card3:  #eaf0f8;
  --b0:     rgba(0,100,180,.07);
  --b1:     rgba(0,100,180,.18);
  --b2:     rgba(0,100,180,.38);
  --b3:     rgba(0,100,180,.6);
  --cyan:   #0070c0;
  --green:  #007a45;
  --red:    #cc0022;
  --amber:  #a06000;
  --purple: #7722bb;
  --txt:    #0d1e33;
  --txt2:   #456080;
  --txt3:   #8aaac5;
  --shadow: 0 4px 20px rgba(0,60,120,.10);
  --glow-c: 0 0 16px rgba(0,112,192,.15);
  --glow-g: 0 0 16px rgba(0,122,69,.12);
  --glow-r: 0 0 16px rgba(204,0,34,.12);
}
.stApp {
  background-color: #f0f4f8 !important;
  background-image:
    linear-gradient(rgba(0,100,180,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,100,180,.04) 1px, transparent 1px),
    radial-gradient(ellipse 100% 60% at 50% 0%, rgba(0,100,180,.06) 0%, transparent 65%) !important;
  background-size: 48px 48px, 48px 48px, 100% 100% !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#e4eaf2 0%,#f0f4f8 100%) !important;
  border-left: 1px solid rgba(0,100,180,.2) !important;
  box-shadow: 4px 0 24px rgba(0,60,120,.08) !important;
}
[data-testid="stSidebar"] * { color: #0d1e33 !important; }
[data-testid="stSidebar"] .stRadio label:hover { background: rgba(0,100,180,.08) !important; }
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div,
.stNumberInput>div>div>input,
.stDateInput>div>div>input {
  background: #ffffff !important;
  border-color: rgba(0,100,180,.25) !important;
  color: #0d1e33 !important;
}
label[data-testid="stWidgetLabel"] p { color: #0d1e33 !important; }
[data-testid="stMetric"] { background:#ffffff !important; border-color:rgba(0,100,180,.18) !important; box-shadow:0 4px 16px rgba(0,60,120,.1) !important; }
[data-testid="stMetricValue"] { color:#0070c0 !important; text-shadow:none !important; }
[data-testid="stMetricLabel"] { color:#456080 !important; }
[data-testid="stForm"] { background:#ffffff !important; border-color:rgba(0,100,180,.18) !important; }
[data-testid="stForm"] .stButton>button { background:linear-gradient(135deg,#0070c0,#004f99) !important; }
.stButton>button { background:rgba(0,100,180,.08) !important; border-color:rgba(0,100,180,.3) !important; color:#0070c0 !important; }
.stButton>button:hover { background:rgba(0,100,180,.16) !important; }
[data-testid="stExpander"] { background:#ffffff !important; border-color:rgba(0,100,180,.18) !important; }
details>summary { color:#0070c0 !important; }
[data-testid="stTabs"] [role="tab"] { color:#456080 !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color:#0070c0 !important; border-bottom-color:#0070c0 !important; }
[data-testid="stDownloadButton"]>button { background:rgba(0,122,69,.1) !important; border-color:rgba(0,122,69,.3) !important; color:#007a45 !important; }
[data-testid="stDataFrame"] { border-color:rgba(0,100,180,.18) !important; }
.kpi { background:#ffffff !important; border-color:rgba(0,100,180,.18) !important; }
div[data-testid="stPopover"]>button { background:#ffffff !important; border-color:rgba(0,100,180,.2) !important; color:#0d1e33 !important; }
.mega-banner { background:linear-gradient(135deg,#ffffff 0%,#eef4ff 50%,#ffffff 100%) !important; border-color:rgba(0,100,180,.25) !important; box-shadow:0 4px 24px rgba(0,60,120,.1) !important; }
.mega-banner h1 { color:#0070c0 !important; text-shadow:none !important; }
.mega-banner .sub { color:#456080 !important; }
::-webkit-scrollbar-track { background:#e4eaf2 !important; }
::-webkit-scrollbar-thumb { background:rgba(0,100,180,.3) !important; }
.tc { background:#ffffff !important; border-color:rgba(0,100,180,.15) !important; }
.mm { background:#ffffff !important; border-color:rgba(0,100,180,.15) !important; }
.sec-h { color:#456080 !important; border-bottom-color:rgba(0,100,180,.2) !important; }
</style>""", unsafe_allow_html=True)


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

def mark_done(task_id, dstr):
    df = db_load_tasks()
    row = df[df["ID"] == task_id]
    if row.empty: return
    existing = [x for x in str(row.iloc[0]["Done_Dates"]).split(",") if x]
    if dstr not in existing:
        existing.append(dstr)
    db_mark_done(task_id, ",".join(existing))

def get_overdue(days=7):
    df = db_load_tasks()
    today = datetime.now().date()
    out = []
    for i in range(1, days + 1):
        d = today - timedelta(days=i)
        for t in tasks_for_date(df, d):
            if not t["is_done"]: out.append(t)
    return out

def week_stats(days=14):
    df = db_load_tasks()
    today = datetime.now().date()
    rows = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        ts = tasks_for_date(df, d)
        tot = len(ts); don = sum(1 for t in ts if t["is_done"])
        rows.append({
            "date": d, "תאריך": d.strftime("%d/%m"),
            "בוצע": don, "מתוכנן": tot,
            "אחוז": round(don / tot * 100) if tot else 0
        })
    return pd.DataFrame(rows)

def monthly_stats(year, month):
    df = db_load_tasks()
    _, nd = cal_lib.monthrange(year, month)
    rows = []
    for day in range(1, nd + 1):
        d = datetime(year, month, day).date()
        ts = tasks_for_date(df, d)
        if ts:
            don = sum(1 for t in ts if t["is_done"])
            rows.append({"יום": day, "בוצע": don, "מתוכנן": len(ts),
                         "אחוז": round(don / len(ts) * 100)})
    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def pbar(pct, color=None, height=8):
    c = color or ("#00ff88" if pct >= 80 else "#ffb800" if pct >= 50 else "#ff2d55")
    glow = f"0 0 10px {c}66"
    return (f'<div class="prog" style="height:{height}px">'
            f'<div class="pfill" style="width:{min(pct,100)}%;background:{c};box-shadow:{glow}"></div>'
            f'</div>')

def badge(text, kind="blue"):
    return f'<span class="b b-{kind}">{text}</span>'

def pri_badge(p):
    return badge(p, {"דחוף":"red","גבוה":"amber","רגיל":"blue","נמוך":"gray"}.get(p,"blue"))

def cat_badge(c):
    return badge(c, {"בטיחות":"red","ספירה":"blue","תחזוקה":"amber",
                     "לוגיסטיקה":"purple","ניקיון":"green","כללי":"gray"}.get(c,"gray"))

def task_card_html(t):
    cls = "tc" + (" done" if t["is_done"] else
                  " urgent" if t["priority"] == "דחוף" else
                  " high"   if t["priority"] == "גבוה" else "")
    icon = "✅" if t["is_done"] else ("🚨" if t["priority"] == "דחוף" else "⏳")
    rec  = f' {badge(t["rec"],"gray")}' if t.get("rec") else ""
    desc = (f'<div style="color:var(--txt2);font-size:.78rem;margin-top:5px;'
            f'font-family:var(--mono)">{t["desc"]}</div>') if t.get("desc") else ""
    return (f'<div class="{cls}">'
            f'{icon} <b style="font-size:.95rem">{t["name"]}</b>'
            f' {pri_badge(t["priority"])} {cat_badge(t["category"])}{rec}'
            f'{desc}</div>')

def kpi_card(val, label, sub="", color="var(--cyan)", icon="📊", kind="blue"):
    glow = {"blue":"var(--glow-c)","green":"var(--glow-g)","red":"var(--glow-r)"}.get(kind,"")
    return (f'<div class="kpi kpi-{kind}" style="box-shadow:{glow}">'
            f'<span class="kpi-icon" style="color:{color}">{icon}</span>'
            f'<div class="kpi-val" style="color:{color};text-shadow:0 0 20px {color}66">{val}</div>'
            f'<div class="kpi-lbl">{label}</div>'
            f'{"<div class=kpi-sub style=color:"+color+";opacity:.7>"+sub+"</div>" if sub else ""}'
            f'</div>')

def sec_header(title):
    st.markdown(f'<div class="sec-h">{title}</div>', unsafe_allow_html=True)


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
    <div class="mega-banner">
      <h1>⬡ אחים כהן · WMS ⬡</h1>
      <div class="sub">
        <span class="live-dot"></span>
        מערכת ניהול מחסן מתקדמת
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.popover("🔑\nמנהל WMS", use_container_width=True):
            st.markdown("#### 🔐 כניסת מנהל מערכת")
            st.markdown('<div style="color:var(--txt2);font-size:.82rem;margin-bottom:12px">גישה מלאה לכל מודולי המערכת</div>', unsafe_allow_html=True)
            pwd = st.text_input("סיסמה", type="password", key="lpwd")
            if st.button("🚀 כניסה למערכת", use_container_width=True):
                if hashlib.sha256(pwd.encode()).hexdigest() == ADMIN_HASH:
                    st.session_state.user_role = "מנהל WMS"
                    st.session_state.login_time = datetime.now()
                    st.rerun()
                else:
                    st.error("❌ סיסמה שגויה")
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
    df = db_load_tasks()
    inv_count = len(db_load_inventory())
    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi_card(len(df), "משימות במערכת", icon="📋", kind="blue"), unsafe_allow_html=True)
    c2.markdown(kpi_card(len(get_overdue()), "פיגורים", icon="⚠️", kind="red", color="var(--red)"), unsafe_allow_html=True)
    c3.markdown(kpi_card(inv_count, "חודשי ספירה", icon="📦", kind="blue"), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    df = db_load_tasks()
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    # ── Overdue Alert ──
    overdue = get_overdue()
    if overdue:
        st.markdown(
            f'<div class="al al-red">🚨 <div><b style="color:var(--red);font-size:1rem">'
            f'{len(overdue)} משימות שלא בוצעו בשבוע האחרון</b>'
            f'<div style="color:var(--txt2);font-size:.8rem;margin-top:2px">'
            f'לחץ להצגה וסגירה</div></div></div>',
            unsafe_allow_html=True)
        with st.expander("📋 פירוט פיגורים וסגירתם"):
            for t in overdue:
                c1, c2 = st.columns([5, 1])
                c1.markdown(task_card_html(t), unsafe_allow_html=True)
                if c2.button("✓", key=f"ov_{t['id']}_{t['date']}"):
                    mark_done(t["id"], t["date"]); st.rerun()

    # ── Date selector ──
    dc, _ = st.columns([1, 3])
    sel = dc.date_input("📅 תאריך", today)
    dstr = sel.strftime("%Y-%m-%d")

    ts = tasks_for_date(df, sel)
    tot = len(ts); don = sum(1 for t in ts if t["is_done"])
    pct = round(don / tot * 100) if tot else 0
    pct_color = "#00ff88" if pct >= 80 else "#ffb800" if pct >= 50 else "#ff2d55"
    lbl = "היום" if sel == today.date() else sel.strftime("%d/%m")

    # ── Big KPI row ──
    k1, k2, k3, k4, k5 = st.columns(5)
    pct_color = "#00ff88" if pct >= 80 else "#ffb800" if pct >= 50 else "#ff2d55"
    k1.markdown(kpi_card(tot,     f"משימות {lbl}", icon="📋", kind="blue"), unsafe_allow_html=True)
    k2.markdown(kpi_card(don,     "בוצעו",         icon="✅", kind="green", color="var(--green)"), unsafe_allow_html=True)
    k3.markdown(kpi_card(tot-don, "נותרו",          icon="⏳",
                         kind="red" if tot-don > 3 else "blue",
                         color="var(--red)" if tot-don > 3 else "var(--cyan)"), unsafe_allow_html=True)
    k4.markdown(kpi_card(f"{pct}%","ביצוע",
                         sub=f"{'🔥 מצוין' if pct>=80 else '⚠️ בינוני' if pct>=50 else '❌ נמוך'}",
                         icon="📈", kind="green" if pct>=80 else "red", color=pct_color), unsafe_allow_html=True)
    k5.markdown(kpi_card(len(overdue),"פיגורים",   icon="🚨", kind="red",  color="var(--red)"), unsafe_allow_html=True)

    st.markdown(f'<div style="margin:8px 0 20px">{pbar(pct, pct_color, 10)}</div>', unsafe_allow_html=True)

    # ── Main content: tasks list + charts side by side ──
    col_l, col_r = st.columns([5, 4])

    with col_l:
        sec_header(f"📋 משימות ל-{lbl}")
        if ts:
            by_cat = {}
            for t in sorted(ts, key=lambda x: (x["is_done"], x["priority"] != "דחוף")):
                by_cat.setdefault(t["category"], []).append(t)
            for cat, cat_tasks in by_cat.items():
                don_c = sum(1 for t in cat_tasks if t["is_done"])
                p = round(don_c / len(cat_tasks) * 100)
                st.markdown(f'<div style="margin:14px 0 6px;display:flex;align-items:center;gap:8px">'
                            f'{cat_badge(cat)} '
                            f'<span style="color:var(--txt2);font-size:.75rem">{don_c}/{len(cat_tasks)}</span>'
                            f'{pbar(p)}</div>', unsafe_allow_html=True)
                for t in cat_tasks:
                    ca, cb = st.columns([7, 1])
                    ca.markdown(task_card_html(t), unsafe_allow_html=True)
                    if not t["is_done"] and cb.button("✓", key=f"d_{t['id']}_{dstr}_{cat}"):
                        mark_done(t["id"], dstr); st.rerun()
        else:
            st.markdown('<div class="al al-cyan">ℹ️ <b>אין משימות לתאריך זה</b></div>', unsafe_allow_html=True)

    with col_r:
        sec_header("📊 מבט מהיר")

        if HAS_PLOTLY and ts:
            cat_done = {}; cat_tot = {}
            for t in ts:
                c = t["category"]
                cat_tot[c] = cat_tot.get(c, 0) + 1
                if t["is_done"]: cat_done[c] = cat_done.get(c, 0) + 1
            cat_names = list(cat_tot.keys())
            cat_vals  = [cat_tot[c] for c in cat_names]
            CMAP = {"בטיחות":"#ff2d55","ספירה":"#c9a84c","תחזוקה":"#ffb800",
                    "לוגיסטיקה":"#c084fc","ניקיון":"#00ff88","כללי":"#8899aa"}
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

        st.markdown("**עדיפות:**")
        for pri, clr in [("דחוף","#ff2d55"),("גבוה","#ffb800"),("רגיל","#c9a84c"),("נמוך","#8899aa")]:
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
                colors_m = ["#00ff88" if v >= 80 else "#ffb800" if v >= 50 else "#ff2d55"
                            for v in mdf["אחוז"]]
                fig_m = go.Figure()
                fig_m.add_trace(go.Bar(
                    x=mdf["יום"], y=mdf["אחוז"],
                    marker_color=colors_m,
                    text=[f"{v}%" for v in mdf["אחוז"]],
                    textposition="outside",
                    textfont=dict(size=9, color="#e2eeff")
                ))
                fig_m.add_hline(
                    y=85, line_dash="dot", line_color="rgba(0,255,136,.4)",
                    annotation_text="יעד 85%",
                    annotation_font_color="#00ff88",
                    annotation_font_size=11
                )
                fig_m.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Heebo", color="#e2eeff"), height=300,
                    margin=dict(t=30, b=30, l=0, r=0), showlegend=False,
                    yaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,.04)"),
                    xaxis=dict(gridcolor="rgba(255,255,255,.03)")
                )
                st.plotly_chart(fig_m, use_container_width=True)

            with c_heat:
                cat_day_data = {}
                for _, row in mdf.iterrows():
                    cat_day_data[int(row["יום"])] = row["אחוז"]
                fig_c = go.Figure(go.Bar(
                    x=list(cat_day_data.keys()),
                    y=list(cat_day_data.values()),
                    marker_color=["#00ff88" if v >= 80 else "#ffb800" if v >= 50 else "#ff2d55"
                                  for v in cat_day_data.values()],
                    name="אחוז יומי"))
                fig_c.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Heebo", color="#e2eeff"), height=300,
                    margin=dict(t=30, b=30, l=0, r=0), showlegend=False,
                    yaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,.04)"),
                    xaxis=dict(gridcolor="rgba(255,255,255,.03)"))
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
        st.markdown('<div class="al al-amber">⚠️ <b>אין נתוני משימות לחודש הנבחר</b></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: WORK ORDER — weekly board
# ═══════════════════════════════════════════════════════════════════════════════
def page_work():
    df = db_load_tasks()
    today = datetime.now()

    curr_day_idx = int(today.strftime('%w'))
    start = today - timedelta(days=curr_day_idx)

    day_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)

    for i, name in enumerate(day_names):
        curr = start + timedelta(days=i)
        ts = tasks_for_date(df, curr)
        don = sum(1 for t in ts if t["is_done"])
        pct = round(don / len(ts) * 100) if ts else 0
        is_today = curr.date() == today.date()
        pct_color = "#00ff88" if pct >= 80 else "#ffb800" if pct >= 50 else "#ff2d55"

        with cols[i]:
            border_color = "var(--cyan)" if is_today else "var(--b2)"
            bg = "rgba(0,212,255,.05)" if is_today else "transparent"
            st.markdown(f"""
            <div class="wchip" style="border-color:{border_color};background:linear-gradient(135deg,var(--card),{bg})">
              {'<span style="color:var(--amber);font-size:.6rem;font-family:var(--mono)">▸ היום ◂</span><br>' if is_today else ""}
              <div class="day-name">{name}</div>
              <div class="day-date">{curr.strftime('%d/%m/%y')}</div>
              <div class="day-count">{don}/{len(ts)} ✓</div>
            </div>
            {pbar(pct, pct_color, 5)}
            """, unsafe_allow_html=True)

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
                            mark_done(t["id"], curr.strftime("%Y-%m-%d"))
                            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════
def page_calendar():
    df = db_load_tasks()
    today = datetime.now().date()
    events = []

    for _, row in df.iterrows():
        base = pd.to_datetime(row["Date"]).date()
        for i in range(180):
            d = base + timedelta(days=i)
            if is_scheduled(base, row["Recurring"], d):
                done = d.strftime("%Y-%m-%d") in str(row["Done_Dates"])
                CMAP = {"בטיחות":"#ff2d55","ספירה":"#c9a84c","תחזוקה":"#ffb800",
                        "לוגיסטיקה":"#c084fc","ניקיון":"#00ff88","כללי":"#8899aa"}
                base_color = CMAP.get(str(row.get("Category","")), "#388bfd")
                color = "#00ff88" if done else ("#ff2d55" if d < today else base_color)
                events.append({
                    "title": f"{'✅ ' if done else ''}{row['Task_Name']}",
                    "start": d.strftime("%Y-%m-%d"),
                    "color": color,
                    "allDay": True,
                })

    CATS_COLORS = [("בטיחות","#ff2d55"),("ספירה","#c9a84c"),("תחזוקה","#ffb800"),
                   ("לוגיסטיקה","#c084fc"),("ניקיון","#00ff88"),("כללי","#8899aa")]
    legend_html = " &nbsp; ".join(
        f'<span style="color:{c}">⬤</span> <span style="color:var(--txt2);font-size:.78rem">{n}</span>'
        for n, c in CATS_COLORS)
    st.markdown(
        f'<div style="margin-bottom:12px;padding:10px 16px;background:var(--card);'
        f'border:1px solid var(--b1);border-radius:10px">'
        f'{legend_html} &nbsp;&nbsp; '
        f'<span style="color:#00ff88">⬤</span> <span style="color:var(--txt2);font-size:.78rem">בוצע</span> &nbsp; '
        f'<span style="color:#ff2d55">⬤</span> <span style="color:var(--txt2);font-size:.78rem">מפוגר</span>'
        f'</div>',
        unsafe_allow_html=True)

    st.markdown(f'<div style="color:var(--txt2);font-size:.8rem;margin-bottom:12px;font-family:var(--mono)">'
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
    df = db_load_tasks()

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
        f'<span style="color:var(--txt2);font-size:.82rem;font-family:var(--mono)">'
        f'◈ {len(filt)} / {len(df)} משימות</span>'
        f'<div style="flex:1">{pbar(round(len(filt)/max(len(df),1)*100), height=4)}</div>'
        f'</div>', unsafe_allow_html=True)

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
                f'{"<div style=color:var(--txt2);font-size:.78rem;margin-top:4px;font-family:var(--mono)>"+str(row.get("Description",""))+"</div>" if row.get("Description") else ""}'
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
                        db_update_task(int(row["ID"]), nn, nd, nr, nd2.strftime("%Y-%m-%d"), np, nc)
                        st.rerun()

            with cd:
                ck = f"cfm_{row['ID']}"
                if not st.session_state.get(ck):
                    if st.button("🗑️", key=f"dl{row['ID']}", help="מחק משימה"):
                        st.session_state[ck] = True; st.rerun()
                else:
                    st.warning("בטוח?")
                    if st.button("כן", key=f"cy{row['ID']}"):
                        db_delete_task(int(row["ID"]))
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
                        f'{"<br><span style=color:var(--txt2);font-size:.78rem>"+str(row.get("Description",""))+"</span>" if row.get("Description") else ""}'
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
                    db_add_task(name.strip(), desc, freq, sdate.strftime("%Y-%m-%d"), pri, cat)
                    st.success(f"✅ משימה '{name}' נוספה בהצלחה!")
                    st.rerun()

    with c_preview:
        sec_header("📊 סטטיסטיקת משימות")
        df = db_load_tasks()
        total = len(df)

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

    inventory = db_load_inventory()

    today = datetime.now()
    month_options = []
    for i in range(12):
        dt = today - timedelta(days=30 * i)
        month_options.append(f"{dt.year}-{dt.month:02d}")
    month_options = list(dict.fromkeys(month_options))

    col_sel, col_new = st.columns([2, 3])
    sel_month = col_sel.selectbox(
        "📅 בחר חודש לצפייה / עריכה",
        month_options,
        format_func=lambda x: f"{MONTHS_HE[int(x.split('-')[1])-1]} {x.split('-')[0]}"
    )

    rec = next((r for r in inventory if r["month"] == sel_month), None)
    if rec is None:
        rec = {"month": sel_month,
               "skus_total": 0, "skus_counted": 0,
               "locs_total": 0, "locs_counted": 0, "no_gap": 0}

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
                    db_save_inventory(sel_month, skus_total, skus_counted,
                                      locs_total, locs_counted, no_gap)
                    st.success("✅ נתונים נשמרו!")
                    st.rerun()

    rec = next((r for r in db_load_inventory() if r["month"] == sel_month), rec)

    st.markdown("---")

    skus_t = max(int(rec["skus_total"]),   1)
    skus_c = int(rec["skus_counted"])
    locs_t = max(int(rec["locs_total"]),   1)
    locs_c = int(rec["locs_counted"])
    no_gap = int(rec["no_gap"])

    pct_skus = round(skus_c / skus_t * 100)
    pct_locs = round(locs_c / locs_t * 100)
    pct_acc  = round(no_gap / max(locs_c, 1) * 100)

    color_skus = "#00ff88" if pct_skus >= 90 else "#ffb800" if pct_skus >= 70 else "#ff2d55"
    color_locs = "#c9a84c" if pct_locs >= 90 else "#ffb800" if pct_locs >= 70 else "#ff2d55"
    color_acc  = "#c084fc" if pct_acc  >= 98 else "#ffb800" if pct_acc  >= 90 else "#ff2d55"

    k1, k2, k3 = st.columns(3)
    k1.markdown(kpi_card(f"{pct_skus}%", 'ספירת איתורים',
                         sub=f'{skus_c:,} / {skus_t:,} מק"טים',
                         color=color_skus, icon="🏷️", kind="blue"), unsafe_allow_html=True)
    k1.markdown(pbar(pct_skus, color_skus, 10), unsafe_allow_html=True)

    k2.markdown(kpi_card(f"{pct_locs}%", 'ספירת מק"טים',
                         sub=f'{locs_c:,} / {locs_t:,} איתורים',
                         color=color_locs, icon="📍", kind="blue"), unsafe_allow_html=True)
    k2.markdown(pbar(pct_locs, color_locs, 10), unsafe_allow_html=True)

    k3.markdown(kpi_card(f"{pct_acc}%", "דיוק ספירה",
                         sub=f'{no_gap:,} ללא פער מתוך {locs_c:,}',
                         color=color_acc, icon="🎯", kind="blue"), unsafe_allow_html=True)
    k3.markdown(pbar(pct_acc, color_acc, 10), unsafe_allow_html=True)

    st.markdown("---")

    left_col, right_col = st.columns([3, 4])

    with left_col:
        sec_header("📊 פירוט מספרי")

        def detail_row(label, val, total, color):
            pct = round(val / max(total, 1) * 100)
            remaining = total - val
            status = "✅ הושלם" if pct >= 100 else f"⏳ נותרו {remaining:,}"
            st.markdown(
                f'<div style="background:var(--card2);border:1px solid var(--b1);'
                f'border-radius:12px;padding:16px 18px;margin-bottom:12px;'
                f'border-right:4px solid {color}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
                f'<span style="font-weight:700;font-size:.95rem;color:var(--txt)">{label}</span>'
                f'<span style="font-family:var(--mono);font-size:.8rem;color:var(--txt2)">{status}</span>'
                f'</div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:8px">'
                f'<span style="font-family:var(--orb);font-size:1.8rem;font-weight:800;color:{color}'
                f';text-shadow:0 0 16px {color}66">{pct}%</span>'
                f'<div style="text-align:left">'
                f'<div style="font-size:.72rem;color:var(--txt2)">נספרו</div>'
                f'<div style="font-family:var(--mono);font-size:1rem;color:{color};font-weight:700">{val:,}</div>'
                f'</div>'
                f'<div style="text-align:left">'
                f'<div style="font-size:.72rem;color:var(--txt2)">סה"כ</div>'
                f'<div style="font-family:var(--mono);font-size:1rem;color:var(--txt);font-weight:700">{total:,}</div>'
                f'</div>'
                f'</div>'
                f'{pbar(pct, color, 8)}'
                f'</div>',
                unsafe_allow_html=True)

        detail_row('איתורים שנספרו', skus_c, skus_t, color_skus)
        detail_row('מק"טים שנספרו', locs_c, locs_t, color_locs)
        detail_row("איתורים ללא פער", no_gap, locs_c, color_acc)

        gap_count = locs_c - no_gap
        gap_pct   = round(gap_count / max(locs_c, 1) * 100)
        gap_color = "#ff2d55" if gap_pct > 10 else "#ffb800" if gap_pct > 5 else "#00ff88"
        st.markdown(
            f'<div style="background:var(--card2);border:1px solid rgba(255,45,85,.3);'
            f'border-radius:12px;padding:14px 18px;border-right:4px solid {gap_color}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<span style="font-weight:700;color:var(--txt)">⚡ איתורים עם פער</span>'
            f'<span style="font-family:var(--orb);font-size:1.5rem;color:{gap_color};font-weight:800">'
            f'{gap_count:,}</span>'
            f'</div>'
            f'<div style="color:var(--txt2);font-size:.78rem;margin-top:4px">'
            f'{gap_pct}% מהאיתורים שנספרו — '
            f'{"⚠️ גבוה" if gap_pct > 10 else "⚡ בינוני" if gap_pct > 5 else "✅ תקין"}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True)

    with right_col:
        if HAS_PLOTLY:
            sec_header("🎯 גרפי ביצוע")

            fig = make_subplots(rows=1, cols=3,
                specs=[[{"type":"pie"},{"type":"pie"},{"type":"pie"}]],
                subplot_titles=["מק\"טים","איתורים","דיוק"])

            for col_idx, (val, total, color, label) in enumerate([
                (skus_c, skus_t, color_skus, "איתורים"),
                (locs_c, locs_t, color_locs, "מק\"טים"),
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

            fig2 = go.Figure()
            cats_bar = ["מק\"טים", "איתורים"]
            counted  = [skus_c, locs_c]
            remaining= [skus_t - skus_c, locs_t - locs_c]
            fig2.add_trace(go.Bar(
                name="נספרו", x=cats_bar, y=counted,
                marker_color=["#00ff88", "#c9a84c"],
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

    if len(db_load_inventory()) >= 2 and HAS_PLOTLY:
        st.markdown("---")
        sec_header("📈 מגמה היסטורית")
        hist = sorted(db_load_inventory(), key=lambda x: x["month"])
        hdf = pd.DataFrame([{
            "חודש":      f"{MONTHS_HE[int(r['month'].split('-')[1])-1]} {r['month'].split('-')[0]}",
            "מק\"טים %": round(int(r["skus_counted"]) / max(int(r["skus_total"]), 1) * 100),
            "איתורים %": round(int(r["locs_counted"]) / max(int(r["locs_total"]), 1) * 100),
            "דיוק %":    round(int(r["no_gap"]) / max(int(r["locs_counted"]), 1) * 100),
        } for r in hist])

        fig_h = go.Figure()
        for col_name, color in [("מק\"טים %","#00ff88"),("איתורים %","#c9a84c"),("דיוק %","#c084fc")]:
            fig_h.add_trace(go.Scatter(
                x=hdf["חודש"], y=hdf[col_name],
                name=col_name, mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=9, color=color,
                            line=dict(color="#040d1c", width=2)),
                fill="tozeroy" if col_name == "דיוק %" else "none",
                fillcolor="rgba(0, 123, 255, 0.1)"))
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

    st.markdown("---")
    if db_load_inventory():
        buf = io.BytesIO()
        export_data = []
        for r in sorted(db_load_inventory(), key=lambda x: x["month"], reverse=True):
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

    # ════════════════════════════════════════════════════════════════════════════
    #  תוכנית ספירה חודשית (מילוי ידני)
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    sec_header("📋 תוכנית ספירה — "
               f"{MONTHS_HE[int(sel_month.split('-')[1])-1]} {sel_month.split('-')[0]}")

    def _n(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    plan = db_load_count_plan(sel_month)

    if not plan:
        st.markdown('<div class="al al-amber">ℹ️ עדיין אין תוכנית ספירה לחודש זה.</div>',
                    unsafe_allow_html=True)
        if st.button("📋 טען תוכנית התחלתית", key="seed_plan", use_container_width=True):
            default_plan = [
                (11, 63), (15, 84), (20, 33), (21, 40), (22, 37), (23, 37),
                (24, 64), (25, 69), (26, 36), (27, 37), (28, 37), (29, 35),
                (30, 51), (31, 51), (32, 67), (33, 59), (34, 56), (35, 56),
                (36, 50), (37, 50), (38, 24), (39, 102), (60, 21), (61, 26),
            ]
            try:
                db_bulk_insert_count_plan([{
                    "month": sel_month, "row_label": str(rl), "sku_count": sc,
                    "counter_name": "", "count_date": "", "sort_order": i,
                } for i, (rl, sc) in enumerate(default_plan)])
                st.rerun()
            except Exception:
                st.error("❌ לא ניתן לשמור. ודא שהרצת את count_plan_supabase.sql "
                         "ב-Supabase (יצירת הטבלה + כיבוי RLS).")
    else:
        # ── עותק עבודה בזיכרון עם מזהים יציבים ──
        work_key = f"cp_work_{sel_month}"
        if st.session_state.get("cp_work_month") != sel_month or work_key not in st.session_state:
            st.session_state[work_key] = [
                {"_id": f"row{idx}", "row_label": p.get("row_label") or "",
                 "sku_count": int(_n(p.get("sku_count"))),
                 "counter_name": p.get("counter_name") or "",
                 "count_date": p.get("count_date") or ""}
                for idx, p in enumerate(plan)
            ]
            st.session_state["cp_work_month"] = sel_month
            st.session_state["cp_next_id"] = len(plan)
            # ניקוי מפתחות ווידג'טים ישנים
            for k in list(st.session_state.keys()):
                if k.startswith(("cp_rl_", "cp_sc_", "cp_cn_", "cp_cd_")):
                    del st.session_state[k]
        work = st.session_state[work_key]

        # פריסום ערכי התחלה למפתחות הווידג'טים (פעם אחת לכל שדה)
        for row in work:
            rid = row["_id"]
            for fld, pre in (("row_label", "cp_rl"), ("counter_name", "cp_cn"),
                             ("count_date", "cp_cd")):
                k = f"{pre}_{rid}"
                if k not in st.session_state:
                    st.session_state[k] = row[fld]
            ks = f"cp_sc_{rid}"
            if ks not in st.session_state:
                st.session_state[ks] = int(row["sku_count"])

        def _sv(pre, rid, default=""):
            return st.session_state.get(f"{pre}_{rid}", default)

        # ── חישוב התקדמות (חי, מהעריכה הנוכחית) ──
        total_rows = len(work)
        done_rows  = [r for r in work
                      if str(_sv("cp_cn", r["_id"])).strip()
                      or str(_sv("cp_cd", r["_id"])).strip()]
        total_sku  = sum(int(_sv("cp_sc", r["_id"], 0) or 0) for r in work)
        done_sku   = sum(int(_sv("cp_sc", r["_id"], 0) or 0) for r in done_rows)
        pct_rows   = (len(done_rows) / total_rows * 100) if total_rows else 0
        pct_sku    = (done_sku / total_sku * 100) if total_sku else 0

        # ── גלגלי התקדמות ──
        gc1, gc2 = st.columns(2)
        if HAS_PLOTLY:
            def gauge(pct, title, color):
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(pct, 1),
                    number={"suffix": "%", "font": {"size": 30, "color": color,
                                                    "family": "Orbitron"}},
                    title={"text": title, "font": {"size": 14, "color": "#e2eeff",
                                                   "family": "Heebo"}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#8899aa"},
                        "bar": {"color": color},
                        "bgcolor": "rgba(0,0,0,0)",
                        "borderwidth": 1, "bordercolor": "rgba(255,255,255,.1)",
                        "steps": [{"range": [0, 100], "color": "rgba(255,255,255,.04)"}],
                    }))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=230,
                                  margin=dict(t=40, b=10, l=20, r=20),
                                  font=dict(family="Heebo"))
                return fig
            gc1.plotly_chart(gauge(pct_sku, "אחוז מקטים שנספרו", "#00ff88"),
                             use_container_width=True)
            gc2.plotly_chart(gauge(pct_rows, "אחוז שורות שנספרו", "#00d4ff"),
                             use_container_width=True)
        else:
            gc1.markdown(kpi_card(f"{pct_sku:.1f}%", "אחוז מקטים שנספרו",
                                  icon="🏷️", kind="green", color="var(--green)"),
                         unsafe_allow_html=True)
            gc2.markdown(kpi_card(f"{pct_rows:.1f}%", "אחוז שורות שנספרו",
                                  icon="📋", kind="blue"), unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.markdown(kpi_card(f"{len(done_rows)}/{total_rows}", "שורות שנספרו",
                             icon="✅", kind="green", color="var(--green)"), unsafe_allow_html=True)
        m2.markdown(kpi_card(f"{done_sku:,.0f}/{total_sku:,.0f}", "מקטים שנספרו",
                             icon="🏷️", kind="blue"), unsafe_allow_html=True)
        m3.markdown(kpi_card(f"{total_rows - len(done_rows)}", "שורות שנותרו",
                             icon="⏳", kind="amber", color="var(--amber)"), unsafe_allow_html=True)

        # ── עיצוב מותאם לשורות ──
        st.markdown("""
        <style>
        div[class*="st-key-cprow_"] { border-bottom: 1px solid var(--b0); padding: 2px 0; }
        div[class*="st-key-cprow_"]:hover { background: rgba(0,212,255,.04); border-radius: 10px; }
        div[class*="st-key-cprow_done_"] { border-right: 3px solid var(--green); border-radius: 8px; }
        </style>""", unsafe_allow_html=True)

        st.markdown("##### עריכת התוכנית")
        # כותרת
        h = st.columns([0.5, 1, 1, 1.8, 1.8])
        for c, t in zip(h, ["", "שורה", "מס' מקטים", "שם סופר", "תאריך ספירה"]):
            c.markdown(f'<div style="font-family:var(--orb);color:var(--cyan);font-size:.74rem;'
                       f'font-weight:700;padding:4px 2px;text-align:center">{t}</div>',
                       unsafe_allow_html=True)

        # שורות
        for row in work:
            rid  = row["_id"]
            done = bool(str(_sv("cp_cn", rid)).strip() or str(_sv("cp_cd", rid)).strip())
            rc = st.container(key=f"cprow_done_{rid}" if done else f"cprow_{rid}")
            cols = rc.columns([0.5, 1, 1, 1.8, 1.8])
            cols[0].markdown(
                f'<div style="text-align:center;font-size:1.1rem;padding-top:6px">'
                f'{"✅" if done else "⏳"}</div>', unsafe_allow_html=True)
            cols[1].text_input("שורה", key=f"cp_rl_{rid}", label_visibility="collapsed")
            cols[2].number_input("מקטים", key=f"cp_sc_{rid}", min_value=0, step=1,
                                 label_visibility="collapsed")
            cols[3].text_input("סופר", key=f"cp_cn_{rid}", label_visibility="collapsed",
                               placeholder="שם סופר")
            cols[4].text_input("תאריך", key=f"cp_cd_{rid}", label_visibility="collapsed",
                               placeholder="dd/mm/yy")

        # ➕ הוספת שורה
        if st.button("➕ הוסף שורה", key="cp_add_row", use_container_width=True):
            nid = st.session_state.get("cp_next_id", len(work))
            work.append({"_id": f"row{nid}", "row_label": "", "sku_count": 0,
                         "counter_name": "", "count_date": ""})
            st.session_state["cp_next_id"] = nid + 1
            st.rerun()

        st.markdown("")
        b1, b2 = st.columns([3, 1])
        if b1.button("💾 שמור תוכנית", key="save_plan", use_container_width=True):
            new_rows = []
            for i, row in enumerate(work):
                rid = row["_id"]
                rl  = str(_sv("cp_rl", rid)).strip()
                cn  = str(_sv("cp_cn", rid)).strip()
                if not rl and not cn:
                    continue
                new_rows.append({
                    "month": sel_month, "row_label": rl,
                    "sku_count": int(_sv("cp_sc", rid, 0) or 0),
                    "counter_name": cn,
                    "count_date": str(_sv("cp_cd", rid)).strip(),
                    "sort_order": i,
                })
            try:
                db_clear_count_plan(sel_month)
                db_bulk_insert_count_plan(new_rows)
                st.session_state["cp_work_month"] = None   # רענון מה-DB
                st.success("✅ התוכנית נשמרה!")
                st.rerun()
            except Exception:
                st.error("❌ לא ניתן לשמור. ודא שהרצת את count_plan_supabase.sql "
                         "ב-Supabase (יצירת הטבלה + כיבוי RLS).")

        if st.session_state.user_role == "מנהל WMS":
            if b2.button("🗑️ אפס", key="reset_plan", use_container_width=True):
                db_clear_count_plan(sel_month)
                st.session_state["cp_work_month"] = None
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    df = db_load_tasks()
    today = datetime.now()
    sec_header("🔬 אנליטיקס מתקדם")

    if not HAS_PLOTLY:
        st.warning("נדרש plotly לדף זה")
        return

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["ביצועים שבועיים", "התפלגות קטגוריות",
                        "עומס לפי יום בשבוע", "ביצועים חודשיים"],
        specs=[[{"type":"scatter"},{"type":"pie"}],
               [{"type":"bar"},{"type":"bar"}]],
        vertical_spacing=0.15, horizontal_spacing=0.1)

    wdf = week_stats(21)
    fig.add_trace(go.Scatter(
        x=wdf["תאריך"], y=wdf["אחוז"], mode="lines+markers",
        line=dict(color="#c9a84c", width=2), marker=dict(size=7, color="#c9a84c"),
        name="אחוז"), row=1, col=1)

    cat_counts = df["Category"].value_counts()
    CMAP = {"בטיחות":"#ff2d55","ספירה":"#c9a84c","תחזוקה":"#ffb800",
            "לוגיסטיקה":"#c084fc","ניקיון":"#00ff88","כללי":"#8899aa"}
    fig.add_trace(go.Pie(
        labels=cat_counts.index.tolist(),
        values=cat_counts.values.tolist(),
        hole=.5, textinfo="label+percent",
        marker_colors=[CMAP.get(c,"#8899aa") for c in cat_counts.index],
        showlegend=False, name=""), row=1, col=2)

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
        colors_mt = ["#00ff88" if v >= 80 else "#ffb800" if v >= 50 else "#ff2d55"
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
#  PAGE: EXTERNAL STORAGE  (אחסנה חיצונית)
# ═══════════════════════════════════════════════════════════════════════════════
def page_external_storage():
    is_admin = st.session_state.user_role == "מנהל WMS"
    sec_header("🏭 אחסנה חיצונית")

    records = db_load_external_storage()

    # ── READ-ONLY NOTICE for non-admins ────────────────────────────────────────
    if not is_admin:
        st.markdown(
            '<div class="al al-cyan">👁️ <b>מצב צפייה בלבד</b> — '
            'רק מנהל WMS רשאי להוסיף, לערוך או למחוק רשומות.</div>',
            unsafe_allow_html=True)

    # ── SUMMARY KPIs ───────────────────────────────────────────────────────────
    total_pallets    = sum(int(r.get("pallets", 0)) for r in records)
    warehouses_set   = {r.get("warehouse_name", "") for r in records if r.get("warehouse_name")}
    unique_warehouses = len(warehouses_set)

    k1, k2 = st.columns(2)
    k1.markdown(kpi_card(total_pallets,      "סה\"כ משטחים",  icon="🔢", kind="green", color="var(--green)"), unsafe_allow_html=True)
    k2.markdown(kpi_card(unique_warehouses,  "מחסנים חיצוניים", icon="🏭", kind="amber", color="var(--amber)"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ADD NEW RECORD FORM (Admin only) ───────────────────────────────────────
    if is_admin:
        sec_header("➕ הוספת רשומה חדשה")
        with st.form("ext_storage_add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_warehouse = st.text_input("🏭 שם מחסן", placeholder="שם המחסן החיצוני")
                new_location  = st.text_input("📍 מיקום",   placeholder="כתובת / עיר")
                new_pallets   = st.number_input("📦 מספר משטחים", min_value=0, step=1, value=0)
            with c2:
                new_contact_name  = st.text_input("👤 איש קשר (רשות)", placeholder="שם איש הקשר")
                new_contact_phone = st.text_input("📞 טלפון (רשות)",    placeholder="050-0000000")
            submitted = st.form_submit_button("💾 שמור רשומה", use_container_width=True)
            if submitted:
                if not new_warehouse.strip():
                    st.error("⚠️ שם מחסן הוא שדה חובה.")
                else:
                    db_add_external_storage(
                        new_warehouse.strip(), new_location.strip(),
                        new_pallets,
                        new_contact_name.strip(), new_contact_phone.strip())
                    st.success("✅ הרשומה נשמרה בהצלחה!")
                    st.rerun()

    # ── EXCEL UPLOAD SECTION ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    sec_header("📊 טבלת אקסל — אחסנה חיצונית")

    excel_rec = db_load_excel_table()

    # ── Info bar: last upload ──────────────────────────────────────────────────
    if excel_rec:
        fname    = excel_rec.get("file_name", "—")
        uploader = excel_rec.get("uploaded_by", "—")
        utime    = excel_rec.get("uploaded_at", "")
        try:
            utime_fmt = datetime.fromisoformat(utime.replace("Z","")).strftime("%d/%m/%Y %H:%M")
        except Exception:
            utime_fmt = utime
        st.markdown(
            f'<div class="al al-green">✅ <b>קובץ פעיל:</b> {fname} &nbsp;|&nbsp; '
            f'הועלה על-ידי <b>{uploader}</b> &nbsp;|&nbsp; {utime_fmt}</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="al al-amber">⚠️ <b>טרם הועלה קובץ אקסל.</b> '
            'המנהל יכול להעלות קובץ למטה.</div>',
            unsafe_allow_html=True)

    # ── Admin: upload widget ───────────────────────────────────────────────────
    if is_admin:
        uploaded_file = st.file_uploader(
            "📤 העלה קובץ אקסל (.xlsx / .xls)",
            type=["xlsx", "xls"],
            key="excel_uploader",
            help="כל העלאה חדשה תחליף את הקובץ הקודם לכולם")

        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file, engine="openpyxl", header=1)
                st.markdown(
                    f'<div class="al al-cyan">👁️ <b>תצוגה מקדימה</b> — '
                    f'{len(df_upload)} שורות, {len(df_upload.columns)} עמודות</div>',
                    unsafe_allow_html=True)
                st.dataframe(df_upload.head(10), use_container_width=True, hide_index=True)

                if st.button("💾 שמור טבלה לכולם", key="save_excel_btn", use_container_width=True):
                    import numpy as np, math, datetime as _dt
                    df_clean = df_upload.copy()
                    # הסר עמודות ריקות לגמרי
                    df_clean = df_clean.dropna(axis=1, how="all")
                    # המר כל סוגי datetime/date/time למחרוזת
                    for col in df_clean.columns:
                        df_clean[col] = df_clean[col].apply(
                            lambda v: v.strftime("%Y-%m-%d") if isinstance(v, (_dt.datetime, _dt.date)) else
                                      str(v) if isinstance(v, _dt.time) else v
                        )
                    # נקה NaN / Inf
                    df_clean = df_clean.where(pd.notnull(df_clean), None)
                    df_clean = df_clean.replace([np.inf, -np.inf], None)
                    table_json = df_clean.to_dict(orient="records")
                    def _clean(v):
                        if v is None: return None
                        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)): return None
                        if isinstance(v, (_dt.datetime, _dt.date, _dt.time)): return str(v)
                        return v
                    table_json = [{k: _clean(v) for k, v in row.items()} for row in table_json]
                    db_save_excel_table(
                        file_name   = uploaded_file.name,
                        table_data  = table_json,
                        uploaded_by = st.session_state.user_role,
                    )
                    st.success("✅ הטבלה נשמרה בהצלחה ותוצג לכולם!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ שגיאה בקריאת הקובץ: {e}")

    # ── Download button only — all roles ──────────────────────────────────────
    if excel_rec and excel_rec.get("table_data"):
        df_saved = pd.DataFrame(excel_rec["table_data"])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_saved.to_excel(writer, index=False, sheet_name="אחסנה חיצונית")
        st.download_button(
            label="📥 ייצא נתוני אחסנה חיצונית לאקסל",
            data=output.getvalue(),
            file_name="אחסנה_חיצונית.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dl_excel_btn",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── WAREHOUSE CARDS ────────────────────────────────────────────────────────
    sec_header("📋 מחסנים רשומים")

    if not records:
        st.markdown('<div class="al al-cyan">ℹ️ <b>אין מחסנים רשומים כרגע.</b></div>', unsafe_allow_html=True)
        return

    # ── Floating cards — 2 per row ─────────────────────────────────────────────
    cols = st.columns(2)
    for idx, r in enumerate(records):
        rec_id       = r.get("id")
        wname        = r.get("warehouse_name") or r.get("supplier") or "—"
        location     = r.get("location", "")
        pallets      = r.get("pallets") or r.get("quantity") or 0
        contact_name = r.get("contact_name", "")
        contact_phone= r.get("contact_phone", "")

        contact_html = ""
        if contact_name or contact_phone:
            contact_html = f"""
            <div style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(0,212,255,.12)">
              <span style="color:var(--txt2);font-size:.72rem;letter-spacing:1px">👤 איש קשר</span><br>
              <span style="color:var(--txt);font-weight:600">{contact_name or "—"}</span>
              {"&nbsp;&nbsp;<span style='color:var(--cyan);font-family:var(--mono);font-size:.85rem'>📞 " + contact_phone + "</span>" if contact_phone else ""}
            </div>"""

        with cols[idx % 2]:
            st.markdown(f"""
            <div style="background:var(--card);border:1px solid var(--b1);border-radius:18px;
                        padding:22px 24px;margin-bottom:16px;position:relative;overflow:hidden;
                        transition:all .3s;box-shadow:var(--shadow);">
              <div style="position:absolute;top:0;right:0;width:100%;height:3px;
                          background:linear-gradient(90deg,var(--cyan),var(--green))"></div>
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
                <div>
                  <div style="font-family:var(--orb);font-size:1rem;font-weight:700;
                              color:var(--cyan);letter-spacing:1px">{wname}</div>
                  {"<div style='color:var(--txt2);font-size:.78rem;margin-top:3px'>📍 " + location + "</div>" if location else ""}
                </div>
                <div style="background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.25);
                            border-radius:10px;padding:6px 14px;text-align:center">
                  <div style="font-family:var(--orb);font-size:1.4rem;font-weight:800;
                              color:var(--green)">{pallets}</div>
                  <div style="font-size:.6rem;color:var(--txt2);letter-spacing:1px">משטחים</div>
                </div>
              </div>
              {contact_html}
            </div>""", unsafe_allow_html=True)

            # Admin edit expander below each card
            if is_admin:
                with st.expander(f"✏️ ערוך / מחק — {wname}"):
                    with st.form(f"ext_edit_{rec_id}"):
                        ef1, ef2 = st.columns(2)
                        with ef1:
                            e_warehouse = st.text_input("🏭 שם מחסן",  value=wname,        key=f"wn_{rec_id}")
                            e_location  = st.text_input("📍 מיקום",    value=location,     key=f"lo_{rec_id}")
                            e_pallets   = st.number_input("📦 משטחים", min_value=0, step=1,
                                                          value=int(pallets),               key=f"pl_{rec_id}")
                        with ef2:
                            e_cname  = st.text_input("👤 איש קשר",  value=contact_name,  key=f"cn_{rec_id}")
                            e_cphone = st.text_input("📞 טלפון",     value=contact_phone, key=f"cp_{rec_id}")

                        bc1, bc2 = st.columns(2)
                        save_btn   = bc1.form_submit_button("💾 שמור", use_container_width=True)
                        delete_btn = bc2.form_submit_button("🗑️ מחק",  use_container_width=True)

                        if save_btn:
                            if not e_warehouse.strip():
                                st.error("⚠️ שם מחסן הוא שדה חובה.")
                            else:
                                db_update_external_storage(
                                    rec_id, e_warehouse.strip(), e_location.strip(),
                                    e_pallets, e_cname.strip(), e_cphone.strip())
                                st.success("✅ עודכן!")
                                st.rerun()
                        if delete_btn:
                            db_delete_external_storage(rec_id)
                            st.success("🗑️ נמחק.")
                            st.rerun()


def page_transfer_value():
    import math

    role       = st.session_state.user_role
    is_manager = (role == "מנהל WMS")

    def _num(v):
        try:
            x = float(v)
            return 0.0 if math.isnan(x) else x
        except (TypeError, ValueError):
            return 0.0

    def _txt(v):
        return "" if v is None or (isinstance(v, float) and math.isnan(v)) else str(v).strip()

    # ── מיפוי קוד מחסן → שם ידידותי (ניתן לעריכה לפי הצורך) ─────────────────────
    WH_NAMES = {
        "500": "מחסן ראשי",      "552": "מפעל",
        "573": "שיקום סחורה",     "575": "החזרת לספקים",
        "605": "השמדות",          "606": "השמדות הבטחת איכות",
        "670": "פגומים",          "671": "החזרות מלקוחות",
        "675": "פגומים קבלן",     "678": "סחורה שנעלמה",
        "550": "חו\"ג גלריה",     "554": "בית שמש",
        "100": "בית שמש",         "121": "בית שמש",        "125": "בית שמש",
        "672": "החזרות מלקוחות",  "680": "החזרת לספקים",
        "950": "אחסנה חיצונית",   "108": "ויסוצקי",        "120": "חו\"ג",
        "LIMB": "LIMB",
    }
    def wn(code):
        c = _txt(code)
        return WH_NAMES.get(c, c or "—")

    sec_header("🚧 דף בבניה")

    # ── בורר חודש (לכל המשתמשים) ──────────────────────────────────────────────
    months = db_movement_months()
    today = datetime.now()
    cur_month = f"{today.year}-{today.month:02d}"
    month_opts = months if months else [cur_month]

    def month_label(m):
        try:
            y, mm = m.split("-")
            return f"{MONTHS_HE[int(mm)-1]} {y}"
        except Exception:
            return m

    cM, _ = st.columns([2, 3])
    sel_month = cM.selectbox("📅 חודש", month_opts, format_func=month_label)

    rows = db_load_movements(sel_month)
    summary = db_load_month_summary(sel_month)
    turn = summary["turnover"]

    # ── טפסי ניהול (זמינים למנהל בלבד) ─────────────────────────────────────────
    def render_turnover_form(expanded):
        with st.expander(f"📈 עדכון מחזור מכירות — {month_label(sel_month)}", expanded=expanded):
            with st.form("turnover_form"):
                nt = st.number_input("מחזור מכירות חודשי (₪)", min_value=0.0,
                                     value=float(turn), step=1000.0, format="%.2f",
                                     help="לא נמצא בקובץ ההעברות — מזינים ידנית לחישוב האחוזים.")
                if st.form_submit_button("💾 שמור מחזור", use_container_width=True):
                    db_save_month_summary(sel_month, nt, summary["destructions"],
                                          summary["returns"], summary["goods_value"],
                                          summary["goods_dir"])
                    st.success("✅ נשמר!")
                    st.rerun()

    def render_uploader():
        st.markdown(
            '<div class="al al-cyan">ℹ️ העלה את קובץ האקסל החודשי. המערכת מזהה אוטומטית '
            'את גליונות התנועות (כל גליון = קטגוריה), את החודש מהתאריך, ומחשבת הכל.</div>',
            unsafe_allow_html=True)
        up = st.file_uploader("📁 בחר קובץ (.xlsx / .xls)", type=["xlsx", "xls"],
                              key="transfer_uploader")
        if up is None:
            return
        try:
            xls = pd.ExcelFile(up, engine="openpyxl")

            def find_col(cols, *subs):
                for c in cols:
                    if any(s in str(c) for s in subs):
                        return c
                return None

            def cat_label(sheet):
                s = str(sheet)
                if "השמד" in s:                              return "השמדות"
                if "ספק" in s:                               return "חזרות לספקים"
                if "לקוח" in s:                              return "החזרות מלקוחות"
                if s.lower() in ("datasheet", "data", "sheet1"): return "העברות בין מחסנים"
                return s

            detected = []
            for sh in xls.sheet_names:
                try:
                    d = pd.read_excel(xls, sheet_name=sh, header=0).dropna(axis=0, how="all")
                except Exception:
                    continue
                cstr = [str(c) for c in d.columns]
                if any("עלות תנועה" in c for c in cstr) and any("מחסן" in c for c in cstr) and len(d) > 0:
                    detected.append((sh, d, list(d.columns)))

            if not detected:
                st.markdown('<div class="al al-amber">⚠️ לא זוהו גליונות מתאימים.</div>',
                            unsafe_allow_html=True)
                return

            st.markdown(f'<div class="al al-green">✅ זוהו <b>{len(detected)}</b> גליונות:</div>',
                        unsafe_allow_html=True)
            chosen, all_months = [], []
            for sh, d, cols in detected:
                c_cost = find_col(cols, "עלות תנועה")
                c_date = find_col(cols, "תאריך")
                s_sum = sum(_num(v) for v in d[c_cost]) if c_cost else 0
                if c_date is not None:
                    for v in d[c_date]:
                        try:
                            ts = pd.to_datetime(v); all_months.append(f"{ts.year}-{ts.month:02d}")
                        except Exception:
                            pass
                if st.checkbox(f"📄 {sh} → «{cat_label(sh)}» | {len(d)} שורות | ₪{s_sum:,.0f}",
                               value=True, key=f"sheet_{sh}"):
                    chosen.append((sh, d, cols))

            auto_month = max(set(all_months), key=all_months.count) if all_months else cur_month
            m_in = st.text_input("📅 חודש היעד (YYYY-MM)", value=auto_month, key="tgt_month")
            replace = st.checkbox("🔄 החלף את כל נתוני החודש הקיימים", value=True, key="repl")

            if st.button("💾 ייבא לחודש", key="import_transfers", use_container_width=True):
                out = []
                for sh, d, cols in chosen:
                    cmap = {
                        "from_wh":   find_col(cols, "ממחסן"),
                        "to_wh":     find_col(cols, "למחסן"),
                        "wh_desc":   find_col(cols, "תאור מחסן", "תיאור מחסן"),
                        "doc":       find_col(cols, "תעודה"),
                        "sku":       find_col(cols, "מק"),
                        "product":   find_col(cols, "תאור מוצר", "מוצר", "תיאור"),
                        "qty":       find_col(cols, "כמות"),
                        "unit":      find_col(cols, "יח"),
                        "unit_cost": find_col(cols, "עלות ליח"),
                        "move_cost": find_col(cols, "עלות תנועה"),
                        "family":    find_col(cols, "משפחה"),
                    }
                    label = cat_label(sh)
                    for _, r in d.iterrows():
                        mc = _num(r.get(cmap["move_cost"])) if cmap["move_cost"] else 0
                        fw = _txt(r.get(cmap["from_wh"]))   if cmap["from_wh"]   else ""
                        tw = _txt(r.get(cmap["to_wh"]))     if cmap["to_wh"]     else ""
                        if mc == 0 and not fw and not tw:
                            continue
                        out.append({
                            "month": m_in.strip(), "category": label,
                            "from_wh": fw, "to_wh": tw,
                            "wh_desc":   _txt(r.get(cmap["wh_desc"]))   if cmap["wh_desc"]   else "",
                            "doc":       _txt(r.get(cmap["doc"]))       if cmap["doc"]       else "",
                            "sku":       _txt(r.get(cmap["sku"]))       if cmap["sku"]       else "",
                            "product":   _txt(r.get(cmap["product"]))   if cmap["product"]   else "",
                            "qty":       _num(r.get(cmap["qty"]))       if cmap["qty"]       else 0,
                            "unit":      _txt(r.get(cmap["unit"]))      if cmap["unit"]      else "",
                            "unit_cost": _num(r.get(cmap["unit_cost"])) if cmap["unit_cost"] else 0,
                            "move_cost": mc,
                            "family":    _txt(r.get(cmap["family"]))    if cmap["family"]    else "",
                        })
                if not out:
                    st.warning("⚠️ לא נמצאו שורות תקינות.")
                else:
                    if replace:
                        db_clear_movements(m_in.strip())
                    db_bulk_insert_movements(out)
                    st.success(f"✅ יובאו {len(out)} תנועות ל-{month_label(m_in.strip())}!")
                    st.rerun()
        except Exception as e:
            st.error(f"❌ שגיאה בקריאת הקובץ: {e}")

    # ════════════════════════════════════════════════════════════════════════════
    #  אין נתונים
    # ════════════════════════════════════════════════════════════════════════════
    if not rows:
        if is_manager:
            render_turnover_form(expanded=False)
            st.markdown("---")
            sec_header("📤 העלאת קובץ העברות חודשי")
            render_uploader()
        st.markdown("---")
        st.markdown('<div class="al al-amber">ℹ️ <b>אין עדיין נתונים לחודש זה.</b></div>',
                    unsafe_allow_html=True)
        return

    # ════════════════════════════════════════════════════════════════════════════
    #  חישובים
    # ════════════════════════════════════════════════════════════════════════════
    # מסלולים שהמנהל בחר להסתיר — לא יוצגו ולא ייכללו בסיכומים
    hidden_routes = db_load_hidden_routes()
    visible_rows = [r for r in rows
                    if (_txt(r.get("from_wh")), _txt(r.get("to_wh"))) not in hidden_routes]

    cat_sum, cat_cnt = {}, {}
    for r in visible_rows:
        c = r.get("category") or "אחר"
        cat_sum[c] = cat_sum.get(c, 0) + _num(r.get("move_cost"))
        cat_cnt[c] = cat_cnt.get(c, 0) + 1

    route_sum = {}
    for r in visible_rows:
        key = (_txt(r.get("from_wh")), _txt(r.get("to_wh")))
        route_sum[key] = route_sum.get(key, 0) + _num(r.get("move_cost"))

    grand = sum(cat_sum.values())

    # קיבוץ מקור→יעד + פירוט מוצר (מעבר אחד)
    src, route_detail = {}, {}
    for r in visible_rows:
        fw = _txt(r.get("from_wh")); tw = _txt(r.get("to_wh"))
        src.setdefault(fw, {}).setdefault(tw, [0.0, 0])
        src[fw][tw][0] += _num(r.get("move_cost"))
        src[fw][tw][1] += 1
        rd = route_detail.setdefault((fw, tw), {})
        k  = (_txt(r.get("sku")), _txt(r.get("product")))
        dd = rd.setdefault(k, [0.0, 0.0, 0])
        dd[0] += _num(r.get("qty")); dd[1] += _num(r.get("move_cost")); dd[2] += 1
    src_sorted = sorted(src.items(), key=lambda kv: -sum(v[0] for v in kv[1].values()))

    # ── כותרת ──────────────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:linear-gradient(135deg,var(--card),var(--card2),var(--card));'
        f'border:1px solid var(--b2);border-radius:16px;padding:16px 28px;margin-bottom:18px;'
        f'text-align:center;box-shadow:var(--glow-c)">'
        f'<div style="font-family:var(--orb);font-size:1.2rem;font-weight:800;color:var(--cyan);'
        f'letter-spacing:1px;text-shadow:0 0 20px rgba(0,212,255,.4)">'
        f'דף בבניה · העברות בין מחסנים — {month_label(sel_month)}</div></div>',
        unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    #  פריסה כמו גליון "הערך":  בלוקים לפי מקור (ימין)  |  תיבת סיכום (מרכז)
    # ════════════════════════════════════════════════════════════════════════════
    def pct_of_turn(v):
        return (v / turn * 100) if turn else None

    col_blocks, col_sum = st.columns([3, 2])

    # ── תיבת סיכום קטגוריות + מחזור ──────────────────────────────────────────────
    with col_sum:
        sec_header("📊 סיכום ערך")

        def sum_row(label, val, color="var(--green)", show_pct=True):
            p = pct_of_turn(val)
            pct_html = (f'<span style="color:var(--amber);font-family:var(--mono);'
                        f'font-size:.78rem;margin-left:10px">{p:.3f}%</span>'
                        if (show_pct and p is not None) else "")
            return (
                f'<div style="background:var(--card2);border:1px solid var(--b1);'
                f'border-radius:12px;padding:13px 16px;margin-bottom:9px;'
                f'border-right:4px solid {color};display:flex;justify-content:space-between;'
                f'align-items:center">'
                f'<span style="font-weight:700;color:var(--txt);font-size:.9rem">{label}</span>'
                f'<span style="white-space:nowrap"><span style="font-family:var(--orb);'
                f'color:{color};font-weight:700;font-size:1.05rem">₪{val:,.0f}</span>{pct_html}</span>'
                f'</div>')

        # 1) מחזור מכירות — ראשון ובולט
        if turn:
            st.markdown(
                f'<div style="background:linear-gradient(135deg,var(--card),var(--card2));'
                f'border:1px solid var(--b2);border-top:3px solid var(--cyan);'
                f'border-radius:12px;padding:14px 18px;margin-bottom:11px;box-shadow:var(--glow-c)">'
                f'<div style="display:flex;justify-content:space-between;align-items:center">'
                f'<span style="font-weight:800;color:var(--txt)">מחזור מכירות</span>'
                f'<span style="font-family:var(--orb);color:var(--cyan);font-weight:800;'
                f'font-size:1.2rem">₪{turn:,.0f}</span></div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="al al-amber" style="font-size:.8rem">הזן מחזור מכירות '
                        '(בניהול נתונים) כדי לראות אחוזים.</div>', unsafe_allow_html=True)

        # 2) סה"כ השמדות   3) סה"כ חזרות לספקים  (ידני גובר על אוטומטי)
        destr_disp = (summary["destructions"] if summary["destructions"] is not None
                      else cat_sum.get("השמדות"))
        ret_disp   = (summary["returns"] if summary["returns"] is not None
                      else cat_sum.get("חזרות לספקים"))

        html = ""
        if destr_disp is not None:
            html += sum_row("סה\"כ השמדות", destr_disp, "var(--red)")
        if ret_disp is not None:
            html += sum_row("סה\"כ חזרות לספקים", ret_disp, "var(--amber)")
        if "החזרות מלקוחות" in cat_sum:
            html += sum_row("החזרות מלקוחות", cat_sum["החזרות מלקוחות"], "var(--purple)")

        # סחורה בשווי (התווסף/הופחת) — מילוי ידני
        if summary["goods_value"]:
            added  = (summary["goods_dir"] == "התווסף")
            signed = summary["goods_value"] if added else -summary["goods_value"]
            html += sum_row(f"{summary['goods_dir']} סחורה בשווי (LIMB)", signed,
                            "var(--green)" if added else "var(--red)")

        limb_in  = route_sum.get(("LIMB", "500"), 0)
        limb_out = route_sum.get(("500", "LIMB"), 0)
        if limb_in:
            html += sum_row("LIMB → מחסן ראשי", limb_in, "var(--cyan)", show_pct=False)
        if limb_out:
            html += sum_row("מחסן ראשי → LIMB", limb_out, "var(--cyan)", show_pct=False)

        st.markdown(html, unsafe_allow_html=True)

        # ── מילוי ידני (מנהל בלבד) ──
        if is_manager:
            with st.expander("✏️ מילוי ידני של ערכי הסיכום"):
                with st.form("manual_summary"):
                    use_manual = st.checkbox(
                        "מילוי ידני של סה\"כ השמדות / חזרות לספקים",
                        value=(summary["destructions"] is not None or summary["returns"] is not None),
                        help="אם לא מסומן — יוצגו הערכים האוטומטיים שחושבו מהקובץ.")
                    md = st.number_input("סה\"כ השמדות (₪)", min_value=0.0, step=100.0,
                        value=float(summary["destructions"] if summary["destructions"] is not None
                                    else cat_sum.get("השמדות", 0)))
                    mr = st.number_input("סה\"כ חזרות לספקים (₪)", min_value=0.0, step=100.0,
                        value=float(summary["returns"] if summary["returns"] is not None
                                    else cat_sum.get("חזרות לספקים", 0)))
                    st.markdown("**סחורה בשווי:**")
                    gdir = st.radio("כיוון", ["הופחת", "התווסף"], horizontal=True,
                                    index=(1 if summary["goods_dir"] == "התווסף" else 0))
                    gv = st.number_input("סכום (₪)", min_value=0.0, step=100.0,
                                         value=float(summary["goods_value"]),
                                         help="0 = לא להציג שורה זו.")
                    if st.form_submit_button("💾 שמור", use_container_width=True):
                        db_save_month_summary(
                            sel_month, turn,
                            (md if use_manual else None),
                            (mr if use_manual else None),
                            gv, gdir)
                        st.success("✅ נשמר!")
                        st.rerun()
    with col_blocks:
        sec_header("🔁 העברות לפי מחסן מקור")
        st.markdown('<div class="al al-cyan" style="font-size:.82rem">👇 לחץ על שורת '
                    'העברה כדי לפתוח את הפירוט שלה לפי מוצר.</div>', unsafe_allow_html=True)

        for fw, dests in src_sorted:
            src_total = sum(v[0] for v in dests.values())
            src_name  = wn(fw)
            # כותרת המקור (כתומה)
            st.markdown(
                f'<div style="background:rgba(255,184,0,.1);border:1px solid var(--b1);'
                f'border-radius:12px;padding:11px 16px;margin:16px 0 8px;'
                f'display:flex;justify-content:space-between;align-items:center">'
                f'<span style="font-family:var(--orb);font-weight:700;color:var(--amber);'
                f'font-size:.92rem">{src_name}</span>'
                f'<span style="font-family:var(--orb);color:var(--amber);font-weight:700;'
                f'font-size:.95rem">₪{src_total:,.0f}</span></div>', unsafe_allow_html=True)

            for tw, (v, c) in sorted(dests.items(), key=lambda x: -x[1][0]):
                desc = f"מ{src_name} ל{wn(tw)}"
                with st.expander(f"{fw or '—'}→{tw or '—'}   ·   {c} תנועות   ·   "
                                 f"{desc}   —   ₪{v:,.0f}"):
                    detail = route_detail.get((fw, tw), {})
                    det_df = pd.DataFrame([{
                        "מק\"ט":     k[0] or "—",
                        "תאור מוצר": k[1] or "—",
                        "כמות":      qv,
                        "תנועות":    cn,
                        "ערך (₪)":   f"₪{val:,.0f}",
                    } for k, (qv, val, cn) in sorted(detail.items(), key=lambda x: -x[1][1])])
                    st.markdown(
                        f'<div style="color:var(--txt2);font-size:.78rem;margin-bottom:6px">'
                        f'{len(detail)} מוצרים · {c} תנועות · סה"כ <b style="color:var(--green)">'
                        f'₪{v:,.0f}</b></div>', unsafe_allow_html=True)
                    st.dataframe(det_df, use_container_width=True, hide_index=True)

    # ════════════════════════════════════════════════════════════════════════════
    #  כניסה לגליונות (drill-down) — לכל המשתמשים
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    sec_header("📂 כניסה לגליונות")
    cat_sorted = sorted(cat_sum.items(), key=lambda x: -x[1])
    for cat, cval in cat_sorted:
        crows = [r for r in visible_rows if (r.get("category") or "אחר") == cat]
        with st.expander(f"📄 {cat}  —  ₪{cval:,.0f}  ·  {len(crows):,} תנועות"):
            rs, rc, rd = {}, {}, {}
            for r in crows:
                key = (_txt(r.get("from_wh")), _txt(r.get("to_wh")))
                rs[key] = rs.get(key, 0) + _num(r.get("move_cost"))
                rc[key] = rc.get(key, 0) + 1
                if key not in rd and _txt(r.get("wh_desc")):
                    rd[key] = _txt(r.get("wh_desc"))
            for (fw, tw), v in sorted(rs.items(), key=lambda x: -x[1]):
                desc = rd.get((fw, tw), "")
                desc_html = (f'<span style="color:var(--txt2);font-size:.78rem;'
                             f'margin-right:8px">· {desc}</span>') if desc else ""
                st.markdown(
                    f'<div style="background:var(--card2);border:1px solid var(--b0);'
                    f'border-radius:10px;padding:11px 16px;margin-bottom:7px;'
                    f'border-right:4px solid var(--cyan);display:flex;'
                    f'justify-content:space-between;align-items:center">'
                    f'<div><span style="font-family:var(--mono);color:var(--cyan);'
                    f'font-weight:700">{fw or "—"} → {tw or "—"}</span>{desc_html}'
                    f'<div style="color:var(--txt3);font-size:.7rem;margin-top:3px">'
                    f'{rc[(fw, tw)]:,} תנועות</div></div>'
                    f'<span style="font-family:var(--orb);color:var(--green);'
                    f'font-weight:700;font-size:1.05rem">₪{v:,.0f}</span></div>',
                    unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    #  ניהול נתונים — מנהל WMS בלבד (שינוי / העלאה / ייצוא / מחיקה)
    # ════════════════════════════════════════════════════════════════════════════
    if not is_manager:
        return

    st.markdown("---")
    sec_header("⚙️ ניהול נתונים (מנהל בלבד)")
    render_turnover_form(expanded=(turn == 0))

    # ── הסתרת מסלולים מהתצוגה ─────────────────────────────────────────────────
    with st.expander("👁️ הסתרת מסלולים מהתצוגה"):
        st.markdown('<div class="al al-cyan" style="font-size:.82rem">בחר מסלולים שלא '
                    'יוצגו בדו"ח (לא יימחקו — רק יוסתרו, וגם לא ייכללו בסיכומים). '
                    'ההסתרה חלה על כל החודשים.</div>', unsafe_allow_html=True)

        # כל המסלולים בחודש (כולל מוסתרים) לבחירה
        all_routes = {}
        for r in rows:
            key = (_txt(r.get("from_wh")), _txt(r.get("to_wh")))
            all_routes[key] = all_routes.get(key, 0) + _num(r.get("move_cost"))
        route_label = {
            f"{wn(f)} → {wn(t)}  ({f or '—'}→{t or '—'})  ·  ₪{v:,.0f}": (f, t)
            for (f, t), v in sorted(all_routes.items(), key=lambda x: -x[1])
        }
        default_hidden = [lbl for lbl, ft in route_label.items() if ft in hidden_routes]

        with st.form("hide_routes_form"):
            sel = st.multiselect("מסלולים להסתרה", list(route_label.keys()),
                                 default=default_hidden)
            if st.form_submit_button("💾 שמור תצוגה", use_container_width=True):
                new_hidden = {route_label[l] for l in sel}
                try:
                    for ft in new_hidden - hidden_routes:
                        db_add_hidden_route(ft[0], ft[1])
                    for ft in hidden_routes - new_hidden:
                        db_remove_hidden_route(ft[0], ft[1])
                    st.success("✅ התצוגה עודכנה!")
                    st.rerun()
                except Exception as e:
                    st.error("❌ לא ניתן לשמור. ודא שהרצת את hidden_routes_supabase.sql "
                             "ב-Supabase (יצירת הטבלה + כיבוי RLS).")

        if hidden_routes:
            st.markdown(f'<div style="color:var(--txt2);font-size:.78rem;margin-top:6px">'
                        f'כרגע מוסתרים {len(hidden_routes)} מסלולים.</div>',
                        unsafe_allow_html=True)

    with st.expander("📤 העלאת / עדכון קובץ חודשי"):
        render_uploader()

    with st.expander("📥 ייצוא ומחיקה"):
        buf = io.BytesIO()
        df_export = pd.DataFrame([{
            "חודש": r.get("month"), "קטגוריה": r.get("category"),
            "ממחסן": r.get("from_wh"), "למחסן": r.get("to_wh"),
            "תאור מחסן": r.get("wh_desc"), "תעודה": r.get("doc"),
            "מק\"ט": r.get("sku"), "תאור מוצר": r.get("product"),
            "כמות": _num(r.get("qty")), "יח'": r.get("unit"),
            "עלות ליח'": _num(r.get("unit_cost")), "עלות תנועה": _num(r.get("move_cost")),
            "משפחה": r.get("family"),
        } for r in visible_rows])
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df_export.to_excel(w, index=False, sheet_name="העברות")
        st.download_button(
            f"📥 ייצוא נתוני {month_label(sel_month)} — Excel",
            buf.getvalue(), f"דף_בבניה_{sel_month}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, key="export_transfers")
        st.markdown('<div class="al al-red" style="margin-top:14px">⚠️ מחיקת כל '
                    f'תנועות <b>{month_label(sel_month)}</b>.</div>', unsafe_allow_html=True)
        if st.button("🗑️ מחק את נתוני החודש", key="clear_month", use_container_width=True):
            db_clear_movements(sel_month)
            st.success("🗑️ נמחק.")
            st.rerun()


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

ROLE_ICONS = {"מנהל WMS": "🔑", "צוות מחסן": "📦", "הנהלה": "📊"}
df_side    = db_load_tasks()
today_side = len(tasks_for_date(df_side, datetime.now()))
ov_side    = len(get_overdue())

MENUS = {
    "מנהל WMS":  ["📊 דשבורד","📋 סידור עבודה","📅 לוח שנה",
                  "📦 ספירות מלאי","🚧 דף בבניה","➕ הוספת משימה","⚙️ ניהול משימות","🔬 אנליטיקס","🏭 אחסנה חיצונית"],
    "הנהלה":     ["📊 דשבורד","📅 לוח שנה","📦 ספירות מלאי","🚧 דף בבניה","🔬 אנליטיקס","🏭 אחסנה חיצונית"],
    "צוות מחסן": ["📊 דשבורד","📋 סידור עבודה","📦 ספירות מלאי","📅 לוח שנה","🚧 דף בבניה","🏭 אחסנה חיצונית"],
}

inject_theme()

# ── ניווט: תפריט "☰" שנפתח בלחיצה (במקום sidebar) ──────────────────────────────
st.markdown("""
<style>
section[data-testid="stSidebar"], div[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"] { display:none !important; }
.block-container { padding-top: 1.1rem !important; max-width: 100% !important; }
header[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
div[class*="st-key-menu_toggle"] button {
    font-family: var(--orb) !important; letter-spacing: 1px !important;
    background: linear-gradient(135deg, var(--card), var(--card2)) !important;
    border: 1px solid var(--cyan) !important; color: var(--cyan) !important;
    box-shadow: 0 0 14px rgba(0,212,255,.25) !important;
    max-width: 200px !important; min-height: 42px !important;
}
div[class*="st-key-navpanel"] {
    background: linear-gradient(160deg, var(--card), var(--card2)) !important;
    border: 1px solid var(--cyan) !important; border-radius: 16px !important;
    box-shadow: 0 0 34px rgba(0,212,255,.18) !important; padding: 8px 12px !important;
    margin-bottom: 14px !important;
}
div[class*="st-key-navpanel"] .stButton > button { min-height: 42px !important; }
div[class*="st-key-nav_"] button { font-family: var(--orb) !important; letter-spacing: .5px !important; }
</style>""", unsafe_allow_html=True)

_ov_color = "var(--red)" if ov_side else "var(--green)"

# העמוד הנוכחי נשמר בזיכרון
if st.session_state.get("page") not in MENUS[role]:
    st.session_state.page = MENUS[role][0]
choice = st.session_state.page

PAGE_ICONS = {
    "📊 דשבורד":          "📊 דשבורד בקרה",
    "📋 סידור עבודה":     "📋 סידור עבודה שבועי",
    "📅 לוח שנה":         "📅 לוח שנה",
    "➕ הוספת משימה":     "➕ הוספת משימה חדשה",
    "⚙️ ניהול משימות":    "⚙️ ניהול ועריכת משימות",
    "📦 ספירות מלאי":     "📦 דשבורד ספירות מלאי",
    "🚧 דף בבניה":        "🚧 דף בבניה",
    "🔬 אנליטיקס":        "🔬 אנליטיקס מתקדם",
    "🏭 אחסנה חיצונית":  "🏭 אחסנה חיצונית",
}

if HAS_PLOTLY:
    pio.templates.default = "plotly_white" if st.session_state.get("theme") == "light" else "plotly_dark"

# ── כפתור התפריט (☰) ──
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

if st.button(("✕  סגור" if st.session_state.menu_open else "☰  תפריט"),
             key="menu_toggle", use_container_width=True):
    st.session_state.menu_open = not st.session_state.menu_open
    st.rerun()

if st.session_state.menu_open:
    with st.container(key="navpanel"):
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:6px 6px 10px;border-bottom:1px solid rgba(0,212,255,.15);
                    margin-bottom:8px;flex-wrap:wrap;gap:8px">
          <div style="display:flex;align-items:center;gap:10px">
            <span style="font-size:1.6rem">{ROLE_ICONS.get(role,"👤")}</span>
            <div>
              <div style="font-family:var(--orb);font-weight:700;font-size:.82rem;
                          color:var(--cyan);letter-spacing:1px">{role}</div>
              <div style="font-size:.62rem;color:var(--txt2);font-family:var(--mono)">מחובר {elapsed_min} דק</div>
            </div>
          </div>
          <div style="font-family:var(--mono);font-size:.64rem;text-align:left">
            <span style="color:var(--txt2)">היום </span>
            <span style="color:var(--cyan);font-weight:700">{today_side}</span>&nbsp;·&nbsp;
            <span style="color:var(--txt2)">פיגורים </span>
            <span style="color:{_ov_color};font-weight:700">{ov_side}</span>&nbsp;·&nbsp;
            <span style="color:var(--txt2)">סה"כ </span>
            <span style="color:var(--txt);font-weight:700">{len(df_side)}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        for _item in MENUS[role]:
            if st.button(_item, key=f"nav_{_item}", use_container_width=True,
                         type=("primary" if _item == choice else "secondary")):
                st.session_state.page = _item
                st.session_state.menu_open = False
                st.rerun()

        st.markdown("---")
        _is_dark = st.session_state.theme == "dark"
        if st.button("☀️ מצב בהיר" if _is_dark else "🌙 מצב כהה",
                     use_container_width=True, key="theme_btn"):
            st.session_state.theme = "light" if _is_dark else "dark"
            st.rerun()
        if st.button("🚪 התנתקות", use_container_width=True, key="logout_btn"):
            st.session_state.user_role  = None
            st.session_state.login_time = None
            st.rerun()

        if elapsed_min >= 50:
            st.markdown(
                f'<div class="al al-amber" style="font-size:.7rem;padding:6px 10px;margin:4px 0">'
                f'הסשן יפוג בעוד {60-elapsed_min} דק</div>',
                unsafe_allow_html=True)

# ── באנר העמוד ──
st.markdown(
    f'<div class="mega-banner" style="padding:18px 32px;margin-bottom:20px">'
    f'<h1 style="font-size:1.4rem;letter-spacing:2px">{PAGE_ICONS.get(choice, choice)}</h1>'
    f'<div class="sub"><span class="live-dot"></span> {(datetime.now() + timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")} &nbsp;|&nbsp; {role}</div>'
    f'</div>', unsafe_allow_html=True)


if   choice == "📊 דשבורד":          page_dashboard()
elif choice == "📋 סידור עבודה":     page_work()
elif choice == "📅 לוח שנה":         page_calendar()
elif choice == "📦 ספירות מלאי":     page_inventory()
elif choice == "🚧 דף בבניה":        page_transfer_value()
elif choice == "➕ הוספת משימה":     page_add()
elif choice == "⚙️ ניהול משימות":    page_manage()
elif choice == "🔬 אנליטיקס":        page_analytics()
elif choice == "🏭 אחסנה חיצונית":  page_external_storage()
