import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# חיבור למסד הנתונים ב-Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"])
        # ניקוי עמודות מיותרות
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.dropna(subset=["ID"], how="all")
    except Exception as e:
        st.error(f"שגיאת טעינה: {e}")
        return pd.DataFrame()

df = load_data()

# וידוא עמודות למניעת שגיאות הרצה
required_cols = ["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"]
for col in required_cols:
    if col not in df.columns:
        df[col] = "לא" if "Done" in col or "Approval" in col else "N/A"

# --- תפריט צד (Sidebar) ---
st.sidebar.title("מערכת ניהול מחסן")
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

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

# --- 1. דף לוח שנה (כולל לחיצה לפירוט) ---
if choice == opt1:
    st.header(opt1)
    st.info("לחץ על משימה בלוח כדי לצפות בפרטים המלאים")
    
    events = []
    for _, r in df.iterrows():
        if pd.notnull(r['Date']) and r['Date'] != "N/A":
            # צבעים לפי סטטוס
            color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff"
            if r['Warehouse_Done'] == "לא": color = "#dc3545" # אדום לביצוע דחוף
            
            events.append({
                "id": str(r['ID']),
                "title": r['Task_Name'],
                "start": str(r['Date']),
                "color": color,
                "extendedProps": {
                    "description": r['Description'],
                    "recurring": r['Recurring'],
                    "day": r['Day_of_Week'],
                    "warehouse": r['Warehouse_Done']
                }
            })
    
    # תצוגת לוח השנה
    cal = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})
    
    # הצגת פירוט בלחיצה
    if "eventClick" in cal:
        event_info = cal["eventClick"]["event"]
        st.divider()
        st.subheader(f"🔍 פירוט משימה: {event_info['title']}")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**מזהה:** {event_info['id']}")
            st.write(f"**תיאור:** {event_info['extendedProps']['description']}")
            st.write(f"**תאריך יעד:** {event_info['start']}")
        with c2:
            st.write(f"**סוג חזרה:** {event_info['extendedProps']['recurring']}")
            st.write(f"**יום בשבוע:** {event_info['extendedProps']['day']}")
            st.write(f"**בוצע במחסן:** {event_info['extendedProps']['warehouse']}")

# --- 2. דף הוספת משימה (הוספה אוטומטית ללוח) ---
elif choice == opt2:
    st.header(opt2)
    
    # בחירת חזרה מחוץ לטופס לטובת דינמיות
    recur_type = st.selectbox("האם זו משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
    
    day_selection = "N/A"
    if recur_type != "לא":
        day_selection = st.selectbox("באיזה יום בשבוע?", ["ראשון", "שני", "שלישי", "רביעי", "חמישי"])

    with st.form("new_task"):
        name = st.text_input("שם המשימה") # שדה ראשון
        desc = st.text_area("תיאור המשימה")
        date_val = st.date_input("תאריך", datetime.now())
        
        if st.form_submit_button("שמור"):
            if name:
                new_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_entry = pd.DataFrame([{
                    "ID": new_id, "Task_Name": name, "Description": desc,
                    "Recurring": recur_type, "Day_of_Week": day_selection,
                    "Date": date_val.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_entry], ignore_index=True))
                st.success(f"המשימה '{name}' נשמרה ותופיע בלוח השנה!")
                st.rerun()
            else:
                st.error("נא להזין שם משימה")

# --- 3. ביטול משימה ---
elif choice == opt3:
    st.header(opt3)
    for i, row in df.iterrows():
        col1, col2 = st.columns([4, 1])
        col1.write(f"#{int(row['ID'])} - {row['Task_Name']} ({row['Date']})")
        if col2.button("מחק ❌", key=f"del_{row['ID']}"):
            conn.update(data=df.drop(i))
            st.rerun()

# --- 4. ביצוע מחסן (צוות מחסן) ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] != "כן"]
    if pending.empty:
        st.info("אין משימות פתוחות.")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"משימה #{int(row['ID'])}: {row['Task_Name']}"):
                st.write(row['Description'])
                if st.button("סמן כבוצע ✅", key=f"wd_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.rerun()

# --- 5. אישור סופי ---
elif choice == opt5:
    st.header(opt5)
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] != "כן")]
    for i, row in to_approve.iterrows():
        if st.button(f"אשר סופית: {row['Task_Name']}", key=f"fa_{row['ID']}"):
            df.at[i, "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()

# --- 6. דוח סיכום ו-7. ניקוי ---
elif choice == opt6:
    st.header(opt6)
    st.dataframe(df, use_container_width=True)

elif choice == opt7:
    st.header(opt7)
    if st.button("נקה היסטוריה מאושרת"):
        conn.update(data=df[df["Final_Approval"] != "כן"])
        st.rerun()
