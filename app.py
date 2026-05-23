import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
from supabase import create_client, Client
import os

# --- 1. הגדרות התחברות ל-SUPABASE ---
SUPABASE_URL = "https://jvyzdftdvzufulwgldck.supabase.co"
SUPABASE_KEY = "sb_publishable_3GLq2axHGkaCPfHG79Fpyw_428KfxBQ" 

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

db = get_supabase()

# --- 2. הגדרות עמוד ועיצוב ---
st.set_page_config(page_title="אחים כהן - ניהול מחסן", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;600;700;900&display=swap');

    /* =========================
        GLOBAL RESET & THEME
       ========================= */
    :root{
        --bg-deep: #050c1a;
        --bg-panel: #0a1628;
        --bg-card: #0d1f3c;
        --bg-card-hover: #112347;
        --border: rgba(56, 139, 253, 0.18);
        --border-bright: rgba(56, 139, 253, 0.45);

        --accent-blue: #388bfd;
        --accent-cyan: #00d4ff;
        --accent-green:#00e5a0;
        --accent-amber:#f59e0b;
        --accent-red:  #ff4d6d;

        --text-primary: #ffffff;
        --text-secondary: rgba(255,255,255,0.78);

        --glow-blue: 0 0 20px rgba(56, 139, 253, 0.35);
        --glow-cyan: 0 0 20px rgba(0, 212, 255, 0.30);
        --glow-green: 0 0 220px rgba(0, 229, 160, 0.22);

        --radius-card: 16px;
        --radius-pill: 50px;
    }

    html, body, [class*="css"]{
        font-family: "Heebo", sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* =========================
        BACKGROUND — deep space
       ========================= */
    .stApp{
        background-color: var(--bg-deep) !important;
        background-image:
            linear-gradient(rgba(56, 139, 253, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(56, 139, 253, 0.04) 1px, transparent 1px),
            radial-gradient(ellipse 80% 60% at 50% 0%, rgba(56, 139, 253, 0.12) 0%, transparent 70%);
        background-size: 40px 40px, 40px 40px, 100% 100%;
    }

    /* =========================
        LOGIN / TITLE
       ========================= */
    .main-title{
        text-align: center;
        margin-top: 40px;
        margin-bottom: 40px;
        color: var(--text-primary);
        font-size: 4rem !important;
        font-weight: 900;
        letter-spacing: 2px;
        font-family: "Orbitron", monospace !important;
    }

    /* =========================
        PAGE TITLES (st.title)
       ========================= */
    .stApp h1{
        font-family: "Orbitron", monospace !important;
        color: var(--accent-cyan) !important;
        letter-spacing: 1.5px;
        text-shadow: 0 0 22px rgba(0, 212, 255, 0.35) !important;
    }
    .stApp h2, .stApp h3{
        color: var(--text-secondary) !important;
        font-family: "Heebo", sans-serif !important;
    }

    /* =========================
        SIDEBAR
       ========================= */
    section[data-testid="stSidebar"]{
        background: var(--bg-panel) !important;
        border-left: 1px solid var(--border) !important;
        box-shadow: 4px 0 32px rgba(0,0,0,0.50) !important;
    }
    section[data-testid="stSidebar"] *{
        color: var(--text-primary) !important;
    }

    /* כותרת "שלום" */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3{
        font-family: "Orbitron", monospace !important;
    }

    /* כפתור התנתקות */
    div.stButton > button[key="logout_btn"]{
        background: rgba(56, 139, 253, 0.12) !important;
        border: 1px solid var(--border-bright) !important;
        color: #fff !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-weight: 800 !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--glow-cyan) !important;
    }
    div.stButton > button[key="logout_btn"]:hover{
        background: rgba(56, 139, 253, 0.18) !important;
        transform: translateY(-1px);
    }

    /* =========================
        SIDEBAR RADIO
       ========================= */
    div[data-testid="stSidebar"] label{
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        padding: 10px 12px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stSidebar"] label:hover{
        border-color: var(--border-bright) !important;
        background: rgba(56, 139, 253, 0.10) !important;
    }

    /* =========================
        BIG LOGIN BUTTONS
       ========================= */
    div[data-testid="stColumn"] button[key^="btn_"]{
        height: 500px !important;
        width: 100% !important;
        background: linear-gradient(135deg, rgba(56, 139, 253, 0.18), rgba(56, 139, 253, 0.05)) !important;
        border: 1px solid var(--border-bright) !important;
        border-radius: 40px !important;
        color: var(--text-primary) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.25s ease !important;
        padding: 40px !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35) !important;
        position: relative;
        overflow: hidden;
    }
    div[data-testid="stColumn"] button[key^="btn_"]::after{
        content:'';
        position:absolute;
        top:-60px; left: 50%;
        transform: translateX(-50%);
        width: 280px; height: 120px;
        background: radial-gradient(ellipse, rgba(0, 212, 255, 0.28) 0%, transparent 70%);
        pointer-events:none;
        opacity: 0.9;
    }
    div[data-testid="stColumn"] button[key^="btn_"] p{
        font-size: 3.4rem !important;
        font-weight: 900 !important;
        color: #e8f0fe !important;
        line-height: 1.3 !important;
        white-space: pre-line !important;
        position: relative;
        z-index: 1;
        text-align:center !important;
        font-family: "Orbitron", monospace !important;
        letter-spacing: 1px;
    }
    div[data-testid="stColumn"] button[key^="btn_"]:hover{
        transform: translateY(-8px) !important;
        border-color: rgba(0, 212, 255, 0.70) !important;
        box-shadow: var(--glow-cyan), 0 16px 46px rgba(0,0,0,0.52) !important;
    }

    /* =========================
        STREAMLIT METRICS
       ========================= */
    [data-testid="stMetric"]{
        background: var(--bg-card) !important;
        padding: 24px 20px !important;
        border-radius: var(--radius-card) !important;
        border: 1px solid var(--border) !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.04) !important;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stMetric"]:hover{
        transform: translateY(-3px) !important;
        box-shadow: var(--glow-blue), 0 8px 32px rgba(0,0,0,0.40) !important;
        border-color: var(--border-bright) !important;
    }
    [data-testid="stMetricLabel"]{
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"]{
        color: var(--accent-cyan) !important;
        font-family: "Orbitron", monospace !important;
        font-weight: 900 !important;
        font-size: 2rem !important;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.40);
    }

    /* =========================
        FORM ELEMENTS
       ========================= */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stDateInput input{
        background: rgba(13, 31, 60, 0.88) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }

    label[data-testid="stWidgetLabel"] p{
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px;
    }

    /* כפתורי Streamlit (כללי) */
    .stButton > button{
        background: linear-gradient(135deg, rgba(56, 139, 253, 0.14), rgba(56, 139, 253, 0.04)) !important;
        border: 1px solid var(--border-bright) !important;
        color: var(--accent-cyan) !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.25) !important;
    }
    .stButton > button:hover{
        transform: translateY(-1px) !important;
        border-color: rgba(0, 212, 255, 0.70) !important;
        box-shadow: var(--glow-blue), 0 10px 26px rgba(0,0,0,0.35) !important;
    }

    /* =========================
        TASK CARDS (DASHBOARD)
       ========================= */
    .task-card{
        background: rgba(13, 31, 60, 0.72) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 18px 18px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.30) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        position: relative;
        overflow: hidden;
        transition: transform 0.15s ease, background 0.15s ease !important;
        color: var(--text-primary) !important;
        border-right: 6px solid var(--accent-blue) !important;
    }
    .task-card:hover{
        transform: translateY(-2px);
        background: rgba(17, 35, 71, 0.78) !important;
    }
    .task-card__top{
        display:flex;
        align-items:center;
        gap: 10px;
        margin-bottom: 8px;
    }
    .task-card__icon{
        width: 30px;
        height: 30px;
        display:flex;
        align-items:center;
        justify-content:center;
        border-radius: 10px;
        background: rgba(0, 212, 255, 0.10);
        border: 1px solid rgba(0, 212, 255, 0.20);
        font-family: "Orbitron", monospace !important;
    }
    .task-card__desc{
        color: var(--text-secondary);
        line-height: 1.45;
        font-size: 0.98rem;
    }

    .task-card--done{
        border-right-color: var(--accent-green) !important;
    }
    .task-card--done .task-card__icon{
        background: rgba(0, 229, 160, 0.12);
        border-color: rgba(0, 229, 160, 0.24);
    }
    .task-card--pending{
        border-right-color: var(--accent-amber) !important;
    }
    .task-card--pending .task-card__icon{
        background: rgba(245, 158, 11, 0.12);
        border-color: rgba(245, 158, 11, 0.24);
    }

    /* =========================
        WORK PAGE
       ========================= */
    .day-chip{
        background: linear-gradient(135deg, rgba(56, 139, 253, 0.20), rgba(13, 31, 60, 0.65)) !important;
        color: #e8f0fe !important;
        padding: 12px 10px !important;
        border-radius: 12px !important;
        text-align: center !important;
        border: 1px solid rgba(56, 139, 253, 0.35) !important;
        box-shadow: var(--glow-blue) !important;
        font-weight: 900 !important;
        margin-bottom: 10px !important;
        font-family: "Orbitron", monospace !important;
        letter-spacing: 0.6px;
    }

    .task-line{
        background: rgba(13, 31, 60, 0.52) !important;
        border: 1px solid rgba(56, 139, 253, 0.18) !important;
        border-radius: 12px !important;
        padding: 10px 12px !important;
        color: var(--text-primary) !important;
        margin-bottom: 10px !important;
        box-shadow: 0 6px 22px rgba(0,0,0,0.25) !important;
    }
    .task-line--done{
        border-color: rgba(0, 229, 160, 0.30) !important;
        background: rgba(0, 229, 160, 0.08) !important;
    }

    /* checkbox styling */
    .stCheckbox label{
        color: rgba(255,255,255,0.92) !important;
        font-weight: 700 !important;
    }
    .stCheckbox input:checked ~ div{
        box-shadow: var(--glow-green) !important;
    }

    /* =========================
        CALENDAR (FullCalendar)
       ========================= */
    .fc-theme-standard .fc-scrollgrid,
    .fc-theme-standard td,
    .fc-theme-standard th{
        border-color: rgba(56, 139, 253, 0.18) !important;
    }
    .fc{
        background: transparent !important;
        color: #e8f0fe !important;
    }
    .fc .fc-toolbar-title{
        font-family: "Orbitron", monospace !important;
        letter-spacing: 0.6px;
        color: #00d4ff !important;
        font-weight: 900 !important;
    }
    .fc-button{
        background: rgba(13, 31, 60, 0.65) !important;
        border: 1px solid rgba(56, 139, 253, 0.35) !important;
        color: #e8f0fe !important;
        border-radius: 12px !important;
    }
    .fc-button:hover{
        background: rgba(17, 35, 71, 0.78) !important;
    }

    /* =========================
        MANAGE PAGE
       ========================= */
    button[key^="del_"]{
        background: rgba(255, 77, 109, 0.10) !important;
        border: 1px solid rgba(255, 77, 109, 0.35) !important;
        color: #ffb3c0 !important;
    }
    button[key^="del_"]:hover{
        box-shadow: 0 0 22px rgba(255, 77, 109, 0.25) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. פונקציות עבודה ---
def load_data():
    try:
        res = db.table("tasks").select("*").execute()
        df = pd.DataFrame(res.data)
        if df.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])
        df.columns = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"]
        return df
    except:
        return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])

def save_new_task(name, desc, freq, date):
    new_id = int(datetime.now().timestamp())
    db.table("tasks").insert({
        "id": new_id, "task_name": name, "description": desc,
        "recurring": freq, "task_date": str(date), "done_dates": ""
    }).execute()

def update_done_dates(t_id, done_str):
    db.table("tasks").update({"done_dates": done_str}).eq("id", t_id).execute()

def delete_task(t_id):
    db.table("tasks").delete().eq("id", t_id).execute()

def get_daily_status(df_input, target_date):
    if df_input.empty: return []
    scheduled = []
    target_str = target_date.strftime("%Y-%m-%d")
    for _, row in df_input.iterrows():
        try:
            base = pd.to_datetime(row['Date']).date()
            diff = (target_date.date() - base).days
            if diff >= 0:
                f = row['Recurring']
                hit = (f == "לא" and diff == 0) or (f == "יומי") or \
                      (f == "שבועי" and diff % 7 == 0) or \
                      (f == "דו-שבועי" and diff % 14 == 0) or \
                      (f == "חודשי" and diff % 30 == 0)
                if hit:
                    done_dates = str(row['Done_Dates']).strip()
                    is_done = target_str in done_dates.split(",") if done_dates else False
                    scheduled.append({
                        "id": row['ID'], "name": row['Task_Name'], 
                        "desc": row['Description'], "is_done": is_done, 
                        "done_str": done_dates
                    })
        except: continue
    return scheduled

# --- 4. ניהול מצב ---
if "user_role" not in st.session_state: st.session_state.user_role = None
if "current_page" not in st.session_state: st.session_state.current_page = None

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# --- 5. מסך כניסה ---
if st.session_state.user_role is None:
    st.markdown('<h1 class="main-title">אחים כהן - ניהול משימות מחסן</h1>', unsafe_allow_html=True)
    st.write("##")
    
    cols = st.columns(3, gap="large")
    roles = [
        {"role": "סמנכ\"ל", "icon": "📊", "id": "vp"},
        {"role": "צוות מחסן", "icon": "📦", "id": "staff"},
        {"role": "מנהל WMS", "icon": "🔑", "id": "admin"}
    ]
    
    for i, col in enumerate(cols):
        with col:
            r = roles[i]
            if st.button(f"{r['icon']}\n\n\n{r['role']}", key=f"btn_{r['id']}", use_container_width=True):
                st.session_state.user_role = r['role']
                st.session_state.current_page = OPT_WORK if r['role'] == "צוות מחסן" else OPT_DASH
                st.rerun()
    st.stop()

# --- 6. תפריט צד ---
df = load_data()
if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
else: menu = [OPT_DASH, OPT_CAL]

with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.user_role} 👋")
    choice = st.radio("ניווט:", menu)
    st.session_state.current_page = choice
    if st.button("🚪 התנתקות", key="logout_btn"):
        st.session_state.user_role = None
        st.rerun()

# --- 7. דפי המערכת ---
if choice == OPT_DASH:
    st.title(OPT_DASH)
    tasks = get_daily_status(df, datetime.now())
    t_count, d_count = len(tasks), sum(1 for t in tasks if t['is_done'])
    c1, c2, c3 = st.columns(3)
    c3.metric("משימות היום", t_count)
    c2.metric("בוצעו", d_count)
    c1.metric("אחוז ביצוע", f"{int(d_count/t_count*100) if t_count>0 else 0}%")
    st.divider()
    for t in tasks:
        status_class = "task-card task-card--done" if t['is_done'] else "task-card task-card--pending"
        status_icon = "✅" if t['is_done'] else "⏳"
        st.markdown(
            f'<div class="{status_class}">'
            f'  <div class="task-card__top">'
            f'    <span class="task-card__icon">{status_icon}</span>'
            f'    <b>{t["name"]}</b>'
            f'  </div>'
            f'  <div class="task-card__desc">{t["desc"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

elif choice == OPT_WORK:
    st.title(OPT_WORK)
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    cols = st.columns(5)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    for i, day_name in enumerate(days_names):
        curr_day = start_of_week + timedelta(days=i)
        curr_str = curr_day.strftime("%Y-%m-%d")
        with cols[4-i]:
            st.markdown(
                f"<div class='day-chip'>{day_name} {curr_day.strftime('%d/%m')}</div>",
                unsafe_allow_html=True
            )
            for t in get_daily_status(df, curr_day):
                if t['is_done']:
                    st.markdown(f"<div class='task-line task-line--done'>✅ {t['name']}</div>", unsafe_allow_html=True)
                elif st.checkbox(f"⏳ {t['name']}", key=f"chk_{t['id']}_{curr_str}"):
                    update_done_dates(t['id'], f"{t['done_str']},{curr_str}".strip(","))
                    st.rerun()

elif choice == OPT_CAL:
    st.title(OPT_CAL)
    events = []
    for _, row in df.iterrows():
        try:
            base, freq = pd.to_datetime(row['Date']), row['Recurring']
            for i in range(30):
                gap = 0 if freq=="לא" else 1 if freq=="יומי" else 7 if freq=="שבועי" else 14 if freq=="דו-שבועי" else 30
                d = (base + timedelta(days=i * gap)).strftime("%Y-%m-%d")
                events.append({"title": row['Task_Name'], "start": d, "color": "#10b981" if d in str(row['Done_Dates']) else "#ef4444"})
                if freq == "לא": break
        except: continue
    calendar(
        events=events,
        options={"direction": "rtl", "locale": "he"},
        key="warehouse_cal",
        custom_css="""
        .fc {
          background: transparent !important;
          color: #e8f0fe !important;
          font-family: "Heebo", sans-serif !important;
        }
        .fc .fc-toolbar-title{
          color: #00d4ff !important;
          font-family: "Orbitron", monospace !important;
          font-weight: 900 !important;
          letter-spacing: 0.6px;
        }
        .fc .fc-scrollgrid{
          border-color: rgba(56, 139, 253, 0.18) !important;
        }
        .fc .fc-daygrid-day{
          background: rgba(13, 31, 60, 0.22) !important;
        }
        .fc .fc-daygrid-day-number{
          color: rgba(255,255,255,0.86) !important;
          font-weight: 800 !important;
        }
        .fc .fc-daygrid-day-top{
          justify-content: center !important;
        }
        .fc .fc-button{
          background: rgba(13, 31, 60, 0.65) !important;
          border: 1px solid rgba(56, 139, 253, 0.35) !important;
          color: #e8f0fe !important;
          border-radius: 12px !important;
        }
        .fc .fc-button:hover{
          background: rgba(17, 35, 71, 0.78) !important;
        }
        .fc .fc-daygrid-event{
          border-radius: 14px !important;
          padding: 6px 10px !important;
          border: 1px solid rgba(56, 139, 253, 0.25) !important;
        }
        """
    )

elif choice == OPT_ADD:
    st.title(OPT_ADD)
    with st.form("add_new"):
        name, desc = st.text_input("שם המשימה"), st.text_area("תיאור")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        date = st.date_input("תאריך התחלה", datetime.now())
        if st.form_submit_button("שמור בענן ☁️"):
            if name: 
                save_new_task(name, desc, freq, date)
                st.rerun()

elif choice == OPT_MANAGE:
    st.title(OPT_MANAGE)
    for _, row in df.iterrows():
        col1, col2 = st.columns([4, 1])
        col1.markdown(
            f"<div class='task-card' style='margin-bottom:0; padding:14px 16px;'>"
            f"  <div class='task-card__top' style='margin-bottom:6px;'>"
            f"    <span class='task-card__icon'>⚙️</span>"
            f"    <b>{row['Task_Name']}</b>"
            f"  </div>"
            f"  <div class='task-card__desc' style='margin-top:4px;'>{row['Recurring']}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        if col2.button("מחק", key=f"del_{row['ID']}"):
            delete_task(row['ID'])
            st.rerun()
