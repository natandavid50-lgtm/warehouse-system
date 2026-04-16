import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    data = conn.read(ttl="0")
    data = data.dropna(how="all")
    # ניקוי עמודות שמתחילות ב-Unnamed (זבל מגוגל שיטס)
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים: {e}")
    st.stop()

# --- תפריט צדי ---
st.sidebar.title("הגדרות")
user_type = st.sidebar.selectbox("מי משתמש במערכת?", ["מנהל מחסן", "מנהל WMS", "סמנכ\"ל/הנהלה"])
st.sidebar.divider()

# שינוי כאן: תפריט רשימה פתוחה לכולם, עם אפשרויות שונות לפי תפקיד
st.sidebar.subheader("תפריט ניווט")
if user_type == "מנהל WMS":
    menu_options = ["📅 לוח שנה", "➕ הוספת משימה", "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום"]
elif user_type == "מנהל מחסן":
    menu_options = ["📦 ביצוע (מחסן)", "📅 לוח שנה"]
else: # סמנכ"ל
    menu_options = ["📊 דוח סיכום", "📅 לוח שנה"]

choice = st.sidebar.radio("", menu_options)

# --- דף לוח שנה ---
if "📅 לוח שנה" in choice:
    st.header("📅 לוח משימות")
    
    calendar_events = []
    if not df.empty:
        for _, row in df.iterrows():
            desc = str(row.get("Description", "")) if pd.notnull(row.get("Description")) else ""
            task_date = str(row.get("Date", ""))
            
            if task_date and task_date != "None":
                color = "#28a745" if row.get("Final_Approval") == "כן" else "#ffc107"
                calendar_events.append({
                    "title": f"#{row.get('ID', '?')} {desc[:15]}",
                    "start": task_date,
                    "color": color,
                })

    # הקטנת הגובה של לוח השנה והתאמה למסך
    calendar_options = {
        "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,dayGridWeek"},
        "initialView": "dayGridMonth",
        "direction": "rtl",
        "height": 600, # גובה קבוע כדי שלא יברח מהמסך
        "locale": "he"  # תמיכה בשמות הימים בעברית
    }
    
    calendar(events=calendar_events, options=calendar_options)
    
    st.divider()
    st.subheader("רשימה מפורטת")
    st.dataframe(df.dropna(subset=["ID"]), use_container_width=True)

# --- דף הוספת משימה ---
elif "➕ הוספת משימה" in choice:
    st.header("➕ הוספת משימה חדשה")
    with st.form("task_form"):
        desc = st.text_area("תיאור המשימה")
        task_date = st.date_input("תאריך לביצוע", datetime.now())
        if st.form_submit_button("שמור"):
            if desc:
                new_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                new_row = pd.DataFrame([{"ID": new_id, "Description": desc, "Warehouse_Done": "לא", "Final_Approval": "לא", "Date": task_date.strftime("%Y-%m-%d"), "User": user_type}])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success("נוסף!")
                st.rerun()

# --- דף ביצוע (מחסן) ---
elif "📦 ביצוע" in choice:
    st.header("📦 משימות לביצוע")
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("אין משימות.")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"משימה #{row['ID']} - {row['Date']}"):
                st.write(row['Description'])
                if st.button(f"בוצע", key=f"d_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.rerun()

# --- דף אישור סופי ---
elif "✅ אישור" in choice:
    st.header("✅ אישור מנהל")
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    if to_approve.empty:
        st.info("אין מה לאשר.")
    else:
        st.dataframe(to_approve[["ID", "Description", "Date"]])
        if st.button("אשר הכל"):
            df.loc[(df["Warehouse_Done"] == "כן"), "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()

# --- דוח סיכום ---
elif "📊 דוח" in choice:
    st.header("📊 דוח סיכום")
    st.dataframe(df, use_container_width=True)
