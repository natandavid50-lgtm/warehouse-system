import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

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

# --- תפריט צדי משופר ---
st.sidebar.title("הגדרות מערכת")
user_type = st.sidebar.selectbox("מי משתמש במערכת עכשיו?", ["מנהל לוגיסטיקה", "צוות מחסן", "סמנכ"ל/הנהלה"])
st.sidebar.markdown(f"**שלום, {user_type}** 👋")
st.sidebar.divider()

menu = ["לוח שנה ומבט על", "הוספת משימה", "ביצוע משימות (מחסן)", "אישור סופי", "דוח סיכום"]
choice = st.sidebar.radio("תפריט ניווט", menu)

# --- לוגיקה של משימות חוזרות (פונקציה קטנה) ---
def add_task_to_db(desc, is_recurring="לא"):
    global df
    new_id = len(df) + 1 if not df.empty else 1
    new_row = pd.DataFrame([{
        "ID": new_id,
        "Description": desc,
        "Warehouse_Done": "לא",
        "Final_Approval": "לא",
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Recurring": is_recurring,
        "User": user_type
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    conn.update(data=df)

# --- דפי האפליקציה ---

if choice == "לוח שנה ומבט על":
    st.header("📅 לוח משימות ולו"ז")
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        # תצוגה פשוטה של משימות לפי תאריך
        st.write("משימות קרובות:")
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("אין עדיין נתונים להצגה.")

elif choice == "הוספת משימה":
    st.header("➕ יצירת משימה חדשה")
    with st.form("task_form"):
        desc = st.text_area("תיאור המשימה")
        recurring = st.selectbox("האם משימה חוזרת?", ["לא", "יומי", "שבועי"])
        submitted = st.form_submit_button("שלח למחסן")
        
        if submitted and desc:
            add_task_to_db(desc, recurring)
            st.success(f"משימה {recurring} נוספה בהצלחה!")

elif choice == "ביצוע משימות (מחסן)":
    st.header("📦 משימות לביצוע במחסן")
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("אין משימות פתוחות. עבודה טובה!")
    else:
        for i, row in pending.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**#{row['ID']}** | {row['Description']} | (נוצר ע\"י: {row.get('User', 'לא ידוע')})")
            with col2:
                if st.button(f"בוצע ✅", key=f"done_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.rerun()

elif choice == "אישור סופי":
    st.header("✅ אישור מנהל למשימות שבוצעו")
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    if to_approve.empty:
        st.info("אין משימות הממתינות לאישור.")
    else:
        st.table(to_approve[["ID", "Description", "Date"]])
        if st.button("אשר את כל המשימות שבוצעו"):
            df.loc[(df["Warehouse_Done"] == "כן"), "Final_Approval"] = "כן"
            conn.update(data=df)
            st.success("הכל אושר!")
            st.rerun()

elif choice == "דוח סיכום":
    st.header("📊 דוח ביצועים")
    st.write(f"שלום {user_type}, כאן ניתן לראות את כל היסטוריית המשימות.")
    st.dataframe(df)
