elif choice == opt2:
    st.header(opt2)
    
    with st.form("new_task_form_v3"):
        # 1. שם המשימה (שדה ראשון)
        new_name = st.text_input("שם המשימה")
        
        # 2. תיאור המשימה (שדה שני)
        new_desc = st.text_area("תיאור המשימה")
        
        # 3. משימה חוזרת (שדה שלישי)
        new_recur = st.selectbox("האם זו משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
        
        # חלון בחירת יום - מופיע רק אם המשימה חוזרת
        selected_day = "N/A"
        if new_recur != "לא":
            # הגבלה לימים ראשון עד חמישי בלבד
            days_list = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
            selected_day = st.selectbox("באיזה יום בשבוע המשימה תתבצע?", days_list)
        
        # תאריך התחלה
        new_date = st.date_input("תאריך לביצוע / התחלה", datetime.now())
        
        submit_btn = st.form_submit_button("שמור משימה במערכת")
        
        if submit_btn:
            if new_name:
                try:
                    # חישוב ID חדש בצורה בטוחה למניעת KeyError
                    next_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                    
                    # יצירת השורה החדשה כולל העמודה של היום בשבוע
                    new_row = pd.DataFrame([{
                        "ID": next_id,
                        "Task_Name": new_name,
                        "Description": new_desc,
                        "Recurring": new_recur,
                        "Day_of_Week": selected_day,
                        "Date": new_date.strftime("%Y-%m-%d"),
                        "Warehouse_Done": "לא",
                        "Final_Approval": "לא",
                        "User": user_role
                    }])
                    
                    # עדכון הגיליון
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    
                    st.success(f"המשימה '{new_name}' נשמרה בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה בשמירת הנתונים: {e}")
            else:
                st.warning("חובה להזין שם למשימה.")
