import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# הגדרות כלליות למניעת שגיאות כתיב
TITLE = "מערכת ניהול מחסן"
st.set_page_config(page_title=TITLE, layout="wide")

# חיבור למסד הנתונים
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

# וידוא עמודות למניעת KeyError
cols = ["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"]
for c in cols:
    if c not in df.columns:
        df[c] = None

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
    menu_options = [opt4, opt1]
else:
    menu_options = [opt6, opt1]

choice = st.sidebar.radio("ניווט:", menu_options)

# --- לוגיקת דפים ---

if choice == opt1: # לוח שנה
    st.header(opt1)
    cal_events = []
    for _, r in df.iterrows():
        if pd.notnull(r.get("Date")) and pd.notnull(r.get("ID")):
            t_title = str(r.get("Task_Name", "משימה"))
            display_text = f"#{int(r['ID'])} {t_title}"
            event_color = "#28a745" if r.get("Final_Approval") == "כן" else "#007bff"
            cal_events.append({"title": display_text, "start": str(r["Date"]), "color": event_color})
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 700})

elif choice == opt2: # הוספת משימה
    st.header(opt2)
    
    # הוצאת השדה מחוץ לטופס כדי שיעבוד "בלייב"
    recur_type = st.selectbox("האם זו משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
    
    day_val = "N/A"
    if recur_type != "לא":
        day_val = st.selectbox("באיזה יום בשבוע?", ["ראשון", "שני", "שלישי", "רביעי", "חמישי"])

    with st.form("task_submission_form"):
        task_name = st.text_input("שם המשימה")
        task_desc = st.text_area("תיאור המשימה")
        task_date = st.date_input("תאריך ביצוע", datetime.now())
        
        if st.form_submit_button("שמור משימה"):
            if task_name:
                next_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                new_row = pd.DataFrame([{
                    "ID": next_id, "Task_Name": task_name, "Description": task_desc, 
                    "Recurring": recur_type, "Day_of_Week": day_val, 
                    "Date": task_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success(f"המשימה '{task_name}' נוספה!")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

elif choice == opt3: # ביטול משימה
    st.header(opt3)
    if not df.empty:
        for i, row in df.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.write(f"#{int(row['ID'])} - {row['Task_Name']} ({row['Date']})")
            if col2.button("מחק ❌", key=f"del_{row['ID']}"):
                new_df = df.drop(i)
                conn.update(data=new_df)
                st.rerun()

elif choice == opt6: # דוח סיכום
    st.header(opt6)
    st.dataframe(df.dropna(subset=["ID"]), use_container_width=True)

elif choice == opt7: # ניקוי היסטוריה
    st.header(opt7)
    if st.button("נקה את כל המשימות המאושרות"):
        # השארת רק משימות שלא אושרו סופית
        new_df = df[df["Final_Approval"] != "כן"]
        conn.update(data=new_df)
        st.success("ההיסטוריה נוקתה")
        st.rerun()

else:
    st.info("דף זה בבנייה...")
