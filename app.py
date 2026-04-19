import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# הגדרות עמוד
st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

# חיבור לנתונים
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Task_Name", "Description", "Recurring", "Date", "Warehouse_Done", "Final_Approval"])
        # ניקוי עמודות מיותרות וערכי NaN שגורמים לשגיאות JSON
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.fillna("לא צוין")
    except Exception as e:
        st.error(f"שגיאת טעינה מהגיליון: {e}")
        return pd.DataFrame()

df = load_data()

# --- תפריט צד ---
st.sidebar.title("מערכת ניהול מחסן")
user_role = st.sidebar.selectbox("בחר תפקיד:", ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"])
st.sidebar.divider()

opt1, opt2, opt3, opt4, opt5, opt6, opt7 = (
    "📅 לוח שנה", "➕ הוספת משימה", "🗑️ ביטול משימה", 
    "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום", "🧹 ניקוי היסטוריה"
)

menu = [opt1, opt2, opt3, opt4, opt5, opt6, opt7] if user_role == "מנהל WMS" else [opt4, opt1] if user_role == "צוות מחסן" else [opt6, opt1]
choice = st.sidebar.radio("ניווט:", menu)

# --- 1. דף לוח שנה (עם לוגיקת זיהוי תאריכים משופרת) ---
if choice == opt1:
    st.header(opt1)
    
    if df.empty:
        st.warning("לא נמצאו משימות בגיליון הנתונים.")
    else:
        events = []
        for index, r in df.iterrows():
            try:
                date_str = str(r['Date']).strip()
                if date_str == "לא צוין" or not date_str:
                    continue
                
                # מנגנון המרת תאריך גמיש למניעת ValueError
                try:
                    base_date = pd.to_datetime(date_str).to_pydatetime()
                except:
                    continue # אם התאריך ממש לא תקין, דלג עליו

                # הגדרת תדירות החזרות
                iterations = 1
                days_step = 0
                
                rec = r['Recurring']
                if rec == "יומי": iterations, days_step = 30, 1
                elif rec == "שבועי": iterations, days_step = 12, 7
                elif rec == "דו-שבועי": iterations, days_step = 8, 14
                elif rec == "חודשי": iterations, days_step = 4, 30
                
                for i in range(iterations):
                    current_date = base_date + timedelta(days=i * days_step)
                    
                    # קביעת צבע לפי סטטוס
                    color = "#28a745" if r['Final_Approval'] == "כן" else "#007bff"
                    if r['Warehouse_Done'] == "לא": color = "#dc3545"
                    
                    events.append({
                        "id": f"{r['ID']}_{i}",
                        "title": str(r['Task_Name']),
                        "start": current_date.strftime("%Y-%m-%d"),
                        "color": color,
                        "extendedProps": {
                            "orig_id": str(r['ID']),
                            "desc": str(r['Description']),
                            "recur": str(r['Recurring']),
                            "w_done": str(r['Warehouse_Done'])
                        }
                    })
            except Exception as e:
                continue

        if not events:
            st.error("הנתונים קיימים אך לא ניתן להציגם על הלוח. בדוק את פורמט התאריכים בגיליון.")
        else:
            st.info("לחץ על משימה כדי לראות את הפירוט המלא מתחת ללוח.")
            cal = calendar(events=events, options={"direction": "rtl", "locale": "he", "height": 600})
            
            if "eventClick" in cal:
                res = cal["eventClick"]["event"]
                st.divider()
                st.subheader(f"📋 פירוט משימה: {res['title']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**תיאור:** {res['extendedProps']['desc']}")
                    st.write(f"**מזהה:** {res['extendedProps']['orig_id']}")
                with col2:
                    st.write(f"**תדירות:** {res['extendedProps']['recur']}")
                    st.write(f"**בוצע במחסן:** {res['extendedProps']['w_done']}")

# --- 2. דף הוספת משימה (סדר שדות מקצועי) ---
elif choice == opt2:
    st.header(opt2)
    with st.form("task_form_final"):
        t_name = st.text_input("שם המשימה")
        t_desc = st.text_area("תיאור המשימה")
        
        col1, col2 = st.columns(2)
        with col1:
            t_recur = st.selectbox("תדירות חזרה", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        with col2:
            t_date = st.date_input("תאריך התחלה", datetime.now())
            
        if st.form_submit_button("✅ שמור משימה"):
            if t_name:
                next_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_row = pd.DataFrame([{
                    "ID": next_id, "Task_Name": t_name, "Description": t_desc,
                    "Recurring": t_recur, "Date": t_date.strftime("%Y-%m-%d"),
                    "Warehouse_Done": "לא", "Final_Approval": "לא"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success(f"המשימה '{t_name}' נוספה! עבור ללוח שנה כדי לראותה.")
                st.rerun()
            else:
                st.error("חובה להזין שם משימה")

# --- 4. ביצוע (מחסן) ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("אין משימות לביצוע.")
    else:
        for i, row in pending.iterrows():
            if st.button(f"סמן כבוצע: {row['Task_Name']}", key=f"d_{row['ID']}"):
                df.at[i, "Warehouse_Done"] = "כן"
                conn.update(data=df)
                st.rerun()

# --- 5. אישור סופי ---
elif choice == opt5:
    st.header(opt5)
    to_app = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    if to_app.empty:
        st.info("אין משימות הממתינות לאישור.")
    else:
        for i, row in to_app.iterrows():
            if st.button(f"אשר סופית: {row['Task_Name']}", key=f"a_{row['ID']}"):
                df.at[i, "Final_Approval"] = "כן"
                conn.update(data=df)
                st.rerun()

elif choice == opt6:
    st.header(opt6)
    st.dataframe(df)

elif choice == opt3:
    st.header(opt3)
    for i, row in df.iterrows():
        if st.button(f"מחק: {row['Task_Name']}", key=f"del_{row['ID']}"):
            conn.update(data=df.drop(i))
            st.rerun()

elif choice == opt7:
    st.header(opt7)
    if st.button("נקה היסטוריה (מאושרים)"):
        conn.update(data=df[df["Final_Approval"] != "כן"])
        st.rerun()
