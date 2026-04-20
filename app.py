import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד ותצוגה
st.set_page_config(page_title="אחים כהן - ניהול משימות", layout="wide", initial_sidebar_state="expanded")

# 2. הזרקת CSS - כחול בהיר, טקסט גדול וכרטיסי ענק
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
    }

    .stApp { background-color: #f8fafc; }

    /* עיצוב כפתורי הכניסה הגדולים - כחול בהיר */
    div.stButton > button[key^="login_"] {
        height: 450px !important;
        width: 100% !important;
        background-color: #38bdf8 !important; /* כחול בהיר */
        color: #ffffff !important;
        border: none !important;
        border-radius: 30px !important;
        box-shadow: 0 15px 30px rgba(56, 189, 248, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 45px !important; /* טקסט ענק */
        font-weight: 800 !important;
        white-space: pre-line !important;
        line-height: 1.2 !important;
    }

    div.stButton > button[key^="login_"]:hover {
        transform: translateY(-15px) !important;
        background-color: #0ea5e9 !important;
        box-shadow: 0 25px 50px rgba(56, 189, 248, 0.6) !important;
    }

    /* עיצוב ה-Sidebar */
    section[data-testid="stSidebar"] { background-color: #0c4a6e !important; }
    section[data-testid="stSidebar"] * { color: white !important; }

    /* כרטיסי משימות בדשבורד */
    .task-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 15px;
        border-right: 10px solid #38bdf8;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .day-header {
        background: #38bdf8;
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ניהול נתונים (CSV)
DB_FILE = "warehouse_tasks_final.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            for col in ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"]:
                if col not in df.columns: df[col] = ""
            return df.fillna("")
        except: return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def get_tasks_for_date(target_date):
    if st.session_state.df.empty: return []
    tasks = []
    t_str = target_date.strftime("%Y-%m-%d")
    for idx, row in st.session_state.df.iterrows():
        try:
            start_date = pd.to_datetime(row['Date']).date()
            diff = (target_date - start_date).days
            if diff >= 0:
                freq = row['Recurring']
                show = (freq == "לא" and diff == 0) or (freq == "יומי") or \
                       (freq == "שבועי" and diff % 7 == 0) or \
                       (freq == "דו-שבועי" and diff % 14 == 0) or \
                       (freq == "חודשי" and diff % 30 == 0)
                if show:
                    done_dates = str(row['Done_Dates']).split(",")
                    tasks.append({"idx": idx, "id": row['ID'], "name": row['Task_Name'], "desc": row['Description'], "done": t_str in done_dates})
        except: continue
    return tasks

# אתחול ה-Session
if "user_role" not in st.session_state: st.session_state.user_role = None
if "df" not in st.session_state: st.session_state.df = load_data()

# --- מסך כניסה ---
if st.session_state.user_role is None:
    st.markdown("<br><h1 style='text-align: center; color: #0c4a6e; font-size: 60px; font-weight: 900;'>אחים כהן - ניהול משימות</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 26px; color: #475569;'>בחר תפקיד כדי להתחבר למערכת</p><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔑\n\nמנהל WMS", key="login_admin", use_container_width=True):
            st.session_state.user_role = "מנהל WMS"; st.rerun()
    with c2:
        if st.button("📦\n\nצוות מחסן", key="login_staff", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"; st.rerun()
    with c3:
        if st.button("📈\n\nסמנכ\"ל", key="login_vp", use_container_width=True):
            st.session_state.user_role = "סמנכ\"ל"; st.rerun()
    st.stop()

# --- הגדרת תפריט לפי תפקיד ---
menu_map = {
    "מנהל WMS": ["📊 דשבורד", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ בסיס נתונים"],
    "צוות מחסן": ["📋 סידור עבודה", "📅 לוח שנה"],
    "סמנכ\"ל": ["📊 דשבורד", "📅 לוח שנה"]
}

with st.sidebar:
    st.markdown(f"## מחובר: {st.session_state.user_role}")
    choice = st.radio("ניווט:", menu_map[st.session_state.user_role])
    if st.button("🚪 התנתק"):
        st.session_state.user_role = None; st.rerun()

# --- דפי המערכת ---

if choice == "📊 דשבורד":
    st.title("📊 סטטוס משימות יומי")
    today = datetime.now().date()
    tasks = get_tasks_for_date(today)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    total = len(tasks)
    done = sum(1 for t in tasks if t['done'])
    col_m1.metric("סה\"כ משימות היום", total)
    col_m2.metric("בוצעו", done)
    col_m3.metric("נותרו", total - done)
    
    st.markdown("---")
    for t in tasks:
        status_c = "#10b981" if t['done'] else "#38bdf8"
        st.markdown(f"""<div class='task-card' style='border-right-color: {status_c}'>
            <h3 style='margin:0;'>{t['name']} {'✅' if t['done'] else '⏳'}</h3>
            <p style='color:#64748b; margin:5px 0;'>{t['desc']}</p>
        </div>""", unsafe_allow_html=True)

elif choice == "📋 סידור עבודה":
    st.title("📋 סידור עבודה שבועי")
    today = datetime.now().date()
    start_week = today - timedelta(days=(today.weekday() + 1) % 7)
    
    cols = st.columns(5)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    
    for i, name in enumerate(days_names):
        curr = start_week + timedelta(days=i)
        curr_str = curr.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"<div class='day-header'>{name}<br>{curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            day_tasks = get_tasks_for_date(curr)
            for t in day_tasks:
                if t['done']:
                    st.write(f"✅ **{t['name']}**")
                else:
                    if st.checkbox(f"{t['name']}", key=f"wk_{t['idx']}_{curr_str}"):
                        current_dates = str(st.session_state.df.at[t['idx'], 'Done_Dates'])
                        st.session_state.df.at[t['idx'], 'Done_Dates'] = f"{current_dates},{curr_str}".strip(",")
                        save_data(st.session_state.df); st.rerun()

elif choice == "📅 לוח שנה":
    st.title("📅 לוח משימות")
    events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            for i in range(15): # הצגה ל-15 מופעים קדימה
                step = {"לא":0, "יומי":1, "שבועי":7, "דו-שבועי":14, "חודשי":30}.get(row['Recurring'], 0)
                d = (base + timedelta(days=i * step)).strftime("%Y-%m-%d")
                is_d = d in str(row['Done_Dates'])
                events.append({"title": f"{'✅' if is_d else '⏳'} {row['Task_Name']}", "start": d, "color": "#10b981" if is_d else "#38bdf8"})
                if row['Recurring'] == "לא": break
        except: continue
    calendar(events=events, options={"direction": "rtl", "locale": "he"})

elif choice == "➕ הוספת משימה":
    st.title("➕ הוספת משימה חדשה")
    with st.form("add_task"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        start_d = st.date_input("תאריך התחלה", datetime.now())
        if st.form_submit_button("שמור משימה"):
            new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 100
            new_row = {"ID": new_id, "Task_Name": name, "Description": desc, "Recurring": freq, "Date": start_d.strftime("%Y-%m-%d"), "Done_Dates": ""}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success("המשימה נשמרה בהצלחה!")

elif choice == "⚙️ בסיס נתונים":
    st.title("⚙️ ניהול בסיס נתונים")
    edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 שמור שינויים"):
        st.session_state.df = edited_df
        save_data(edited_df)
        st.success("בסיס הנתונים עודכן!")
