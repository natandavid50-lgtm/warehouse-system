import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="אחים כהן - ניהול מחסן", layout="wide", initial_sidebar_state="expanded")

# 2. הזרקת CSS - שדרוג ויזואלי למסך הכניסה ושאר המערכת
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
    }

    .stApp { background-color: #f1f5f9; }

    /* עיצוב כרטיסי הכניסה */
    .login-container {
        display: flex;
        justify-content: center;
        gap: 30px;
        padding-top: 50px;
    }

    /* הגדרת כפתור Streamlit ככרטיס צף */
    div.stButton > button {
        height: 280px;
        width: 100%;
        background-color: white !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 24px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease-in-out !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    div.stButton > button:hover {
        transform: translateY(-10px) !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
    }

    /* אייקונים גדולים בתוך הכפתורים */
    .role-icon {
        font-size: 60px;
        margin-bottom: 20px;
        display: block;
    }

    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    section[data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    .task-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 12px;
        border-right: 8px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    .cal-container {
        background: white;
        padding: 20px;
        border-radius: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. פונקציות ליבה (ללא שינוי)
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

if "user_role" not in st.session_state: st.session_state.user_role = None
if "df" not in st.session_state: st.session_state.df = load_data()

OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE = "📊 דשבורד בקרה", "📋 סידור עבודה", "📅 לוח שנה", "➕ הוספת משימה", "⚙️ הגדרות"

# --- מסך כניסה מעוצב מחדש ---
if st.session_state.user_role is None:
    st.markdown("<br><br><h1 style='text-align: center; color: #1e293b; font-size: 45px;'>אחים כהן - ניהול משימות מחסן</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 20px;'>בחר תפקיד כדי להתחבר למערכת</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # שימוש בטורים ליצירת הכרטיסים הצפים
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔑\n\nמנהל WMS", use_container_width=True):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
            
    with col2:
        if st.button("📦\n\nצוות מחסן", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
            
    with col3:
        if st.button("📈\n\nסמנכ\"ל", use_container_width=True):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
    st.stop()

# --- שאר הקוד (ללא שינוי פונקציונלי) ---
if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "סמנכ\"ל":
    menu = [OPT_DASH, OPT_CAL]
else:
    menu = [OPT_WORK, OPT_CAL]

with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.user_role} 👋")
    choice = st.radio("תפריט ניווט:", menu)
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 התנתקות מהמערכת", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()

# לוגיקת הדפים נשארת כפי שהייתה בקוד הקודם שלך
if choice == OPT_DASH:
    st.markdown("<h1 style='color: #0f172a;'>📊 דשבורד סטטוס</h1>", unsafe_allow_html=True)
    tasks = get_daily_status(datetime.now())
    t_count = len(tasks)
    d_count = sum(1 for t in tasks if t['is_done'])
    perc = int(d_count/t_count*100) if t_count > 0 else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות היום", t_count)
    c2.metric("בוצעו", d_count)
    c3.metric("אחוז ביצוע", f"{perc}%")
    st.markdown("---")
    for t in tasks:
        color = "#10b981" if t['is_done'] else "#f59e0b"
        st.markdown(f'<div class="task-card" style="border-right-color: {color}"><b>{t["name"]}</b><br><small>{t["desc"]}</small></div>', unsafe_allow_html=True)

elif choice == OPT_WORK:
    st.markdown("<h1 style='color: #0f172a;'>📋 סידור עבודה שבועי</h1>", unsafe_allow_html=True)
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    cols = st.columns(5)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    for i, day in enumerate(days_names):
        curr = start + timedelta(days=i)
        curr_str = curr.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"<div class='day-header'>{day} {curr.strftime('%d/%m')}</div>", unsafe_allow_html=True)
            day_tasks = get_daily_status(curr)
            for t in day_tasks:
                if t['is_done']:
                    st.markdown(f"<div style='background:#dcfce7; color:#166534; padding:10px; border-radius:10px; margin-bottom:5px;'>✅ {t['name']}</div>", unsafe_allow_html=True)
                else:
                    if st.checkbox(f"בצע: {t['name']}", key=f"chk_{t['id']}_{curr_str}"):
                        current_done = str(st.session_state.df.at[t['idx'], "Done_Dates"])
                        new_done = f"{current_done},{curr_str}".strip(",")
                        st.session_state.df.at[t['idx'], "Done_Dates"] = new_done
                        save_data(st.session_state.df)
                        st.rerun()

elif choice == OPT_CAL:
    st.markdown("<h1 style='color: #0f172a;'>📅 לוח שנה</h1>", unsafe_allow_html=True)
    events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date'])
            for i in range(30):
                gap = {"יומי":1, "שבועי":7, "דו-שבועי":14, "חודשי":30}.get(row['Recurring'], 0)
                if row['Recurring'] == "לא" and i > 0: break
                d = (base + timedelta(days=i * gap)).strftime("%Y-%m-%d")
                done = d in str(row['Done_Dates'])
                events.append({"title": f"{'✅' if done else '⏳'} {row['Task_Name']}", "start": d, "color": "#10b981" if done else "#3b82f6"})
        except: continue
    st.markdown('<div class="cal-container">', unsafe_allow_html=True)
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600}, key="cal_main")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == OPT_ADD:
    st.title(OPT_ADD)
    with st.form("add_form"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        date = st.date_input("תאריך התחלה", datetime.now())
        if st.form_submit_button("שמור משימה"):
            new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 100
            new_row = pd.DataFrame([{"ID":new_id, "Task_Name":name, "Description":desc, "Recurring":freq, "Date":date.strftime("%Y-%m-%d"), "Done_Dates":""}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df)
            st.success("המשימה התווספה!")
            st.rerun()

elif choice == OPT_MANAGE:
    st.title("⚙️ הגדרות ניהול")
    if not st.session_state.df.empty:
        task_list = st.session_state.df['Task_Name'].tolist()
        task_to_edit = st.selectbox("בחר משימה לעריכה/מחיקה", task_list)
        idx = st.session_state.df[st.session_state.df['Task_Name'] == task_to_edit].index[0]
        
        col1, col2 = st.columns(2)
        new_n = col1.text_input("שם חדש", value=st.session_state.df.at[idx, 'Task_Name'])
        new_f = col2.selectbox("תדירות חדשה", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"], 
                               index=["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"].index(st.session_state.df.at[idx, 'Recurring']))
        
        b1, b2 = st.columns(2)
        if b1.button("✅ שמור שינויים", use_container_width=True):
            st.session_state.df.at[idx, 'Task_Name'] = new_n
            st.session_state.df.at[idx, 'Recurring'] = new_f
            save_data(st.session_state.df)
            st.success("עודכן!")
            st.rerun()
        if b2.button("🗑️ מחק משימה", use_container_width=True):
            st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
            save_data(st.session_state.df)
            st.warning("נמחק!")
            st.rerun()
