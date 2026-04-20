import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
from supabase import create_client, Client
import os

# --- 1. הגדרות התחברות ל-SUPABASE ---
SUPABASE_URL = "https://jvyzdftdvzufulwgldck.supabase.co"
# תדביק כאן את המפתח שהעתקת מהלשונית Publishable key
SUPABASE_KEY = "תדביק_כאן_את_המפתח" 

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

db = get_supabase()

# --- 2. הגדרות עמוד ועיצוב (RTL מלא) ---
st.set_page_config(page_title="אחים כהן - ניהול מחסן", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* כיוון ימין לשמאל */
    .stApp { 
        background-color: #f8fafc;
        direction: rtl;
        text-align: right;
    }
    
    /* עיצוב סיידבר */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        min-width: 280px !important;
        direction: rtl;
    }
    section[data-testid="stSidebar"] * { color: white !important; text-align: right; }
    
    /* כרטיסי כניסה */
    .login-card {
        background: white;
        border-radius: 20px;
        height: 320px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        transition: transform 0.3s ease;
    }
    .login-card:hover { transform: translateY(-5px); }
    
    /* כרטיסי משימות */
    .task-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 12px;
        border-right: 10px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. פונקציות עבודה מול הענן ---
def load_data():
    try:
        res = db.table("tasks").select("*").execute()
        df = pd.DataFrame(res.data)
        if df.empty:
            return pd.DataFrame(columns=["id", "task_name", "description", "recurring", "task_date", "done_dates"])
        # המרה לשמות עמודות שהקוד מכיר
        df.columns = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"]
        return df
    except:
        return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])

def save_new_task(name, desc, freq, date):
    new_id = int(datetime.now().timestamp())
    db.table("tasks").insert({
        "id": new_id,
        "task_name": name,
        "description": desc,
        "recurring": freq,
        "task_date": str(date),
        "done_dates": ""
    }).execute()

def update_done_dates(t_id, done_str):
    db.table("tasks").update({"done_dates": done_str}).eq("id", t_id).execute()

def delete_task(t_id):
    db.table("tasks").delete().eq("id", t_id).execute()

# פונקציית עזר לחישוב משימות להיום
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
                    scheduled.append({"id": row['ID'], "name": row['Task_Name'], "desc": row['Description'], "is_done": is_done, "done_str": done_dates})
        except: continue
    return scheduled

# --- 4. ניהול מצב (Session) ---
if "user_role" not in st.session_state: st.session_state.user_role = None
if "current_page" not in st.session_state: st.session_state.current_page = None

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# --- 5. מסך כניסה ---
if st.session_state.user_role is None:
    st.markdown("<h1 style='text-align: center; color: #0f172a; margin-top: 50px;'>אחים כהן - ניהול משימות מחסן</h1>", unsafe_allow_html=True)
    cols = st.columns(3, gap="large")
    roles = [
        {"role": "מנהל WMS", "icon": "🔑", "color": "#2563eb", "id": "admin"},
        {"role": "צוות מחסן", "icon": "📦", "color": "#f59e0b", "id": "staff"},
        {"role": "סמנכ\"ל", "icon": "📊", "color": "#10b981", "id": "vp"}
    ]
    for i, col in enumerate(cols):
        with col:
            r = roles[i]
            st.markdown(f"<div class='login-card'><h1>{r['icon']}</h1><h2>{r['role']}</h2></div>", unsafe_allow_html=True)
            if st.button(f"כניסה כ-{r['role']}", key=f"login_{r['id']}", use_container_width=True):
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
    choice = st.radio("ניווט:", menu, index=menu.index(st.session_state.current_page) if st.session_state.current_page in menu else 0)
    st.session_state.current_page = choice
    if st.button("🚪 התנתקות", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()

# --- 7. דפי המערכת ---

if choice == OPT_DASH:
    st.title(OPT_DASH)
    tasks = get_daily_status(df, datetime.now())
    t_count = len(tasks)
    d_count = sum(1 for t in tasks if t['is_done'])
    
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
        with cols[4-i]: # תצוגה מימין לשמאל
            st.markdown(f"<div style='background:#1e293b; color:white; padding:10px; border-radius:10px; text-align:center;'>{day_name} {curr_day.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            day_tasks = get_daily_status(df, curr_day)
            for t in day_tasks:
                if t['is_done']:
                    st.success(f"✅ {t['name']}")
                else:
                    if st.checkbox(f"בצע: {t['name']}", key=f"chk_{t['id']}_{curr_str}"):
                        new_done = f"{t['done_str']},{curr_str}".strip(",")
                        update_done_dates(t['id'], new_done)
                        st.rerun()

elif choice == OPT_CAL:
    st.title(OPT_CAL)
    events = []
    for _, row in df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            freq = row['Recurring']
            for i in range(30): # מציג חודש קדימה
                gap = 0 if freq=="לא" else 1 if freq=="יומי" else 7 if freq=="שבועי" else 14 if freq=="דו-שבועי" else 30
                d = (base + timedelta(days=i * gap)).strftime("%Y-%m-%d")
                is_done = d in str(row['Done_Dates'])
                events.append({"title": f"{'✅' if is_done else '⏳'} {row['Task_Name']}", "start": d, "color": "#10b981" if is_done else "#ef4444"})
                if freq == "לא": break
        except: continue
    calendar(events=events, options={"direction": "rtl", "locale": "he"}, key="warehouse_cal")

elif choice == OPT_ADD:
    st.title(OPT_ADD)
    with st.form("add_new"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        date = st.date_input("תאריך התחלה", datetime.now())
        if st.form_submit_button("שמור בענן ☁️"):
            if name:
                save_new_task(name, desc, freq, date)
                st.success("נשמר ב-Supabase!")
                st.rerun()
            else: st.error("צריך שם למשימה!")

elif choice == OPT_MANAGE:
    st.title(OPT_MANAGE)
    st.write("משימות קיימות (מחיקה ועדכון):")
    for _, row in df.iterrows():
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{row['Task_Name']}** ({row['Recurring']})")
        if col2.button("מחק", key=f"del_{row['ID']}"):
            delete_task(row['ID'])
            st.rerun()
