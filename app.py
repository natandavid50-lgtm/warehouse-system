import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

DB_FILE = "warehouse_db.csv"

# --- ניהול נתונים ---
def load_data():
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
    df_to_save.to_csv(DB_FILE, index=False)

if "df" not in st.session_state:
    st.session_state.df = load_data()

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

# --- תפריט צד ---
st.sidebar.title("מערכת ניהול מחסן")
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

# הגדרת שמות האופציות (קבוע כדי למנוע שגיאות הקלדה)
OPT_CAL = "📅 לוח שנה אינטראקטיבי"
OPT_MANAGE = "⚙️ ניהול ומחיקה"
OPT_ADD = "➕ הוספת משימה"
OPT_WORK = "📦 סידור עבודה שבועי"
OPT_DASH = "📊 דשבורד מנהלים"

# בניית תפריט לפי תפקיד
if user_role == "מנהל WMS":
    menu_options = [OPT_CAL, OPT_WORK, OPT_ADD, OPT_MANAGE, OPT_DASH]
elif user_role == "צוות מחסן":
    menu_options = [OPT_WORK, OPT_CAL]
else: # סמנכ"ל
    menu_options = [OPT_DASH, OPT_CAL]

choice = st.sidebar.radio("ניווט:", menu_options)

# --- 1. לוח שנה ---
if choice == OPT_CAL:
    st.header(OPT_CAL)
    events = []
    for _, r in st.session_state.df.iterrows():
        try:
            if not r['Date']: continue
            base_date = pd.to_datetime(r['Date']).to_pydatetime()
            done_dates = str(r['Done_Dates']).split(",") if r['Done_Dates'] else []
            
            iters = 30 if r['Recurring'] == "יומי" else 12 if r['Recurring'] == "שבועי" else 8 if r['Recurring'] == "דו-שבועי" else 4 if r['Recurring'] == "חודשי" else 1
            gap = 1 if r['Recurring'] == "יומי" else 7 if r['Recurring'] == "שבועי" else 14 if r['Recurring'] == "דו-שבועי" else 30 if r['Recurring'] == "חודשי" else 0
            
            for i in range(iters):
                curr = base_date + timedelta(days=i * gap)
                curr_str = curr.strftime("%Y-%m-%d")
                color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff" if curr_str in done_dates else "#dc3545"
                
                events.append({
                    "id": f"{r['ID']}_{curr_str}",
                    "title": str(r['Task_Name']),
                    "start": curr_str,
                    "color": color,
                    "extendedProps": {"description": str(r['Description']), "status": "בוצע" if curr_str in done_dates else "ממתין"}
                })
        except: continue

    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600}, key="main_calendar")

# --- 2. ניהול ומחיקה ---
elif choice == OPT_MANAGE:
    st.header(OPT_MANAGE)
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        to_del = st.selectbox("בחר משימה למחיקה:", st.session_state.df["Task_Name"])
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != to_del]
            save_data(st.session_state.df)
            st.rerun()

# --- 3. הוספת משימה ---
elif choice == OPT_ADD:
    st.header(OPT_ADD)
    with st.form("add_task_form"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור/הערות")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        start_date = st.date_input("תאריך התחלה", datetime.now())
        
        if st.form_submit_button("שמור משימה"):
            if name:
                new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 100
                new_row = pd.DataFrame([{
                    "ID": new_id, "Task_Name": name, "Description": desc, 
                    "Recurring": freq, "Date": start_date.strftime("%Y-%m-%d"), 
                    "Done_Dates": "", "Final_Approval": "לא"
                }])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"המשימה '{name}' נוספה!")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

# --- 4. סידור עבודה שבועי ---
elif choice == OPT_WORK:
    st.header(OPT_WORK)
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    cols = st.columns(5)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    
    for i, name in enumerate(days_names):
        target_dt = start_of_week + timedelta(days=i)
        t_str = target_dt.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"### יום {name}\n**{target_dt.strftime('%d/%m')}**")
            for idx, r in st.session_state.df.iterrows():
                try:
                    base = pd.to_datetime(r['Date']).to_pydatetime()
                    diff = (target_dt - base).days
                    is_hit = (diff == 0) or (r['Recurring'] == "יומי" and diff > 0) or \
                             (r['Recurring'] == "שבועי" and diff > 0 and diff % 7 == 0) or \
                             (r['Recurring'] == "דו-שבועי" and diff > 0 and diff % 14 == 0) or \
                             (r['Recurring'] == "חודשי" and diff > 0 and diff % 30 == 0)
                    
                    if is_hit:
                        done_list = str(r['Done_Dates']).split(",")
                        if t_str in done_list:
                            st.success(f"✅ {r['Task_Name']}")
                        else:
                            st.write(f"⏳ {r['Task_Name']}")
                            if user_role == "מנהל WMS":
                                if st.button("בצע", key=f"d_{r['ID']}_{t_str}"):
                                    updated_done = f"{str(r['Done_Dates'])},{t_str}".strip(",")
                                    st.session_state.df.at[idx, "Done_Dates"] = updated_done
                                    save_data(st.session_state.df)
                                    st.rerun()
                except: continue

# --- 5. דשבורד מנהלים (KPI יומי) ---
elif choice == OPT_DASH:
    st.header(OPT_DASH)
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    scheduled_today = []
    done_today = []
    
    for _, r in st.session_state.df.iterrows():
        try:
            base = pd.to_datetime(r['Date']).to_pydatetime()
            diff = (now - base).days
            hit = (diff == 0) or (r['Recurring'] == "יומי" and diff > 0) or \
                  (r['Recurring'] == "שבועי" and diff > 0 and diff % 7 == 0) or \
                  (r['Recurring'] == "דו-שבועי" and diff > 0 and diff % 14 == 0) or \
                  (r['Recurring'] == "חודשי" and diff > 0 and diff % 30 == 0)
            if hit:
                scheduled_today.append(r['Task_Name'])
                if today_str in str(r['Done_Dates']).split(","):
                    done_today.append(r['Task_Name'])
        except: continue

    c1, c2, c3 = st.columns(3)
    c1.metric("משימות להיום", len(scheduled_today))
    c2.metric("בוצעו היום", len(done_today))
    prog = (len(done_today)/len(scheduled_today)*100) if scheduled_today else 0
    c3.metric("ניצולת יומית", f"{int(prog)}%")

    st.divider()
    col_r, col_l = st.columns(2)
    with col_r:
        st.subheader("📋 פירוט ביצועי היום")
        for t in scheduled_today:
            st.write(f"{'✅' if t in done_today else '⏳'} {t}")
    
    with col_l:
        st.subheader("🏁 אישור סופי (סמנכ\"ל)")
        to_app = st.session_state.df[st.session_state.df["Final_Approval"] != "כן"]
        for i, r in to_app.iterrows():
            if st.button(f"אישור סופי: {r['Task_Name']}", key=f"f_{r['ID']}"):
                st.session_state.df.at[i, "Final_Approval"] = "כן"
                save_data(st.session_state.df)
                st.rerun()
