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
# 2) Theme / CSS (Light & Professional UI)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800;900&display=swap');

/* הגדרות כלליות למראה בהיר */
:root {
    --bg-main: #f8fafc;
    --card-white: #ffffff;
    --text-dark: #1e293b;
    --text-muted: #64748b;
    --accent-blue: #2563eb;
    --border-color: #e2e8f0;
}

html, body, [class*="css"] { 
    font-family: "Heebo", sans-serif !important; 
    direction: rtl; 
    text-align: right; 
}

/* רקע האפליקציה */
.stApp { 
    background-color: var(--bg-main); 
    color: var(--text-dark); 
}

/* כותרת ראשית */
.hero-title {
    text-align: center; 
    font-size: 3.2rem !important; 
    font-weight: 900;
    color: #0f172a;
    margin-bottom: 0.5rem;
    padding-top: 20px;
}

/* עיצוב כפתורי הכניסה כמלבנים לבנים גדולים */
.stButton>button {
    height: 200px;
    border-radius: 20px;
    background-color: var(--card-white) !important;
    border: 2px solid var(--border-color) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
    color: var(--text-dark) !important;
}
.stButton>button:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.1);
    border-color: var(--accent-blue) !important;
}
.stButton>button div p {
    font-size: 28px !important;
    font-weight: 800 !important;
}

/* צבעי סטטוס בכפתורים */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 10px solid #2563eb !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 10px solid #f59e0b !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 10px solid #10b981 !important; }

/* עיצוב כרטיסיות משימות בדשבורד */
.dashboard-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 15px;
}

.task-item {
    background: white;
    padding: 15px;
    border-radius: 10px;
    border-right: 5px solid #cbd5e1;
    margin-bottom: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.task-done { border-right-color: #10b981; background-color: #f0fdf4; }
.task-pending { border-right-color: #f59e0b; background-color: #fffbeb; }

/* מטריקות (מספרים למעלה) */
[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid var(--border-color);
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

# =========================
# 4) Utilities
# =========================
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
# 5) Main Logic
# =========================
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# --- Welcome Screen ---
if st.session_state.user_role is None:
    st.markdown('<div class="hero-title">אחים כהן • ניהול מחסן</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-size:1.3rem; color:#64748b;">מערכת ניהול משימות ובקרה</p>', unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3, gap="medium")
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

df = load_data()
st.sidebar.markdown(f"### שלום, **{st.session_state.user_role}**")
if st.sidebar.button("🚪 התנתקות"):
    st.session_state.user_role = None
    st.rerun()

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"
if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
else: menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("ניווט", menu)

# --- Pages ---
if choice == OPT_DASH:
    st.markdown(f"## {OPT_DASH}")
    today_tasks = get_daily_status(df, datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t["is_done"])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות פתוחות היום", total)
    c2.metric("בוצעו בפועל", done)
    c3.metric("אחוז עמידה ביעדים", f"{int(done/total*100) if total > 0 else 0}%")
    
    st.write("<br>", unsafe_allow_html=True)
    st.subheader("סטטוס משימות נוכחי")
    
    if not today_tasks:
        st.info("אין משימות מתוזמנות להיום.")
    else:
        for t in today_tasks:
            status_class = "task-done" if t["is_done"] else "task-pending"
            icon = "✅" if t["is_done"] else "⏳"
            st.markdown(f"""
            <div class="task-item {status_class}">
                <b style="font-size:1.2rem;">{icon} {t['name']}</b><br>
                <span style="color:var(--text-muted);">{t['desc'] if t['desc'] else 'אין תיאור למשימה'}</span>
            </div>
            """, unsafe_allow_html=True)

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
            st.markdown(f"""
            <div style="background:#e2e8f0; padding:10px; border-radius:10px; text-align:center; margin-bottom:10px;">
                <b>{day_name}</b><br>{curr_day.strftime('%d/%m')}
            </div>
            """, unsafe_allow_html=True)
            tasks = get_daily_status(df, curr_day)
            for t in tasks:
                if t["is_done"]:
                    st.success(f"**{t['name']}**")
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
            for i in range(90):
                d = base + timedelta(days=i)
                if is_scheduled_on(base, row["Recurring"], d):
                    d_str = d.strftime("%Y-%m-%d")
                    events.append({
                        "title": row["Task_Name"], "start": d_str,
                        "color": "#10b981" if d_str in str(row["Done_Dates"]) else "#ef4444"
                    })
        except: continue
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})

elif choice == OPT_ADD:
    st.markdown(f"## {OPT_ADD}")
    with st.form("add_form"):
        name = st.text_input("שם המשימה (למשל: ספירת גבינות)")
        desc = st.text_area("הוראות לביצוע")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        start_d = st.date_input("תאריך התחלה", value=datetime.now().date())
        if st.form_submit_button("הוסף למערכת"):
            if name:
                new_id = int(datetime.now().timestamp())
                new_row = pd.DataFrame([{"ID": new_id, "Task_Name": name, "Description": desc, "Recurring": freq, "Date": start_d.strftime("%Y-%m-%d"), "Done_Dates": ""}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("המשימה נוספה בהצלחה!")
                st.rerun()

elif choice == OPT_MANAGE:
    st.markdown(f"## {OPT_MANAGE}")
    st.write("ניהול ומחיקת משימות קיימות:")
    st.dataframe(df[["Task_Name", "Recurring", "Date"]], use_container_width=True)
    if not df.empty:
        to_del = st.selectbox("בחר משימה למחיקה:", df["Task_Name"].unique())
        if st.button("מחק משימה זו"):
            df = df[df["Task_Name"] != to_del]
            save_data(df)
            st.rerun()
