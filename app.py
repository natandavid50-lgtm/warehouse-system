import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os
import plotly.express as px
import calendar as cal_lib
import io

# =========================
# 1) App Config
# =========================
st.set_page_config(
    page_title="אחים כהן | ניהול מחסן",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = "warehouse_management_db.csv"
INV_TARGET_FILE = "inventory_target.csv" # קובץ לשמירת יעדי הספירה
ADMIN_PASSWORD = "1234" 

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
    --glow-green:     0 0 209px rgba(0, 229, 160, 0.3);
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
    SIDEBAR FIX
   ========================================= */
[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-left: 1px solid var(--border) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
}

[data-testid="stSidebar"][aria-expanded="false"] div {
    display: none !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 8px 12px;
    transition: all 0.2s ease;
    display: block;
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
    METRICS
   ========================================= */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    padding: 24px 20px !important;
    border-radius: var(--radius-card) !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04) !important;
    transition: transform 0.2s ease !important;
}

[data-testid="stMetricValue"] {
    color: var(--accent-cyan) !important;
    font-family: "Orbitron", monospace !important;
}

/* =========================================
    HOME PAGE — BIG BUTTONS
   ========================================= */
div[data-testid="stHorizontalBlock"] .stButton > button,
div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {
    min-height: 220px !important;
    height: 220px !important;
    width: 100% !important;
    border-radius: var(--radius-card) !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
}

/* =========================================
    GENERAL BUTTONS & FORMS
   ========================================= */
.stButton > button {
    background: linear-gradient(135deg, rgba(56, 139, 253, 0.15), rgba(56, 139, 253, 0.05)) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--accent-cyan) !important;
    border-radius: 10px !important;
}

.week-day-chip {
    background: linear-gradient(135deg, var(--bg-card), #0b1e40);
    border: 1px solid var(--border-bright);
    border-radius: 12px;
    padding: 12px 10px;
    margin-bottom: 14px;
    text-align: center;
    color: var(--accent-cyan);
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

def load_inv_target():
    if os.path.exists(INV_TARGET_FILE):
        return pd.read_csv(INV_TARGET_FILE).iloc[0].to_dict()
    return {"Target": 0, "Current": 0}

def save_inv_target(target, current):
    pd.DataFrame([{"Target": target, "Current": current}]).to_csv(INV_TARGET_FILE, index=False)

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

def get_overdue_tasks(df_input):
    today = datetime.now().date()
    overdue = []
    for i in range(1, 8):
        check_date = today - timedelta(days=i)
        tasks = get_daily_status(df_input, check_date)
        for t in tasks:
            if not t["is_done"]:
                t["overdue_date"] = check_date.strftime("%d/%m")
                overdue.append(t)
    return overdue

# =========================
# 4) Main Flow
# =========================
if "user_role" not in st.session_state:
    st.session_state.user_role = None

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
    with c2:
        if st.button("📦\nצוות מחסן", use_container_width=True): 
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
    with c3:
        if st.button("📊\nהנהלה", use_container_width=True): 
            st.session_state.user_role = "הנהלה"
            st.rerun()
    st.stop()

df = load_data()
inv_data = load_inv_target()
OPT_DASH, OPT_WORK, OPT_INV, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📦 ספירות מלאי", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

st.sidebar.markdown(f"### שלום, **{st.session_state.user_role}**")
if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_INV, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "הנהלה":
    menu = [OPT_DASH, OPT_INV, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_WORK, OPT_INV, OPT_CAL]

choice = st.sidebar.radio("תפריט", menu)
if st.sidebar.button("התנתקות"):
    st.session_state.user_role = None
    st.rerun()

st.markdown(f'<div class="page-header-banner"><h1>{choice}</h1></div>', unsafe_allow_html=True)

if choice == OPT_DASH:
    overdue_list = get_overdue_tasks(df)
    if overdue_list:
        st.markdown(f"""<div style="background: rgba(255, 77, 109, 0.15); border: 1px solid var(--accent-red); border-radius: 12px; padding: 15px; margin-bottom: 20px;"><h4 style="color: var(--accent-red); margin: 0;">⚠️ שים לב: ישנן {len(overdue_list)} משימות בפיגור מהשבוע האחרון</h4></div>""", unsafe_allow_html=True)

    c_date, _ = st.columns([1, 3])
    selected_date = c_date.date_input("בחר תאריך לבדיקה:", datetime.now())
    selected_tasks = get_daily_status(df, selected_date)
    total, done = len(selected_tasks), sum(1 for t in selected_tasks if t["is_done"])
    pct = int((done / total) * 100) if total > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    date_label = "להיום" if selected_date == datetime.now().date() else f"ל- {selected_date.strftime('%d/%m')}"
    m1.metric(f"משימות {date_label}", total)
    m2.metric("בוצעו", done)
    m3.metric("אחוז ביצוע", f"{pct}%")
    
    st.write(f"### פירוט משימות {date_label}")
    if total > 0:
        for t in selected_tasks: st.info(f"{'✅' if t['is_done'] else '⏳'} {t['name']}")
    else: st.write("אין משימות מתוכננות לתאריך זה.")

    st.write("---")
    st.write("### 📈 מגמת ביצועים שבועית")
    weekly_data = []
    for i in range(6, -1, -1):
        day = datetime.now().date() - timedelta(days=i)
        tasks = get_daily_status(df, day)
        t_total, t_done = len(tasks), sum(1 for t in tasks if t["is_done"])
        weekly_data.append({"תאריך": day.strftime("%d/%m"), "אחוז": int((t_done / t_total) * 100) if t_total > 0 else 0})
    
    fig = px.area(pd.DataFrame(weekly_data), x="תאריך", y="אחוז", markers=True)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#8eafd4", height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    st.write("### 📅 ניתוח ביצועים חודשי (הנהלה)")
    month_col, year_col = st.columns(2)
    selected_month = month_col.selectbox("בחר חודש", range(1, 13), index=datetime.now().month - 1)
    selected_year = year_col.selectbox("בחר שנה", [2025, 2026], index=1)

    monthly_stats = []
    _, num_days = cal_lib.monthrange(selected_year, selected_month)
    for day in range(1, num_days + 1):
        check_date = datetime(selected_year, selected_month, day).date()
        tasks = get_daily_status(df, check_date)
        if tasks:
            t_total, t_done = len(tasks), sum(1 for t in tasks if t["is_done"])
            monthly_stats.append({"תאריך": check_date.strftime("%d/%m/%Y"), "יום": day, "בוצע": t_done, "מתוכנן": t_total, "אחוז": int((t_done / t_total) * 100)})

    if monthly_stats:
        df_monthly = pd.DataFrame(monthly_stats)
        col_m1, col_m2 = st.columns([3, 1])
        col_m1.metric("ממוצע ביצוע חודשי", f"{int(df_monthly['אחוז'].mean())}%")
        
        # תיקון שגיאת האקסל: שימוש במנוע ברירת מחדל
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_monthly.to_excel(writer, index=False, sheet_name='Monthly_Report')
            excel_data = output.getvalue()
            col_m2.download_button(label="📥 הורד דוח ל-Excel", data=excel_data, file_name=f"report_{selected_month}_{selected_year}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except:
            st.error("שגיאה ביצירת קובץ אקסל - וודא שספריית openpyxl מותקנת")
        
        fig_month = px.bar(df_monthly, x="יום", y=["מתוכנן", "בוצע"], barmode="group", color_discrete_map={"מתוכנן": "#112347", "בוצע": "#00e5a0"})
        fig_month.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#8eafd4")
        st.plotly_chart(fig_month, use_container_width=True)
    else: st.warning("אין נתוני משימות לחודש הנבחר.")

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
                        save_data(df); st.rerun()

elif choice == OPT_INV:
    st.markdown("### 📦 סטטוס ספירת מלאי")
    if st.session_state.user_role == "מנהל WMS":
        with st.form("inv_management"):
            c1, c2 = st.columns(2)
            new_target = c1.number_input("סה\"כ איתורים:", min_value=0, value=int(inv_data['Target']))
            new_current = c2.number_input("נספרו:", min_value=0, value=int(inv_data['Current']))
            if st.form_submit_button("עדכן נתונים"): save_inv_target(new_target, new_current); st.rerun()
    
    target, current = inv_data['Target'], inv_data['Current']
    if target > 0:
        pct_inv = min(100, int((current / target) * 100))
        fig = px.pie(values=[current, max(0, target-current)], names=["בוצע", "נותר"], hole=0.7, color_discrete_sequence=["#00e5a0", "#112347"])
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', annotations=[dict(text=f"{pct_inv}%", x=0.5, y=0.5, font_size=40, font_family="Orbitron", font_color="#00d4ff", showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("טרם הוגדרו יעדי ספירה.")

elif choice == OPT_MANAGE:
    st.markdown("### ⚙️ ניהול ועריכת משימות")
    for idx, row in df.iterrows():
        st.markdown(f"""<div style="border: 1px solid var(--border); border-radius: 12px; padding: 15px; margin-bottom: 10px; background: var(--bg-card); border-right: 4px solid var(--accent-cyan);"><div style="display: flex; justify-content: space-between;"><b>{row['Task_Name']}</b><span>{row['Recurring']}</span></div></div>""", unsafe_allow_html=True)
        col1, col2, _ = st.columns([1.2, 1, 3])
        with col1:
            with st.popover("📝 עריכה", use_container_width=True):
                n_n = st.text_input("שם", value=row['Task_Name'], key=f"e_n_{row['ID']}")
                n_d = st.text_area("תיאור", value=row['Description'], key=f"e_d_{row['ID']}")
                if st.button("שמור", key=f"s_{row['ID']}"):
                    df.at[idx, 'Task_Name'], df.at[idx, 'Description'] = n_n, n_d
                    save_data(df); st.rerun()
        with col2:
            if st.button("🗑️ מחיקה", key=f"d_{row['ID']}"): df = df.drop(idx); save_data(df); st.rerun()

elif choice == OPT_ADD:
    with st.form("add_form"):
        name, desc = st.text_input("שם משימה"), st.text_area("פירוט נוסף")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        sd = st.date_input("תאריך התחלה")
        if st.form_submit_button("שמור משימה"):
            new = pd.DataFrame([{"ID": int(datetime.now().timestamp()), "Task_Name": name, "Description": desc, "Recurring": freq, "Date": sd.strftime("%Y-%m-%d"), "Done_Dates": ""}])
            df = pd.concat([df, new], ignore_index=True); save_data(df); st.rerun()

elif choice == OPT_CAL:
    events = []
    for _, row in df.iterrows():
        base = pd.to_datetime(row["Date"]).date()
        for i in range(500):
            d = base + timedelta(days=i)
            if is_scheduled_on(base, row["Recurring"], d):
                is_done = d.strftime("%Y-%m-%d") in str(row["Done_Dates"])
                events.append({"title": row["Task_Name"], "start": d.strftime("%Y-%m-%d"), "color": "#00e5a0" if is_done else "#ff4d6d", "allDay": True})
    calendar(events=events, options={"direction": "rtl", "locale": "he", "initialView": "dayGridMonth"}, custom_css=".fc { background: #0d1f3c; color: #e8f0fe; border-radius: 16px; }")
