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
    import plotly.io as pio  
    
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
    initial_sidebar_state="expanded",
    page_icon="📦",
)

ADMIN_HASH = hashlib.sha256(b"1234").hexdigest()
SESSION_MINS = 60
PRIS  = ["רגיל", "דחוף", "גבוה", "נמוך"]
CATS  = ["כללי", "בטיחות", "לוגיסטיקה", "ניקיון", "תחזוקה", "ספירה"]
RECUR = ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"]
MONTHS_HE = ["ינואר","פברואר","מרץ","אפריל","מאי","יוני",
             "יולי","אוקטובר","ספטמבר","אוקטובר","נובמבר","דצמבר"]


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
  bottom: 0; left: 0; right: 0;
  height: 1px;
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
  top: 0; right: 0;
  width: 100%; height: 3px;
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
    
    overdue = get_overdue()
    if overdue:
        st.markdown(
            f'<div class="al al-red">🚨 <div><b style="color:var(--red);font-size:1rem">'
            f'{len(overdue)} משימות שלא בוצעו בשבוע האחרון</b>'
            f'<div style="color:var(--txt2);font-size:.8rem;margin-top:2px">'
            f'לחץ להצגה וסגירה</div></div></div>', unsafe_allow_html=True)
        with st.expander("📋 פירוט פיגורים וסגירתם"):
            for t in overdue:
                c1, c2 = st.columns([5, 1])
                c1.markdown(task_card_html(t), unsafe_allow_html=True)
                if c2.button("✓", key=f"ov_{t['id']}_{t['date']}"):
                    mark_done(t["id"], t["date"]); st.rerun()
                    
    dc, _ = st.columns([1, 3])
    sel = dc.date_input("📅 תאריך", today)
    dstr = sel.strftime("%Y-%m-%d")
    
    ts = tasks_for_date(df, sel)
    tot = len(ts); don = sum(1 for t in ts if t["is_done"])
    pct = round(don / tot * 100) if tot else 0
    
    c1, c2 = st.columns([7, 3])
    with c1:
        sec_header(f"📋 משימות ליום {sel.strftime('%d/%m/%Y')}")
        if not ts:
            st.info("🌴 אין משימות מתוכננות ליום זה")
        else:
            for t in ts:
                col_card, col_btn = st.columns([6, 1])
                col_card.markdown(task_card_html(t), unsafe_allow_html=True)
                if not t["is_done"]:
                    if col_btn.button("בצע", key=f"d_{t['id']}_{dstr}", use_container_width=True):
                        mark_done(t["id"], dstr); st.rerun()
                        
    with c2:
        sec_header("📊 סטטוס יומי")
        st.markdown(kpi_card(f"{don}/{tot}", f"הושלמו היום ({pct}%)", sub=sel.strftime("%B"), color="var(--green)" if pct>=80 else "var(--cyan)", icon="🎯"), unsafe_allow_html=True)
        st.markdown(pbar(pct, height=12), unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top:20px"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-row"><span class="stat-label">משימות פתוחות:</span><span class="stat-val" style="color:var(--amber)">{tot-don}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-row"><span class="stat-label">סגורות:</span><span class="stat-val" style="color:var(--green)">{don}</span></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: EXTERNAL STORAGE
# ═══════════════════════════════════════════════════════════════════════════════
def page_external_storage():
    st.markdown("### 🏠 ניהול ובקרת אחסנה חיצונית")
    st.markdown('<div style="color:var(--txt2);font-size:.85rem;margin-bottom:15px">מעקב מלא אחר מלאי משטחים המאוחסנים במחסנים חיצוניים</div>', unsafe_allow_html=True)
    
    role = st.session_state.get("user_role")
    is_admin = (role == "מנהל WMS")
    supabase = get_conn()
    
    try:
        res = supabase.table("external_storage").select("*").order("warehouse_name").execute()
        warehouses = res.data if res.data else []
    except Exception as e:
        st.error(f"שגיאה בטעינת נתוני מחסנים: {e}")
        warehouses = []

    total_warehouses = len(warehouses)
    total_pallets = sum(int(w.get("pallets_count", 0)) for w in warehouses)
    
    k1, k2 = st.columns(2)
    k1.markdown(kpi_card(total_warehouses, "סך הכל מחסנים חיצוניים", icon="🏢", kind="blue"), unsafe_allow_html=True)
    k2.markdown(kpi_card(total_pallets, "סך הכל משטחים באחסנה חיצוני", icon="📦", color="var(--amber)", kind="blue"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    if is_admin:
        tab1, tab2, tab3 = st.columns([4, 4, 4])
        
        with tab1:
            sec_header("➕ הוספת מחסן חיצוני חדש")
            with st.form("add_warehouse_form", clear_on_submit=True):
                w_name = st.text_input("שם המחסן / אתר האחסון")
                w_pallets = st.number_input("כמות משטחים ראשונית", min_value=0, step=1, value=0)
                submit_add = st.form_submit_button("🚀 צור מחסן חדש")
                
                if submit_add:
                    if not w_name.strip():
                        st.error("⚠️ חובה להזין שם מחסן תקין")
                    else:
                        try:
                            supabase.table("external_storage").insert({
                                "warehouse_name": w_name.strip(),
                                "pallets_count": int(w_pallets)
                            }).execute()
                            st.success(f"✅ מחסן '{w_name}' נוצר בהצלחה!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ שגיאה: ייתכן שהמחסן כבר קיים במערכת ({e})")
                            
        with tab2:
            sec_header("⚙️ עדכון כמות משטחים")
            if not warehouses:
                st.info("אין מחסנים לעדכון")
            else:
                w_options = [w["warehouse_name"] for w in warehouses]
                selected_w = st.selectbox("בחר מחסן לעדכון", w_options)
                
                current_pallets = next(w["pallets_count"] for w in warehouses if w["warehouse_name"] == selected_w)
                updated_pallets = st.number_input("כמות משטחים חדשה", min_value=0, step=1, value=int(current_pallets), key="update_pal_input")
                
                if st.button("💾 שמור עדכון מלאי", use_container_width=True):
                    try:
                        supabase.table("external_storage").update({
                            "pallets_count": int(updated_pallets),
                            "updated_at": datetime.now().isoformat()
                        }).eq("warehouse_name", selected_w).execute()
                        st.success(f"✅ המלאי במחסן '{selected_w}' עודכן ל-{updated_pallets} משטחים!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה בעדכון כמות המשטחים: {e}")
                        
        with tab3:
            sec_header("🗑️ הסרת מחסן מהמערכת")
            if not warehouses:
                st.info("אין מחסנים להסרה")
            else:
                w_delete_options = [w["warehouse_name"] for w in warehouses]
                to_delete = st.selectbox("בחר מחסן למחיקה לצמיתות", w_delete_options, key="del_selectbox")
                
                if st.button("🚨 מחק מחסן לחלוטין", use_container_width=True):
                    try:
                        supabase.table("external_storage").delete().eq("warehouse_name", to_delete).execute()
                        st.success(f"🗑️ המחסן '{to_delete}' הוסר בהצלחה מהרשימה")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה במחיקת המחסן: {e}")
                        
        st.markdown("---")
        sec_header("📋 מצב מלאי נוכחי (תצוגת מנהל)")
    else:
        sec_header("📋 מצב מלאי נוכחי באחסנה חיצונית")
        
    if not warehouses:
        st.info("הטבלה ריקה. אין נתוני אחסנה חיצונית במערכת כרגע.")
    else:
        table_data = []
        for w in warehouses:
            raw_date = w.get("updated_at")
            formatted_date = "-"
            if raw_date:
                try:
                    formatted_date = datetime.fromisoformat(raw_date.split(".")[0].replace("Z", "")).strftime("%d/%m/%Y %H:%M")
                except:
                    formatted_date = str(raw_date)
                    
            table_data.append({
                "שם המחסן / אתר": w.get("warehouse_name"),
                "כמות משטחים במלאי": w.get("pallets_count"),
                "עדכון אחרון": formatted_date
            })
            
        df_display = pd.DataFrame(table_data)
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: WORK (SCHEDULE)
# ═══════════════════════════════════════════════════════════════════════════════
def page_work():
    df = db_load_tasks()
    today = datetime.now().date()
    start_week = today - timedelta(days=today.weekday())
    
    sec_header(f"📋 סידור עבודה שבועי — משימות פתוחות")
    
    cols = st.columns(7)
    DAYS_HE = ["שני","שלישי","רביעי","חמישי","שישי","שבת","ראשון"]
    for i in range(7):
        d = start_week + timedelta(days=i)
        ts = tasks_for_date(df, d, skip_weekend=False)
        open_count = sum(1 for t in ts if not t["is_done"])
        
        with cols[i]:
            st.markdown(
                f'<div class="wchip">'
                f'<div class="day-name">{DAYS_HE[i]}</div>'
                f'<div class="day-date">{d.strftime("%d/%m")}</div>'
                f'<div class="day-count" style="color:var(--{"green" if not open_count else "amber"})">'
                f'{open_count} פתוחות</div>'
                f'</div>', unsafe_allow_html=True)
                
    st.markdown('<div style="margin-top:20px"></div>', unsafe_allow_html=True)
    
    for i in range(7):
        d = start_week + timedelta(days=i)
        ts = [t for t in tasks_for_date(df, d, skip_weekend=False) if not t["is_done"]]
        
        if ts:
            with st.expander(f"📅 {DAYS_HE[i]} ({d.strftime('%d/%m')}) — {len(ts)} משימות פתוחות", expanded=(d==today)):
                for t in ts:
                    c1, c2 = st.columns([6, 1])
                    c1.markdown(task_card_html(t), unsafe_allow_html=True)
                    if c2.button("בצע", key=f"wk_{t['id']}_{t['date']}", use_container_width=True):
                        mark_done(t["id"], t["date"]); st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════
def page_calendar():
    if not HAS_CAL:
        st.warning("⚠️ streamlit-calendar אינו מותקן. לא ניתן להציג לוח שנה אינטראקטיבי.")
        return
        
    df = db_load_tasks()
    sec_header("📅 לוח שנה משימות")
    
    events = []
    today = datetime.now().date()
    for i in range(-30, 60):
        d = today + timedelta(days=i)
        ts = tasks_for_date(df, d, skip_weekend=False)
        for t in ts:
            color = "#00ff88" if t["is_done"] else ("#ff2d55" if t["priority"] == "דחוף" else "#00d4ff")
            events.append({
                "id": f"{t['id']}_{t['date']}",
                "title": f"{'✅' if t['is_done'] else '⏳'} {t['name']}",
                "start": t["date"],
                "end": t["date"],
                "backgroundColor": color,
                "borderColor": color,
                "allDay": True
            })
            
    cal_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
        "initialView": "dayGridMonth",
        "direction": "rtl",
        "locale": "he"
    }
    
    st_calendar(events=events, options=cal_options, custom_css="""
        .fc { font-family: var(--heb); background: var(--card); padding:20px; border-radius:14px; border:1px solid var(--b1); }
        .fc-col-header-cell { background: var(--bg2); color: var(--cyan); padding: 8px 0; }
        .fc-daygrid-day:hover { background: rgba(0,212,255,.03); }
        .fc-event { cursor:pointer; font-weight:600; padding: 2px 4px; }
    """)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: INVENTORY COUNT
# ═══════════════════════════════════════════════════════════════════════════════
def page_inventory():
    sec_header("📦 דשבורד ובקרת ספירות מלאי")
    
    if st.session_state.user_role == "מנהל WMS":
        with st.expander("➕ הזנת נתוני ספירת מלאי חודשית חדשה / עדכון"):
            with st.form("inv_form"):
                c1, c2 = st.columns(2)
                y_sel = c1.selectbox("שנה", [2025, 2026, 2027], index=1)
                m_sel = c2.selectbox("חודש", list(range(1, 13)), format_func=lambda x: MONTHS_HE[x-1])
                
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                skus_t = c1.number_input("סך פריטים במחסן (SKUs)", min_value=1, value=1500)
                skus_c = c1.number_input("פריטים שנספרו בפועל", min_value=0, value=1500)
                
                locs_t = c2.number_input("סך מיקומים במחסן", min_value=1, value=3000)
                locs_c = c2.number_input("מיקומים שנספרו בפועל", min_value=0, value=3000)
                
                no_g   = c3.number_input("מיקומים שנמצאו ללא פער (פיקס)", min_value=0, value=2950)
                
                if st.form_submit_button("💾 שמור נתוני ספירה"):
                    m_str = f"{y_sel}-{m_sel:02d}"
                    db_save_inventory(m_str, skus_t, skus_c, locs_t, locs_c, no_g)
                    st.success(f"✅ נתוני הספירה לחודש {MONTHS_HE[m_sel-1]} {y_sel} נשמרו בהצלחה!")
                    st.rerun()
                    
    hist = db_load_inventory()
    if not hist:
        st.info("אין נתוני ספירות מלאי במערכת")
        return
        
    latest = hist[0]
    
    st.markdown(f"### 📊 סטטוס ספירה אחרונה: {latest['month']}")
    c1, c2, c3, c4 = st.columns(4)
    
    sku_pct = round(latest["skus_counted"] / latest["skus_total"] * 100)
    loc_pct = round(latest["locs_counted"] / latest["locs_total"] * 100)
    acc_pct = round(latest["no_gap"] / latest["locs_counted"] * 100) if latest["locs_counted"] else 0
    
    c1.markdown(kpi_card(f"{sku_pct}%", "התקדמות פריטים", f"{latest['skus_counted']:,} / {latest['skus_total']:,}", color="var(--cyan)", icon="🔬"), unsafe_allow_html=True)
    c2.markdown(kpi_card(f"{loc_pct}%", "התקדמות מיקומים", f"{latest['locs_counted']:,} / {latest['locs_total']:,}", color="var(--cyan)", icon="📍"), unsafe_allow_html=True)
    c3.markdown(kpi_card(f"{acc_pct}%", "דיוק מלאי (מבוסס מיקום)", f"{latest['no_gap']:,} פיקס", color="var(--green)" if acc_pct>=95 else "var(--amber)", icon="🎯", kind="green" if acc_pct>=95 else "blue"), unsafe_allow_html=True)
    c4.markdown(kpi_card(f"{latest['locs_counted'] - latest['no_gap']:,}", "מיקומים עם פער", "דורש בדיקה / התאמה", color="var(--red)" if (latest['locs_counted'] - latest['no_gap'])>0 else "var(--txt2)", icon="🚨", kind="red" if (latest['locs_counted'] - latest['no_gap'])>0 else "blue"), unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top:25px"></div>', unsafe_allow_html=True)
    sec_header("⏳ היסטוריית ספירות מלאי")
    
    rows = []
    for h in hist:
        stot = h["skus_total"]; scnt = h["skus_counted"]
        ltot = h["locs_total"]; lcnt = h["locs_counted"]
        ng   = h["no_gap"]
        rows.append({
            "חודש":       h["month"],
            "פריטים במחסן":   f"{stot:,}",
            "נספרו (פריטים)": f"{scnt:,} ({round(scnt/stot*100)}%)",
            "סך מיקומים":     f"{ltot:,}",
            "נספרו (מיקומים)": f"{lcnt:,} ({round(lcnt/ltot*100)}%)",
            "מיקומים תקינים": f"{ng:,}",
            "דיוק מלאי":      f"{round(ng/lcnt*100) if lcnt else 0}%"
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: ADD TASK
# ═══════════════════════════════════════════════════════════════════════════════
def page_add():
    if st.session_state.user_role != "מנהל WMS":
        st.warning("🔒 מדור זה פתוח למנהל מערכת בלבד")
        return
        
    sec_header("➕ הוספת משימת תפעול / תחזוקה חדשה")
    
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("🎯 שם המשימה", placeholder="לדוגמה: ביקורת מטפים, ריענון מלאי...")
        desc = st.text_area("📝 תיאור והנחיות לביצוע")
        
        c1, c2, c3 = st.columns(3)
        recurring = c1.selectbox("🔁 מחזוריות", RECUR)
        priority  = c2.selectbox("🚨 עדיפות", PRIS)
        category  = c3.selectbox("📦 קטגוריה", CATS)
        
        start_date = st.date_input("📅 תאריך תחילת תוקף / ביצוע", datetime.now())
        
        if st.form_submit_button("🚀 צור משימה והפץ למערכת"):
            if not name.strip(): st.error("❌ לא ניתן ליצור משימה ללא שם")
            else:
                new_id = db_add_task(name, desc, recurring, start_date, priority, category)
                st.success(f"🎉 המשימה נוצרה בהצלחה במערכת! (ID: {new_id})")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: MANAGE TASKS
# ═══════════════════════════════════════════════════════════════════════════════
def page_manage():
    if st.session_state.user_role != "מנהל WMS":
        st.warning("🔒 מדור זה פתוח למנהל מערכת בלבד")
        return
        
    sec_header("⚙️ ניהול, עריכה ומחיקת משימות")
    df = db_load_tasks()
    
    if df.empty:
        st.info("אין משימות לניהול")
        return
        
    for idx, row in df.iterrows():
        with st.expander(f"⚙️ {row['Task_Name']} [{row['Priority']}] — {row['Recurring']}"):
            with st.form(f"ed_{row['ID']}"):
                ename = st.text_input("שם המשימה", row["Task_Name"])
                edesc = st.text_area("תיאור", row["Description"])
                
                c1, c2, c3 = st.columns(3)
                erec  = c1.selectbox("מחזוריות", RECUR, index=RECUR.index(row["Recurring"]) if row["Recurring"] in RECUR else 0)
                epri  = c2.selectbox("עדיפות", PRIS, index=PRIS.index(row["Priority"]) if row["Priority"] in PRIS else 0)
                ecat  = c3.selectbox("קטגוריה", CATS, index=CATS.index(row["Category"]) if row["Category"] in CATS else 0)
                
                edat  = st.date_input("תאריך", pd.to_datetime(row["Date"]))
                
                cc1, cc2 = st.columns(2)
                if cc1.form_submit_button("💾 שמור שינויים", use_container_width=True):
                    db_update_task(row["ID"], ename, edesc, erec, edat, epri, ecat)
                    st.success("העדכון נשמר")
                    st.rerun()
                if cc2.form_submit_button("🗑️ מחק משימה לחלוטין", use_container_width=True):
                    db_delete_task(row["ID"])
                    st.success("המשימה נמחקה")
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    sec_header("🔬 אנליטיקס מתקדם וניתוח מגמות ביצוע")
    
    if not HAS_PLOTLY:
        st.warning("⚠️ ספריית Plotly אינה מותקנת. לא ניתן להציג גרפים מתקדמים.")
        return
        
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📈 קצב ביצוע משימות (14 ימים אחרונים)")
        w_df = week_stats(14)
        if not w_df.empty:
            fig = px.line(w_df, x="תאריך", y="אחוז", text="אחוז", markers=True,
                          labels={"אחוז":"אחוז ביצוע (%)"})
            fig.update_traces(line_color= "#00d4ff", line_width=3, marker_size=8, textposition="top center")
            fig.update_layout(height=300, margin=dict(l=20,r=20,t=20,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
    with c2:
        st.markdown("#### 📊 מפת קטגוריות משימות")
        df = db_load_tasks()
        if not df.empty:
            cat_counts = df["Category"].value_counts().reset_index()
            cat_counts.columns = ["קטגוריה", "כמות"]
            fig2 = px.bar(cat_counts, x="קטגוריה", y="כמות", color="קטגוריה",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_layout(height=300, showlegend=False, margin=dict(l=20,r=20,t=20,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    check_timeout()
    
    role = st.session_state.user_role
    if not role:
        login_screen()
        return
        
    st.sidebar.markdown(
        f'<div style="text-align:center;padding:10px 0;margin-bottom:15px">'
        f'<h3 style="color:var(--cyan);font-family:var(--orb);margin:0">📦 WMS PANEL</h3>'
        f'<span class="b b-blue" style="font-size:.7rem">{role}</span>'
        f'</div>', unsafe_allow_html=True)
        
    lt = st.session_state.get("login_time", datetime.now())
    elapsed_min = int((datetime.now() - lt).total_seconds() // 60)
    
    MENUS = {
        "מנהל WMS": [
            "📊 דשבורד",
            "🏠 אחסנה חיצונית",  
            "📋 סידור עבודה",
            "📅 לוח שנה",
            "📦 ספירות מלאי",
            "➕ הוספת משימה",
            "⚙️ ניהול משימות",
            "🔬 אנליטיקס",
        ],
        "צוות מחסן": [
            "📊 דשבורד",
            "🏠 אחסנה חיצונית",  
            "📋 סידור עבודה",
            "📅 לוח שנה",
            "📦 ספירות מלאי",
        ],
        "הנהלה": [
            "📊 דשבורד",
            "🏠 אחסנה חיצונית",  
            "📦 ספירות מלאי",
            "🔬 אנליטיקס",
        ]
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
        "📊 דשבורד":        "📊 דשבורד בקרה",
        "🏠 אחסנה חיצונית": "🏠 אחסנה חיצונית",
        "📋 סידור עבודה":   "📋 סידור עבודה שבועי",
        "📅 לוח שנה":       "📅 לוח שנה",
        "➕ הוספת משימה":   "➕ הוספת משימה חדשה",
        "⚙️ ניהול משימות":  "⚙️ ניהול ועריכת משימות",
        "📦 ספירות מלאי":   "📦 דשבורד ספירות מלאי",
        "🔬 אנליטיקס":      "🔬 אנליטיקס מתקדם",
    }
    
    st.markdown(
        f'<div class="mega-banner" style="padding:18px 32px;margin-bottom:20px">'
        f'<h1 style="font-size:1.4rem !important;letter-spacing:2px !important">{PAGE_ICONS.get(choice, choice)}</h1>'
        f'<div class="sub"><span class="live-dot"></span> מחובר כעת: {role}</div>'
        f'</div>', unsafe_allow_html=True)
        
    if choice == "📊 דשבורד":
        page_dashboard()
    elif choice == "🏠 אחסנה חיצונית":
        page_external_storage()
    elif choice == "📋 סידור עבודה":
        page_work()
    elif choice == "📅 לוח שנה":
        page_calendar()
    elif choice == "📦 ספירות מלאי":
        page_inventory()
    elif choice == "➕ הוספת משימה":
        page_add()
    elif choice == "⚙️ ניהול משימות":
        page_manage()
    elif choice == "🔬 אנליטיקס":
        page_analytics()


if __name__ == "__main__":
    main()
