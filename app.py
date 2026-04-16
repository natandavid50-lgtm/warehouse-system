import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# חיבור לגיליון
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    data = conn.read(ttl="0")
    # הסרת שורות ריקות לחלוטין כדי למנוע כפילויות במפתחות (Duplicate Keys)
    data = data.dropna(subset=["ID", "Description"], how="all")
    # ניקוי עמודות זבל
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"שגיאה בטעינה: {e}")
    st.stop()

# --- תפריט ניווט רשימה פתוחה ---
st.sidebar.title("תפריט ניהול")
user_role = st.sidebar.selectbox("תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

if user_role == "מנהל WMS":
    options = ["📅 לוח שנה", "➕ הוספת משימה", "🗑️ ביטול משימה", "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום"]
elif user_role == "צוות מחסן":
    options = ["📦 ביצוע (מחסן)", "📅 לוח שנה"]
else:
    options = ["📊 דוח סיכום", "📅 לוח שנה"]

choice = st.sidebar.radio("ניווט מהיר:", options)

# --- לוח שנה מוקטן עם שמות ימים בעברית ---
if choice == "📅 לוח שנה":
    st.header("📅 לוח משימות")
    cal_events = []
    for _, r in df.iterrows():
        if pd.notnull(r.get("Date")):
            c = "#28a745" if r.get("Final_Approval") == "כן" else "#ffc107"
            cal_events.append({
                "title": f"#{int(r['ID'])} {str(r['Description'])[:15]}",
                "start": str(r["Date"]),
                "color": c
            })
    
    # הגדרות לוח שנה מותאמות
    cal_opts = {"direction": "rtl", "locale": "he", "height": 550, "initialView": "dayGridMonth"}
    calendar(events=cal_events, options=cal_opts)

# --- ביטול משימות (כולל הגנה על מפתחות) ---
elif choice == "🗑️ ביטול משימה":
    st.header("🗑️ ביטול משימות")
    # סינון שורות לא תקינות כדי למנוע את שגיאת ה-Duplicate Key
    valid_tasks = df.dropna(subset=["ID"])
    open_tasks = valid_tasks[valid_tasks["Final_Approval"] != "כן"]
    
    if open_tasks.empty:
        st.info("אין משימות לביטול.")
    else:
        for i, r in open_tasks.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(f"#{int(r['ID'])} | {r['Date']} | {r['Description']}")
            # שימוש ב-Index של ה-DataFrame כמפתח ייחודי לכפתור
            if c2.button("מחק ❌", key=f"btn_del_{i}"):
                df = df.drop(i)
                conn.update(data=df)
                st.warning(f"משימה {int(r['ID'])} נמחקה.")
                st.rerun()

# --- הוספת משימה עם חזרה ---
elif choice == "➕ הוספת משימה":
    st.header("➕ הוספת משימה")
    with st.form("new_task"):
        d_text = st.text_input("תיאור")
        d_date = st.date_input("תאריך", datetime.now())
        d_recur = st.selectbox("חזרה", ["לא", "יומי", "שבועי", "חודשי"])
        if st.form_submit_button("שמור"):
            nid = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{
                "ID": nid, "Description": d_text, "Warehouse_Done": "לא",
                "Final_Approval": "לא", "Date": d_date.strftime("%Y-%m-%d"),
                "Recurring": d_recur, "User": user_role
            }])
            conn.update(data=pd.concat([df, new_row], ignore_index=True))
            st.success("נוסף
