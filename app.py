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
# 2) Theme / CSS (המראה המקורי והמלא)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-main: #f3f6fb;
    --text-dark: #0f172a;
    --text-muted: #64748b;
    --accent-blue: #2563eb;
    --accent-violet: #7c3aed;
    --border-color: #dbe4f0;
    --success: #10b981;
    --warning: #f59e0b;
    --radius-lg: 22px;
}

html, body, [class*="css"] {
    font-family: "Heebo", "Inter", sans-serif !important;
    direction: rtl;
    text-align: right;
}

.stApp {
    background: radial-gradient(circle at 85% 10%, rgba(37,99,235,0.08), transparent 40%),
                linear-gradient(180deg, #f8fbff 0%, var(--bg-main) 100%);
}

/* Hero Section */
.hero-wrap {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 24px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    padding: 30px;
    margin-bottom: 20px;
    text-align: center;
}
.hero-title { font-size: 3.15rem !important; font-weight: 900; color: #0b1220; }

/* כרטיסיות כניסה - העיצוב שחזר */
.stButton > button {
    min-height: 210px;
    border-radius: var(--radius-lg) !important;
    background: white !important;
    border: 1.5px solid var(--border-color) !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    transition: all 0.25s ease;
    font-weight: 900 !important;
    font-size: 1.65rem !important;
}
.stButton > button:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.1);
}

/* פסי צבע עליונים לכרטיסיות */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 8px solid #2563eb !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 8px solid #f59e0b !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 8px solid #10b981 !important; }

/* כפתורי פעולה (כמו כניסה ואישור) */
.stFormSubmitButton > button, 
div[data-testid="column"] .stButton > button[kind="secondary"] {
    background: linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-violet) 100%) !important;
    color: white !important;
    min-height: 44px !important;
    border-radius: 12px !important;
    border: none !important;
}

/* Metric & Task Cards */
[data-testid="stMetric"] { background: white; border: 1px solid var(--border-color); border-radius: 16px; padding: 15px; }
.task-item { background: white; padding: 15px; border-radius: 12px; border: 1px solid var(--border-color); margin-bottom: 10px; border-right: 6px solid #cbd5e1; }
.task-done { border-right-color: var(--success); background: #f0fdf4; }
.task-pending { border-right-color: var(--warning); background: #fffbeb; }

.week-day-chip { background: #edf3ff; border: 1px solid #cfe0ff; border-radius: 12px; text-align: center; padding: 10px; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# =========================
# 3) Data & Logic
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
# 4) Main App Flow
# =========================
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False

ADMIN_PASSWORD = "1234"

if st.session_state.user_role is None:
    st.markdown('<div class="hero-wrap"><div class="hero-title">אחים כהן • ניהול מחסן</div><p style="color:var(--text-muted);">מערכת ניהול משימות ובקרה</p></div>', unsafe_allow_html=True)

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
        # מסך הזנת סיסמה עם תיקון ה-TypeError
        st.markdown("<div style='max-width:400px; margin:0 auto; background:white; padding:25px; border-radius:20px; border:1px solid var(--border-color); box-shadow: 0 4px 15px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        st.subheader("כניסת מנהל")
        pwd = st.text_input("סיסמה:", type="password")
        col_ok, col_cancel = st.columns(2)
        if col_ok.button("כניסה", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.user_role = "מנהל WMS"
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("סיסמה שגויה")
        if col_cancel.button("ביטול", use_container_width=True):
            st.session_state.show_login = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Main Interface ---
df = load_data()
st.sidebar.markdown(f"### שלום, **{st.session_state.user_role}**")
if st.sidebar.button("🚪 התנתקות"):
    st.session_state.user_role = None
    st.rerun()

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספה", "⚙️ הגדרות"
if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן":
    menu = [OPT_WORK, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("ניווט", menu)

# --- Pages Logic (קוצר למען הבהירות) ---
if choice == OPT_DASH:
    st.markdown(f"## {OPT_DASH}")
    today_tasks = get_daily_status(df, datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t["is_done"])
    m1, m2, m3 = st.columns(3)
    m1.metric("משימות היום", total)
    m2.metric("בוצעו", done)
    m3.metric("הספק", f"{int(done/total*100) if total > 0 else 0}%")
    for t in today_tasks:
        cls = "task-done" if t["is_done"] else "task-pending"
        st.markdown(f'<div class="task-item {cls}"><b>{"✅" if t["is_done"] else "⏳"} {t["name"]}</b><br>{t["desc"]}</div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.markdown(f"## {OPT_WORK}")
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)
    for i, name in enumerate(days):
        d = start + timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="week-day-chip">{name}<br>{d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            for t in get_daily_status(df, d):
                if t["is_done"]: st.success(t["name"])
                else:
                    if st.button(f"בצע: {t['name']}", key=f"{t['id']}_{d_str}"):
                        idx = t['idx']
                        old = str(df.at[idx, "Done_Dates"])
                        df.at[idx, "Done_Dates"] = f"{old},{d_str}".strip(",")
                        save_data(df)
                        st.rerun()

elif choice == OPT_CAL:
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
    with st.form("add"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("הוראות")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        start_d = st.date_input("תאריך התחלה")
        if st.form_submit_button("שמור"):
            if name:
                new_row = pd.DataFrame([{"ID": int(datetime.now().timestamp()), "Task_Name": name, "Description": desc, "Recurring": freq, "Date": start_d.strftime("%Y-%m-%d"), "Done_Dates": ""}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("נוסף!")
                st.rerun()

elif choice == OPT_MANAGE:
    st.dataframe(df[["Task_Name", "Recurring", "Date"]], use_container_width=True)
    if not df.empty:
        to_del = st.selectbox("בחר למחיקה:", df["Task_Name"].unique())
        if st.button("מחק"):
            df = df[df["Task_Name"] != to_del]
            save_data(df)
            st.rerun()
