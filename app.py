import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת מחסן - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX משופר - דגש על קריאות ופרופורציות
st.markdown("""
    <style>
    /* רקע כללי */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* עיצוב Sidebar - תיקון קריאות */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important; /* כחול כהה מאוד */
    }
    section[data-testid="stSidebar"] .stRadio > label {
        color: #f8fafc !important; /* כותרת הניווט בלבן */
        font-weight: bold;
    }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #f8fafc !important;
        font-size: 1.1rem;
    }
    /* צבע הטקסט של האופציות בניווט */
    div[data-testid="stSidebarUserContent"] .st-c3 {
        color: #cbd5e1 !important;
    }
    
    /* הגדלת כפתורי הכניסה */
    .stButton>button {
        height: 280px !important;
        border-radius: 25px !important;
        background: white !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
        transition: all 0.4s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.12) !important;
        border: 2px solid #3b82f6 !important;
    }

    /* תיקון צבעים לפי תפקיד במסך הכניסה */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 12px solid #1e40af !important; color: #1e40af !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 12px solid #d97706 !important; color: #d97706 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 12px solid #059669 !important; color: #059669 !important; }

    /* עיצוב כרטיסי משימות בדשבורד */
    .task-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        border-right: 6px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

# --- פונקציות לוגיקה ---
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
    scheduled, target_str = [], target_date.strftime("%Y-%m-%d")
    for idx, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date']).to_pydatetime()
            diff = (target_date - base).days
            if diff >= 0:
                f = row.get('Recurring', 'לא')
                hit = (f=="לא" and diff==0) or (f=="יומי") or (f=="שבועי" and diff%7==0) or (f=="דו-שבועי" and diff%14==0) or (f=="חודשי" and diff%30==0)
                if hit:
                    scheduled.append({"idx": idx, "id": row['ID'], "name": row['Task_Name'], "desc": row['Description'], "is_done": target_str in str(row['Done_Dates']).split(",")})
        except: continue
    return scheduled

# 4. ניהול כניסה
if "user_role" not in st.session_state: st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown("<h1 style='text-align: center; color: #1e293b; margin-top: 50px;'>ברוכים הבאים למערכת המחסן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem;'>אחים כהן - בחר תפקיד לכניסה</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1: 
        if st.button("👑\nמנהל WMS", key="l1"): st.session_state.user_role = "מנהל WMS"; st.rerun()
    with c2: 
        if st.button("📦\nצוות מחסן", key="l2"): st.session_state.user_role = "צוות מחסן"; st.rerun()
    with c3: 
        if st.button("📈\nסמנכ\"ל", key="l3"): st.session_state.user_role = "סמנכ\"ל"; st.rerun()
    st.stop()

# 5. תפריט וניווט
if "df" not in st.session_state: st.session_state.df = load_data()

with st.sidebar:
    st.markdown(f"<h3 style='color: white;'>שלום, {st.session_state.user_role}</h3>", unsafe_allow_html=True)
    st.divider()
    OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH = "📅 לוח שנה", "📋 סידור עבודה", "➕ הוספת משימה", "⚙️ הגדרות", "📊 דשבורד בקרה"
    if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
    elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
    else: menu = [OPT_DASH, OPT_CAL]
    choice = st.radio("ניווט:", menu)
    if st.button("🚪 התנתקות", use_container_width=True): st.session_state.user_role = None; st.rerun()

# 6. דפים
if choice == OPT_DASH:
    st.title("📊 דשבורד בקרה")
    t_tasks = get_daily_status(datetime.now())
    total, done = len(t_tasks), sum(1 for t in t_tasks if t['is_done'])
    m1, m2, m3 = st.columns(3)
    m1.metric("משימות היום", total)
    m2.metric("בוצעו", done)
    m3.metric("עמידה ביעדים", f"{int(done/total*100) if total>0 else 0}%")
    st.divider()
    for t in t_tasks:
        st.markdown(f"<div class='task-card' style='border-right-color: {'#10b981' if t['is_done'] else '#f59e0b'}'><b>{t['name']}</b><br>{t['desc']}</div>", unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.title("📋 סידור עבודה שבועי")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(len(days))
    for i, day in enumerate(days):
        curr = start + timedelta(days=i)
        with cols[i]:
            st.markdown(f"<div style='background:#1e293b; color:white; padding:8px; border-radius:10px; text-align:center;'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            for t in get_daily_status(curr):
                if t['is_done']: st.success(t['name'])
                else:
                    st.warning(t['name'])
                    if st.button("בצע", key=f"b_{t['id']}_{i}"):
                        idx = t['idx']
                        st.session_state.df.at[idx, "Done_Dates"] = f"{str(st.session_state.df.at[idx, 'Done_Dates'])},{curr.strftime('%Y-%m-%d')}".strip(",")
                        save_data(st.session_state.df); st.rerun()

elif choice == OPT_CAL:
    st.title("📅 לוח שנה משימות")
    cal_events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            f = row['Recurring']
            for i in range(100 if f != "לא" else 1):
                gap = 1 if f=="יומי" else 7 if f=="שבועי" else 14 if f=="דו-שבועי" else 30 if f=="חודשי" else 0
                d = (base + timedelta(days=i*gap)).strftime("%Y-%m-%d")
                cal_events.append({"title": row['Task_Name'], "start": d, "color": "#10b981" if d in str(row['Done_Dates']) else "#ef4444"})
        except: continue
    # הגבלת גובה ללוח השנה
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 500})

elif choice == OPT_ADD:
    st.title("➕ הוספת משימה")
    with st.form("f"):
        c1, c2 = st.columns(2)
        n = c1.text_input("שם המשימה")
        f = c1.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        d = c2.date_input("תאריך")
        ds = c2.text_area("תיאור")
        if st.form_submit_button("שמור"):
            new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])], ignore_index=True)
            save_data(st.session_state.df); st.success("נשמר!"); st.rerun()

elif choice == OPT_MANAGE:
    st.title("⚙️ הגדרות")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        t_del = st.selectbox("מחיקה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != t_del]
            save_data(st.session_state.df); st.rerun()
