import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# הגדרות עמוד רחבות למערכת מקצועית
st.set_page_config(page_title="מערכת ניהול מחסן חכמה", layout="wide", initial_sidebar_state="expanded")

# --- הגדרות קובץ נתונים מקומי ---
DB_FILE = "warehouse_management_db.csv"

def load_data():
    """טוען את הנתונים מהקובץ המקומי ומוודא שכל העמודות קיימות"""
    if os.path.exists(DB_FILE):
        try:
            data = pd.read_csv(DB_FILE)
            required_cols = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"]
            for col in required_cols:
                if col not in data.columns:
                    data[col] = ""
            return data.fillna("")
        except:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])
    return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])

def save_data(df_to_save):
    """שומר את הנתונים פיזית לדיסק"""
    df_to_save.to_csv(DB_FILE, index=False)

# אתחול הנתונים ב-Session State
if "df" not in st.session_state:
    st.session_state.df = load_data()

# --- לוגיקת עזר לחישוב משימות לפי תאריך (תומך ב-200 מופעים) ---
def get_daily_status(target_date):
    """מחשב אילו משימות חלות בתאריך מסוים לפי התדירות שלהן"""
    scheduled = []
    target_str = target_date.strftime("%Y-%m-%d")
    
    for idx, row in st.session_state.df.iterrows():
        try:
            if not row['Date']: continue
            base_date = pd.to_datetime(row['Date']).to_pydatetime()
            diff_days = (target_date - base_date).days
            
            if diff_days >= 0:
                is_hit = False
                # בדיקה אם המשימה היא אחת מ-200 המופעים הראשונים
                if row['Recurring'] == "לא" and diff_days == 0:
                    is_hit = True
                elif row['Recurring'] == "יומי" and diff_days < 200:
                    is_hit = True
                elif row['Recurring'] == "שבועי" and diff_days % 7 == 0 and (diff_days // 7) < 200:
                    is_hit = True
                elif row['Recurring'] == "דו-שבועי" and diff_days % 14 == 0 and (diff_days // 14) < 200:
                    is_hit = True
                elif row['Recurring'] == "חודשי" and diff_days % 30 == 0 and (diff_days // 30) < 200:
                    is_hit = True
                
                if is_hit:
                    done_list = str(row['Done_Dates']).split(",")
                    scheduled.append({
                        "idx": idx,
                        "id": row['ID'],
                        "name": row['Task_Name'],
                        "desc": row['Description'],
                        "is_done": target_str in done_list
                    })
        except:
            continue
    return scheduled

# --- תפריט צד (Sidebar) ---
st.sidebar.title("📦 ניהול לוגיסטי")
user_role = st.sidebar.selectbox("זהות משתמש:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

OPT_DASH = "📊 דשבורד מנהלים"
OPT_WORK = "📋 סידור עבודה שבועי"
OPT_CAL = "📅 לוח שנה משימות"
OPT_ADD = "➕ הוספת משימה חדשה"
OPT_MANAGE = "⚙️ הגדרות ומחיקה"

if user_role == "מנהל WMS":
    menu = [OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH]
elif user_role == "צוות מחסן":
    menu = [OPT_WORK, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("עבור אל:", menu)

# --- 1. דשבורד מנהלים ---
if choice == OPT_DASH:
    st.header(f"📊 תמונת מצב יומית - {datetime.now().strftime('%d/%m/%Y')}")
    today_tasks = get_daily_status(datetime.now())
    total = len(today_tasks)
    done = sum(1 for t in today_tasks if t['is_done'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("משימות להיום", total)
    col2.metric("בוצעו בפועל", done)
    pct = (done / total * 100) if total > 0 else 0
    col3.metric("אחוז עמידה ביעדים", f"{int(pct)}%")
    
    st.divider()
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("📝 פירוט משימות היום")
        if today_tasks:
            for t in today_tasks:
                st.write(f"{'✅' if t['is_done'] else '⏳'} **{t['name']}** - {t['desc']}")
        else:
            st.info("אין משימות מתוכננות להיום.")

# --- 2. סידור עבודה שבועי ---
elif choice == OPT_WORK:
    st.header("📋 סידור עבודה שבועי (ראשון - חמישי)")
    dt = datetime.now()
    start_of_week = dt - timedelta(days=(dt.weekday() + 1) % 7)
    
    days_labels = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)
    
    for i, day_label in enumerate(days_labels):
        current_date = start_of_week + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"### {day_label}\n*{current_date.strftime('%d/%m')}*")
            day_tasks = get_daily_status(current_date)
            for t in day_tasks:
                if t['is_done']:
                    st.success(f"**{t['name']}**\n(בוצע)")
                else:
                    st.warning(f"**{t['name']}**")
                    if user_role == "מנהל WMS":
                        if st.button("סמן ביצוע", key=f"btn_{t['id']}_{date_str}"):
                            idx = t['idx']
                            current_val = str(st.session_state.df.at[idx, "Done_Dates"])
                            new_val = f"{current_val},{date_str}".strip(",")
                            st.session_state.df.at[idx, "Done_Dates"] = new_val
                            save_data(st.session_state.df)
                            st.rerun()
            st.divider()

# --- 3. לוח שנה (מותאם לעמוד + 200 מופעים) ---
elif choice == OPT_CAL:
    st.header("📅 לוח שנה משימות")
    cal_events = []
    
    for _, row in st.session_state.df.iterrows():
        try:
            if not row['Date']: continue
            base = pd.to_datetime(row['Date']).to_pydatetime()
            done_list = str(row['Done_Dates']).split(",")
            
            # הגדרה ל-200 מופעים חוזרים
            num_instances = 200 if row['Recurring'] != "לא" else 1
            gap = 1 if row['Recurring'] == "יומי" else 7 if row['Recurring'] == "שבועי" else 14 if row['Recurring'] == "דו-שבועי" else 30 if row['Recurring'] == "חודשי" else 0
            
            for i in range(num_instances):
                curr = base + timedelta(days=i * gap)
                c_str = curr.strftime("%Y-%m-%d")
                cal_events.append({
                    "title": row['Task_Name'],
                    "start": c_str,
                    "color": "#28a745" if c_str in done_list else "#dc3545",
                    "allDay": True
                })
        except: continue
    
    # הגדרת height מגבילה את הלוח שלא יגדל מדי
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 650}, key="fixed_cal")

# --- 4. הוספת משימה חדשה ---
elif choice == OPT_ADD:
    st.header("➕ הוספת משימה חדשה")
    with st.form("new_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_name = st.text_input("שם המשימה")
            t_freq = st.selectbox("תדירות (תיצור 200 מופעים)", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        with col2:
            t_date = st.date_input("תאריך התחלה", datetime.now())
        
        t_desc = st.text_area("תיאור המשימה")
        
        if st.form_submit_button("שמור משימה"):
            if t_name:
                new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 1000
                new_entry = pd.DataFrame([{
                    "ID": new_id, "Task_Name": t_name, "Description": t_desc,
                    "Recurring": t_freq, "Date": t_date.strftime("%Y-%m-%d"),
                    "Done_Dates": "", "Final_Approval": "לא"
                }])
                st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"המשימה '{t_name}' נוספה עם תדירות {t_freq}")
                st.rerun()

# --- 5. הגדרות ומחיקה ---
elif choice == OPT_MANAGE:
    st.header("⚙️ ניהול נתונים")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        task_to_del = st.selectbox("מחיקת משימה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != task_to_del]
            save_data(st.session_state.df)
            st.rerun()
