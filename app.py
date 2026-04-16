elif choice == opt2:
    st.header(opt2)
    
    with st.form("new_task_form_with_days"):
        # 1. שם משימה
        new_name = st.text_input("שם המשימה")
        
        # 2. תיאור
        new_desc = st.text_area("תיאור המשימה")
        
        # 3. משימה חוזרת
        new_recur = st.selectbox("משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
        
        # חלון בחירת יום - מופיע רק אם המשימה חוזרת
        selected_day = "N/A"
        if new_recur != "לא":
            days_list = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
            selected_day = st.selectbox("באיזה יום בשבוע?", days_list)
        
        # 4. תאריך לביצוע (תאריך התחלה)
        new_date = st.date_input("תאריך לביצוע / התחלה", datetime.now())
        
        if st.form_submit_button("שמור"):
            if new_name:
                try:
                    next_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                    
                    # יצירת השורה החדשה כולל העמודה של היום בשבוע
                    new_row = pd.DataFrame([{
                        "ID": next_id,
                        "Task_Name": new_name,
                        "Description": new_desc,
                        "Recurring": new_recur,
                        "Day_of_Week": selected_day, # העמודה החדשה
                        "Date": new_date.strftime("%Y-%m-%d"),
                        "Warehouse_Done": "לא",
                        "Final_Approval": "לא",
                        "User": user_role
                    }])
                    
                    conn.update(data=pd.concat([df, new_row], ignore_index=True))
                    st.success(f"המשימה '{new_name}' נשמרה לימי {selected_day}")
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה בשמירה: {e}")
            else:
                st.error("נא להזין שם משימה")
