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

# הגדרת תפריט לפי תפקיד
if user_role == "מנהל WMS": menu = [opt1, opt2, opt3, opt4, opt5, opt6, opt7]
elif user_role == "צוות מחסן": menu = [opt4, opt1]
else: menu = [opt6, opt1]

choice = st.sidebar.radio("ניווט:", menu)

# --- 1. דף לוח שנה (עם תיקון שגיאת תאריך וחזרתיות) ---
if choice == opt1:
    st.header(opt1)
    st.info("משימות חוזרות מוצגות ל-8 השבועות הקרובים. לחץ על משימה לפירוט.")
    
    events = []
    for _, r in df.iterrows():
        # בדיקה שהתאריך תקין ובפורמט הנכון לפני עיבוד
        try:
            if r['Date'] == "לא צוין": continue
            base_date = datetime.strptime(str(r['Date']), "%Y-%m-%d")
            
            # קביעת כמות חזרות
            iterations = 1
            if r['Recurring'] == "שבועי": iterations = 8
            elif r['Recurring'] == "יומי": iterations = 14 # שבועיים קדימה ליומי
            
            for i in range(iterations):
                if r['Recurring'] == "שבועי":
                    curr_date = base_date + timedelta(weeks=i)
                elif r['Recurring'] == "יומי":
                    curr_date = base_date + timedelta(days=i)
                else:
                    curr_date = base_date
                
                # עיצוב צבעים
                color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff"
                if r['Warehouse_Done'] == "לא": color = "#dc3545"
                
                events.append({
                    "id": f"{r['ID']}_{i}",
                    "title": str(r['Task_Name']),
                    "start": curr_date.strftime("%Y-%m-%d"),
                    "color": color,
                    "extendedProps": {
                        "orig_id": str(r['ID']),
                        "desc": str(r['Description']),
                        "recur": str(r['Recurring']),
                        "status": "בוצע" if r['Warehouse_Done'] == "כן" else "ממתין"
                    }
                })
        except ValueError:
            continue # דילוג על שורות עם תאריך לא תקין
    
    cal = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})
    
    if "eventClick" in cal:
        ev = cal["eventClick"]["event"]
        st.divider()
        st.subheader(f"🔍 פירוט משימה: {ev['title']}")
        st.write(f"**תיאור:** {ev['extendedProps']['desc']}")
        st.write(f"**סטטוס ביצוע:** {ev['extendedProps']['status']}")
        st.write(f"**סוג חזרה:** {ev['extendedProps']['recur']}")

# --- 2. דף הוספת משימה ---
elif choice == opt2:
    st.header(opt2)
    recur_type = st.selectbox("האם המשימה חוזרת?", ["לא", "יומי", "שבועי"])
    
    with st.form("task_form"):
        t_name = st.text_input("שם המשימה") #
        t_desc = st.text_area("תיאור/פירוט")
        t_date = st.date_input("תאריך התחלה", datetime.now())
        
        if st.form_submit_button("שמור והוסף ללוח"):
            if t_name:
                new_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_data = pd.DataFrame([{
                    "ID": new_id, "Task_Name": t_name, "Description": t_desc,
                    "Recurring": recur_type, "Date": t_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_data], ignore_index=True))
                st.success("המשימה נשמרה!")
                st.rerun()
            else:
                st.error("נא להזין שם משימה")

# --- 4. ביצוע מחסן (הפעלה מלאה) ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("אין משימות פתוחות לביצוע.")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"📦 משימה #{int(row['ID'])}: {row['Task_Name']}"):
                st.write(f"תיאור: {row['Description']}")
                if st.button("סמן כבוצע ✅", key=f"btn_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.rerun()

# --- 5. אישור סופי ---
elif choice == opt5:
    st.header(opt5)
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    if to_approve.empty:
        st.info("אין משימות הממתינות לאישור סופי.")
    else:
        for i, row in to_approve.iterrows():
            if st.button(f"אשר סופית: {row['Task_Name']}", key=f"app_{row['ID']}"):
                df.at[i, "Final_Approval"] = "כן"
                conn.update(data=df)
                st.rerun()

# --- דפים נוספים ---
elif choice == opt6:
    st.header(opt6)
    st.dataframe(df)

elif choice == opt7:
    st.header(opt7)
    if st.button("נקה היסטוריה (מחיקת מאושרים)"):
        conn.update(data=df[df["Final_Approval"] != "כן"])
        st.rerun()
