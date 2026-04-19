import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול משימות - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX - כרטיסי ענק בלחיצה ישירה (ללא כפתור "כניסה" למטה)
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
    .stButton > button[key="logout_btn"]:hover { background-color: #dc2626 !important; transform: scale(1.02); }

    /* עיצוב כרטיסי הכניסה - הגודל שביקשת */
    .login-card {
        background: white;
        border-radius: 20px;
        height: 450px; /* גובה משמעותי כמו בציור */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .login-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12);
        border-color: #3b82f6;
    }

    .card-icon { font-size: 80px; margin-bottom: 20px; }
    .card-title { font-size: 36px; font-weight: 900; color: #1e293b; text-align: center; }
    
    /* פס צבע תחתון עבה */
    .card-strip {
        width: 100%;
        height: 20px;
        position: absolute;
        bottom: 0;
        left: 0;
    }

    /* הסתרת הכפתורים המקוריים של Streamlit כדי להפוך את כל הכרטיס ללחיץ */
    .stButton > button.clickable-card {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            data = pd.read_csv(DB_FILE)
            for col in ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"]:
                if col not in data.columns: data[col] = ""
            return data.fillna("")
        except: return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])

def save_data(df_to_save):
    df_to_save.to_csv(DB_FILE, index=False)

# ניהול כניסה
if "user_role" not in st.session_state: st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown("<h1 style='text-align: center; color: #0f172a; font-size: 3.5rem; font-weight: 900; padding-top: 40px;'>ברוכים הבאים למערכת ניהול משימות - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.5rem; margin-bottom: 50px;'>ניהול לוגיסטי מתקדם | בחר תפקיד לכניסה</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    roles = [
        {"id": "l_admin", "title": "WMS<br>מנהל", "icon": "🔑", "color": "#2563eb", "role": "מנהל WMS"},
        {"id": "l_staff", "title": "צוות<br>מחסן", "icon": "📦", "color": "#d97706", "role": "צוות מחסן"},
        {"id": "l_vp", "title": "סמנכ\"ל", "icon": "📊", "color": "#059669", "role": "סמנכ\"ל"}
    ]
    
    for i, role_data in enumerate([col1, col2, col3]):
        with role_data:
            role = roles[i]
            # יצירת המבנה הויזואלי
            st.markdown(f"""
                <div class='login-card'>
                    <div class='card-icon'>{role['icon']}</div>
                    <div class='card-title'>{role['title']}</div>
                    <div class='card-strip' style='background-color: {role['color']};'></div>
                </div>
            """, unsafe_allow_html=True)
            # כפתור שקוף מעל הכל שהופך את כל הכרטיס ללחיץ
            if st.button("", key=role['id'], help=f"כניסה כ-{role['role']}", use_container_width=True, cls="clickable-card"):
                st.session_state.user_role = role['role']
                st.rerun()

    st.stop()

# המשך המערכת לאחר כניסה
if "df" not in st.session_state: st.session_state.df = load_data()

with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    st.divider()
    OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"
    
    if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
    elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
    else: menu = [OPT_DASH, OPT_CAL]
    
    choice = st.radio("ניווט:", menu)
    st.write("<br>"*15, unsafe_allow_html=True)
    if st.button("🚪 התנתקות", key="logout_btn", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()

# לוגיקת דפים (מקוצרת לצורך הצגת הקוד המתוקן)
if choice == OPT_DASH:
    st.title(OPT_DASH)
    # כאן יבוא שאר הקוד של הדשבורד ששלחתי לך קודם...
elif choice == OPT_CAL:
    st.title(OPT_CAL)
    # כאן לוגיקת לוח השנה...
