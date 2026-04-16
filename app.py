import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="מערכת ניהול מחסן - לוח שנה", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    data = conn.read(ttl="0")
    # ניקוי עמודות ריקות שגורמות לשגיאה
    data = data.dropna(how="all", axis=0).dropna(how="all", axis=1)
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"שגיאה בחיבור: {e}")
    st.stop()

# --- תפריט צדי ---
st.sidebar.title("הגדרות")
user_type = st.sidebar.selectbox("משתמש:", ["מנהל מחסן", "מנהל WMS", "סמנכ\"ל/הנהלה"])

if user_type == "מנהל WMS":
    menu = ["📅 לוח שנה", "➕ הוספת משימה", "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום"]
    choice = st.sidebar.selectbox("ניווט:", menu)
else:
    choice = st.sidebar.radio("פעולות:", ["📦 ביצוע (מחסן)", "📅 לוח שנה", "📊 דוח סיכום"])

# --- תצוגת לוח שנה אמיתי ---
if "📅 לוח שנה" in choice:
    st.header("📅 לוח משימות חודשי")
    
    # הכנת הנתונים לפורמט של לוח שנה
    calendar_events = []
    for _, row in df.iterrows():
        color = "#28a745" if row.get("Final_Approval") == "כן" else "#ffc107"
        calendar_events.append({
            "title": f"#{row['ID']} - {row['Description'][:20]}...",
            "start": row["Date"],
            "end": row["Date"],
            "color": color
        })

    calendar_options = {
        "editable": "true",
        "selectable": "true",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek",
        },
        "initialView": "dayGridMonth",
    }
    
    # הצגת לוח השנה
    state = calendar(events=calendar_events, options=calendar_options)
    
    st.divider()
    st.subheader("פירוט משימות")
    st.dataframe(df[["ID", "Description", "Warehouse_Done", "Date", "User"]], use_container_width=True)

# --- המשך שאר הדפים (הוספת משימה וכו') ---
elif "➕ הוספת משימה" in choice:
    st.header("➕ הוספת משימה")
    with st.form("add"):
        desc = st.text_area("תיאור")
        d = st.date_input("תאריך", datetime.now())
        if st.form_submit_button("שלח"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{"ID": new_id, "Description": desc, "Date": d.strftime("%Y-%m-%d"), "Warehouse_Done": "לא", "Final_Approval": "לא", "User": user_type}])
            conn.update(data=pd.concat([df, new_row], ignore_index=True))
            st.success("נוסף!")
            st.rerun()

# שאר הלוגיקה (ביצוע משימות ואישור סופי) נשארת דומה אך עם ניקוי שגיאות
elif "📦 ביצוע" in choice:
    st.header("📦 משימות לביצוע")
    pending = df[df["Warehouse_Done"] == "לא"]
    for i, row in pending.iterrows():
        if st.button(f"בצע משימה {row['ID']}", key=f"b_{row['ID']}"):
            df.at[i, "Warehouse_Done"] = "כן"
            conn.update(data=df)
            st.rerun()

elif "✅ אישור" in choice:
    st.header("✅ אישור סופי")
    to_app = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    st.table(to_app[["ID", "Description", "Date"]])
    if st.button("אשר הכל"):
        df.loc[df["Warehouse_Done"] == "כן", "Final_Approval"] = "כן"
        conn.update(data=df)
        st.rerun()
