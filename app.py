import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# הגדרת דף
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# חיבור לגיליון (הגנה מפני שגיאות חיבור)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"])
        # הסרת עמודות ריקות
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        # מילוי ערכים ריקים למניעת שגיאת JSON
        return data.fillna("")
    except Exception as e:
        st.error(f"שגיאת טעינה: {e}")
        return pd.DataFrame()

df = load_data()

# --- תפריט צד ---
st.sidebar.title("מערכת ניהול מחסן")
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

# אפשרויות ניווט
opt1, opt2, opt3, opt4, opt5, opt6, opt7 = (
    "📅 לוח שנה", "➕ הוספת משימה", "🗑️ ביטול משימה", 
    "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום", "🧹 ניקוי היסטוריה"
)

if user_role == "מנהל WMS":
    menu = [opt1, opt2, opt3, opt4, opt5, opt6, opt7]
elif user_role == "צוות מחסן":
    menu = [opt4, opt1]
else:
    menu = [opt6, opt1]

choice = st.sidebar.radio("ניווט:", menu)

# --- דפים ---

# 1. לוח שנה
if choice == opt1:
    st.header(opt1)
    events = []
    # המרת נתונים ללוח שנה בצורה בטוחה
    for _, r in df.iterrows():
        if r['Date']:
            events.append({
                "title": str(r['Task_Name']),
                "start": str(r['Date']),
                "extendedProps": {"description": str(r['Description'])}
            })
    calendar(events=events, options={"direction": "rtl", "locale": "he"})

# 2. הוספת משימה
elif choice == opt2:
    st.header(opt2)
    with st.form("add_task_form", clear_on_submit=True):
        t_name = st.text_input("שם המשימה")
        t_desc = st.text_area("תיאור המשימה")
        t_date = st.date_input("תאריך לביצוע")
        if st.form_submit_button("שמור משימה"):
            if t_name:
                new_id = int(df["ID"].max() + 1) if not df.empty and str(df["ID"].max()).isdigit() else 1
                new_row = pd.DataFrame([{
                    "ID": new_id, "Task_Name": t_name, "Description": t_desc, 
                    "Date": t_date.strftime("%Y-%m-%d"), "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success("המשימה נוספה!")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

# 3. ביטול משימה
elif choice == opt3:
    st.header(opt3)
    for i, row in df.iterrows():
        c1, c2 = st.columns([4, 1])
        c1.write(f"#{row['ID']} - {row['Task_Name']}")
        if c2.button("מחק", key=f"del_{i}"):
            conn.update(data=df.drop(i))
            st.rerun()

# 4. ביצוע מחסן
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty: st.info("אין משימות פתוחות.")
    for i, row in pending.iterrows():
        if st.button(f"סמן כבוצע: {row['Task_Name']}", key=f"done_{i}"):
            df.at[i, "Warehouse_Done"] = "כן"
            conn.update(data=df)
            st.rerun()

# 5. אישור סופי
elif choice == opt5:
    st.header(opt5)
    to_approve = df[df["Warehouse_Done"] == "כן"]
    for i, row in to_approve.iterrows():
        if st.button(f"אשר סופית: {row['Task_Name']}", key=f"app_{i}"):
            df.at[i, "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()

# 6. דוח סיכום
elif choice == opt6:
    st.header(opt6)
    st.dataframe(df, use_container_width=True)

# 7. ניקוי
elif choice == opt7:
    st.header(opt7)
    if st.button("נקה היסטוריה"):
        conn.update(data=df[df["Final_Approval"] != "כן"])
        st.rerun()
