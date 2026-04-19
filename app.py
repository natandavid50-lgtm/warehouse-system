import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# 1. הגדרות עמוד
st.set_page_config(page_title="מערכת מחסן - אחים כהן", layout="wide", initial_sidebar_state="expanded")

# 2. עיצוב CSS מתקדם למסך כניסה ולממשק
st.markdown("""
    <style>
    /* עיצוב כפתורי הכניסה כמלבנים צפים */
    .stButton>button {
        height: 220px;
        border-radius: 25px;
        border: 1px solid #f0f2f6;
        background-color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        white-space: pre-line;
    }
    .stButton>button:hover {
        transform: translateY(-15px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12);
    }
    .stButton>button div p {
        font-size: 28px !important;
        font-weight: 800 !important;
    }
    /* צבעים ייחודיים לכל תפקיד */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-top: 10px solid #1E3A8A !important; color: #1E3A8A !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-top: 10px solid #F59E0B !important; color: #F59E0B !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-top: 10px solid #10B981 !important; color: #10B981 !important; }
    
    .card-label { text-align: center; margin-top: 10px; font-size: 18px; font-weight: 600; color: #4B5563; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_management_db.csv"

# 3. פונקציות ניהול נתונים
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
    st.markdown("<p style='text-align: center; font-size: 1.5rem;'>בחר תפקיד לכניסה</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        if st.button("🔑\nמנהל WMS", use_container_width=True):
            st.session_state.user_role = "מנהל WMS"
            st.rerun()
    with c2:
        if st.button("📦\nצוות מחסן", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"
            st.rerun()
    with c3:
        if st.button("📊\nסמנכ\"ל", use_container_width=True):
            st.session_state.user_role = "סמנכ\"ל"
            st.rerun()
    st.stop()

# 5. טעינת נתונים ותפריט צד
if "df" not in st.session_state:
    st.session_state.df = load_data()

user_role = st.session_state.user_role
st.sidebar.markdown(f"### שלום, **{user_role}**")
if st.sidebar.button("התנתקות"):
    st.session_state.user_role = None
    st.rerun()

OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH = "📅 לוח שנה", "📋 סידור עבודה", "➕ הוספת משימה", "⚙️ הגדרות", "📊 דשבורד בקרה"

if user_role == "מנהל WMS": menu = [OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH]
elif user_role == "צוות מחסן": menu = [OPT_WORK, OPT_CAL]
else: menu = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("ניווט במערכת:", menu)

# 6. דפי המערכת
if choice == OPT_DASH:
    st.header("📊 דשבורד בקרה")
    today_tasks = get_daily_status(datetime.now())
    total, done = len(today_tasks), sum(1 for t in today_tasks if t['is_done'])
    c1, c2, c3 = st.columns(3)
    c1.metric("משימות להיום", total)
    c2.metric("בוצעו", done)
    pct = (done/total*100) if total > 0 else 0
    c3.metric("אחוז ביצוע", f"{int(pct)}%")
    st.divider()
    for t in today_tasks:
        st.write(f"{'✅' if t['is_done'] else '⏳'} **{t['name']}** - {t['desc']}")

elif choice == OPT_WORK:
    st.header("📋 סידור עבודה שבועי")
    start = datetime.now() - timedelta(days=(datetime.now().weekday() + 1) % 7)
    cols = st.columns(5)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    for i, day_label in enumerate(days):
        curr_date = start + timedelta(days=i)
        date_str = curr_date.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"### {day_label}\n*{curr_date.strftime('%d/%m')}*")
            for t in get_daily_status(curr_date):
                if t['is_done']: st.success(f"**{t['name']}**")
                else:
                    st.warning(f"**{t['name']}**")
                    if user_role == "מנהל WMS":
                        if st.button("בצע", key=f"btn_{t['id']}_{date_str}"):
                            idx = t['idx']
                            old_val = str(st.session_state.df.at[idx, "Done_Dates"])
                            st.session_state.df.at[idx, "Done_Dates"] = f"{old_val},{date_str}".strip(",")
                            save_data(st.session_state.df)
                            st.rerun()

elif choice == OPT_CAL:
    st.header("📅 לוח שנה משימות")
    cal_events = []
    for _, row in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(row['Date']).to_pydatetime()
            done_list = str(row['Done_Dates']).split(",")
            f = row['Recurring']
            num = 200 if f != "לא" else 1
            gap = 1 if f=="יומי" else 7 if f=="שבועי" else 14 if f=="דו-שבועי" else 30 if f=="חודשי" else 0
            for i in range(num):
                curr = base + timedelta(days=i * gap)
                c_str = curr.strftime("%Y-%m-%d")
                cal_events.append({"title": row['Task_Name'], "start": c_str, "color": "#28a745" if c_str in done_list else "#dc3545", "allDay": True})
        except: continue
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 650})

elif choice == OPT_ADD:
    st.header("➕ הוספת משימה חדשה")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: t_name, t_freq = st.text_input("שם המשימה"), st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        with c2: t_date, t_desc = st.date_input("תאריך התחלה"), st.text_area("תיאור המשימה")
        if st.form_submit_button("שמור משימה"):
            if t_name:
                new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 1000
                new_row = pd.DataFrame([{"ID": new_id, "Task_Name": t_name, "Description": t_desc, "Recurring": t_freq, "Date": t_date.strftime("%Y-%m-%d"), "Done_Dates": "", "Final_Approval": "לא"}])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.success("המשימה נוספה!")
                st.rerun()

elif choice == OPT_MANAGE:
    st.header("⚙️ הגדרות")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        to_del = st.selectbox("מחיקת משימה:", st.session_state.df["Task_Name"].unique())
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != to_del]
            save_data(st.session_state.df)
            st.rerun()
