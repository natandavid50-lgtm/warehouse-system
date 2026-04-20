import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="אחים כהן - ניהול מחסן", layout="wide", initial_sidebar_state="expanded")

# 2. הזרקת CSS - שדרוג ויזואלי
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
    }

    .stApp { background-color: #f1f5f9; }

    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    section[data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    .task-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 12px;
        border-right: 8px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    .day-header {
        background: #1e293b;
        color: #f8fafc;
        padding: 10px;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        margin-bottom: 15px;
    }

    /* מסגרת יפה ללוח השנה */
    .cal-container {
        background: white;
        padding: 20px;
        border-radius: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. פונקציות ליבה
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

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# --- מסך כניסה ---
if st.session_state.user_role is None:
    st.markdown("<br><br><h1 style='text-align: center;'>אחים כהן - ניהול משימות</h1>", unsafe_allow_html=True)
    cols = st.columns(3)
    roles = [("מנהל WMS", "🔑"), ("צוות מחסן", "📦"), ("סמנכ\"ל", "📈")]
    for i, (role, icon) in enumerate(roles):
        with cols[i]:
            if st.button(f"{icon} {role}", use_container_width=True):
                st.session_state.user_role = role
                st.rerun()
    st.stop()

# --- תפריט ---
menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE] if st.session_state.user_role == "מנהל WMS" else [OPT_WORK, OPT_CAL]
with st.sidebar:
    st.markdown(f"### {st.session_state.user_role}")
    choice = st.radio("ניווט", menu)
    if st.button("🚪 התנתקות"):
        st.session_state.user_role = None
        st.rerun()

# --- דפים ---
if choice == OPT_DASH:
    st.title(OPT_DASH)
    tasks = get_daily_status(datetime.now())
    c1, c2 = st.columns(2)
    c1.metric("משימות להיום", len(tasks))
    c2.metric("בוצעו", sum(1 for t in tasks if t['is_done']))
    for t in tasks:
        color = "#10b981" if t['is_done'] else "#f59e0b"
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><b>{t["name"]}</b></div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.title(OPT_WORK)
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    cols = st.columns(5)
    for i, day in enumerate(["ראשון", "שני", "שלישי", "רביעי", "חמישי"]):
        curr = start + timedelta(days=i)
        curr_str = curr.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"<div class='day-header'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            for t in get_daily_status(curr):
                if t['is_done']: st.success(f"✅ {t['name']}")
                else:
                    if st.checkbox(f"{t['name']}", key=f"chk_{t['id']}_{curr_str}"):
                        st.session_state.df.at[t['idx'], "Done_Dates"] = f"{str(st.session_state.df.at[t['idx'], 'Done_Dates'])},{curr_str}".strip(",")
                        save_data(st.session_state.df)
                        st.rerun()

elif choice == OPT_CAL:
    st.markdown("<h1 style='color: #0f172a;'>📅 יומן משימות מלא</h1>", unsafe_allow_html=True)
    events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            num = 1 if row['Recurring'] == "לא" else 30
            gap = {"יומי":1, "שבועי":7, "דו-שבועי":14, "חודשי":30}.get(row['Recurring'], 0)
            for i in range(num):
                d = (base + timedelta(days=i * gap)).strftime("%Y-%m-%d")
                done = d in str(row['Done_Dates'])
                events.append({"title": f"{'✅' if done else '⏳'} {row['Task_Name']}", "start": d, "color": "#10b981" if done else "#3b82f6"})
        except: continue
    
    # הצגת הלוח בתוך Container מעוצב ובגובה מתאים לעמוד (600px)
    st.markdown('<div class="cal-container">', unsafe_allow_html=True)
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600}, key="cal_full_v2")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == OPT_ADD:
    st.title(OPT_ADD)
    with st.form("add"):
        name = st.text_input("שם המשימה")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        date = st.date_input("תאריך התחלה", datetime.now())
        if st.form_submit_button("הוסף משימה"):
            new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 1000
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":name, "Recurring":freq, "Date":date.strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df)
            st.success("נוסף בהצלחה!")
            st.rerun()

elif choice == OPT_MANAGE:
    st.title("⚙️ ניהול ועריכת משימות")
    if st.session_state.df.empty:
        st.info("אין משימות.")
    else:
        task_list = st.session_state.df['Task_Name'].tolist()
        task_to_edit = st.selectbox("בחר משימה לניהול", task_list)
        idx = st.session_state.df[st.session_state.df['Task_Name'] == task_to_edit].index[0]
        row = st.session_state.df.loc[idx]

        with st.container():
            col1, col2 = st.columns(2)
            u_name = col1.text_input("שם המשימה", value=row['Task_Name'])
            u_freq = col2.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"], index=["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"].index(row['Recurring']))
            u_date = col1.date_input("תאריך התחלה", value=pd.to_datetime(row['Date']))
            
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("✅ שמור שינויים", use_container_width=True):
                st.session_state.df.at[idx, 'Task_Name'] = u_name
                st.session_state.df.at[idx, 'Recurring'] = u_freq
                st.session_state.df.at[idx, 'Date'] = u_date.strftime("%Y-%m-%d")
                save_data(st.session_state.df)
                st.success("עודכן!")
                st.rerun()
            
            if c_btn2.button("🗑️ מחק משימה", use_container_width=True):
                st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
                save_data(st.session_state.df)
                st.warning("נמחק!")
                st.rerun()
