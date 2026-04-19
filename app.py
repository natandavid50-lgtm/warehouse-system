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
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"])
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

# --- 1. דף לוח שנה (מתוקן לתמיכה בחזרתיות) ---
if choice == opt1:
    st.header(opt1)
    st.info("משימות חוזרות מוצגות אוטומטית ל-8 השבועות הקרובים")
    
    events = []
    for _, r in df.iterrows():
        if r['Date'] != "לא צוין":
            base_date = datetime.strptime(r['Date'], "%Y-%m-%d")
            
            # הגדרת מספר החזרות להצגה (למשל 8 שבועות קדימה)
            iterations = 1
            if r['Recurring'] == "שבועי": iterations = 8
            elif r['Recurring'] == "יומי": iterations = 30
            elif r['Recurring'] == "חודשי": iterations = 3
            
            for i in range(iterations):
                if r['Recurring'] == "שבועי":
                    current_date = base_date + timedelta(weeks=i)
                elif r['Recurring'] == "יומי":
                    current_date = base_date + timedelta(days=i)
                elif r['Recurring'] == "חודשי":
                    current_date = base_date + timedelta(days=i*30)
                else:
                    current_date = base_date
                
                color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff"
                if r['Warehouse_Done'] == "לא": color = "#dc3545"
                
                events.append({
                    "id": f"{r['ID']}_{i}",
                    "title": r['Task_Name'],
                    "start": current_date.strftime("%Y-%m-%d"),
                    "color": color,
                    "extendedProps": {
                        "orig_id": str(r['ID']),
                        "desc": str(r['Description']),
                        "recur": str(r['Recurring']),
                        "w_done": str(r['Warehouse_Done'])
                    }
                })
    
    cal = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})
    
    if "eventClick" in cal:
        ev = cal["eventClick"]["event"]
        st.divider()
        st.subheader(f"🔍 פרטי משימה #{ev['extendedProps']['orig_id']}")
        st.write(f"**שם:** {ev['title']}")
        st.write(f"**תיאור:** {ev['extendedProps']['desc']}")
        st.write(f"**חזרתיות:** {ev['extendedProps']['recur']}")

# --- 2. דף הוספת משימה ---
elif choice == opt2:
    st.header(opt2)
    recur_val = st.selectbox("משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
    day_val = "לא צוין"
    if recur_val == "שבועי":
        day_val = st.selectbox("באיזה יום?", ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"])

    with st.form("add_task_form"):
        t_name = st.text_input("שם המשימה")
        t_desc = st.text_area("תיאור המשימה")
        t_date = st.date_input("תאריך התחלה", datetime.now())
        
        if st.form_submit_button("שמור משימה"):
            if t_name:
                next_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_row = pd.DataFrame([{
                    "ID": next_id, "Task_Name": t_name, "Description": t_desc,
                    "Recurring": recur_val, "Day_of_Week": day_val,
                    "Date": t_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success(f"המשימה '{t_name}' נוספה למערכת!")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

# (שאר חלקי הקוד - ביטול, ביצוע וכו' - נשארים ללא שינוי)
