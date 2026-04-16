import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# הגדרות כותרות למניעת שגיאות סינטקס עם עברית
TITLE = "מערכת ניהול מחסן"
ROLE_LABEL = "בחר תפקיד:"
NAV_LABEL = "תפריט ניווט:"

st.set_page_config(page_title=TITLE, layout="wide")

# חיבור ל-Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"])
        # ניקוי עמודות ריקות
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.dropna(subset=["ID"], how="all")
    except Exception as e:
        st.error(f"שגיאת טעינה: {e}")
        return pd.DataFrame()

df = load_data()

# וידוא קיום עמודות למניעת KeyError
cols = ["ID", "Task_Name", "Description", "Recurring", "Day_of_Week", "Date", "Warehouse_Done", "Final_Approval"]
for c in cols:
    if c not in df.columns:
        df[c] = None

# --- תפריט צד (Sidebar) ---
st.sidebar.title(TITLE)
user_role = st.sidebar.selectbox(ROLE_LABEL, ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

# הגדרת כפתורי הניווט (ללא המילה "מעוצב")
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
    st.header(opt1)
    cal_events = []
    for _, r in df.iterrows():
        if pd.notnull(r.get("Date")) and pd.notnull(r.get("ID")):
            # הגנה מפני שגיאת TypeError בלוח השנה
            t_title = str(r.get("Task_Name", "משימה"))
            display_text = f"#{int(r['ID'])} {t_title}"
            event_color = "#28a745" if r.get("Final_Approval") == "כן" else "#007bff"
            cal_events.append({"title": display_text, "start": str(r["Date"]), "color": event_color})
    
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "height": 700})

# --- דף הוספת משימה (הסדר החדש שביקשת) ---
elif choice == opt2:
    st.header(opt2)
    with st.form("task_form"):
        # 1. שם משימה (ראשון)
        name = st.text_input("שם המשימה")
        
        # 2. תיאור (שני)
        desc = st.text_area("תיאור המשימה")
        
        # 3. משימה חוזרת (שלישי)
        recur = st.selectbox("משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
        
        # חלון בחירת יום (א'-ה') שמופיע רק אם המשימה חוזרת
        day_val = "N/A"
        if recur != "לא":
            day_val = st.selectbox("באיזה יום בשבוע?", ["ראשון", "שני", "שלישי", "רביעי", "חמישי"])
        
        task_date = st.date_input("תאריך", datetime.now())
        
        if st.form_submit_button("שמור משימה"):
            if name:
                new_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                new_data = pd.DataFrame([{
                    "ID": new_id, "Task_Name": name, "Description": desc, 
                    "Recurring": recur, "Day_of_Week": day_val, "Date": task_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_data], ignore_index=True))
                st.success("המשימה נוספה בהצלחה!")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

# --- דף דוח סיכום ---
elif choice == opt6:
    st.header(opt6)
    st.dataframe(df.dropna(subset=["ID"]), use_container_width=True)

# הודעת ברירה למניעת קריסת הממשק
else:
    st.info("דף זה נמצא בבנייה או שאין לך הרשאות לצפות בו.")
