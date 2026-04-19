import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# הגדרות עמוד
st.set_page_config(page_title="מערכת מחסן - אחים כהן", layout="wide")

# --- עיצוב CSS למלבנים צפים ---
st.markdown("""
    <style>
    .stButton>button {
        height: 150px;
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        background-color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
    }
    .stButton>button:hover {
        transform: translateY(-10px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.15);
        border-color: #1E3A8A;
        color: #ff4b4b;
    }
    .card-label {
        text-align: center;
        margin-top: -20px;
        font-size: 14px;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

# --- פונקציות ליבה ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            data = pd.read_csv(DB_FILE)
            required_cols = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"]
            for col in required_cols:
                if col not in data.columns: data[col] = ""
            return data.fillna("")
        except:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])

def save_data(df_to_save):
    df_to_save.to_csv(DB_FILE, index=False)

def get_daily_status(target_date):
    scheduled = []
    target_str = target_date.strftime("%Y-%m-%d")
    # הגנה מפני DataFrame ריק או שגיאות Key
    if st.session_state.df.empty: return []
    
    for idx, row in st.session_state.df.iterrows():
        try:
            if not row.get('Date'): continue
            base_date = pd.to_datetime(row['Date']).to_pydatetime()
            diff_days = (target_date - base_date).days
            if diff_days >= 0:
                is_hit = False
                freq = row.get('Recurring', 'לא')
                if freq == "לא" and diff_days == 0: is_hit = True
                elif freq == "יומי" and diff_days < 200: is_hit = True
                elif freq == "שבועי" and diff_days % 7 == 0: is_hit = True
                elif freq == "דו-שבועי" and diff_days % 14 == 0: is_hit = True
                elif freq == "חודשי" and diff_days % 30 == 0: is_hit = True
                
                if is_hit:
                    done_dates = str(row.get('Done_Dates', ""))
                    scheduled.append({
                        "idx": idx, "id": row['ID'], "name": row['Task_Name'], 
                        "desc": row['Description'], "is_done": target_str in done_dates.split(",")
                    })
        except: continue
    return scheduled

# --- מסך כניסה מעוצב (אחים כהן) ---
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if st.session_state.user_role is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-family: sans-serif;'>ברוכים הבאים למערכת המחסן - אחים כהן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 1.2em;'>אנא בחר את התפקיד שלך לכניסה למערכת</p>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        if st.button("🔑\n\nמנהל WMS", use_container_width=True):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
        st.markdown("<p class='card-label'>ניהול משימות, ביצוע והגדרות</p>", unsafe_allow_html=True)

    with col2:
        if st.button("📦\n\nצוות מחסן", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
        st.markdown("<p class='card-label'>צפייה בסידור עבודה וביצוע</p>", unsafe_allow_html=True)

    with col3:
        if st.button("📊\n\nסמנכ\"ל", use_container_width=True):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
        st.markdown("<p class='card-label'>דשבורד בקרה וסטטיסטיקה</p>", unsafe_allow_html=True)

    st.stop()

# --- המשך האפליקציה ---
if "df" not in st.session_state:
    st.session_state.df = load_data()

user_role = st.session_state.user_role
st.sidebar.subheader(f"👤 משתמש: {user_role}")
if st.sidebar.button("התנתק / החלף משתמש"):
    st.session_state.user_role = None
    st.rerun()

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד מנהלים", "📋 סידור עבודה שבועי", "📅 לוח שנה משימות", "➕ הוספת משימה", "⚙️ הגדרות"

if user_role == "מנהל WMS":
    menu = [OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH]
elif user_role == "צוות מחסן":
    menu = [OPT_WORK, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("ניווט:", menu)

# --- טיפול ב-KeyError ובסטטיסטיקה (תיקון לפי התמונה ששלחת) ---
if choice == OPT_DASH:
    st.header("📊 דשבורד בקרה לסמנכ\"ל")
    today_tasks = get_daily_status(datetime.now())
    total = len(today_tasks)
    done = sum(1 for t in today_tasks if t['is_done'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות להיום", total)
    c2.metric("בוצעו היום", done)
    pct = (done/total*100) if total > 0 else 0
    c3.metric("עמידה ביעדים", f"{int(pct)}%")
    
    st.divider()
    if today_tasks:
        st.subheader(f"✅ משימות להיום ({datetime.now().strftime('%d/%m/%Y')}):")
        for t in today_tasks:
            st.write(f"- **{t['name']}**: {'בוצע ✅' if t['is_done'] else 'ממתין ⏳'}")
    else:
        st.info("אין משימות להיום.")

elif choice == OPT_WORK:
    st.header("📋 סידור עבודה שבועי")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)
    for i, day_label in enumerate(days):
        curr_date = start + timedelta(days=i)
        date_str = curr_date.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"### {day_label}\n*{curr_date.strftime('%d/%m')}*")
            tasks = get_daily_status(curr_date)
            for t in tasks:
                if t['is_done']: st.success(f"**{t['name']}**")
                else:
                    st.warning(f"**{t['name']}**")
                    if user_role == "מנהל WMS":
                        if st.button("בצע", key=f"b_{t['id']}_{date_str}"):
                            idx = t['idx']
                            old = str(st.session_state.df.at[idx, "Done_Dates"])
                            st.session_state.df.at[idx, "Done_Dates"] = f"{old},{date_str}".strip(",")
                            save_data(st.session_state.df)
                            st.rerun()

elif choice == OPT_CAL:
    st.header("📅 לוח שנה אינטראקטיבי")
    cal_events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date']).to_pydatetime()
            done_list = str(row['Done_Dates']).split(",")
            freq = row['Recurring']
            num = 200 if freq != "לא" else 1
            gap = 1 if freq == "יומי" else 7 if freq == "שבועי" else 14 if freq == "דו-שבועי" else 30 if freq == "חודשי" else 0
            for i in range(num):
                curr = base + timedelta(days=i * gap)
                c_str = curr.strftime("%Y-%m-%d")
                cal_events.append({"title": row['Task_Name'], "start": c_str, "color": "#28a745" if c_str in done_list else "#dc3545", "allDay": True})
        except: continue
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 650}, key="fixed_cal")

elif choice == OPT_ADD:
    st.header("➕ הוספת משימה חדשה")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: t_name, t_freq = st.text_input("שם המשימה"), st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        with c2: t_date, t_desc = st.date_input("תאריך התחלה"), st.text_area("תיאור")
        if st.form_submit_button("שמור"):
            if t_name:
                new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 1000
                new_row = pd.DataFrame([{"ID": new_id, "Task_Name": t_name, "Description": t_desc, "Recurring": t_freq, "Date": t_date.strftime("%Y-%m-%d"), "Done_Dates": "", "Final_Approval": "לא"}])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.success("נשמר!")
                st.rerun()

elif choice == OPT_MANAGE:
    st.header("⚙️ הגדרות מערכת")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        to_del = st.selectbox("בחר משימה למחיקה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != to_del]
            save_data(st.session_state.df)
            st.rerun()
