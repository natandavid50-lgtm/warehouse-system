import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# הגדרות עמוד ראשי
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# חיבור ל-Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"])
        # ניקוי עמודות ריקות שנוצרות לעיתים בגיליון
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.dropna(subset=["ID"], how="all")
    except Exception as e:
        st.error(f"שגיאת טעינה: {e}")
        return pd.DataFrame()

df = load_data()

# וידוא קיום עמודות למניעת שגיאות KeyError
required_cols = ["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"]
for col in required_cols:
    if col not in df.columns:
        df[col] = "לא" if "Done" in col or "Approval" in col else "N/A"

# --- תפריט צד (Sidebar) ---
st.sidebar.title("מערכת ניהול מחסן")
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

# הגדרת אפשרויות ניווט
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

# --- 1. דף לוח שנה ---
if choice == opt1:
    st.header(opt1)
    events = []
    for _, r in df.iterrows():
        if pd.notnull(r['Date']) and r['Date'] != "N/A":
            color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff"
            events.append({
                "title": f"#{int(r['ID'])} {r['Task_Name']}",
                "start": str(r['Date']),
                "color": color
            })
    calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 700})

# --- 2. דף הוספת משימה (סדר שדות מתוקן) ---
elif choice == opt2:
    st.header(opt2)
    # הוצאת בחירת החזרה מחוץ לטופס לטובת רענון מיידי
    recur_type = st.selectbox("האם זו משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
    
    day_of_week = "N/A"
    if recur_type != "לא":
        day_of_week = st.selectbox("באיזה יום בשבוע?", ["ראשון", "שני", "שלישי", "רביעי", "חמישי"])

    with st.form("add_task_form"):
        t_name = st.text_input("שם המשימה")
        t_desc = st.text_area("תיאור המשימה")
        t_date = st.date_input("תאריך לביצוע", datetime.now())
        
        if st.form_submit_button("שמור משימה"):
            if t_name:
                new_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_row = pd.DataFrame([{
                    "ID": new_id, "Task_Name": t_name, "Description": t_desc,
                    "Recurring": recur_type, "Day_of_Week": day_of_week,
                    "Date": t_date.strftime("%Y-%m-%d"), "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success(f"המשימה '{t_name}' נוספה בהצלחה!")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

# --- 3. דף ביטול משימה ---
elif choice == opt3:
    st.header(opt3)
    for i, row in df.iterrows():
        c1, c2 = st.columns([4, 1])
        c1.write(f"#{int(row['ID'])} - {row['Task_Name']} ({row['Date']})")
        # שימוש ב-key ייחודי למניעת DuplicateElementKey
        if c2.button("מחק ❌", key=f"del_btn_{row['ID']}_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()

# --- 4. דף ביצוע מחסן ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] != "כן"]
    if pending.empty:
        st.info("אין משימות פתוחות לביצוע.")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"משימה #{int(row['ID'])}: {row['Task_Name']}"):
                st.write(f"תיאור: {row['Description']}")
                if st.button("סמן כבוצע ✅", key=f"wdone_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.rerun()

# --- 5. דף אישור סופי ---
elif choice == opt5:
    st.header(opt5)
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] != "כן")]
    if to_approve.empty:
        st.info("אין משימות הממתינות לאישור סופי.")
    else:
        for i, row in to_approve.iterrows():
            with st.expander(f"לאישור: {row['Task_Name']}"):
                if st.button("אשר משימה סופית 👍", key=f"fapp_{row['ID']}"):
                    df.at[i, "Final_Approval"] = "כן"
                    conn.update(data=df)
                    st.rerun()

# --- 6. דוח סיכום ---
elif choice == opt6:
    st.header(opt6)
    st.dataframe(df, use_container_width=True)

# --- 7. ניקוי היסטוריה ---
elif choice == opt7:
    st.header(opt7)
    if st.button("נקה משימות מאושרות"):
        df = df[df["Final_Approval"] != "כן"]
        conn.update(data=df)
        st.success("ההיסטוריה נוקתה")
        st.rerun()
