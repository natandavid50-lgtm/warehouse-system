import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="אחים כהן - ניהול מחסן", layout="wide", initial_sidebar_state="expanded")

# 2. הזרקת CSS - עיצוב נייבי פרימיום (Navy & Gold Look)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
    }

    .stApp { background-color: #f8fafc; }

    /* עיצוב כפתורי הכניסה - כחול נייבי עמוק */
    div.stButton > button[key^="btn_"] {
        height: 350px !important;
        width: 100% !important;
        background: linear-gradient(145deg, #0f172a, #1e293b) !important;
        color: #ffffff !important;
        border: 2px solid #334155 !important;
        border-radius: 30px !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        font-size: 36px !important;
        font-weight: 800 !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2) !important;
        white-space: pre-line !important;
    }

    div.stButton > button[key^="btn_"]:hover {
        transform: translateY(-15px) !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3) !important;
        color: #60a5fa !important;
    }

    /* עיצוב כרטיסי משימות בדשבורד */
    .task-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 12px;
        border-right: 8px solid #0f172a;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .day-header {
        background: #0f172a;
        color: white;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        margin-bottom: 15px;
    }

    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    section[data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    /* עיצוב מטריקות */
    [data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. ניהול מסד נתונים
DB_FILE = "warehouse_tasks_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            expected_cols = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"]
            for col in expected_cols:
                if col not in df.columns: df[col] = ""
            return df.fillna("")
        except: return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def get_tasks_for_date(target_date):
    if st.session_state.df.empty: return []
    scheduled = []
    target_str = target_date.strftime("%Y-%m-%d")
    for idx, row in st.session_state.df.iterrows():
        try:
            base_date = pd.to_datetime(row['Date']).date()
            diff = (target_date - base_date).days
            if diff >= 0:
                freq = row['Recurring']
                hit = (freq == "לא" and diff == 0) or \
                      (freq == "יומי") or \
                      (freq == "שבועי" and diff % 7 == 0) or \
                      (freq == "דו-שבועי" and diff % 14 == 0) or \
                      (freq == "חודשי" and diff % 30 == 0)
                if hit:
                    done_list = str(row['Done_Dates']).split(",")
                    is_done = target_str in done_list
                    scheduled.append({"idx": idx, "name": row['Task_Name'], "desc": row['Description'], "is_done": is_done})
        except: continue
    return scheduled

# 4. אתחול Session State
if "user_role" not in st.session_state: st.session_state.user_role = None
if "df" not in st.session_state: st.session_state.df = load_data()

# הגדרת שמות דפים
OPT_DASH = "📊 דשבורד בקרה"
OPT_WORK = "📋 סידור עבודה"
OPT_CAL = "📅 לוח שנה"
OPT_ADD = "➕ הוספת משימה"
OPT_MANAGE = "⚙️ הגדרות"

# --- מסך כניסה ---
if st.session_state.user_role is None:
    st.markdown("<br><br><h1 style='text-align: center; color: #0f172a; font-size: 55px; font-weight: 900;'>אחים כהן - ניהול משימות</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #475569; font-size: 24px; margin-bottom: 50px;'>בחר תפקיד לכניסה למערכת</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔑\n\nמנהל WMS", key="btn_admin"):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
    with col2:
        if st.button("📦\n\nצוות מחסן", key="btn_staff"):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
    with col3:
        if st.button("📈\n\nסמנכ\"ל", key="btn_vp"):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
    st.stop()

# --- תפריט צד ---
if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "סמנכ\"ל":
    menu = [OPT_DASH, OPT_CAL]
else:
    menu = [OPT_WORK, OPT_CAL]

with st.sidebar:
    st.markdown(f"## {st.session_state.user_role}")
    choice = st.radio("ניווט:", menu)
    st.markdown("---")
    if st.button("🚪 התנתקות", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()

# --- לוגיקת דפים ---

if choice == OPT_DASH:
    st.title("📊 דשבורד סטטוס יומי")
    today_tasks = get_tasks_for_date(datetime.now().date())
    total = len(today_tasks)
    done = sum(1 for t in today_tasks if t['is_done'])
    perc = int((done/total)*100) if total > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות להיום", total)
    c2.metric("בוצעו", done)
    c3.metric("עמידה ביעדים", f"{perc}%")
    
    st.markdown("### רשימת משימות נוכחית")
    for t in today_tasks:
        status_color = "#10b981" if t['is_done'] else "#f59e0b"
        status_text = "בוצע ✅" if t['is_done'] else "בממתנה ⏳"
        st.markdown(f"""
            <div class="task-card" style="border-right-color: {status_color}">
                <div style="display: flex; justify-content: space-between;">
                    <b>{t['name']}</b>
                    <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
                </div>
                <div style="font-size: 0.9em; color: #64748b;">{t['desc']}</div>
            </div>
        """, unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.title("📋 סידור עבודה שבועי")
    today = datetime.now().date()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7) # יום ראשון
    
    cols = st.columns(5)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    
    for i, day_name in enumerate(days):
        current_date = start_of_week + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"<div class='day-header'>{day_name}<br>{current_date.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            day_tasks = get_tasks_for_date(current_date)
            for t in day_tasks:
                if t['is_done']:
                    st.success(f"✅ {t['name']}")
                else:
                    if st.checkbox(f"בצע: {t['name']}", key=f"chk_{date_str}_{t['name']}"):
                        current_done = str(st.session_state.df.at[t['idx'], 'Done_Dates'])
                        st.session_state.df.at[t['idx'], 'Done_Dates'] = f"{current_done},{date_str}".strip(",")
                        save_data(st.session_state.df)
                        st.rerun()

elif choice == OPT_CAL:
    st.title("📅 לוח שנה משימות")
    events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            for i in range(30): # הצגה ל-30 מופעים קדימה
                gap = {"לא":0, "יומי":1, "שבועי":7, "דו-שבועי":14, "חודשי":30}.get(row['Recurring'], 0)
                curr = (base + timedelta(days=i * gap)).strftime("%Y-%m-%d")
                is_done = curr in str(row['Done_Dates'])
                events.append({
                    "title": f"{'✅' if is_done else '⏳'} {row['Task_Name']}",
                    "start": curr,
                    "color": "#10b981" if is_done else "#0f172a"
                })
                if row['Recurring'] == "לא": break
        except: continue
    
    calendar(events=events, options={"direction": "rtl", "locale": "he"})

elif choice == OPT_ADD:
    st.title("➕ הוספת משימה חדשה")
    with st.form("new_task"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור המשימה")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        start_d = st.date_input("תאריך התחלה")
        if st.form_submit_button("שמור משימה"):
            new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 100
            new_row = {"ID": new_id, "Task_Name": name, "Description": desc, "Recurring": freq, "Date": start_d.strftime("%Y-%m-%d"), "Done_Dates": ""}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success("המשימה נוספה בהצלחה!")

elif choice == OPT_MANAGE:
    st.title("⚙️ ניהול בסיס נתונים")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        task_to_del = st.selectbox("בחר משימה למחיקה", st.session_state.df['Task_Name'].tolist())
        if st.button("🗑️ מחק משימה שנבחרה"):
            st.session_state.df = st.session_state.df[st.session_state.df['Task_Name'] != task_to_del]
            save_data(st.session_state.df)
            st.rerun()
