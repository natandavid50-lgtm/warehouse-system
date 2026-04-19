import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

DB_FILE = "warehouse_db.csv"

# --- פונקציות ניהול נתונים ---
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

if "df" not in st.session_state:
    st.session_state.df = load_data()

# --- תפריט צד והרשאות ---
st.sidebar.title("מערכת ניהול מחסן")
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

OPT_CAL = "📅 לוח שנה אינטראקטיבי"
OPT_MANAGE = "⚙️ ניהול ומחיקה"
OPT_ADD = "➕ הוספת משימה"
OPT_WORK = "📦 סידור עבודה שבועי"
OPT_DASH = "📊 דשבורד מנהלים"

if user_role == "מנהל WMS":
    menu = [OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH]
elif user_role == "צוות מחסן":
    menu = [OPT_WORK, OPT_CAL]
else: # סמנכ"ל
    menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("ניווט:", menu)

# --- לוגיקה לחישוב משימות של יום ספציפי ---
def get_tasks_for_date(target_date):
    scheduled = []
    t_str = target_date.strftime("%Y-%m-%d")
    for _, r in st.session_state.df.iterrows():
        try:
            if not r['Date']: continue
            base = pd.to_datetime(r['Date']).to_pydatetime()
            diff = (target_date - base).days
            if diff < 0: continue
            
            hit = (diff == 0) or (r['Recurring'] == "יומי") or \
                  (r['Recurring'] == "שבועי" and diff % 7 == 0) or \
                  (r['Recurring'] == "דו-שבועי" and diff % 14 == 0) or \
                  (r['Recurring'] == "חודשי" and diff % 30 == 0)
            
            if hit:
                is_done = t_str in str(r['Done_Dates']).split(",")
                scheduled.append({"id": r['ID'], "name": r['Task_Name'], "done": is_done, "row_idx": _})
        except: continue
    return scheduled

# --- 5. דשבורד סמנכ"ל (צפייה בלבד) ---
if choice == OPT_DASH:
    st.header("📊 תמונת מצב ניהולית (סמנכ\"ל)")
    now = datetime.now()
    tasks_today = get_tasks_for_date(now)
    
    done_count = sum(1 for t in tasks_today if t['done'])
    total_count = len(tasks_today)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות להיום", total_count)
    c2.metric("בוצעו בפועל", done_count)
    prog = (done_count / total_count * 100) if total_count > 0 else 0
    c3.metric("אחוז ביצוע", f"{int(prog)}%")
    
    st.divider()
    st.subheader(f"📋 פירוט משימות להיום ({now.strftime('%d/%m/%Y')})")
    if tasks_today:
        for t in tasks_today:
            st.write(f"{'✅' if t['done'] else '⏳'} {t['name']}")
    else:
        st.write("אין משימות מתוכננות להיום.")

# --- 4. סידור עבודה שבועי (ביצוע למנהל WMS בלבד) ---
elif choice == OPT_WORK:
    st.header(OPT_WORK)
    today = datetime.now()
    # התחלת שבוע מיום ראשון הקרוב/הנוכחי
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    
    cols = st.columns(5)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    
    for i, name in enumerate(days_names):
        curr_date = start_of_week + timedelta(days=i)
        t_str = curr_date.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"### יום {name}\n**{curr_date.strftime('%d/%m')}**")
            tasks = get_tasks_for_date(curr_date)
            for t in tasks:
                if t['done']:
                    st.success(f"✅ {t['name']}")
                else:
                    st.write(f"⏳ {t['name']}")
                    if user_role == "מנהל WMS":
                        if st.button("בצע", key=f"btn_{t['id']}_{t_str}"):
                            # עדכון רק של התאריך הספציפי
                            idx = t['row_idx']
                            old_dates = str(st.session_state.df.at[idx, "Done_Dates"])
                            new_dates = f"{old_dates},{t_str}".strip(",")
                            st.session_state.df.at[idx, "Done_Dates"] = new_dates
                            save_data(st.session_state.df)
                            st.rerun()
            st.divider()

# --- 1. לוח שנה ---
elif choice == OPT_CAL:
    st.header(OPT_CAL)
    events = []
    for _, r in st.session_state.df.iterrows():
        try:
            if not r['Date']: continue
            base_date = pd.to_datetime(r['Date']).to_pydatetime()
            done_list = str(r['Done_Dates']).split(",")
            
            # הצגת חודש קדימה
            for d in range(45):
                curr = base_date + timedelta(days=d)
                diff = (curr - base_date).days
                hit = (diff == 0) or (r['Recurring'] == "יומי") or \
                      (r['Recurring'] == "שבועי" and diff % 7 == 0) or \
                      (r['Recurring'] == "דו-שבועי" and diff % 14 == 0) or \
                      (r['Recurring'] == "חודשי" and diff % 30 == 0)
                
                if hit:
                    curr_s = curr.strftime("%Y-%m-%d")
                    is_done = curr_s in done_list
                    events.append({
                        "title": r['Task_Name'], "start": curr_s,
                        "color": "#28a745" if is_done else "#dc3545"
                    })
        except: continue
    calendar(events=events, options={"direction": "rtl", "locale": "he"}, key="cal")

# --- 3. הוספת משימה ---
elif choice == OPT_ADD:
    st.header(OPT_ADD)
    with st.form("add"):
        name = st.text_input("שם המשימה")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        sd = st.date_input("תאריך התחלה", datetime.now())
        if st.form_submit_button("שמור"):
            if name:
                new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 100
                new_row = pd.DataFrame([{"ID": new_id, "Task_Name": name, "Description": "", "Recurring": freq, "Date": sd.strftime("%Y-%m-%d"), "Done_Dates": "", "Final_Approval": "לא"}])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.rerun()

# --- 2. ניהול ומחיקה ---
elif choice == OPT_MANAGE:
    st.header(OPT_MANAGE)
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        to_del = st.selectbox("משימה למחיקה:", st.session_state.df["Task_Name"])
        if st.button("מחק"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != to_del]
            save_data(st.session_state.df)
            st.rerun()
