import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול משימות - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב UI/UX מלא - כרטיסי כניסה פרימיום וקריאות Sidebar
st.markdown("""
    <style>
    /* רקע כללי Off-white רך */
    .stApp { background-color: #f1f5f9; }
    
    /* === תפריט צד (Sidebar) - קריאות מקסימלית === */
    section[data-testid="stSidebar"] { 
        background-color: #0f172a !important; /* כחול-כהה עמוק */
        border-left: 1px solid #1e293b;
    }
    
    /* טקסטים, לייבלים וכותרות ב-Sidebar - לבן בוהק */
    section[data-testid="stSidebar"] .st-bd, 
    section[data-testid="stSidebar"] .st-bc,
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        line-height: 1.6;
    }
    
    /* כותרות ה-Sidebar - כחול בהיר בולט */
    section[data-testid="stSidebar"] h3 { 
        color: #60a5fa !important; 
        font-weight: 800 !important; 
        margin-top: 15px;
    }

    /* רכיב ה-Radio (הניווט) - לבן על כהה */
    div[data-testid="stSidebarUserContent"] .st-bd {
        color: #FFFFFF !important;
    }

    /* === כפתור התנתקות פרימיום - CSS ממוקד === */
    .stButton > button[key="logout_btn"] {
        background-color: #b91c1c !important; /* אדום יוקרתי כהה */
        color: white !important;
        border-radius: 15px !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        border: none !important;
        height: 60px !important;
        width: 100% !important;
        margin-top: 30px !important;
        box-shadow: 0 4px 10px rgba(185, 28, 28, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[key="logout_btn"]:hover {
        background-color: #dc2626 !important; /* אדום בוהק יותר בריחוף */
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 15px rgba(185, 28, 28, 0.5) !important;
    }

    /* === מסך כניסה - בניית כרטיסים מאפס ב-CSS === */
    .login-wrapper {
        display: flex;
        justify-content: center;
        gap: 30px;
        padding-top: 50px;
        width: 100%;
    }

    /* כרטיס בודד - יחס גובה-רוחב מדוייק מ-image_1.png */
    .login-card {
        background: white;
        border-radius: 25px;
        width: 280px; /* רוחב קבוע למניעת מתיחה */
        height: 380px; /* גובה קבוע ומאוזן */
        box-shadow: 0 10px 25px rgba(0,0,0,0.06);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 30px;
        cursor: pointer;
        border: 2px solid #f1f5f9;
    }

    /* אפקט ריחוף על הכרטיס */
    .login-card:hover {
        transform: scale(1.05) translateY(-10px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }

    /* חלקים פנימיים בכרטיס */
    .card-top { flex-grow: 1; display: flex; flex-direction: column; align-items: center; }
    .card-icon { font-size: 50px; margin-bottom: 20px; }
    .card-title { font-size: 26px; font-weight: 800; color: #1e293b; margin-top: 10px; }
    
    /* פס צבע תחתון - מדוייק וגבוה */
    .card-strip {
        width: 100%;
        height: 15px;
        position: absolute;
        bottom: 0;
        left: 0;
        border-radius: 0 0 25px 25px;
    }

    /* שיפור עיצוב המטריקות והדשבורד */
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-right: 6px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

# --- פונקציות ניהול נתונים (ללא שינוי לוגי) ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            data = pd.read_csv(DB_FILE)
            for col in ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"]:
                if col not in data.columns: data[col] = ""
            return data.fillna("")
        except: return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"])

def save_data(df_to_save):
    df_to_save.to_csv(DB_FILE, index=False)

def get_daily_status(target_date):
    if st.session_state.df.empty: return []
    scheduled, target_str = [], target_date.strftime("%Y-%m-%d")
    for idx, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date']).to_pydatetime()
            diff = (target_date - base).days
            if diff >= 0:
                f = row.get('Recurring', 'לא')
                hit = (f=="לא" and diff==0) or (f=="יומי") or (f=="שבועי" and diff%7==0) or (f=="דו-שבועי" and diff%14==0) or (f=="חודשי" and diff%30==0)
                if hit:
                    scheduled.append({"idx": idx, "id": row['ID'], "name": row['Task_Name'], "desc": row['Description'], "recurring": f, "is_done": target_str in str(row['Done_Dates']).split(",")})
        except: continue
    return scheduled

# 4. ניהול כניסה למערכת - בניית הכרטיסים המושלמת ב-Custom CSS
if "user_role" not in st.session_state: st.session_state.user_role = None

if st.session_state.user_role is None:
    # כותרות הדף הראשון - בולטות ומרוכזות
    st.markdown("<h1 style='text-align: center; color: #0f172a; font-size: 3.5rem; font-weight: 900; padding-top: 50px;'>ברוכים הבאים למערכת ניהול משימות - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.6rem; margin-bottom: 40px;'>ניהול לוגיסטי מתקדם | בחר תפקיד לכניסה</p>", unsafe_allow_html=True)
    
    # עטיפה מרכזית לכרטיסים
    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    
    # עמודות לכרטיסים
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # בניית כרטיס WMS Manager ב-HTML
        st.markdown(f"""
            <div class='login-card'>
                <div class='card-top'>
                    <div class='card-icon'>🔑</div>
                    <div class='card-title'>WMS<br>מנהל</div>
                </div>
                <div class='card-strip' style='background-color: #2563eb;'></div>
            </div>
        """, unsafe_allow_html=True)
        # כפתור שקוף המכסה את הכרטיס
        if st.button("כניסה", key="l_admin", use_container_width=True):
            st.session_state.user_role = "מנהל WMS"; st.rerun()

    with c2:
        # בניית כרטיס Warehouse Team ב-HTML
        st.markdown(f"""
            <div class='login-card'>
                <div class='card-top'>
                    <div class='card-icon'>📦</div>
                    <div class='card-title'>מחסן<br>צוות</div>
                </div>
                <div class='card-strip' style='background-color: #d97706;'></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("כניסה", key="l_staff", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"; st.rerun()

    with c3:
        # בניית כרטיס VP ב-HTML
        st.markdown(f"""
            <div class='login-card'>
                <div class='card-top'>
                    <div class='card-icon'>📊</div>
                    <div class='card-title'>סמנכ"ל</div>
                </div>
                <div class='card-strip' style='background-color: #059669;'></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("כניסה", key="l_vp", use_container_width=True):
            st.session_state.user_role = "סמנכ\"ל"; st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 5. ניווט ותפריט צד (Sidebar) - קריאות מלאה וכפתור פרימיום
if "df" not in st.session_state: st.session_state.df = load_data()

with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    st.divider()
    
    OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"
    
    if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
    elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
    else: menu = [OPT_DASH, OPT_CAL]
    
    choice = st.radio("תפריט ניווט:", menu)
    
    # כפתור התנתקות פרימיום ממוקם בתחתית
    st.write("<br>"*15, unsafe_allow_html=True)
    if st.button("🚪 התנתקות מהמערכת", key="logout_btn", use_container_width=True):
        st.session_state.user_role = None; st.rerun()

# 6. דפי המערכת (ללא שינוי לוגי)
if choice == OPT_DASH:
    st.title("📊 דשבורד בקרה")
    tasks = get_daily_status(datetime.now())
    c1, c2, c3 = st.columns(3)
    c1.metric("📋 משימות להיום", len(tasks))
    c2.metric("✅ בוצעו", sum(1 for t in tasks if t['is_done']))
    st.divider()
    for t in tasks:
        icon, color = ("✅", "#10b981") if t['is_done'] else ("⏳", "#f59e0b")
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><div><strong style="font-size:1.15rem;">{t["name"]}</strong><br><span style="color: #64748b;">{t["desc"]}</span></div><div style="font-size:24px;">{icon}</div></div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.title("📋 סידור עבודה שבועי")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(len(days))
    for i, day in enumerate(days):
        curr = start + timedelta(days=i)
        with cols[i]:
            st.markdown(f"<div style='background:#1e293b; color:white; padding:10px; border-radius:10px; text-align:center; margin-bottom:15px;'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            for t in get_daily_status(curr):
                status_prefix = "✅" if t['is_done'] else "⏳"
                st.markdown(f"**{status_prefix} {t['name']}**")
                if not t['is_done'] and st.button("בצע", key=f"btn_{t['id']}_{i}"):
                    idx = t['idx']
                    st.session_state.df.at[idx, "Done_Dates"] = f"{str(st.session_state.df.at[idx, 'Done_Dates'])},{curr.strftime('%Y-%m-%d')}".strip(",")
                    save_data(st.session_state.df); st.rerun()

elif choice == OPT_CAL:
    st.title("📅 לוח שנה")
    st.info("טיפ: לחץ על משימה בלוח כדי לראות את הפרטים שלה למטה")
    cal_events, task_lookup = [], {}
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            f = row['Recurring']
            for i in range(100 if f != "לא" else 1):
                gap = 1 if f=="יומי" else 7 if f=="שבועי" else 14 if f=="דו-שבועי" else 30 if f=="חודשי" else 0
                d = (base + timedelta(days=i*gap)).strftime("%Y-%m-%d")
                is_done = d in str(row['Done_Dates'])
                event_id = f"{row['ID']}_{d}"
                cal_events.append({"id": event_id, "title": f"{'✅' if is_done else '⏳'} {row['Task_Name']}", "start": d, "color": "#10b981" if is_done else "#ef4444"})
                task_lookup[event_id] = row
        except: continue
    res = calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 550}, key="main_cal")
    if res.get("eventClick"):
        task = task_lookup.get(res["eventClick"]["event"]["id"])
        if task is not None:
            st.markdown(f'<div class="detail-box"><h2>🔍 פרטי משימה מהלוח</h2><p><strong>משימה:</strong> {task["Task_Name"]}</p><p><strong>תדירות:</strong> {task["Recurring"]}</p><p><strong>תיאור:</strong> {task["Description"]}</p></div>', unsafe_allow_html=True)

elif choice == OPT_ADD:
    st.title("➕ הוספת משימה")
    with st.form("add_task"):
        n = st.text_input("שם המשימה")
        f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        d = st.date_input("תאריך התחלה", datetime.now())
        ds = st.text_area("תיאור")
        if st.form_submit_button("שמור במערכת"):
            new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df); st.success("המשימה נוספה בהצלחה!"); st.rerun()

elif choice == OPT_MANAGE:
    st.title("⚙️ הגדרות")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        t_del = st.selectbox("מחיקת משימה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != t_del]
            save_data(st.session_state.df); st.rerun()
