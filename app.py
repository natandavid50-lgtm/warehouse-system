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
   SIDEBAR
   ========================================= */
[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-left: 1px solid var(--border) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
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
   HOME PAGE — BIG BUTTONS
   ========================================= */
div[data-testid="stHorizontalBlock"] .stButton > button {
    min-height: 200px !important;
    border-radius: var(--radius-card) !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    letter-spacing: 1px;
    position: relative;
    overflow: hidden;
}

div[data-testid="stHorizontalBlock"] .stButton > button::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, transparent 60%);
    pointer-events: none;
}

div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    transform: translateY(-5px) !important;
    color: #fff !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
    border-top: 3px solid var(--accent-blue) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3), 0 -1px 0 var(--accent-blue) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover {
    box-shadow: var(--glow-blue), 0 12px 40px rgba(0,0,0,0.5) !important;
    border-color: var(--accent-blue) !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
    border-top: 3px solid var(--accent-amber) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
    box-shadow: 0 0 20px rgba(245,158,11,0.4), 0 12px 40px rgba(0,0,0,0.5) !important;
    border-color: var(--accent-amber) !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
    border-top: 3px solid var(--accent-green) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover {
    box-shadow: var(--glow-green), 0 12px 40px rgba(0,0,0,0.5) !important;
    border-color: var(--accent-green) !important;
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
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(56, 139, 253, 0.3), rgba(56, 139, 253, 0.1)) !important;
    box-shadow: var(--glow-blue) !important;
    transform: translateY(-2px) !important;
    color: #fff !important;
}

/* =========================================
   POPOVER (TASK CARDS)
   ========================================= */
div[data-testid="stPopover"] > button {
    width: 100% !important;
    min-height: 70px !important;
    margin-bottom: 10px !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    transition: all 0.2s ease !important;
    font-size: 0.9rem !important;
    text-align: right !important;
    padding: 12px 16px !important;
    letter-spacing: 0.3px;
}

div[data-testid="stPopover"] > button:hover {
    background: var(--bg-card-hover) !important;
    border-color: var(--border-bright) !important;
    box-shadow: var(--glow-blue) !important;
    transform: translateX(-3px) !important;
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
    letter-spacing: 1px;
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
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px rgba(56, 139, 253, 0.15) !important;
}

.stDateInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

.stSelectbox > div > div {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}

/* Labels */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stDateInput label,
.stRadio label {
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

/* =========================================
   INFO / ALERT BOXES
   ========================================= */
[data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    border-right: 3px solid var(--accent-blue) !important;
}

/* =========================================
   CHARTS
   ========================================= */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-card) !important;
    border: 1px solid var(--border) !important;
    padding: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
}

/* =========================================
   DIVIDERS & TEXT
   ========================================= */
hr {
    border-color: var(--border) !important;
    margin: 20px 0 !important;
}

h1, h2, h3, h4 {
    color: var(--text-primary) !important;
    font-family: "Heebo", sans-serif !important;
}

p, li, span {
    color: var(--text-secondary) !important;
}

/* =========================================
   SCROLLBAR
   ========================================= */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-panel); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-blue); }

/* =========================================
   FORM SUBMIT BUTTON
   ========================================= */
[data-testid="stForm"] .stButton > button {
    background: linear-gradient(135deg, var(--accent-blue), #1a6fd4) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 700 !important;
    padding: 12px 28px !important;
    font-size: 1rem !important;
    letter-spacing: 1px;
    box-shadow: var(--glow-blue) !important;
}

[data-testid="stForm"] .stButton > button:hover {
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)) !important;
    box-shadow: var(--glow-cyan) !important;
    transform: translateY(-2px) !important;
}

/* Form container */
[data-testid="stForm"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-card) !important;
    padding: 24px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
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

# תפריט צד - הגדרת הרשאות
st.sidebar.markdown(f"### שלום, **{st.session_state.user_role}**")
if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "סמנכ\"ל":
    menu = [OPT_DASH, OPT_CAL]
else:
    # צוות מחסן
    menu = [OPT_DASH, OPT_WORK, OPT_CAL]

choice = st.sidebar.radio("תפריט", menu)
if st.sidebar.button("התנתקות"):
    st.session_state.user_role = None
    st.rerun()

# --- הצגת כותרת הדף בתוך הבאנר המעוצב ---
st.markdown(f'<div class="page-header-banner"><h1>{choice}</h1></div>', unsafe_allow_html=True)

# --- דשבורד בקרה ---
if choice == OPT_DASH:
    # 1. בורר תאריכים ומדדים
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
    
    # --- הצגת פירוט משימות ---
    st.write(f"### פירוט משימות {date_label}")
    if total > 0:
        for t in selected_tasks:
            st.info(f"{'✅' if t['is_done'] else '⏳'} {t['name']}")
    else:
        st.write("אין משימות מתוכננות לתאריך זה.")

    # --- הצגת המגמה בסוף ---
    st.write("---")
    st.write("### 📈 מגמת ביצועים שבועית")
    
    import plotly.express as px
    
    weekly_data = []
    for i in range(6, -1, -1):
        day = datetime.now().date() - timedelta(days=i)
        tasks = get_daily_status(df, day)
        t_total = len(tasks)
        t_done = sum(1 for t in tasks if t["is_done"])
        t_pct = int((t_done / t_total) * 100) if t_total > 0 else 0
        weekly_data.append({"תאריך": day.strftime("%d/%m"), "אחוז": t_pct})
    
    chart_df = pd.DataFrame(weekly_data)

    fig = px.area(chart_df, x="תאריך", y="אחוז", markers=True)

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#8eafd4",
        margin=dict(l=0, r=0, t=20, b=0),
        height=300,
        xaxis=dict(showgrid=True, gridcolor='rgba(56, 139, 253, 0.1)', title=""),
        yaxis=dict(showgrid=True, gridcolor='rgba(56, 139, 253, 0.1)', range=[0, 105], title="אחוז ביצוע")
    )
    
    fig.update_traces(
        line=dict(width=3, color='#00d4ff'),
        marker=dict(size=8, color='#388bfd', line=dict(width=2, color='#00d4ff')),
        fillcolor='rgba(0, 212, 255, 0.1)'
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

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

# --- הגדרות (ניהול משימות מעוצב) ---
elif choice == OPT_MANAGE:
    st.markdown("### ⚙️ ניהול ועריכת משימות")
    
    if df.empty:
        st.info("אין משימות רשומות במערכת.")
    else:
        for idx, row in df.iterrows():
            # יצירת כרטיס מעוצב לכל משימה
            st.markdown(f"""
            <div style="
                border: 1px solid var(--border); 
                border-radius: 12px; 
                padding: 15px; 
                margin-bottom: 10px; 
                background: var(--bg-card);
                border-right: 4px solid var(--accent-cyan);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--text-primary); font-weight: bold; font-size: 1.1rem;">{row['Task_Name']}</span>
                    <span style="color: var(--accent-cyan); font-size: 0.85rem; background: rgba(0, 212, 255, 0.1); padding: 2px 8px; border-radius: 20px;">{row['Recurring']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # כפתורי פעולה בטורים
            col1, col2, _ = st.columns([1.2, 1, 3])
            
            with col1:
                # כפתור עריכה ב-Popover
                with st.popover("📝 עריכה", use_container_width=True):
                    st.markdown(f"**עריכת משימה: {row['Task_Name']}**")
                    new_name = st.text_input("שם המשימה", value=row['Task_Name'], key=f"edit_name_{row['ID']}")
                    new_desc = st.text_area("תיאור", value=row['Description'], key=f"edit_desc_{row['ID']}")
                    
                    freq_options = ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"]
                    current_freq_idx = freq_options.index(row['Recurring']) if row['Recurring'] in freq_options else 0
                    new_freq = st.selectbox("תדירות", freq_options, index=current_freq_idx, key=f"edit_freq_{row['ID']}")
                    
                    if st.button("שמור שינויים", key=f"save_{row['ID']}", use_container_width=True):
                        df.at[idx, 'Task_Name'] = new_name
                        df.at[idx, 'Description'] = new_desc
                        df.at[idx, 'Recurring'] = new_freq
                        save_data(df)
                        st.success("המשימה עודכנה!")
                        st.rerun()

            with col2:
                # כפתור מחיקה
                if st.button("🗑️ מחיקה", key=f"del_{row['ID']}", use_container_width=True):
                    df = df.drop(idx)
                    save_data(df)
                    st.rerun()
            
            st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

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
                events.append({
                    "title": row["Task_Name"], 
                    "start": d.strftime("%Y-%m-%d"), 
                    "color": "#10b981" if d.strftime("%Y-%m-%d") in str(row["Done_Dates"]) else "#ef4444"
                })
    calendar(events=events, options={"direction": "rtl", "locale": "he"})
