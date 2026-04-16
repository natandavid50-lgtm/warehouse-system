import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# הגדרות שפה וטקסטים - מניעת שגיאות סינטקס
TITLE = "מערכת ניהול מחסן"
ROLE_LABEL = "בחר תפקיד:"
NAV_LABEL = "תפריט ניווט:"
SUCCESS_MSG = "המשימה נוספה בהצלחה"

st.set_page_config(page_title=TITLE, layout="wide")

# חיבור לנתונים
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Description", "Warehouse_Done", "Final_Approval", "Date", "Recurring", "User"])
        # ניקוי עמודות ושורות ריקות
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        data = data.dropna(subset=["ID", "Description"], how="all")
        return data
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

# וידוא עמודות למניעת KeyError
for col in ["ID", "Final_Approval", "Warehouse_Done", "Date", "Description"]:
    if col not in df.columns:
        df[col] = None

# --- תפריט צד (Sidebar) ---
st.sidebar.title(TITLE)
roles = ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"]
user_role = st.sidebar.selectbox(ROLE_LABEL, roles)
st.sidebar.divider()

# הסרת המילה "מעוצב" מהאפשרויות
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

choice = st.sidebar.radio(NAV_LABEL, menu_options)

# --- דף לוח שנה ---
if choice == opt1:
    st.header(opt1) # כותרת נקייה: "לוח שנה"
    cal_events = []
    for i, r in df.iterrows():
        if pd.notnull(r.get("Date")) and pd.notnull(r.get("ID")):
            # הגדרת צבעים לפי סטטוס
            event_color = "#28a745" if r.get("Final_Approval") == "כן" else "#007bff"
            # מניעת שגיאת טיפוס בכותרת
            display_title = f"#{int(r['ID'])} {str(r['Description'])[:20]}"
            cal_events.append({
                "title": display_title,
                "start": str(r["Date"]),
                "color": event_color,
                "allDay": True
            })
    
    calendar_options = {
        "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,listWeek"},
        "initialView": "dayGridMonth",
        "direction": "rtl",
        "locale": "he",
        "height": 700
    }
    calendar(events=cal_events, options=calendar_options, key='main_cal')

# --- שאר דפי המערכת ---
elif choice == opt2:
    st.header(opt2)
    with st.form("add_form"):
        desc = st.text_input("תיאור המשימה")
        date_val = st.date_input("תאריך", datetime.now())
        if st.form_submit_button("שמור"):
            new_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
            new_row = pd.DataFrame([{
                "ID": new_id, "Description": desc, "Warehouse_Done": "לא",
                "Final_Approval": "לא", "Date": date_val.strftime("%Y-%m-%d"), "User": user_role
            }])
            conn.update(data=pd.concat([df, new_row], ignore_index=True))
            st.success(SUCCESS_MSG)
            st.rerun()

elif choice == opt6:
    st.header(opt6)
    st.dataframe(df.dropna(subset=["ID"]), use_container_width=True)

# המשך לוגיקת שאר הכפתורים...
