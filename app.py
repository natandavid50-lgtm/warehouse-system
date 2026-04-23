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
ADMIN_PASSWORD = "1234" # תוכל לשנות את הסיסמה כאן

# =========================
# 2) Theme / CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;600;700;900&display=swap');

/* =========================================
    GLOBAL RESET & VARIABLES
   ========================================= */
:root {
    --bg-deep:        #050c1a;
    --bg-panel:       #0a1628;
    --bg-card:        #0d1f3c;
    --bg-card-hover:  #112347;
    --border:          rgba(56, 139, 253, 0.18);
    --border-bright:  rgba(56, 139, 253, 0.45);
    --accent-blue:    #388bfd;
    --accent-cyan:    #00d4ff;
    --accent-green:   #00e5a0;
    --accent-amber:   #f59e0b;
    --accent-red:      #ff4d6d;
    --text-primary:    #e8f0fe;
    --text-secondary: #8eafd4;
    --text-muted:      #4a6fa5;
    --glow-blue:      0 0 20px rgba(56, 139, 253, 0.35);
    --glow-cyan:      0 0 20px rgba(0, 212, 255, 0.3);
    --glow-green:     0 0 20px rgba(0, 229, 160, 0.3);
    --radius-card:    16px;
    --radius-pill:    50px;
}

html, body, [class*="css"] {
    font-family: "Heebo", sans-serif !important;
    direction: rtl;
    text-align: right;
}

/* =========================================
    BACKGROUND — deep space grid
   ========================================= */
.stApp {
    background-color: var(--bg-deep) !important;
    background-image:
        linear-gradient(rgba(56, 139, 253, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56, 139, 253, 0.04) 1px, transparent 1px),
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(56, 139, 253, 0.12) 0%, transparent 70%);
    background-size: 40px 40px, 40px 40px, 100% 100%;
}

/* =========================================
    SIDEBAR & USER INFO
   ========================================= */
[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-left: 1px solid var(--border) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
}

/* קופסת שם המשתמש בתפריט הצד */
.user-profile-box {
    padding: 1.2rem;
    margin: 10px 10px 25px 10px;
    background: linear-gradient(135deg, rgba(56, 139, 253, 0.1), rgba(0, 212, 255, 0.05));
    border: 1px solid var(--border-bright);
    border-radius: 12px;
    text-align: center;
    box-shadow: inset 0 0 15px rgba(56, 139, 253, 0.05);
}

.user-profile-box .label {
    display: block;
    font-size: 0.7rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
}

.user-profile-box .username {
    display: block;
    font-family: "Orbitron", sans-serif;
    color: var(--accent-cyan);
    font-weight: 700;
    font-size: 1.1rem;
    text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebarNav"] {
    padding-top: 0 !important;
}

[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 8px 12px;
    transition: all 0.2s ease;
    display: block;
    margin-bottom: 5px;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(56, 139, 253, 0.12) !important;
    border-color: var(--border-bright) !important;
}

/* =========================================
    PAGE HEADER BANNER
   ========================================= */
.page-header-banner {
    background: linear-gradient(135deg, var(--bg-card) 0%, #0b1e40 100%);
    padding: 28px 36px;
    border-radius: var(--radius-card);
    border: 1px solid var(--border-bright);
    box-shadow: var(--glow-blue), inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 28px;
    text-align: center;
    color: var(--text-primary);
    position: relative;
    overflow: hidden;
}

.page-header-banner h1 {
    font-family: "Orbitron", monospace !important;
    font-weight: 700 !important;
    font-size: 1.8rem !important;
    letter-spacing: 2px !important;
    color: var(--accent-cyan) !important;
    margin: 0 0 6px 0 !important;
    text-shadow: 0 0 30px rgba(0, 212, 255, 0.5) !important;
}

/* =========================================
    REMAINING STYLES (Metrics, Buttons, Forms)
   ========================================= */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    padding: 24px 20px !important;
    border-radius: var(--radius-card) !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04) !important;
}

[data-testid="stMetricValue"] {
    color: var(--accent-cyan) !important;
    font-family: "Orbitron", monospace !important;
    font-size: 2rem !important;
}

div[data-testid="stHorizontalBlock"] .stButton > button {
    min-height: 200px !important;
    border-radius: var(--radius-card) !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    background: var(--bg-card) !important;
}

div[data-testid="stPopover"] > button {
    width: 100% !important;
    min-height: 70px !important;
    margin-bottom: 10px !important;
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}

.week-day-chip {
    background: linear-gradient(135deg, var(--bg-card), #0b1e40);
    border: 1px solid var(--border-bright);
    border-radius: 12px;
    padding: 12px 10px;
    margin-bottom: 14px;
    text-align: center;
    color: var(--accent-cyan);
    font-family: "Orbitron", monospace;
}

/* Scrollbar and other minor UI resets */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }

</style>
""", unsafe_allow_html=True)

# =========================
# 3) Data Logic
# =========================
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE).fillna("")
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
    if isinstance(target_dt, datetime):
        target_date = target_dt.date()
    else:
        target_date = target_dt
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

# דף כניסה
if st.session_state.user_role is None:
    st.markdown('<div class="page-header-banner"><h1>אחים כהן • ניהול מחסן</h1><p>מערכת ניהול משימות ובקרה</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        with st.popover("🔑\nמנהל WMS", use_container_width=True):
            entered_pwd = st.text_input("הזן סיסמת ניהול", type="password")
            if st.button("אישור כניסה", use_container_width=True):
                if entered_pwd == ADMIN_PASSWORD:
                    st.session_state.user_role = "מנהל WMS"
                    st.rerun()
                else:
                    st.error("סיסמה שגויה")
                        
    if c2.button("📦\nצוות מחסן", use_container_width=True): st.session_state.user_role = "צוות מחסן"; st.rerun()
    if c3.button("📊\nסמנכ\"ל", use_container_width=True): st.session_state.user_role = "סמנכ\"ל"; st.rerun()
    st.stop()

df = load_data()
OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# תפריט צד - תצוגת משתמש מעוצבת
st.sidebar.markdown(
    f"""
    <div class="user-profile-box">
        <span class="label">Connected as</span>
        <span class="username">{st.session_state.user_role}</span>
    </div>
    """, 
    unsafe_allow_html=True
)

if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "סמנכ\"ל":
    menu = [OPT_DASH, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_WORK, OPT_CAL]

# מרווח בטיחות לפני תפריט הרדיו
st.sidebar.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
choice = st.sidebar.radio("ניווט במערכת", menu)

if st.sidebar.button("התנתקות"):
    st.session_state.user_role = None
    st.rerun()

# הצגת כותרת הדף
st.markdown(f'<div class="page-header-banner"><h1>{choice}</h1></div>', unsafe_allow_html=True)

# --- דשבורד בקרה ---
if choice == OPT_DASH:
    c_date, _ = st.columns([1, 3])
    selected_date = c_date.date_input("בחר תאריך לבדיקה:", datetime.now())
    
    selected_tasks = get_daily_status(df, selected_date)
    total = len(selected_tasks)
    done = sum(1 for t in selected_tasks if t["is_done"])
    pct = int((done / total) * 100) if total > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    date_label = "להיום" if selected_date == datetime.now().date() else f"ל- {selected_date.strftime('%d/%m')}"
    m1.metric(f"משימות {date_label}", total)
    m2.metric("בוצעו", done)
    m3.metric("אחוז ביצוע", f"{pct}%")
    
    st.write(f"### פירוט משימות {date_label}")
    if total > 0:
        for t in selected_tasks:
            st.info(f"{'✅' if t['is_done'] else '⏳'} {t['name']}")
    else:
        st.write("אין משימות מתוכננות לתאריך זה.")

# --- סידור עבודה ---
elif choice == OPT_WORK:
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)
    
    for i, name in enumerate(days):
        curr_d = start + timedelta(days=i)
        with cols[i]:
            st.markdown(f'<div class="week-day-chip">{name}<br>{curr_d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            for t in get_daily_status(df, curr_d):
                label = f"✅ {t['name']}" if t['is_done'] else f"⏳ {t['name']}"
                with st.popover(label, use_container_width=True):
                    st.write(f"**תיאור:** {t['desc']}")
                    if not t['is_done'] and st.button("סמן כבוצע", key=f"btn_{t['id']}_{i}"):
                        d_str = curr_d.strftime("%Y-%m-%d")
                        df.at[t['idx'], "Done_Dates"] = f"{df.at[t['idx'], 'Done_Dates']},{d_str}".strip(",")
                        save_data(df)
                        st.rerun()

# --- הגדרות ---
elif choice == OPT_MANAGE:
    st.markdown("### ⚙️ ניהול ועריכת משימות")
    if df.empty:
        st.info("אין משימות רשומות במערכת.")
    else:
        for idx, row in df.iterrows():
            st.markdown(f"""
            <div style="border: 1px solid var(--border); border-radius: 12px; padding: 15px; margin-bottom: 10px; background: var(--bg-card); border-right: 4px solid var(--accent-cyan);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--text-primary); font-weight: bold;">{row['Task_Name']}</span>
                    <span style="color: var(--accent-cyan); font-size: 0.85rem;">{row['Recurring']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            col1, col2, _ = st.columns([1.2, 1, 3])
            with col1:
                with st.popover("📝 עריכה", use_container_width=True):
                    new_name = st.text_input("שם", value=row['Task_Name'], key=f"edit_n_{row['ID']}")
                    if st.button("שמור", key=f"s_{row['ID']}"):
                        df.at[idx, 'Task_Name'] = new_name
                        save_data(df)
                        st.rerun()
            with col2:
                if st.button("🗑️ מחיקה", key=f"d_{row['ID']}", use_container_width=True):
                    df = df.drop(idx); save_data(df); st.rerun()

# --- הוספת משימה ---
elif choice == OPT_ADD:
    with st.form("add_form"):
        name = st.text_input("שם משימה")
        desc = st.text_area("פירוט")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        sd = st.date_input("תאריך התחלה")
        if st.form_submit_button("שמור משימה"):
            new = pd.DataFrame([{"ID": int(datetime.now().timestamp()), "Task_Name": name, "Description": desc, "Recurring": freq, "Date": sd.strftime("%Y-%m-%d"), "Done_Dates": ""}])
            df = pd.concat([df, new], ignore_index=True); save_data(df); st.rerun()

# --- לוח שנה ---
elif choice == OPT_CAL:
    events = []
    for _, row in df.iterrows():
        base = pd.to_datetime(row["Date"]).date()
        for i in range(120): # תצוגה ל-4 חודשים קדימה
            d = base + timedelta(days=i)
            if is_scheduled_on(base, row["Recurring"], d):
                is_done = d.strftime("%Y-%m-%d") in str(row["Done_Dates"])
                events.append({"title": row["Task_Name"], "start": d.strftime("%Y-%m-%d"), "color": "#00e5a0" if is_done else "#ff4d6d", "allDay": True})

    calendar(events=events, options={"direction": "rtl", "locale": "he", "initialView": "dayGridMonth"})
