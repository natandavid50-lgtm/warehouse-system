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
    # ניקוי עמודות זבל
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

menu_options = ["📅 לוח שנה", "➕ הוספת משימה", "📦 ביצוע (מחסן)", "✅ אישור סופי", "📊 דוח סיכום"]
choice = st.sidebar.radio("תפריט ניווט", menu_options)

# --- לוגיקת לוח שנה עם תמיכה במשימות חוזרות ---
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
                    
                    # הצגת המשימה המקורית
                    calendar_events.append({
                        "title": f"#{row.get('ID', '?')} {desc[:15]}",
                        "start": base_date.isoformat(),
                        "color": color,
                    })
                    
                    # לוגיקה ויזואלית לחזרות (מציג קדימה בלוח השנה למשך חודשיים)
                    if row.get("Final_Approval") != "כן": # רק משימות פתוחות חוזרות ויזואלית
                        for i in range(1, 9): # עד 8 חזרות קדימה
                            new_date = None
                            if recurring == "יומי":
                                new_date = base_date + timedelta(days=i)
                            elif recurring == "שבועי":
                                new_date = base_date + timedelta(weeks=i)
                            elif recurring == "חודשי":
                                new_date = base_date + timedelta(days=i*30)
                            
                            if new_date:
                                calendar_events.append({
                                    "title": f"🔄 {desc[:15]}",
                                    "start": new_date.isoformat(),
                                    "color": "#17a2b8", # צבע כחול למשימה עתידית חוזרת
                                })
                except:
                    continue

    calendar_options = {"headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,dayGridWeek"}, "initialView": "dayGridMonth", "direction": "rtl", "height": 600, "locale": "he"}
    calendar(events=calendar_events, options=calendar_options)

# --- הוספת משימה עם אפשרויות חזרה ---
elif "➕ הוספת משימה" in choice:
    st.header("➕ הוספת משימה חדשה")
    with st.form("task_form"):
        desc = st.text_area("תיאור המשימה")
        task_date = st.date_input("תאריך לביצוע", datetime.now())
        recurring = st.selectbox("האם זו משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
        
        if st.form_submit_button("שמור"):
            if desc:
                new_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                new_row = pd.DataFrame([{
                    "ID": new_id, "Description": desc, "Warehouse_Done": "לא", 
                    "Final_Approval": "לא", "Date": task_date.strftime("%Y-%m-%d"), 
                    "Recurring": recurring, "User": user_type
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success(f"המשימה נוספה! (חזרה: {recurring})")
                st.rerun()

# --- אישור סופי - משימה בודדת ---
elif "✅ אישור" in choice:
    st.header("✅ אישור מנהל (לפי משימה)")
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    
    if to_approve.empty:
        st.info("אין משימות הממתינות לאישור.")
    else:
        for i, row in to_approve.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**#{row['ID']}** | {row['Date']} | {row['Description']}")
            with col2:
                if st.button(f"אשר משימה {row['ID']}", key=f"app_{row['ID']}"):
                    df.at[i, "Final_Approval"] = "כן"
                    # אם זו משימה חוזרת שבוצעה, המערכת יכולה ליצור אוטומטית את המשימה הבאה בגיליון
                    if row.get("Recurring") != "לא":
                        new_id = int(df["ID"].max() + 1)
                        base_dt = pd.to_datetime(row['Date'])
                        if row['Recurring'] == "יומי": next_dt = base_dt + timedelta(days=1)
                        elif row['Recurring'] == "שבועי": next_dt = base_dt + timedelta(weeks=1)
                        else: next_dt = base_dt + timedelta(days=30)
                        
                        new_task = pd.DataFrame([{
                            "ID": new_id, "Description": row['Description'], "Warehouse_Done": "לא",
                            "Final_Approval": "לא", "Date": next_dt.strftime("%Y-%m-%d"),
                            "Recurring": row['Recurring'], "User": row['User']
                        }])
                        df = pd.concat([df, new_task], ignore_index=True)
                    
                    conn.update(data=df)
                    st.success(f"משימה {row['ID']} אושרה!")
                    st.rerun()

elif "📊 דוח" in choice:
    st.header("📊 דוח סיכום")
    st.dataframe(df, use_container_width=True)

# ביצוע מחסן (נשאר דומה)
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
