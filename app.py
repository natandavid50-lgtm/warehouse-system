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
    
    pio.templates.default = "plotly_dark"  # 🎯 2. הגדרנו את המצב הכהה כברירת מחדל לכולם
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

# ── External Storage ────────────────────────────────────────────────────────────
def db_load_external_storage() -> list:
    try:
        supabase = get_conn()
        res = supabase.table("external_storage").select("*").order("id").execute()
        return res.data if res.data else []
    except Exception:
        return []

def db_add_external_storage(supplier, location, item_desc, quantity, unit, arrival_date, notes):
    supabase = get_conn()
    data = {
        "supplier":     supplier,
        "location":     location,
        "item_desc":    item_desc,
        "quantity":     int(quantity),
        "unit":         unit,
        "arrival_date": str(arrival_date),
        "notes":        notes,
    }
    supabase.table("external_storage").insert(data).execute()

def db_update_external_storage(record_id, supplier, location, item_desc, quantity, unit, arrival_date, notes):
    supabase = get_conn()
    data = {
        "supplier":     supplier,
        "location":     location,
        "item_desc":    item_desc,
        "quantity":     int(quantity),
        "unit":         unit,
        "arrival_date": str(arrival_date),
        "notes":        notes,
    }
    supabase.table("external_storage").update(data).eq("id", record_id).execute()

def db_delete_external_storage(record_id):
    supabase = get_conn()
    supabase.table("external_storage").delete().eq("id", record_id).execute()

# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def init_state():
    if "user_role"  not in st.session_state: st.session_state.user_role  = None
    if "login_time" not in st.session_state: st.session_state.login_time = None

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

        detail_row('מק"טים שנספרו', skus_c, skus_t, color_skus)
        detail_row("איתורים שנספרו", locs_c, locs_t, color_locs)
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
    total_records  = len(records)
    total_qty      = sum(int(r.get("quantity", 0)) for r in records)
    suppliers_set  = {r.get("supplier", "") for r in records if r.get("supplier")}
    unique_suppliers = len(suppliers_set)

    k1, k2, k3 = st.columns(3)
    k1.markdown(kpi_card(total_records,    "רשומות פעילות",    icon="📦", kind="blue"),  unsafe_allow_html=True)
    k2.markdown(kpi_card(total_qty,        "סה\"כ כמות",        icon="🔢", kind="green", color="var(--green)"), unsafe_allow_html=True)
    k3.markdown(kpi_card(unique_suppliers, "ספקים",            icon="🏢", kind="amber", color="var(--amber)"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ADD NEW RECORD FORM (Admin only) ───────────────────────────────────────
    if is_admin:
        sec_header("➕ הוספת רשומה חדשה")
        with st.form("ext_storage_add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_supplier    = st.text_input("🏢 ספק", placeholder="שם הספק / מחסן חיצוני")
                new_location    = st.text_input("📍 מיקום", placeholder="כתובת / שם מחסן חיצוני")
                new_item_desc   = st.text_area("📝 תיאור הפריט / הסחורה", placeholder="תאר את הסחורה המאוחסנת", height=100)
            with c2:
                new_quantity    = st.number_input("🔢 כמות", min_value=0, step=1, value=0)
                new_unit        = st.selectbox("📐 יחידה", ["יחידות", "פלטות", "קרטונים", "ק\"ג", "טון", "מ\"ר", "אחר"])
                new_arrival     = st.date_input("📅 תאריך כניסה", datetime.now().date())
                new_notes       = st.text_area("🗒️ הערות", placeholder="הערות נוספות...", height=80)
            submitted = st.form_submit_button("💾 שמור רשומה", use_container_width=True)
            if submitted:
                if not new_supplier.strip() or not new_item_desc.strip():
                    st.error("⚠️ שם ספק ותיאור פריט הם שדות חובה.")
                else:
                    db_add_external_storage(
                        new_supplier.strip(), new_location.strip(),
                        new_item_desc.strip(), new_quantity, new_unit,
                        new_arrival, new_notes.strip())
                    st.success("✅ הרשומה נשמרה בהצלחה!")
                    st.rerun()

    # ── DATA TABLE ─────────────────────────────────────────────────────────────
    sec_header("📋 רשומות קיימות")

    if not records:
        st.markdown('<div class="al al-cyan">ℹ️ <b>אין רשומות אחסנה חיצונית כרגע.</b></div>', unsafe_allow_html=True)
        return

    # Build display dataframe for all roles
    display_rows = []
    for r in records:
        display_rows.append({
            "מזהה":          r.get("id", ""),
            "ספק":           r.get("supplier", ""),
            "מיקום":         r.get("location", ""),
            "תיאור פריט":    r.get("item_desc", ""),
            "כמות":          r.get("quantity", ""),
            "יחידה":         r.get("unit", ""),
            "תאריך כניסה":   r.get("arrival_date", ""),
            "הערות":         r.get("notes", ""),
        })
    df_ext = pd.DataFrame(display_rows)

    # ── READ-ONLY TABLE for non-admins ─────────────────────────────────────────
    if not is_admin:
        st.dataframe(
            df_ext.drop(columns=["מזהה"]),
            use_container_width=True,
            hide_index=True)
        return

    # ── ADMIN: inline edit / delete per row ────────────────────────────────────
    # Show the table for reference
    st.dataframe(
        df_ext.drop(columns=["מזהה"]),
        use_container_width=True,
        hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sec_header("✏️ עריכה / מחיקה")

    for r in records:
        rec_id = r.get("id")
        with st.expander(
            f"📦  {r.get('supplier','—')} · {r.get('item_desc','—')} "
            f"· {r.get('quantity','')} {r.get('unit','')}"):

            with st.form(f"ext_edit_{rec_id}"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_supplier  = st.text_input("🏢 ספק",    value=r.get("supplier",""),  key=f"sup_{rec_id}")
                    e_location  = st.text_input("📍 מיקום",  value=r.get("location",""),  key=f"loc_{rec_id}")
                    e_item_desc = st.text_area("📝 תיאור",   value=r.get("item_desc",""), key=f"itm_{rec_id}", height=90)
                with ec2:
                    e_quantity  = st.number_input("🔢 כמות", min_value=0, step=1,
                                                  value=int(r.get("quantity", 0)),        key=f"qty_{rec_id}")
                    e_unit      = st.selectbox("📐 יחידה",
                                              ["יחידות","פלטות","קרטונים","ק\"ג","טון","מ\"ר","אחר"],
                                              index=["יחידות","פלטות","קרטונים","ק\"ג","טון","מ\"ר","אחר"].index(
                                                  r.get("unit","יחידות"))
                                              if r.get("unit","יחידות") in
                                              ["יחידות","פלטות","קרטונים","ק\"ג","טון","מ\"ר","אחר"] else 0,
                                              key=f"unt_{rec_id}")
                    try:
                        arr_val = datetime.strptime(str(r.get("arrival_date", "")), "%Y-%m-%d").date()
                    except Exception:
                        arr_val = datetime.now().date()
                    e_arrival   = st.date_input("📅 תאריך כניסה", value=arr_val,          key=f"arr_{rec_id}")
                    e_notes     = st.text_area("🗒️ הערות",  value=r.get("notes",""),      key=f"nts_{rec_id}", height=72)

                btn_col1, btn_col2 = st.columns(2)
                save_btn   = btn_col1.form_submit_button("💾 שמור שינויים", use_container_width=True)
                delete_btn = btn_col2.form_submit_button("🗑️ מחק רשומה",   use_container_width=True)

                if save_btn:
                    if not e_supplier.strip() or not e_item_desc.strip():
                        st.error("⚠️ שם ספק ותיאור פריט הם שדות חובה.")
                    else:
                        db_update_external_storage(
                            rec_id, e_supplier.strip(), e_location.strip(),
                            e_item_desc.strip(), e_quantity, e_unit,
                            e_arrival, e_notes.strip())
                        st.success("✅ הרשומה עודכנה!")
                        st.rerun()

                if delete_btn:
                    db_delete_external_storage(rec_id)
                    st.success("🗑️ הרשומה נמחקה.")
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
df_side = db_load_tasks()
today_side = len(tasks_for_date(df_side, datetime.now()))
ov_side    = len(get_overdue())

st.sidebar.markdown(f"""
<div style="padding:20px 0 12px;text-align:center">
  <div style="font-size:2.4rem;margin-bottom:8px">{ROLE_ICONS.get(role,'👤')}</div>
  <div style="font-family:'Orbitron',monospace;font-weight:700;font-size:.95rem;
              color:var(--cyan);letter-spacing:1px">{role}</div>
  <div style="font-size:.72rem;color:var(--txt2);margin-top:4px;font-family:var(--mono)">
    ● מחובר {elapsed_min} דק'
  </div>
</div>
<div style="background:var(--card2);border:1px solid var(--b1);border-radius:10px;
            padding:10px 12px;margin-bottom:16px;font-family:var(--mono);font-size:.72rem">
  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
    <span style="color:var(--txt2)">להיום:</span>
    <span style="color:var(--cyan);font-weight:700">{today_side}</span>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
    <span style="color:var(--txt2)">פיגורים:</span>
    <span style="color:{'var(--red)' if ov_side else 'var(--green)'};font-weight:700">{ov_side}</span>
  </div>
  <div style="display:flex;justify-content:space-between">
    <span style="color:var(--txt2)">סה"כ:</span>
    <span style="color:var(--txt);font-weight:700">{len(df_side)}</span>
  </div>
</div>
""", unsafe_allow_html=True)

MENUS = {
    "מנהל WMS":  ["📊 דשבורד","📋 סידור עבודה","📅 לוח שנה",
                  "📦 ספירות מלאי","➕ הוספת משימה","⚙️ ניהול משימות","🔬 אנליטיקס","🏭 אחסנה חיצונית"],
    "הנהלה":     ["📊 דשבורד","📅 לוח שנה","📦 ספירות מלאי","🔬 אנליטיקס","🏭 אחסנה חיצונית"],
    "צוות מחסן": ["📊 דשבורד","📋 סידור עבודה","📦 ספירות מלאי","📅 לוח שנה","🏭 אחסנה חיצונית"],
}
choice = st.sidebar.radio("", MENUS[role], label_visibility="collapsed")

st.sidebar.markdown("---")
if elapsed_min >= 50:
    st.sidebar.markdown(
        f'<div class="al al-amber" style="font-size:.78rem;padding:8px 12px">'
        f'⚠️ הסשן יפוג בעוד {60-elapsed_min} דק\'</div>',
        unsafe_allow_html=True)
if st.sidebar.button("🚪 התנתקות", use_container_width=True):
    st.session_state.user_role = None
    st.session_state.login_time = None
    st.rerun()

PAGE_ICONS = {
    "📊 דשבורד":          "📊 דשבורד בקרה",
    "📋 סידור עבודה":     "📋 סידור עבודה שבועי",
    "📅 לוח שנה":         "📅 לוח שנה",
    "➕ הוספת משימה":     "➕ הוספת משימה חדשה",
    "⚙️ ניהול משימות":    "⚙️ ניהול ועריכת משימות",
    "📦 ספירות מלאי":     "📦 דשבורד ספירות מלאי",
    "🔬 אנליטיקס":        "🔬 אנליטיקס מתקדם",
    "🏭 אחסנה חיצונית":  "🏭 אחסנה חיצונית",
}
st.markdown(
    f'<div class="mega-banner" style="padding:18px 32px;margin-bottom:20px">'
    f'<h1 style="font-size:1.4rem;letter-spacing:2px">{PAGE_ICONS.get(choice, choice)}</h1>'
    f'<div class="sub"><span class="live-dot"></span> {datetime.now().strftime("%d/%m/%Y %H:%M")} &nbsp;|&nbsp; {role}</div>'
    f'</div>', unsafe_allow_html=True)

if   choice == "📊 דשבורד":          page_dashboard()
elif choice == "📋 סידור עבודה":     page_work()
elif choice == "📅 לוח שנה":         page_calendar()
elif choice == "📦 ספירות מלאי":     page_inventory()
elif choice == "➕ הוספת משימה":     page_add()
elif choice == "⚙️ ניהול משימות":    page_manage()
elif choice == "🔬 אנליטיקס":        page_analytics()
elif choice == "🏭 אחסנה חיצונית":  page_external_storage()
