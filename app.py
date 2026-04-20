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
    section[data-testid="stSidebar"] { background-color: #0f172a !important; min-width: 300px !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] h3 { color: #60a5fa !important; font-weight: 800 !important; }
    
    /* עיצוב כפתורי הניווט החדשים בסיידבר */
    .stButton > button.nav-btn {
        width: 100% !important;
        background-color: transparent !important;
        color: white !important;
        border: 1px solid #334155 !important;
        text-align: right !important;
        padding: 15px !important;
        font-size: 18px !important;
        margin-bottom: 8px !important;
        transition: 0.3s;
    }
    .stButton > button.nav-btn:hover {
        background-color: #1e293b !important;
        border-color: #60a5fa !important;
    }
    .stButton > button.active-nav {
        background-color: #2563eb !important;
        border-color: #60a5fa !important;
        font-weight: bold !important;
    }

    /* כפתור התנתקות */
    .stButton > button[key="logout_btn"] {
        background-color: #b91c1c !important; border-radius: 12px !important;
        font-weight: bold !important; height: 50px !important; border: none !important; margin-top: 20px;
    }

    /* כרטיסי כניסה */
    .login-card {
        background: white; border-radius: 20px; height: 400px; 
        display: flex; flex-direction: column; justify-content: center;
        align-items: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; position: relative; overflow: hidden; pointer-events: none;
    }
    .card-icon { font-size: 80px; margin-bottom: 20px; }
    .card-title { font-size: 32px; font-weight: 900; color: #1e293b; text-align: center; }
    
    div.stButton > button.login-trigger {
        height: 400px !important; width: 100% !important; background: transparent !important;
        color: transparent !important; border: none !important; position: absolute !important;
        top: -400px !important; z-index: 100 !important;
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

# --- מסך כניסה ---
if st.session_state.user_role is None:
    st.markdown("<h1 style='text-align: center; font-size: 3rem; font-weight: 900; padding-top: 40px;'>מערכת ניהול משימות - אחים כהן</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    roles = [
        {"id": "admin", "title": "WMS מנהל", "icon": "🔑", "role": "מנהל WMS"},
        {"id": "staff", "title": "צוות מחסן", "icon": "📦", "role": "צוות מחסן"},
        {"id": "vp", "title": "סמנכ\"ל", "icon": "📊", "role": "סמנכ\"ל"}
    ]
    for i, col in enumerate([col1, col2, col3]):
        with col:
            r = roles[i]
            st.markdown(f"<div class='login-card'><div class='card-icon'>{r['icon']}</div><div class='card-title'>{r['title']}</div></div>", unsafe_allow_html=True)
            if st.button(f"כניסה {r['id']}", key=f"btn_{r['id']}", help=r['role'], use_container_width=True):
                st.session_state.user_role = r['role']
                st.session_state.current_page = OPT_WORK if r['role'] == "צוות מחסן" else OPT_DASH
                st.rerun()
    st.stop()

# --- הגדרת תפריט מורשה ---
if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
else: menu = [OPT_DASH, OPT_CAL]

if st.session_state.current_page not in menu:
    st.session_state.current_page = menu[0]

# --- Sidebar (ניווט מבוסס כפתורים) ---
with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("<p style='color: #94a3b8;'>ניווט:</p>", unsafe_allow_html=True)
    for item in menu:
        is_active = "active-nav" if st.session_state.current_page == item else ""
        if st.button(item, key=f"nav_{item}", cls="nav-btn " + is_active, use_container_width=True):
            st.session_state.current_page = item
            st.rerun()

    st.write("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 התנתקות", key="logout_btn", use_container_width=True):
        st.session_state.user_role = None
        st.session_state.current_page = None
        st.rerun()

# --- הצגת התוכן ---
current = st.session_state.current_page

if current == OPT_DASH:
    st.title("📊 דשבורד בקרה")
    tasks = get_daily_status(datetime.now())
    t, d = len(tasks), sum(1 for x in tasks if x['is_done'])
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות להיום", t)
    c2.metric("בוצעו", d)
    c3.metric("הספק", f"{int(d/t*100) if t>0 else 0}%")
    for x in tasks:
        st.markdown(f'<div class="task-card" style="border-right-color: {"#10b981" if x["is_done"] else "#f59e0b"}"><strong>{x["name"]}</strong><br>{x["desc"]}</div>', unsafe_allow_html=True)

elif current == OPT_WORK:
    st.title("📋 סידור עבודה")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    cols = st.columns(5)
    for i, day in enumerate(["ראשון", "שני", "שלישי", "רביעי", "חמישי"]):
        curr = start + timedelta(days=i)
        curr_s = curr.strftime('%Y-%m-%d')
        with cols[i]:
            st.markdown(f"<div style='background:#1e293b; color:white; padding:10px; border-radius:8px; text-align:center;'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            for x in get_daily_status(curr):
                if x['is_done']: st.success(f"✅ {x['name']}")
                else:
                    if st.checkbox(f"בצע: {x['name']}", key=f"chk_{x['id']}_{curr_s}"):
                        idx = x['idx']
                        done = str(st.session_state.df.at[idx, "Done_Dates"]).strip()
                        st.session_state.df.at[idx, "Done_Dates"] = f"{done},{curr_s}".strip(",")
                        save_data(st.session_state.df); st.rerun()

elif current == OPT_CAL:
    st.title("📅 לוח שנה")
    events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            for i in range(30):
                gap = 1 if row['Recurring']=="יומי" else 7 if row['Recurring']=="שבועי" else 14 if row['Recurring']=="דו-שבועי" else 30 if row['Recurring']=="חודשי" else 0
                d = (base + timedelta(days=i*gap)).strftime("%Y-%m-%d")
                done = d in str(row['Done_Dates'])
                events.append({"title": f"{'✅' if done else '⏳'} {row['Task_Name']}", "start": d, "color": "#10b981" if done else "#ef4444"})
                if row['Recurring'] == "לא": break
        except: continue
    calendar(events=events, options={"direction": "rtl", "locale": "he"}, key="final_calendar")

elif current == OPT_ADD:
    st.title("➕ הוספת משימה")
    with st.form("add"):
        n = st.text_input("שם המשימה")
        f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        d = st.date_input("תאריך", datetime.now())
        ds = st.text_area("תיאור")
        if st.form_submit_button("שמור"):
            new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df); st.success("נוסף!"); st.rerun()

elif current == OPT_MANAGE:
    st.title("⚙️ הגדרות")
    edited = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
    if st.button("שמור"):
        st.session_state.df = edited
        save_data(edited); st.success("עודכן!"); st.rerun()
