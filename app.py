import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="מערכת ניהול מחסן מתקדמת", layout="wide")

# חיבור לגוגל שיטס
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="0")

try:
    df = load_data()
except Exception as e:
    st.error(f"שגיאה בחיבור לנתונים: {e}")
    st.stop()

# --- תפריט צדי ---
st.sidebar.title("הגדרות מערכת")

# בחירת משתמש
user_type = st.sidebar.selectbox("מי משתמש במערכת עכשיו?", ["מנהל מחסן", "מנהל WMS", "סמנכ\"ל/הנהלה"])
st.sidebar.markdown(f"**שלום, {user_type}** 👋")
st.sidebar.divider()

# לוגיקת תפריט ניווט מבוסס הרשאות
if user_type == "מנהל WMS":
    # רק מנהל WMS רואה את כל האפשרויות בתפריט נפתח
    menu = ["📅 לוח שנה ומבט על", "➕ הוספת משימה", "📦 ביצוע משימות (מחסן)", "✅ אישור סופי", "📊 דוח סיכום"]
    choice = st.sidebar.selectbox("תפריט ניווט מלא (מנהל WMS)", menu)
else:
    # משתמשים אחרים רואים תפריט מוגבל לפי התפקיד שלהם
    if user_type == "מנהל מחסן":
        menu = ["📦 ביצוע משימות (מחסן)", "📅 לוח שנה ומבט על"]
    else: # סמנכ"ל/הנהלה
        menu = ["📊 דוח סיכום", "📅 לוח שנה ומבט על"]
    
    choice = st.sidebar.radio("פעולות מורשות", menu)

# --- דפי האפליקציה ---

if choice == "📅 לוח שנה ומבט על":
    st.header("📅 לוח משימות ולו\"ז")
    selected_date = st.date_input("בחר תאריך לצפייה", datetime.now())
    date_str = selected_date.strftime("%Y-%m-%d")
    day_tasks = df[df["Date"] == date_str]
    
    if not day_tasks.empty:
        st.dataframe(day_tasks, use_container_width=True)
    else:
        st.info(f"אין משימות לתאריך {date_str}")
    
    st.divider()
    st.subheader("כל המשימות במערכת")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

elif choice == "➕ הוספת משימה":
    st.header("➕ יצירת משימה חדשה")
    with st.form("task_form"):
        desc = st.text_area("תיאור המשימה")
        task_date = st.date_input("תאריך לביצוע", datetime.now())
        recurring = st.selectbox("האם משימה חוזרת?", ["לא", "יומי", "שבועי"])
        submitted = st.form_submit_button("שלח למערכת")
        
        if submitted and desc:
            new_id = len(df) + 1 if not df.empty else 1
            new_row = pd.DataFrame([{
                "ID": new_id, "Description": desc, "Warehouse_Done": "לא",
                "Final_Approval": "לא", "Date": task_date.strftime("%Y-%m-%d"),
                "Recurring": recurring, "User": user_type
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("המשימה נוספה!")
            st.rerun()

elif choice == "📦 ביצוע משימות (מחסן)":
    st.header("📦 משימות לביצוע במחסן")
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("אין משימות פתוחות.")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"משימה #{row['ID']} - {row['Date']}"):
                st.write(row['Description'])
                if st.button(f"סמן כבוצע ✅", key=f"btn_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.rerun()

elif choice == "✅ אישור סופי":
    st.header("✅ אישור מנהל")
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    if to_approve.empty:
        st.info("אין משימות הממתינות לאישור.")
    else:
        st.dataframe(to_approve[["ID", "Description", "Date", "User"]])
        if st.button("אשר את כל המשימות שבוצעו"):
            df.loc[(df["Warehouse_Done"] == "כן"), "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()

elif choice == "📊 דוח סיכום":
    st.header("📊 דוח ביצועים")
    st.dataframe(df, use_container_width=True)
