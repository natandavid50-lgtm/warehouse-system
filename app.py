import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת משימות - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX מלא - הכל כולל כפתור התנתקות פרימיום
st.markdown("""
    <style>
    /* רקע כללי */
    .stApp { background: #f8fafc; }
    
    /* תפריט צד (Sidebar) */
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    section[data-testid="stSidebar"] .st-bd, section[data-testid="stSidebar"] .st-bc,
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] h3 { color: #60a5fa !important; font-weight: 800 !important; }

    /* עיצוב כפתור התנתקות מושלם */
    .stButton > button[key="logout_btn"] {
        background-color: #ef4444 !important;
        color: white !important;
        border-radius: 15px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border: none !important;
        height: 50px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
    }
    .stButton > button[key="logout_btn"]:hover {
        background-color: #dc2626 !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
    }

    /* מסך כניסה - ריבועים ענקיים */
    .login-container { padding: 50px 20px; text-align: center; }
    
    /* עיצוב כפתורי כניסה */
    .stButton > button:not([key="logout_btn"]) {
        height: 400px !important;
        border-radius: 35px !important;
        background: white !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.08) !important;
        border: 1px solid #e2e8f0 !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stButton > button:not([key="logout_btn"]):hover {
        transform: translateY(-20px) !important;
        box-shadow: 0 25px 60px rgba(0,0,0,0.15) !important;
        border-color: #3b82f6 !important;
    }
    .stButton > button:not([key="logout_btn"]) p {
        font-size: 40px !important;
        font-weight: 900 !important;
    }

    /* פסי צבע תחתונים לכפתורי כניסה */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-bottom: 20px solid #2563eb !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-bottom: 20px solid #d97706 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-bottom: 20px solid #059669 !important; }

    /* כרטיסי משימות בדשבורד */
    .task-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 12px;
        border-right: 10px solid #3b82f6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .detail-box {
        background: #eff6ff;
        border: 2px solid #3b82f6;
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

# --- פונקציות ניהול נתונים ---
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
                    scheduled.append({"idx": idx, "id": row['ID'], "name": row['Task_Name'], "desc": row['Description'], "recurring": f, "is_done": target_str in str(row['Done_Dates']).split(",")})
        except: continue
    return scheduled

# 4. ניהול כניסה ותפקידים
if "user_role" not in st.session_state: st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #0f172a; font-size: 3.8rem; font-weight: 900; margin-bottom: 5px;'>ברוכים הבאים למערכת ניהול משימות - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 1.8rem; margin-bottom: 50px;'>ניהול לוגיסטי חכם | בחר תפקיד לכניסה</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        if st.button("🔑\nמנהל WMS", key="admin_role"): st.session_state.user_role = "מנהל WMS"; st.rerun()
    with col2:
        if st.button("📦\nצוות מחסן", key="staff_role"): st.session_state.user_role = "צוות מחסן"; st.rerun()
    with col3:
        if st.button("📊\nסמנכ\"ל", key="vp_role"): st.session_state.user_role = "סמנכ\"ל"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 5. ניווט ותפריט
if "df" not in st.session_state: st.session_state.df = load_data()

with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    st.divider()
    OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"
    if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
    elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
    else: menu = [OPT_DASH, OPT_CAL]
    choice = st.radio("תפריט ניווט:", menu)
    
    st.write("<br>"*15, unsafe_allow_html=True)
    if st.button("🚪 התנתקות", key="logout_btn", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()

# 6. הצגת דפים
if choice == OPT_DASH:
    st.title("📊 דשבורד בקרה")
    tasks = get_daily_status(datetime.now())
    total, done = len(tasks), sum(1 for t in tasks if t['is_done'])
    c1, c2, c3 = st.columns(3)
    c1.metric("📋 משימות להיום", total)
    c2.metric("✅ בוצעו", done)
    c3.metric("🎯 הספק", f"{int(done/total*100) if total>0 else 0}%")
    st.divider()
    for t in tasks:
        icon, color = ("✅", "#10b981") if t['is_done'] else ("⏳", "#f59e0b")
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><div><strong style="font-size:1.2rem;">{t["name"]}</strong><br>{t["desc"]}</div><div style="font-size:26px;">{icon}</div></div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.title("📋 סידור עבודה שבועי")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(len(days))
    for i, day in enumerate(days):
        curr = start + timedelta(days=i)
        with cols[i]:
            st.markdown(f"<div style='background:#1e293b; color:white; padding:10px; border-radius:10px; text-align:center; margin-bottom:15px;'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            for t in get_daily_status(curr):
                status = "✅" if t['is_done'] else "⏳"
                st.markdown(f"**{status} {t['name']}**")
                if not t['is_done'] and st.button("בצע", key=f"d_{t['id']}_{i}"):
                    idx = t['idx']
                    st.session_state.df.at[idx, "Done_Dates"] = f"{str(st.session_state.df.at[idx, 'Done_Dates'])},{curr.strftime('%Y-%m-%d')}".strip(",")
                    save_data(st.session_state.df); st.rerun()

elif choice == OPT_CAL:
    st.title("📅 לוח שנה משימות")
    cal_events, task_lookup = [], {}
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            f = row['Recurring']
            for i in range(100 if f != "לא" else 1):
                gap = 1 if f=="יומי" else 7 if f=="שבועי" else 14 if f=="דו-שבועי" else 30 if f=="חודשי" else 0
                d = (base + timedelta(days=i*gap)).strftime("%Y-%m-%d")
                done = d in str(row['Done_Dates'])
                eid = f"{row['ID']}_{d}"
                cal_events.append({"id": eid, "title": f"{'✅' if done else '⏳'} {row['Task_Name']}", "start": d, "color": "#10b981" if done else "#ef4444"})
                task_lookup[eid] = row
        except: continue
    res = calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 550}, key="main_cal")
    if res.get("eventClick"):
        task = task_lookup.get(res["eventClick"]["event"]["id"])
        if task is not None:
            st.markdown(f'<div class="detail-box"><h2>🔍 פרטי משימה</h2><p><strong>משימה:</strong> {task["Task_Name"]}</p><p><strong>תדירות:</strong> {task["Recurring"]}</p><p><strong>תיאור:</strong> {task["Description"]}</p></div>', unsafe_allow_html=True)

elif choice == OPT_ADD:
    st.title("➕ הוספת משימה")
    with st.form("new_task"):
        n = st.text_input("שם המשימה")
        f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        d = st.date_input("תאריך התחלה")
        ds = st.text_area("תיאור")
        if st.form_submit_button("שמור"):
            new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df); st.success("נשמר!"); st.rerun()

elif choice == OPT_MANAGE:
    st.title("⚙️ ניהול נתונים")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        t_del = st.selectbox("בחר משימה למחיקה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != t_del]
            save_data(st.session_state.df); st.rerun()
