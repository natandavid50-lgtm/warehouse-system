import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os
import plotly.express as px
import calendar as cal_lib

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
    SIDEBAR FIX - תיקון לבעיית הטקסט בסגירה
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

.page-header-banner::before {
    content: '';
    position: absolute;
    top: -60px; left: 50%;
    transform: translateX(-50%);
    width: 300px; height: 120px;
    background: radial-gradient(ellipse, rgba(56, 139, 253, 0.25) 0%, transparent 70%);
    pointer-events: none;
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

.page-header-banner p {
    color: var(--text-secondary) !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
    letter-spacing: 1px;
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
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: var(--glow-blue), 0 8px 32px rgba(0,0,0,0.4) !important;
    border-color: var(--border-bright) !important;
}

[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px;
}

[data-testid="stMetricValue"] {
    color: var(--accent-cyan) !important;
    font-family: "Orbitron", monospace !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

/* =========================================
    HOME PAGE — BIG BUTTONS (FIXED SIZES)
   ========================================= */
div[data-testid="stHorizontalBlock"] .stButton > button,
div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {
    min-height: 220px !important;
    height: 220px !important;
    width: 100% !important;
    border-radius: var(--radius-card) !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    white-space: pre-wrap !important;
}

div[data-testid="stHorizontalBlock"] .stButton > button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
    border-top: 4px solid var(--accent-blue) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
    border-top: 4px solid var(--accent-amber) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
    border-top: 4px solid var(--accent-green) !important;
}

/* =========================================
    GENERAL BUTTONS
   ========================================= */
.stButton > button {
    background: linear-gradient(135deg, rgba(56, 139, 253, 0.15), rgba(56, 139, 253, 0.05)) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--accent-cyan) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

/* =========================================
    POPOVER (TASK CARDS)
   ========================================= */
div[data-testid="stPopover"] > button {
    width: 100% !important;
    min-height: 70px;
    margin-bottom: 10px !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    text-align: right !important;
}

/* =========================================
    WEEK DAY CHIP
   ========================================= */
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
    font-size: 0.85rem;
    box-shadow: var(--glow-blue);
}

/* =========================================
    FORM ELEMENTS
   ========================================= */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

/* =========================================
    SCROLLBAR
   ========================================= */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-panel); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }

/* =========================================
    FORM SUBMIT BUTTON
   ========================================= */
[data-testid="stForm"] .stButton > button {
    background: linear-gradient(135deg, var(--accent-blue), #1a6fd4) !important;
    color: #fff !important;
    border: none !important;
    padding: 12px 28px !important;
}

[data-testid="stForm"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-card) !important;
    padding: 24px !important;
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

# פונקציה לחישוב פיגורי משימות
def get_overdue_tasks(df_input):
    today = datetime.now().date()
    overdue = []
    for i in range(1, 8):
        check_date = today - timedelta(days=i)
        tasks = get_daily_status(df_input, check_date)
        for t in tasks:
            if not t["is_done"]:
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

# --- דשבורד בקרה ---
if choice == OPT_DASH:
    # הצגת התראת פיגורים
    overdue_list = get_overdue_tasks(df)
    if len(overdue_list) > 0:
        st.markdown(f"""
            <div style="background: rgba(255, 77, 109, 0.15); border: 1px solid var(--accent-red); border-radius: 12px; padding: 15px; margin-bottom: 20px; text-align: center;">
                <h4 style="color: var(--accent-red); margin: 0;">⚠️ שים לב: ישנן {len(overdue_list)} משימות שלא בוצעו מהשבוע האחרון</h4>
            </div>
        """, unsafe_allow_html=True)

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

    st.write("---")
    st.write("### 📈 מגמת ביצועים שבועית")
    weekly_data = []
    for i in range(6, -1, -1):
        day = datetime.now().date() - timedelta(days=i)
        tasks = get_daily_status(df, day)
        t_total = len(tasks)
        t_done = sum(1 for t in tasks if t["is_done"])
        t_pct = int((t_done / t_total) * 100) if t_total > 0 else 0
        weekly_data.append({"תאריך": day.strftime("%d/%m"), "אחוז": t_pct})
    
    fig = px.area(pd.DataFrame(weekly_data), x="תאריך", y="אחוז", markers=True)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#8eafd4", height=300)
    st.plotly_chart(fig, use_container_width=True)

    # --- תוספת: דוח חודשי למנהלים (חדש!) ---
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
            t_total = len(tasks)
            t_done = sum(1 for t in tasks if t["is_done"])
            monthly_stats.append({"יום": day, "בוצע": t_done, "מתוכנן": t_total, "אחוז": int((t_done / t_total) * 100)})

    if monthly_stats:
        df_monthly = pd.DataFrame(monthly_stats)
        avg_pct = int(df_monthly["אחוז"].mean())
        st.metric("ממוצע ביצוע חודשי", f"{avg_pct}%")
        
        fig_month = px.bar(df_monthly, x="יום", y=["מתוכנן", "בוצע"], 
                           title=f"פירוט ביצועים יומי - {selected_month}/{selected_year}",
                           barmode="group",
                           color_discrete_map={"מתוכנן": "#112347", "בוצע": "#00e5a0"})
        fig_month.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#8eafd4")
        st.plotly_chart(fig_month, use_container_width=True)
    else:
        st.warning("אין נתוני משימות לחודש הנבחר.")

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
                        save_data(df); st.rerun()

# --- ספירות מלאי ---
elif choice == OPT_INV:
    st.markdown("### 📦 סטטוס ספירת מלאי")
    if st.session_state.user_role == "מנהל WMS":
        with st.form("inv_management"):
            st.write("#### 🛠️ ניהול יעדי ספירה (רק אתה רואה)")
            c1, c2 = st.columns(2)
            new_target = c1.number_input("כמה איתורים יש לספור סה\"כ?", min_value=0, value=int(inv_data['Target']))
            new_current = c2.number_input("כמה איתורים נספרו עד כה?", min_value=0, value=int(inv_data['Current']))
            if st.form_submit_button("עדכן נתונים"):
                save_inv_target(new_target, new_current)
                st.rerun()
    
    st.write("---")
    target, current = inv_data['Target'], inv_data['Current']
    if target > 0:
        pct_inv = min(100, int((current / target) * 100))
        fig = px.pie(values=[current, max(0, target-current)], names=["בוצע", "נותר"], hole=0.7, color_discrete_sequence=["#00e5a0", "#112347"])
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(t=0, b=0, l=0, r=0),
                          annotations=[dict(text=f"{pct_inv}%", x=0.5, y=0.5, font_size=40, font_family="Orbitron", font_color="#00d4ff", showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<h3 style='text-align: center; color: var(--text-secondary);'>נספרו {int(current)} מתוך {int(target)} איתורים</h3>", unsafe_allow_html=True)
    else:
        st.info("טרם הוגדרו יעדי ספירה על ידי המנהל.")

# --- הגדרות ---
elif choice == OPT_MANAGE:
    st.markdown("### ⚙️ ניהול ועריכת משימות")
    for idx, row in df.iterrows():
        st.markdown(f"""<div style="border: 1px solid var(--border); border-radius: 12px; padding: 15px; margin-bottom: 10px; background: var(--bg-card); border-right: 4px solid var(--accent-cyan);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: var(--text-primary); font-weight: bold; font-size: 1.1rem;">{row['Task_Name']}</span>
                <span style="color: var(--accent-cyan); font-size: 0.85rem; background: rgba(0, 212, 255, 0.1); padding: 2px 8px; border-radius: 20px;">{row['Recurring']}</span>
            </div>
        </div>""", unsafe_allow_html=True)
        col1, col2, _ = st.columns([1.2, 1, 3])
        with col1:
            with st.popover("📝 עריכה", use_container_width=True):
                n_n = st.text_input("שם", value=row['Task_Name'], key=f"e_n_{row['ID']}")
                n_d = st.text_area("תיאור", value=row['Description'], key=f"e_d_{row['ID']}")
                if st.button("שמור", key=f"s_{row['ID']}"):
                    df.at[idx, 'Task_Name'], df.at[idx, 'Description'] = n_n, n_d
                    save_data(df); st.rerun()
        with col2:
            if st.button("🗑️ מחיקה", key=f"d_{row['ID']}"):
                df = df.drop(idx); save_data(df); st.rerun()

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
        for i in range(500):
            d = base + timedelta(days=i)
            if is_scheduled_on(base, row["Recurring"], d):
                is_done = d.strftime("%Y-%m-%d") in str(row["Done_Dates"])
                events.append({"title": row["Task_Name"], "start": d.strftime("%Y-%m-%d"), "color": "#00e5a0" if is_done else "#ff4d6d", "allDay": True})
    calendar(events=events, options={"direction": "rtl", "locale": "he", "initialView": "dayGridMonth"}, custom_css=".fc { background: #0d1f3c; color: #e8f0fe; border-radius: 16px; }")
