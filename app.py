import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar as cal_lib
import io
import hashlib
import random

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    from streamlit_calendar import calendar as st_calendar
    HAS_CAL = True
except ImportError:
    HAS_CAL = False

# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="WMS • אחים כהן",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📦",
)

ADMIN_HASH = hashlib.sha256(b"1234").hexdigest()
SESSION_MINS = 60
WORKERS = ["יוסי כהן", "דוד לוי", "מיכל אברהם", "אחמד חסן", "רינה שמיר", "ברק נחמיאס"]
PRIS  = ["רגיל", "דחוף", "גבוה", "נמוך"]
CATS  = ["כללי", "בטיחות", "לוגיסטיקה", "ניקיון", "תחזוקה", "ספירה"]
RECUR = ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"]

# ═══════════════════════════════════════════════════════════════════════════════
#  SEED TASKS — 40 משימות hardcoded
# ═══════════════════════════════════════════════════════════════════════════════
SEED_TASKS = [
    # יומיות
    {"id":1,  "name":"פתיחת מחסן",               "desc":"פתיחת שערים, בדיקת חשמל, מצלמות, מערכת אזעקה",         "rec":"יומי",     "date":"2026-01-01","pri":"דחוף", "cat":"בטיחות",    "worker":"יוסי כהן"},
    {"id":2,  "name":"בדיקת טמפרטורות",           "desc":"רישום ב-3 נקודות מדידה, עדכון בטבלה",                  "rec":"יומי",     "date":"2026-01-01","pri":"דחוף", "cat":"בטיחות",    "worker":"דוד לוי"},
    {"id":3,  "name":"סיבוב מחסן בוקר",           "desc":"בדיקת מעברים, סימון חסימות, דיווח חריגים",             "rec":"יומי",     "date":"2026-01-01","pri":"גבוה", "cat":"לוגיסטיקה", "worker":"מיכל אברהם"},
    {"id":4,  "name":"עדכון יומן קבלה",           "desc":"רישום כל הספקים, כמויות, מספרי הזמנה",                 "rec":"יומי",     "date":"2026-01-01","pri":"רגיל", "cat":"לוגיסטיקה", "worker":"אחמד חסן"},
    {"id":5,  "name":"ניקוי רצפה — אזור A",       "desc":"שטיפה עם מגב וחומר ניקוי, ייבוש, פינוי אשפה",          "rec":"יומי",     "date":"2026-01-01","pri":"רגיל", "cat":"ניקיון",    "worker":"רינה שמיר"},
    {"id":6,  "name":"ניקוי רצפה — אזור B",       "desc":"שטיפה עם מגב וחומר ניקוי, ייבוש, פינוי אשפה",          "rec":"יומי",     "date":"2026-01-01","pri":"רגיל", "cat":"ניקיון",    "worker":"ברק נחמיאס"},
    {"id":7,  "name":"בדיקת ציוד חירום",          "desc":"עזרה ראשונה, כיבאים, יציאות חירום — תקינות",           "rec":"יומי",     "date":"2026-01-01","pri":"דחוף", "cat":"בטיחות",    "worker":"יוסי כהן"},
    {"id":8,  "name":"סגירת מחסן",                "desc":"נעילת שערים, כיבוי אורות ומערכות, הפעלת אזעקה",        "rec":"יומי",     "date":"2026-01-01","pri":"דחוף", "cat":"בטיחות",    "worker":"דוד לוי"},
    {"id":9,  "name":"עדכון סטטוס הזמנות",        "desc":"בדיקת מערכת הזמנות, עדכון סטטוס לוגיסטיקה",           "rec":"יומי",     "date":"2026-01-01","pri":"גבוה", "cat":"לוגיסטיקה", "worker":"מיכל אברהם"},
    {"id":10, "name":"ניקוי שירותים ופינה",       "desc":"חיטוי שירותים, מילוי חומרי ניקוי",                     "rec":"יומי",     "date":"2026-01-01","pri":"רגיל", "cat":"ניקיון",    "worker":"רינה שמיר"},

    # שבועיות
    {"id":11, "name":"ספירת מלאי — מדף 1-10",    "desc":"ספירה ידנית + עדכון מערכת + תיעוד פערים",              "rec":"שבועי",    "date":"2026-01-04","pri":"גבוה", "cat":"ספירה",     "worker":"יוסי כהן"},
    {"id":12, "name":"ספירת מלאי — מדף 11-20",   "desc":"ספירה ידנית + עדכון מערכת + תיעוד פערים",              "rec":"שבועי",    "date":"2026-01-05","pri":"גבוה", "cat":"ספירה",     "worker":"דוד לוי"},
    {"id":13, "name":"ספירת מלאי — מדף 21-30",   "desc":"ספירה ידנית + עדכון מערכת + תיעוד פערים",              "rec":"שבועי",    "date":"2026-01-06","pri":"גבוה", "cat":"ספירה",     "worker":"אחמד חסן"},
    {"id":14, "name":"תחזוקת מלגזה 1",            "desc":"בדיקת שמן, גלגלים, מטען, בלמים, מזלג",                "rec":"שבועי",    "date":"2026-01-04","pri":"גבוה", "cat":"תחזוקה",    "worker":"ברק נחמיאס"},
    {"id":15, "name":"תחזוקת מלגזה 2",            "desc":"בדיקת שמן, גלגלים, מטען, בלמים, מזלג",                "rec":"שבועי",    "date":"2026-01-05","pri":"גבוה", "cat":"תחזוקה",    "worker":"ברק נחמיאס"},
    {"id":16, "name":"בדיקת גנרטור",              "desc":"הפעלת בדיקה 10 דקות, רישום נתונים, בדיקת דלק",        "rec":"שבועי",    "date":"2026-01-04","pri":"גבוה", "cat":"תחזוקה",    "worker":"יוסי כהן"},
    {"id":17, "name":"דוח קבלת סחורה שבועי",     "desc":"ריכוז נתוני ספקים, כמויות, חריגות, דוח PDF",           "rec":"שבועי",    "date":"2026-01-05","pri":"רגיל", "cat":"לוגיסטיקה", "worker":"מיכל אברהם"},
    {"id":18, "name":"בדיקת מצלמות אבטחה",       "desc":"בדיקה ויזואלית ל-32 מצלמות, בדיקת הקלטה",             "rec":"שבועי",    "date":"2026-01-04","pri":"גבוה", "cat":"בטיחות",    "worker":"דוד לוי"},
    {"id":19, "name":"הדרכת בטיחות שבועית",      "desc":"15 דקות הדרכה עם כל הצוות, חתימה על נוכחות",          "rec":"שבועי",    "date":"2026-01-06","pri":"גבוה", "cat":"בטיחות",    "worker":"יוסי כהן"},
    {"id":20, "name":"ניקוי מדפים — שורה A",     "desc":"אבק, ניקוי עמוק, בדיקת יציבות מדפים",                  "rec":"שבועי",    "date":"2026-01-06","pri":"רגיל", "cat":"ניקיון",    "worker":"רינה שמיר"},
    {"id":21, "name":"ניקוי מדפים — שורה B",     "desc":"אבק, ניקוי עמוק, בדיקת יציבות מדפים",                  "rec":"שבועי",    "date":"2026-01-07","pri":"רגיל", "cat":"ניקיון",    "worker":"רינה שמיר"},
    {"id":22, "name":"בדיקת תאריכי תפוגה",       "desc":"סריקת קטגוריית מזון + תרופות + חומרים כימיים",         "rec":"שבועי",    "date":"2026-01-05","pri":"דחוף", "cat":"בטיחות",    "worker":"אחמד חסן"},

    # דו-שבועיות
    {"id":23, "name":"ספירה מלאה — אזור C",       "desc":"ספירה מלאה כולל תיעוד צילום + דוח פערים",              "rec":"דו-שבועי", "date":"2026-01-06","pri":"גבוה", "cat":"ספירה",     "worker":"יוסי כהן"},
    {"id":24, "name":"כיול מאזניים",               "desc":"3 מאזניים — כיול ותיעוד, אישור מדידה",                 "rec":"דו-שבועי", "date":"2026-01-06","pri":"גבוה", "cat":"תחזוקה",    "worker":"ברק נחמיאס"},
    {"id":25, "name":"בדיקת ממטרות אש",           "desc":"בדיקת לחץ מים ב-6 נקודות, תיעוד",                     "rec":"דו-שבועי", "date":"2026-01-07","pri":"דחוף", "cat":"בטיחות",    "worker":"יוסי כהן"},
    {"id":26, "name":"עדכון טבלת מיקומים",        "desc":"עדכון מפת המחסן במערכת, סימון שינויים",                "rec":"דו-שבועי", "date":"2026-01-08","pri":"רגיל", "cat":"לוגיסטיקה", "worker":"מיכל אברהם"},
    {"id":27, "name":"פגישת צוות דו-שבועית",     "desc":"סיכום ביצועים, שיחת שיפור, עדכוני הנהלה",              "rec":"דו-שבועי", "date":"2026-01-07","pri":"רגיל", "cat":"כללי",      "worker":"יוסי כהן"},
    {"id":28, "name":"בדיקת מערכת כריכה",        "desc":"בדיקת כריכה אוטומטית + ניקוי ראש כריכה",              "rec":"דו-שבועי", "date":"2026-01-08","pri":"גבוה", "cat":"תחזוקה",    "worker":"ברק נחמיאס"},

    # חודשיות
    {"id":29, "name":"ספירה חודשית מלאה",         "desc":"כל המחסן — ספירה ותיעוד, דוח מלאי חודשי",             "rec":"חודשי",    "date":"2026-01-01","pri":"דחוף", "cat":"ספירה",     "worker":"יוסי כהן"},
    {"id":30, "name":"בדיקת חשמל ראשית",          "desc":"חשמלאי מוסמך — 4 לוחות, בדיקת נתיכים",               "rec":"חודשי",    "date":"2026-01-01","pri":"דחוף", "cat":"תחזוקה",    "worker":"ברק נחמיאס"},
    {"id":31, "name":"החלפת פילטרים",              "desc":"מיזוג, אוורור, ניקוי אוויר — 8 יחידות",               "rec":"חודשי",    "date":"2026-01-15","pri":"גבוה", "cat":"תחזוקה",    "worker":"ברק נחמיאס"},
    {"id":32, "name":"דוח ביצועים חודשי",         "desc":"ריכוז נתונים, גרפים, הצגה להנהלה",                    "rec":"חודשי",    "date":"2026-01-28","pri":"גבוה", "cat":"כללי",      "worker":"מיכל אברהם"},
    {"id":33, "name":"גיבוי נתוני מערכת",         "desc":"גיבוי לשרת ענן + בדיקת שחזור, תיעוד",                 "rec":"חודשי",    "date":"2026-01-01","pri":"דחוף", "cat":"כללי",      "worker":"מיכל אברהם"},
    {"id":34, "name":"תרגיל חירום ופינוי",        "desc":"תרגיל פינוי עם כל הצוות, עדכון נהלים",                "rec":"חודשי",    "date":"2026-01-10","pri":"גבוה", "cat":"בטיחות",    "worker":"יוסי כהן"},
    {"id":35, "name":"בדיקת ארגז עזרה ראשונה",   "desc":"תוקף תרופות, מילוי חסרים, בדיקת ציוד",               "rec":"חודשי",    "date":"2026-01-05","pri":"גבוה", "cat":"בטיחות",    "worker":"דוד לוי"},
    {"id":36, "name":"עדכון נהלי עבודה",          "desc":"סקירת SOP ועדכון לפי שינויים רגולטוריים",             "rec":"חודשי",    "date":"2026-01-20","pri":"רגיל", "cat":"כללי",      "worker":"מיכל אברהם"},
    {"id":37, "name":"ביקורת ספקים",              "desc":"הערכת 5 ספקים מובילים, דוח איכות",                    "rec":"חודשי",    "date":"2026-01-25","pri":"רגיל", "cat":"לוגיסטיקה", "worker":"אחמד חסן"},
    {"id":38, "name":"בדיקת רכב משלוחים",        "desc":"טסט + שמן + צמיגים + בלמים + רישיון",                 "rec":"חודשי",    "date":"2026-01-10","pri":"גבוה", "cat":"תחזוקה",    "worker":"ברק נחמיאס"},
    {"id":39, "name":"עדכון מפת סכנות",           "desc":"עדכון מפת נקודות סכנה, שלטים, מסלולי פינוי",          "rec":"חודשי",    "date":"2026-01-12","pri":"גבוה", "cat":"בטיחות",    "worker":"יוסי כהן"},
    {"id":40, "name":"ישיבת הנהלה + WMS",         "desc":"הצגת ביצועי מחסן להנהלה, תכנון חודש הבא",             "rec":"חודשי",    "date":"2026-01-26","pri":"גבוה", "cat":"כללי",      "worker":"מיכל אברהם"},
]

# ═══════════════════════════════════════════════════════════════════════════════
#  MEGA CSS — industrial dark + neon
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  --bg0:     #020810;
  --bg1:     #040d1c;
  --bg2:     #071526;
  --card:    #0a1c35;
  --card2:   #0d2240;
  --card3:   #102850;
  --b0:      rgba(0,212,255,.08);
  --b1:      rgba(0,212,255,.2);
  --b2:      rgba(0,212,255,.45);
  --b3:      rgba(0,212,255,.7);
  --cyan:    #00d4ff;
  --cyan2:   #00a8cc;
  --green:   #00ff88;
  --green2:  #00cc6a;
  --red:     #ff2d55;
  --red2:    #cc1f3f;
  --amber:   #ffb800;
  --amber2:  #cc9200;
  --purple:  #bf5af2;
  --pink:    #ff375f;
  --txt:     #e2eeff;
  --txt2:    #6b8aaa;
  --txt3:    #3d5a75;
  --mono:    'JetBrains Mono', monospace;
  --orb:     'Orbitron', monospace;
  --heb:     'Heebo', sans-serif;
  --r:       14px;
  --r2:      20px;
  --shadow:  0 8px 32px rgba(0,0,0,.6);
  --glow-c:  0 0 30px rgba(0,212,255,.25);
  --glow-g:  0 0 30px rgba(0,255,136,.2);
  --glow-r:  0 0 30px rgba(255,45,85,.25);
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: var(--heb) !important;
  direction: rtl !important;
  text-align: right !important;
}

/* ── App Background — animated grid ── */
.stApp {
  background-color: var(--bg0) !important;
  background-image:
    linear-gradient(rgba(0,212,255,.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,212,255,.03) 1px, transparent 1px),
    radial-gradient(ellipse 100% 60% at 50% 0%,
      rgba(0,212,255,.07) 0%, transparent 65%),
    radial-gradient(ellipse 60% 40% at 80% 100%,
      rgba(0,255,136,.04) 0%, transparent 60%);
  background-size: 48px 48px, 48px 48px, 100% 100%, 100% 100%;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--bg1) 0%, var(--bg0) 100%) !important;
  border-left: 1px solid var(--b1) !important;
  box-shadow: 4px 0 40px rgba(0,0,0,.5) !important;
}
[data-testid="stSidebar"] * { color: var(--txt) !important; }
[data-testid="stSidebar"] .stRadio label {
  background: transparent !important;
  border: 1px solid transparent;
  border-radius: 10px;
  padding: 10px 14px;
  margin: 3px 0;
  transition: all .2s;
  display: block;
  font-weight: 600;
  letter-spacing: .3px;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(0,212,255,.08) !important;
  border-color: var(--b2) !important;
  transform: translateX(-3px);
}

/* ── Metrics ── */
[data-testid="stMetric"] {
  background: var(--card) !important;
  padding: 22px 20px !important;
  border-radius: var(--r) !important;
  border: 1px solid var(--b1) !important;
  box-shadow: var(--shadow) !important;
  transition: all .25s !important;
  position: relative;
  overflow: hidden;
}
[data-testid="stMetric"]::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 100%; height: 2px;
  background: linear-gradient(90deg, var(--cyan), var(--green));
}
[data-testid="stMetric"]::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0;
  width: 40%; height: 1px;
  background: linear-gradient(90deg, transparent, var(--cyan));
}
[data-testid="stMetric"]:hover {
  transform: translateY(-4px) !important;
  border-color: var(--b2) !important;
  box-shadow: var(--glow-c), var(--shadow) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--txt2) !important;
  font-size: .78rem !important;
  font-weight: 600 !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  color: var(--cyan) !important;
  font-family: var(--orb) !important;
  font-weight: 800 !important;
  font-size: 2.1rem !important;
  text-shadow: 0 0 20px rgba(0,212,255,.4);
}
[data-testid="stMetricDelta"] { font-size: .78rem !important; font-weight: 600 !important; }

/* ── Buttons ── */
.stButton > button {
  background: rgba(0,212,255,.08) !important;
  border: 1px solid var(--b2) !important;
  color: var(--cyan) !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-family: var(--heb) !important;
  transition: all .2s !important;
  letter-spacing: .3px;
}
.stButton > button:hover {
  background: rgba(0,212,255,.18) !important;
  box-shadow: var(--glow-c) !important;
  transform: translateY(-1px);
}

/* ── Form ── */
[data-testid="stForm"] {
  background: var(--card) !important;
  border: 1px solid var(--b1) !important;
  border-radius: var(--r2) !important;
  padding: 28px !important;
}
[data-testid="stForm"] .stButton > button {
  background: linear-gradient(135deg, #0088cc, #005fa3) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 4px 20px rgba(0,136,204,.4) !important;
}
[data-testid="stForm"] .stButton > button:hover {
  background: linear-gradient(135deg, #00a8ff, #0077cc) !important;
  box-shadow: 0 6px 28px rgba(0,168,255,.5) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
  background: var(--bg2) !important;
  border: 1px solid var(--b1) !important;
  border-radius: 10px !important;
  color: var(--txt) !important;
  font-family: var(--heb) !important;
  transition: border-color .2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--b3) !important;
  box-shadow: 0 0 0 2px rgba(0,212,255,.12) !important;
}
label[data-testid="stWidgetLabel"] p { color: var(--txt) !important; font-weight: 600 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg0); }
::-webkit-scrollbar-thumb { background: var(--b2); border-radius: 3px; }

/* ── Popover ── */
div[data-testid="stPopover"] > button {
  width: 100% !important;
  min-height: 58px !important;
  margin-bottom: 6px !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  border: 1px solid var(--b1) !important;
  background: var(--card) !important;
  color: var(--txt) !important;
  text-align: right !important;
  transition: all .2s !important;
}
div[data-testid="stPopover"] > button:hover {
  border-color: var(--b2) !important;
  background: var(--card2) !important;
}

/* ── Expander ── */
details > summary { color: var(--cyan) !important; font-weight: 700 !important; }
[data-testid="stExpander"] {
  background: var(--card) !important;
  border: 1px solid var(--b1) !important;
  border-radius: var(--r) !important;
}

/* ── Tab ── */
[data-testid="stTabs"] [role="tab"] {
  color: var(--txt2) !important;
  font-weight: 700 !important;
  border-radius: 8px 8px 0 0 !important;
  transition: all .2s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom: 2px solid var(--cyan) !important;
}

/* ── CUSTOM COMPONENTS ── */

/* Banner */
.mega-banner {
  background: linear-gradient(135deg, var(--card) 0%, var(--card2) 50%, var(--card) 100%);
  border: 1px solid var(--b2);
  border-radius: var(--r2);
  padding: 32px 40px;
  margin-bottom: 28px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: var(--glow-c), var(--shadow);
}
.mega-banner::before {
  content: '';
  position: absolute;
  top: -80px; left: 50%;
  transform: translateX(-50%);
  width: 400px; height: 160px;
  background: radial-gradient(ellipse, rgba(0,212,255,.15) 0%, transparent 70%);
  pointer-events: none;
}
.mega-banner::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--cyan), transparent);
}
.mega-banner h1 {
  font-family: var(--orb) !important;
  font-size: 2rem !important;
  font-weight: 900 !important;
  color: var(--cyan) !important;
  letter-spacing: 4px !important;
  margin: 0 0 8px !important;
  text-shadow: 0 0 40px rgba(0,212,255,.5) !important;
}
.mega-banner .sub {
  color: var(--txt2);
  font-size: .85rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-weight: 500;
}
.mega-banner .live-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 12px var(--green);
  margin-left: 8px;
  animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:.5; transform:scale(.7); }
}

/* KPI Card */
.kpi {
  background: var(--card);
  border: 1px solid var(--b1);
  border-radius: var(--r2);
  padding: 24px 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all .3s;
  cursor: default;
}
.kpi:hover { transform: translateY(-5px); border-color: var(--b2); }
.kpi::before {
  content: '';
  position: absolute;
  top: 0; right: 0; width: 100%; height: 3px;
}
.kpi-blue::before  { background: linear-gradient(90deg, var(--cyan), #005fa3); }
.kpi-green::before { background: linear-gradient(90deg, var(--green), #005f35); }
.kpi-red::before   { background: linear-gradient(90deg, var(--red), #6b001e); }
.kpi-amber::before { background: linear-gradient(90deg, var(--amber), #6b4a00); }
.kpi-purple::before{ background: linear-gradient(90deg, var(--purple), #3d0070); }
.kpi:hover.kpi-blue  { box-shadow: var(--glow-c); }
.kpi:hover.kpi-green { box-shadow: var(--glow-g); }
.kpi:hover.kpi-red   { box-shadow: var(--glow-r); }
.kpi-icon {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
  filter: drop-shadow(0 0 12px currentColor);
}
.kpi-val {
  font-family: var(--orb);
  font-size: 2.8rem;
  font-weight: 900;
  line-height: 1;
  margin-bottom: 8px;
}
.kpi-lbl {
  font-size: .72rem;
  color: var(--txt2);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  font-weight: 600;
}
.kpi-sub {
  font-size: .75rem;
  margin-top: 6px;
  font-weight: 700;
  font-family: var(--mono);
}

/* Progress bar */
.prog {
  background: rgba(255,255,255,.06);
  border-radius: 20px;
  height: 8px;
  overflow: hidden;
  margin: 6px 0;
  position: relative;
}
.prog::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,.06) 50%, transparent 100%);
  animation: shimmer 2s ease infinite;
}
@keyframes shimmer { 0%{transform:translateX(100%)} 100%{transform:translateX(-100%)} }
.pfill {
  height: 100%;
  border-radius: 20px;
  transition: width .8s cubic-bezier(.4,0,.2,1);
  position: relative;
}

/* Task Card */
.tc {
  background: var(--card);
  border: 1px solid var(--b0);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 7px;
  border-right: 4px solid var(--cyan);
  transition: all .2s;
  position: relative;
  overflow: hidden;
}
.tc::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 4px; height: 100%;
}
.tc:hover {
  background: var(--card2);
  border-color: var(--b2);
  transform: translateX(-3px);
}
.tc.done  { border-right-color: var(--green) !important; opacity: .65; }
.tc.urgent{ border-right-color: var(--red)   !important; }
.tc.high  { border-right-color: var(--amber) !important; }

/* Badge */
.b {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 20px;
  font-size: .67rem;
  font-weight: 800;
  margin: 1px;
  letter-spacing: .3px;
}
.b-blue   { background: rgba(0,212,255,.14);   color: #5dd8ff; border: 1px solid rgba(0,212,255,.25); }
.b-green  { background: rgba(0,255,136,.12);   color: #00ff88; border: 1px solid rgba(0,255,136,.2); }
.b-red    { background: rgba(255,45,85,.14);   color: #ff5577; border: 1px solid rgba(255,45,85,.25); }
.b-amber  { background: rgba(255,184,0,.14);   color: #ffd040; border: 1px solid rgba(255,184,0,.25); }
.b-purple { background: rgba(191,90,242,.14);  color: #d070ff; border: 1px solid rgba(191,90,242,.25); }
.b-gray   { background: rgba(255,255,255,.07); color: var(--txt2); border: 1px solid var(--b1); }

/* Week chip */
.wchip {
  background: linear-gradient(135deg, var(--card), var(--card2));
  border: 1px solid var(--b2);
  border-radius: 12px;
  padding: 12px 8px;
  margin-bottom: 10px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: var(--glow-c);
}
.wchip .day-name {
  font-family: var(--orb);
  font-size: .72rem;
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 1px;
}
.wchip .day-date {
  font-size: .68rem;
  color: var(--txt2);
  font-family: var(--mono);
  margin-top: 2px;
}
.wchip .day-count {
  font-size: .62rem;
  color: var(--green);
  font-weight: 700;
  margin-top: 4px;
}

/* Alert boxes */
.al {
  border-radius: 12px;
  padding: 14px 18px;
  margin-bottom: 14px;
  font-size: .9rem;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.al-red    { background: rgba(255,45,85,.1);   border: 1px solid rgba(255,45,85,.4); }
.al-green  { background: rgba(0,255,136,.07);  border: 1px solid rgba(0,255,136,.25); }
.al-amber  { background: rgba(255,184,0,.08);  border: 1px solid rgba(255,184,0,.3); }
.al-cyan   { background: rgba(0,212,255,.07);  border: 1px solid rgba(0,212,255,.25); }

/* Stat row */
.stat-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--b0);
}
.stat-row:last-child { border-bottom: none; }
.stat-label { color: var(--txt2); font-size: .82rem; flex: 1; }
.stat-val   { color: var(--txt);  font-size: .85rem; font-weight: 700; font-family: var(--mono); }

/* Section header */
.sec-h {
  font-family: var(--orb);
  font-size: .85rem;
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin: 24px 0 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--b1);
  position: relative;
}
.sec-h::after {
  content: '';
  position: absolute;
  bottom: -1px; right: 0;
  width: 60px; height: 2px;
  background: var(--cyan);
  box-shadow: var(--glow-c);
}

/* Mini metric */
.mm {
  background: var(--card);
  border: 1px solid var(--b1);
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all .2s;
}
.mm:hover { border-color: var(--b2); transform: translateY(-2px); }
.mm-icon { font-size: 1.5rem; }
.mm-val  { font-family: var(--orb); font-size: 1.4rem; font-weight: 700; color: var(--cyan); }
.mm-lbl  { font-size: .72rem; color: var(--txt2); letter-spacing: .5px; }

/* Timeline dot */
.tl-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

/* Login buttons */
div[data-testid="stHorizontalBlock"] .stButton > button {
  min-height: 220px !important;
  height: 220px !important;
  width: 100% !important;
  border-radius: var(--r2) !important;
  font-size: 1.5rem !important;
  font-weight: 900 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: pre-wrap !important;
  text-align: center !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
  border-top: 4px solid var(--cyan) !important;
  box-shadow: 0 -4px 20px rgba(0,212,255,.2) inset !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
  border-top: 4px solid var(--green) !important;
  box-shadow: 0 -4px 20px rgba(0,255,136,.15) inset !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
  border-top: 4px solid var(--amber) !important;
  box-shadow: 0 -4px 20px rgba(255,184,0,.15) inset !important;
}

/* Table / dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--b1) !important;
  border-radius: var(--r) !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
  background: linear-gradient(135deg, rgba(0,255,136,.15), rgba(0,255,136,.05)) !important;
  border: 1px solid rgba(0,255,136,.4) !important;
  color: var(--green) !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: rgba(0,255,136,.25) !important;
  box-shadow: var(--glow-g) !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def init_state():
    if "tasks" not in st.session_state:
        st.session_state.tasks = pd.DataFrame([{
            "ID": t["id"], "Task_Name": t["name"], "Description": t["desc"],
            "Recurring": t["rec"], "Date": t["date"],
            "Done_Dates": "", "Priority": t["pri"],
            "Category": t["cat"], "Assigned_To": t["worker"],
        } for t in SEED_TASKS])
        st.session_state.next_id = max(t["id"] for t in SEED_TASKS) + 1
    if "user_role"   not in st.session_state: st.session_state.user_role   = None
    if "login_time"  not in st.session_state: st.session_state.login_time  = None
    if "active_page" not in st.session_state: st.session_state.active_page = None

init_state()


# ═══════════════════════════════════════════════════════════════════════════════
#  TASK LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def is_scheduled(base, rec, target):
    if target < base: return False
    diff = (target - base).days
    if rec == "לא":        return diff == 0
    if rec == "יומי":      return diff < 365
    if rec == "שבועי":     return diff % 7 == 0
    if rec == "דו-שבועי":  return diff % 14 == 0
    if rec == "חודשי":     return target.day == base.day
    return False

def tasks_for_date(df, dt, skip_weekend=True):
    d = dt.date() if isinstance(dt, datetime) else dt
    if skip_weekend and d.weekday() in [4, 5]: return []
    dstr = d.strftime("%Y-%m-%d")
    out = []
    for idx, row in df.iterrows():
        try:
            base = pd.to_datetime(row["Date"]).date()
            if is_scheduled(base, row["Recurring"], d):
                done = [x for x in str(row["Done_Dates"]).split(",") if x]
                out.append({
                    "idx": idx, "id": row["ID"], "name": row["Task_Name"],
                    "desc": str(row.get("Description", "")),
                    "priority": str(row.get("Priority", "רגיל")),
                    "category": str(row.get("Category", "כללי")),
                    "assigned": str(row.get("Assigned_To", "")),
                    "is_done": dstr in done, "date": dstr,
                    "rec": str(row.get("Recurring", "")),
                })
        except: continue
    return out

def mark_done(idx, dstr):
    existing = [x for x in str(st.session_state.tasks.at[idx, "Done_Dates"]).split(",") if x]
    if dstr not in existing: existing.append(dstr)
    st.session_state.tasks.at[idx, "Done_Dates"] = ",".join(existing)

def get_overdue(days=7):
    today = datetime.now().date()
    out = []
    for i in range(1, days + 1):
        d = today - timedelta(days=i)
        for t in tasks_for_date(st.session_state.tasks, d):
            if not t["is_done"]: out.append(t)
    return out

def week_stats(days=14):
    today = datetime.now().date()
    rows = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        ts = tasks_for_date(st.session_state.tasks, d)
        tot = len(ts); don = sum(1 for t in ts if t["is_done"])
        rows.append({
            "date": d, "תאריך": d.strftime("%d/%m"),
            "בוצע": don, "מתוכנן": tot,
            "אחוז": round(don / tot * 100) if tot else 0
        })
    return pd.DataFrame(rows)

def monthly_stats(year, month):
    _, nd = cal_lib.monthrange(year, month)
    rows = []
    for day in range(1, nd + 1):
        d = datetime(year, month, day).date()
        ts = tasks_for_date(st.session_state.tasks, d)
        if ts:
            don = sum(1 for t in ts if t["is_done"])
            rows.append({"יום": day, "בוצע": don, "מתוכנן": len(ts),
                         "אחוז": round(don / len(ts) * 100)})
    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def pbar(pct, color=None, height=8):
    c = color or ("#00ff88" if pct >= 80 else "#ffb800" if pct >= 50 else "#ff2d55")
    glow = f"0 0 10px {c}66"
    return (f'<div class="prog" style="height:{height}px">'
            f'<div class="pfill" style="width:{min(pct,100)}%;background:{c};box-shadow:{glow}"></div>'
            f'</div>')

def badge(text, kind="blue"):
    return f'<span class="b b-{kind}">{text}</span>'

def pri_badge(p):
    return badge(p, {"דחוף": "red", "גבוה": "amber", "רגיל": "blue", "נמוך": "gray"}.get(p, "blue"))

def cat_badge(c):
    return badge(c, {"בטיחות": "red", "ספירה": "blue", "תחזוקה": "amber",
                     "לוגיסטיקה": "purple", "ניקיון": "green", "כללי": "gray"}.get(c, "gray"))

def task_card_html(t):
    cls = "tc" + (" done" if t["is_done"] else
                  " urgent" if t["priority"] == "דחוף" else
                  " high" if t["priority"] == "גבוה" else "")
    icon = "✅" if t["is_done"] else ("🚨" if t["priority"] == "דחוף" else "⏳")
    asgn = f' {badge(t["assigned"],"green")}' if t.get("assigned") else ""
    rec  = f' {badge(t["rec"],"gray")}' if t.get("rec") else ""
    desc = (f'<div style="color:var(--txt2);font-size:.78rem;margin-top:5px;'
            f'font-family:var(--mono)">{t["desc"]}</div>') if t.get("desc") else ""
    return (f'<div class="{cls}">'
            f'{icon} <b style="font-size:.95rem">{t["name"]}</b>'
            f' {pri_badge(t["priority"])} {cat_badge(t["category"])}{asgn}{rec}'
            f'{desc}</div>')

def kpi_card(val, label, sub="", color="var(--cyan)", icon="📊", kind="blue"):
    glow = {"blue": "var(--glow-c)", "green": "var(--glow-g)", "red": "var(--glow-r)"}.get(kind, "")
    return (f'<div class="kpi kpi-{kind}" style="box-shadow:{glow if glow else ""}">'
            f'<span class="kpi-icon" style="color:{color}">{icon}</span>'
            f'<div class="kpi-val" style="color:{color};text-shadow:0 0 20px {color}66">{val}</div>'
            f'<div class="kpi-lbl">{label}</div>'
            f'{"<div class=kpi-sub style=color:"+color+";opacity:.7>"+sub+"</div>" if sub else ""}'
            f'</div>')

def sec_header(title):
    st.markdown(f'<div class="sec-h">{title}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════════════════════════════
def check_timeout():
    lt = st.session_state.get("login_time")
    if lt and (datetime.now() - lt).total_seconds() > SESSION_MINS * 60:
        st.session_state.user_role = None
        st.session_state.login_time = None
        st.rerun()

def login_screen():
    st.markdown("""
    <div class="mega-banner">
      <h1>⬡ COHEN BROTHERS WMS ⬡</h1>
      <div class="sub">
        <span class="live-dot"></span>
        מערכת ניהול מחסן מתקדמת • v4.0 ULTRA
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.popover("🔑\nמנהל WMS", use_container_width=True):
            st.markdown("#### 🔐 כניסת מנהל מערכת")
            st.markdown('<div style="color:var(--txt2);font-size:.82rem;margin-bottom:12px">גישה מלאה לכל מודולי המערכת</div>', unsafe_allow_html=True)
            pwd = st.text_input("סיסמה", type="password", key="lpwd")
            if st.button("🚀 כניסה למערכת", use_container_width=True):
                if hashlib.sha256(pwd.encode()).hexdigest() == ADMIN_HASH:
                    st.session_state.user_role = "מנהל WMS"
                    st.session_state.login_time = datetime.now()
                    st.rerun()
                else:
                    st.error("❌ סיסמה שגויה")
    with c2:
        if st.button("📦\nצוות מחסן", use_container_width=True):
            st.session_state.user_role = "צוות מחסן"
            st.session_state.login_time = datetime.now()
            st.rerun()
    with c3:
        if st.button("📊\nהנהלה", use_container_width=True):
            st.session_state.user_role = "הנהלה"
            st.session_state.login_time = datetime.now()
            st.rerun()

    # Stats below login
    st.markdown("---")
    df = st.session_state.tasks
    today_ts = tasks_for_date(df, datetime.now())
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi_card(len(df), "משימות במערכת", icon="📋", kind="blue"), unsafe_allow_html=True)
    c2.markdown(kpi_card(len(today_ts), "להיום", icon="📅", kind="green"), unsafe_allow_html=True)
    c3.markdown(kpi_card(len(get_overdue()), "פיגורים", icon="⚠️", kind="red", color="var(--red)"), unsafe_allow_html=True)
    c4.markdown(kpi_card(len(WORKERS), "עובדים פעילים", icon="👥", kind="blue"), unsafe_allow_html=True)
    c5.markdown(kpi_card(datetime.now().strftime("%H:%M"), "שעה נוכחית", icon="🕐", kind="blue"), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    df = st.session_state.tasks
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    # ── Overdue Alert ──
    overdue = get_overdue()
    if overdue:
        st.markdown(
            f'<div class="al al-red">🚨 <div><b style="color:var(--red);font-size:1rem">'
            f'{len(overdue)} משימות שלא בוצעו בשבוע האחרון</b>'
            f'<div style="color:var(--txt2);font-size:.8rem;margin-top:2px">'
            f'לחץ להצגה וסגירה</div></div></div>',
            unsafe_allow_html=True)
        with st.expander("📋 פירוט פיגורים וסגירתם"):
            for t in overdue:
                c1, c2 = st.columns([5, 1])
                c1.markdown(task_card_html(t), unsafe_allow_html=True)
                if c2.button("✓", key=f"ov_{t['id']}_{t['date']}"):
                    mark_done(t["idx"], t["date"]); st.rerun()

    # ── Date + Live clock ──
    dc, tc, _ = st.columns([1, 1, 2])
    sel = dc.date_input("📅 תאריך", today)
    dstr = sel.strftime("%Y-%m-%d")
    tc.markdown(f"""
    <div style="padding:8px 0;color:var(--txt2);font-family:var(--mono);font-size:.85rem">
      🕐 {today.strftime('%H:%M:%S')} &nbsp;|&nbsp; 
      📆 {today.strftime('%A')} &nbsp;|&nbsp;
      {'🟢 <span style="color:var(--green)">עסק פתוח</span>' if today.weekday() not in [4,5] else '🔴 <span style="color:var(--red)">סגור (סוף שבוע)</span>'}
    </div>""", unsafe_allow_html=True)

    ts = tasks_for_date(df, sel)
    tot = len(ts); don = sum(1 for t in ts if t["is_done"])
    pct = round(don / tot * 100) if tot else 0
    pct_color = "#00ff88" if pct >= 80 else "#ffb800" if pct >= 50 else "#ff2d55"
    lbl = "היום" if sel == today.date() else sel.strftime("%d/%m")

    # ── Big KPI row ──
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(kpi_card(tot,   f"משימות {lbl}", icon="📋", kind="blue"), unsafe_allow_html=True)
    k2.markdown(kpi_card(don,   "בוצעו",  icon="✅", kind="green", color="var(--green)"), unsafe_allow_html=True)
    k3.markdown(kpi_card(tot-don,"נותרו", icon="⏳", kind="red" if tot-don > 3 else "blue",
                         color="var(--red)" if tot-don > 3 else "var(--cyan)"), unsafe_allow_html=True)
    k4.markdown(kpi_card(f"{pct}%","ביצוע", sub=f"{'🔥 מצוין' if pct>=80 else '⚠️ בינוני' if pct>=50 else '❌ נמוך'}",
                         icon="📈", kind="green" if pct>=80 else "red", color=pct_color), unsafe_allow_html=True)
    k5.markdown(kpi_card(len(overdue),"פיגורים", icon="🚨", kind="red", color="var(--red)"), unsafe_allow_html=True)

    st.markdown(f'<div style="margin:8px 0 20px">{pbar(pct, pct_color, 10)}</div>', unsafe_allow_html=True)

    # ── Main content: tasks list + charts side by side ──
    col_l, col_r = st.columns([5, 4])

    with col_l:
        sec_header(f"📋 משימות ל-{lbl}")
        if ts:
            # group by category
            by_cat = {}
            for t in sorted(ts, key=lambda x: (x["is_done"], x["priority"] != "דחוף")):
                by_cat.setdefault(t["category"], []).append(t)
            for cat, cat_tasks in by_cat.items():
                don_c = sum(1 for t in cat_tasks if t["is_done"])
                p = round(don_c / len(cat_tasks) * 100)
                st.markdown(f'<div style="margin:14px 0 6px;display:flex;align-items:center;gap:8px">'
                            f'{cat_badge(cat)} '
                            f'<span style="color:var(--txt2);font-size:.75rem">{don_c}/{len(cat_tasks)}</span>'
                            f'{pbar(p)}</div>', unsafe_allow_html=True)
                for t in cat_tasks:
                    ca, cb = st.columns([7, 1])
                    ca.markdown(task_card_html(t), unsafe_allow_html=True)
                    if not t["is_done"] and cb.button("✓", key=f"d_{t['id']}_{dstr}_{cat}"):
                        mark_done(t["idx"], dstr); st.rerun()
        else:
            st.markdown('<div class="al al-cyan">ℹ️ <b>אין משימות לתאריך זה</b></div>', unsafe_allow_html=True)

    with col_r:
        sec_header("📊 מבט מהיר")

        # Category breakdown pie
        if HAS_PLOTLY and ts:
            cat_done = {}; cat_tot = {}
            for t in ts:
                c = t["category"]
                cat_tot[c] = cat_tot.get(c, 0) + 1
                if t["is_done"]: cat_done[c] = cat_done.get(c, 0) + 1
            cat_names = list(cat_tot.keys())
            cat_vals  = [cat_tot[c] for c in cat_names]
            CMAP = {"בטיחות":"#ff2d55","ספירה":"#00d4ff","תחזוקה":"#ffb800",
                    "לוגיסטיקה":"#bf5af2","ניקיון":"#00ff88","כללי":"#8899aa"}
            colors = [CMAP.get(c, "#8899aa") for c in cat_names]
            fig_pie = go.Figure(go.Pie(
                labels=cat_names, values=cat_vals,
                hole=.6, marker_colors=colors,
                textinfo="label+percent",
                textfont=dict(size=11, color="#e2eeff"),
                hovertemplate="<b>%{label}</b><br>%{value} משימות<extra></extra>",
            ))
            fig_pie.add_annotation(
                text=f"<b>{tot}</b><br><span style='font-size:10'>סה\"כ</span>",
                x=.5, y=.5, font_size=18, font_color="#00d4ff", showarrow=False)
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", height=260,
                margin=dict(t=10, b=0, l=0, r=0),
                showlegend=True,
                legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#e2eeff", font_size=11),
                font=dict(family="Heebo"))
            st.plotly_chart(fig_pie, use_container_width=True)

        # Priority breakdown
        st.markdown("**עדיפות:**")
        for pri, clr in [("דחוף","#ff2d55"),("גבוה","#ffb800"),("רגיל","#00d4ff"),("נמוך","#8899aa")]:
            cnt = sum(1 for t in ts if t["priority"] == pri)
            don_c = sum(1 for t in ts if t["priority"] == pri and t["is_done"])
            if cnt:
                p = round(don_c / cnt * 100)
                st.markdown(
                    f'<div class="stat-row"><div class="tl-dot" style="background:{clr};box-shadow:0 0 8px {clr}66"></div>'
                    f'<span class="stat-label">{pri}</span>'
                    f'<span class="stat-val" style="color:{clr}">{don_c}/{cnt}</span></div>'
                    f'{pbar(p, clr, 5)}', unsafe_allow_html=True)

        # Worker breakdown
        st.markdown("**לפי עובד:**")
        worker_ts = {}
        for t in ts:
            w = t["assigned"] or "לא שויך"
            worker_ts.setdefault(w, {"done": 0, "total": 0})
            worker_ts[w]["total"] += 1
            if t["is_done"]: worker_ts[w]["done"] += 1
        for w, v in sorted(worker_ts.items(), key=lambda x: -x[1]["total"]):
            p = round(v["done"] / v["total"] * 100) if v["total"] else 0
            c = "#00ff88" if p >= 80 else "#ffb800" if p >= 50 else "#ff2d55"
            st.markdown(
                f'<div class="stat-row">'
                f'<span class="stat-label">👤 {w}</span>'
                f'<span class="stat-val" style="color:{c}">{v["done"]}/{v["total"]}</span>'
                f'</div>{pbar(p, c, 5)}', unsafe_allow_html=True)

    # ── Weekly chart ──
    st.markdown("---")
    sec_header("📈 מגמת ביצועים — 14 ימים אחרונים")
    wdf = week_stats(14)
    if HAS_PLOTLY:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=wdf["תאריך"], y=wdf["מתוכנן"],
            name="מתוכנן", marker_color="rgba(0,212,255,.15)",
            marker_line_color="rgba(0,212,255,.3)", marker_line_width=1))
        fig.add_trace(go.Bar(
            x=wdf["תאריך"], y=wdf["בוצע"],
            name="בוצע", marker_color="rgba(0,255,136,.65)",
            marker_line_color="rgba(0,255,136,.8)", marker_line_width=1))
        fig.add_trace(go.Scatter(
            x=wdf["תאריך"], y=wdf["אחוז"],
            name="אחוז%", yaxis="y2", mode="lines+markers",
            line=dict(color="#00d4ff", width=2.5, dash="solid"),
            marker=dict(size=8, color="#00d4ff",
                        line=dict(color="#ffffff", width=1.5)),
            fill="tozeroy", fillcolor="rgba(0,212,255,.06)"))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Heebo", color="#e2eeff"), height=340,
            barmode="overlay", margin=dict(t=10, b=40, l=0, r=0),
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                        y=1.12, font_size=12),
            yaxis=dict(gridcolor="rgba(255,255,255,.04)", title="",
                       tickfont=dict(size=11)),
            yaxis2=dict(overlaying="y", side="left", range=[0, 115],
                        gridcolor="rgba(0,212,255,.05)", showgrid=False,
                        title="", tickfont=dict(size=11)),
            xaxis=dict(gridcolor="rgba(255,255,255,.03)", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Monthly analysis ──
    st.markdown("---")
    sec_header("📅 ניתוח חודשי מעמיק")

    MONTHS_HE = ["ינואר","פברואר","מרץ","אפריל","מאי","יוני",
                 "יולי","אוגוסט","ספטמבר","אוקטובר","נובמבר","דצמבר"]
    mc, yc, _, exp_col = st.columns([1, 1, 1, 1])
    sm = mc.selectbox("חודש", range(1, 13), index=today.month - 1,
                      format_func=lambda x: MONTHS_HE[x - 1])
    sy = yc.selectbox("שנה", [2025, 2026], index=1)

    mdf = monthly_stats(sy, sm)
    if not mdf.empty:
        avg = round(mdf["אחוז"].mean())
        best = int(mdf.loc[mdf["אחוז"].idxmax(), "יום"])
        worst = int(mdf.loc[mdf["אחוז"].idxmin(), "יום"])

        ma, mb, mc2, md = st.columns(4)
        ma.metric("ממוצע חודשי",    f"{avg}%",  delta="יעד: 85%")
        mb.metric("יום שיא",        f"{best} בחודש")
        mc2.metric("יום חלש",       f"{worst} בחודש")
        md.metric("סה\"כ בוצע",     int(mdf["בוצע"].sum()))

        if HAS_PLOTLY:
            c_bar, c_heat = st.columns([3, 2])
            with c_bar:
                colors_m = ["#00ff88" if v >= 80 else "#ffb800" if v >= 50 else "#ff2d55"
                            for v in mdf["אחוז"]]
                fig_m = go.Figure()
                fig_m.add_trace(go.Bar(
                    x=mdf["יום"], y=mdf["אחוז"],
                    marker_color=colors_m,
                    text=[f"{v}%" for v in mdf["אחוז"]],
                    textposition="outside", textfont=dict(size=9, color="#e2eeff")))
                fig_m.add_hline(y=85, line_dash="dot", line_color="rgba(0,255,136,.4)",
                                annotation_text="יעד 85%",
                                annotation_font_color="#00ff88",
                                annotation_font_size=11)
                fig_m.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Heebo", color="#e2eeff"), height=300,
                    margin=dict(t=30, b=30, l=0, r=0), showlegend=False,
                    yaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,.04)"),
                    xaxis=dict(gridcolor="rgba(255,255,255,.03)"))
                st.plotly_chart(fig_m, use_container_width=True)

            with c_heat:
                # Category breakdown for month
                cat_m = {}
                _, nd = cal_lib.monthrange(sy, sm)
                for day in range(1, nd + 1):
                    for t in tasks_for_date(st.session_state.tasks,
                                            datetime(sy, sm, day).date()):
                        c = t["category"]
                        cat_m.setdefault(c, {"done": 0, "total": 0})
                        cat_m[c]["total"] += 1
                        if t["is_done"]: cat_m[c]["done"] += 1
                if cat_m:
                    cdf = pd.DataFrame([
                        {"קטגוריה": k, "אחוז": round(v["done"]/max(v["total"],1)*100),
                         "בוצע": v["done"], "מתוכנן": v["total"]}
                        for k, v in cat_m.items()]).sort_values("אחוז", ascending=True)
                    CMAP2 = {"בטיחות":"#ff2d55","ספירה":"#00d4ff","תחזוקה":"#ffb800",
                             "לוגיסטיקה":"#bf5af2","ניקיון":"#00ff88","כללי":"#8899aa"}
                    fig_c = go.Figure(go.Bar(
                        x=cdf["אחוז"], y=cdf["קטגוריה"],
                        orientation="h",
                        marker_color=[CMAP2.get(c,"#8899aa") for c in cdf["קטגוריה"]],
                        text=[f"{v}%" for v in cdf["אחוז"]],
                        textposition="outside",
                        textfont=dict(color="#e2eeff", size=11)))
                    fig_c.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Heebo", color="#e2eeff"), height=300,
                        margin=dict(t=10, b=10, l=80, r=60),
                        xaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,.04)"),
                        yaxis=dict(gridcolor="rgba(255,255,255,.03)"),
                        showlegend=False)
                    st.plotly_chart(fig_c, use_container_width=True)

        # Excel export
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            mdf.to_excel(w, index=False, sheet_name="ביצועים יומי")
            wdf.to_excel(w, index=False, sheet_name="ביצועים שבועי")
        st.download_button(
            "📥 ייצוא דוח Excel מלא", buf.getvalue(),
            f"דוח_ביצועים_{sm:02d}_{sy}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.markdown('<div class="al al-amber">⚠️ אין נתוני משימות לחודש הנבחר</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: WORK ORDER — weekly board
# ═══════════════════════════════════════════════════════════════════════════════
def page_work():
    df = st.session_state.tasks
    today = datetime.now()
    start = today - timedelta(days=(today.weekday() + 1) % 7)
    day_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5)

    for i, name in enumerate(day_names):
        curr = start + timedelta(days=i)
        ts = tasks_for_date(df, curr)
        don = sum(1 for t in ts if t["is_done"])
        pct = round(don / len(ts) * 100) if ts else 0
        is_today = curr.date() == today.date()
        pct_color = "#00ff88" if pct >= 80 else "#ffb800" if pct >= 50 else "#ff2d55"

        with cols[i]:
            border_color = "var(--cyan)" if is_today else "var(--b2)"
            bg = "rgba(0,212,255,.05)" if is_today else "transparent"
            st.markdown(f"""
            <div class="wchip" style="border-color:{border_color};background:linear-gradient(135deg,var(--card),{bg})">
              {'<span style="color:var(--amber);font-size:.6rem;font-family:var(--mono)">▸ היום ◂</span><br>' if is_today else ""}
              <div class="day-name">{name}</div>
              <div class="day-date">{curr.strftime('%d/%m/%y')}</div>
              <div class="day-count">{don}/{len(ts)} ✓</div>
            </div>
            {pbar(pct, pct_color, 5)}
            """, unsafe_allow_html=True)

            # group by priority within day
            urgent = [t for t in ts if t["priority"] == "דחוף"]
            rest   = [t for t in ts if t["priority"] != "דחוף"]

            for t in urgent + rest:
                ico = "✅" if t["is_done"] else ("🚨" if t["priority"] == "דחוף" else "⏳")
                lbl = f"{ico} {t['name']}"
                with st.popover(lbl, use_container_width=True):
                    st.markdown(f"**📋 {t['name']}**")
                    st.markdown(f"**עדיפות:** {t['priority']}")
                    st.markdown(f"**קטגוריה:** {t['category']}")
                    if t["assigned"]: st.markdown(f"**👤 שויך ל:** {t['assigned']}")
                    if t["desc"]:     st.markdown(f"**📝 פירוט:** {t['desc']}")
                    if not t["is_done"]:
                        if st.button("✅ סמן כבוצע", key=f"w_{t['id']}_{i}_{curr.date()}"):
                            mark_done(t["idx"], curr.strftime("%Y-%m-%d"))
                            st.rerun()

    # ── Worker view below ──
    st.markdown("---")
    sec_header("👥 מבט לפי עובד — השבוע הנוכחי")
    wcols = st.columns(len(WORKERS))
    for wi, worker in enumerate(WORKERS):
        with wcols[wi]:
            w_don = 0; w_tot = 0
            for i in range(5):
                curr = start + timedelta(days=i)
                for t in tasks_for_date(df, curr):
                    if t["assigned"] == worker:
                        w_tot += 1
                        if t["is_done"]: w_don += 1
            w_pct = round(w_don / w_tot * 100) if w_tot else 0
            w_color = "#00ff88" if w_pct >= 80 else "#ffb800" if w_pct >= 50 else "#ff2d55"
            st.markdown(
                f'<div class="mm">'
                f'<div class="mm-icon">👤</div>'
                f'<div>'
                f'<div class="mm-val" style="color:{w_color}">{w_pct}%</div>'
                f'<div class="mm-lbl">{worker}</div>'
                f'<div style="font-size:.68rem;color:var(--txt2);font-family:var(--mono)">{w_don}/{w_tot}</div>'
                f'</div></div>',
                unsafe_allow_html=True)
            st.markdown(pbar(w_pct, w_color, 5), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════
def page_calendar():
    df = st.session_state.tasks
    today = datetime.now().date()
    events = []

    for _, row in df.iterrows():
        base = pd.to_datetime(row["Date"]).date()
        for i in range(180):
            d = base + timedelta(days=i)
            if is_scheduled(base, row["Recurring"], d):
                done = d.strftime("%Y-%m-%d") in str(row["Done_Dates"])
                CMAP = {"בטיחות":"#ff2d55","ספירה":"#00d4ff","תחזוקה":"#ffb800",
                        "לוגיסטיקה":"#bf5af2","ניקיון":"#00ff88","כללי":"#8899aa"}
                base_color = CMAP.get(str(row.get("Category","")), "#388bfd")
                color = "#00ff88" if done else ("#ff2d55" if d < today else base_color)
                events.append({
                    "title": f"{'✅ ' if done else ''}{row['Task_Name']}",
                    "start": d.strftime("%Y-%m-%d"),
                    "color": color,
                    "allDay": True,
                })

    # Legend
    CATS_COLORS = [("בטיחות","#ff2d55"),("ספירה","#00d4ff"),("תחזוקה","#ffb800"),
                   ("לוגיסטיקה","#bf5af2"),("ניקיון","#00ff88"),("כללי","#8899aa")]
    legend_html = " &nbsp; ".join(
        f'<span style="color:{c}">⬤</span> <span style="color:var(--txt2);font-size:.78rem">{n}</span>'
        for n, c in CATS_COLORS)
    st.markdown(
        f'<div style="margin-bottom:12px;padding:10px 16px;background:var(--card);'
        f'border:1px solid var(--b1);border-radius:10px">'
        f'{legend_html} &nbsp;&nbsp; '
        f'<span style="color:#00ff88">⬤</span> <span style="color:var(--txt2);font-size:.78rem">בוצע</span> &nbsp; '
        f'<span style="color:#ff2d55">⬤</span> <span style="color:var(--txt2);font-size:.78rem">מפוגר</span>'
        f'</div>',
        unsafe_allow_html=True)

    st.markdown(f'<div style="color:var(--txt2);font-size:.8rem;margin-bottom:12px;font-family:var(--mono)">'
                f'◈ {len(events)} אירועים | 6 חודשים קדימה</div>', unsafe_allow_html=True)

    if HAS_CAL:
        st_calendar(events=events,
            options={
                "direction": "rtl", "locale": "he",
                "initialView": "dayGridMonth", "height": 680,
                "headerToolbar": {
                    "right": "today prev,next",
                    "center": "title",
                    "left": "dayGridMonth,timeGridWeek,listMonth"
                }
            },
            custom_css="""
              .fc { background:#0a1c35; color:#e2eeff; border-radius:16px; padding:14px; }
              .fc-toolbar-title { font-family:'Orbitron',monospace; color:#00d4ff; font-size:1.1rem; }
              .fc-button { background:#0d2240!important; border:1px solid rgba(0,212,255,.4)!important;
                           border-radius:8px!important; color:#00d4ff!important; font-weight:700!important; }
              .fc-button:hover { background:rgba(0,212,255,.15)!important; }
              .fc-button-active { background:rgba(0,212,255,.2)!important; }
              .fc-day-today { background:rgba(0,212,255,.08)!important; border:1px solid rgba(0,212,255,.3)!important; }
              .fc-event { border-radius:5px!important; border:none!important; font-size:.72rem; font-weight:600; }
              .fc-daygrid-day-number { color:#7a90b0; font-size:.8rem; }
              .fc-col-header-cell { background:#071526; }
              .fc-col-header-cell-cushion { color:#00d4ff; font-weight:700; font-size:.8rem; }
            """)
    else:
        st.warning("💡 התקן `streamlit-calendar` לתצוגה מלאה")
        upcoming = sorted([e for e in events if e["start"] >= today.strftime("%Y-%m-%d")],
                          key=lambda x: x["start"])[:50]
        if upcoming:
            edf = pd.DataFrame(upcoming)[["start", "title"]]
            edf.columns = ["תאריך", "משימה"]
            st.dataframe(edf, use_container_width=True, height=500)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: MANAGE TASKS
# ═══════════════════════════════════════════════════════════════════════════════
def page_manage():
    df = st.session_state.tasks

    # ── Filters ──
    f1, f2, f3, f4, f5 = st.columns(5)
    fsearch = f1.text_input("🔍 חיפוש", placeholder="שם משימה...")
    fpri    = f2.selectbox("עדיפות",   ["הכל"] + PRIS)
    fcat    = f3.selectbox("קטגוריה",  ["הכל"] + CATS)
    frec    = f4.selectbox("תדירות",   ["הכל"] + RECUR)
    fwork   = f5.selectbox("עובד",     ["הכל"] + WORKERS)

    filt = df.copy()
    if fsearch: filt = filt[filt["Task_Name"].str.contains(fsearch, na=False, case=False)]
    if fpri   != "הכל": filt = filt[filt["Priority"]    == fpri]
    if fcat   != "הכל": filt = filt[filt["Category"]    == fcat]
    if frec   != "הכל": filt = filt[filt["Recurring"]   == frec]
    if fwork  != "הכל": filt = filt[filt["Assigned_To"] == fwork]

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;margin:10px 0 16px">'
        f'<span style="color:var(--txt2);font-size:.82rem;font-family:var(--mono)">'
        f'◈ {len(filt)} / {len(df)} משימות</span>'
        f'<div style="flex:1">{pbar(round(len(filt)/max(len(df),1)*100), height=4)}</div>'
        f'</div>', unsafe_allow_html=True)

    # Tab view: All / By category
    tab_all, tab_cat = st.tabs(["📋 כל המשימות", "🏷️ לפי קטגוריה"])

    with tab_all:
        for idx, row in filt.iterrows():
            ci, ce, cd = st.columns([5, 1, 1])
            asgn_b = badge(str(row.get("Assigned_To", "")), "green") if row.get("Assigned_To") else ""
            ci.markdown(
                f'<div class="tc">'
                f'<b style="font-size:.95rem">{row["Task_Name"]}</b> '
                f'{pri_badge(row.get("Priority","רגיל"))} '
                f'{cat_badge(row.get("Category",""))} '
                f'{badge(row.get("Recurring",""),"gray")} {asgn_b}'
                f'{"<div style=color:var(--txt2);font-size:.78rem;margin-top:4px;font-family:var(--mono)>"+str(row.get("Description",""))+"</div>" if row.get("Description") else ""}'
                f'</div>', unsafe_allow_html=True)

            with ce:
                with st.popover("✏️", use_container_width=True):
                    nn = st.text_input("שם", value=row["Task_Name"], key=f"en{row['ID']}")
                    nd = st.text_area("תיאור", value=str(row.get("Description", "")), key=f"ed{row['ID']}")
                    np = st.selectbox("עדיפות", PRIS,
                        index=PRIS.index(row.get("Priority","רגיל")) if row.get("Priority") in PRIS else 0,
                        key=f"ep{row['ID']}")
                    nc = st.selectbox("קטגוריה", CATS,
                        index=CATS.index(row.get("Category","כללי")) if row.get("Category") in CATS else 0,
                        key=f"ec{row['ID']}")
                    nr = st.selectbox("תדירות", RECUR,
                        index=RECUR.index(row.get("Recurring","יומי")) if row.get("Recurring") in RECUR else 0,
                        key=f"er{row['ID']}")
                    na = st.selectbox("שייך ל", ["—"] + WORKERS,
                        index=(WORKERS.index(row.get("Assigned_To","")) + 1
                               if row.get("Assigned_To") in WORKERS else 0),
                        key=f"ea{row['ID']}")
                    nd2 = st.date_input("תאריך", value=pd.to_datetime(row["Date"]).date(),
                                        key=f"edt{row['ID']}")
                    if st.button("💾 שמור שינויים", key=f"sv{row['ID']}", use_container_width=True):
                        st.session_state.tasks.at[idx, "Task_Name"]   = nn
                        st.session_state.tasks.at[idx, "Description"] = nd
                        st.session_state.tasks.at[idx, "Priority"]    = np
                        st.session_state.tasks.at[idx, "Category"]    = nc
                        st.session_state.tasks.at[idx, "Recurring"]   = nr
                        st.session_state.tasks.at[idx, "Assigned_To"] = "" if na == "—" else na
                        st.session_state.tasks.at[idx, "Date"]        = nd2.strftime("%Y-%m-%d")
                        st.rerun()

            with cd:
                ck = f"cfm_{row['ID']}"
                if not st.session_state.get(ck):
                    if st.button("🗑️", key=f"dl{row['ID']}", help="מחק משימה"):
                        st.session_state[ck] = True; st.rerun()
                else:
                    st.warning("בטוח?")
                    if st.button("כן", key=f"cy{row['ID']}"):
                        st.session_state.tasks = st.session_state.tasks.drop(idx).reset_index(drop=True)
                        st.session_state.pop(ck, None); st.rerun()
                    if st.button("לא", key=f"cn{row['ID']}"):
                        st.session_state.pop(ck, None); st.rerun()

    with tab_cat:
        for cat in CATS:
            cat_tasks = filt[filt["Category"] == cat]
            if cat_tasks.empty: continue
            with st.expander(f"{cat_badge(cat)} {cat} — {len(cat_tasks)} משימות", expanded=False):
                for idx, row in cat_tasks.iterrows():
                    st.markdown(
                        f'<div class="tc">'
                        f'<b>{row["Task_Name"]}</b> {pri_badge(row.get("Priority","רגיל"))} '
                        f'{badge(row.get("Recurring",""),"gray")}'
                        f'{"<br><span style=color:var(--txt2);font-size:.78rem>"+str(row.get("Description",""))+"</span>" if row.get("Description") else ""}'
                        f'</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: ADD TASK
# ═══════════════════════════════════════════════════════════════════════════════
def page_add():
    c_form, c_preview = st.columns([2, 1])

    with c_form:
        with st.form("add_form", clear_on_submit=True):
            sec_header("➕ הוספת משימה חדשה")
            a, b = st.columns(2)
            name = a.text_input("שם המשימה *", placeholder="לדוגמה: בדיקת מלאי אזור D")
            freq = b.selectbox("תדירות חזרה", RECUR)
            desc = st.text_area("פירוט / הוראות ביצוע",
                                placeholder="תאר את המשימה בפירוט: מה לבדוק, איך לבצע, מה לתעד...")
            c, d, e = st.columns(3)
            pri  = c.selectbox("עדיפות",   PRIS)
            cat  = d.selectbox("קטגוריה",  CATS)
            asgn = e.selectbox("שייך לעובד", ["—"] + WORKERS)
            sdate = st.date_input("תאריך התחלה", datetime.now())

            submitted = st.form_submit_button("🚀 שמור משימה", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("⚠️ שם משימה הוא שדה חובה")
                else:
                    new_row = {
                        "ID": st.session_state.next_id,
                        "Task_Name": name.strip(), "Description": desc,
                        "Recurring": freq, "Date": sdate.strftime("%Y-%m-%d"),
                        "Done_Dates": "", "Priority": pri, "Category": cat,
                        "Assigned_To": "" if asgn == "—" else asgn,
                    }
                    st.session_state.tasks = pd.concat(
                        [st.session_state.tasks, pd.DataFrame([new_row])],
                        ignore_index=True)
                    st.session_state.next_id += 1
                    st.success(f"✅ משימה '{name}' נוספה בהצלחה!")
                    st.rerun()

    with c_preview:
        sec_header("📊 סטטיסטיקת משימות")
        df = st.session_state.tasks
        total = len(df)

        # By recurring type
        st.markdown("**לפי תדירות:**")
        for rec in RECUR:
            cnt = len(df[df["Recurring"] == rec])
            if cnt:
                p = round(cnt / total * 100)
                st.markdown(
                    f'<div class="stat-row">'
                    f'<span class="stat-label">{rec}</span>'
                    f'<span class="stat-val">{cnt}</span>'
                    f'</div>{pbar(p, height=4)}', unsafe_allow_html=True)

        # By category
        st.markdown("**לפי קטגוריה:**")
        for cat in CATS:
            cnt = len(df[df["Category"] == cat])
            if cnt:
                p = round(cnt / total * 100)
                st.markdown(
                    f'<div class="stat-row">'
                    f'{cat_badge(cat)}'
                    f'<span class="stat-val">{cnt}</span>'
                    f'</div>{pbar(p, height=4)}', unsafe_allow_html=True)

        # By worker
        st.markdown("**לפי עובד:**")
        for w in WORKERS:
            cnt = len(df[df["Assigned_To"] == w])
            if cnt:
                p = round(cnt / total * 100)
                st.markdown(
                    f'<div class="stat-row">'
                    f'<span class="stat-label">👤 {w}</span>'
                    f'<span class="stat-val">{cnt}</span>'
                    f'</div>{pbar(p, height=4)}', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: WORKERS ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
def page_workers():
    df = st.session_state.tasks
    today = datetime.now().date()

    sec_header("👥 ניתוח ביצועי עובדים")

    # 30-day performance per worker
    perf = []
    for w in WORKERS:
        wdf = df[df["Assigned_To"] == w]
        tot = 0; don = 0
        for i in range(30):
            d = today - timedelta(days=i)
            ts = tasks_for_date(wdf, d)
            tot += len(ts)
            don += sum(1 for t in ts if t["is_done"])
        pct = round(don / tot * 100) if tot else 0
        streak = 0
        for i in range(30):
            d = today - timedelta(days=i)
            ts = tasks_for_date(wdf, d)
            if not ts: continue
            if all(t["is_done"] for t in ts): streak += 1
            else: break
        perf.append({"עובד": w, "ביצוע": pct, "בוצע": don,
                     "סה\"כ": tot, "רצף_ימים": streak})

    perf_df = pd.DataFrame(perf).sort_values("ביצוע", ascending=False)

    # Worker cards
    cols = st.columns(3)
    for wi, (_, row) in enumerate(perf_df.iterrows()):
        with cols[wi % 3]:
            pct = int(row["ביצוע"])
            c = "#00ff88" if pct >= 80 else "#ffb800" if pct >= 50 else "#ff2d55"
            medal = "🥇" if wi == 0 else "🥈" if wi == 1 else "🥉" if wi == 2 else "👤"
            st.markdown(f"""
            <div class="kpi kpi-{'green' if pct>=80 else 'amber' if pct>=50 else 'red'}"
                 style="margin-bottom:14px">
              <div style="font-size:2rem;margin-bottom:6px">{medal}</div>
              <div style="font-weight:800;font-size:1rem;color:var(--txt);margin-bottom:8px">{row['עובד']}</div>
              <div class="kpi-val" style="color:{c};font-size:2.2rem">{pct}%</div>
              <div class="kpi-lbl">ביצוע 30 ימים</div>
              <div style="color:var(--txt2);font-size:.72rem;font-family:var(--mono);margin-top:6px">
                {int(row['בוצע'])} / {int(row['סה"כ'])} משימות
              </div>
            </div>
            {pbar(pct, c, 6)}
            """, unsafe_allow_html=True)

    if HAS_PLOTLY:
        st.markdown("---")
        sec_header("📊 גרף ביצועים השוואתי")
        colors_w = ["#00ff88" if v >= 80 else "#ffb800" if v >= 50 else "#ff2d55"
                    for v in perf_df["ביצוע"]]
        fig = go.Figure(go.Bar(
            x=perf_df["ביצוע"], y=perf_df["עובד"],
            orientation="h", marker_color=colors_w,
            text=[f"{v}%" for v in perf_df["ביצוע"]],
            textposition="outside", textfont=dict(color="#e2eeff", size=12)))
        fig.add_vline(x=80, line_dash="dot", line_color="rgba(0,255,136,.4)",
                      annotation_text="יעד 80%", annotation_font_color="#00ff88")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Heebo", color="#e2eeff"), height=340,
            margin=dict(t=10, b=10, l=100, r=80),
            xaxis=dict(range=[0, 120], gridcolor="rgba(255,255,255,.04)"),
            yaxis=dict(gridcolor="rgba(255,255,255,.03)"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Tasks distribution donut per worker
        st.markdown("---")
        sec_header("📋 התפלגות משימות לפי עובד")
        worker_counts = {w: len(df[df["Assigned_To"] == w]) for w in WORKERS}
        fig2 = go.Figure(go.Pie(
            labels=list(worker_counts.keys()),
            values=list(worker_counts.values()),
            hole=.55, textinfo="label+percent",
            textfont=dict(size=11, color="#e2eeff"),
            marker_colors=["#00d4ff","#00ff88","#ffb800","#ff2d55","#bf5af2","#ff6b8a"],
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=320,
            margin=dict(t=10, b=0, l=0, r=0),
            legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#e2eeff"),
            font=dict(family="Heebo"))
        st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS (מנהל בלבד)
# ═══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    df = st.session_state.tasks
    today = datetime.now()
    sec_header("🔬 אנליטיקס מתקדם")

    if not HAS_PLOTLY:
        st.warning("נדרש plotly לדף זה")
        return

    # ── 4-panel overview ──
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["ביצועים שבועיים", "התפלגות קטגוריות",
                        "עומס לפי יום בשבוע", "ביצועים חודשיים"],
        specs=[[{"type":"scatter"},{"type":"pie"}],
               [{"type":"bar"},{"type":"bar"}]],
        vertical_spacing=0.15, horizontal_spacing=0.1)

    # 1. Weekly trend
    wdf = week_stats(21)
    fig.add_trace(go.Scatter(
        x=wdf["תאריך"], y=wdf["אחוז"], mode="lines+markers",
        line=dict(color="#00d4ff", width=2), marker=dict(size=7, color="#00d4ff"),
        name="אחוז"), row=1, col=1)

    # 2. Category pie
    cat_counts = df["Category"].value_counts()
    CMAP = {"בטיחות":"#ff2d55","ספירה":"#00d4ff","תחזוקה":"#ffb800",
            "לוגיסטיקה":"#bf5af2","ניקיון":"#00ff88","כללי":"#8899aa"}
    fig.add_trace(go.Pie(
        labels=cat_counts.index.tolist(),
        values=cat_counts.values.tolist(),
        hole=.5, textinfo="label+percent",
        marker_colors=[CMAP.get(c,"#8899aa") for c in cat_counts.index],
        showlegend=False, name=""), row=1, col=2)

    # 3. Load by day of week
    day_load = {d: 0 for d in range(5)}
    for _, row in df.iterrows():
        rec = row["Recurring"]
        if rec == "יומי":
            for d in range(5): day_load[d] += 1
        elif rec == "שבועי":
            try:
                base = pd.to_datetime(row["Date"]).date()
                day_load[base.weekday() % 5] += 1
            except: pass
    day_names_en = ["ראשון","שני","שלישי","רביעי","חמישי"]
    fig.add_trace(go.Bar(
        x=day_names_en, y=[day_load[i] for i in range(5)],
        marker_color=["rgba(0,212,255,.7)"]*5,
        name="עומס"), row=2, col=1)

    # 4. Monthly 6-month trend
    months_data = []
    for m in range(6, 0, -1):
        dt = today - timedelta(days=30 * m)
        mdf = monthly_stats(dt.year, dt.month)
        if not mdf.empty:
            months_data.append({
                "חודש": f"{dt.month:02d}/{dt.year}",
                "ממוצע": round(mdf["אחוז"].mean())
            })
    if months_data:
        mtrend = pd.DataFrame(months_data)
        colors_mt = ["#00ff88" if v >= 80 else "#ffb800" if v >= 50 else "#ff2d55"
                     for v in mtrend["ממוצע"]]
        fig.add_trace(go.Bar(
            x=mtrend["חודש"], y=mtrend["ממוצע"],
            marker_color=colors_mt, name="ממוצע חודשי",
            text=[f"{v}%" for v in mtrend["ממוצע"]],
            textposition="outside", textfont=dict(color="#e2eeff", size=10)), row=2, col=2)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Heebo", color="#e2eeff"), height=700,
        margin=dict(t=60, b=40, l=20, r=20),
        showlegend=False,
        yaxis=dict(gridcolor="rgba(255,255,255,.04)"),
        yaxis3=dict(gridcolor="rgba(255,255,255,.04)"),
        yaxis4=dict(gridcolor="rgba(255,255,255,.04)"),
    )
    for ann in fig.layout.annotations:
        ann.update(font=dict(color="#00d4ff", size=13, family="Orbitron"))
    st.plotly_chart(fig, use_container_width=True)

    # ── Priority heatmap ──
    st.markdown("---")
    sec_header("🔥 מפת חום — עדיפות × קטגוריה")
    heat_data = {}
    for _, row in df.iterrows():
        p = str(row.get("Priority","רגיל"))
        c = str(row.get("Category","כללי"))
        heat_data.setdefault(p, {})
        heat_data[p][c] = heat_data[p].get(c, 0) + 1

    heat_df = pd.DataFrame(heat_data).fillna(0).T
    heat_df = heat_df.reindex(columns=PRIS, fill_value=0)
    fig_heat = go.Figure(go.Heatmap(
        z=heat_df.values, x=heat_df.columns.tolist(),
        y=heat_df.index.tolist(),
        colorscale=[[0,"rgba(0,212,255,.05)"],[0.5,"rgba(0,212,255,.4)"],[1,"#00d4ff"]],
        text=heat_df.values, texttemplate="%{text}",
        textfont=dict(size=14, color="#e2eeff"), showscale=False))
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Heebo", color="#e2eeff"), height=300,
        margin=dict(t=10, b=10, l=80, r=20),
        xaxis=dict(side="top"), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_heat, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
check_timeout()

if not st.session_state.user_role:
    login_screen()
    st.stop()

role = st.session_state.user_role
lt   = st.session_state.login_time
elapsed_min = int((datetime.now() - lt).total_seconds() / 60) if lt else 0

# ── Sidebar ──
ROLE_ICONS = {"מנהל WMS": "🔑", "צוות מחסן": "📦", "הנהלה": "📊"}
df_side = st.session_state.tasks
today_side = len(tasks_for_date(df_side, datetime.now()))
ov_side    = len(get_overdue())

st.sidebar.markdown(f"""
<div style="padding:20px 0 12px;text-align:center">
  <div style="font-size:2.4rem;margin-bottom:8px">{ROLE_ICONS.get(role,'👤')}</div>
  <div style="font-family:'Orbitron',monospace;font-weight:700;font-size:.95rem;
              color:var(--cyan);letter-spacing:1px">{role}</div>
  <div style="font-size:.72rem;color:var(--txt2);margin-top:4px;font-family:var(--mono)">
    ● מחובר {elapsed_min} דק'
  </div>
</div>
<div style="background:var(--card2);border:1px solid var(--b1);border-radius:10px;
            padding:10px 12px;margin-bottom:16px;font-family:var(--mono);font-size:.72rem">
  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
    <span style="color:var(--txt2)">להיום:</span>
    <span style="color:var(--cyan);font-weight:700">{today_side}</span>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
    <span style="color:var(--txt2)">פיגורים:</span>
    <span style="color:{'var(--red)' if ov_side else 'var(--green)'};font-weight:700">{ov_side}</span>
  </div>
  <div style="display:flex;justify-content:space-between">
    <span style="color:var(--txt2)">סה"כ:</span>
    <span style="color:var(--txt);font-weight:700">{len(df_side)}</span>
  </div>
</div>
""", unsafe_allow_html=True)

MENUS = {
    "מנהל WMS":  ["📊 דשבורד","📋 סידור עבודה","📅 לוח שנה",
                  "➕ הוספת משימה","⚙️ ניהול משימות","👥 עובדים","🔬 אנליטיקס"],
    "הנהלה":     ["📊 דשבורד","📅 לוח שנה","👥 עובדים","🔬 אנליטיקס"],
    "צוות מחסן": ["📊 דשבורד","📋 סידור עבודה","📅 לוח שנה"],
}
choice = st.sidebar.radio("", MENUS[role], label_visibility="collapsed")

st.sidebar.markdown("---")
if elapsed_min >= 50:
    st.sidebar.markdown(
        f'<div class="al al-amber" style="font-size:.78rem;padding:8px 12px">'
        f'⚠️ הסשן יפוג בעוד {60-elapsed_min} דק\'</div>',
        unsafe_allow_html=True)
if st.sidebar.button("🚪 התנתקות", use_container_width=True):
    st.session_state.user_role = None
    st.session_state.login_time = None
    st.rerun()

# ── Header Banner ──
PAGE_ICONS = {
    "📊 דשבורד":"📊 דשבורד בקרה","📋 סידור עבודה":"📋 סידור עבודה שבועי",
    "📅 לוח שנה":"📅 לוח שנה","➕ הוספת משימה":"➕ הוספת משימה חדשה",
    "⚙️ ניהול משימות":"⚙️ ניהול ועריכת משימות","👥 עובדים":"👥 ביצועי עובדים",
    "🔬 אנליטיקס":"🔬 אנליטיקס מתקדם",
}
st.markdown(
    f'<div class="mega-banner" style="padding:18px 32px;margin-bottom:20px">'
    f'<h1 style="font-size:1.4rem;letter-spacing:2px">{PAGE_ICONS.get(choice,choice)}</h1>'
    f'<div class="sub"><span class="live-dot"></span> {datetime.now().strftime("%d/%m/%Y %H:%M")} &nbsp;|&nbsp; {role}</div>'
    f'</div>', unsafe_allow_html=True)

# ── Route ──
if   choice == "📊 דשבורד":          page_dashboard()
elif choice == "📋 סידור עבודה":     page_work()
elif choice == "📅 לוח שנה":          page_calendar()
elif choice == "➕ הוספת משימה":     page_add()
elif choice == "⚙️ ניהול משימות":    page_manage()
elif choice == "👥 עובדים":           page_workers()
elif choice == "🔬 אנליטיקס":        page_analytics()
