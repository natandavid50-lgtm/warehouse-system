import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    data = conn.read(ttl="0")
    data = data.dropna(how="all")
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים: {e}")
    st.stop()

# --- תפריט צדי ---
st.sidebar.title("הגדרות מערכת")
user_type = st.sidebar.selectbox("מי משתמש במערכת?", ["מנהל לוגיסטיקה", "צוות מחסן", "סמנכ\"ל/הנהלה"])
st.sidebar.divider()

# הוספת "ביטול משימות" לתפריט
menu_options = ["📅 לוח שנה", "➕ הוספת משימה", "📦 ביצוע (מחסן)", "✅ אישור סופי", "🗑️ ביטול משימות", "📊 דוח סיכום"]
choice = st.sidebar.radio("תפריט ניווט", menu_options)

# --- דף לוח שנה ---
if "📅 לוח שנה" in choice:
    st.header("📅 לוח משימות")
    calendar_events = []
    if not df.empty:
        for _, row in df.iterrows():
            desc = str(row.get("Description", ""))
            task_date_str = str(row.get("Date", ""))
            recurring = row.get("Recurring", "לא")
            if task_date_str and task_date_str != "None":
                try:
                    base_date = pd.to_datetime(task_date_str).date()
                    color = "#28a745" if row.get("Final_Approval") == "כן" else "#ffc107"
                    calendar_events.append({"title": f"#{row.get('ID', '?')} {desc[:15]}", "start": base_date.isoformat(), "color": color})
                    if row.get("Final_Approval") != "כן" and recurring != "לא":
                        for i in range(1, 5):
                            new_date = base_date + (timedelta(weeks=i) if recurring == "שבועי" else timedelta(days=i) if recurring == "יומי" else timedelta(days=i*30))
                            calendar_events.append({"title": f"🔄 {desc[:15]}", "start": new_date.isoformat(), "color": "#17a2b8"})
                except: continue
    calendar_options = {"headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,dayGridWeek"}, "initialView": "dayGridMonth", "direction": "rtl", "height": 600, "locale": "he"}
    calendar(events=calendar_events, options=calendar_options)

# --- דף ביטול משימות (החדש!) ---
elif "🗑️ ביטול משימות" in choice:
    st.header("🗑️ ניהול וביטול משימות")
    st.write("כאן ניתן למחוק משימות שהוספת בטעות מהמערכת.")
    
    if df.empty:
        st.info("אין משימות במערכת.")
    else:
        # מציגים רק משימות שעדיין לא אושרו סופית
        open_tasks = df[df["Final_Approval"] != "כן"]
        
        if open_tasks.empty:
            st.success("כל המשימות בוצעו ואושרו!")
        else:
            for i, row in open_tasks.iterrows():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"**#{row['ID']}** | {row['Date']} | {row['Description']} (נוצר ע\"י: {row.get('User', 'לא ידוע')})")
                with col2:
                    # כפתור מחיקה סופי
                    if st.button("בטל משימה ❌", key=f"del_{row['ID']}"):
                        # הסרת השורה מה-DataFrame
                        df = df.drop(i)
                        conn.update(data=df)
                        st.warning(f"משימה {row['ID']} נמחקה מהמערכת.")
                        st.rerun()

# --- הוספת משימה ---
elif "➕ הוספת משימה" in choice:
    st.header("➕ הוספת משימה חדשה")
    with st.form("task_form"):
        desc = st.text_area("תיאור המשימה")
        task_date = st.date_input("תאריך לביצוע", datetime.now())
        recurring = st.selectbox("האם זו משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
        if st.form_submit_button("שמור"):
            if desc:
                new_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                new_row = pd.DataFrame([{"ID": new_id, "Description": desc, "Warehouse_Done": "לא", "Final_Approval": "לא", "Date": task_date.strftime("%Y-%m-%d"), "Recurring": recurring, "User": user_type}])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success("המשימה נוספה!")
                st.rerun()

# --- שאר הדפים (ביצוע ואישור) ---
elif "📦 ביצוע" in choice:
    st.header("📦 משימות לביצוע")
    pending = df[df["Warehouse_Done"] == "לא"]
    for i, row in pending.iterrows():
        with st.expander(f"משימה #{row['ID']} - {row['Date']}"):
            st.write(row['Description'])
            if st.button(f"סמן כבוצע", key=f"d_{row['ID']}"):
                df.at[i, "Warehouse_Done"] = "כן"
                conn.update(data=df)
                st.rerun()

elif "✅ אישור" in choice:
    st.header("✅ אישור מנהל")
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    for i, row in to_approve.iterrows():
        col1, col2 = st.columns([4, 1])
        with col1: st.write(f"**#{row['ID']}** | {row['Date']} | {row['Description']}")
        with col2:
            if st.button(f"אשר {row['ID']}", key=f"app_{row['ID']}"):
                df.at[i, "Final_Approval"] = "כן"
                if row.get("Recurring") != "לא":
                    # יצירת משימה חוזרת בגיליון
                    new_id = int(df["ID"].max() + 1)
                    base_dt = pd.to_datetime(row['Date'])
                    next_dt = base_dt + (timedelta(weeks=1) if row['Recurring'] == "שבועי" else timedelta(days=1) if row['Recurring'] == "יומי" else timedelta(days=30))
                    new_task = pd.DataFrame([{"ID": new_id, "Description": row['Description'], "Warehouse_Done": "לא", "Final_Approval": "לא
