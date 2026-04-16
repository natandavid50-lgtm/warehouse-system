import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# הגדרות מערכת למניעת שגיאות סינטקס
TITLE = "מערכת ניהול מחסן"
st.set_page_config(page_title=TITLE, layout="wide")

# חיבור לנתונים
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"])
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.dropna(subset=["ID"], how="all")
    except Exception as e:
        st.error(f"שגיאת טעינה: {e}")
        return pd.DataFrame()

df = load_data()

# וידוא עמודות קריטיות
cols = ["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"]
for c in cols:
    if c not in df.columns:
        df[c] = "לא" if "Done" in c or "Approval" in c else None

# --- תפריט צד (Sidebar) ---
st.sidebar.title(TITLE)
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

opt1, opt2, opt3, opt4, opt5, opt6, opt7 = (
    "📅 לוח שנה", "➕ הוספת משימה", "🗑️ ביטול משימה", 
    "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום", "🧹 ניקוי היסטוריה"
)

if user_role == "מנהל WMS":
    menu_options = [opt1, opt2, opt3, opt4, opt5, opt6, opt7]
elif user_role == "צוות מחסן":
    menu_options = [opt4, opt1] # כאן הגדרנו מה צוות מחסן רואה
else:
    menu_options = [opt6, opt1]

choice = st.sidebar.radio("ניווט:", menu_options)

# --- דף לוח שנה ---
if choice == opt1:
    st.header(opt1)
    cal_events = []
    for _, r in df.iterrows():
        if pd.notnull(r.get("Date")) and pd.notnull(r.get("ID")):
            t_title = str(r.get("Task_Name", "משימה"))
            display_text = f"#{int(r['ID'])} {t_title}"
            event_color = "#28a745" if r.get("Final_Approval") == "כן" else "#007bff"
            cal_events.append({"title": display_text, "start": str(r["Date"]), "color": event_color})
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 700})

# --- דף הוספת משימה (העדכני) ---
elif choice == opt2:
    st.header(opt2)
    # השדה מחוץ לטופס כדי לאפשר רענון דינמי של ימי השבוע
    recur_type = st.selectbox("האם זו משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
    
    day_val = "N/A"
    if recur_type != "לא":
        day_val = st.selectbox("באיזה יום בשבוע?", ["ראשון", "שני", "שלישי", "רביעי", "חמישי"])

    with st.form("add_task"):
        task_name = st.text_input("שם המשימה") # שדה ראשון
        task_desc = st.text_area("תיאור המשימה") # שדה שני
        task_date = st.date_input("תאריך ביצוע", datetime.now())
        
        if st.form_submit_button("שמור"):
            if task_name:
                next_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                new_row = pd.DataFrame([{
                    "ID": next_id, "Task_Name": task_name, "Description": task_desc, 
                    "Recurring": recur_type, "Day_of_Week": day_val, 
                    "Date": task_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success("נשמר!")
                st.rerun()

# --- דף ביצוע (מחסן) - הפתרון למה שראית בתמונה ---
elif choice == opt4:
    st.header(opt4)
    # הצגת משימות שטרם בוצעו במחסן
    pending = df[df["Warehouse_Done"] != "כן"]
    if pending.empty:
        st.info("אין משימות פתוחות לביצוע כרגע.")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"משימה #{int(row['ID'])}: {row['Task_Name']}"):
                st.write(f"**תיאור:** {row['Description']}")
                st.write(f"**תאריך:** {row['Date']}")
                if st.button("סמן כבוצע ✅", key=f"done_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.success("המשימה עודכנה!")
                    st.rerun()

# --- דף דוח סיכום ---
elif choice == opt6:
    st.header(opt6)
    st.dataframe(df.dropna(subset=["ID"]), use_container_width=True)

# --- דפים נוספים (ביטול/אישור סופי) ---
else:
    st.warning("הדף שנבחר נמצא בתהליך הטמעה או שאינו זמין לתפקידך.")
