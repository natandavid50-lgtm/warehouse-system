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
# 2) Theme / CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-main: #f3f6fb;
    --card-white: #ffffff;
    --text-dark: #0f172a;
    --accent-blue: #2563eb;
    --accent-violet: #7c3aed;
    --border-color: #dbe4f0;
    --success: #10b981;
    --warning: #f59e0b;
    --shadow-md: 0 10px 24px rgba(15, 23, 42, 0.08);
    --radius-lg: 22px;
}

html, body, [class*="css"] {
    font-family: "Heebo", "Inter", sans-serif !important;
    direction: rtl;
    text-align: right;
}

.stApp {
    background: radial-gradient(circle at 85% 10%, rgba(37,99,235,0.08), transparent 40%),
                linear-gradient(180deg, #f8fbff 0%, var(--bg-main) 45%, #edf3fa 100%);
}

.hero-wrap {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 24px;
    box-shadow: var(--shadow-md);
    padding: 25px;
    margin-bottom: 25px;
    text-align: center;
}

/* כפתורי כניסה ראשיים */
.stButton > button {
    min-height: 200px;
    border-radius: var(--radius-lg) !important;
    font-weight: 900 !important;
    font-size: 1.5rem !important;
}

/* עיצוב הפופ-אובר (כפתור המשימה הקטן) */
div[data-testid="stPopover"] > button {
    width: 100% !important;
    min-height: 50px !important; /* קטן יותר משמעותית */
    margin-bottom: 8px !important;
    border-radius: 12px !important;
    font-size: 0.95rem !important; /* פונט קטן יותר */
    font-weight: 700 !important;
    background: white !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
}

.week-day-chip {
    background: linear-gradient(180deg, #edf3ff 0%, #e8f0ff 100%);
    border: 1px solid #cfe0ff;
    border-radius: 12px;
    text-align: center;
    padding: 10px;
    margin-bottom: 15px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3) Data & Logic
# =========================
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
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
# 4) App Flow
# =========================
if "user_role" not in st.session_state: st.session_state.user_role = None
if "show_login" not in st.session_state: st.session_state.show_login = False

ADMIN_PASSWORD = "1234"

if st.session_state.user_role is None:
    st.markdown('<div class="hero-wrap"><div class="hero-title" style="font-size:2.5rem; font-weight:900;">אחים כהן • ניהול מחסן</div></div>', unsafe_allow_html=True)
    if not st.session_state.show_login:
        c1, c2, c3 = st.columns(3)
        if c1.button("🔑\nמנהל WMS", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()
        if c2.button("📦\nצוות מחסן", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
        if c3.button("📊\nסמנכ\"ל", use_container_width=True):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
    else:
        pwd = st.text_input("סיסמה:", type="password")
        if st.button("כניסה"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.user_role = "מנהל WMS"
                st.session_state.show_login = False
                st.rerun()
            else: st.error("שגויה")
    st.stop()

df = load_data()
st.sidebar.subheader(f"שלום, {st.session_state.user_role}")
if st.sidebar.button("התנתקות"):
    st.session_state.user_role = None
    st.rerun()

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"
menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE] if st.session_state.user_role == "מנהל WMS" else [OPT_WORK, OPT_CAL]
choice = st.sidebar.radio("תפריט", menu)

# --- דשבורד ---
if choice == OPT_DASH:
    st.header(OPT_DASH)
    today_tasks = get_daily_status(df, datetime.now())
    m1, m2 = st.columns(2)
    m1.metric("משימות היום", len(today_tasks))
    m2.metric("בוצעו", sum(1 for t in today_tasks if t["is_done"]))

# --- סידור עבודה (הגרסה החדשה עם הפופ-אפ) ---
elif choice == OPT_WORK:
    st.header(OPT_WORK)
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)

    for i, name in enumerate(days):
        curr_d = start + timedelta(days=i)
        d_str = curr_d.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="week-day-chip">{name}<br>{curr_d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            tasks = get_daily_status(df, curr_d)
            for t in tasks:
                label = f"✅ {t['name']}" if t['is_done'] else f"⏳ {t['name']}"
                
                # יצירת כפתור "פופ-אובר" לכל משימה
                with st.popover(label, use_container_width=True):
                    st.markdown(f"### {t['name']}")
                    st.write(f"**פירוט:** {t['desc'] if t['desc'] else 'אין תיאור'}")
                    st.write(f"**תאריך:** {curr_d.strftime('%d/%m/%Y')}")
                    
                    if not t['is_done']:
                        if st.button("סמן כבוצע ✅", key=f"done_{t['id']}_{d_str}"):
                            idx = t['idx']
                            old = str(df.at[idx, "Done_Dates"])
                            df.at[idx, "Done_Dates"] = f"{old},{d_str}".strip(",")
                            save_data(df)
                            st.rerun()
                    else:
                        st.success("המשימה בוצעה!")

# --- לוח שנה ---
elif choice == OPT_CAL:
    st.header(OPT_CAL)
    events = []
    for _, row in df.iterrows():
        try:
            base = pd.to_datetime(row["Date"]).date()
            for i in range(45):
                d = base + timedelta(days=i)
                if is_scheduled_on(base, row["Recurring"], d):
                    d_s = d.strftime("%Y-%m-%d")
                    events.append({
                        "title": row["Task_Name"], 
                        "start": d_s, 
                        "color": "#10b981" if d_s in str(row["Done_Dates"]) else "#ef4444"
                    })
        except: continue
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 550})

# --- הוספת משימה ---
elif choice == OPT_ADD:
    st.header(OPT_ADD)
    with st.form("new_task"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור המשימה (פירוט)")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        sd = st.date_input("תאריך התחלה")
        if st.form_submit_button("שמור"):
            new_task = pd.DataFrame([{"ID": int(datetime.now().timestamp()), "Task_Name": name, "Description": desc, "Recurring": freq, "Date": sd.strftime("%Y-%m-%d"), "Done_Dates": ""}])
            df = pd.concat([df, new_task], ignore_index=True)
            save_data(df)
            st.success("נוסף!")
            st.rerun()

# --- הגדרות ---
elif choice == OPT_MANAGE:
    st.dataframe(df[["Task_Name", "Recurring"]], use_container_width=True)
    if st.button("מחק הכל"):
        save_data(pd.DataFrame(columns=df.columns))
        st.rerun()
