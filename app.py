import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from streamlit_calendar import calendar
import calendar as pycal
import os

# =========================
# 1) App Config
# =========================
st.set_page_config(
    page_title="אחים כהן | ניהול מחסן",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = "warehouse_management_db.csv"

# =========================
# 2) Theme / CSS (Professional Light UI)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-main: #f3f6fb;
    --card-white: #ffffff;
    --text-dark: #0f172a;
    --text-muted: #64748b;
    --accent-blue: #2563eb;
    --accent-violet: #7c3aed;
    --border-color: #dbe4f0;
    --success: #10b981;
    --warning: #f59e0b;
    --shadow-sm: 0 4px 12px rgba(15, 23, 42, 0.06);
    --shadow-md: 0 10px 24px rgba(15, 23, 42, 0.08);
    --radius: 16px;
    --radius-lg: 22px;
}

html, body, [class*="css"] {
    font-family: "Heebo", "Inter", sans-serif !important;
    direction: rtl;
    text-align: right;
}

.stApp {
    background: linear-gradient(180deg, #f8fbff 0%, var(--bg-main) 100%);
    color: var(--text-dark);
}

/* Hero Section */
.hero-wrap {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 24px;
    box-shadow: var(--shadow-md);
    padding: 30px;
    margin-bottom: 25px;
    text-align: center;
}
.hero-title { font-size: 3rem !important; font-weight: 900; color: #0b1220; margin-bottom: 5px; }

/* Role Selection Buttons */
div[data-testid="stHorizontalBlock"] .stButton > button {
    min-height: 200px;
    border-radius: var(--radius-lg);
    background: white !important;
    border: 1.5px solid var(--border-color) !important;
    font-size: 1.5rem !important;
    transition: all 0.3s ease;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-md);
}

/* Custom styles for the Login/Action buttons to replace "kind=primary" */
.main .stButton > button {
    background: linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-violet) 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    padding: 0.5rem 2rem !important;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    box-shadow: var(--shadow-sm);
}

/* Task Items */
.task-item {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    margin-bottom: 10px;
}
.task-done { border-right: 6px solid var(--success); background: #f0fdf4; }
.task-pending { border-right: 6px solid var(--warning); background: #fffbeb; }

.week-day-chip {
    background: #edf3ff;
    border: 1px solid #cfe0ff;
    border-radius: 12px;
    text-align: center;
    padding: 10px;
    margin-bottom: 10px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3) Data Layer
# =========================
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            for col in ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"]:
                if col not in df.columns: df[col] = ""
            return df.fillna("")
        except: pass
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def is_scheduled_on(base_date, recurring, target_date):
    if target_date < base_date: return False
    diff = (target_date - base_date).days
    if recurring == "לא": return diff == 0
    if recurring == "יומי": return diff < 365
    if recurring == "שבועי": return diff % 7 == 0
    if recurring == "דו-שבועי": return diff % 14 == 0
    if recurring == "חודשי": return target_date.day == base_date.day
    return False

def get_daily_status(df_input, target_dt):
    target_date = target_dt.date()
    target_str = target_date.strftime("%Y-%m-%d")
    scheduled = []
    for idx, row in df_input.iterrows():
        try:
            base_date = pd.to_datetime(row["Date"]).date()
            if is_scheduled_on(base_date, row["Recurring"], target_date):
                done_list = str(row["Done_Dates"]).split(",")
                scheduled.append({
                    "idx": idx, "id": row["ID"], "name": row["Task_Name"],
                    "desc": row["Description"], "is_done": target_str in done_list
                })
        except: continue
    return scheduled

# =========================
# 4) Main Flow
# =========================
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False

ADMIN_PASSWORD = "1234"

if st.session_state.user_role is None:
    st.markdown('<div class="hero-wrap"><div class="hero-title">אחים כהן • ניהול מחסן</div><p style="color:gray;">מערכת ניהול משימות ובקרה</p></div>', unsafe_allow_html=True)

    if not st.session_state.show_login:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔑\nמנהל WMS", use_container_width=True):
                st.session_state.show_login = True
                st.rerun()
        with c2:
            if st.button("📦\nצוות מחסן", use_container_width=True):
                st.session_state.user_role = "צוות מחסן"
                st.rerun()
        with c3:
            if st.button("📊\nסמנכ\"ל", use_container_width=True):
                st.session_state.user_role = "סמנכ\"ל"
                st.rerun()
    else:
        st.markdown("<div style='max-width:400px; margin:0 auto; background:white; padding:20px; border-radius:15px; border:1px solid #dbe4f0;'>", unsafe_allow_html=True)
        pwd = st.text_input("הזן סיסמת מנהל:", type="password")
        col_login, col_back = st.columns(2)
        if col_login.button("כניסה למערכת", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.user_role = "מנהל WMS"
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("סיסמה שגויה")
        if col_back.button("חזרה", use_container_width=True):
            st.session_state.show_login = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- App Content ---
df = load_data()
st.sidebar.title(f"שלום, {st.session_state.user_role}")
if st.sidebar.button("התנתק"):
    st.session_state.user_role = None
    st.rerun()

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספה", "⚙️ הגדרות"
if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן":
    menu = [OPT_WORK, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("תפריט", menu)

if choice == OPT_DASH:
    st.header(OPT_DASH)
    today_tasks = get_daily_status(df, datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t["is_done"])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("משימות היום", total)
    m2.metric("בוצעו", done)
    m3.metric("הספק", f"{int(done/total*100) if total > 0 else 0}%")
    
    st.subheader("משימות נוכחיות")
    for t in today_tasks:
        cls = "task-done" if t["is_done"] else "task-pending"
        st.markdown(f'<div class="task-item {cls}"><b>{"✅" if t["is_done"] else "⏳"} {t["name"]}</b><br>{t["desc"]}</div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.header(OPT_WORK)
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)
    for i, name in enumerate(days):
        d = start + timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="week-day-chip">{name}<br>{d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            tasks = get_daily_status(df, d)
            for t in tasks:
                if t["is_done"]: st.success(t["name"])
                else:
                    if st.button(f"בצע: {t['name']}", key=f"{t['id']}_{d_str}"):
                        idx = t['idx']
                        old = str(df.at[idx, "Done_Dates"])
                        df.at[idx, "Done_Dates"] = f"{old},{d_str}".strip(",")
                        save_data(df)
                        st.rerun()

elif choice == OPT_CAL:
    st.header(OPT_CAL)
    events = []
    for _, row in df.iterrows():
        try:
            base = pd.to_datetime(row["Date"]).date()
            for i in range(60):
                curr = base + timedelta(days=i)
                if is_scheduled_on(base, row["Recurring"], curr):
                    c_str = curr.strftime("%Y-%m-%d")
                    events.append({"title": row["Task_Name"], "start": c_str, "color": "#10b981" if c_str in str(row["Done_Dates"]) else "#ef4444"})
        except: continue
    calendar(events=events, options={"direction": "rtl", "locale": "he"})

elif choice == OPT_ADD:
    st.header("הוספת משימה חדשה")
    with st.form("add_task"):
        t_name = st.text_input("שם המשימה")
        t_desc = st.text_area("תיאור/הוראות")
        t_freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        t_start = st.date_input("תאריך התחלה")
        if st.form_submit_button("שמור משימה"):
            if t_name:
                new_row = pd.DataFrame([{"ID": int(datetime.now().timestamp()), "Task_Name": t_name, "Description": t_desc, "Recurring": t_freq, "Date": t_start.strftime("%Y-%m-%d"), "Done_Dates": ""}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("המשימה נוספה!")
                st.rerun()

elif choice == OPT_MANAGE:
    st.header("ניהול משימות")
    st.dataframe(df[["Task_Name", "Recurring", "Date"]], use_container_width=True)
    if not df.empty:
        to_del = st.selectbox("בחר משימה למחיקה:", df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            df = df[df["Task_Name"] != to_del]
            save_data(df)
            st.rerun()
