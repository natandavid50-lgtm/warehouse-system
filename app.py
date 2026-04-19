import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
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
        # טיפול בערכים ריקים למניעת שגיאת JSON בלוח השנה
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

if user_role == "מנהל WMS":
    menu = [opt1, opt2, opt3, opt4, opt5, opt6, opt7]
elif user_role == "צוות מחסן":
    menu = [opt4, opt1]
else:
    menu = [opt6, opt1]

choice = st.sidebar.radio("ניווט:", menu)

# --- 1. דף לוח שנה (כולל פירוט בלחיצה) ---
if choice == opt1:
    st.header(opt1)
    st.info("לחץ על משימה לצפייה בפרטים")
    events = []
    for _, r in df.iterrows():
        if r['Date'] != "לא צוין":
            # צבעים לפי סטטוס
            color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff"
            if r['Warehouse_Done'] == "לא": color = "#dc3545"
            
            events.append({
                "id": str(r['ID']),
                "title": str(r['Task_Name']),
                "start": str(r['Date']),
                "color": color,
                "extendedProps": {
                    "desc": str(r['Description']),
                    "recur": str(r['Recurring']),
                    "day": str(r['Day_of_Week']),
                    "w_done": str(r['Warehouse_Done'])
                }
            })
    
    cal = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})
    
    if "eventClick" in cal:
        ev = cal["eventClick"]["event"]
        st.divider()
        st.subheader(f"🔍 פרטי משימה #{ev['id']}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**שם:** {ev['title']}")
            st.write(f"**תיאור:** {ev['extendedProps']['desc']}")
        with col2:
            st.write(f"**סוג חזרה:** {ev['extendedProps']['recur']}")
            st.write(f"**בוצע במחסן:** {ev['extendedProps']['w_done']}")

# --- 2. דף הוספת משימה (כולל משימות חוזרות וסדר שדות) ---
elif choice == opt2:
    st.header(opt2)
    # שדה החזרה מחוץ לטופס כדי לאפשר רענון של בחירת היום
    recur_val = st.selectbox("משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
    day_val = "לא צוין"
    if recur_val != "לא":
        day_val = st.selectbox("באיזה יום?", ["ראשון", "שני", "שלישי", "רביעי", "חמישי"])

    with st.form("add_task_form"):
        t_name = st.text_input("שם המשימה") # שדה ראשון
        t_desc = st.text_area("תיאור המשימה")
        t_date = st.date_input("תאריך ביצוע", datetime.now())
        
        if st.form_submit_button("שמור"):
            if t_name:
                next_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_row = pd.DataFrame([{
                    "ID": next_id, "Task_Name": t_name, "Description": t_desc,
                    "Recurring": recur_val, "Day_of_Week": day_val,
                    "Date": t_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success("המשימה נשמרה בהצלחה!")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

# --- 3. ביטול משימה ---
elif choice == opt3:
    st.header(opt3)
    for i, row in df.iterrows():
        c1, c2 = st.columns([4, 1])
        c1.write(f"#{int(row['ID'])} - {row['Task_Name']}")
        if c2.button("מחק ❌", key=f"del_{row['ID']}"):
            conn.update(data=df.drop(i))
            st.rerun()

# --- 4. ביצוע (מחסן) ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("אין משימות לביצוע")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"משימה {row['Task_Name']}"):
                st.write(row['Description'])
                if st.button("סמן כבוצע ✅", key=f"done_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.rerun()

# --- 5. אישור סופי ---
elif choice == opt5:
    st.header(opt5)
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    for i, row in to_approve.iterrows():
        if st.button(f"אשר סופית: {row['Task_Name']}", key=f"fapp_{row['ID']}"):
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
    if st.button("מחק משימות מאושרות"):
        conn.update(data=df[df["Final_Approval"] != "כן"])
        st.rerun()
