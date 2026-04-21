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
# 2) Theme / CSS (Modern Dark UI + Large Color Cards)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800;900&display=swap');

:root {
    --bg: #0b1220;
    --text: #e6edf9;
    --muted: #9fb0d0;
    --accent: #59a5ff;
}

html, body, [class*="css"] { font-family: "Heebo", sans-serif !important; direction: rtl; text-align: right; }

.stApp { background: #0a1120; color: var(--text); }

/* עיצוב כפתורי הכניסה כמלבנים גדולים וצבעוניים */
.stButton>button {
    height: 220px;
    border-radius: 25px;
    background-color: #141f36 !important;
    border: 1px solid rgba(151, 174, 225, 0.18) !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    transition: all 0.4s ease;
}
.stButton>button:hover {
    transform: translateY(-12px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    border-color: var(--accent) !important;
}
.stButton>button div p {
    font-size: 32px !important;
    font-weight: 900 !important;
}

/* צבעים ייחודיים לפי עמודות */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 12px solid #1E3A8A !important; color: #59a5ff !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 12px solid #F59E0B !important; color: #fbbf24 !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 12px solid #10B981 !important; color: #2dd4bf !important; }

.hero-title {
    text-align: center; font-size: 3.5rem !important; font-weight: 900;
    background: linear-gradient(90deg, #dfeaff 0%, #9ac8ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3) Data Layer (Local CSV)
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

# =========================
# 4) Utilities
# =========================
def is_scheduled_on(base_date, recurring, target_date):
    if target_date < base_date: return False
    diff = (target_date - base_date).days
    if recurring == "לא": return diff == 0
    if recurring == "יומי": return diff < 200
    if recurring == "שבועי": return diff % 7 == 0
    if recurring == "דו-שבועי": return diff % 14 == 0
    if recurring == "חודשי": return target_date.day == base_date.day or (target_date.day >= 28 and pycal.monthrange(target_date.year, target_date.month)[1] == target_date.day)
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
# 5) App Logic
# =========================
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# --- מסך כניסה (אחים כהן המקורי) ---
if st.session_state.user_role is None:
    st.markdown('<div class="hero-title">מערכת המחסן - אחים כהן</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-size:1.5rem; color:#9fb0d0;">בחר תפקיד לכניסה מהירה</p>', unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        if st.button("🔑\nמנהל WMS", use_container_width=True):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
    with c2:
        if st.button("📦\nצוות מחסן", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
    with c3:
        if st.button("📊\nסמנכ\"ל", use_container_width=True):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
    st.stop()

# --- טעינת נתונים ותפריט צד ---
df = load_data()
st.sidebar.title(f"שלום, {st.session_state.user_role}")
if st.sidebar.button("🚪 התנתקות"):
    st.session_state.user_role = None
    st.rerun()

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"
if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
else: menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("ניווט", menu)

# --- דפים ---
if choice == OPT_DASH:
    st.title(OPT_DASH)
    today_tasks = get_daily_status(df, datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t["is_done"])
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות להיום", total)
    c2.metric("בוצעו", done)
    c3.metric("אחוז ביצוע", f"{int(done/total*100) if total > 0 else 0}%")
    st.divider()
    for t in today_tasks:
        st.write(f"{'✅' if t['is_done'] else '⏳'} **{t['name']}** - {t['desc']}")

elif choice == OPT_WORK:
    st.title(OPT_WORK)
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    cols = st.columns(5)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    for i, day_name in enumerate(days_names):
        curr_day = start_of_week + timedelta(days=i)
        date_str = curr_day.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"### {day_name}\n*{curr_day.strftime('%d/%m')}*")
            tasks = get_daily_status(df, curr_day)
            for t in tasks:
                if t["is_done"]: st.success(f"**{t['name']}**")
                else:
                    if st.button(f"בצע: {t['name']}", key=f"btn_{t['id']}_{date_str}"):
                        idx = t['idx']
                        old = str(df.at[idx, "Done_Dates"])
                        df.at[idx, "Done_Dates"] = f"{old},{date_str}".strip(",")
                        save_data(df)
                        st.rerun()

elif choice == OPT_CAL:
    st.title(OPT_CAL)
    events = []
    for _, row in df.iterrows():
        try:
            base = pd.to_datetime(row["Date"]).date()
            for i in range(60): # הצגת חודשיים קדימה
                d = base + timedelta(days=i)
                if is_scheduled_on(base, row["Recurring"], d):
                    d_str = d.strftime("%Y-%m-%d")
                    events.append({
                        "title": row["Task_Name"], "start": d_str,
                        "color": "#2dd4bf" if d_str in str(row["Done_Dates"]) else "#f87171"
                    })
        except: continue
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})

elif choice == OPT_ADD:
    st.title(OPT_ADD)
    with st.form("add_form"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        start_d = st.date_input("תאריך התחלה", value=datetime.now().date())
        if st.form_submit_button("שמור משימה"):
            if name:
                new_id = int(datetime.now().timestamp())
                new_row = pd.DataFrame([{"ID": new_id, "Task_Name": name, "Description": desc, "Recurring": freq, "Date": start_d.strftime("%Y-%m-%d"), "Done_Dates": ""}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("נשמר בהצלחה!")
                st.rerun()

elif choice == OPT_MANAGE:
    st.title(OPT_MANAGE)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        to_del = st.selectbox("מחיקת משימה:", df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            df = df[df["Task_Name"] != to_del]
            save_data(df)
            st.rerun()
