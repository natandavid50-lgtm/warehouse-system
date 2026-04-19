import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# חיבור מאובטח ל-Google Sheets
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

if user_role == "מנהל WMS": menu = [opt1, opt2, opt3, opt4, opt5, opt6, opt7]
elif user_role == "צוות מחסן": menu = [opt4, opt1]
else: menu = [opt6, opt1]

choice = st.sidebar.radio("ניווט:", menu)

# --- 1. דף לוח שנה (תצוגת חזרתיות מלאה) ---
if choice == opt1:
    st.header(opt1)
    st.info("המערכת מציגה משימות חוזרות קדימה באופן אוטומטי. לחץ על משימה לפירוט.")
    
    events = []
    for _, r in df.iterrows():
        try:
            if r['Date'] == "לא צוין": continue
            base_date = datetime.strptime(str(r['Date']), "%Y-%m-%d")
            
            # לוגיקת חישוב חזרות להצגה בלוח
            iterations = 1
            step = timedelta(days=0)
            
            if r['Recurring'] == "יומי":
                iterations = 30
                step = timedelta(days=1)
            elif r['Recurring'] == "שבועי":
                iterations = 12
                step = timedelta(weeks=1)
            elif r['Recurring'] == "דו-שבועי":
                iterations = 6
                step = timedelta(weeks=2)
            elif r['Recurring'] == "חודשי":
                iterations = 4
                step = timedelta(days=30)
            
            for i in range(iterations):
                current_date = base_date + (step * i)
                
                # קביעת צבע לפי סטטוס
                color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff"
                if r['Warehouse_Done'] == "לא": color = "#dc3545"
                
                events.append({
                    "id": f"{r['ID']}_{i}",
                    "title": str(r['Task_Name']),
                    "start": current_date.strftime("%Y-%m-%d"),
                    "color": color,
                    "extendedProps": {
                        "orig_id": str(r['ID']),
                        "desc": str(r['Description']),
                        "recur": str(r['Recurring']),
                        "w_done": str(r['Warehouse_Done'])
                    }
                })
        except (ValueError, TypeError):
            continue

    cal = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})
    
    if "eventClick" in cal:
        ev = cal["eventClick"]["event"]
        st.divider()
        st.subheader(f"🔍 פרטי משימה: {ev['title']}")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**מזהה מקורי:** {ev['extendedProps']['orig_id']}")
            st.write(f"**תיאור:** {ev['extendedProps']['desc']}")
        with c2:
            st.write(f"**תדירות:** {ev['extendedProps']['recur']}")
            st.write(f"**בוצע במחסן:** {ev['extendedProps']['w_done']}")

# --- 2. דף הוספת משימה (סדר שדות מקצועי וחזרתיות מלאה) ---
elif choice == opt2:
    st.header(opt2)
    with st.form("professional_add_form"):
        # שדות קלט בסדר לוגי
        t_name = st.text_input("שם המשימה", placeholder="לדוגמה: ספירת מלאי שבועית")
        t_desc = st.text_area("תיאור מפורט של המשימה")
        
        col1, col2 = st.columns(2)
        with col1:
            recur_val = st.selectbox("תדירות חזרה", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        with col2:
            t_date = st.date_input("תאריך התחלה / ביצוע", datetime.now())
            
        if st.form_submit_button("✅ שמור משימה והוסף ללוח"):
            if t_name:
                next_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_entry = pd.DataFrame([{
                    "ID": next_id, "Task_Name": t_name, "Description": t_desc,
                    "Recurring": recur_val, "Date": t_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_entry], ignore_index=True))
                st.success(f"המשימה '{t_name}' נוספה בהצלחה בפורמט {recur_val}!")
                st.rerun()
            else:
                st.error("אנא הזן שם למשימה")

# --- 4. ביצוע (מחסן) ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("כל המשימות בוצעו!")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"📦 #{int(row['ID'])}: {row['Task_Name']}"):
                st.write(f"**תיאור:** {row['Description']}")
                st.write(f"**תדירות:** {row['Recurring']}")
                if st.button("סמן כבוצע ✅", key=f"done_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.rerun()

# --- 5. אישור סופי ---
elif choice == opt5:
    st.header(opt5)
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    if to_approve.empty:
        st.info("אין משימות הממתינות לאישור.")
    else:
        for i, row in to_approve.iterrows():
            if st.button(f"אשר סופית: {row['Task_Name']}", key=f"app_{row['ID']}"):
                df.at[i, "Final_Approval"] = "כן"
                conn.update(data=df)
                st.rerun()

# --- דפים משלימים ---
elif choice == opt3:
    st.header(opt3)
    for i, row in df.iterrows():
        c1, c2 = st.columns([5, 1])
        c1.write(f"#{int(row['ID'])} - {row['Task_Name']} ({row['Recurring']})")
        if c2.button("מחיקה", key=f"del_{row['ID']}"):
            conn.update(data=df.drop(i))
            st.rerun()

elif choice == opt6:
    st.header(opt6)
    st.dataframe(df, use_container_width=True)

elif choice == opt7:
    st.header(opt7)
    if st.button("נקה היסטוריה (משימות מאושרות)"):
        conn.update(data=df[df["Final_Approval"] != "כן"])
        st.rerun()
