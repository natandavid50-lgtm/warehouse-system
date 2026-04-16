import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# הגדרות שפה גלובליות
TITLE = "מערכת ניהול מחסן"
CALENDAR_TAB = "📅 לוח משימות מעוצב"
SUCCESS_MSG = "המשימה נוספה"

st.set_page_config(page_title=TITLE, layout="wide") # פריסה רחבה למסך

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="0")
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        return data.dropna(subset=["ID", "Description"], how="all")
    except:
        return pd.DataFrame()

df = load_data()

# וידוא עמודות למניעת KeyError
for col in ["ID", "Final_Approval", "Date", "Description"]:
    if col not in df.columns:
        df[col] = None

# --- תצוגת לוח שנה משופרת ---
st.header(CALENDAR_TAB)

cal_events = []
for i, r in df.iterrows():
    if pd.notnull(r.get("Date")) and pd.notnull(r.get("ID")):
        # התאמת צבעים לפי סטטוס
        is_approved = r.get("Final_Approval") == "כן"
        event_color = "#28a745" if is_approved else "#007bff" # ירוק למאושר, כחול לחדש
        
        # בניית כותרת האירוע
        task_id = int(r['ID'])
        desc = str(r['Description'])[:20]
        event_title = f"#{task_id} - {desc}"
        
        cal_events.append({
            "title": event_title,
            "start": str(r["Date"]),
            "color": event_color,
            "allDay": True,
            "resourceId": i
        })

# הגדרות לוח שנה למראה מותאם למסך
calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,listWeek",
    },
    "initialView": "dayGridMonth",
    "direction": "rtl",
    "locale": "he",
    "height": 700, # גובה מותאם למסך
}

# הצגת לוח השנה
state = calendar(
    events=cal_events,
    options=calendar_options,
    custom_css="""
        .fc-event-main {
            font-size: 14px;
            padding: 2px;
        }
        .fc-toolbar-title {
            font-size: 1.5rem !important;
            color: #1f2937;
        }
    """,
    key='warehouse_calendar'
)

# הצגת פרטי משימה בלחיצה (אופציונלי)
if state.get("eventClick"):
    clicked_event = state["eventClick"]["event"]
    st.info(f"משימה שנבחרה: {clicked_event['title']}")
