import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="מערכת ניהול מחסן", layout="wide")

st.title("ניהול וסנכרון משימות מחסן")

# חיבור לגוגל שיטס
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="0")

try:
    df = load_data()
except Exception as e:
    st.error(f"שגיאה בחיבור לנתונים: {e}")
    st.info("וודא שה-Secrets מוגדרים נכון וששיתפת את הגיליון עם המייל של השירות.")
    st.stop()

menu = ["הוספת משימה", "משימות לביצוע (מחסן)", "אישור סופי (מנהל)", "דוח סיכום לסמנכ\"ל"]
choice = st.sidebar.selectbox("תפריט ניהול", menu)

if choice == "הוספת משימה":
    st.header("הוספת משימה חדשה")
    with st.form("add_task"):
        desc = st.text_area("תיאור המשימה")
        submitted = st.form_submit_button("שלח למחסן")
        if submitted and desc:
            new_id = len(df) + 1 if not df.empty else 1
            new_row = pd.DataFrame([{
                "ID": new_id,
                "Description": desc,
                "Warehouse_Done": "לא",
                "Final_Approval": "לא",
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("המשימה נוספה בהצלחה!")
            st.rerun()

elif choice == "משימות לביצוע (מחסן)":
    st.header("משימות להכנה במחסן")
    pending = df[df["Warehouse_Done"] == "לא"]
    if pending.empty:
        st.info("אין משימות ממתינות במחסן.")
    else:
        for i, row in pending.iterrows():
            with st.expander(f"משימה #{row['ID']} - {row['Date']}"):
                st.write(row["Description"])
                if st.button(f"סימנתי כבוצע #{row['ID']}"):
                    df.at[i, "Warehouse_Done"] = "כן"
                    conn.update(data=df)
                    st.success("עודכן!")
                    st.rerun()

elif choice == "אישור סופי (מנהל)":
    st.header("אישור משימות שבוצעו")
    to_approve = df[(df["Warehouse_Done"] == "כן") & (df["Final_Approval"] == "לא")]
    if to_approve.empty:
        st.info("אין משימות הממתינות לאישור סופי.")
    else:
        for i, row in to_approve.iterrows():
            with st.container():
                st.write(f"**משימה {row['ID']}:** {row['Description']}")
                if st.button(f"אשר וסגור משימה #{row['ID']}"):
                    df.at[i, "Final_Approval"] = "כן"
                    conn.update(data=df)
                    st.success("המשימה אושרה ונסגרה!")
                    st.rerun()

elif choice == "דוח סיכום לסמנכ\"ל":
    st.header("ריכוז משימות שבוצעו ואושרו")
    final_df = df[df["Final_Approval"] == "כן"]
    st.dataframe(final_df, use_container_width=True)
    st.download_button("הורד דוח אקסל", final_df.to_csv(index=False).encode('utf-8-sig'), "report.csv", "text/csv")
