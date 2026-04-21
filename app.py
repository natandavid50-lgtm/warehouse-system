import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
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
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: "Heebo", sans-serif !important;
    direction: rtl;
    text-align: right;
}

/* תיקון תצוגת מטריקות בדשבורד */
[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #dbe4f0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    text-align: center;
}

.hero-wrap {
    background: white;
    border: 1px solid #dbe4f0;
    border-radius: 24px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    padding: 30px;
    margin-bottom: 25px;
    text-align: center;
}

/* כפתורי כניסה בדף הבית */
div[data-testid="stHorizontalBlock"] .stButton > button {
    min-height: 200px !important;
    background: white !important;
    border: 1px solid #dbe4f0 !important;
    border-radius: 22px !important;
    font-weight: 900 !important;
    font-size: 1.5rem !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 8px solid #2563eb !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 8px solid #f59e0b !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 8px solid #10b981 !important; }

/* פופ-אובר למשימות */
div[data-testid="stPopover"] > button {
    width: 100% !important;
    min-height: 70px !important;
    margin-bottom: 10px !important;
    border-radius: 15px !important;
    font-weight: 700 !important;
    background: white !important;
    border: 1px solid #dbe4f0 !important;
}

.week-day-chip {
    background: #edf3ff;
    border-radius: 12px;
    text-align: center;
    padding: 10px;
    margin-bottom: 15px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3) Logic & Data
# =========================
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df.fillna("")
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
if "user_role" not in st.session_state: st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown('<div class="hero-wrap"><h1>אחים כהן • ניהול מחסן</h1></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("🔑\nמנהל WMS"): st.session_state.user_role = "מנהל WMS"; st.rerun()
    if c2.button("📦\nצוות מחסן"): st.session_state.user_role = "צוות מחסן"; st.rerun()
    if c3.button("📊\nסמנכ\"ל"): st.session_state.user_role = "סמנכ\"ל"; st.rerun()
    st.stop()

df = load_data()
OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"
menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE] if st.session_state.user_role == "מנהל WMS" else [OPT_WORK, OPT_CAL]
choice = st.sidebar.radio("ניווט", menu)

if st.sidebar.button("התנתקות"):
    st.session_state.user_role = None
    st.rerun()

# --- דשבורד (עם האחוזים שחזרו) ---
if choice == OPT_DASH:
    st.header(OPT_DASH)
    today_tasks = get_daily_status(df, datetime.now())
    total = len(today_tasks)
    done = sum(1 for t in today_tasks if t["is_done"])
    pct = int((done / total) * 100) if total > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("משימות להיום", total)
    m2.metric("בוצעו", done)
    m3.metric("אחוז ביצוע", f"{pct}%")

# --- סידור עבודה ---
elif choice == OPT_WORK:
    st.header(OPT_WORK)
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    cols = st.columns(5)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    
    for i, name in enumerate(days):
        curr_d = start + timedelta(days=i)
        with cols[i]:
            st.markdown(f'<div class="week-day-chip">{name}<br>{curr_d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            for t in get_daily_status(df, curr_d):
                label = f"✅ {t['name']}" if t['is_done'] else f"⏳ {t['name']}"
                with st.popover(label, use_container_width=True):
                    st.write(f"**פירוט:** {t['desc']}")
                    if not t['is_done'] and st.button("בצע", key=f"btn_{t['id']}_{i}"):
                        d_str = curr_d.strftime("%Y-%m-%d")
                        df.at[t['idx'], "Done_Dates"] = f"{df.at[t['idx'], 'Done_Dates']},{d_str}".strip(",")
                        save_data(df)
                        st.rerun()

# --- הגדרות (ניהול משימות עם כפתור מחיקה בודד) ---
elif choice == OPT_MANAGE:
    st.header("ניהול משימות קיימות")
    for idx, row in df.iterrows():
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{row['Task_Name']}** ({row['Recurring']})")
        if c3.button("מחק 🗑️", key=f"del_{row['ID']}"):
            df = df.drop(idx)
            save_data(df)
            st.rerun()
    st.divider()
    if st.button("מחק הכל (זהירות)"):
        save_data(pd.DataFrame(columns=df.columns))
        st.rerun()

# --- הוספה ולוח שנה (ללא שינוי) ---
elif choice == OPT_ADD:
    with st.form("add"):
        name = st.text_input("שם משימה")
        desc = st.text_area("תיאור")
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
    calendar(events=events, options={"direction": "rtl", "locale": "he"})
