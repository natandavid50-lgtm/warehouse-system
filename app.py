import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import calendar as cal_lib
from streamlit_calendar import calendar

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# אתחול ה-State
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
    "➕ הוספת משימה", "📦 סידור עבודה שבועי (מחסן)", "✅ אישור סמנכ\"ל"
)

if user_role == "מנהל WMS":
    menu = [opt1, opt2, opt3, opt4, opt5]
elif user_role == "צוות מחסן":
    menu = [opt4, opt1]
else:
    menu = [opt1, opt5]

choice = st.sidebar.radio("ניווט:", menu)

# --- 1. לוח שנה אינטראקטיבי ---
if choice == opt1:
    st.header(opt1)
    events = []
    for _, r in df.iterrows():
        try:
            if r['Date'] == "לא צוין": continue
            base_date = pd.to_datetime(r['Date']).to_pydatetime()
            iterations = 30 if r['Recurring'] == "יומי" else 12 if r['Recurring'] == "שבועי" else 6 if r['Recurring'] == "דו-שבועי" else 4 if r['Recurring'] == "חודשי" else 1
            days_step = 1 if r['Recurring'] == "יומי" else 7 if r['Recurring'] == "שבועי" else 14 if r['Recurring'] == "דו-שבועי" else 30 if r['Recurring'] == "חודשי" else 0
            
            for i in range(iterations):
                curr = base_date + timedelta(days=i * days_step)
                color = "#28a745" if r['Final_Approval'] == "כן" else "#dc3545" if r['Warehouse_Done'] == "לא" else "#007bff"
                events.append({
                    "id": f"{r['ID']}_{i}",
                    "title": str(r['Task_Name']),
                    "start": curr.strftime("%Y-%m-%d"),
                    "color": color,
                    "extendedProps": {"orig_id": str(r['ID']), "desc": str(r['Description']), "rec": str(r['Recurring'])}
                })
        except: continue

    res = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 650})
    if res.get("eventClick"):
        st.session_state.selected_event = res["eventClick"]["event"]
    
    if st.session_state.selected_event:
        ev = st.session_state.selected_event
        st.info(f"**משימה:** {ev['title']} | **תיאור:** {ev['extendedProps']['desc']}")

# --- 4. סידור עבודה שבועי למחסן (התצוגה החדשה שביקשת) ---
elif choice == opt4:
    st.header("📦 סידור עבודה שבועי - צוות מחסן")
    
    # חישוב ימי השבוע הנוכחי (ראשון עד חמישי)
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7) # יום ראשון הקרוב/האחרון
    
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)
    
    for i, day_name in enumerate(days_names):
        target_date = start_of_week + timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        
        with cols[i]:
            st.markdown(f"### יום {day_name}\n**{target_date.strftime('%d/%m')}**")
            st.divider()
            
            # סינון משימות שחלות ביום הזה (כולל משימות חוזרות)
            day_tasks = []
            for _, r in df.iterrows():
                try:
                    base_date = pd.to_datetime(r['Date']).to_pydatetime()
                    # בדיקה אם המשימה חלה ביום הספציפי הזה בלוח
                    rec = r['Recurring']
                    diff = (target_date - base_date).days
                    is_today = False
                    
                    if diff == 0: is_today = True
                    elif rec == "יומי" and diff > 0: is_today = True
                    elif rec == "שבועי" and diff > 0 and diff % 7 == 0: is_today = True
                    elif rec == "דו-שבועי" and diff > 0 and diff % 14 == 0: is_today = True
                    elif rec == "חודשי" and diff > 0 and diff % 30 == 0: is_today = True
                    
                    if is_today:
                        status_icon = "✅" if r['Warehouse_Done'] == "כן" else "⏳"
                        st.write(f"{status_icon} **{r['Task_Name']}**")
                        if r['Warehouse_Done'] == "לא":
                            if st.button("בצע", key=f"btn_{r['ID']}_{date_str}"):
                                df.loc[df['ID'] == r['ID'], "Warehouse_Done"] = "כן"
                                conn.update(data=df)
                                st.rerun()
                        st.caption(f"ID: {r['ID']}")
                        st.divider()
                except: continue

# --- 2. ניהול ומחיקה ---
elif choice == opt2:
    st.header(opt2)
    st.dataframe(df, use_container_width=True)
    task_id = st.selectbox("בחר ID למחיקה:", df["ID"].unique())
    if st.button("🗑️ מחק לצמיתות"):
        conn.update(data=df[df["ID"] != task_id])
        st.success("נמחק!")
        st.rerun()

# --- 3. הוספת משימה ---
elif choice == opt3:
    st.header(opt3)
    with st.form("add"):
        n = st.text_input("שם")
        d = st.text_area("תיאור")
        r = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        dt = st.date_input("תאריך", datetime.now())
        if st.form_submit_button("שמור"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{"ID": new_id, "Task_Name": n, "Description": d, "Recurring": r, "Date": dt.strftime("%Y-%m-%d"), "Warehouse_Done": "לא", "Final_Approval": "לא"}])
            conn.update(data=pd.concat([df, new_row], ignore_index=True))
            st.rerun()

# --- 5. אישור סמנכ"ל ---
elif choice == opt5:
    st.header(opt5)
    for i, r in df[(df["Warehouse_Done"]=="כן") & (df["Final_Approval"]=="לא")].iterrows():
        if st.button(f"אשר: {r['Task_Name']}", key=f"app_{r['ID']}"):
            df.at[i, "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()
