import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="מערכת ניהול מחסן מתקדמת", layout="wide")

# חיבור לגוגל שיטס
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # קריאת הנתונים וניקוי שורות ריקות לחלוטין
    data = conn.read(ttl="0")
    data = data.dropna(how="all")
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"שגיאה בחיבור לנתונים: {e}")
    st.stop()

# --- תפריט צדי ---
st.sidebar.title("הגדרות מערכת")
user_type = st.sidebar.selectbox("מי משתמש במערכת עכשיו?", ["מנהל מחסן", "מנהל WMS", "סמנכ\"ל/הנהלה"])
st.sidebar.markdown(f"**שלום, {user_type}** 👋")
st.sidebar.divider()

# לוגיקת הרשאות לתפריט
if user_type == "מנהל WMS":
    menu = ["📅 לוח שנה ומבט על", "➕ הוספת משימה", "📦 ביצוע משימות (מחסן)", "✅ אישור סופי", "📊 דוח סיכום"]
    choice = st.sidebar.selectbox("תפריט ניווט מלא", menu)
else:
    if user_type == "מנהל מחסן":
        menu = ["📦 ביצוע משימות (מחסן)", "📅 לוח שנה ומבט על"]
    else:
        menu = ["📊 דוח סיכום", "📅 לוח שנה ומבט על"]
    choice = st.sidebar.radio("פעולות", menu)

# פונקציה לעיצוב צבעים בטבלה
def style_status(val):
    color = 'red' if val == 'לא' else 'green'
    return f'color: {color}; font-weight: bold'

# --- דפי האפליקציה ---

if "📅 לוח שנה ומבט על" in choice:
    st.header("📅 לוח משימות ולו\"ז")
    selected_date = st.date_input("בחר תאריך לצפייה", datetime.now())
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # סינון רק לעמודות החשובות
    cols_to_show = ["ID", "Description", "Warehouse_Done", "Final_Approval", "Date", "User"]
    
    day_tasks = df[df["Date"] == date_str]
    if not day_tasks.empty:
        st.subheader(f"משימות ליום {date_str}")
        # הצגת טבלה מעוצבת
        st.dataframe(day_tasks[cols_to_show].style.applymap(style_status, subset=['Warehouse_Done', 'Final_Approval']), use_container_width=True)
    else:
        st.info(f"אין משימות לתאריך {date_str}")
    
    st.divider()
    st.subheader("כל המשימות במערכת")
    st.dataframe(df[cols_to_show].sort_values(by="ID", ascending=False).style.applymap(style_status, subset=['Warehouse_Done', 'Final_Approval']), use_container_width=True)

elif "➕ הוספת משימה" in choice:
    st.header("➕ יצירת משימה חדשה")
    with st.form("task_form"):
        desc = st.text_area("תיאור המשימה")
        task_date = st.date_input("תאריך לביצוע", datetime.now())
        recurring = st.selectbox("האם משימה חוזרת?", ["לא", "יומי", "שבועי"])
        submitted = st.form_submit_button("שלח למערכת")
        
        if submitted and desc:
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{
                "ID": new_id, "Description": desc, "Warehouse_Done": "לא",
                "Final_Approval": "לא", "Date": task_date.strftime("%Y-%m-%d"),
                "Recurring": recurring, "User": user_type
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("המשימה נוספה!")
            st.rerun()

elif "📦 ביצוע משימות" in choice:
    st.header("📦 משימות לביצוע במחסן")
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("אין משימות פתוחות.")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"משימה #{row['ID']} | תאריך: {row['Date']}"):
                st.write(f"**מה לעשות:** {row['Description']}")
                if st.button(f"סימנתי כבוצע ✅", key=f"btn_{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.rerun()

elif "✅ אישור סופי" in choice:
    st.header("✅ אישור מנהל")
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    if to_approve.empty:
        st.info("אין משימות הממתינות לאישור.")
    else:
        st.write("אשר את המשימות שבוצעו במחסן:")
        st.dataframe(to_approve[["ID", "Description", "Date", "User"]], use_container_width=True)
        if st.button("אשר את כל המשימות שבוצעו"):
            df.loc[(df["Warehouse_Done"] == "כן"), "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()

elif "📊 דוח סיכום" in choice:
    st.header("📊 דוח ביצועים")
    # הצגת הטבלה הנקייה בלבד
    st.dataframe(df[["ID", "Description", "Warehouse_Done", "Final_Approval", "Date", "User"]], use_container_width=True)
