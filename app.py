import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# חיבור ל-Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    data = conn.read(ttl="0")
    data = data.dropna(how="all")
    # ניקוי עמודות מיותרות
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"שגיאה בטעינה: {e}")
    st.stop()

# --- תפריט צדי (Radio - רשימה פתוחה) ---
st.sidebar.title("ניהול מערכת")
user_type = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

if user_type == "מנהל WMS":
    menu = ["📅 לוח שנה", "➕ הוספת משימה", "🗑️ ביטול משימה", "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום"]
elif user_type == "צוות מחסן":
    menu = ["📦 ביצוע (מחסן)", "📅 לוח שנה"]
else:
    menu = ["📊 דוח סיכום", "📅 לוח שנה"]

choice = st.sidebar.radio("ניווט:", menu)

# --- דף לוח שנה ---
if choice == "📅 לוח שנה":
    st.header("📅 לוח משימות")
    events = []
    if not df.empty:
        for _, row in df.iterrows():
            d = str(row.get("Date", ""))
            if d and d != "None":
                color = "#28a745" if row.get("Final_Approval") == "כן" else "#ffc107"
                events.append({
                    "title": f"#{row.get('ID','')} {str(row.get('Description',''))[:15]}",
                    "start": d,
                    "color": color
                })
    
    calendar_options = {"direction": "rtl", "locale": "he", "height": 500, "initialView": "dayGridMonth"}
    calendar(events=events, options=calendar_options)

# --- דף הוספת משימה (כולל משימה חוזרת) ---
elif choice == "➕ הוספת משימה":
    st.header("➕ הוספת משימה")
    with st.form("add_form"):
        desc = st.text_input("תיאור המשימה")
        date_val = st.date_input("תאריך לביצוע", datetime.now())
        recur = st.selectbox("חזרה:", ["לא", "יומי", "שבועי", "חודשי"])
        if st.form_submit_button("שמור"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{
                "ID": new_id, "Description": desc, "Warehouse_Done": "לא",
                "Final_Approval": "לא", "Date": date_val.strftime("%Y-%m-%d"),
                "Recurring": recur, "User": user_type
            }])
            conn.update(data=pd.concat([df, new_row], ignore_index=True))
            st.success("המשימה נוספה!")
            st.rerun()

# --- דף ביטול משימה (הבקשה שלך) ---
elif choice == "🗑️ ביטול משימה":
    st.header("🗑️ ביטול משימות קיימות")
    open_tasks = df[df["Final_Approval"] != "כן"]
    if open_tasks.empty:
        st.info("אין משימות לביטול.")
    else:
        for i, row in open_tasks.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.write(f"#{row['ID']} - {row['Description']} ({row['Date']})")
            if col2.button("מחק ❌", key=f"del_{row['ID']}"):
                df = df.drop(i)
                conn.update(data=df)
                st.warning(f"משימה {row['ID']} בוטלה.")
                st.rerun()

# --- דף ביצוע (צוות מחסן) ---
elif choice == "📦 ביצוע (מחסן)":
    st.header("📦 משימות לביצוע")
    pending = df[df["Warehouse_Done"] == "לא"]
    for i, row in pending.iterrows():
        with st.expander(f"משימה #{row['ID']} - {row['Date']}"):
            st.write(row["Description"])
            if st.button("סמן כבוצע ✅", key=f"done_{row['ID']}"):
                df.at[i, "Warehouse_Done"] = "כן"
                conn.update(data=df)
                st.rerun()

# --- דף אישור סופי (פר משימה) ---
elif choice == "✅ אישור סופי":
    st.header("✅ אישור מנהל (בודד)")
    to_app = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    for i, row in to_app.iterrows():
        col1, col2 = st.columns([4, 1])
        col1.write(f"#{row['ID']} - {row['Description']}")
        if col2.button("אשר ✅", key=f"app_{row['ID']}"):
            df.at[i, "Final_Approval"] = "כן"
            # יצירת משימה חוזרת אם מוגדר
            if row.get("Recurring") != "לא":
                new_date = pd.to_datetime(row["Date"]) + (timedelta(days=1) if row["Recurring"]=="יומי" else timedelta(weeks=1) if row["Recurring"]=="שבועי" else timedelta(days=30))
                new_row = pd.DataFrame([{
                    "ID": int(df["ID"].max()+1), "Description": row["Description"], "Warehouse_Done": "לא",
                    "Final_Approval": "לא", "Date": new_date.strftime("%Y-%m-%d"),
                    "Recurring": row["Recurring"], "User": row["User"]
                }])
                df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=df)
            st.rerun()

elif choice == "📊 דוח סיכום":
    st.header("📊 דוח סיכום")
    st.dataframe(df, use_container_width=True)
