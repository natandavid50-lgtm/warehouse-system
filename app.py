import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן חכמה", layout="wide")

DB_FILE = "warehouse_management_db.csv"

# --- פונקציות ליבה (נתונים) ---
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
    for idx, row in st.session_state.df.iterrows():
        try:
            if not row['Date']: continue
            base_date = pd.to_datetime(row['Date']).to_pydatetime()
            diff_days = (target_date - base_date).days
            if diff_days >= 0:
                is_hit = False
                if row['Recurring'] == "לא" and diff_days == 0: is_hit = True
                elif row['Recurring'] == "יומי" and diff_days < 200: is_hit = True
                elif row['Recurring'] == "שבועי" and diff_days % 7 == 0 and (diff_days // 7) < 200: is_hit = True
                elif row['Recurring'] == "דו-שבועי" and diff_days % 14 == 0 and (diff_days // 14) < 200: is_hit = True
                elif row['Recurring'] == "חודשי" and diff_days % 30 == 0 and (diff_days // 30) < 200: is_hit = True
                
                if is_hit:
                    done_list = str(row['Done_Dates']).split(",")
                    scheduled.append({"idx": idx, "id": row['ID'], "name": row['Task_Name'], "desc": row['Description'], "is_done": target_str in done_list})
        except: continue
    return scheduled

# --- ניהול התחברות (Login Logic) ---
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# פונקציה להצגת מסך הכניסה
@st.dialog("כניסה למערכת")
def login():
    st.write("ברוך הבא למערכת ניהול המחסן. אנא הזדהה כדי להמשיך:")
    role = st.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
    if st.button("התחבר"):
        st.session_state.user_role = role
        st.rerun()

# הפעלת מסך הכניסה אם המשתמש לא מחובר
if st.session_state.user_role is None:
    login()
    st.warning("אנא בחר משתמש כדי לצפות בנתונים.")
    st.stop() # עוצר את הרצת שאר הקוד עד להתחברות

# --- המשך האפליקציה (רק לאחר התחברות) ---
if "df" not in st.session_state:
    st.session_state.df = load_data()

user_role = st.session_state.user_role

# תפריט צד
st.sidebar.title(f"שלום, {user_role}")
if st.sidebar.button("החלף משתמש/התנתק"):
    st.session_state.user_role = None
    st.rerun()

st.sidebar.divider()

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד מנהלים", "📋 סידור עבודה שבועי", "📅 לוח שנה משימות", "➕ הוספת משימה חדשה", "⚙️ הגדרות ומחיקה"

if user_role == "מנהל WMS":
    menu = [OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH]
elif user_role == "צוות מחסן":
    menu = [OPT_WORK, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("עבור אל:", menu)

# --- תוכן הדפים ---
if choice == OPT_DASH:
    st.header(f"📊 תמונת מצב יומית - {datetime.now().strftime('%d/%m/%Y')}")
    today_tasks = get_daily_status(datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t['is_done'])
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות להיום", total)
    c2.metric("בוצעו בפועל", done)
    pct = (done/total*100) if total > 0 else 0
    c3.metric("אחוז עמידה ביעדים", f"{int(pct)}%")
    st.divider()
    if today_tasks:
        for t in today_tasks: st.write(f"{'✅' if t['is_done'] else '⏳'} **{t['name']}** - {t['desc']}")
    else: st.info("אין משימות מתוכננות להיום.")

elif choice == OPT_WORK:
    st.header("📋 סידור עבודה שבועי")
    start_of_week = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)
    for i, day_label in enumerate(days):
        curr_date = start_of_week + timedelta(days=i)
        date_str = curr_date.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"### {day_label}\n*{curr_date.strftime('%d/%m')}*")
            for t in get_daily_status(curr_date):
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
            st.divider()

elif choice == OPT_CAL:
    st.header("📅 לוח שנה משימות")
    cal_events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base, done_list = pd.to_datetime(row['Date']).to_pydatetime(), str(row['Done_Dates']).split(",")
            num = 200 if row['Recurring'] != "לא" else 1
            gap = 1 if row['Recurring'] == "יומי" else 7 if row['Recurring'] == "שבועי" else 14 if row['Recurring'] == "דו-שבועי" else 30 if row['Recurring'] == "חודשי" else 0
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
        with c2: t_date, t_desc = st.date_input("תאריך התחלה", datetime.now()), st.text_area("תיאור")
        if st.form_submit_button("שמור משימה"):
            if t_name:
                new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 1000
                new_row = pd.DataFrame([{"ID": new_id, "Task_Name": t_name, "Description": t_desc, "Recurring": t_freq, "Date": t_date.strftime("%Y-%m-%d"), "Done_Dates": "", "Final_Approval": "לא"}])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"נשמר: {t_name}")
                st.rerun()

elif choice == OPT_MANAGE:
    st.header("⚙️ ניהול נתונים")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        to_del = st.selectbox("מחיקה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != to_del]
            save_data(st.session_state.df)
            st.rerun()
