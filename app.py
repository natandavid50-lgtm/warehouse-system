import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד (חובה בתחילת הקוד)
st.set_page_config(page_title="מערכת ניהול משימות - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. הזרקת עיצוב CSS מלא - החזרת המראה היוקרתי והתיקון ללוח השנה
st.markdown("""
    <style>
    /* רקע כללי */
    .stApp { background-color: #f1f5f9; }
    
    /* עיצוב סיידבר כהה מלא */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        min-width: 280px !important;
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] h3 { 
        color: #60a5fa !important; 
        font-weight: 800 !important; 
        letter-spacing: 1px;
    }

    /* כפתור התנתקות מעוצב בתחתית הסיידבר */
    .stButton > button[key="logout_btn"] {
        background-color: #b91c1c !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s;
        height: 50px !important;
    }
    .stButton > button[key="logout_btn"]:hover {
        background-color: #ef4444 !important;
        transform: scale(1.02);
    }

    /* עיצוב כרטיסי הכניסה - המראה היוקרתי המקורי */
    .login-card {
        background: white;
        border-radius: 24px;
        height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
        position: relative;
        overflow: hidden;
        transition: all 0.4s ease;
    }
    .login-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
    }
    .card-icon { font-size: 85px; margin-bottom: 20px; }
    .card-title { 
        font-size: 34px; 
        font-weight: 900; 
        color: #1e293b; 
        text-align: center;
        line-height: 1.1;
    }
    .card-strip { 
        width: 100%; 
        height: 12px; 
        position: absolute; 
        bottom: 0; 
        left: 0; 
    }

    /* הפיכת כפתור הכניסה לשקוף על כל הכרטיס */
    div.stButton > button.login-trigger {
        height: 380px !important;
        width: 100% !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        position: absolute !important;
        top: -380px !important; 
        z-index: 100 !important;
    }

    /* עיצוב כרטיסי משימות בדשבורד ובסידור */
    .task-card {
        background: white;
        padding: 24px;
        border-radius: 18px;
        margin-bottom: 15px;
        border-right: 12px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* --- תיקון מלא ללוח השנה --- */
    .fc {
        max-width: 900px !important;  /* הגבלת רוחב הלוח */
        margin: 0 auto !important;     /* מרכוז */
        height: 600px !important;     /* הגבלת גובה חזקה */
        overflow: hidden !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        background: white !important;
        padding: 10px !important;
    }
    
    /* תיקון נראות הטבלה */
    .fc-view-harness {
        border: 1px solid #e2e8f0 !important;
    }
    
    /* מראה כותרות הימים */
    .fc-col-header-cell-cushion {
        font-weight: bold !important;
        color: #1e293b !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ניהול נתונים (CSV Load/Save)
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

# 4. אתחול Session State (הזיכרון המערכתי)
if "user_role" not in st.session_state: st.session_state.user_role = None
if "df" not in st.session_state: st.session_state.df = load_data()
if "current_page" not in st.session_state: st.session_state.current_page = None

# הגדרת שמות הדפים
OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# --- לוגיקת מסך כניסה (מעוצב ומחוסן מניתוקים) ---
if st.session_state.user_role is None:
    st.markdown("<br><h1 style='text-align: center; font-size: 3.8rem; font-weight: 900; color: #0f172a;'>מערכת ניהול משימות - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.6rem; color: #64748b; margin-bottom: 60px;'>בקרה לוגיסטית וניהול משימות חכם</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    roles = [
        {"id": "admin", "title": "מנהל<br>WMS", "icon": "🔑", "color": "#2563eb", "role": "מנהל WMS"},
        {"id": "staff", "title": "צוות<br>מחסן", "icon": "📦", "color": "#f59e0b", "role": "צוות מחסן"},
        {"id": "vp", "title": "סמנכ\"ל<br>ניהול", "icon": "📊", "color": "#10b981", "role": "סמנכ\"ל"}
    ]
    
    for i, col in enumerate([col1, col2, col3]):
        with col:
            r = roles[i]
            # יצירת ה-HTML של הכרטיס המעוצב
            st.markdown(f"""
                <div class='login-card'>
                    <div class='card-icon'>{r['icon']}</div>
                    <div class='card-title'>{r['title']}</div>
                    <div class='card-strip' style='background-color: {r['color']};'></div>
                </div>
            """, unsafe_allow_html=True)
            # יצירת הכפתור השקוף שמונח מעל הכרטיס
            if st.button(f"התחברות כ-{r['role']}", key=f"login_btn_{r['id']}", cls="login-trigger", use_container_width=True):
                st.session_state.user_role = r['role']
                # הגדרת דף ראשון לפי תפקיד
                if r['role'] == "צוות מחסן": st.session_state.current_page = OPT_WORK
                else: st.session_state.current_page = OPT_DASH
                st.rerun()
    st.stop() # עוצר את הקוד כאן אם לא מחוברים

# --- הגדרת תפריט הרשאות דינמי ---
if st.session_state.user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
else: menu = [OPT_DASH, OPT_CAL] # סמנכ"ל

# וידוא שהדף הנוכחי קיים בתפריט (מונע קריסה במעבר תפקידים)
if st.session_state.current_page not in menu:
    st.session_state.current_page = menu[0]

# --- Sidebar (החזרת הסטייל הכהה המלא) ---
with st.sidebar:
    st.markdown(f"<h3>שלום, {st.session_state.user_role} 👋</h3>", unsafe_allow_html=True)
    st.divider()
    
    # שימוש ב-Radio פשוט ויציב
    choice = st.radio("תפריט ניווט:", menu, index=menu.index(st.session_state.current_page), key=f"sidebar_nav_{st.session_state.user_role}")
    st.session_state.current_page = choice

    st.write("<br>"*15, unsafe_allow_html=True)
    if st.button("🚪 התנתקות מהמערכת", key="logout_btn", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- דפים ---

if choice == OPT_DASH:
    st.title("📊 דשבורד בקרה וניהול")
    tasks = get_daily_status(datetime.now())
    total, done = len(tasks), sum(1 for t in tasks if t['is_done'])
    c1, c2, c3 = st.columns(3)
    c1.metric("📋 משימות להיום", total)
    c2.metric("✅ בוצעו בהצלחה", done)
    c3.metric("🎯 הספק (אחוז ביצוע)", f"{int(done/total*100) if total>0 else 0}%")
    st.divider()
    for t in tasks:
        color = "#10b981" if t['is_done'] else "#f59e0b"
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><strong>{t["name"]}</strong><br><small>{t["desc"]}</small></div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.title("📋 סידור עבודה שבועי - אחים כהן")
    st.info("סמנו את התיבה ליד המשימה ברגע שסיימתם אותה")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    cols = st.columns(5)
    for i, day in enumerate(["ראשון", "שני", "שלישי", "רביעי", "חמישי"]):
        curr = start + timedelta(days=i)
        curr_str = curr.strftime('%Y-%m-%d')
        with cols[i]:
            st.markdown(f"<div style='background:#1e293b; color:white; padding:12px; border-radius:12px; text-align:center; margin-bottom:15px; font-weight:bold;'>{day}<br>{curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            for t in get_daily_status(curr):
                if t['is_done']: 
                    st.success(f"✅ {t['name']}")
                else:
                    # ה-Key כולל את התאריך והתפקיד למניעת התנגשויות
                    if st.checkbox(f"לבצע: {t['name']}", key=f"chk_{t['id']}_{curr_str}_{st.session_state.user_role}"):
                        idx = t['idx']
                        old = str(st.session_state.df.at[idx, "Done_Dates"]).strip()
                        st.session_state.df.at[idx, "Done_Dates"] = f"{old},{curr_str}".strip(",")
                        save_data(st.session_state.df)
                        st.rerun()

elif choice == OPT_CAL:
    st.title("📅 לוח שנה משימות")
    events = []
    # בניית המשימות לפי תדירויות
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            recurring = row['Recurring']
            for i in range(40): # בונה 40 מופעים קדימה
                gap = 1 if recurring=="יומי" else 7 if recurring=="שבועי" else 14 if recurring=="דו-שבועי" else 30 if recurring=="חודשי" else 0
                d = (base + timedelta(days=i*gap)).strftime("%Y-%m-%d")
                done = d in str(row['Done_Dates'])
                events.append({
                    "title": f"{'✅' if done else '⏳'} {row['Task_Name']}", 
                    "start": d, 
                    "color": "#10b981" if done else "#ef4444"
                })
                if recurring == "לא": break # משימה חד פעמית
        except: continue
    
    # שימוש ב-Key ייחודי למניעת קריסות (תלוי בתפקיד)
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600}, key=f"cal_v_final_{st.session_state.user_role}")

elif choice == OPT_ADD:
    st.title("➕ הוספת משימה חדשה למערכת")
    with st.container():
        st.markdown("<div style='background:white; padding:30px; border-radius:20px; border:1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);'>", unsafe_allow_html=True)
        with st.form("new_task_form"):
            n = st.text_input("שם המשימה", placeholder="לדוגמה: ספירת מלאי שבועית")
            f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
            d = st.date_input("תאריך התחלה", datetime.now())
            ds = st.text_area("תיאור המשימה")
            if st.form_submit_button("שמור משימה במערכת"):
                new_id = int(st.session_state.df["ID"].max()+1) if not st.session_state.df.empty else 1000
                new_row = pd.DataFrame([{"ID":new_id, "Task_Name":n, "Description":ds, "Recurring":f, "Date":d.strftime("%Y-%m-%d"), "Done_Dates":""}])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df); st.success("המשימה נוספה בהצלחה!"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

elif choice == OPT_MANAGE:
    st.title("⚙️ ניהול והגדרות בסיס הנתונים")
    st.info("כאן ניתן לערוך, למחוק או לעדכן את כלל המשימות בקובץ ה-CSV.")
    edited = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic", key="df_editor")
    if st.button("שמור שינויים"):
        st.session_state.df = edited
        save_data(edited); st.success("בסיס הנתונים עודכן!"); st.rerun()
