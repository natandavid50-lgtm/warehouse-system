import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# הגדרות טקסט גלובליות למניעת SyntaxError
TITLE = "מערכת ניהול מחסן"
ROLE_LABEL = "מי משתמש במערכת?"
NAV_LABEL = "תפריט ניווט"

st.set_page_config(page_title=TITLE, layout="wide")

# חיבור לנתונים
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Warehouse_Done", "Final_Approval"])
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.dropna(subset=["ID"], how="all")
    except Exception as e:
        st.error(f"Error loading: {e}")
        return pd.DataFrame()

df = load_data()

# וידוא עמודות קריטיות כולל העמודה החדשה Task_Name
for col in ["ID", "Task_Name", "Description", "Recurring", "Date", "Warehouse_Done", "Final_Approval"]:
    if col not in df.columns:
        df[col] = None

# --- תפריט צד (Sidebar) ---
st.sidebar.title(TITLE)
user_role = st.sidebar.selectbox(ROLE_LABEL, ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

opt1, opt2, opt3, opt4, opt5, opt6, opt7 = (
    "📅 לוח שנה", "➕ הוספת משימה", "🗑️ ביטול משימה", 
    "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום", "🧹 ניקוי היסטוריה"
)

# הגדרת הרשאות לפי תפקיד
if user_role == "מנהל WMS":
    menu_options = [opt1, opt2, opt3, opt4, opt5, opt6, opt7]
elif user_role == "צוות מחסן":
    menu_options = [opt4, opt1]
else:
    menu_options = [opt6, opt1]

choice = st.sidebar.radio(NAV_LABEL, menu_options)

# --- ניווט דפים ---

if choice == opt1:
    st.header(opt1)
    cal_events = []
    for i, r in df.iterrows():
        if pd.notnull(r.get("Date")) and pd.notnull(r.get("ID")):
            # שימוש בשם המשימה החדש לכותרת בלוח
            t_name = r.get("Task_Name") if pd.notnull(r.get("Task_Name")) else "משימה"
            display_title = f"#{int(r['ID'])} {t_name}"
            event_color = "#28a745" if r.get("Final_Approval") == "כן" else "#007bff"
            cal_events.append({
                "title": display_title,
                "start": str(r["Date"]),
                "color": event_color
            })
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 700})

elif choice == opt2:
    st.header(opt2)
    # טופס הוספת משימה עם הסדר החדש שביקשת
    with st.form("new_task_form"):
        # 1. שם משימה
        new_name = st.text_input("שם המשימה")
        # 2. תיאור
        new_desc = st.text_area("תיאור המשימה")
        # 3. משימה חוזרת
        new_recur = st.selectbox("משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
        # שאר השדות
        new_date = st.date_input("תאריך לביצוע", datetime.now())
        
        if st.form_submit_button("שמור"):
            if new_name:
                next_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                new_row = pd.DataFrame([{
                    "ID": next_id, "Task_Name": new_name, "Description": new_desc, 
                    "Recurring": new_recur, "Date": new_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא", "User": user_role
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success("המשימה נשמרה בהצלחה")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

elif choice == opt6:
    st.header(opt6)
    st.dataframe(df.dropna(subset=["ID"]), use_container_width=True)

# הוסף כאן את שאר הלוגיקה (opt3, opt4, opt5, opt7) באותה צורה
