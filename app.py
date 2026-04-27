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
INV_FILE = "inventory_counts_db.csv" # קובץ חדש לספירות
ADMIN_PASSWORD = "1234" 

# =========================
# 2) Theme / CSS (נשמר בדיוק כפי ששלחת)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;600;700;900&display=swap');

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

.stApp {
    background-color: var(--bg-deep) !important;
    background-image:
        linear-gradient(rgba(56, 139, 253, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56, 139, 253, 0.04) 1px, transparent 1px),
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(56, 139, 253, 0.12) 0%, transparent 70%);
    background-size: 40px 40px, 40px 40px, 100% 100%;
}

[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-left: 1px solid var(--border) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
}

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
    color: var(--accent-cyan) !important;
    text-shadow: 0 0 30px rgba(0, 212, 255, 0.5) !important;
}

[data-testid="stMetricValue"] {
    color: var(--accent-cyan) !important;
    font-family: "Orbitron", monospace !important;
}

div[data-testid="stHorizontalBlock"] .stButton > button,
div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {
    min-height: 220px !important;
    height: 220px !important;
    width: 100% !important;
    border-radius: var(--radius-card) !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
}

.week-day-chip {
    background: linear-gradient(135deg, var(--bg-card), #0b1e40);
    border: 1px solid var(--border-bright);
    border-radius: 12px;
    padding: 12px 10px;
    margin-bottom: 14px;
    text-align: center;
    font-weight: 800;
    color: var(--accent-cyan);
    font-family: "Orbitron", monospace;
    box-shadow: var(--glow-blue);
}

.stButton > button {
    background: linear-gradient(135deg, rgba(56, 139, 253, 0.15), rgba(56, 139, 253, 0.05)) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--accent-cyan) !important;
    border-radius: 10px !important;
}

div[data-testid="stPopover"] > button {
    width: 100% !important;
    min-height: 70px;
    margin-bottom: 10px !important;
    background: var(--bg-card) !important;
    text-align: right !important;
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

def load_inv_data():
    if os.path.exists(INV_FILE):
        df = pd.read_csv(INV_FILE).fillna("")
        if "Is_Done" not in df.columns: df["Is_Done"] = False
        return df
    return pd.DataFrame(columns=["ID", "Location", "Expected_Qty", "Actual_Qty", "Date", "Is_Done"])

def save_inv_data(df):
    df.to_csv(INV_FILE, index=False)

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
    target_date = target_dt.date() if isinstance(target_dt, datetime) else target_dt
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

if st.session_state.user_role is None:
    st.markdown('<div class="page-header-banner"><h1>אחים כהן • ניהול מחסן</h1><p>מערכת ניהול משימות ובקרה</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.popover("🔑\nמנהל WMS", use_container_width=True):
            entered_pwd = st.text_input("הזן סיסמת ניהול", type="password")
            if st.button("אישור כניסה", use_container_width=True):
                if entered_pwd == ADMIN_PASSWORD:
                    st.session_state.user_role = "מנהל WMS"; st.rerun()
                else: st.error("סיסמה שגויה")
    with c2:
        if st.button("📦\nצוות מחסן", use_container_width=True): 
            st.session_state.user_role = "צוות מחסן"; st.rerun()
    with c3:
        if st.button("📊\nהנהלה", use_container_width=True): 
            st.session_state.user_role = "הנהלה"; st.rerun()
    st.stop()

df = load_data()
df_inv = load_inv_data()

OPT_DASH, OPT_WORK, OPT_INV, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📦 ספירות מלאי", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_INV, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "הנהלה":
    menu = [OPT_DASH, OPT_INV, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_WORK, OPT_INV, OPT_CAL]

choice = st.sidebar.radio("תפריט", menu)
if st.sidebar.button("התנתקות"):
    st.session_state.user_role = None; st.rerun()

st.markdown(f'<div class="page-header-banner"><h1>{choice}</h1></div>', unsafe_allow_html=True)

# --- דשבורד בקרה --- (ללא שינוי מהמקור שלך)
if choice == OPT_DASH:
    c_date, _ = st.columns([1, 3])
    selected_date = c_date.date_input("בחר תאריך לבדיקה:", datetime.now())
    selected_tasks = get_daily_status(df, selected_date)
    total, done = len(selected_tasks), sum(1 for t in selected_tasks if t["is_done"])
    pct = int((done / total) * 100) if total > 0 else 0
    m1, m2, m3 = st.columns(3)
    m1.metric("משימות להיום", total)
    m2.metric("בוצעו", done)
    m3.metric("אחוז ביצוע", f"{pct}%")
    st.write("### פירוט משימות")
    for t in selected_tasks: st.info(f"{'✅' if t['is_done'] else '⏳'} {t['name']}")
    
    st.write("---")
    st.write("### 📈 מגמת ביצועים שבועית")
    weekly_data = []
    for i in range(6, -1, -1):
        day = datetime.now().date() - timedelta(days=i)
        tasks = get_daily_status(df, day)
        t_total = len(tasks)
        t_done = sum(1 for t in tasks if t["is_done"])
        weekly_data.append({"תאריך": day.strftime("%d/%m"), "אחוז": int((t_done / t_total) * 100) if t_total > 0 else 0})
    fig = px.area(pd.DataFrame(weekly_data), x="תאריך", y="אחוז", markers=True)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#8eafd4", height=300)
    st.plotly_chart(fig, use_container_width=True)

# --- סידור עבודה --- (ללא שינוי מהמקור שלך)
elif choice == OPT_WORK:
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)
    for i, name in enumerate(days_names):
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

# --- ספירות מלאי --- (תצוגה בלבד)
elif choice == OPT_INV:
    if df_inv.empty:
        st.info("אין נתוני ספירה להצגה.")
    else:
        st.write("### 📊 התקדמות ספירה כללית")
        total_l = len(df_inv)
        done_l = len(df_inv[df_inv["Is_Done"] == True])
        fig = px.pie(values=[done_l, total_l - done_l], names=['בוצע', 'נותר'], hole=0.7, color_discrete_sequence=["#00e5a0", "#112347"])
        fig.add_annotation(text=f"{done_l}/{total_l}", x=0.5, y=0.5, font_size=40, font_color="white", showarrow=False)
        fig.update_layout(showlegend=False, height=300, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        st.write("### 📍 סטטוס איתורים")
        for _, row in df_inv.iterrows():
            st.markdown(f"""
            <div style="background: var(--bg-card); padding: 15px; border-radius: 10px; border: 1px solid var(--border); margin-bottom: 10px; display: flex; justify-content: space-between;">
                <span><strong>איתור:</strong> {row['Location']}</span>
                <span><strong>נספר:</strong> {int(row['Actual_Qty'])} / {int(row['Expected_Qty'])}</span>
                <span>{'✅' if row['Is_Done'] else '⏳'}</span>
            </div>
            """, unsafe_allow_html=True)

# --- הגדרות --- (ניהול משימות + ניהול ספירה)
elif choice == OPT_MANAGE:
    tab1, tab2 = st.tabs(["📋 משימות", "📦 ניהול ספירה"])
    
    with tab1:
        # כאן נמצא כל הקוד המקורי שלך מעריכת משימות
        for idx, row in df.iterrows():
            with st.expander(f"ערוך: {row['Task_Name']}"):
                n_name = st.text_input("שם", row['Task_Name'], key=f"e_n_{idx}")
                n_freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"], index=["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"].index(row['Recurring']), key=f"e_f_{idx}")
                if st.button("שמור", key=f"s_v_{idx}"):
                    df.at[idx, 'Task_Name'] = n_name; df.at[idx, 'Recurring'] = n_freq; save_data(df); st.rerun()
                if st.button("מחק", key=f"d_l_{idx}"):
                    df = df.drop(idx); save_data(df); st.rerun()

    with tab2:
        st.write("### הוספת איתור לספירה")
        with st.form("inv_form"):
            c1, c2 = st.columns(2)
            l_name = c1.text_input("שם איתור (למשל A-01-01)")
            l_exp = c2.number_input("כמות מצופה", min_value=0)
            if st.form_submit_button("הוסף"):
                new_l = pd.DataFrame([{"ID": int(datetime.now().timestamp()), "Location": l_name, "Expected_Qty": l_exp, "Actual_Qty": 0, "Date": datetime.now().strftime("%Y-%m-%d"), "Is_Done": False}])
                df_inv = pd.concat([df_inv, new_l], ignore_index=True); save_inv_data(df_inv); st.rerun()
        
        st.write("---")
        st.write("### ביצוע ספירה בפועל")
        for idx, row in df_inv.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.write(f"📍 {row['Location']}")
                a_qty = c2.number_input("כמות", value=int(row['Actual_Qty']), key=f"inv_a_{idx}")
                is_d = c3.checkbox("בוצע", value=row['Is_Done'], key=f"inv_c_{idx}")
                if c4.button("💾", key=f"inv_s_{idx}"):
                    df_inv.at[idx, "Actual_Qty"] = a_qty; df_inv.at[idx, "Is_Done"] = is_d
                    save_inv_data(df_inv); st.rerun()
                if c4.button("🗑️", key=f"inv_d_{idx}"):
                    df_inv = df_inv.drop(idx); save_inv_data(df_inv); st.rerun()

# --- הוספת משימה --- (ללא שינוי מהמקור שלך)
elif choice == OPT_ADD:
    with st.form("add_form"):
        name = st.text_input("שם משימה")
        desc = st.text_area("פירוט נוסף")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        sd = st.date_input("תאריך התחלה")
        if st.form_submit_button("שמור משימה"):
            new = pd.DataFrame([{"ID": int(datetime.now().timestamp()), "Task_Name": name, "Description": desc, "Recurring": freq, "Date": sd.strftime("%Y-%m-%d"), "Done_Dates": ""}])
            df = pd.concat([df, new], ignore_index=True); save_data(df); st.rerun()

# --- לוח שנה --- (ללא שינוי מהמקור שלך)
elif choice == OPT_CAL:
    events = []
    for _, row in df.iterrows():
        base = pd.to_datetime(row["Date"]).date()
        for i in range(365):
            d = base + timedelta(days=i)
            if is_scheduled_on(base, row["Recurring"], d):
                done = d.strftime("%Y-%m-%d") in str(row["Done_Dates"])
                events.append({"title": row["Task_Name"], "start": d.strftime("%Y-%m-%d"), "color": "#00e5a0" if done else "#ff4d6d", "allDay": True})
    calendar(events=events, options={"direction": "rtl", "locale": "he", "initialView": "dayGridMonth"})
