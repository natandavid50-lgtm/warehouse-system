import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os
import plotly.express as px

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

.stApp {
    background: linear-gradient(180deg, #f8fbff 0%, #f3f6fb 45%, #edf3fa 100%);
}

/* באנר כותרת דף */
.page-header-banner {
    background: white;
    padding: 25px;
    border-radius: 20px;
    border: 1px solid #dbe4f0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-bottom: 30px;
    text-align: center;
    color: #0f172a;
}

/* מטריקות דשבורד */
[data-testid="stMetric"] {
    background: white !important;
    padding: 20px !important;
    border-radius: 18px !important;
    border: 1px solid #dbe4f0 !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
}

/* עיצוב רשימת משימות מקצועית */
.task-row {
    background: white;
    padding: 12px 20px;
    border-radius: 12px;
    border-right: 5px solid #2563eb;
    margin-bottom: 10px;
    display: flex;
    justify-content: right;
    align-items: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    font-weight: 700;
}
.task-done {
    border-right: 5px solid #10b981;
    color: #94a3b8;
    text-decoration: line-through;
    font-weight: 400;
}

/* כפתורי כניסה בדף הבית */
div[data-testid="stHorizontalBlock"] .stButton > button {
    min-height: 200px !important;
    border-radius: 22px !important;
    font-size: 1.5rem !important;
    font-weight: 900 !important;
    background: white !important;
    border: 1px solid #dbe4f0 !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 8px solid #2563eb !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 8px solid #f59e0b !important; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 8px solid #10b981 !important; }

/* פופ-אובר למשימות */
div[data-testid="stPopover"] > button {
    width: 100% !important;
    min-height: 75px !important;
    margin-bottom: 12px !important;
    font-weight: 700 !important;
    border-radius: 15px !important;
    border: 1px solid #dbe4f0 !important;
}

.week-day-chip {
    background: #edf3ff;
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 15px;
    text-align: center;
    font-weight: 800;
}
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
    if c1.button("🔑\nמנהל WMS", use_container_width=True): st.session_state.user_role = "מנהל WMS"; st.rerun()
    if c2.button("📦\nצוות מחסן", use_container_width=True): st.session_state.user_role = "צוות מחסן"; st.rerun()
    if c3.button("📊\nסמנכ\"ל", use_container_width=True): st.session_state.user_role = "סמנכ\"ל"; st.rerun()
    st.stop()

df = load_data()
OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# תפריט צד
st.sidebar.markdown(f"### שלום, **{st.session_state.user_role}**")
if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "סמנכ\"ל":
    menu = [OPT_DASH, OPT_CAL]
else:
    menu = [OPT_WORK, OPT_CAL]

choice = st.sidebar.radio("תפריט", menu)
if st.sidebar.button("התנתקות"):
    st.session_state.user_role = None
    st.rerun()

# --- הצגת כותרת הדף בתוך הבאנר המעוצב ---
st.markdown(f'<div class="page-header-banner"><h1>{choice}</h1></div>', unsafe_allow_html=True)

# --- דשבורד בקרה ---
if choice == OPT_DASH:
    # 1. בורר תאריכים בראש הדף
    c_date, _ = st.columns([1, 3])
    selected_date = c_date.date_input("בחר תאריך לבדיקה:", datetime.now())
    
    # חישוב נתונים ליום הנבחר
    selected_tasks = get_daily_status(df, selected_date)
    total = len(selected_tasks)
    done = sum(1 for t in selected_tasks if t["is_done"])
    pct = int((done / total) * 100) if total > 0 else 0
    
    # חישוב דלתא (השוואה לאתמול)
    yesterday = selected_date - timedelta(days=1)
    y_tasks = get_daily_status(df, yesterday)
    y_total = len(y_tasks)
    y_pct = int((sum(1 for t in y_tasks if t["is_done"]) / y_total) * 100) if y_total > 0 else 0
    delta_val = pct - y_pct
    
    m1, m2, m3 = st.columns(3)
    date_label = "להיום" if selected_date == datetime.now().date() else f"ל- {selected_date.strftime('%d/%m')}"
    m1.metric(f"משימות {date_label}", total)
    m2.metric("בוצעו", done)
    m3.metric("אחוז ביצוע", f"{pct}%", delta=f"{delta_val}% מאתמול")
    
    # 2. גרף ביצועים שבועי (צבעוני ומקצועי)
    st.write("---")
    st.write("### מגמת ביצועים שבועית (רמזור)")
    weekly_data = []
    for i in range(6, -1, -1):
        day = datetime.now().date() - timedelta(days=i)
        tasks = get_daily_status(df, day)
        t_total = len(tasks)
        t_pct = int((sum(1 for t in tasks if t["is_done"]) / t_total) * 100) if t_total > 0 else 0
        
        # לוגיקת צבעים לפי ביצועים
        color = "#10b981" if t_pct > 90 else ("#f59e0b" if t_pct > 60 else "#ef4444")
        weekly_data.append({"תאריך": day.strftime("%d/%m"), "אחוז ביצוע": t_pct, "צבע": color})
    
    chart_df = pd.DataFrame(weekly_data)
    fig = px.bar(chart_df, x="תאריך", y="אחוז ביצוע", color="צבע", 
                 color_discrete_map={"#10b981": "#10b981", "#f59e0b": "#f59e0b", "#ef4444": "#ef4444"})
    fig.update_layout(showlegend=False, height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    st.write(f"### פירוט משימות {date_label}")
    if total > 0:
        for t in selected_tasks:
            status_class = "task-row task-done" if t['is_done'] else "task-row"
            icon = "✅" if t['is_done'] else "⏳"
            st.markdown(f'<div class="{status_class}"><span>{icon} {t["name"]}</span></div>', unsafe_allow_html=True)
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
    for idx, row in df.iterrows():
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{row['Task_Name']}**")
        c2.write(f"({row['Recurring']})")
        if c3.button("מחיקה 🗑️", key=f"del_{row['ID']}"):
            df = df.drop(idx)
            save_data(df)
            st.rerun()
        st.divider()

# --- הוספת משימה ---
elif choice == OPT_ADD:
    with st.form("add_form"):
        name = st.text_input("שם משימה")
        desc = st.text_area("פירוט נוסף")
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
        for i in range(30):
            d = base + timedelta(days=i)
            if is_scheduled_on(base, row["Recurring"], d):
                events.append({
                    "title": row["Task_Name"], 
                    "start": d.strftime("%Y-%m-%d"), 
                    "color": "#10b981" if d.strftime("%Y-%m-%d") in str(row["Done_Dates"]) else "#ef4444"
                })
    calendar(events=events, options={"direction": "rtl", "locale": "he"})
