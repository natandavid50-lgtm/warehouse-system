elif choice == opt2:
    st.header(opt2)
    
    with st.form("add_new_task_form"):
        # 1. שם המשימה (שדה ראשון)
        task_name = st.text_input("שם המשימה", placeholder="לדוגמה: סידור מלאי")
        
        # 2. תיאור המשימה (שדה שני)
        task_desc = st.text_area("תיאור המשימה", placeholder="פרט כאן את שלבי המשימה...")
        
        # 3. משימה חוזרת (שדה שלישי)
        is_recurring = st.selectbox("האם זו משימה חוזרת?", ["לא", "יומי", "שבועי", "חודשי"])
        
        # שדות נוספים שנחוצים למערכת
        task_date = st.date_input("תאריך לביצוע", datetime.now())
        
        submit_button = st.form_submit_button("שמור משימה")
        
        if submit_button:
            if task_name: # בדיקה ששם המשימה לא ריק
                try:
                    # חישוב ID חדש בצורה בטוחה
                    new_id = int(df["ID"].max() + 1) if not df.empty and pd.notnull(df["ID"].max()) else 1
                    
                    # יצירת השורה החדשה (שימוש בשמות משתנים ברורים למניעת שגיאות מחרוזת)
                    new_row = pd.DataFrame([{
                        "ID": new_id,
                        "Task_Name": task_name,
                        "Description": task_desc,
                        "Recurring": is_recurring,
                        "Date": task_date.strftime("%Y-%m-%d"),
                        "Warehouse_Done": "לא",
                        "Final_Approval": "לא",
                        "User": user_role
                    }])
                    
                    # עדכון בסיס הנתונים
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    
                    st.success(f"המשימה '{task_name}' נוספה בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה בשמירת הנתונים: {e}")
            else:
                st.warning("נא להזין שם למשימה.")
