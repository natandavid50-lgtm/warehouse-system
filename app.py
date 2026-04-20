import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול משימות - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] h3 { color: #60a5fa !important; font-weight: 800 !important; }
    .stButton > button[key="logout_btn"] {
        background-color: #b91c1c !important; border-radius: 12px !important;
        font-weight: bold !important; height: 50px !important; border: none !important; margin-top: 20px;
    }
    .login-card {
        background: white; border-radius: 20px; height: 450px; 
        display: flex; flex-direction: column; justify-content: center;
        align-items: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; position: relative; overflow: hidden; pointer-events: none;
    }
    .card-icon { font-size: 80px; margin-bottom: 20px; }
    .card-title { font-size: 36px; font-weight: 900; color: #1e293b; text-align: center; }
    .card-strip { width: 100%; height: 20px; position: absolute; bottom: 0; left: 0; }
    div.stButton > button:not([key="logout_btn"]):not(.action-btn):not([key^="chk_"]) {
        height: 450px !important; width: 100% !important; background: transparent !important;
        color: transparent !important; border: none !important; position: absolute !important;
        top: -450px !important; z-index: 100 !important;
    }
    .task-card {
        background: white; padding: 20px; border-radius: 15px;
        margin-bottom: 12px; border-right: 10px solid #3b82f6;
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
                    scheduled.append({"idx": idx, "id": row['ID'], "name": row['Task_Name'], "desc": row['Description'], "recurring": f, "is_done": target_str in str(row['Done_Dates']).split(",")})
        except: continue
    return scheduled

# 4. אתחול Session State
if "user_role" not in st.session_state: st.session_state.user_role = None
if "df" not in st.session_state: st.session_state.df = load_data()
if "current_page" not in st.session_state: st.session_state.current_page = None

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# --- פונקציית ניווט בטוחה ---
def nav_to(page):
    st.session_state.current_page = page

# --- מסך כניסה ---
if st.session_state.user_role is None:
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem; font-weight: 900; padding-top: 40px;'>ברוכים הבאים למערכת ניהול משימות - אחים כהן</h1>", unsafe_allow_html=True)
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
            if st.button("", key=f"login_trigger_{r['id']}", use_container_width=True):
                st.session_state.user_role = r['role']
                st.session_state.current_page = OPT_WORK if r['role'] == "צוות מחסן" else OPT_DASH
                st.rerun()
    st.stop()

# --- הגדרת תפריט דינמי ---
if st.session_state.user_role == "מנהל WMS": 
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן": 
    menu = [OPT_WORK, OPT_CAL]
else: 
    menu = [OPT_DASH, OPT_CAL]

# הגנה: אם הדף לא קיים בתפריט (קורה במעבר בין משתמשים), חזור לדף הראשון
if st.session_state.current_page not in menu:
    st.session_state.current_page = menu[0]

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    st.divider()
    
    # שימוש ב-Radio עם מפתח סופר-ייחודי ושימוש ב-current_page
    choice = st.radio(
        "ניווט:", 
        menu, 
        index=menu.index(st.session_state.current_page),
        key=f"fixed_nav_{st.session_state.user_role}"
    )
    st.session_state.current_page = choice

    st.write("<br>"*15, unsafe_allow_html=True)
    if st.button("🚪 התנתקות", key="logout_btn", use_container_width=True):
        st.session_state.user_role = None
        st.session_state.current_page = None
        st.rerun()

# --- הצגת הדפים (שימוש ב-st.session_state.current_page) ---
current = st.session_state.current_page

if current == OPT_DASH:
    st.title("📊 דשבורד בקרה")
    tasks = get_daily_status(datetime.now())
    total, done = len(tasks), sum(1 for t in tasks if t['is_done'])
    c1, c2, c3 = st.columns(3)
    c1.metric("📋 משימות להיום", total)
    c2.metric("✅ בוצעו", done)
    c3.metric("🎯 הספק", f"{int(done/total*100) if total>0 else 0}%")
    for t in tasks:
        color = "#10b981" if t['is_done'] else "#f59e0b"
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><strong>{t["name"]}</strong><br>{t["desc"]}</div>', unsafe_allow_html=True)

elif current == OPT_WORK:
    st.title("📋 סידור עבודה שבועי")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(len(days))
    for i, day in enumerate(days):
        curr = start + timedelta(days=i)
        curr_str = curr.strftime('%Y-%m-%d')
        with cols[i]:
            st.markdown(f"<div style='background:#1e293b; color:white; padding:10px; border-radius:10px; text-align:center; margin-bottom:15px;'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            for t in get_daily_status(curr):
                if t['is_done']: st.success(f"✅ {t['name']}")
                else:
                    if st.checkbox(f"בצע: {t['name']}", key=f"chk_{t['id']}_{curr_str}"):
                        idx = t['idx']
                        done_dates = str(st.session_state.df.at[idx, "Done_Dates"]).strip()
                        st.session_state.df.at[idx, "Done_Dates"] = f"{done_dates},{curr_str}".strip(",")
                        save_data(st.session_state.df)
                        st.rerun()

elif current == OPT_CAL:
    st.title("📅 לוח שנה")
    cal_events, task_lookup = [], {}
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            f = row['Recurring']
            for i in range(40):
                gap = 1 if f=="יומי" else 7 if f=="שבועי" else 14 if f=="דו-שבועי" else 30 if f=="חודשי" else 0
                d = (base + timedelta(days=i*gap)).strftime("%Y-%m-%d")
                done = d in str(row['Done_Dates'])
                eid = f"{row['ID']}_{d}"
                cal_events.append({"id": eid, "title": f"{'✅' if done else '⏳'} {row['Task_Name']}", "start": d, "color": "#10b981" if done else "#ef4444"})
                task_lookup[eid] = row
                if f == "לא": break
        except: continue
    
    # מפתח ייחודי ללוח שנה שמוודא שהוא לא קורס
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he"}, key=f"full_calendar_{st.session_state.user_role}")

elif current == OPT_ADD:
    st.title("➕ הוספת משימה")
    with st.form("new_task"):
        n = st.text_input("שם המשימה")
        f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        d = st.date_input("תאריך התחלה", datetime.now())
        ds = st.text_area("תיאור")
        if st.form_submit_button("שמור"):
            new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df); st.success("נשמר בהצלחה!"); st.rerun()

elif current == OPT_MANAGE:
    st.title("⚙️ הגדרות")
    edited = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
    if st.button("שמור שינויים"):
        st.session_state.df = edited
        save_data(edited); st.success("הנתונים עודכנו!"); st.rerun()
