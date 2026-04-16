import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# הגדרות שפה גלובליות למניעת שגיאות Syntax
TITLE = "מערכת ניהול מחסן"
ROLE_LABEL = "בחר תפקיד:"
NAV_LABEL = "תפריט ניווט:"
SUCCESS_MSG = "המשימה נוספה בהצלחה"
DELETE_CONFIRM = "המשימה נמחקה"
CLEAR_HISTORY_MSG = "היסטוריית המשימות נוקתה"

st.set_page_config(page_title=TITLE, layout="wide")

# חיבור לגיליון
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        if data is None or data.empty:
            return pd.DataFrame(columns=["ID", "Description", "Warehouse_Done", "Final_Approval", "Date", "Recurring", "User"])
        
        # ניקוי עמודות לא רלוונטיות ושורות ריקות
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        data = data.dropna(subset=["ID", "Description"], how="all")
        return data
    except Exception as e:
        st.error(f"שגיאת טעינה: {e}")
        return pd.DataFrame()

df = load_data()

# וידוא עמודות קריטיות למניעת KeyError
for col in ["ID", "Final_Approval", "Warehouse_Done", "Date"]:
    if col not in df.columns:
        df[col] = None

# --- הגדרת אפשרויות התפריט ---
opt1, opt2, opt3, opt4, opt5, opt6, opt7 = (
    "📅 לוח שנה", "➕ הוספת משימה", "🗑️ ביטול משימה", 
    "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום", "🧹 ניקוי היסטוריה"
)

st.sidebar.title(TITLE)
roles = ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"]
user_role = st.sidebar.selectbox(ROLE_LABEL, roles)
st.sidebar.divider()

if user_role == "מנהל WMS":
    menu_options = [opt1, opt2, opt3, opt4, opt5, opt6, opt7]
elif user_role == "צוות מחסן":
    menu_options = [opt4, opt1]
else:
    menu_options = [opt6, opt1]

choice = st.sidebar.radio(NAV_LABEL, menu_options)

# --- 1. לוח שנה ---
if choice == opt1:
    st.header(opt1)
    cal_events = []
    for i, r in df.iterrows():
        if pd.notnull(r.get("Date")) and pd.notnull(r.get("ID")):
            color = "#28a745" if r.get("Final_Approval") == "כן" else "#ffc107"
            cal_events.append({
                "title": f"#{int(r['ID'])} {str(r['Description'])[:15]}",
                "start": str(r["Date"]),
                "color": color
            })
    calendar(events=cal_events, options={"direction": "rtl", "locale": "he", "initialView": "dayGridMonth"})

# --- 2. הוספת משימה ---
elif choice == opt2:
    st.header(opt2)
    with st.form("task_form"):
        desc = st.text_input("תיאור המשימה")
        date_val = st.date_input("תאריך לביצוע", datetime.now())
        recur_val = st.selectbox("חזרה:", ["לא", "יומי", "שבועי", "חודשי"])
        if st.form_submit_button("שמור"):
            new_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
            new_row = pd.DataFrame([{
                "ID": new_id, "Description": desc, "Warehouse_Done": "לא",
                "Final_Approval": "לא", "Date": date_val.strftime("%Y-%m-%d"),
                "Recurring": recur_val, "User": user_role
            }])
            conn.update(data=pd.concat([df, new_row], ignore_index=True))
            st.success(SUCCESS_MSG)
            st.rerun()

# --- 3. ביטול משימה ---
elif choice == opt3:
    st.header(opt3)
    to_cancel = df[df["Final_Approval"] != "כן"].dropna(subset=["ID"])
    for i, r in to_cancel.iterrows():
        c1, c2 = st.columns([5, 1])
        c1.write(f"#{int(r['ID'])} | {r['Description']}")
        if c2.button("מחק ❌", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.warning(DELETE_CONFIRM)
            st.rerun()

# --- 4. ביצוע מחסן ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] != "כן"].dropna(subset=["ID"])
    for i, r in pending.iterrows():
        with st.expander(f"#{int(r['ID'])} - {r['Description']}"):
            if st.button("סמן כבוצע ✅", key=f"done_{i}"):
                df.at[i, "Warehouse_Done"] = "כן"
                conn.update(data=df)
                st.rerun()

# --- 5. אישור סופי ---
elif choice == opt5:
    st.header(opt5)
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] != "כן")].dropna(subset=["ID"])
    for i, r in to_approve.iterrows():
        c1, c2 = st.columns([5, 1])
        c1.write(f"#{int(r['ID'])} | {r['Description']}")
        if c2.button("אשר ✅", key=f"app_{i}"):
            df.at[i, "Final_Approval"] = "כן"
            conn.update(data=df)
            st.rerun()

# --- 6. דוח סיכום ---
elif choice == opt6:
    st.header(opt6)
    st.dataframe(df.dropna(subset=["ID"]), use_container_width=True)

# --- 7. ניקוי היסטוריה (התיקון ל-KeyError) ---
elif choice == opt7:
    st.header(opt7)
    # וידוא סינון בטוח של משימות שהושלמו
    completed = df[df["Final_Approval"] == "כן"].dropna(subset=["ID"])
    
    if completed.empty:
        st.info("אין משימות שהושלמו למחיקה.")
    else:
        if st.button("נקה את כל ההיסטוריה ⚠️"):
            df = df[df["Final_Approval"] != "כן"]
            conn.update(data=df)
            st.success(CLEAR_HISTORY_MSG)
            st.rerun()
        
        st.divider()
        for i, r in completed.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(f"#{int(r['ID'])} |
