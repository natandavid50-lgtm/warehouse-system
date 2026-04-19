import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול משימות - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX - תיקון שגיאת ה-TypeError ועיצוב כרטיסים נקי
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
    /* עיצוב ה-Sidebar */
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] h3 { color: #60a5fa !important; font-weight: 800 !important; }

    /* כפתור התנתקות מעוצב בתחתית */
    .stButton > button[key="logout_btn"] {
        background-color: #b91c1c !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 50px !important;
        border: none !important;
        transition: 0.3s;
    }

    /* עיצוב כרטיסי הכניסה - הגודל שביקשת */
    .login-card {
        background: white;
        border-radius: 20px;
        height: 450px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        pointer-events: none; /* מאפשר ללחיצה לעבור לכפתור שמתחת */
    }
    
    .card-icon { font-size: 80px; margin-bottom: 20px; }
    .card-title { font-size: 36px; font-weight: 900; color: #1e293b; text-align: center; }
    .card-strip { width: 100%; height: 20px; position: absolute; bottom: 0; left: 0; }

    /* הפיכת כפתור ה-Streamlit לשקוף ופרוס על כל הכרטיס */
    div.stButton > button {
        height: 450px !important;
        width: 100% !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        position: absolute !important;
        top: -450px !important; /* מעלה את הכפתור השקוף על גבי ה-HTML */
        z-index: 100 !important;
    }
    
    /* ביטול העיצוב לכפתור ההתנתקות כדי שלא יהיה שקוף */
    div.stButton > button[key="logout_btn"] {
        height: 50px !important;
        top: 0 !important;
        color: white !important;
        background-color: #b91c1c !important;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            data = pd.read_csv(DB_FILE)
            return data.fillna("")
        except: return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])

def save_data(df_to_save):
    df_to_save.to_csv(DB_FILE, index=False)

if "user_role" not in st.session_state: st.session_state.user_role = None

# מסך כניסה
if st.session_state.user_role is None:
    st.markdown("<h1 style='text-align: center; color: #0f172a; font-size: 3.5rem; font-weight: 900; padding-top: 40px;'>ברוכים הבאים למערכת ניהול משימות - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.5rem; margin-bottom: 50px;'>ניהול לוגיסטי מתקדם | בחר תפקיד לכניסה</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    roles = [
        {"id": "admin", "title": "WMS<br>מנהל", "icon": "🔑", "color": "#2563eb", "role": "מנהל WMS"},
        {"id": "staff", "title": "צוות<br>מחסן", "icon": "📦", "color": "#d97706", "role": "צוות מחסן"},
        {"id": "vp", "title": "סמנכ\"ל", "icon": "📊", "color": "#059669", "role": "סמנכ\"ל"}
    ]
    
    for i, col in enumerate([col1, col2, col3]):
        with col:
            r = roles[i]
            st.markdown(f"""
                <div class='login-card'>
                    <div class='card-icon'>{r['icon']}</div>
                    <div class='card-title'>{r['title']}</div>
                    <div class='card-strip' style='background-color: {r['color']};'></div>
                </div>
            """, unsafe_allow_html=True)
            # הכפתור השקוף (ללא הפרמטר cls שגרם לשגיאה)
            if st.button("", key=f"btn_{r['id']}", use_container_width=True):
                st.session_state.user_role = r['role']
                st.rerun()
    st.stop()

# שאר המערכת
if "df" not in st.session_state: st.session_state.df = load_data()

with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    st.divider()
    menu = ["📊 דשבורד בקרה", "📅 לוח שנה"] # דוגמה לתפריט
    choice = st.radio("ניווט:", menu)
    st.write("<br>"*15, unsafe_allow_html=True)
    if st.button("🚪 התנתקות", key="logout_btn", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()
