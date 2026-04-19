import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת מחסן - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX ממוקד קריאות ונוכחות
st.markdown("""
    <style>
    /* רקע כללי */
    .stApp {
        background: #f1f5f9;
    }
    
    /* תיקון Sidebar - קריאות מקסימלית */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    /* צבע הטקסט של הרדיו באטנס והלייבלים */
    section[data-testid="stSidebar"] .st-bd, 
    section[data-testid="stSidebar"] .st-bc,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: white !important;
        font-size: 1.15rem !important;
        font-weight: 500 !important;
    }
    /* צבע הכותרת ב-Sidebar */
    section[data-testid="stSidebar"] h3 {
        color: #3b82f6 !important;
        font-weight: 800 !important;
    }

    /* מסך כניסה - כפתורים ענקיים למילוי המסך */
    .login-container {
        padding-top: 50px;
    }
    .stButton>button {
        height: 450px !important; /* גובה ענקי למילוי המסך */
        width: 100% !important;
        border-radius: 35px !important;
        background: white !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        border: 1px solid #e2e8f0 !important;
    }
    .stButton>button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 30px 60px rgba(0,0,0,0.15) !important;
        background: #f8fafc !important;
    }
    /* טקסט בתוך כפתורי הכניסה */
    .stButton>button p {
        font-size: 38px !important;
        font-weight: 900 !important;
    }

    /* פס צבע תחתון לכל כפתור כניסה */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-bottom: 20px solid #1e40af !important; color: #1e40af !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-bottom: 20px solid #d97706 !important; color: #d97706 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-bottom: 20px solid #059669 !important; color: #059669 !important; }

    /* עיצוב כרטיסי משימות */
    .task-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-right: 10px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

# --- לוגיקה ופונקציות (ללא שינוי) ---
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

# 4. מסך כניסה משודרג
if "user_role" not in st.session_state: st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #0f172a; font-size: 4rem; font-weight: 900;'>מערכת המחסן - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #475569; font-size: 1.8rem; margin-bottom: 50px;'>ניהול לוגיסטי מתקדם | בחר תפקיד לכניסה</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        if st.button("🔑\nמנהל WMS", key="admin_btn"):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
    with col2:
        if st.button("📦\nצוות מחסן", key="staff_btn"):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
    with col3:
        if st.button("📊\nסמנכ\"ל", key="vp_btn"):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 5. טעינת נתונים ותפריט
if "df" not in st.session_state: st.session_state.df = load_data()

with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    st.divider()
    OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH = "📅 לוח שנה", "📋 סידור עבודה", "➕ הוספת משימה", "⚙️ הגדרות", "📊 דשבורד בקרה"
    
    if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
    elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
    else: menu = [OPT_DASH, OPT_CAL]
    
    choice = st.radio("ניווט במערכת:", menu)
    
    st.write("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 התנתקות", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()

# 6. הצגת דפים (נשאר ללא שינוי לוגי, רק שיפור קל בלוח שנה)
if choice == OPT_DASH:
    st.title("📊 דשבורד בקרה")
    tasks = get_daily_status(datetime.now())
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות היום", len(tasks))
    c2.metric("בוצעו", sum(1 for t in tasks if t['is_done']))
    st.divider()
    for t in tasks:
        color = "#10b981" if t['is_done'] else "#f59e0b"
        st.markdown(f"<div class='task-card' style='border-right-color: {color}'><strong>{t['name']}</strong><br>{t['desc']}</div>", unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.title("📋 סידור עבודה שבועי")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(len(days))
    for i, day in enumerate(days):
        curr = start + timedelta(days=i)
        with cols[i]:
            st.markdown(f"<div style='background:#0f172a; color:white; padding:10px; border-radius:10px; text-align:center;'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            for t in get_daily_status(curr):
                if t['is_done']: st.success(t['name'])
                else:
                    st.warning(t['name'])
                    if st.button("בצע", key=f"b_{t['id']}_{i}"):
                        idx = t['idx']
                        st.session_state.df.at[idx, "Done_Dates"] = f"{str(st.session_state.df.at[idx, 'Done_Dates'])},{curr.strftime('%Y-%m-%d')}".strip(",")
                        save_data(st.session_state.df); st.rerun()

elif choice == OPT_CAL:
    st.title("📅 לוח שנה")
    cal_events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            f = row['Recurring']
            for i in range(120 if f != "לא" else 1):
                gap = 1 if f=="יומי" else 7 if f=="שבועי" else 14 if f=="דו-שבועי" else 30 if f=="חודשי" else 0
                d = (base + timedelta(days=i*gap)).strftime("%Y-%m-%d")
                cal_events.append({"title": row['Task_Name'], "start": d, "color": "#10b981" if d in str(row['Done_Dates']) else "#ef4444"})
        except: continue
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 550})

elif choice == OPT_ADD:
    st.title("➕ הוספת משימה")
    with st.form("add_task_form"):
        n = st.text_input("שם המשימה")
        f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        d = st.date_input("תאריך התחלה")
        ds = st.text_area("תיאור")
        if st.form_submit_button("שמור במערכת"):
            new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df); st.success("המשימה נוספה!"); st.rerun()

elif choice == OPT_MANAGE:
    st.title("⚙️ הגדרות")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        t_del = st.selectbox("מחיקת משימה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != t_del]
            save_data(st.session_state.df); st.rerun()
