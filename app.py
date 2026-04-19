import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# חיבור לנתונים
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Warehouse_Done", "Final_Approval"])
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.fillna("לא צוין")
    except Exception as e:
        st.error(f"שגיאת טעינה: {e}")
        return pd.DataFrame()

df = load_data()

# --- תפריט צד ---
st.sidebar.title("מערכת ניהול מחסן")
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

opt1, opt2, opt3, opt4, opt5, opt6, opt7 = (
    "📅 לוח שנה", "➕ הוספת משימה", "🗑️ ביטול משימה", 
    "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום", "🧹 ניקוי היסטוריה"
)

menu = [opt1, opt2, opt3, opt4, opt5, opt6, opt7] if user_role == "מנהל WMS" else [opt4, opt1] if user_role == "צוות מחסן" else [opt6, opt1]
choice = st.sidebar.radio("ניווט:", menu)

# --- 1. דף לוח שנה (לוגיקה משופרת ופירוט מלא) ---
if choice == opt1:
    st.header(opt1)
    st.info("לחץ על משימה כדי לראות את הפירוט המלא מתחת ללוח.")
    
    events = []
    for _, r in df.iterrows():
        try:
            if r['Date'] == "לא צוין": continue
            # המרת התאריך מהגיליון לאובייקט זמן
            base_date = datetime.strptime(str(r['Date']), "%Y-%m-%d")
            
            # הגדרת תדירות החזרות
            iterations = 1
            days_step = 0
            
            if r['Recurring'] == "יומי":
                iterations, days_step = 30, 1
            elif r['Recurring'] == "שבועי":
                iterations, days_step = 12, 7
            elif r['Recurring'] == "דו-שבועי":
                iterations, days_step = 8, 14
            elif r['Recurring'] == "חודשי":
                iterations, days_step = 4, 30
            
            for i in range(iterations):
                current_date = base_date + timedelta(days=i * days_step)
                
                # צבעים לפי סטטוס
                color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff"
                if r['Warehouse_Done'] == "לא": color = "#dc3545"
                
                events.append({
                    "id": f"{r['ID']}_{i}", # מזהה ייחודי לכל מופע בלוח
                    "title": str(r['Task_Name']),
                    "start": current_date.strftime("%Y-%m-%d"),
                    "color": color,
                    "extendedProps": {
                        "orig_id": str(r['ID']),
                        "desc": str(r['Description']),
                        "recur": str(r['Recurring']),
                        "done": str(r['Warehouse_Done']),
                        "app": str(r['Final_Approval'])
                    }
                })
        except:
            continue

    # הצגת הלוח
    cal = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})
    
    # הצגת הפירוט בלחיצה
    if "eventClick" in cal:
        res = cal["eventClick"]["event"]
        st.divider()
        st.subheader(f"📋 פירוט משימה: {res['title']}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**תיאור:** {res['extendedProps']['desc']}")
            st.write(f"**מזהה במערכת:** {res['extendedProps']['orig_id']}")
        with col2:
            st.write(f"**תדירות:** {res['extendedProps']['recur']}")
            st.write(f"**סטטוס:** {'בוצע' if res['extendedProps']['done'] == 'כן' else 'ממתין לביצוע'}")
            st.write(f"**אישור סמנכ\"ל:** {'מאושר' if res['extendedProps']['app'] == 'כן' else 'טרם אושר'}")

# --- 2. דף הוספת משימה (סדר שדות ותדירויות) ---
elif choice == opt2:
    st.header(opt2)
    with st.form("task_form_final"):
        t_name = st.text_input("שם המשימה")
        t_desc = st.text_area("תיאור המשימה")
        
        col1, col2 = st.columns(2)
        with col1:
            t_recur = st.selectbox("תדירות חזרה", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        with col2:
            t_date = st.date_input("תאריך התחלה", datetime.now())
            
        if st.form_submit_button("שמור והוסף ללוח"):
            if t_name:
                next_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_row = pd.DataFrame([{
                    "ID": next_id, "Task_Name": t_name, "Description": t_desc,
                    "Recurring": t_recur, "Date": t_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success(f"המשימה '{t_name}' נוספה בהצלחה!")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

# --- שאר הפונקציות (ביצוע, אישור וכו') ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] == "לא"]
    for i, row in pending.iterrows():
        if st.button(f"סמן כבוצע: {row['Task_Name']}", key=f"d_{row['ID']}"):
            df.at[i, "Warehouse_Done"] = "כן"
            conn.update(data=df)
            st.rerun()

elif choice == opt5:
    st.header(opt5)
    to_app = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    for i, row in to_app.iterrows():
        if st.button(f"אשר סופית: {row['Task_Name']}", key=f"a_{row['ID']}"):
            df.at[i, "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()

else:
    st.write("בחר אפשרות מהתפריט")
