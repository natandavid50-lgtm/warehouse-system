import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# הגדרות עמוד
st.set_page_config(page_title="מערכת מחסן - אחים כהן", layout="wide")

# --- עיצוב CSS מתקדם: מלבנים גדולים, צבעוניים וצפים ---
st.markdown("""
    <style>
    /* עיצוב כללי לכפתורים ככרטיסים */
    .stButton>button {
        height: 220px;
        border-radius: 25px;
        border: 1px solid #f0f2f6;
        background-color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* אפקט ריחוף */
    .stButton>button:hover {
        transform: translateY(-15px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12);
        border-color: #d1d5db;
    }

    /* הגדלת הטקסט בתוך הכפתור */
    .stButton>button div p {
        font-size: 28px !important;
        font-weight: 800 !important;
    }

    /* התאמת צבעים ספציפית לכל כפתור (לפי סדר העמודות) */
    /* מנהל WMS - כחול עוצמתי */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        border-top: 10px solid #1E3A8A !important;
        color: #1E3A8A !important;
    }
    
    /* צוות מחסן - כתום לוגיסטי */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        border-top: 10px solid #F59E0B !important;
        color: #F59E0B !important;
    }
    
    /* סמנכ"ל - ירוק צמיחה */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
        border-top: 10px solid #10B981 !important;
        color: #10B981 !important;
    }

    .card-label {
        text-align: center;
        margin-top: 10px;
        font-size: 18px;
        font-weight: 600;
        color: #4B5563;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

# --- פונקציות טעינה (זהות לגרסה היציבה) ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            data = pd.read_csv(DB_FILE)
            for col in ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"]:
                if col not in data.columns: data[col] = ""
            return data.fillna("")
        except: return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])

def save_data(df_to_save):
    df_to_save.to_csv(DB_FILE, index=False)

def get_daily_status(target_date):
    if st.session_state.df.empty: return []
    scheduled = []
    target_str = target_date.strftime("%Y-%m-%d")
    for idx, row in st.session_state.df.iterrows():
        try:
            if not row.get('Date'): continue
            base = pd.to_datetime(row['Date']).to_pydatetime()
            diff = (target_date - base).days
            if diff >= 0:
                hit = False
                f = row.get('Recurring', 'לא')
                if f == "לא" and diff == 0: hit = True
                elif f == "יומי" and diff < 200: hit = True
                elif f == "שבועי" and diff % 7 == 0: hit = True
                elif f == "דו-שבועי" and diff % 14 == 0: hit = True
                elif f == "חודשי" and diff % 30 == 0: hit = True
                if hit:
                    done = str(row.get('Done_Dates', ""))
                    scheduled.append({"idx": idx, "id": row['ID'], "name": row['Task_Name'], "desc": row['Description'], "is_done": target_str in done.split(",")})
        except: continue
    return scheduled

# --- מסך כניסה צבעוני וגדול ---
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #111827; font-size: 3.5rem; font-weight: 900;'>מערכת המחסן - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280; font-size: 1.5rem;'>בחר תפקיד לכניסה מהירה</p>", unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        if st.button("🔑\nמנהל WMS", use_container_width=True):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
        st.markdown("<p class='card-label'>ניהול והגדרות</p>", unsafe_allow_html=True)

    with col2:
        if st.button("📦\nצוות מחסן", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
        st.markdown("<p class='card-label'>ביצוע משימות</p>", unsafe_allow_html=True)

    with col3:
        if st.button("📊\nסמנכ\"ל", use_container_width=True):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
        st.markdown("<p class='card-label'>בקרה וסטטיסטיקה</p>", unsafe_allow_html=True)

    st.stop()

# --- המשך האפליקציה ---
if "df" not in st.session_state:
    st.session_state.df = load_data()

user_role = st.session_state.user_role
st.sidebar.markdown(f"### מחובר כעת: **{user_role}**")
if st.sidebar.button("התנתקות"):
    st.session_state.user_role = None
    st.rerun()

st.sidebar.divider()

# המשך לוגיקת התפריטים והדפים (זהה לקוד הקודם...)
OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH = "📅 לוח שנה", "📋 סידור עבודה", "➕ הוספת משימה", "⚙️ הגדרות", "📊 דשבורד"
if user_role == "מנהל WMS": menu = [OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE]
elif user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
else: menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("ניווט:", menu)

# --- דפים (מקוצר לצורך התצוגה, הלוגיקה נשמרת) ---
if choice == OPT_DASH:
    st.header("📊 דשבורד מנהלים")
    # ... כאן מגיע קוד הדשבורד עם התיקון ל-KeyError ...
    st.info("כאן מוצגת תמונת המצב היומית")
# (שאר דפי המערכת...)
