import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול משימות - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. הזרקת עיצוב CSS מתוקן ללוח שנה ולסיידבר
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
    /* סיידבר כהה */
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] h3 { color: #60a5fa !important; font-weight: 800 !important; }

    /* התאמת לוח השנה למסך */
    .calendar-container {
        width: 100%;
        max-width: 100%;
        overflow-x: auto; /* מאפשר גלילה רוחבית רק אם המסך ממש קטן */
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* תיקון גובה ורוחב של הלוח עצמו */
    .fc { 
        max-width: 100% !important;
        height: auto !important; 
        min-height: 600px !important;
    }
    
    /* עיצוב כרטיסי כניסה ומשימות */
    .login-card {
        background: white; border-radius: 24px; height: 350px;
        display: flex; flex-direction: column; justify-content: center;
        align-items: center; box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; position: relative; overflow: hidden;
    }
    .card-icon { font-size: 70px; margin-bottom: 15px; }
    .card-title { font-size: 30px; font-weight: 900; color: #1e293b; text-align: center; }
    .card-strip { width: 100%; height: 10px; position: absolute; bottom: 0; left: 0; }
    
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

# 4. אתחול Session
if "user_role" not in st.session_state: st.session_state.user_role = None
if "df" not in st.session_state: st.session_state.df = load_data()
if "current_page" not in st.session_state: st.session_state.current_page = None

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# --- מסך כניסה ---
if st.session_state.user_role is None:
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem; font-weight: 900; color: #0f172a; padding-top: 40px;'>אחים כהן - ניהול משימות</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="large")
    roles = [
        {"id": "admin", "title": "מנהל WMS", "icon": "🔑", "color": "#2563eb", "role": "מנהל WMS"},
        {"id": "staff", "title": "צוות מחסן", "icon": "📦", "color": "#f59e0b", "role": "צוות מחסן"},
        {"id": "vp", "title": "סמנכ\"ל", "icon": "📊", "color": "#10b981", "role": "סמנכ\"ל"}
    ]
    for i, col in enumerate([col1, col2, col3]):
        with col:
            r = roles[i]
            st.markdown(f"<div class='login-card'><div class='card-icon'>{r['icon']}</div><div class='card-title'>{r['title']}</div><div class='card-strip' style='background-color: {r['color']};'></div></div>", unsafe_allow_html=True)
            if st.button(f"כניסה כ-{r['role']}", key=f"btn_{r['id']}", use_container_width=True):
                st.session_state.user_role = r['role']
                st.session_state.current_page = OPT_WORK if r['role'] == "צוות מחסן" else OPT_DASH
                st.rerun()
    st.stop()

# --- ניווט ---
menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE] if st.session_state.user_role == "מנהל WMS" else [OPT_WORK, OPT_CAL] if st.session_state.user_role == "צוות מחסן" else [OPT_DASH, OPT_CAL]
if st.session_state.current_page not in menu: st.session_state.current_page = menu[0]

with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    choice = st.radio("ניווט:", menu, index=menu.index(st.session_state.current_page))
    st.session_state.current_page = choice
    if st.button("🚪 התנתקות", key="logout_btn", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- דפים ---
if choice == OPT_DASH:
    st.title("📊 דשבורד")
    tasks = get_daily_status(datetime.now())
    for t in tasks:
        color = "#10b981" if t['is_done'] else "#f59e0b"
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><strong>{t["name"]}</strong></div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.title("📋 סידור עבודה")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    cols = st.columns(5)
    for i, day in enumerate(["א", "ב", "ג", "ד", "ה"]):
        curr = start + timedelta(days=i)
        with cols[i]:
            st.write(f"**יום {day}**")
            for t in get_daily_status(curr):
                if t['is_done']: st.success(t['name'])
                elif st.checkbox(f"{t['name']}", key=f"c_{t['id']}_{i}"):
                    idx = t['idx']
                    st.session_state.df.at[idx, "Done_Dates"] = f"{str(st.session_state.df.at[idx, 'Done_Dates'])},{curr.strftime('%Y-%m-%d')}".strip(",")
                    save_data(st.session_state.df); st.rerun()

elif choice == OPT_CAL:
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
    
    # עטיפה של הלוח בתוך ה-Container שעיצבנו ב-CSS
    st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
    calendar(events=events, options={"direction": "rtl", "locale": "he", "initialView": "dayGridMonth"}, key="cal_fixed")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == OPT_ADD:
    st.title("➕ הוספה")
    with st.form("add"):
        name = st.text_input("שם")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        if st.form_submit_button("שמור"):
            new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":name, "Recurring":freq, "Date":datetime.now().strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df); st.rerun()

elif choice == OPT_MANAGE:
    st.title("⚙️ הגדרות")
    edited = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
    if st.button("שמור"):
        st.session_state.df = edited
        save_data(edited); st.rerun()
