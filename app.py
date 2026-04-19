import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת מחסן - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX מומחה - צבעוניות וכרטיסים צפים
st.markdown("""
    <style>
    /* רקע כללי וגופנים */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* עיצוב כפתורי הכניסה - הגדלה משמעותית וצבעוניות */
    .stButton>button {
        height: 320px !important; /* הגדלה משמעותית של החלון */
        width: 100% !important;
        border-radius: 30px !important;
        border: 2px solid rgba(255,255,255,0.5) !important;
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1) !important;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        cursor: pointer;
    }
    
    .stButton>button:hover {
        transform: scale(1.05) translateY(-10px) !important;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15) !important;
        background: white !important;
    }

    /* טקסט בתוך כפתורי הכניסה */
    .stButton>button div p {
        font-size: 32px !important;
        font-weight: 900 !important;
        letter-spacing: 1px;
    }

    /* התאמת צבעים אישית לכל תפקיד - עיצוב יוקרתי */
    /* מנהל WMS - כחול עמוק */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { 
        border-bottom: 15px solid #1E3A8A !important; 
        color: #1E3A8A !important; 
    }
    /* צוות מחסן - כתום זהב */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { 
        border-bottom: 15px solid #F59E0B !important; 
        color: #F59E0B !important; 
    }
    /* סמנכ"ל - ירוק אמרלד */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { 
        border-bottom: 15px solid #10B981 !important; 
        color: #10B981 !important; 
    }

    /* עיצוב ה-Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] label {
        color: #F8FAFC !important;
    }

    /* כרטיסי המטריקות (Metrics) */
    div[data-testid="stMetric"] {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 8px solid #3B82F6;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

# --- פונקציות ניהול נתונים (ללא שינוי לוגי) ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            data = pd.read_csv(DB_FILE)
            cols = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"]
            for col in cols:
                if col not in data.columns: data[col] = ""
            return data.fillna("")
        except:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])

def save_data(df_to_save):
    df_to_save.to_csv(DB_FILE, index=False)

def get_daily_status(target_date):
    if st.session_state.df.empty: return []
    scheduled = []
    target_str = target_date.strftime("%Y-%m-%d")
    for idx, row in st.session_state.df.iterrows():
        try:
            if not row.get('Date'): continue
            base = pd.to_datetime(row['Date']).to_pydatetime()
            diff = (target_date - base).days
            if diff >= 0:
                hit = False
                f = row.get('Recurring', 'לא')
                if f == "לא" and diff == 0: hit = True
                elif f == "יומי" and diff < 200: hit = True
                elif f == "שבועי" and diff % 7 == 0 and (diff // 7) < 200: hit = True
                elif f == "דו-שבועי" and diff % 14 == 0 and (diff // 14) < 200: hit = True
                elif f == "חודשי" and diff % 30 == 0 and (diff // 30) < 200: hit = True
                
                if hit:
                    done = str(row.get('Done_Dates', ""))
                    scheduled.append({
                        "idx": idx, "id": row['ID'], "name": row['Task_Name'], 
                        "desc": row['Description'], "is_done": target_str in done.split(",")
                    })
        except: continue
    return scheduled

# 4. ניהול כניסה למערכת - מסך מעוצב
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown("<br><br><h1 style='text-align: center; color: #1E293B; font-size: 3.5rem;'>ברוכים הבאים למערכת המחסן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.5rem; color: #475569;'>אחים כהן | ניהול לוגיסטי חכם</p>", unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        if st.button("👑\nמנהל WMS", key="btn_admin"):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
    with c2:
        if st.button("📦\nצוות מחסן", key="btn_staff"):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
    with c3:
        if st.button("📈\nסמנכ\"ל", key="btn_vp"):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
    st.stop()

# 5. טעינת נתונים ותפריט צד
if "df" not in st.session_state:
    st.session_state.df = load_data()

user_role = st.session_state.user_role
with st.sidebar:
    st.markdown(f"<h2 style='color: white;'>שלום, {user_role}</h2>", unsafe_allow_html=True)
    st.divider()
    
    OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH = "📅 לוח שנה", "📋 סידור עבודה", "➕ הוספת משימה", "⚙️ הגדרות", "📊 דשבורד בקרה"
    
    if user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
    elif user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
    else: menu = [OPT_DASH, OPT_CAL]
    
    choice = st.radio("ניווט במערכת:", menu)
    
    st.write("<br>"*5, unsafe_allow_html=True)
    if st.button("🚪 התנתקות", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()

# 6. דפי המערכת - דגש על צבעוניות וסידור
if choice == OPT_DASH:
    st.markdown("<h1 style='color: #1E3A8A;'>📊 מרכז בקרה וביצועים</h1>", unsafe_allow_html=True)
    today_tasks = get_daily_status(datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t['is_done'])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("משימות להיום", total)
    m2.metric("בוצעו בהצלחה", done)
    pct = (done/total*100) if total > 0 else 0
    m3.metric("אחוזי עמידה ביעדים", f"{int(pct)}%")
    
    st.write("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 רשימת ביצוע להיום", "💹 סטטיסטיקה"])
    with tab1:
        for t in today_tasks:
            color = "#10B981" if t['is_done'] else "#F59E0B"
            st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 15px; border-right: 10px solid {color}; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <h4 style="margin:0; color: #1E293B;">{t['name']}</h4>
                    <p style="margin:0; color: #64748B;">{t['desc']}</p>
                </div>
            """, unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.markdown("<h1 style='color: #1E3A8A;'>📋 סידור עבודה שבועי</h1>", unsafe_allow_html=True)
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(len(days))
    
    for i, day_label in enumerate(days):
        curr_date = start + timedelta(days=i)
        date_str = curr_date.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"<div style='text-align: center; background: #334155; color: white; padding: 10px; border-radius: 15px; margin-bottom: 10px;'>{day_label}<br>{curr_date.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            tasks = get_daily_status(curr_date)
            for t in tasks:
                if t['is_done']:
                    st.success(f"**{t['name']}**")
                else:
                    st.warning(f"**{t['name']}**")
                    if user_role in ["מנהל WMS", "צוות מחסן"]:
                        if st.button("סמן בוצע", key=f"btn_{t['id']}_{date_str}"):
                            idx = t['idx']
                            old_val = str(st.session_state.df.at[idx, "Done_Dates"])
                            st.session_state.df.at[idx, "Done_Dates"] = f"{old_val},{date_str}".strip(",")
                            save_data(st.session_state.df)
                            st.rerun()

elif choice == OPT_CAL:
    st.header("📅 לוח שנה")
    cal_events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date']).to_pydatetime()
            done_list = str(row['Done_Dates']).split(",")
            f = row['Recurring']
            num = 120 if f != "לא" else 1
            gap = 1 if f=="יומי" else 7 if f=="שבועי" else 14 if f=="דו-שבועי" else 30 if f=="חודשי" else 0
            for i in range(num):
                curr = base + timedelta(days=i * gap)
                c_str = curr.strftime("%Y-%m-%d")
                cal_events.append({"title": row['Task_Name'], "start": c_str, "color": "#10B981" if c_str in done_list else "#EF4444"})
        except: continue
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he"})

elif choice == OPT_ADD:
    st.markdown("<h1 style='color: #1E3A8A;'>➕ הוספת משימה חדשה</h1>", unsafe_allow_html=True)
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            t_name = st.text_input("שם המשימה")
            t_freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        with c2:
            t_date = st.date_input("תאריך התחלה")
            t_desc = st.text_area("תיאור")
        if st.form_submit_button("שמור משימה במערכת"):
            if t_name:
                new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 1000
                new_row = pd.DataFrame([{"ID": new_id, "Task_Name": t_name, "Description": t_desc, "Recurring": t_freq, "Date": t_date.strftime("%Y-%m-%d"), "Done_Dates": "", "Final_Approval": "לא"}])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.success("המשימה נשמרה בהצלחה!")
                st.rerun()

elif choice == OPT_MANAGE:
    st.header("⚙️ הגדרות מערכת")
    st.dataframe(st.session_state.df, use_container_width=True)
