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
    --bg-soft: #eef3fa;
    --card-white: #ffffff;
    --text-dark: #0f172a;
    --text-muted: #64748b;
    --accent-blue: #2563eb;
    --accent-blue-2: #1d4ed8;
    --accent-violet: #7c3aed;
    --border-color: #dbe4f0;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
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

/* App background */
.stApp {
    background:
        radial-gradient(circle at 85% 10%, rgba(37,99,235,0.08), transparent 40%),
        radial-gradient(circle at 10% 15%, rgba(124,58,237,0.07), transparent 35%),
        linear-gradient(180deg, #f8fbff 0%, var(--bg-main) 45%, #edf3fa 100%);
    color: var(--text-dark);
}

/* Main container spacing */
.main .block-container {
    padding-top: 1.2rem;
    padding-bottom: 1.5rem;
    max-width: 1350px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%) !important;
    border-left: 1px solid var(--border-color) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text-dark) !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    font-weight: 800 !important;
}

/* Hero */
.hero-wrap {
    background: linear-gradient(120deg, #ffffff 0%, #f8fbff 55%, #f2f7ff 100%);
    border: 1px solid var(--border-color);
    border-radius: 24px;
    box-shadow: var(--shadow-md);
    padding: 30px 24px 18px 24px;
    margin-bottom: 18px;
}
.hero-title {
    text-align: center;
    font-size: 3.15rem !important;
    font-weight: 900;
    color: #0b1220;
    margin-bottom: 0.2rem;
    line-height: 1.2;
}
.hero-subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: var(--text-muted);
    margin-bottom: 0;
}

/* Login buttons (large role cards) */
.stButton > button {
    min-height: 210px;
    border-radius: var(--radius-lg);
    background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%) !important;
    border: 1.5px solid var(--border-color) !important;
    box-shadow: var(--shadow-sm);
    transition: all 0.25s ease;
    color: var(--text-dark) !important;
    font-weight: 800 !important;
}
.stButton > button:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-md);
    border-color: #b8c8e3 !important;
}
.stButton > button div p {
    font-size: 1.65rem !important;
    font-weight: 900 !important;
    line-height: 1.6 !important;
}

/* Role-card top accents */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 8px solid #2563eb !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 8px solid #f59e0b !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 8px solid #10b981 !important; }

/* Dashboard metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    padding: 16px 14px;
    box-shadow: var(--shadow-sm);
}

/* Task cards */
.task-item {
    background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    border-right: 6px solid #cbd5e1;
    margin-bottom: 10px;
}
.task-done { border-right-color: var(--success); background: #f0fdf4; }
.task-pending { border-right-color: var(--warning); background: #fffbeb; }

/* Inputs & Form Buttons */
.stTextInput input { border-radius: 12px !important; }
.stFormSubmitButton > button, button[kind="primary"] {
    min-height: 44px !important;
    border-radius: 12px !important;
    background: linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-violet) 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 18px rgba(37,99,235,0.22) !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3) Data Layer & Logic
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
# 4) Authentication & Main
# =========================
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False

ADMIN_PASSWORD = "1234"  # <--- שנה כאן את הסיסמה שלך

# --- Welcome Screen ---
if st.session_state.user_role is None:
    st.markdown('<div class="hero-wrap"><div class="hero-title">אחים כהן • ניהול מחסן</div><p class="hero-subtitle">מערכת ניהול משימות ובקרה</p></div>', unsafe_allow_html=True)

    if not st.session_state.show_login:
        c1, c2, c3 = st.columns(3, gap="medium")
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
        # חלונית הזנת סיסמה
        st.markdown("<div style='max-width:400px; margin:0 auto;'>", unsafe_allow_html=True)
        pwd = st.text_input("הזן סיסמת מנהל:", type="password")
        cc1, cc2 = st.columns(2)
        if cc1.button("כניסה", kind="primary", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.user_role = "מנהל WMS"
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("סיסמה שגויה")
        if cc2.button("ביטול", use_container_width=True):
            st.session_state.show_login = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Main App Interface ---
df = load_data()
st.sidebar.markdown(f"### שלום, **{st.session_state.user_role}**")
if st.sidebar.button("🚪 התנתקות"):
    st.session_state.user_role = None
    st.rerun()

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"
if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן":
    menu = [OPT_WORK, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("ניווט", menu)

# --- Pages Logic ---
if choice == OPT_DASH:
    st.markdown(f"## {OPT_DASH}")
    today_tasks = get_daily_status(df, datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t["is_done"])
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות פתוחות היום", total)
    c2.metric("בוצעו בפועל", done)
    c3.metric("אחוז עמידה ביעדים", f"{int(done/total*100) if total > 0 else 0}%")
    
    st.write("<br>", unsafe_allow_html=True)
    for t in today_tasks:
        status_class = "task-done" if t["is_done"] else "task-pending"
        icon = "✅" if t["is_done"] else "⏳"
        st.markdown(f'<div class="task-item {status_class}"><b>{icon} {t["name"]}</b><br><small>{t["desc"]}</small></div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.markdown(f"## {OPT_WORK}")
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)
    for i, day_name in enumerate(days_names):
        curr_day = start_of_week + timedelta(days=i)
        date_str = curr_day.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="week-day-chip"><b>{day_name}</b><br>{curr_day.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            tasks = get_daily_status(df, curr_day)
            for t in tasks:
                if t["is_done"]: st.success(f"**{t['name']}**")
                else:
                    if st.button(f"סמן: {t['name']}", key=f"btn_{t['id']}_{date_str}"):
                        idx = t['idx']
                        old = str(df.at[idx, "Done_Dates"])
                        df.at[idx, "Done_Dates"] = f"{old},{date_str}".strip(",")
                        save_data(df)
                        st.rerun()

elif choice == OPT_CAL:
    st.markdown(f"## {OPT_CAL}")
    events = []
    for _, row in df.iterrows():
        try:
            base = pd.to_datetime(row["Date"]).date()
            for i in range(60):
                d = base + timedelta(days=i)
                if is_scheduled_on(base, row["Recurring"], d):
                    d_str = d.strftime("%Y-%m-%d")
                    events.append({"title": row["Task_Name"], "start": d_str, "color": "#10b981" if d_str in str(row["Done_Dates"]) else "#ef4444"})
        except: continue
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})

elif choice == OPT_ADD:
    st.markdown(f"## {OPT_ADD}")
    with st.form("add_form"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        start_d = st.date_input("תאריך התחלה", value=datetime.now().date())
        if st.form_submit_button("הוסף משימה"):
            if name:
                new_row = pd.DataFrame([{"ID": int(datetime.now().timestamp()), "Task_Name": name, "Description": desc, "Recurring": freq, "Date": start_d.strftime("%Y-%m-%d"), "Done_Dates": ""}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("נוסף!")
                st.rerun()

elif choice == OPT_MANAGE:
    st.markdown(f"## {OPT_MANAGE}")
    st.dataframe(df[["Task_Name", "Recurring", "Date"]], use_container_width=True)
    if not df.empty:
        to_del = st.selectbox("מחק משימה:", df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            df = df[df["Task_Name"] != to_del]
            save_data(df)
            st.rerun()
