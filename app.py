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
CATS  = ["כללי", "בטיחות", "לוגיסטיקה", "ניקיון", "תחזוקה", "ספירה", "אחסנה חיצונית"]
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

*, *::before, *::after { box-sizing: border-box;
}
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
[data-testid="stSidebar"] * { color: var(--txt) !important;
}
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
  top: 0;
  right: 0;
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

::-webkit-scrollbar { width: 5px;
  height: 5px; }
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
  bottom: 0; left: 0;
  right: 0; height: 1px;
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
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 12px var(--green);
  margin-left: 8px;
  animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:.5; transform:scale(.7);
}
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
  top: 0;
  right: 0; width: 100%; height: 3px;
}
.kpi-blue::before   { background: linear-gradient(90deg, var(--cyan), #005fa3);
}
.kpi-green::before  { background: linear-gradient(90deg, var(--green), #005f35); }
.kpi-red::before    { background: linear-gradient(90deg, var(--red), #6b001e);
}
.kpi-amber::before  { background: linear-gradient(90deg, var(--amber), #6b4a00); }
.kpi-purple::before { background: linear-gradient(90deg, var(--purple), #3d0070); }
.kpi:hover.kpi-blue  { box-shadow: var(--glow-c);
}
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
.tc:hover { background: var(--card2); border-color: var(--b2); transform: translateX(-3px);
}
.tc.done   { border-right-color: var(--green) !important; opacity: .65; }
.tc.urgent { border-right-color: var(--red)   !important;
}
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
.b-blue   { background: rgba(0,212,255,.14);  color: #5dd8ff; border: 1px solid rgba(0,212,255,.25);
}
.b-green  { background: rgba(0,255,136,.12);  color: #00ff88; border: 1px solid rgba(0,255,136,.2); }
.b-red    { background: rgba(255,45,85,.14);  color: #ff5577;
  border: 1px solid rgba(255,45,85,.25); }
.b-amber  { background: rgba(255,184,0,.14);  color: #ffd040; border: 1px solid rgba(255,184,0,.25); }
.b-purple { background: rgba(191,90,242,.14);
  color: #d070ff; border: 1px solid rgba(191,90,242,.25); }
.b-gray   { background: rgba(255,255,255,.07);color: var(--txt2); border: 1px solid var(--b1);
}

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
.wchip .day-count { font-size: .62rem; color: var(--green); font-weight: 700;
  margin-top: 4px; }

.al { border-radius: 12px; padding: 14px 18px; margin-bottom: 14px; font-size: .9rem; display: flex; align-items: flex-start; gap: 10px;
}
.al-red    { background: rgba(255,45,85,.1);   border: 1px solid rgba(255,45,85,.4); }
.al-green  { background: rgba(0,255,136,.07);  border: 1px solid rgba(0,255,136,.25);
}
.al-amber  { background: rgba(255,184,0,.08);  border: 1px solid rgba(255,184,0,.3); }
.al-cyan   { background: rgba(0,212,255,.07);  border: 1px solid rgba(0,212,255,.25);
}

.stat-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--b0); }
.stat-row:last-child { border-bottom: none;
}
.stat-label { color: var(--txt2); font-size: .82rem; flex: 1; }
.stat-val   { color: var(--txt);  font-size: .85rem; font-weight: 700; font-family: var(--mono);
}

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

.mm { background: var(--card); border: 1px solid var(--b1); border-radius: 10px;
  padding: 12px 14px; display: flex; align-items: center; gap: 12px; transition: all .2s; }
.mm:hover { border-color: var(--b2); transform: translateY(-2px);
}
.mm-icon { font-size: 1.5rem; }
.mm-val  { font-family: var(--orb); font-size: 1.4rem; font-weight: 700; color: var(--cyan); }
.mm-lbl  { font-size: .72rem;
  color: var(--txt2); letter-spacing: .5px; }

.tl-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 4px;
}

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
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 4px solid var(--cyan) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 4px solid var(--green) !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 4px solid var(--amber) !important;
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
    if rec == "לא":         return diff == 0
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
            if not t["is_done"]:
                out.append(t)
    return out

def week_stats(days=14):
    df = db_load_tasks()
    today = datetime.now().date()
    rows = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        ts = tasks_for_date(df, d)
        tot = len(ts)
        don = sum(1 for t in ts if t["is_done"])
        rows.append({
            "date": d,
            "תאריך": d.strftime("%d/%m"),
            "בוצע": don,
            "מתוכנן": tot,
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
            rows.append({"יום": day, "בוצע": don, "מתוכנן": len(ts), "אחוז": round(don / len(ts) * 100)})
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
    cls = "tc" + (" done" if t["is_done"] else " urgent" if t["priority"] == "דחוף" else " high" if t["priority"] == "גבוה" else "")
    icon = "✅" if t["is_done"] else ("🚨" if t["priority"] == "דחוף" else "⏳")
    rec = f' {badge(t["rec"],"gray")}' if t.get("rec") else ""
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
    c1.markdown(kpi_card(len(df), "משימות במערכת", icon="📋", color="var(--cyan)", kind="blue"), unsafe_allow_html=True)
    c2.markdown(kpi_card(inv_count, "חודשי ספירה מתועדים", icon="📦", color="var(--green)", kind="green"), unsafe_allow_html=True)
    
    overdue_tasks = get_overdue()
    c3.markdown(kpi_card(len(overdue_tasks), "משימות באיחור (שבוע אחרון)", icon="🚨", color="var(--red)", kind="red"), unsafe_allow_html=True)
