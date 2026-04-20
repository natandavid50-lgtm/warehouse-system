import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="אחים כהן - ניהול משימות", layout="wide", initial_sidebar_state="expanded")

# 2. הזרקת CSS מקצועי - Navy Blue Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* רקע כללי נקי */
    .stApp { background-color: #f4f7f9; }

    /* עיצוב כפתורי הכניסה - Navy Blue */
    div.stButton > button[key^="login_"] {
        height: 380px !important;
        width: 100% !important;
        background-color: #000080 !important; /* Navy Blue */
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 20px rgba(0,0,128,0.2) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }

    div.stButton > button[key^="login_"]:hover {
        transform: translateY(-8px) !important;
        background-color: #0000a0 !important; /* כחול מעט בהיר יותר במעבר עכבר */
        box-shadow: 0 15px 30px rgba(0,0,128,0.3) !important;
    }

    /* הגדרת הטקסט והסמל בתוך הכפתור */
    .button-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 20px;
    }

    .button-icon {
        font-size: 100px !important; /* סמל ענק וברור */
        line-height: 1 !important;
    }

    .button-text {
        font-size: 36px !important; /* טקסט גדול */
        font-weight: 800 !important;
    }

    /* עיצוב ה-Sidebar */
    section[data-testid="stSidebar"] { background-color: #000080 !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    /* כרטיסי משימות */
    .task-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-right: 6px solid #000080;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ניהול נתונים (CSV)
DB_FILE = "warehouse_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df.fillna("")
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
                       (freq == "שבועי" and diff % 7 == 0) or (freq == "חודשי" and diff % 30 == 0)
                if show:
                    is_done = t_str in str(row['Done_Dates']).split(",")
                    tasks.append({"idx": idx, "name": row['Task_Name'], "desc": row['Description'], "done": is_done})
        except: continue
    return tasks

# אתחול
if "user_role" not in st.session_state: st.session_state.user_role = None
if "df" not in st.session_state: st.session_state.df = load_data()

# --- מסך כניסה ---
if st.session_state.user_role is None:
    st.markdown("<br><h1 style='text-align: center; color: #000080; font-size: 50px;'>אחים כהן - ניהול משימות</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px;'>בחר תפקיד להתחברות</p><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # שימוש ב-Markdown בתוך הכפתור כדי לשלוט בגודל
        if st.button("🔑\n\nמנהל WMS", key="login_admin", use_container_width=True):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
            
    with col2:
        if st.button("📦\n\nצוות מחסן", key="login_staff", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
            
    with col3:
        if st.button("📈\n\nסמנכ\"ל", key="login_vp", use_container_width=True):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
    st.stop()

# --- תפריט ראשי ---
menu_options = {
    "מנהל WMS": ["📊 דשבורד", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ ניהול"],
    "צוות מחסן": ["📋 סידור עבודה", "📅 לוח שנה"],
    "סמנכ\"ל": ["📊 דשבורד", "📅 לוח שנה"]
}

with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.user_role}")
    choice = st.radio("ניווט:", menu_options[st.session_state.user_role])
    if st.button("🚪 התנתקות"):
        st.session_state.user_role = None
        st.rerun()

# --- לוגיקת דפים ---
if "דשבורד" in choice:
    st.title("📊 דשבורד סטטוס")
    t_tasks = get_tasks_for_date(datetime.now().date())
    done = sum(1 for t in t_tasks if t['done'])
    total = len(t_tasks)
    
    c1, c2 = st.columns(2)
    c1.metric("משימות להיום", total)
    c2.metric("בוצעו", done)
    
    st.markdown("---")
    for t in t_tasks:
        c = "#10b981" if t['done'] else "#000080"
        st.markdown(f"<div class='task-card' style='border-right-color: {c}'><b>{t['name']}</b><br>{t['desc']}</div>", unsafe_allow_html=True)

elif "סידור עבודה" in choice:
    st.title("📋 סידור עבודה")
    today = datetime.now().date()
    t_tasks = get_tasks_for_date(today)
    for t in t_tasks:
        if t['done']:
            st.success(f"✅ {t['name']} - בוצע")
        else:
            if st.checkbox(f"סמן כבוצע: {t['name']}", key=f"check_{t['idx']}"):
                d_dates = str(st.session_state.df.at[t['idx'], 'Done_Dates'])
                st.session_state.df.at[t['idx'], 'Done_Dates'] = f"{d_dates},{today.strftime('%Y-%m-%d')}".strip(",")
                save_data(st.session_state.df)
                st.rerun()

elif "הוספת משימה" in choice:
    st.title("➕ הוספת משימה")
    with st.form("add"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "חודשי"])
        if st.form_submit_button("שמור"):
            new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 100
            new_row = {"ID": new_id, "Task_Name": name, "Description": desc, "Recurring": freq, "Date": datetime.now().strftime("%Y-%m-%d"), "Done_Dates": ""}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success("נשמר!")

elif "לוח שנה" in choice:
    st.title("📅 לוח שנה")
    ev = []
    for _, r in st.session_state.df.iterrows():
        ev.append({"title": r['Task_Name'], "start": r['Date'], "color": "#000080"})
    calendar(events=ev)

elif "ניהול" in choice:
    st.title("⚙️ ניהול נתונים")
    st.write(st.session_state.df)
    if st.button("מחק הכל (זהירות)"):
        st.session_state.df = pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])
        save_data(st.session_state.df)
        st.rerun()
