import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.fillna("")
    except Exception:
        return pd.DataFrame()

df = load_data()

# --- תפריט צד ---
st.sidebar.title("מערכת ניהול מחסן")
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

opt1, opt2, opt3, opt4, opt5 = (
    "📅 לוח שנה אינטראקטיבי", "⚙️ ניהול ומחיקה", 
    "➕ הוספת משימה", "📦 סידור עבודה שבועי", "📊 דשבורד מנהלים"
)

if user_role == "מנהל WMS":
    menu = [opt1, opt2, opt3, opt4, opt5]
elif user_role == "צוות מחסן":
    menu = [opt4, opt1]
else:
    menu = [opt5, opt1]

choice = st.sidebar.radio("ניווט:", menu)

# --- לוגיקת צביעה חכמה ללוח שנה ---
if choice == opt1:
    st.header(opt1)
    events = []
    for _, r in df.iterrows():
        try:
            base_date = pd.to_datetime(r['Date']).to_pydatetime()
            done_dates = str(r.get('Done_Dates', "")).split(",") # רשימת תאריכים שבוצעו
            
            iterations = 30 if r['Recurring'] == "יומי" else 12 if r['Recurring'] == "שבועי" else 6 if r['Recurring'] == "דו-שבועי" else 4 if r['Recurring'] == "חודשי" else 1
            days_step = 1 if r['Recurring'] == "יומי" else 7 if r['Recurring'] == "שבועי" else 14 if r['Recurring'] == "דו-שבועי" else 30 if r['Recurring'] == "חודשי" else 0
            
            for i in range(iterations):
                curr = base_date + timedelta(days=i * days_step)
                curr_str = curr.strftime("%Y-%m-%d")
                
                # צביעה פרטנית: אם התאריך הספציפי ברשימת הבוצעו -> כחול. אחרת -> אדום.
                color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff" if curr_str in done_dates else "#dc3545"
                
                events.append({
                    "id": f"{r['ID']}_{curr_str}",
                    "title": r['Task_Name'],
                    "start": curr_str,
                    "color": color,
                    "extendedProps": {"desc": r['Description'], "id": r['ID']}
                })
        except: continue

    res = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 650})
    if res.get("eventClick"):
        st.session_state.selected_event = res["eventClick"]["event"]
    if st.session_state.selected_event:
        st.info(f"**משימה:** {st.session_state.selected_event['title']} | {st.session_state.selected_event['extendedProps']['desc']}")

# --- דשבורד סמנכ"ל משופר ---
elif choice == opt5:
    st.header("📊 דשבורד בקרה למנהלים")
    
    col1, col2, col3 = st.columns(3)
    total_tasks = len(df)
    # ספירת ביצועים כוללת מתוך מחרוזת התאריכים
    total_done = sum([len(str(x).split(",")) if x else 0 for x in df['Done_Dates']])
    
    col1.metric("סה\"כ משימות מוגדרות", total_tasks)
    col2.metric("סה\"כ ביצועים בשטח", total_done)
    col3.metric("ממתין לאישור סופי", len(df[df["Final_Approval"] != "כן"]))

    st.subheader("פירוט סטטוס משימות")
    st.table(df[["ID", "Task_Name", "Recurring", "Final_Approval"]])
    
    st.divider()
    st.subheader("✅ אישור משימות שבוצעו")
    to_app = df[df["Final_Approval"] != "כן"]
    for i, r in to_app.iterrows():
        if st.button(f"אשר סופית: {r['Task_Name']}", key=f"ap_{r['ID']}"):
            df.at[i, "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()

# --- סידור עבודה לצוות (עם שמירת תאריך ספציפי) ---
elif choice == opt4:
    st.header("📦 סידור עבודה יומי")
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.subheader(f"משימות להיום: {today_str}")
    
    for i, r in df.iterrows():
        # בדיקה אם המשימה חלה היום (לוגיקה דומה ללוח שנה)
        done_dates = str(r.get('Done_Dates', "")).split(",")
        if st.button(f"סמן כבוצע: {r['Task_Name']}", key=f"work_{r['ID']}"):
            if today_str not in done_dates:
                new_done = f"{r['Done_Dates']},{today_str}".strip(",")
                df.at[i, "Done_Dates"] = new_done
                conn.update(data=df)
                st.success(f"בוצע ב-{today_str}!")
                st.rerun()

# --- שאר הדפים (הוספה וניהול) נשארים כפי שהיו ---
elif choice == opt3:
    st.header(opt3)
    with st.form("add"):
        n = st.text_input("שם המשימה")
        r = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        dt = st.date_input("תאריך התחלה")
        if st.form_submit_button("שמור"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{"ID": new_id, "Task_Name": n, "Description": "", "Recurring": r, "Date": dt.strftime("%Y-%m-%d"), "Done_Dates": "", "Final_Approval": "לא"}])
            conn.update(data=pd.concat([df, new_row], ignore_index=True))
            st.rerun()

elif choice == opt2:
    st.header(opt2)
    st.dataframe(df)
    tid = st.selectbox("מחק ID:", df["ID"].unique())
    if st.button("מחק"):
        conn.update(data=df[df["ID"] != tid])
        st.rerun()
