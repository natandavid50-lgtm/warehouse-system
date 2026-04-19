import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# הגדרות עמוד - מבטיח שהלוח לא ייצא מפרופורציה
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# אתחול ה-State עבור הפירוט בלחיצה
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

# הגדרת הרשאות
if user_role == "מנהל WMS":
    menu = [opt1, opt2, opt3, opt4, opt5]
elif user_role == "צוות מחסן":
    menu = [opt1, opt4]
else:
    menu = [opt1, opt5]

choice = st.sidebar.radio("ניווט:", menu)

# --- 1. לוח שנה אינטראקטיבי (תדירויות מלאות) ---
if choice == opt1:
    st.header(opt1)
    
    events = []
    for _, r in df.iterrows():
        try:
            if r['Date'] == "לא צוין": continue
            base_date = pd.to_datetime(r['Date']).to_pydatetime()
            
            # לוגיקת חזרתיות מלאה
            iterations = 1
            days_step = 0
            
            if r['Recurring'] == "יומי": iterations, days_step = 30, 1
            elif r['Recurring'] == "שבועי": iterations, days_step = 12, 7
            elif r['Recurring'] == "דו-שבועי": iterations, days_step = 6, 14
            elif r['Recurring'] == "חודשי": iterations, days_step = 4, 30
            
            for i in range(iterations):
                curr = base_date + timedelta(days=i * days_step)
                
                # צבעים לפי סטטוס
                color = "#28a745" if r['Final_Approval'] == "כן" else "#dc3545" if r['Warehouse_Done'] == "לא" else "#007bff"
                
                events.append({
                    "id": f"{r['ID']}_{i}",
                    "title": str(r['Task_Name']),
                    "start": curr.strftime("%Y-%m-%d"),
                    "color": color,
                    "extendedProps": {
                        "orig_id": str(r['ID']),
                        "desc": str(r['Description']),
                        "rec": str(r['Recurring']),
                        "status": "בוצע" if r['Warehouse_Done'] == "כן" else "ממתין"
                    }
                })
        except: continue

    # הצגת הלוח עם הגבלת גובה למניעת עיוות
    res = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 650})
    
    # תפיסת לחיצה
    if res.get("eventClick"):
        st.session_state.selected_event = res["eventClick"]["event"]
    
    if st.session_state.selected_event:
        ev = st.session_state.selected_event
        st.divider()
        st.subheader(f"🔍 פירוט משימה: {ev['title']}")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**תיאור:** {ev['extendedProps']['desc']}")
            st.write(f"**תדירות:** {ev['extendedProps']['rec']}")
        with c2:
            st.write(f"**סטטוס:** {ev['extendedProps']['status']}")
            if st.button("סגור פירוט"):
                st.session_state.selected_event = None
                st.rerun()

# --- 2. ניהול ומחיקה לצמיתות ---
elif choice == opt2:
    st.header(opt2)
    if df.empty:
        st.info("אין משימות.")
    else:
        st.dataframe(df, use_container_width=True)
        st.divider()
        task_id = st.selectbox("בחר ID של משימה למחיקה לצמיתות:", df["ID"].unique())
        if st.button("🗑️ מחק משימה לצמיתות"):
            updated_df = df[df["ID"] != task_id]
            conn.update(data=updated_df)
            st.success(f"משימה {task_id} נמחקה מהגיליון.")
            st.rerun()

# --- 3. הוספת משימה (כולל חודשי) ---
elif choice == opt3:
    st.header(opt3)
    with st.form("add_form"):
        t_name = st.text_input("שם המשימה")
        t_desc = st.text_area("תיאור")
        col1, col2 = st.columns(2)
        with col1:
            t_rec = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        with col2:
            t_date = st.date_input("תאריך התחלה", datetime.now())
        
        if st.form_submit_button("שמור משימה"):
            if t_name:
                next_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_row = pd.DataFrame([{"ID": next_id, "Task_Name": t_name, "Description": t_desc, "Recurring": t_rec, "Date": t_date.strftime("%Y-%m-%d"), "Warehouse_Done": "לא", "Final_Approval": "לא"}])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success("המשימה נוספה!")
                st.rerun()

# --- 4. ביצוע (מחסן) ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("אין משימות פתוחות.")
    else:
        for i, r in pending.iterrows():
            if st.button(f"סמן כבוצע: {r['Task_Name']}", key=f"d_{r['ID']}"):
                df.at[i, "Warehouse_Done"] = "כן"
                conn.update(data=df)
                st.rerun()

# --- 5. אישור סמנכ"ל ---
elif choice == opt5:
    st.header(opt5)
    to_app = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    if to_app.empty:
        st.info("אין משימות הממתינות לאישור.")
    else:
        for i, r in to_app.iterrows():
            if st.button(f"אשר סופית: {r['Task_Name']}", key=f"a_{r['ID']}"):
                df.at[i, "Final_Approval"] = "כן"
                conn.update(data=df)
                st.rerun()
