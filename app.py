import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# אתחול ה-State עבור הפירוט
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Warehouse_Done", "Final_Approval"])
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.fillna("לא צוין")
    except Exception:
        return pd.DataFrame()

df = load_data()

# --- תפריט צד ---
st.sidebar.title("מערכת ניהול מחסן")
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

opt1, opt2, opt3, opt4, opt5 = (
    "📅 לוח שנה אינטראקטיבי", "⚙️ ניהול ומחיקת משימות", 
    "➕ הוספת משימה", "📦 ביצוע (מחסן)", "✅ אישור סמנכ\"ל"
)

menu = [opt1, opt2, opt3, opt4, opt5] if user_role == "מנהל WMS" else [opt1, opt4]
choice = st.sidebar.radio("ניווט:", menu)

# --- 1. לוח שנה אינטראקטיבי ---
if choice == opt1:
    st.header(opt1)
    
    events = []
    for _, r in df.iterrows():
        try:
            base_date = pd.to_datetime(r['Date']).to_pydatetime()
            iter_count = 8 if r['Recurring'] == "דו-שבועי" else 12 if r['Recurring'] == "שבועי" else 1
            step = 14 if r['Recurring'] == "דו-שבועי" else 7 if r['Recurring'] == "שבועי" else 0
            
            for i in range(iter_count):
                curr = base_date + timedelta(days=i * step)
                events.append({
                    "id": str(r['ID']),
                    "title": r['Task_Name'],
                    "start": curr.strftime("%Y-%m-%d"),
                    "color": "#28a745" if r['Final_Approval'] == "כן" else "#dc3545" if r['Warehouse_Done'] == "לא" else "#007bff",
                    "extendedProps": {"desc": r['Description'], "rec": r['Recurring'], "status": r['Warehouse_Done']}
                })
        except: continue

    res = calendar(events=events, options={"direction": "rtl", "locale": "he"})
    
    # תפיסת לחיצה והצגת פירוט
    if res.get("eventClick"):
        st.session_state.selected_event = res["eventClick"]["event"]
    
    if st.session_state.selected_event:
        ev = st.session_state.selected_event
        st.info(f"**פרטי משימה:** {ev['title']}\n\n**תיאור:** {ev['extendedProps']['desc']}\n\n**תדירות:** {ev['extendedProps']['rec']}")

# --- 2. מערכת ניהול ומחיקה לצמיתות ---
elif choice == opt2:
    st.header(opt2)
    st.write("כאן ניתן לראות את כל המשימות הגולמיות ולמחוק אותן מהבסיס נתונים.")
    
    if df.empty:
        st.info("אין משימות במערכת.")
    else:
        # הצגת טבלה למעקב מהיר
        st.dataframe(df[["ID", "Task_Name", "Recurring", "Date", "Warehouse_Done"]], use_container_width=True)
        
        st.divider()
        task_to_delete = st.selectbox("בחר משימה למחיקה לצמיתות:", df["Task_Name"].unique())
        
        if st.button("🗑️ מחק משימה לצמיתות מהמערכת"):
            updated_df = df[df["Task_Name"] != task_to_delete]
            conn.update(data=updated_df)
            st.success(f"המשימה '{task_to_delete}' הוסרה לצמיתות.")
            st.rerun()

# --- 3. הוספת משימה ---
elif choice == opt3:
    st.header(opt3)
    with st.form("new_task"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        rec = st.selectbox("חזרה", ["לא", "שבועי", "דו-שבועי"])
        date = st.date_input("תאריך התחלה")
        if st.form_submit_button("שמור"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_data = pd.DataFrame([{"ID": new_id, "Task_Name": name, "Description": desc, "Recurring": rec, "Date": date.strftime("%Y-%m-%d"), "Warehouse_Done": "לא", "Final_Approval": "לא"}])
            conn.update(data=pd.concat([df, new_data], ignore_index=True))
            st.success("נוסף!")
            st.rerun()

# --- ביצוע ואישור ---
elif choice == opt4:
    st.header(opt4)
    for i, r in df[df["Warehouse_Done"]=="לא"].iterrows():
        if st.button(f"בוצע: {r['Task_Name']}", key=f"p_{r['ID']}"):
            df.at[i, "Warehouse_Done"] = "כן"
            conn.update(data=df)
            st.rerun()

elif choice == opt5:
    st.header(opt5)
    for i, r in df[(df["Warehouse_Done"]=="כן") & (df["Final_Approval"]=="לא")].iterrows():
        if st.button(f"אשר: {r['Task_Name']}", key=f"a_{r['ID']}"):
            df.at[i, "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()
