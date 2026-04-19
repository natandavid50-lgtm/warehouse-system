import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת מחסן - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX מלא
st.markdown("""
    <style>
    .stApp { background: #f8fafc; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    section[data-testid="stSidebar"] .st-bd, section[data-testid="stSidebar"] .st-bc,
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-size: 1.1rem !important;
    }
    section[data-testid="stSidebar"] h3 { color: #60a5fa !important; font-weight: 800 !important; }

    /* מסך כניסה */
    .stButton>button {
        height: 280px !important;
        border-radius: 25px !important;
        background: white !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button p { font-size: 30px !important; font-weight: 800 !important; }
    
    /* פסי צבע בכניסה */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-bottom: 12px solid #2563eb !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-bottom: 12px solid #d97706 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-bottom: 12px solid #059669 !important; }

    /* כרטיסי משימות */
    .task-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 12px;
        border-right: 8px solid #3b82f6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* תיבת תיאור משימה מלוח שנה */
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

# --- פונקציות נתונים ---
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

# 4. ניהול כניסה
if "user_role" not in st.session_state: st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown("<h1 style='text-align: center; color: #0f172a; padding-top: 50px;'>מערכת המחסן - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.5rem;'>בחר תפקיד לכניסה</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="large")
    with c1: 
        if st.button("🔑\nמנהל WMS", key="l1"): st.session_state.user_role = "מנהל WMS"; st.rerun()
    with c2: 
        if st.button("📦\nצוות מחסן", key="l2"): st.session_state.user_role = "צוות מחסן"; st.rerun()
    with c3: 
        if st.button("📊\nסמנכ\"ל", key="l3"): st.session_state.user_role = "סמנכ\"ל"; st.rerun()
    st.stop()

# 5. ניווט וטעינה
if "df" not in st.session_state: st.session_state.df = load_data()

with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    st.divider()
    OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"
    if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
    elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
    else: menu = [OPT_DASH, OPT_CAL]
    choice = st.radio("ניווט:", menu)
    if st.button("🚪 התנתקות", use_container_width=True): st.session_state.user_role = None; st.rerun()

# 6. דפים
if choice == OPT_DASH:
    st.title("📊 דשבורד בקרה")
    tasks = get_daily_status(datetime.now())
    total, done = len(tasks), sum(1 for t in tasks if t['is_done'])
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("📋 משימות להיום", total)
    col_m2.metric("✅ בוצעו", done)
    col_m3.metric("🎯 הספק", f"{int(done/total*100) if total>0 else 0}%")
    st.divider()
    for t in tasks:
        icon, color = ("✅", "#10b981") if t['is_done'] else ("⏳", "#f59e0b")
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><div><strong>{t["name"]}</strong><br><small>{t["desc"]}</small></div><div>{icon}</div></div>', unsafe_allow_html=True)

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
                status_prefix = "✅" if t['is_done'] else "⏳"
                st.markdown(f"**{status_prefix} {t['name']}**")
                if not t['is_done'] and st.button("בצע", key=f"btn_{t['id']}_{i}"):
                    idx = t['idx']
                    st.session_state.df.at[idx, "Done_Dates"] = f"{str(st.session_state.df.at[idx, 'Done_Dates'])},{curr.strftime('%Y-%m-%d')}".strip(",")
                    save_data(st.session_state.df); st.rerun()

elif choice == OPT_CAL:
    st.title("📅 לוח שנה")
    st.info("טיפ: לחץ על משימה בלוח כדי לראות את הפרטים שלה למטה")
    
    cal_events = []
    # מפה כדי לשלוף נתונים בלחיצה
    task_lookup = {}
    
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            f = row['Recurring']
            for i in range(100 if f != "לא" else 1):
                gap = 1 if f=="יומי" else 7 if f=="שבועי" else 14 if f=="דו-שבועי" else 30 if f=="חודשי" else 0
                d = (base + timedelta(days=i*gap)).strftime("%Y-%m-%d")
                is_done = d in str(row['Done_Dates'])
                event_id = f"{row['ID']}_{d}"
                cal_events.append({
                    "id": event_id,
                    "title": f"{'✅' if is_done else '⏳'} {row['Task_Name']}",
                    "start": d,
                    "color": "#10b981" if is_done else "#ef4444"
                })
                task_lookup[event_id] = row
        except: continue

    res = calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 500}, key="main_cal")
    
    # בדיקה אם המשתמש לחץ על משימה
    if res.get("eventClick"):
        clicked_id = res["eventClick"]["event"]["id"]
        if clicked_id in task_lookup:
            task = task_lookup[clicked_id]
            st.markdown(f"""
                <div class="detail-box">
                    <h2 style="margin-top:0; color:#1e40af;">🔍 פרטי משימה</h2>
                    <p><strong>שם המשימה:</strong> {task['Task_Name']}</p>
                    <p><strong>תדירות:</strong> {task['Recurring']}</p>
                    <p><strong>תיאור מלא:</strong><br>{task['Description']}</p>
                </div>
            """, unsafe_allow_html=True)

elif choice == OPT_ADD:
    st.title("➕ הוספת משימה")
    with st.form("f"):
        n = st.text_input("שם המשימה")
        f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        d = st.date_input("תאריך התחלה")
        ds = st.text_area("תיאור")
        if st.form_submit_button("שמור"):
            new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df); st.success("נוסף!"); st.rerun()

elif choice == OPT_MANAGE:
    st.title("⚙️ הגדרות")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        t_del = st.selectbox("מחק:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != t_del]
            save_data(st.session_state.df); st.rerun()
