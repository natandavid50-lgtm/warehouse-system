import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת מחסן - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב CSS משודרג - מראה נקי ומקצועי
st.markdown("""
    <style>
    /* הגדרות כלליות */
    .main { background-color: #f8f9fa; }
    div[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    
    /* עיצוב כפתורי הכניסה - מלבנים צפים ומודרניים */
    .stButton>button {
        height: 180px;
        border-radius: 20px;
        border: none;
        background-color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        background-color: #fcfcfc;
    }
    
    /* כותרות בתוך כפתורי הכניסה */
    .stButton>button p {
        font-size: 24px !important;
        font-weight: 700 !important;
        margin-top: 10px;
    }

    /* עיצוב כרטיסיות (Containers) */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        border-bottom: 4px solid #1E3A8A;
    }
    
    /* שיפור תצוגת הטקסט */
    h1, h2, h3 { color: #1E3A8A; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* צבעים ייחודיים לכפתורי הכניסה לפי תפקיד */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 8px solid #1E3A8A !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 8px solid #F59E0B !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 8px solid #10B981 !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

# 3. פונקציות ניהול נתונים (נשאר ללא שינוי לוגי)
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

# 4. ניהול כניסה למערכת
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown("<br><br><h1 style='text-align: center;'>מערכת המחסן - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>ברוך הבא! אנא בחר את התפקיד שלך לכניסה למערכת</p>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        if st.button("🔑\nמנהל WMS", key="btn_admin"):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
    with c2:
        if st.button("📦\nצוות מחסן", key="btn_staff"):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
    with c3:
        if st.button("📊\nסמנכ\"ל", key="btn_vp"):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
    st.stop()

# 5. טעינת נתונים ותפריט צד
if "df" not in st.session_state:
    st.session_state.df = load_data()

user_role = st.session_state.user_role
with st.sidebar:
    st.markdown(f"### שלום, 👋\n**{user_role}**")
    st.divider()
    
    OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH = "📅 לוח שנה", "📋 סידור עבודה", "➕ הוספת משימה", "⚙️ הגדרות", "📊 דשבורד בקרה"
    
    if user_role == "מנהל WMS": menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
    elif user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
    else: menu = [OPT_DASH, OPT_CAL]
    
    choice = st.radio("ניווט במערכת:", menu)
    
    st.spacer = st.write("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 התנתקות מהמערכת", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()

# 6. דפי המערכת
if choice == OPT_DASH:
    st.header("📊 דשבורד בקרה וביצועים")
    today_tasks = get_daily_status(datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t['is_done'])
    
    # הצגת מטריקות בתוך קונטיינר מעוצב
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("משימות להיום", total)
    with m2:
        st.metric("בוצעו", done, delta=f"{done}" if done > 0 else None)
    with m3:
        pct = (done/total*100) if total > 0 else 0
        st.metric("אחוז ביצוע", f"{int(pct)}%")
        st.progress(pct/100)
    
    st.divider()
    
    tab1, tab2 = st.tabs(["📝 פירוט משימות להיום", "📈 ניתוח נתונים"])
    with tab1:
        if not today_tasks:
            st.info("אין משימות מתוזמנות להיום.")
        else:
            for t in today_tasks:
                with st.expander(f"{'✅' if t['is_done'] else '⏳'} {t['name']}"):
                    st.write(f"**תיאור:** {t['desc']}")
                    st.write(f"**סטטוס:** {'בוצע' if t['is_done'] else 'ממתין לביצוע'}")

elif choice == OPT_WORK:
    st.header("📋 סידור עבודה שבועי")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    
    # תצוגה לפי ימי השבוע בעמודות רחבות
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(len(days))
    
    for i, day_label in enumerate(days):
        curr_date = start + timedelta(days=i)
        date_str = curr_date.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"<div style='text-align: center; background: #1E3A8A; color: white; padding: 5px; border-radius: 10px 10px 0 0;'>{day_label}<br>{curr_date.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            tasks = get_daily_status(curr_date)
            if not tasks:
                st.write("<p style='color: gray; text-align: center;'>אין משימות</p>", unsafe_allow_html=True)
            for t in tasks:
                with st.container():
                    if t['is_done']:
                        st.success(f"**{t['name']}**")
                    else:
                        st.warning(f"**{t['name']}**")
                        if user_role in ["מנהל WMS", "צוות מחסן"]:
                            if st.button("סמן כבוצע", key=f"btn_{t['id']}_{date_str}", use_container_width=True):
                                idx = t['idx']
                                old_val = str(st.session_state.df.at[idx, "Done_Dates"])
                                st.session_state.df.at[idx, "Done_Dates"] = f"{old_val},{date_str}".strip(",")
                                save_data(st.session_state.df)
                                st.toast(f"משימה '{t['name']}' סומנה כבוצעה!")
                                st.rerun()

elif choice == OPT_CAL:
    st.header("📅 לוח שנה משימות")
    cal_events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date']).to_pydatetime()
            done_list = str(row['Done_Dates']).split(",")
            f = row['Recurring']
            num = 150 if f != "לא" else 1
            gap = 1 if f=="יומי" else 7 if f=="שבועי" else 14 if f=="דו-שבועי" else 30 if f=="חודשי" else 0
            for i in range(num):
                curr = base + timedelta(days=i * gap)
                c_str = curr.strftime("%Y-%m-%d")
                cal_events.append({
                    "title": row['Task_Name'], 
                    "start": c_str, 
                    "color": "#10B981" if c_str in done_list else "#EF4444", 
                    "allDay": True
                })
        except: continue
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 650})

elif choice == OPT_ADD:
    st.header("➕ הוספת משימה חדשה")
    with st.container():
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                t_name = st.text_input("שם המשימה", placeholder="למשל: ספירת מלאי מדף A")
                t_freq = st.selectbox("תדירות חזרה", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
            with c2:
                t_date = st.date_input("תאריך התחלה", datetime.now())
                t_desc = st.text_area("תיאור המשימה", placeholder="פרט כאן מה נדרש לבצע...")
            
            st.write("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("💾 שמור משימה במערכת", use_container_width=True)
            
            if submit:
                if t_name:
                    new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 1000
                    new_row = pd.DataFrame([{
                        "ID": new_id, "Task_Name": t_name, "Description": t_desc, 
                        "Recurring": t_freq, "Date": t_date.strftime("%Y-%m-%d"), 
                        "Done_Dates": "", "Final_Approval": "לא"
                    }])
                    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                    save_data(st.session_state.df)
                    st.success(f"המשימה '{t_name}' נוספה בהצלחה!")
                else:
                    st.error("חובה להזין שם משימה.")

elif choice == OPT_MANAGE:
    st.header("⚙️ ניהול והגדרות מערכת")
    
    with st.expander("👀 צפייה בבסיס הנתונים הגולמי"):
        st.dataframe(st.session_state.df, use_container_width=True)
    
    st.subheader("🗑️ מחיקת משימות")
    if not st.session_state.df.empty:
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            to_del = st.selectbox("בחר משימה להסרה:", st.session_state.df["Task_Name"].unique())
        with col_del2:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("מחק משימה", use_container_width=True, type="primary"):
                st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != to_del]
                save_data(st.session_state.df)
                st.rerun()
    else:
        st.info("אין משימות רשומות במערכת.")
