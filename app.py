import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# --- ניהול נתונים מקומי (במקום Google Sheets) ---
DB_FILE = "warehouse_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        data = pd.read_csv(DB_FILE)
        # הבטחת קיום עמודות הכרחיות
        cols = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"]
        for col in cols:
            if col not in data.columns:
                data[col] = ""
        return data.fillna("")
    else:
        # יצירת בסיס נתונים חדש אם לא קיים
        return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

df = load_data()

# אתחול ה-State עבור לחיצה על אירועים
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

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

# --- 1. לוח שנה אינטראקטיבי ---
if choice == opt1:
    st.header(opt1)
    events = []
    for _, r in df.iterrows():
        try:
            base_date = pd.to_datetime(r['Date']).to_pydatetime()
            done_dates = str(r['Done_Dates']).split(",") if r['Done_Dates'] else []
            
            # לוגיקת חזרתיות
            iterations = 30 if r['Recurring'] == "יומי" else 12 if r['Recurring'] == "שבועי" else 8 if r['Recurring'] == "דו-שבועי" else 4 if r['Recurring'] == "חודשי" else 1
            step = 1 if r['Recurring'] == "יומי" else 7 if r['Recurring'] == "שבועי" else 14 if r['Recurring'] == "דו-שבועי" else 30 if r['Recurring'] == "חודשי" else 0
            
            for i in range(iterations):
                curr = base_date + timedelta(days=i * step)
                curr_str = curr.strftime("%Y-%m-%d")
                
                # צבעים: ירוק (מאושר), כחול (בוצע באותו יום), אדום (ממתין)
                color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff" if curr_str in done_dates else "#dc3545"
                
                events.append({
                    "id": f"{r['ID']}_{curr_str}",
                    "title": str(r['Task_Name']),
                    "start": curr_str,
                    "color": color,
                    "extendedProps": {"desc": r['Description'], "status": "בוצע" if curr_str in done_dates else "ממתין"}
                })
        except: continue

    res = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 650})
    
    if res.get("eventClick"):
        st.session_state.selected_event = res["eventClick"]["event"]
    
    if st.session_state.selected_event:
        ev = st.session_state.selected_event
        st.info(f"**משימה:** {ev['title']} | **תיאור:** {ev['extendedProps']['desc']} | **סטטוס:** {ev['extendedProps']['status']}")

# --- 2. ניהול ומחיקה ---
elif choice == opt2:
    st.header(opt2)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        tid = st.selectbox("בחר מזהה (ID) למחיקה:", df["ID"].unique())
        if st.button("🗑️ מחק משימה לצמיתות"):
            df = df[df["ID"] != tid]
            save_data(df)
            st.success("המשימה נמחקה")
            st.rerun()

# --- 3. הוספת משימה ---
elif choice == opt3:
    st.header(opt3)
    with st.form("add_task"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        rec = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        start_dt = st.date_input("תאריך התחלה", datetime.now())
        if st.form_submit_button("✅ שמור משימה"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 100
            new_row = pd.DataFrame([{"ID": new_id, "Task_Name": name, "Description": desc, "Recurring": rec, "Date": start_dt.strftime("%Y-%m-%d"), "Done_Dates": "", "Final_Approval": "לא"}])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("המשימה נשמרה במערכת")
            st.rerun()

# --- 4. סידור עבודה שבועי (צוות מחסן) ---
elif choice == opt4:
    st.header("📦 סידור עבודה שבועי - ראשון עד חמישי")
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    
    cols = st.columns(5)
    days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    
    for i, day in enumerate(days):
        target_dt = start_of_week + timedelta(days=i)
        t_str = target_dt.strftime("%Y-%m-%d")
        with cols[i]:
            st.subheader(f"{day} {target_dt.strftime('%d/%m')}")
            # לוגיקת הצגת משימות ליום ספציפי
            for idx, r in df.iterrows():
                try:
                    base = pd.to_datetime(r['Date']).to_pydatetime()
                    diff = (target_dt - base).days
                    show = False
                    if diff == 0: show = True
                    elif r['Recurring'] == "יומי" and diff > 0: show = True
                    elif r['Recurring'] == "שבועי" and diff > 0 and diff % 7 == 0: show = True
                    elif r['Recurring'] == "דו-שבועי" and diff > 0 and diff % 14 == 0: show = True
                    elif r['Recurring'] == "חודשי" and diff > 0 and diff % 30 == 0: show = True
                    
                    if show:
                        done_list = str(r['Done_Dates']).split(",")
                        if t_str in done_list:
                            st.write(f"✅ {r['Task_Name']}")
                        else:
                            st.write(f"⏳ {r['Task_Name']}")
                            if st.button("בצע", key=f"do_{r['ID']}_{t_str}"):
                                current_done = str(r['Done_Dates'])
                                new_done = f"{current_done},{t_str}".strip(",")
                                df.at[idx, "Done_Dates"] = new_done
                                save_data(df)
                                st.rerun()
                except: continue
            st.divider()

# --- 5. דשבורד מנהלים (סמנכ"ל) ---
elif choice == opt5:
    st.header("📊 דשבורד ניהולי")
    c1, c2, c3 = st.columns(3)
    c1.metric("סה\"כ משימות", len(df))
    done_count = sum([len(str(x).split(",")) for x in df['Done_Dates'] if x])
    c2.metric("ביצועים שדווחו", done_count)
    c3.metric("ממתינים לאישור סופי", len(df[df["Final_Approval"] != "כן"]))

    st.subheader("אישור סופי של משימות שבוצעו")
    to_approve = df[df["Final_Approval"] != "כן"]
    for i, r in to_approve.iterrows():
        if st.button(f"אשר לצמיתות: {r['Task_Name']}", key=f"fin_{r['ID']}"):
            df.at[i, "Final_Approval"] = "כן"
            save_data(df)
            st.success(f"משימה {r['Task_Name']} אושרה סופית")
            st.rerun()
