import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# הגדרות עברית מראש כדי למנוע שגיאות סינטקס
TITLE = "מערכת ניהול מחסן"
ROLE_LABEL = "בחר תפקיד:"
NAV_LABEL = "תפריט ניווט:"
SUCCESS_MSG = "המשימה נוספה בהצלחה"
DELETE_CONFIRM = "המשימה נמחקה"

st.set_page_config(page_title=TITLE, layout="wide")

# חיבור לגיליון
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    data = conn.read(ttl="0")
    # ניקוי שורות ריקות למניעת כפילויות במפתחות
    data = data.dropna(subset=["ID", "Description"], how="all")
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

# --- תפריט צדי (Radio) ---
st.sidebar.title(TITLE)
roles = ["מנהל WMS", "צוות מחסן", "סמנכ\"ל"]
user_role = st.sidebar.selectbox(ROLE_LABEL, roles)
st.sidebar.divider()

# הגדרת אופציות התפריט
opt1, opt2, opt3, opt4, opt5, opt6 = "📅 לוח שנה", "➕ הוספת משימה", "🗑️ ביטול משימה", "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום"

if user_role == "מנהל WMS":
    menu_options = [opt1, opt2, opt3, opt4, opt5, opt6]
elif user_role == "צוות מחסן":
    menu_options = [opt4, opt1]
else:
    menu_options = [opt6, opt1]

choice = st.sidebar.radio(NAV_LABEL, menu_options)

# --- לוח שנה ---
if choice == opt1:
    st.header(opt1)
    cal_events = []
    for i, r in df.iterrows():
        if pd.notnull(r.get("Date")):
            color = "#28a745" if r.get("Final_Approval") == "כן" else "#ffc107"
            cal_events.append({
                "title": f"#{int(r['ID'])} {str(r['Description'])[:15]}",
                "start": str(r["Date"]),
                "color": color
            })
    
    cal_opts = {"direction": "rtl", "locale": "he", "height": 500, "initialView": "dayGridMonth"}
    calendar(events=cal_events, options=cal_opts)

# --- הוספת משימה ---
elif choice == opt2:
    st.header(opt2)
    with st.form("task_form"):
        desc = st.text_input("תיאור המשימה")
        date_val = st.date_input("תאריך לביצוע", datetime.now())
        recur_val = st.selectbox("חזרה:", ["לא", "יומי", "שבועי", "חודשי"])
        if st.form_submit_button("שמור"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{
                "ID": new_id, "Description": desc, "Warehouse_Done": "לא",
                "Final_Approval": "לא", "Date": date_val.strftime("%Y-%m-%d"),
                "Recurring": recur_val, "User": user_role
            }])
            conn.update(data=pd.concat([df, new_row], ignore_index=True))
            st.success(SUCCESS_MSG)
            st.rerun()

# --- ביטול משימה (פתרון ל-Duplicate Key) ---
elif choice == opt3:
    st.header(opt3)
    # סינון משימות שניתן לבטל (טרם אושרו)
    to_cancel = df[df["Final_Approval"] != "כן"].dropna(subset=["ID"])
    if to_cancel.empty:
        st.info("אין משימות לביטול")
    else:
        for i, r in to_cancel.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(f"#{int(r['ID'])} | {r['Date']} | {r['Description']}")
            # שימוש באינדקס i מבטיח מפתח ייחודי לכפתור
            if c2.button("ביטול ❌", key=f"cancel_btn_{i}"):
                df = df.drop(i)
                conn.update(data=df)
                st.warning(DELETE_CONFIRM)
                st.rerun()

# --- ביצוע מחסן ---
elif choice == opt4:
    st.header(opt4)
    pending = df[df["Warehouse_Done"] != "כן"]
    for i, r in pending.iterrows():
        with st.expander(f"#{int(r['ID'])} - {r['Date']}"):
            st.write(r["Description"])
            if st.button("בוצע ✅", key=f"done_btn_{i}"):
                df.at[i, "Warehouse_Done"] = "כן"
                conn.update(data=df)
                st.rerun()

# --- אישור סופי (פר משימה) ---
elif choice == opt5:
    st.header(opt5)
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] != "כן")]
    for i, r in to_approve.iterrows():
        ca, cb = st.columns([5, 1])
        ca.write(f"#{int(r['ID'])} | {r['Description']}")
        if cb.button("אשר ✅", key=f"app_btn_{i}"):
            df.at[i, "Final_Approval"] = "כן"
            # יצירת המשימה הבאה במידה והיא חוזרת
            if r.get("Recurring") in ["יומי", "שבועי", "חודשי"]:
                base_d = pd.to_datetime(r["Date"])
                if r["Recurring"] == "יומי": next_d = base_d + timedelta(days=1)
                elif r["Recurring"] == "שבועי": next_d = base_d + timedelta(weeks=1)
                else: next_d = base_d + timedelta(days=30)
                
                new_task = pd.DataFrame([{
                    "ID": int(df["ID"].max() + 1), "Description": r["Description"],
                    "Warehouse_Done": "לא", "Final_Approval": "לא",
                    "Date": next_d.strftime("%Y-%m-%d"), "Recurring": r["Recurring"],
                    "User": r["User"]
                }])
                df = pd.concat([df, new_task], ignore_index=True)
            conn.update(data=df)
            st.rerun()

elif choice == opt6:
    st.header(opt6)
    st.dataframe(df.dropna(subset=["ID"]), use_container_width=True)
