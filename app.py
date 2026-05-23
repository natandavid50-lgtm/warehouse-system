import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from streamlit_calendar import calendar
from supabase import create_client
import calendar as pycal


# =========================
# 1) App Config
# =========================
st.set_page_config(
    page_title="אחים כהן | ניהול מחסן",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# 2) Supabase Connection
# =========================
# חשוב: להגדיר ב-.streamlit/secrets.toml:
# SUPABASE_URL="https://....supabase.co"
# SUPABASE_KEY="...."
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")


@st.cache_resource
def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in st.secrets")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def safe_db():
    try:
        return get_supabase_client()
    except Exception as e:
        st.error(f"שגיאת התחברות ל-Supabase: {e}")
        st.stop()


db = safe_db()

# =========================
# 3) Theme / CSS (Modern Dark UI)
# =========================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800;900&display=swap');

:root {
    --bg: #0b1220;
    --bg-soft: #111a2e;
    --card: #141f36;
    --card-2: #1a2744;
    --text: #e6edf9;
    --muted: #9fb0d0;
    --accent: #59a5ff;
    --accent-2: #7c5cff;
    --success: #2dd4bf;
    --warning: #fbbf24;
    --danger: #f87171;
    --border: rgba(151, 174, 225, 0.18);
    --glow: 0 8px 30px rgba(92, 130, 255, 0.18);
}

html, body, [class*="css"] {
    font-family: "Heebo", sans-serif !important;
}

.stApp {
    direction: rtl;
    text-align: right;
    background:
        radial-gradient(1200px 600px at 100% -10%, rgba(124, 92, 255, 0.20), transparent 50%),
        radial-gradient(900px 500px at -10% 0%, rgba(89, 165, 255, 0.20), transparent 45%),
        linear-gradient(180deg, #0a1120 0%, #0b1220 100%);
    color: var(--text);
}

/* Top spacing + container */
.main .block-container {
    padding-top: 1.4rem;
    padding-bottom: 1.6rem;
    max-width: 1400px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d172b 0%, #0f1b33 100%) !important;
    border-left: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* Headings */
h1, h2, h3 {
    color: var(--text) !important;
    letter-spacing: 0.2px;
}
.hero-title {
    text-align: center;
    font-size: 3rem !important;
    font-weight: 900;
    line-height: 1.15;
    margin: 0.6rem 0 0.3rem 0;
    background: linear-gradient(90deg, #dfeaff 0%, #9ac8ff 35%, #c0b4ff 70%, #e7efff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    text-align: center;
    color: var(--muted);
    margin-bottom: 1.2rem;
}

/* Cards */
.glass-card {
    background: linear-gradient(135deg, rgba(29, 44, 77, 0.85), rgba(20, 31, 54, 0.95));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: var(--glow);
    backdrop-filter: blur(8px);
}
.task-card {
    background: linear-gradient(135deg, #14203a 0%, #18274a 100%);
    border: 1px solid var(--border);
    border-right: 6px solid var(--accent);
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: var(--text);
}
.task-card.done {
    border-right-color: var(--success);
}
.task-card.pending {
    border-right-color: var(--warning);
}
.task-title {
    font-weight: 800;
    font-size: 1.05rem;
}
.task-desc {
    color: var(--muted);
    margin-top: 4px;
    font-size: 0.95rem;
}

/* Metrics */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(21, 34, 60, 0.9), rgba(18, 29, 52, 0.95));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 12px 14px;
    box-shadow: var(--glow);
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    color: #f4f8ff !important;
    font-weight: 900 !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #0f1a31 !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px rgba(89, 165, 255, 0.4) !important;
}

/* Buttons */
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(90deg, #3b82f6 0%, #7c5cff 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    padding: 0.55rem 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 6px 18px rgba(82, 127, 255, 0.35) !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.06);
}

/* Checkbox labels */
.stCheckbox label {
    color: var(--text) !important;
    font-weight: 500;
}

/* Radio */
[data-testid="stRadio"] label {
    color: var(--text) !important;
}

/* Success/info messages */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 12px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# 4) Constants & Session State
# =========================
OPT_DASH = "📊 דשבורד בקרה"
OPT_WORK = "📋 סידור עבודה"
OPT_CAL = "📅 לוח שנה"
OPT_ADD = "➕ הוספת משימה"
OPT_MANAGE = "⚙️ הגדרות"

if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "current_page" not in st.session_state:
    st.session_state.current_page = None


# =========================
# 5) Utilities
# =========================
def parse_done_dates(done_str) -> set[str]:
    if done_str is None:
        return set()
    s = str(done_str).strip()
    if not s:
        return set()
    return {d.strip() for d in s.split(",") if d.strip()}


def serialize_done_dates(done_dates: set[str]) -> str:
    return ",".join(sorted(done_dates))


def add_months(d: date, months: int) -> date:
    """
    חיבור חודשים באופן קלנדרי אמיתי:
    31/01 + חודש => 28/29/02
    """
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, pycal.monthrange(year, month)[1])
    return date(year, month, day)


def is_scheduled_on(base_date: date, recurring: str, target_date: date) -> bool:
    if target_date < base_date:
        return False

    if recurring == "לא":
        return target_date == base_date
    if recurring == "יומי":
        return True
    if recurring == "שבועי":
        return (target_date - base_date).days % 7 == 0
    if recurring == "דו-שבועי":
        return (target_date - base_date).days % 14 == 0
    if recurring == "חודשי":
        # בדיקה חודשית קלנדרית אמיתית
        if target_date.day != min(base_date.day, pycal.monthrange(target_date.year, target_date.month)[1]):
            return False
        # חייב להיות לפחות אותו חודש/שנה ומעלה
        return (target_date.year, target_date.month) >= (base_date.year, base_date.month)

    return False


def generate_occurrences(base_date: date, recurring: str, days_ahead: int = 45) -> list[date]:
    dates = []
    end_date = date.today() + timedelta(days=days_ahead)

    if recurring == "לא":
        if base_date <= end_date:
            dates.append(base_date)
        return dates

    current = base_date
    while current <= end_date:
        dates.append(current)
        if recurring == "יומי":
            current += timedelta(days=1)
        elif recurring == "שבועי":
            current += timedelta(days=7)
        elif recurring == "דו-שבועי":
            current += timedelta(days=14)
        elif recurring == "חודשי":
            current = add_months(current, 1)
        else:
            break

    return dates


# =========================
# 6) Data Layer
# =========================
EXPECTED_COLS = ["ID", "Task_Name", "Description", "Recurring", "Date", "Done_Dates"]


def empty_tasks_df():
    return pd.DataFrame(columns=EXPECTED_COLS)


def normalize_tasks_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw.empty:
        return empty_tasks_df()

    # מיפוי שמות עמודות גמיש
    rename_map = {
        "id": "ID",
        "task_name": "Task_Name",
        "description": "Description",
        "recurring": "Recurring",
        "task_date": "Date",
        "date": "Date",
        "done_dates": "Done_Dates",
    }
    df = df_raw.rename(columns=rename_map)

    for c in EXPECTED_COLS:
        if c not in df.columns:
            df[c] = ""

    # סדר עמודות
    df = df[EXPECTED_COLS].copy()

    # ניקוי בסיסי
    df["Task_Name"] = df["Task_Name"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    df["Recurring"] = df["Recurring"].fillna("לא").astype(str)
    df["Done_Dates"] = df["Done_Dates"].fillna("").astype(str)

    return df


def load_data() -> pd.DataFrame:
    try:
        res = db.table("tasks").select("*").execute()
        data = res.data or []
        return normalize_tasks_df(pd.DataFrame(data))
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים: {e}")
        return empty_tasks_df()


def save_new_task(name: str, desc: str, freq: str, task_date: date) -> tuple[bool, str]:
    try:
        # מתאים לרוב לטבלאות id מסוג bigint
        new_id = int(datetime.now().timestamp() * 1000)
        db.table("tasks").insert(
            {
                "id": new_id,
                "task_name": name.strip(),
                "description": desc.strip(),
                "recurring": freq,
                "task_date": str(task_date),
                "done_dates": "",
            }
        ).execute()
        return True, "המשימה נשמרה בהצלחה"
    except Exception as e:
        return False, f"שגיאה בשמירת המשימה: {e}"


def mark_task_done(task_id, existing_done_str: str, day_str: str) -> tuple[bool, str]:
    try:
        done = parse_done_dates(existing_done_str)
        done.add(day_str)
        db.table("tasks").update({"done_dates": serialize_done_dates(done)}).eq("id", task_id).execute()
        return True, "סומן בהצלחה"
    except Exception as e:
        return False, f"שגיאה בסימון המשימה: {e}"


def delete_task(task_id) -> tuple[bool, str]:
    try:
        db.table("tasks").delete().eq("id", task_id).execute()
        return True, "המשימה נמחקה"
    except Exception as e:
        return False, f"שגיאה במחיקה: {e}"


def get_daily_status(df_input: pd.DataFrame, target_dt: datetime) -> list[dict]:
    if df_input.empty:
        return []

    target_date = target_dt.date()
    target_str = target_date.strftime("%Y-%m-%d")
    scheduled = []

    for _, row in df_input.iterrows():
        try:
            base_date = pd.to_datetime(row["Date"]).date()
            recurring = str(row["Recurring"]).strip() or "לא"

            if is_scheduled_on(base_date, recurring, target_date):
                done_dates = parse_done_dates(row["Done_Dates"])
                scheduled.append(
                    {
                        "id": row["ID"],
                        "name": row["Task_Name"],
                        "desc": row["Description"],
                        "is_done": target_str in done_dates,
                        "done_str": serialize_done_dates(done_dates),
                    }
                )
        except Exception:
            # לא מפילים את כל האפליקציה בגלל רשומה בודדת תקולה
            continue

    return scheduled


# =========================
# 7) Login Screen
# =========================
if st.session_state.user_role is None:
    st.markdown('<div class="hero-title">אחים כהן • ניהול משימות מחסן</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">מערכת מתקדמת לניהול תפעול, מעקב ביצועים וסנכרון צוות</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="large")
    roles = [
        {"role": 'סמנכ"ל', "icon": "📊", "id": "vp", "desc": "דשבורד ניהולי ובקרה"},
        {"role": "צוות מחסן", "icon": "📦", "id": "staff", "desc": "ביצוע משימות יומיות"},
        {"role": "מנהל WMS", "icon": "🔐", "id": "admin", "desc": "ניהול מלא והגדרות"},
    ]

    cols = [c1, c2, c3]
    for i, col in enumerate(cols):
        r = roles[i]
        with col:
            st.markdown(
                f"""
                <div class="glass-card">
                    <h3 style="margin:0 0 4px 0;">{r["icon"]} {r["role"]}</h3>
                    <div style="color:var(--muted); margin-bottom:10px;">{r["desc"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"כניסה כ- {r['role']}", key=f"btn_{r['id']}", use_container_width=True):
                st.session_state.user_role = r["role"]
                st.session_state.current_page = OPT_WORK if r["role"] == "צוות מחסן" else OPT_DASH
                st.rerun()

    st.stop()

# =========================
# 8) Sidebar Navigation
# =========================
df = load_data()

if st.session_state.user_role == "מנהל WMS":
    menu = [OPT_DASH, OPT_WORK, OPT_CAL, OPT_ADD, OPT_MANAGE]
elif st.session_state.user_role == "צוות מחסן":
    menu = [OPT_WORK, OPT_CAL]
else:
    menu = [OPT_DASH, OPT_CAL]

with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.user_role} 👋")
    choice = st.radio("ניווט", menu)
    st.session_state.current_page = choice
    st.markdown("---")
    if st.button("🚪 התנתקות", key="logout_btn", use_container_width=True):
        st.session_state.user_role = None
        st.session_state.current_page = None
        st.rerun()

# =========================
# 9) Pages
# =========================
if choice == OPT_DASH:
    st.title(OPT_DASH)

    today_tasks = get_daily_status(df, datetime.now())
    total = len(today_tasks)
    done = sum(1 for t in today_tasks if t["is_done"])
    pct = int((done / total) * 100) if total else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("📌 משימות היום", total)
    c2.metric("✅ בוצעו", done)
    c3.metric("📈 אחוז ביצוע", f"{pct}%")

    st.markdown("### סטטוס משימות יומי")
    if not today_tasks:
        st.info("אין משימות מתוזמנות להיום.")
    else:
        for t in today_tasks:
            cls = "done" if t["is_done"] else "pending"
            icon = "✅" if t["is_done"] else "🕒"
            desc = t["desc"] if t["desc"] else "ללא תיאור"
            st.markdown(
                f"""
                <div class="task-card {cls}">
                    <div class="task-title">{icon} {t["name"]}</div>
                    <div class="task-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

elif choice == OPT_WORK:
    st.title(OPT_WORK)

    today = datetime.now()
    # שבוע שמתחיל ביום ראשון
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    days_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
    cols = st.columns(5, gap="medium")

    for i, day_name in enumerate(days_names):
        curr_day = start_of_week + timedelta(days=i)
        curr_str = curr_day.strftime("%Y-%m-%d")

        # כדי RTL יראה נכון כמו אצלך
        with cols[4 - i]:
            st.markdown(
                f"""
                <div class="glass-card" style="padding:10px 12px; margin-bottom:8px;">
                    <div style="font-weight:800;">{day_name}</div>
                    <div style="color:var(--muted);">{curr_day.strftime('%d/%m/%Y')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            tasks_for_day = get_daily_status(df, curr_day)
            if not tasks_for_day:
                st.caption("אין משימות")
                continue

            for t in tasks_for_day:
                if t["is_done"]:
                    st.success(f"✅ {t['name']}")
                else:
                    if st.checkbox(f"בצע: {t['name']}", key=f"chk_{t['id']}_{curr_str}"):
                        ok, msg = mark_task_done(t["id"], t["done_str"], curr_str)
                        if ok:
                            st.rerun()
                        else:
                            st.error(msg)

elif choice == OPT_CAL:
    st.title(OPT_CAL)

    events = []
    if not df.empty:
        for _, row in df.iterrows():
            try:
                base_date = pd.to_datetime(row["Date"]).date()
                recurring = str(row["Recurring"]).strip() or "לא"
                done_dates = parse_done_dates(row["Done_Dates"])
                task_name = str(row["Task_Name"]).strip() or "משימה"

                for occ in generate_occurrences(base_date, recurring, days_ahead=60):
                    d = occ.strftime("%Y-%m-%d")
                    events.append(
                        {
                            "title": task_name,
                            "start": d,
                            "color": "#2dd4bf" if d in done_dates else "#f87171",
                        }
                    )
            except Exception:
                continue

    calendar(
        events=events,
        options={
            "direction": "rtl",
            "locale": "he",
            "height": 700,
            "firstDay": 0,  # ראשון
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,listWeek",
            },
        },
        key="warehouse_cal",
    )

elif choice == OPT_ADD:
    st.title(OPT_ADD)

    with st.form("add_new_task_form"):
        name = st.text_input("שם המשימה")
        desc = st.text_area("תיאור")
        freq = st.selectbox("תדירות", ["לא", "יומי", "שבועי", "דו-שבועי", "חודשי"])
        task_date = st.date_input("תאריך התחלה", value=datetime.now().date())

        submitted = st.form_submit_button("💾 שמור בענן")
        if submitted:
            if not name or not name.strip():
                st.warning("יש להזין שם משימה.")
            else:
                ok, msg = save_new_task(name, desc, freq, task_date)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

elif choice == OPT_MANAGE:
    st.title(OPT_MANAGE)

    if df.empty:
        st.info("אין משימות לניהול.")
    else:
        for _, row in df.iterrows():
            c1, c2 = st.columns([5, 1], gap="small")
            with c1:
                st.markdown(
                    f"""
                    <div class="glass-card" style="margin-bottom:8px;">
                        <div style="font-weight:800;">{row['Task_Name']}</div>
                        <div style="color:var(--muted);">תדירות: {row['Recurring']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button("🗑️ מחק", key=f"del_{row['ID']}", use_container_width=True):
                    ok, msg = delete_task(row["ID"])
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
