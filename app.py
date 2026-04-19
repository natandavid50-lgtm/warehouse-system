import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

DB_FILE = "warehouse_db.csv"

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

opt1, opt2, opt3, opt4, opt5 = (
    "📅 לוח שנה אינטראקטיבי", "⚙️ ניהול ומחיקה", 
    "➕ הוספת משימה", "📦 סידור עבודה שבועי", "📊 דשבורד מנהלים"
)

# הגדרת תפריט לפי תפקיד
if user_role == "מנהל WMS":
    menu = [opt1, opt2, opt3, opt4, opt5]
elif user_role == "צוות מחסן":
    menu = [opt4, opt1]
else:
    menu = [opt5, opt1]

choice = st.sidebar.radio("ניווט:", menu)

# --- 1. לוח שנה ---
if choice == opt1:
    st.header(opt1)
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

    res = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600}, key="main_calendar")
    if res.get("eventClick"):
        st.session_state.selected_event = res["eventClick"]["event"]
    
    if st.session_state.selected_event:
        ev = st.session_state.selected_event
        props = ev.get('extendedProps', {})
        st.info(f"🔍 **משימה:** {ev.get('title')}\n\n**תיאור:** {props.get('description')}\n\n**סטטוס:** {props.get('status')}")

# --- 4. סידור עבודה (הרשאות מנהל WMS לסימון) ---
elif choice == opt4:
    st.header("📦 סידור עבודה שבועי")
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
                            # הגבלת הכפתור למנהל WMS בלבד
                            if user_role == "מנהל WMS":
                                if st.button("בצע", key=f"d_{r['ID']}_{t_str}"):
                                    current_done = str(r['Done_Dates'])
                                    updated_done = f"{current_done},{t_str}".strip(",")
                                    st.session_state.df.at[idx, "Done_Dates"] = updated_done
                                    save_data(st.session_state.df)
                                    st.rerun()
                except: continue

# --- 5. דשבורד סמנכ"ל (משימות שהושלמו היום) ---
elif choice == opt5:
    st.header("📊 דשבורד בקרה לסמנכ\"ל")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    c1, c2 = st.columns(2)
    c1.metric("משימות במערכת", len(st.session_state.df))
    
    # סינון משימות שבוצעו היום
    completed_today = []
    for _, r in st.session_state.df.iterrows():
        if today_str in str(r['Done_Dates']).split(","):
            completed_today.append(r['Task_Name'])
    
    c2.metric("בוצעו היום", len(completed_today))

    st.subheader(f"✅ משימות שהושלמו היום ({datetime.now().strftime('%d/%m/%Y')})")
    if completed_today:
        for task in completed_today:
            st.write(f"🔹 {task}")
    else:
        st.write("טרם הושלמו משימות היום.")

    st.divider()
    st.subheader("📋 סטטוס אישורים סופיים")
    st.dataframe(st.session_state.df[["Task_Name", "Recurring", "Final_Approval"]], use_container_width=True)

# --- 3. הוספת משימה (מנהל WMS בלבד) ---
elif choice == opt3:
    st.header("➕ הוספת משימה")
    with st.form("add"):
        n = st.text_input("שם המשימה")
        f = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        sd = st.date_input("תאריך התחלה", datetime.now())
        if st.form_submit_button("שמור"):
            nid = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 100
            new_r = pd.DataFrame([{"ID": nid, "Task_Name": n, "Description": "", "Recurring": f, "Date": sd.strftime("%Y-%m-%d"), "Done_Dates": "", "Final_Approval": "לא"}])
            st.session_state.df = pd.concat([st.session_state.df, new_r], ignore_index=True)
            save_data(st.session_state.df)
            st.rerun()

# --- 2. ניהול ומחיקה ---
elif choice == opt2:
    st.header("⚙️ ניהול")
    st.dataframe(st.session_state.df)
    if not st.session_state.df.empty:
        to_del = st.selectbox("בחר למחיקה:", st.session_state.df["Task_Name"])
        if st.button("מחק"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != to_del]
            save_data(st.session_state.df)
            st.rerun()
