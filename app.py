import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול משימות - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX מלא
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
    /* עיצוב ה-Sidebar */
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] h3 { color: #60a5fa !important; font-weight: 800 !important; }

    /* כפתור התנתקות בתחתית */
    .stButton > button[key="logout_btn"] {
        background-color: #b91c1c !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 50px !important;
        border: none !important;
        transition: 0.3s;
        margin-top: 20px;
    }
    .stButton > button[key="logout_btn"]:hover { background-color: #dc2626 !important; transform: scale(1.02); }

    /* עיצוב כרטיסי הכניסה הענקיים */
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
        pointer-events: none;
    }
    
    .card-icon { font-size: 80px; margin-bottom: 20px; }
    .card-title { font-size: 36px; font-weight: 900; color: #1e293b; text-align: center; }
    .card-strip { width: 100%; height: 20px; position: absolute; bottom: 0; left: 0; }

    /* הפיכת כפתורי ה-Streamlit לשקופים מעל הכרטיסים */
    div.stButton > button:not([key="logout_btn"]):not(.action-btn) {
        height: 450px !important;
        width: 100% !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        position: absolute !important;
        top: -450px !important; 
        z-index: 100 !important;
    }

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
    </style>
    """, unsafe_allow_html=True)

# 3. ניהול נתונים
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
                    scheduled.append({
                        "idx": idx, 
                        "id": row['ID'], 
                        "name": row['Task_Name'], 
                        "desc": row['Description'], 
                        "recurring": f, 
                        "is_done": target_str in str(row['Done_Dates']).split(",")
                    })
        except: continue
    return scheduled

# 4. ניהול כניסה
if "user_role" not in st.session_state: st.session_state.user_role = None

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
            st.markdown(f"<div class='login-card'><div class='card-icon'>{r['icon']}</div><div class='card-title'>{r['title']}</div><div class='card-strip' style='background-color: {r['color']};'></div></div>", unsafe_allow_html=True)
            if st.button("", key=f"btn_{r['id']}", use_container_width=True):
                st.session_state.user_role = r['role']
                st.rerun()
    st.stop()

# 5. ניווט
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

# 6. דפים
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
    st.info("אנא סמן בתיבה (V) ברגע שסיימת משימה כדי לעדכן את המערכת")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(len(days))
    
    for i, day in enumerate(days):
        curr = start + timedelta(days=i)
        curr_str = curr.strftime('%Y-%m-%d')
        with cols[i]:
            st.markdown(f"<div style='background:#1e293b; color:white; padding:10px; border-radius:10px; text-align:center; margin-bottom:15px;'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            tasks = get_daily_status(curr)
            for t in tasks:
                if t['is_done']:
                    st.success(f"✅ {t['name']}")
                else:
                    # הוספת תיבת סימון לאישור משימה
                    confirm = st.checkbox(f"אישור: {t['name']}", key=f"chk_{t['id']}_{i}")
                    if confirm:
                        idx = t['idx']
                        current_done = str(st.session_state.df.at[idx, "Done_Dates"]).strip()
                        new_done = f"{current_done},{curr_str}".strip(",")
                        st.session_state.df.at[idx, "Done_Dates"] = new_done
                        save_data(st.session_state.df)
                        st.success(f"בוצע!")
                        st.rerun()

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
            st.markdown(f'<div style="background:#eff6ff; border:2px solid #3b82f6; padding:20px; border-radius:15px;"><h2>🔍 פרטי משימה</h2><p><strong>משימה:</strong> {task["Task_Name"]}</p><p><strong>תדירות:</strong> {task["Recurring"]}</p><p><strong>תיאור:</strong> {task["Description"]}</p></div>', unsafe_allow_html=True)

elif choice == OPT_ADD:
    st.title("➕ הוספת משימה חדשה")
    with st.form("new_task"):
        n = st.text_input("שם המשימה")
        f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        d = st.date_input("תאריך התחלה", datetime.now())
        ds = st.text_area("תיאור")
        if st.form_submit_button("שמור"):
            new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df); st.success("נשמר!"); st.rerun()

elif choice == OPT_MANAGE:
    st.title("⚙️ הגדרות ניהול")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        t_del = st.selectbox("בחר משימה למחיקה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != t_del]
            save_data(st.session_state.df); st.rerun()
