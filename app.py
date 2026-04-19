import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת משימות - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX מלא - מעודכן
st.markdown("""
    <style>
    .stApp { background: #f8fafc; }
    
    /* Sidebar - קריאות מלאה */
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    section[data-testid="stSidebar"] .st-bd, section[data-testid="stSidebar"] .st-bc,
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] h3 { color: #60a5fa !important; font-weight: 800 !important; }

    /* עיצוב כפתור התנתקות ייחודי */
    div[data-testid="stSidebarUserContent"] div[role="button"] {
        background-color: #b91c1c !important; /* אדום עמוק */
        color: white !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        font-weight: bold !important;
        border: none !important;
        transition: background-color 0.3s ease !important;
    }
    div[data-testid="stSidebarUserContent"] div[role="button"]:hover {
        background-color: #991b1b !important; /* אדום כהה יותר בריחוף */
    }

    /* מסך כניסה - כפתורים ענקיים */
    .login-container {
        padding: 80px 20px;
        text-align: center;
    }
    .stButton>button {
        height: 420px !important; /* הגדלה משמעותית */
        width: 100% !important;
        border-radius: 30px !important;
        background: white !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.1) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        border: 1px solid #f1f5f9 !important;
        padding: 25px !important;
    }
    .stButton>button:hover {
        transform: translateY(-15px) !important;
        box-shadow: 0 25px 60px rgba(0,0,0,0.15) !important;
        border-color: #3b82f6 !important;
    }
    /* טקסט בתוך כפתורי הכניסה */
    .stButton>button p {
        font-size: 42px !important; /* הגדלת טקסט */
        font-weight: 900 !important;
        margin-top: 20px !important;
    }
    
    /* פסי צבע בכניסה */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-bottom: 18px solid #2563eb !important; color: #1e40af !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-bottom: 18px solid #d97706 !important; color: #d97706 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-bottom: 18px solid #059669 !important; color: #059669 !important; }

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
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #0f172a; font-size: 4rem; font-weight: 900; margin-bottom: 10px;'>ברוכים הבאים למערכת ניהול משימות - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 1.8rem; margin-bottom: 60px;'>אנא בחר את התפקיד שלך לכניסה</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        if st.button("🔑\nמנהל WMS", key="btn1"):
            st.session_state.user_role = "מנהל WMS"; st.rerun()
    with col2:
        if st.button("📦\nצוות מחסן", key="btn2"):
            st.session_state.user_role = "צוות מחסן"; st.rerun()
    with col3:
        if st.button("📊\nסמנכ\"ל", key="btn3"):
            st.session_state.user_role = "סמנכ\"ל"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
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
    
    st.write("<br>"*12, unsafe_allow_html=True)
    if st.button("🚪 התנתקות מהמערכת", use_container_width=True): st.session_state.user_role = None; st.rerun()

# 6. דפים
if choice == OPT_DASH:
    st.title("📊 דשבורד בקרה")
    tasks = get_daily_status(datetime.now())
    total, done = len(tasks), sum(1 for t in tasks if t['is_done'])
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("📋 משימות להיום", total)
    col_m2.metric("✅ בוצעו בהצלחה", done)
    col_m3.metric("🎯 הספק", f"{int(done/total*100) if total>0 else 0}%")
    st.divider()
    for t in tasks:
        icon, color = ("✅", "#10b981") if t['is_done'] else ("⏳", "#f59e0b")
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><div><strong style="font-size:1.15rem;">{t["name"]}</strong><br><span style="color: #64748b;">{t["desc"]}</span></div><div style="font-size:24px;">{icon}</div></div>', unsafe_allow_html=True)

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

    res = calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 550}, key="main_cal")
    
    if res.get("eventClick"):
        clicked_id = res["eventClick"]["event"]["id"]
        if clicked_id in task_lookup:
            task = task_lookup[clicked_id]
            st.markdown(f"""
                <div class="detail-box">
                    <h2 style="margin-top:0; color:#1e40af;">🔍 פרטי משימה מהלוח</h2>
                    <p><strong>שם המשימה:</strong> {task['Task_Name']}</p>
                    <p><strong>תדירות:</strong> {task['Recurring']}</p>
                    <p><strong>תיאור מלא:</strong><br>{task['Description']}</p>
                </div>
            """, unsafe_allow_html=True)

elif choice == OPT_ADD:
    st.title("➕ הוספת משימה חדשה")
    with st.form("add_new_task"):
        n = st.text_input("שם המשימה")
        f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        d = st.date_input("תאריך התחלה", datetime.now())
        ds = st.text_area("תיאור מלא")
        if st.form_submit_button("שמור במערכת"):
            if n:
                new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
                new_row = pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df); st.success("המשימה נוספה בהצלחה!"); st.rerun()
            else:
                st.error("חובה להזין שם משימה.")

elif choice == OPT_MANAGE:
    st.title("⚙️ הגדרות")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        t_del = st.selectbox("מחק משימה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != t_del]
            save_data(st.session_state.df); st.rerun()
