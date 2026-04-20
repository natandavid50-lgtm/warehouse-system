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
    .stApp { 
        background-color: #020617;
        direction: rtl;
        text-align: right;
    }
    
    /* עיצוב גלובלי לכפתורי הכניסה הגדולים */
    div[data-testid="stColumn"] button[key^="btn_"] {
        height: 320px !important;
        width: 100% !important;
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 20px !important;
        color: #10b981 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 15px !important;
        transition: all 0.4s ease !important;
        padding: 20px !important;
    }

    div[data-testid="stColumn"] button[key^="btn_"]:hover {
        transform: translateY(-12px) !important;
        border-color: #10b981 !important;
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.2) !important;
        background-color: #1e293b !important;
    }

    /* תיקון הטקסט בתוך הכפתור הגדול */
    div[data-testid="stColumn"] button[key^="btn_"] p {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        line-height: 1.4 !important;
        white-space: pre-wrap !important;
    }

    /* עיצוב כפתורים רגילים (התנתקות, מחק וכו') - שומר על העיצוב המקורי שלך */
    div.stButton > button:not([key^="btn_"]) {
        background-color: #000000 !important;
        color: #10b981 !important;
        border: 2px solid #10b981 !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-weight: bold !important;
        width: 100%;
        transition: 0.3s;
    }
    
    div.stButton > button:not([key^="btn_"]):hover {
        background-color: #10b981 !important;
        color: #000000 !important;
    }

    section[data-testid="stSidebar"] { background-color: #020617 !important; border-left: 1px solid #1e293b; }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    .task-card {
        background: #0f172a;
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-right: 6px solid #10b981; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
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
    st.markdown("<h1 style='text-align: center; margin-top: 50px; color: white;'>אחים כהן - ניהול משימות מחסן</h1>", unsafe_allow_html=True)
    st.write("") # מרווח
    
    cols = st.columns(3, gap="large")
    roles = [
        {"role": "סמנכ\"ל", "icon": "📊", "id": "vp"},
        {"role": "צוות מחסן", "icon": "📦", "id": "staff"},
        {"role": "מנהל WMS", "icon": "🔑", "id": "admin"}
    ]
    
    for i, col in enumerate(cols):
        with col:
            r = roles[i]
            # לחיצה על כל הכרטיס
            if st.button(f"{r['icon']}\n\n{r['role']}", key=f"btn_{r['id']}", use_container_width=True):
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
        color = "#10b981" if t['is_done'] else "#f59e0b"
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><b>{t["name"]}</b><br>{t["desc"]}</div>', unsafe_allow_html=True)

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
            st.markdown(f"<div style='background:#1e293b; color:white; padding:10px; border-radius:10px; text-align:center;'>{day_name} {curr_day.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            for t in get_daily_status(df, curr_day):
                if t['is_done']: st.success(f"✅ {t['name']}")
                elif st.checkbox(f"בצע: {t['name']}", key=f"chk_{t['id']}_{curr_str}"):
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
    calendar(events=events, options={"direction": "rtl", "locale": "he"}, key="warehouse_cal")

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
        col1.write(f"**{row['Task_Name']}** ({row['Recurring']})")
        if col2.button("מחק", key=f"del_{row['ID']}"):
            delete_task(row['ID'])
            st.rerun()
