import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os, hashlib, io, json
import calendar as cal_lib

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    from streamlit_calendar import calendar as st_calendar
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

# ═══════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════
st.set_page_config(page_title="אחים כהן WMS", layout="wide",
                   initial_sidebar_state="expanded", page_icon="📦")

DB_FILE       = "wms_tasks.csv"
INV_FILE      = "wms_inventory.csv"
AUDIT_FILE    = "wms_audit.csv"
WORKERS_FILE  = "wms_workers.csv"
SESSION_MINS  = 60

DEFAULT_HASH  = hashlib.sha256(b"1234").hexdigest()
try:
    ADMIN_HASH = st.secrets.get("ADMIN_HASH", DEFAULT_HASH)
except Exception:
    ADMIN_HASH = DEFAULT_HASH

WORKERS_DEFAULT = ["יוסי כהן","דוד לוי","מיכל אברהם","אחמד חסן","רינה שמיר"]
PRIORITIES = ["רגיל","דחוף","גבוה","נמוך"]
CATEGORIES = ["כללי","בטיחות","לוגיסטיקה","ניקיון","תחזוקה","ספירה"]
RECURRENCES = ["לא","יומי","שבועי","דו-שבועי","חודשי"]

# ═══════════════════════════════════════════════════════
#  THEME / CSS
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&family=Orbitron:wght@500;700;900&display=swap');

:root {
  --bg:        #040d1c;
  --panel:     #071223;
  --card:      #0c1e3a;
  --card2:     #0f2448;
  --b:         rgba(56,139,253,.16);
  --bh:        rgba(56,139,253,.45);
  --blue:      #388bfd;
  --cyan:      #00d4ff;
  --green:     #00e5a0;
  --amber:     #f59e0b;
  --red:       #ff4d6d;
  --purple:    #a78bfa;
  --pink:      #f472b6;
  --txt:       #e8f0fe;
  --txt2:      #7a90b0;
  --r:         16px;
  --gb:        0 0 28px rgba(56,139,253,.28);
  --gg:        0 0 28px rgba(0,229,160,.22);
}

html,body,[class*="css"]{font-family:"Heebo",sans-serif!important;direction:rtl;text-align:right;}

/* ── App bg ── */
.stApp{
  background-color:var(--bg)!important;
  background-image:
    linear-gradient(rgba(56,139,253,.035) 1px,transparent 1px),
    linear-gradient(90deg,rgba(56,139,253,.035) 1px,transparent 1px),
    radial-gradient(ellipse 90% 55% at 50% 0%,rgba(56,139,253,.09) 0%,transparent 68%);
  background-size:44px 44px,44px 44px,100% 100%;
}

/* ── Sidebar ── */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,var(--panel) 0%,#050f22 100%)!important;
  border-left:1px solid var(--b)!important;
}
[data-testid="stSidebar"] *{color:var(--txt)!important;}
[data-testid="stSidebar"] .stRadio label{
  background:transparent!important;border:1px solid transparent;
  border-radius:10px;padding:9px 14px;transition:all .2s;display:block;margin:2px 0;
}
[data-testid="stSidebar"] .stRadio label:hover{
  background:rgba(56,139,253,.1)!important;border-color:var(--bh)!important;
}

/* ── Banner ── */
.banner{
  background:linear-gradient(135deg,var(--card) 0%,#0b1e42 100%);
  padding:26px 36px;border-radius:var(--r);border:1px solid var(--bh);
  box-shadow:var(--gb),inset 0 1px 0 rgba(255,255,255,.04);
  margin-bottom:24px;text-align:center;position:relative;overflow:hidden;
}
.banner::before{
  content:'';position:absolute;top:-60px;left:50%;transform:translateX(-50%);
  width:320px;height:120px;
  background:radial-gradient(ellipse,rgba(56,139,253,.2) 0%,transparent 70%);
}
.banner h1{font-family:"Orbitron",monospace!important;font-weight:700!important;
  font-size:1.75rem!important;letter-spacing:2px!important;color:var(--cyan)!important;
  margin:0 0 4px!important;text-shadow:0 0 30px rgba(0,212,255,.45)!important;}
.banner .sub{color:var(--txt2)!important;font-size:.85rem;letter-spacing:1px;}

/* ── Metrics ── */
[data-testid="stMetric"]{
  background:var(--card)!important;padding:22px 18px!important;
  border-radius:var(--r)!important;border:1px solid var(--b)!important;
  box-shadow:0 4px 24px rgba(0,0,0,.35)!important;
  transition:transform .25s,box-shadow .25s!important;position:relative;overflow:hidden;
}
[data-testid="stMetric"]:hover{transform:translateY(-4px)!important;
  box-shadow:var(--gb),0 8px 32px rgba(0,0,0,.4)!important;border-color:var(--bh)!important;}
[data-testid="stMetric"]::before{content:'';position:absolute;top:0;right:0;width:100%;height:3px;
  background:linear-gradient(90deg,var(--blue),var(--cyan));}
[data-testid="stMetricLabel"]{color:var(--txt2)!important;font-size:.8rem!important;font-weight:500!important;}
[data-testid="stMetricValue"]{color:var(--cyan)!important;font-family:"Orbitron",monospace!important;
  font-weight:700!important;font-size:2rem!important;}

/* ── Buttons ── */
.stButton>button{
  background:linear-gradient(135deg,rgba(56,139,253,.14),rgba(56,139,253,.04))!important;
  border:1px solid var(--bh)!important;color:var(--cyan)!important;
  border-radius:10px!important;font-weight:600!important;transition:all .2s!important;
}
.stButton>button:hover{background:rgba(56,139,253,.22)!important;box-shadow:var(--gb)!important;}

/* ── Forms ── */
[data-testid="stForm"]{background:var(--card)!important;border:1px solid var(--b)!important;
  border-radius:var(--r)!important;padding:22px!important;}
[data-testid="stForm"] .stButton>button{
  background:linear-gradient(135deg,#388bfd,#1a6fd4)!important;
  color:#fff!important;border:none!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,
.stSelectbox>div>div,.stNumberInput>div>div>input,.stDateInput>div>div>input{
  background:var(--card)!important;border:1px solid var(--b)!important;
  border-radius:10px!important;color:var(--txt)!important;}
label[data-testid="stWidgetLabel"] p{color:var(--txt)!important;}

/* ── KPI big card ── */
.kpi-card{
  background:var(--card);border:1px solid var(--b);border-radius:var(--r);
  padding:20px;text-align:center;position:relative;overflow:hidden;transition:all .25s;
}
.kpi-card:hover{border-color:var(--bh);transform:translateY(-3px);box-shadow:var(--gb);}
.kpi-card::after{content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,transparent 60%,rgba(56,139,253,.04));pointer-events:none;}
.kpi-val{font-family:"Orbitron",monospace;font-size:2.6rem;font-weight:900;line-height:1;margin-bottom:6px;}
.kpi-lbl{font-size:.78rem;color:var(--txt2);letter-spacing:.5px;text-transform:uppercase;}
.kpi-sub{font-size:.72rem;margin-top:5px;font-weight:600;}
.kpi-trend{font-size:.7rem;margin-top:4px;}

/* ── Progress ── */
.prog-track{background:rgba(255,255,255,.07);border-radius:20px;height:8px;overflow:hidden;margin:6px 0;}
.prog-fill{height:100%;border-radius:20px;transition:width .7s cubic-bezier(.4,0,.2,1);}

/* ── Task card ── */
.tc{background:var(--card);border:1px solid var(--b);border-radius:12px;
  padding:13px 15px;margin-bottom:7px;border-right:4px solid var(--cyan);transition:all .2s;}
.tc:hover{background:var(--card2);border-color:var(--bh);}
.tc.done{border-right-color:var(--green)!important;opacity:.7;}
.tc.late{border-right-color:var(--red)!important;}
.tc.urgent{border-right-color:var(--amber)!important;}

/* ── Badge ── */
.b{display:inline-block;padding:2px 9px;border-radius:20px;font-size:.7rem;font-weight:700;margin:1px;}
.b-blue  {background:rgba(56,139,253,.18);color:#7ab8ff;}
.b-green {background:rgba(0,229,160,.14);color:#00e5a0;}
.b-red   {background:rgba(255,77,109,.14);color:#ff6b82;}
.b-amber {background:rgba(245,158,11,.14);color:#fbbf24;}
.b-purple{background:rgba(167,139,250,.14);color:#c4b5fd;}
.b-pink  {background:rgba(244,114,182,.14);color:#f9a8d4;}

/* ── Week chip ── */
.wchip{
  background:linear-gradient(135deg,var(--card),#0b1e40);
  border:1px solid var(--bh);border-radius:12px;padding:10px 6px;
  margin-bottom:10px;text-align:center;font-family:"Orbitron",monospace;
  font-size:.75rem;font-weight:700;color:var(--cyan);box-shadow:var(--gb);
}

/* ── Alert ── */
.al{border-radius:12px;padding:14px 18px;margin-bottom:14px;font-size:.9rem;}
.al-r{background:rgba(255,77,109,.1);border:1px solid rgba(255,77,109,.4);}
.al-g{background:rgba(0,229,160,.08);border:1px solid rgba(0,229,160,.3);}
.al-a{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.3);}

/* ── Popover ── */
div[data-testid="stPopover"]>button{
  width:100%!important;min-height:58px;margin-bottom:6px!important;font-weight:700!important;
  border-radius:10px!important;border:1px solid var(--b)!important;
  background:var(--card)!important;color:var(--txt)!important;text-align:right!important;
}

/* ── Login buttons ── */
div[data-testid="stHorizontalBlock"] .stButton>button{
  min-height:210px!important;height:210px!important;width:100%!important;
  border-radius:var(--r)!important;font-size:1.45rem!important;font-weight:800!important;
  display:flex!important;align-items:center!important;justify-content:center!important;
  white-space:pre-wrap!important;
}
div[data-testid="stHorizontalBlock"]>div:nth-child(1) button{border-top:4px solid var(--blue)!important;}
div[data-testid="stHorizontalBlock"]>div:nth-child(2) button{border-top:4px solid var(--green)!important;}
div[data-testid="stHorizontalBlock"]>div:nth-child(3) button{border-top:4px solid var(--amber)!important;}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--panel);}
::-webkit-scrollbar-thumb{background:var(--bh);border-radius:3px;}

/* ── Divider ── */
hr{border-color:var(--b)!important;}

/* ── Expander ── */
details summary{color:var(--cyan)!important;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  DATA LAYER
# ═══════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def load_tasks():
    cols = ["ID","Task_Name","Description","Recurring","Date",
            "Done_Dates","Priority","Category","Assigned_To"]
    if os.path.exists(DB_FILE):
        try: return pd.read_csv(DB_FILE).fillna("")
        except: pass
    return pd.DataFrame(columns=cols)

@st.cache_data(ttl=30)
def load_inv():
    cols = ["Month","Target","Current","SKU_Target","SKU_Current","No_Discrepancy"]
    if os.path.exists(INV_FILE):
        try: return pd.read_csv(INV_FILE).fillna("")
        except: pass
    return pd.DataFrame(columns=cols)

@st.cache_data(ttl=10)
def load_audit():
    cols = ["Timestamp","User","Action","Details"]
    if os.path.exists(AUDIT_FILE):
        try: return pd.read_csv(AUDIT_FILE).fillna("")
        except: pass
    return pd.DataFrame(columns=cols)

@st.cache_data(ttl=60)
def load_workers():
    if os.path.exists(WORKERS_FILE):
        try:
            df = pd.read_csv(WORKERS_FILE).fillna("")
            return df
        except: pass
    df = pd.DataFrame([{"Name":w,"Active":True} for w in WORKERS_DEFAULT])
    df.to_csv(WORKERS_FILE, index=False)
    return df

def save_tasks(df):
    df.to_csv(DB_FILE, index=False)
    load_tasks.clear()

def save_inv(df):
    df.to_csv(INV_FILE, index=False)
    load_inv.clear()

def save_workers(df):
    df.to_csv(WORKERS_FILE, index=False)
    load_workers.clear()

def log_action(action, details=""):
    try:
        user = st.session_state.get("user_role","?")
        entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "User": user, "Action": action, "Details": details
        }])
        audit = load_audit()
        audit = pd.concat([audit, entry], ignore_index=True).tail(1000)
        audit.to_csv(AUDIT_FILE, index=False)
        load_audit.clear()
    except: pass

def get_workers_list():
    df = load_workers()
    return df[df["Active"].astype(str).str.lower() != "false"]["Name"].tolist()


# ═══════════════════════════════════════════════════════
#  TASK LOGIC
# ═══════════════════════════════════════════════════════
def is_scheduled(base, recurring, target):
    if target < base: return False
    diff = (target - base).days
    if recurring == "לא":       return diff == 0
    if recurring == "יומי":     return diff < 365
    if recurring == "שבועי":    return diff % 7 == 0
    if recurring == "דו-שבועי": return diff % 14 == 0
    if recurring == "חודשי":    return target.day == base.day
    return False

def tasks_for_date(df, dt, skip_weekend=True):
    d = dt.date() if isinstance(dt, datetime) else dt
    if skip_weekend and d.weekday() in [4,5]: return []
    dstr = d.strftime("%Y-%m-%d")
    out = []
    for idx, row in df.iterrows():
        try:
            base = pd.to_datetime(row["Date"]).date()
            if is_scheduled(base, row["Recurring"], d):
                done = [x for x in str(row["Done_Dates"]).split(",") if x]
                out.append({
                    "idx":idx,"id":row["ID"],"name":row["Task_Name"],
                    "desc":row.get("Description",""),"priority":row.get("Priority","רגיל"),
                    "category":row.get("Category","כללי"),"assigned":row.get("Assigned_To",""),
                    "is_done":dstr in done,"date":dstr
                })
        except: continue
    return out

def get_overdue(df, days=7):
    today = datetime.now().date()
    out = []
    for i in range(1, days+1):
        for t in tasks_for_date(df, today - timedelta(days=i)):
            if not t["is_done"]: out.append(t)
    return out

def mark_done(df, idx, dstr):
    existing = [x for x in str(df.at[idx,"Done_Dates"]).split(",") if x]
    if dstr not in existing: existing.append(dstr)
    df.at[idx,"Done_Dates"] = ",".join(existing)
    return df

def week_stats(df, days=7):
    today = datetime.now().date()
    rows = []
    for i in range(days-1, -1, -1):
        d = today - timedelta(days=i)
        ts = tasks_for_date(df, d)
        tot = len(ts); don = sum(1 for t in ts if t["is_done"])
        rows.append({"תאריך": d.strftime("%d/%m"), "בוצע":don, "מתוכנן":tot,
                     "אחוז": round(don/tot*100) if tot else 0})
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════
def pbar(pct, color=None):
    c = color or ("#00e5a0" if pct>=80 else "#f59e0b" if pct>=50 else "#ff4d6d")
    return f'<div class="prog-track"><div class="prog-fill" style="width:{min(pct,100)}%;background:{c};"></div></div>'

def badge(text, kind="blue"):
    return f'<span class="b b-{kind}">{text}</span>'

def pri_badge(p):
    m={"דחוף":"red","גבוה":"amber","רגיל":"blue","נמוך":"purple"}
    return badge(p, m.get(p,"blue"))

def kpi(val, label, sub="", color="var(--cyan)", trend=""):
    return f"""<div class="kpi-card">
  <div class="kpi-val" style="color:{color}">{val}</div>
  <div class="kpi-lbl">{label}</div>
  {"<div class='kpi-sub' style='color:"+color+";opacity:.75'>"+sub+"</div>" if sub else ""}
  {"<div class='kpi-trend' style='color:var(--txt2)'>"+trend+"</div>" if trend else ""}
</div>"""

def render_task_card(t, show_btn=True, extra_key=""):
    cls = "done" if t["is_done"] else ("late" if t["date"]<datetime.now().strftime("%Y-%m-%d") else
          ("urgent" if t["priority"]=="דחוף" else ""))
    icon = "✅" if t["is_done"] else ("⚠️" if t["priority"]=="דחוף" else "⏳")
    asgn = f' {badge(t["assigned"],"green")}' if t.get("assigned") else ""
    return f"""<div class="tc {cls}">
  {icon} <b style="font-size:1rem">{t['name']}</b>
  {pri_badge(t['priority'])} {badge(t['category'],'pink')}{asgn}
  {"<div style='color:var(--txt2);font-size:.8rem;margin-top:4px'>"+t['desc']+"</div>" if t.get('desc') else ""}
</div>"""


# ═══════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════
def check_timeout():
    lt = st.session_state.get("login_time")
    if lt and (datetime.now()-lt).total_seconds() > SESSION_MINS*60:
        st.session_state.user_role = None
        st.session_state.login_time = None
        st.rerun()

def login():
    st.markdown('<div class="banner"><h1>אחים כהן • WMS</h1><p class="sub">מערכת ניהול מחסן מתקדמת v3.0</p></div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        with st.popover("🔑\nמנהל WMS", use_container_width=True):
            st.markdown("#### כניסת מנהל מערכת")
            pwd = st.text_input("סיסמה", type="password", key="lpwd")
            if st.button("כניסה", use_container_width=True, key="lbtn"):
                if hashlib.sha256(pwd.encode()).hexdigest() == ADMIN_HASH:
                    st.session_state.user_role = "מנהל WMS"
                    st.session_state.login_time = datetime.now()
                    log_action("LOGIN")
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


# ═══════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════
def page_dashboard(df):
    # ── Overdue alert ──
    overdue = get_overdue(df)
    if overdue:
        st.markdown(f'<div class="al al-r">⚠️ <b style="color:var(--red)">{len(overdue)} משימות שלא בוצעו בשבוע האחרון</b></div>', unsafe_allow_html=True)
        with st.expander("📋 צפה בפיגורים וסגור אותם"):
            for t in overdue:
                c1,c2 = st.columns([5,1])
                c1.markdown(render_task_card(t, extra_key="ov"), unsafe_allow_html=True)
                if c2.button("✓", key=f"ov_{t['id']}_{t['date']}"):
                    df = mark_done(df, t["idx"], t["date"])
                    save_tasks(df); log_action("MARK_DONE_OVERDUE", t["name"]); st.rerun()

    # ── Date selector ──
    dc, _, _ = st.columns([1,2,1])
    sel = dc.date_input("📅 תאריך", datetime.now())
    sel_str = sel.strftime("%Y-%m-%d")
    today_tasks = tasks_for_date(df, sel)
    tot = len(today_tasks); don = sum(1 for t in today_tasks if t["is_done"])
    pct = round(don/tot*100) if tot else 0
    lbl = "היום" if sel == datetime.now().date() else sel.strftime("%d/%m/%y")

    # ── Big KPIs ──
    k1,k2,k3,k4 = st.columns(4)
    kpi_color = "#00e5a0" if pct>=80 else "#f59e0b" if pct>=50 else "#ff4d6d"
    k1.markdown(kpi(tot, f"משימות {lbl}", color="var(--cyan)"), unsafe_allow_html=True)
    k2.markdown(kpi(don, "בוצעו", color="var(--green)"), unsafe_allow_html=True)
    k3.markdown(kpi(tot-don, "נותרו", color=kpi_color), unsafe_allow_html=True)
    k4.markdown(kpi(f"{pct}%", "ביצוע", color=kpi_color), unsafe_allow_html=True)

    st.markdown(f'<div style="margin:4px 0 20px">{pbar(pct)}</div>', unsafe_allow_html=True)

    # ── Tasks list + Weekly chart side by side ──
    col_tasks, col_chart = st.columns([2,3])

    with col_tasks:
        st.markdown(f"#### 📋 משימות {lbl}")
        if today_tasks:
            for t in sorted(today_tasks, key=lambda x:(x["is_done"], x["priority"]!="דחוף")):
                c_t, c_b = st.columns([6,1])
                c_t.markdown(render_task_card(t), unsafe_allow_html=True)
                if not t["is_done"] and c_b.button("✓", key=f"d_{t['id']}_{sel_str}"):
                    df = mark_done(df, t["idx"], sel_str)
                    save_tasks(df); log_action("MARK_DONE", t["name"]); st.rerun()
        else:
            st.markdown('<div class="al al-g">✅ אין משימות לתאריך זה</div>', unsafe_allow_html=True)

    with col_chart:
        st.markdown("#### 📈 ביצועים שבועיים")
        wdf = week_stats(df, 14)
        if HAS_PLOTLY:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=wdf["תאריך"], y=wdf["מתוכנן"],
                name="מתוכנן", marker_color="rgba(56,139,253,.2)",
                marker_line_color="rgba(56,139,253,.4)", marker_line_width=1))
            fig.add_trace(go.Bar(x=wdf["תאריך"], y=wdf["בוצע"],
                name="בוצע", marker_color="rgba(0,229,160,.7)"))
            fig.add_trace(go.Scatter(x=wdf["תאריך"], y=wdf["אחוז"],
                name="אחוז%", yaxis="y2", mode="lines+markers",
                line=dict(color="#00d4ff",width=2.5),
                marker=dict(size=7,color="#00d4ff")))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e8f0fe", height=320, barmode="overlay",
                margin=dict(t=10,b=30,l=0,r=0),
                legend=dict(bgcolor="rgba(0,0,0,0)",orientation="h",y=1.12),
                yaxis=dict(gridcolor="rgba(255,255,255,.05)",title=""),
                yaxis2=dict(overlaying="y",side="left",range=[0,110],
                    gridcolor="rgba(0,212,255,.06)",title="",showgrid=False),
                xaxis=dict(gridcolor="rgba(255,255,255,.04)"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(wdf, use_container_width=True)

    # ── Monthly deep-dive ──
    st.markdown("---")
    st.markdown("### 📅 ניתוח חודשי מעמיק")
    mc,yc,_ = st.columns([1,1,2])
    sm = mc.selectbox("חודש",range(1,13), index=datetime.now().month-1,
                      format_func=lambda x:["ינואר","פברואר","מרץ","אפריל","מאי","יוני",
                                            "יולי","אוגוסט","ספטמבר","אוקטובר","נובמבר","דצמבר"][x-1])
    sy = yc.selectbox("שנה",[2025,2026],index=1)
    _,nd = cal_lib.monthrange(sy,sm)
    mon_rows=[]
    for day in range(1,nd+1):
        d = datetime(sy,sm,day).date()
        ts = tasks_for_date(df,d)
        if ts:
            dn = sum(1 for t in ts if t["is_done"])
            mon_rows.append({"יום":day,"בוצע":dn,"מתוכנן":len(ts),"אחוז":round(dn/len(ts)*100)})
    if mon_rows:
        mdf = pd.DataFrame(mon_rows)
        avg = round(mdf["אחוז"].mean())
        best = int(mdf.loc[mdf["אחוז"].idxmax(),"יום"])
        total_done = int(mdf["בוצע"].sum()); total_plan = int(mdf["מתוכנן"].sum())

        ma,mb,mc2,md = st.columns(4)
        ma.metric("ממוצע חודשי", f"{avg}%")
        mb.metric("יום שיא", f"{best} בחודש")
        mc2.metric("סה\"כ בוצע", total_done)
        md.metric("סה\"כ מתוכנן", total_plan)

        if HAS_PLOTLY:
            fig2 = go.Figure()
            colors = ["#00e5a0" if r>=80 else "#f59e0b" if r>=50 else "#ff4d6d" for r in mdf["אחוז"]]
            fig2.add_trace(go.Bar(x=mdf["יום"], y=mdf["אחוז"],
                marker_color=colors, name="אחוז ביצוע",
                text=[f"{v}%" for v in mdf["אחוז"]], textposition="outside",
                textfont=dict(size=10,color="#ffffff")))
            fig2.add_hline(y=80, line_dash="dot", line_color="rgba(0,229,160,.4)",
                annotation_text="יעד 80%", annotation_font_color="var(--green)")
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e8f0fe", height=300,
                margin=dict(t=30,b=30,l=0,r=0),
                yaxis=dict(range=[0,115],gridcolor="rgba(255,255,255,.05)"),
                xaxis=dict(gridcolor="rgba(255,255,255,.04)"), showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Category breakdown
        st.markdown("#### 🏷️ ביצוע לפי קטגוריה")
        cat_data={}
        for day in range(1,nd+1):
            for t in tasks_for_date(df, datetime(sy,sm,day).date()):
                cat = t["category"] or "כללי"
                if cat not in cat_data: cat_data[cat]={"done":0,"total":0}
                cat_data[cat]["total"]+=1
                if t["is_done"]: cat_data[cat]["done"]+=1
        if cat_data and HAS_PLOTLY:
            cdf = pd.DataFrame([{"קטגוריה":k,"בוצע":v["done"],"מתוכנן":v["total"],
                "אחוז":round(v["done"]/max(v["total"],1)*100)} for k,v in cat_data.items()])
            fig3 = px.bar(cdf, x="קטגוריה", y="אחוז", color="אחוז",
                color_continuous_scale=[[0,"#ff4d6d"],[0.5,"#f59e0b"],[1,"#00e5a0"]],
                text=[f"{v}%" for v in cdf["אחוז"]])
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e8f0fe",height=260,margin=dict(t=10,b=30,l=0,r=0),
                coloraxis_showscale=False,showlegend=False,
                yaxis=dict(range=[0,110],gridcolor="rgba(255,255,255,.05)"))
            fig3.update_traces(textposition="outside",textfont_color="#ffffff")
            st.plotly_chart(fig3, use_container_width=True)

        # Export
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            mdf.to_excel(w, index=False, sheet_name="ביצועים יומי")
            wdf.to_excel(w, index=False, sheet_name="ביצועים שבועי")
            if cat_data:
                pd.DataFrame([{"קטגוריה":k,"בוצע":v["done"],"מתוכנן":v["total"]}
                    for k,v in cat_data.items()]).to_excel(w,index=False,sheet_name="לפי קטגוריה")
        st.download_button("📥 ייצוא דוח Excel מלא",buf.getvalue(),
            f"דוח_{sm:02d}_{sy}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("אין נתוני משימות לחודש הנבחר")


# ═══════════════════════════════════════════════════════
#  PAGE: WORK ORDER
# ═══════════════════════════════════════════════════════
def page_work(df):
    today = datetime.now()
    # start of week (Sunday)
    start = today - timedelta(days=(today.weekday()+1)%7)
    days = ["ראשון","שני","שלישי","רביעי","חמישי"]
    cols = st.columns(5)
    for i,name in enumerate(days):
        curr = start + timedelta(days=i)
        ts = tasks_for_date(df, curr)
        don = sum(1 for t in ts if t["is_done"])
        pct = round(don/len(ts)*100) if ts else 0
        is_today = curr.date()==today.date()
        with cols[i]:
            bc = "var(--cyan)" if is_today else "var(--bh)"
            st.markdown(f"""<div class="wchip" style="border-color:{bc}">
              {name}<br>
              <span style="font-family:Heebo;font-size:.7rem">{curr.strftime('%d/%m')}</span><br>
              <span style="font-size:.65rem;color:var(--green)">{don}/{len(ts)}</span>
            </div>""", unsafe_allow_html=True)
            st.markdown(pbar(pct), unsafe_allow_html=True)
            for t in ts:
                ico = "✅" if t["is_done"] else "⏳"
                with st.popover(f"{ico} {t['name']}", use_container_width=True):
                    st.markdown(f"**עדיפות:** {t['priority']}")
                    st.markdown(f"**קטגוריה:** {t['category']}")
                    if t["assigned"]: st.markdown(f"**שויך ל:** {t['assigned']}")
                    if t["desc"]:    st.markdown(f"**פירוט:** {t['desc']}")
                    if not t["is_done"]:
                        if st.button("✅ סמן כבוצע", key=f"w_{t['id']}_{i}_{curr.date()}"):
                            df = mark_done(df, t["idx"], curr.strftime("%Y-%m-%d"))
                            save_tasks(df)
                            log_action("MARK_DONE", f"{t['name']} ({curr.strftime('%d/%m')})")
                            st.rerun()


# ═══════════════════════════════════════════════════════
#  PAGE: INVENTORY
# ═══════════════════════════════════════════════════════
def page_inventory():
    inv_df = load_inv()
    base_months = [datetime.now().strftime("%Y-%m"),
                   (datetime.now()-timedelta(days=30)).strftime("%Y-%m"),
                   (datetime.now()-timedelta(days=60)).strftime("%Y-%m")]
    all_months = sorted(list(set(base_months+inv_df["Month"].tolist())),reverse=True)

    sc,_ = st.columns([2,3])
    sel_month = sc.selectbox("📅 בחר חודש",all_months)

    row = inv_df[inv_df["Month"]==sel_month]
    data = row.iloc[0].to_dict() if not row.empty else {
        "Month":sel_month,"Target":0,"Current":0,
        "SKU_Target":0,"SKU_Current":0,"No_Discrepancy":0
    }

    if st.session_state.user_role == "מנהל WMS":
        with st.expander("🛠️ עדכון נתוני ספירה", expanded=row.empty):
            with st.form("inv_form"):
                a,b = st.columns(2)
                nt  = a.number_input('סה"כ מק"טים',  min_value=0, value=int(data.get("Target",0)))
                nc  = b.number_input("מק\"טים שנספרו",min_value=0, value=int(data.get("Current",0)))
                c,d = st.columns(2)
                nst = c.number_input("איתורים (יעד)", min_value=0, value=int(data.get("SKU_Target",0)))
                nsc = d.number_input("איתורים שנספרו",min_value=0, value=int(data.get("SKU_Current",0)))
                nnd = st.number_input("ללא פער",       min_value=0, value=int(data.get("No_Discrepancy",0)))
                if st.form_submit_button("💾 שמור", use_container_width=True):
                    nr = {"Month":sel_month,"Target":nt,"Current":nc,
                          "SKU_Target":nst,"SKU_Current":nsc,"No_Discrepancy":nnd}
                    if sel_month in inv_df["Month"].values:
                        for k,v in nr.items():
                            inv_df.loc[inv_df["Month"]==sel_month,k]=v
                    else:
                        inv_df = pd.concat([inv_df,pd.DataFrame([nr])],ignore_index=True)
                    save_inv(inv_df)
                    log_action("INV_UPDATE", sel_month)
                    st.rerun()

    st.markdown("---")
    tv  = max(int(data.get("Target",1)),1)
    cv  = int(data.get("Current",0))
    stv = max(int(data.get("SKU_Target",1)),1)
    scv = int(data.get("SKU_Current",0))
    ndv = int(data.get("No_Discrepancy",0))
    psku = round(scv/stv*100) if stv else 0
    ploc = round(cv/tv*100)   if tv  else 0
    pacc = round(ndv/cv*100)  if cv  else 0

    # Big KPI row
    k1,k2,k3 = st.columns(3)
    c_sku = "#388bfd" if psku>=80 else "#f59e0b" if psku>=50 else "#ff4d6d"
    c_loc = "#00d4ff" if ploc>=80 else "#f59e0b" if ploc>=50 else "#ff4d6d"
    c_acc = "#a78bfa" if pacc>=95 else "#f59e0b" if pacc>=80 else "#ff4d6d"
    k1.markdown(kpi(f"{psku}%","מספר ספירות",f"{scv:,} / {stv:,} איתורים",c_sku),unsafe_allow_html=True)
    k1.markdown(pbar(psku,c_sku),unsafe_allow_html=True)
    k2.markdown(kpi(f"{ploc}%","מספר מק\"טים",f"{cv:,} / {tv:,} מק\"טים",c_loc),unsafe_allow_html=True)
    k2.markdown(pbar(ploc,c_loc),unsafe_allow_html=True)
    k3.markdown(kpi(f"{pacc}%","רמת דיוק",f"{ndv:,} איתורים ללא פער",c_acc),unsafe_allow_html=True)
    k3.markdown(pbar(pacc,c_acc),unsafe_allow_html=True)

    # Gauge charts
    if HAS_PLOTLY:
        st.markdown("---")
        p1,p2,p3 = st.columns(3)
        for col_w,(val,mx,title,clr) in zip([p1,p2,p3],[
            (scv,stv,"ספירות",c_sku),(cv,tv,"מק\"טים",c_loc),(ndv,max(cv,1),"דיוק",c_acc)
        ]):
            remain = max(0,mx-val)
            fig = go.Figure(go.Pie(
                values=[val,remain],hole=.72,
                marker_colors=[clr,"rgba(255,255,255,.06)"],
                showlegend=False,textinfo="none",
                hoverinfo="skip",
            ))
            pct_v = round(val/max(mx,1)*100)
            fig.add_annotation(text=f"<b>{pct_v}%</b>",x=.5,y=.5,
                font_size=30,font_family="Orbitron",font_color=clr,showarrow=False)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",height=200,
                margin=dict(t=10,b=0,l=0,r=0),title=dict(text=title,font_color="#e8f0fe",font_size=13))
            col_w.plotly_chart(fig,use_container_width=True)

    # Trend chart
    if len(inv_df)>1 and HAS_PLOTLY:
        st.markdown("---")
        st.markdown("### 📈 מגמת ספירות — 6 חודשים אחרונים")
        hist = inv_df.sort_values("Month").tail(6).copy()
        hist["מק\"טים %"] = (hist["Current"].astype(float)/
                             hist["Target"].replace(0,1).astype(float)*100).round(1)
        hist["דיוק %"] = (hist["No_Discrepancy"].astype(float)/
                          hist["Current"].replace(0,1).astype(float)*100).round(1)
        fig_h = go.Figure()
        fig_h.add_trace(go.Scatter(x=hist["Month"],y=hist["מק\"טים %"],
            mode="lines+markers",name="מק\"טים",
            line=dict(color="#00d4ff",width=2.5),marker=dict(size=8)))
        fig_h.add_trace(go.Scatter(x=hist["Month"],y=hist["דיוק %"],
            mode="lines+markers",name="דיוק",
            line=dict(color="#a78bfa",width=2.5),marker=dict(size=8)))
        fig_h.add_hline(y=95,line_dash="dot",line_color="rgba(167,139,250,.4)",
            annotation_text="יעד דיוק 95%",annotation_font_color="#a78bfa")
        fig_h.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8f0fe",height=280,margin=dict(t=10,b=30,l=0,r=0),
            yaxis=dict(range=[0,110],gridcolor="rgba(255,255,255,.05)"),
            xaxis=dict(gridcolor="rgba(255,255,255,.04)"),
            legend=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_h,use_container_width=True)


# ═══════════════════════════════════════════════════════
#  PAGE: CALENDAR
# ═══════════════════════════════════════════════════════
def page_calendar(df):
    events=[]
    today=datetime.now().date()
    for _,row in df.iterrows():
        base=pd.to_datetime(row["Date"]).date()
        for i in range(180):
            d=base+timedelta(days=i)
            if is_scheduled(base,row["Recurring"],d):
                done=d.strftime("%Y-%m-%d") in str(row["Done_Dates"])
                events.append({
                    "title":row["Task_Name"],
                    "start":d.strftime("%Y-%m-%d"),
                    "color":"#00e5a0" if done else ("#ff4d6d" if d<today else "#388bfd"),
                    "allDay":True
                })
    if HAS_CALENDAR:
        st_calendar(events=events,
            options={"direction":"rtl","locale":"he","initialView":"dayGridMonth","height":640},
            custom_css="""
              .fc{background:#0c1e3a;color:#e8f0fe;border-radius:16px;padding:10px;}
              .fc-toolbar-title{font-family:Orbitron,monospace;color:#00d4ff;}
              .fc-button{background:#388bfd!important;border:none!important;}
              .fc-day-today{background:rgba(56,139,253,.15)!important;}
            """)
    else:
        st.info("💡 התקן `streamlit-calendar` לתצוגת לוח שנה אינטראקטיבי")
        upcoming = sorted([e for e in events if e["start"]>=today.strftime("%Y-%m-%d")],
                          key=lambda x:x["start"])[:30]
        if upcoming:
            edf = pd.DataFrame(upcoming)[["start","title"]]
            edf.columns = ["תאריך","משימה"]
            st.dataframe(edf, use_container_width=True)


# ═══════════════════════════════════════════════════════
#  PAGE: ADD TASK
# ═══════════════════════════════════════════════════════
def page_add(df):
    workers = get_workers_list()
    with st.form("add_form", clear_on_submit=True):
        st.markdown("#### ➕ הוספת משימה חדשה")
        a,b = st.columns(2)
        name = a.text_input("שם המשימה *")
        freq = b.selectbox("תדירות חזרה", RECURRENCES)
        desc = st.text_area("פירוט / הוראות ביצוע")
        c,d,e = st.columns(3)
        pri  = c.selectbox("עדיפות", PRIORITIES)
        cat  = d.selectbox("קטגוריה", CATEGORIES)
        asgn = e.selectbox("שייך לעובד", ["—"]+workers)
        sdate = st.date_input("תאריך התחלה", datetime.now())
        if st.form_submit_button("💾 שמור משימה", use_container_width=True):
            if not name.strip():
                st.error("⚠️ שם משימה הוא שדה חובה")
            else:
                new = pd.DataFrame([{
                    "ID": int(datetime.now().timestamp()*1000),
                    "Task_Name": name.strip(), "Description": desc,
                    "Recurring": freq, "Date": sdate.strftime("%Y-%m-%d"),
                    "Done_Dates": "", "Priority": pri, "Category": cat,
                    "Assigned_To": "" if asgn=="—" else asgn
                }])
                save_tasks(pd.concat([df,new],ignore_index=True))
                log_action("ADD_TASK", name)
                st.success(f"✅ משימה '{name}' נשמרה בהצלחה!")
                st.rerun()


# ═══════════════════════════════════════════════════════
#  PAGE: MANAGE TASKS
# ═══════════════════════════════════════════════════════
def page_manage(df):
    workers = get_workers_list()
    # Filters
    fa,fb,fc = st.columns(3)
    fsearch = fa.text_input("🔍 חיפוש",placeholder="שם משימה...")
    fpri    = fb.selectbox("עדיפות",["הכל"]+PRIORITIES)
    fcat    = fc.selectbox("קטגוריה",["הכל"]+CATEGORIES)
    filtered = df.copy()
    if fsearch: filtered = filtered[filtered["Task_Name"].str.contains(fsearch,na=False,case=False)]
    if fpri!="הכל": filtered = filtered[filtered["Priority"]==fpri]
    if fcat!="הכל": filtered = filtered[filtered["Category"]==fcat]
    st.markdown(f'<div style="color:var(--txt2);font-size:.82rem;margin-bottom:10px">נמצאו {len(filtered)} משימות</div>',unsafe_allow_html=True)

    for idx,row in filtered.iterrows():
        ci,ce,cd = st.columns([5,1,1])
        asgn_b = badge(str(row.get("Assigned_To","")), "green") if row.get("Assigned_To") else ""
        ci.markdown(f"""<div class="tc">
          <b style="font-size:1rem">{row['Task_Name']}</b>
          {pri_badge(row.get('Priority','רגיל'))}
          {badge(row.get('Category',''),'pink')}
          {badge(row.get('Recurring',''),'blue')}
          {asgn_b}
          {"<div style='color:var(--txt2);font-size:.8rem;margin-top:4px'>"+str(row.get('Description',''))+"</div>" if row.get('Description') else ""}
        </div>""",unsafe_allow_html=True)

        with ce:
            with st.popover("✏️",use_container_width=True):
                nn = st.text_input("שם",value=row["Task_Name"],key=f"en{row['ID']}")
                nd = st.text_area("תיאור",value=row.get("Description",""),key=f"ed{row['ID']}")
                np = st.selectbox("עדיפות",PRIORITIES,
                    index=PRIORITIES.index(row.get("Priority","רגיל")) if row.get("Priority") in PRIORITIES else 0,
                    key=f"ep{row['ID']}")
                nc = st.selectbox("קטגוריה",CATEGORIES,key=f"ec{row['ID']}")
                na = st.selectbox("שייך ל",["—"]+workers,key=f"ea{row['ID']}")
                if st.button("💾 שמור",key=f"sv{row['ID']}"):
                    df.at[idx,"Task_Name"]=nn; df.at[idx,"Description"]=nd
                    df.at[idx,"Priority"]=np; df.at[idx,"Category"]=nc
                    df.at[idx,"Assigned_To"]="" if na=="—" else na
                    save_tasks(df); log_action("EDIT_TASK",nn); st.rerun()

        with cd:
            ck = f"cfm_{row['ID']}"
            if not st.session_state.get(ck):
                if st.button("🗑️",key=f"dl{row['ID']}",help="מחק"):
                    st.session_state[ck]=True; st.rerun()
            else:
                st.warning("בטוח?")
                if st.button("כן",key=f"cy{row['ID']}"):
                    save_tasks(df.drop(idx))
                    log_action("DELETE_TASK",str(row["Task_Name"]))
                    st.session_state.pop(ck,None); st.rerun()
                if st.button("לא",key=f"cn{row['ID']}"):
                    st.session_state.pop(ck,None); st.rerun()


# ═══════════════════════════════════════════════════════
#  PAGE: WORKERS
# ═══════════════════════════════════════════════════════
def page_workers(df):
    wdf = load_workers()
    st.markdown("### 👥 ניהול עובדים")
    ca,cb = st.columns([2,3])
    with ca:
        with st.form("add_w"):
            wn = st.text_input("שם עובד חדש")
            if st.form_submit_button("➕ הוסף עובד"):
                if wn and wn not in wdf["Name"].values:
                    wdf = pd.concat([wdf,pd.DataFrame([{"Name":wn,"Active":True}])],ignore_index=True)
                    save_workers(wdf); log_action("ADD_WORKER",wn); st.rerun()
    with cb:
        for _,wr in wdf.iterrows():
            active = str(wr["Active"]).lower() != "false"
            w1,w2 = st.columns([3,1])
            w1.markdown(f"{'🟢' if active else '🔴'} {wr['Name']}")
            if w2.button("הפעל/כבה",key=f"wt_{wr['Name']}"):
                wdf.loc[wdf["Name"]==wr["Name"],"Active"]=not active
                save_workers(wdf); st.rerun()

    # Performance by worker (last 30 days)
    st.markdown("---")
    st.markdown("### 📊 ביצועים לפי עובד — 30 ימים אחרונים")
    perf=[]
    today=datetime.now().date()
    for w in get_workers_list():
        wdf_tasks = df[df["Assigned_To"]==w]
        tot=0; don=0
        for i in range(30):
            d=today-timedelta(days=i)
            ts=tasks_for_date(wdf_tasks,d)
            tot+=len(ts); don+=sum(1 for t in ts if t["is_done"])
        pct=round(don/tot*100) if tot else 0
        perf.append({"עובד":w,"ביצוע":pct,"בוצע":don,"סה\"כ":tot})
    if perf and HAS_PLOTLY:
        pef_df=pd.DataFrame(perf).sort_values("ביצוע",ascending=True)
        colors=["#00e5a0" if v>=80 else "#f59e0b" if v>=50 else "#ff4d6d" for v in pef_df["ביצוע"]]
        fig=go.Figure(go.Bar(x=pef_df["ביצוע"],y=pef_df["עובד"],orientation="h",
            marker_color=colors,text=[f"{v}%" for v in pef_df["ביצוע"]],textposition="outside",
            textfont=dict(color="#ffffff")))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8f0fe",height=300,margin=dict(t=10,b=10,l=80,r=60),
            xaxis=dict(range=[0,115],gridcolor="rgba(255,255,255,.05)"),showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    elif perf:
        st.dataframe(pd.DataFrame(perf),use_container_width=True)


# ═══════════════════════════════════════════════════════
#  PAGE: AUDIT LOG
# ═══════════════════════════════════════════════════════
def page_audit():
    audit=load_audit()
    st.markdown("### 🔍 יומן פעולות מלא")
    if audit.empty:
        st.info("אין עדיין רשומות ביומן")
        return
    c1,c2,c3 = st.columns(3)
    fa = c1.selectbox("פעולה",["הכל"]+sorted(audit["Action"].unique().tolist()))
    fu = c2.selectbox("משתמש",["הכל"]+sorted(audit["User"].unique().tolist()))
    fl = c3.number_input("הצג אחרונות",min_value=10,max_value=500,value=100,step=10)
    filt=audit.copy()
    if fa!="הכל": filt=filt[filt["Action"]==fa]
    if fu!="הכל": filt=filt[filt["User"]==fu]
    filt=filt.sort_values("Timestamp",ascending=False).head(int(fl))
    st.dataframe(filt,use_container_width=True,height=400)
    buf=io.BytesIO(); filt.to_excel(buf,index=False)
    st.download_button("📥 ייצוא יומן",buf.getvalue(),"audit.xlsx")


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════
for k,v in [("user_role",None),("login_time",None)]:
    if k not in st.session_state: st.session_state[k]=v

check_timeout()

if not st.session_state.user_role:
    login(); st.stop()

df = load_tasks()
role = st.session_state.user_role
lt   = st.session_state.login_time
elapsed_min = int((datetime.now()-lt).total_seconds()/60) if lt else 0

# ── Sidebar ──
ICONS = {"מנהל WMS":"🔑","צוות מחסן":"📦","הנהלה":"📊"}
st.sidebar.markdown(f"""
<div style="padding:16px 0 8px;text-align:center">
  <div style="font-size:2rem">{ICONS.get(role,'👤')}</div>
  <div style="font-weight:700;font-size:1.05rem;color:var(--txt)">{role}</div>
  <div style="font-size:.75rem;color:var(--txt2);margin-top:2px">מחובר {elapsed_min} דק'</div>
</div>
""",unsafe_allow_html=True)

MENUS = {
    "מנהל WMS":  ["📊 דשבורד","📋 סידור עבודה","📦 ספירות מלאי","📅 לוח שנה",
                  "➕ הוספת משימה","⚙️ ניהול משימות","👥 עובדים","🔍 יומן פעולות"],
    "הנהלה":     ["📊 דשבורד","📦 ספירות מלאי","📅 לוח שנה","🔍 יומן פעולות"],
    "צוות מחסן": ["📊 דשבורד","📋 סידור עבודה","📦 ספירות מלאי","📅 לוח שנה"],
}
choice = st.sidebar.radio("",MENUS[role],label_visibility="collapsed")
st.sidebar.markdown("---")
if elapsed_min >= 50:
    st.sidebar.warning(f"⚠️ הסשן יפוג בעוד {60-elapsed_min} דק'")
if st.sidebar.button("🚪 התנתקות",use_container_width=True):
    log_action("LOGOUT"); st.session_state.update(user_role=None,login_time=None); st.rerun()

# ── Header ──
st.markdown(f'<div class="banner"><h1>{choice}</h1></div>',unsafe_allow_html=True)

# ── Route ──
if   choice=="📊 דשבורד":          page_dashboard(df)
elif choice=="📋 סידור עבודה":     page_work(df)
elif choice=="📦 ספירות מלאי":     page_inventory()
elif choice=="📅 לוח שנה":         page_calendar(df)
elif choice=="➕ הוספת משימה":     page_add(df)
elif choice=="⚙️ ניהול משימות":    page_manage(df)
elif choice=="👥 עובדים":           page_workers(df)
elif choice=="🔍 יומן פעולות":     page_audit()
