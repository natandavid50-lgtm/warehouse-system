import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# --- ניהול נתונים מקומי יציב ---
DB_FILE = "warehouse_db.csv"

def load_data():
    # אם הקובץ קיים, נטען אותו
    if os.path.exists(DB_FILE):
        try:
            data = pd.read_csv(DB_FILE)
            # מוודא שכל העמודות הקריטיות קיימות כדי למנוע קריסה
            required_cols = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"]
            for col in required_cols:
                if col not in data.columns:
                    data[col] = ""
            return data.fillna("")
        except Exception:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])
    else:
        # יצירת בסיס נתונים ריק בפעם הראשונה
        new_df = pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates", "Final_Approval"])
        new_df.to_csv(DB_FILE, index=False)
        return new_df

def save_data(df_to_save):
    # שמירה פיזית של הנתונים לקובץ
    df_to_save.to_csv(DB_FILE, index=False)

# טעינת הנתונים למערכת
if "df" not in st.session_state:
    st.session_state.df = load_data()

# אתחול ה-State עבור הלוח
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

menu = [opt1, opt2, opt3, opt4, opt5] if user_role == "מנהל WMS" else [opt4, opt1] if user_role == "צוות מחסן" else [opt5, opt1]
choice = st.sidebar.radio("ניווט:", menu)

# --- 1. לוח שנה עם צביעה יומית פרטנית ---
if choice == opt1:
    st.header(opt1)
    events = []
    for _, r in st.session_state.df.iterrows():
        try:
            base_date = pd.to_datetime(r['Date']).to_pydatetime()
            done_dates = str(r['Done_Dates']).split(",") if r['Done_Dates'] else []
            
            # הגדרת כמות חזרות להצגה
            iters = 30 if r['Recurring'] == "יומי" else 12 if r['Recurring'] == "שבועי" else 8 if r['Recurring'] == "דו-שבועי" else 4 if r['Recurring'] == "חודשי" else 1
            gap = 1 if r['Recurring'] == "יומי" else 7 if r['Recurring'] == "שבועי" else 14 if r['Recurring'] == "דו-שבועי" else 30 if r['Recurring'] == "חודשי" else 0
            
            for i in range(iters):
                curr = base_date + timedelta(days=i * gap)
                curr_str = curr.strftime("%Y-%m-%d")
                
                # צביעה: רק יום שבוצע נצבע בכחול
                color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff" if curr_str in done_dates else "#dc3545"
                
                events.append({
                    "id": f"{r['ID']}_{curr_str}",
                    "title": r['Task_Name'],
                    "start": curr_str,
                    "color": color,
                    "extendedProps": {"desc": r['Description'], "id": r['ID'], "date": curr_str}
                })
        except: continue

    res = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})
    if res.get("eventClick"):
        st.session_state.selected_event = res["eventClick"]["event"]
    
    if st.session_state.selected_event:
        ev = st.session_state.selected_event
        st.info(f"🔍 **משימה:** {ev['title']} | **תאריך:** {ev['extendedProps']['date']}\n\n**תיאור:** {ev['extendedProps']['desc']}")

# --- 4. סידור עבודה שבועי לצוות מחסן ---
elif choice == opt4:
    st.header("📦 סידור עבודה שבועי (ראשון-חמישי)")
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    
    cols = st.columns(5)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    
    for i, name in enumerate(days_names):
        target_dt = start_of_week + timedelta(days=i)
        t_str = target_dt.strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f"### יום {name}\n**{target_dt.strftime('%d/%m')}**")
            for idx, r in st.session_state.df.iterrows():
                # לוגיקה לבדיקה אם המשימה רלוונטית ליום זה
                try:
                    base = pd.to_datetime(r['Date']).to_pydatetime()
                    diff = (target_dt - base).days
                    is_hit = (diff == 0) or (r['Recurring'] == "יומי" and diff > 0) or \
                             (r['Recurring'] == "שבועי" and diff > 0 and diff % 7 == 0) or \
                             (r['Recurring'] == "דו-שבועי" and diff > 0 and diff % 14 == 0) or \
                             (r['Recurring'] == "חודשי" and diff > 0 and diff % 30 == 0)
                    
                    if is_hit:
                        done_list = str(r['Done_Dates']).split(",")
                        if t_str in done_list:
                            st.success(f"✅ {r['Task_Name']}")
                        else:
                            st.write(f"⏳ {r['Task_Name']}")
                            if st.button("בצע", key=f"d_{r['ID']}_{t_str}"):
                                # הוספת התאריך הספציפי לרשימת הביצועים
                                existing = str(r['Done_Dates'])
                                updated_done = f"{existing},{t_str}".strip(",")
                                st.session_state.df.at[idx, "Done_Dates"] = updated_done
                                save_data(st.session_state.df)
                                st.rerun()
                except: continue
            st.divider()

# --- 3. הוספת משימה חדשה ---
elif choice == opt3:
    st.header("➕ הוספת משימה חדשה")
    with st.form("add_task_form"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        start_date = st.date_input("תאריך התחלה", datetime.now())
        
        if st.form_submit_button("שמור משימה"):
            if name:
                new_id = int(st.session_state.df["ID"].max() + 1) if not st.session_state.df.empty else 100
                new_row = pd.DataFrame([{
                    "ID": new_id, "Task_Name": name, "Description": desc, 
                    "Recurring": freq, "Date": start_date.strftime("%Y-%m-%d"), 
                    "Done_Dates": "", "Final_Approval": "לא"
                }])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.success("המשימה נשמרה בהצלחה!")
                st.rerun()

# --- 2. ניהול ומחיקה ---
elif choice == opt2:
    st.header("⚙️ ניהול משימות")
    st.dataframe(st.session_state.df, use_container_width=True)
    if not st.session_state.df.empty:
        to_del = st.selectbox("בחר משימה למחיקה:", st.session_state.df["Task_Name"])
        if st.button("מחק לצמיתות"):
            st.session_state.df = st.session_state.df[st.session_state.df["Task_Name"] != to_del]
            save_data(st.session_state.df)
            st.rerun()

# --- 5. דשבורד סמנכ"ל ---
elif choice == opt5:
    st.header("📊 דשבורד מנהלים")
    c1, c2 = st.columns(2)
    c1.metric("סה\"כ משימות", len(st.session_state.df))
    done_total = sum([len(str(x).split(",")) for x in st.session_state.df['Done_Dates'] if x])
    c2.metric("ביצועים בשטח", done_total)
    
    st.subheader("אישור סופי למשימות")
    for i, r in st.session_state.df[st.session_state.df["Final_Approval"] != "כן"].iterrows():
        if st.button(f"אשר סופית: {r['Task_Name']}", key=f"f_{r['ID']}"):
            st.session_state.df.at[i, "Final_Approval"] = "כן"
            save_data(st.session_state.df)
            st.rerun()
