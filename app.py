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
    --text-dark: #0f172a;
    --text-muted: #64748b;
    --accent-blue: #2563eb;
    --border-color: #dbe4f0;
    --shadow-md: 0 10px 24px rgba(15, 23, 42, 0.08);
    --radius-lg: 22px;
}

html, body, [class*="css"] {
    font-family: "Heebo", "Inter", sans-serif !important;
    direction: rtl;
    text-align: right;
}

.stApp {
    background: 
        radial-gradient(circle at 85% 10%, rgba(37,99,235,0.08), transparent 40%),
        linear-gradient(180deg, #f8fbff 0%, var(--bg-main) 45%, #edf3fa 100%);
    color: var(--text-dark);
}

.hero-wrap {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 24px;
    box-shadow: var(--shadow-md);
    padding: 30px 24px;
    margin-bottom: 25px;
    text-align: center;
}

div[data-testid="stHorizontalBlock"] .stButton > button {
    min-height: 210px !important;
    border-radius: var(--radius-lg) !important;
    background: white !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06) !important;
    font-size: 1.65rem !important;
    font-weight: 900 !important;
    color: var(--text-dark) !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 8px solid #2563eb !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 8px solid #f59e0b !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 8px solid #10b981 !important; }

div[data-testid="stPopover"] > button {
    width: 100% !important;
    min-height: 80px !important;
    margin-bottom: 12px !important;
    background: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 15px !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
}

[data-testid="stMetric"] {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-md);
}

.week-day-chip {
    background: #edf3ff;
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
# 4) Flow & Authentication
# =========================
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown('<div class="hero-wrap"><div style="font-size:3rem; font-weight:900;">אחים כהן • ניהול מחסן</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    if c1.button("🔑\nמנהל WMS", use_container_width=True): st.session_state.user_role = "מנהל WMS"; st.rerun()
    if c2.button("📦\nצוות מחסן", use_container_width=True): st.session_state.user_role = "צוות מחסן"; st.rerun()
    if c3.button("📊\nסמנכ\"ל", use_container_width=True): st.session_state.user_role = "סמנכ\"ל"; st.rerun()
    st.stop()

df = load_data()
OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# תיקון תפריט סמנכ"ל - עכשיו הוא רואה דשבורד
if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "סמנכ\"ל":
    menu = [OPT_DASH, OPT_CAL]
else: # צוות מחסן
    menu = [OPT_WORK, OPT_CAL]

choice = st.sidebar.radio("ניווט", menu)

if st.sidebar.button("🚪 התנתקות"):
    st.session_state.user_role = None
    st.rerun()

# --- דשבורד בקרה ---
if choice == OPT_DASH:
    st.markdown(f"## {OPT_DASH}")
    today_tasks = get_daily_status(df, datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t["is_done"])
    pct = int((done / total) * 100) if total > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("משימות היום", total)
    m2.metric("בוצעו", done)
    m3.metric("הספק", f"{pct}%")
    st.write("<br>", unsafe_allow_html=True)
    for t in today_tasks:
        st.info(f"{'✅' if t['is_done'] else '⏳'} {t['name']}")

# --- סידור עבודה ---
elif choice == OPT_WORK:
    st.markdown(f"## {OPT_WORK}")
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    cols = st.columns(5)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    for i, name in enumerate(days):
        curr_d = start + timedelta(days=i)
        d_str = curr_d.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="week-day-chip"><b>{name}</b><br>{curr_d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            for t in get_daily_status(df, curr_d):
                label = f"✅ {t['name']}" if t['is_done'] else f"⏳ {t['name']}"
                with st.popover(label, use_container_width=True):
                    st.subheader(t['name'])
                    st.write(f"**פירוט:**\n{t['desc'] if t['desc'] else 'אין פירוט'}")
                    if not t['is_done'] and st.button("סמן כבוצע", key=f"d_{t['id']}_{i}"):
                        df.at[t['idx'], "Done_Dates"] = f"{df.at[t['idx'], 'Done_Dates']},{d_str}".strip(",")
                        save_data(df)
                        st.rerun()

# --- הגדרות ---
elif choice == OPT_MANAGE:
    st.markdown(f"## {OPT_MANAGE}")
    for idx, row in df.iterrows():
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{row['Task_Name']}** | {row['Recurring']}")
        if c2.button("מחק 🗑️", key=f"del_{row['ID']}"):
            df = df.drop(idx)
            save_data(df)
            st.rerun()

# --- הוספה ולוח שנה ---
elif choice == OPT_ADD:
    with st.form("add"):
        name = st.text_input("שם משימה")
        desc = st.text_area("פירוט")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        sd = st.date_input("התחלה")
        if st.form_submit_button("שמור"):
            new = pd.DataFrame([{"ID": int(datetime.now().timestamp()), "Task_Name": name, "Description": desc, "Recurring": freq, "Date": sd.strftime("%Y-%m-%d"), "Done_Dates": ""}])
            df = pd.concat([df, new], ignore_index=True); save_data(df); st.rerun()

elif choice == OPT_CAL:
    events = []
    for _, row in df.iterrows():
        base = pd.to_datetime(row["Date"]).date()
        for i in range(30):
            d = base + timedelta(days=i)
            if is_scheduled_on(base, row["Recurring"], d):
                events.append({"title": row["Task_Name"], "start": d.strftime("%Y-%m-%d"), "color": "#10b981" if d.strftime("%Y-%m-%d") in str(row["Done_Dates"]) else "#ef4444"})
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 550})
