import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד - רוחב מלא
st.set_page_config(page_title="אחים כהן - ניהול מחסן", layout="wide", initial_sidebar_state="expanded")

# 2. הזרקת CSS - שדרוג ויזואלי מקיף
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');

    /* הגדרות גלובליות */
    html, body, [class*="css"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
    }

    .stApp { background-color: #f1f5f9; }

    /* סיידבר מעוצב */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-left: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] * { color: #f8fafc !important; }
    .st-emotion-cache-16txtl3 { padding: 2rem 1rem; }
    
    /* כרטיסי כניסה - עיצוב פרימיום */
    .login-card {
        background: white;
        border-radius: 24px;
        padding: 40px 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #f1f5f9;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        margin-bottom: 20px;
    }
    .login-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #3b82f6;
    }
    .card-icon { font-size: 80px; margin-bottom: 20px; filter: drop-shadow(0 10px 8px rgba(0,0,0,0.1)); }
    .card-title { font-size: 28px; font-weight: 800; color: #0f172a; margin-bottom: 10px; }
    
    /* מטריקות בדשבורד */
    [data-testid="stMetricValue"] { font-size: 3rem !important; font-weight: 800 !important; color: #3b82f6 !important; }
    [data-testid="stMetricLabel"] { font-size: 1.1rem !important; color: #64748b !important; }
    div[data-testid="metric-container"] {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }

    /* כרטיסי משימות */
    .task-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 16px;
        border-right: 8px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: all 0.2s ease;
    }
    .task-card:hover { box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
    .task-card b { font-size: 1.2rem; color: #1e293b; }
    .task-card small { color: #64748b; font-size: 0.9rem; }

    /* עיצוב כותרות ימים בסידור */
    .day-header {
        background: #1e293b;
        color: #f8fafc;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* כפתור התנתקות יוקרתי */
    .stButton > button {
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    button[key="logout_btn"] {
        background-color: transparent !important;
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
    }
    button[key="logout_btn"]:hover {
        background-color: #ef4444 !important;
        color: white !important;
    }

    /* תיקון צ'קבוקסים */
    .stCheckbox {
        background: #f8fafc;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. פונקציות ליבה (לוגיקה)
DB_FILE = "warehouse_management_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            data = pd.read_csv(DB_FILE)
            cols = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"]
            for col in cols:
                if col not in data.columns: data[col] = ""
            return data.fillna("")
        except: return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])

def save_data(df_to_save):
    df_to_save.to_csv(DB_FILE, index=False)

def get_daily_status(target_date):
    if st.session_state.df.empty: return []
    scheduled = []
    target_str = target_date.strftime("%Y-%m-%d")
    for idx, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date']).to_pydatetime().replace(tzinfo=None)
            target_naive = target_date.replace(tzinfo=None) if hasattr(target_date, 'tzinfo') else target_date
            diff = (target_naive - base).days
            if diff >= 0:
                f = row.get('Recurring', 'לא')
                hit = (f == "לא" and diff == 0) or (f == "יומי") or (f == "שבועי" and diff % 7 == 0) or \
                      (f == "דו-שבועי" and diff % 14 == 0) or (f == "חודשי" and diff % 30 == 0)
                if hit:
                    done_dates = str(row['Done_Dates']).strip()
                    is_done = target_str in done_dates.split(",") if done_dates else False
                    scheduled.append({"idx": idx, "id": row['ID'], "name": row['Task_Name'], "desc": row['Description'], "recurring": f, "is_done": is_done})
        except: continue
    return scheduled

# 4. ניהול מצב (Session)
if "user_role" not in st.session_state: st.session_state.user_role = None
if "df" not in st.session_state: st.session_state.df = load_data()
if "current_page" not in st.session_state: st.session_state.current_page = None

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# --- מסך כניסה מעוצב ---
if st.session_state.user_role is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #0f172a; font-size: 3.5rem; font-weight: 800;'>אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #64748b; font-weight: 400;'>מערכת ניהול משימות מחסן חכמה</h3>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    cols = st.columns(3, gap="large")
    roles = [
        {"role": "מנהל WMS", "icon": "🔑", "color": "#3b82f6", "id": "admin"},
        {"role": "צוות מחסן", "icon": "📦", "color": "#f59e0b", "id": "staff"},
        {"role": "סמנכ\"ל", "icon": "📈", "color": "#10b981", "id": "vp"}
    ]
    for i, col in enumerate(cols):
        with col:
            r = roles[i]
            st.markdown(f"""
                <div class='login-card'>
                    <div class='card-icon'>{r['icon']}</div>
                    <div class='card-title'>{r['role']}</div>
                    <div style='color: #94a3b8;'>כניסה למערכת</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"התחבר כ-{r['role']}", key=f"login_{r['id']}", use_container_width=True):
                st.session_state.user_role = r['role']
                st.session_state.current_page = OPT_WORK if r['role'] == "צוות מחסן" else OPT_DASH
                st.rerun()
    st.stop()

# --- תפריט לפי הרשאות ---
if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
else: menu = [OPT_DASH, OPT_CAL]

if st.session_state.current_page not in menu: st.session_state.current_page = menu[0]

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"<div style='padding: 10px; border-radius: 12px; background: #1e293b; margin-bottom: 20px;'><h3 style='margin:0; text-align:center;'>{st.session_state.user_role}</h3></div>", unsafe_allow_html=True)
    choice = st.radio("ניווט במערכת", menu, index=menu.index(st.session_state.current_page))
    st.session_state.current_page = choice
    st.spacer = st.container()
    with st.spacer:
        st.markdown("<br>" * 5, unsafe_allow_html=True)
        if st.button("🚪 התנתקות", key="logout_btn", use_container_width=True):
            st.session_state.user_role = None
            st.rerun()

# --- דפים ---
if choice == OPT_DASH:
    st.markdown("<h1 style='color: #0f172a;'>דשבורד בקרה</h1>", unsafe_allow_html=True)
    tasks = get_daily_status(datetime.now())
    t_count, d_count = len(tasks), sum(1 for t in tasks if t['is_done'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות להיום", t_count)
    c2.metric("בוצעו בהצלחה", d_count)
    c3.metric("אחוז עמידה ביעדים", f"{int(d_count/t_count*100) if t_count>0 else 0}%")
    
    st.markdown("<br><h3>פירוט משימות נוכחי</h3>", unsafe_allow_html=True)
    for t in tasks:
        color = "#10b981" if t['is_done'] else "#f59e0b"
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><b>{t["name"]}</b><br><small>{t["desc"]}</small></div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.markdown("<h1 style='color: #0f172a;'>סידור עבודה שבועי</h1>", unsafe_allow_html=True)
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    cols = st.columns(5)
    for i, day in enumerate(["ראשון", "שני", "שלישי", "רביעי", "חמישי"]):
        curr = start + timedelta(days=i)
        curr_str = curr.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"<div class='day-header'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            day_tasks = get_daily_status(curr)
            if not day_tasks:
                st.markdown("<p style='text-align:center; color:#94a3b8;'>אין משימות</p>", unsafe_allow_html=True)
            for t in day_tasks:
                if t['is_done']: 
                    st.markdown(f"<div style='background:#f0fdf4; color:#166534; padding:10px; border-radius:8px; margin-bottom:8px; border:1px solid #bbf7d0;'>✅ {t['name']}</div>", unsafe_allow_html=True)
                else:
                    if st.checkbox(f"{t['name']}", key=f"chk_{t['id']}_{curr_str}"):
                        idx = t['idx']
                        old = str(st.session_state.df.at[idx, "Done_Dates"]).strip()
                        st.session_state.df.at[idx, "Done_Dates"] = f"{old},{curr_str}".strip(",")
                        save_data(st.session_state.df)
                        st.rerun()

elif choice == OPT_CAL:
    st.markdown("<h1 style='color: #0f172a;'>יומן משימות</h1>", unsafe_allow_html=True)
    events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            freq = row['Recurring']
            num_range = 1 if freq == "לא" else 30
            gap = 1 if freq=="יומי" else 7 if freq=="שבועי" else 14 if freq=="דו-שבועי" else 30 if freq=="חודשי" else 0
            for i in range(num_range):
                d = (base + timedelta(days=i * gap)).strftime("%Y-%m-%d")
                done = d in str(row['Done_Dates'])
                events.append({"title": f"{'✅' if done else '⏳'} {row['Task_Name']}", "start": d, "color": "#10b981" if done else "#3b82f6"})
        except: continue
    
    st.markdown('<div style="background:white; padding:20px; border-radius:24px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 650}, key="cal_v3")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == OPT_ADD:
    st.markdown("<h1 style='color: #0f172a;'>הוספת משימה חדשה</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div style="background:white; padding:30px; border-radius:24px; border:1px solid #e2e8f0;">', unsafe_allow_html=True)
        with st.form("add_task", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("שם המשימה", placeholder="למשל: ספירת מלאי")
            freq = c2.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
            date = c1.date_input("תאריך התחלה", datetime.now())
            desc = st.text_area("תיאור המשימה")
            submit = st.form_submit_button("הוסף משימה למערכת", use_container_width=True)
            
            if submit:
                if name:
                    max_id = pd.to_numeric(st.session_state.df["ID"], errors="coerce").max()
                    new_id = int(max_id + 1) if not pd.isna(max_id) else 1000
                    new_row = pd.DataFrame([{"ID":new_id, "Task_Name":name, "Description":desc, "Recurring":freq, "Date":date.strftime("%Y-%m-%d"), "Done_Dates":""}])
                    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                    save_data(st.session_state.df)
                    st.success("המשימה התווספה בהצלחה!")
                    st.rerun()
                else: st.error("נא להזין שם משימה")
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == OPT_MANAGE:
    st.markdown("<h1 style='color: #0f172a;'>ניהול בסיס נתונים</h1>", unsafe_allow_html=True)
    st.info("💡 לעריכה: לחץ פעמיים על תא. למחיקה: סמן שורה ולחץ Delete במקלדת.")
    
    # התיקון: num_rows="dynamic" מאפשר מחיקה והוספה, ו-key ייחודי מבטיח סנכרון
    edited_df = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic", 
        key="main_data_editor"
    )
    
    if st.button("💾 שמור שינויים במערכת", use_container_width=True):
        st.session_state.df = edited_df
        save_data(edited_df)
        st.success("הנתונים נשמרו בהצלחה!")
        st.rerun()
