import mysql.connector, mysql, traceback
from datetime import datetime
from config_setter import is_home

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass

def get_my_db():
    if is_home == 0:
        db = mysql.connector.connect(host="localhost", user="root", passwd="dbpassword", db="flask_companyname", connect_timeout=30)
    else:
        db = mysql.connector.connect(host="localhost", user="root", passwd="", db="flask_companyname", connect_timeout=30)
    return db

# region WAREHOUSE

def Handle_Notification_Checked(data):
    return data

def Handle_Log_Save(data):
    timestamp="NOW()"

# endregion

#region HR

# region ADVANCE PAYMENTS

def Add_Advance_Payment(data):
    db = get_my_db()
    employee_name =                     data['employee_name']
    employee_surname =                  data['employee_surname']
    payment_amount =                    data['advance_amount']
    payment_date =                      data['advance_date']
    dt_obj = datetime.strptime(payment_date, '%d.%m.%Y')
    mysql_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    sql = '''INSERT INTO hr_payments_advance (id, employee_name, employee_surname, payment_amount, payment_date) 
        VALUES (%s, %s, %s, %s, %s)'''
    try:
        cursor.execute(sql, (None, employee_name, employee_surname, payment_amount, mysql_timestamp))
        db.commit()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Get_Advance_Payments(data):
    try:
        year = data["year"]
        month = data["month"]
        db = get_my_db()
        cursor = db.cursor()
        query = f"SELECT * FROM hr_payments_advance WHERE MONTH(payment_date) = '{month}' AND YEAR(payment_date) = '{year}'"
        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close()

        total_rows = []
        if len(foundRecords) > 0:
            for row in foundRecords:
                payment_id =                        row[0]
                employee_name =                     row[1]
                employee_surname =                  row[2]
                payment_amount =                    row[3]
                payment_date =                      row[4]
                date_app_string = payment_date.strftime('%d.%m.%Y')

                row_data = {
                    "id" :                  payment_id,
                    "name" :                employee_name,
                    "surname" :             employee_surname,
                    "payment_amount" :      f"{payment_amount} TRY",
                    "payment_date" :        payment_date,
                    "date_app_string" :     date_app_string,
                }
                total_rows.append(row_data)

            response_data = {"status" : "ok", "result_list" : total_rows}
        else:
            response_data = {"status" : "not_found"}

    except Exception as error:
        LogError(error)
        cursor.close()
        print(f"Error While Getting Employees: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Get_Specific_Advance_Payment(data):
    try:
        db = get_my_db()
        employee_name =                     data['employee_name']
        employee_surname =                  data['employee_surname']
        payment_amount =                    data['payment_amount']
        payment_date =                      data['payment_date']
        dt_obj = datetime.strptime(payment_date, '%d.%m.%Y')
        mysql_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

        cursor = db.cursor()
        query = f'''SELECT * FROM hr_payments_advance WHERE 
        employee_name="%s" AND 
        employee_surname="%s" AND 
        payment_amount="%s" AND 
        payment_date="%s" ''' % (employee_name, employee_surname, payment_amount, mysql_timestamp)
        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close()

        total_rows = []
        if len(foundRecords) > 0:
            for row in foundRecords:
                payment_id =                        row[0]
                employee_name =                     row[1]
                employee_surname =                  row[2]
                payment_amount =                    row[3]
                payment_date =                      row[4]
                date_app_string = payment_date.strftime('%d.%m.%Y')

                row_data = {
                    "id" :                  payment_id,
                    "name" :                employee_name,
                    "surname" :             employee_surname,
                    "payment_amount" :      payment_amount,
                    "payment_date" :        payment_date,
                    "date_app_string" :     date_app_string,
                }
                total_rows.append(row_data)

            response_data = {"status" : "ok", "result_rows" : total_rows}
        else:
            response_data = {"status" : "not_found"}

    except Exception as error:
        LogError(error)
        cursor.close()
        print(f"Error While Getting Employees: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Edit_Advance_Payment(data):
    db = get_my_db()
    employee_name =                         data['employee_name']
    employee_surname =                      data['employee_surname']
    payment_amount_old =                    data['payment_amount_old']
    payment_date_old =                      data['payment_date_old']
    payment_amount_new =                    data['payment_amount_new']
    payment_date_new =                      data['payment_date_new']

    dt_obj = datetime.strptime(payment_date_old, '%d.%m.%Y')
    timestamp_old = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    dt_obj = datetime.strptime(payment_date_new, '%d.%m.%Y')
    timestamp_new = dt_obj.strftime('%Y-%m-%d %H:%M:%S')


    cursor = db.cursor()
    query = f'''SELECT * FROM hr_payments_advance WHERE 
    employee_name="%s" AND 
    employee_surname="%s" AND 
    payment_amount="%s" AND 
    payment_date="%s" ''' % (employee_name, employee_surname, payment_amount_old, timestamp_old)

    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        response_data = {"status" : "not_found"}
        return response_data
    
    cursor = db.cursor()
    sql = '''UPDATE hr_payments_advance SET employee_name = %s, employee_surname = %s, payment_amount = %s, payment_date = %s'''
    try:
        cursor.execute(sql, (employee_name, employee_surname, payment_amount_new, timestamp_new))
        db.commit()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Updating Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Remove_Advance_Payment(data):
    db = get_my_db()
    employee_name =                     data['employee_name']
    employee_surname =                  data['employee_surname']
    payment_amount =                    data['payment_amount']
    payment_date =                      data['payment_date']
    dt_obj = datetime.strptime(payment_date, '%d.%m.%Y')
    mysql_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_payments_advance WHERE 
    employee_name="%s" AND 
    employee_surname="%s" AND 
    payment_amount="%s" AND 
    payment_date="%s" ''' % (employee_name, employee_surname, payment_amount, mysql_timestamp)

    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM hr_payments_advance WHERE 
        employee_name="%s" AND 
        employee_surname="%s" AND 
        payment_amount="%s" AND 
        payment_date="%s" ''' % (employee_name, employee_surname, payment_amount, mysql_timestamp)
    try:
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        print(error)
        cursor.close()
        db.rollback()
        print(f"Error While Removing Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    return response_data

# endregion

# region EXTRA PAYMENTS


def Add_Extra_Payment(data):
    db = get_my_db()
    employee_name =                     data['employee_name']
    employee_surname =                  data['employee_surname']
    payment_amount =                    data['payment_amount']
    payment_date =                      data['payment_date']
    dt_obj = datetime.strptime(payment_date, '%d.%m.%Y')
    mysql_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    sql = '''INSERT INTO hr_payments_extra (id, employee_name, employee_surname, payment_amount, payment_date) 
        VALUES (%s, %s, %s, %s, %s)'''
    try:
        cursor.execute(sql, (None, employee_name, employee_surname, payment_amount, mysql_timestamp))
        db.commit()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Get_Extra_Payments():
    try:
        db = get_my_db()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_payments_extra'''
        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close()

        total_rows = []
        if len(foundRecords) > 0:
            for row in foundRecords:
                payment_id =                        row[0]
                employee_name =                     row[1]
                employee_surname =                  row[2]
                payment_amount =                    row[3]
                payment_date =                      row[4]
                date_app_string = payment_date.strftime('%d.%m.%Y')

                row_data = {
                    "id" :                  payment_id,
                    "name" :                employee_name,
                    "surname" :             employee_surname,
                    "payment_amount" :      payment_amount,
                    "payment_date" :        payment_date,
                    "date_app_string" :     date_app_string,
                }
                total_rows.append(row_data)

            response_data = {"status" : "ok", "result_rows" : total_rows}
        else:
            response_data = {"status" : "not_found"}

    except Exception as error:
        LogError(error)
        cursor.close()
        print(f"Error While Getting Employees: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Get_Specific_Extra_Payment(data):
    try:
        db = get_my_db()
        employee_name =                     data['employee_name']
        employee_surname =                  data['employee_surname']
        payment_amount =                    data['payment_amount']
        payment_date =                      data['payment_date']
        dt_obj = datetime.strptime(payment_date, '%d.%m.%Y')
        mysql_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

        cursor = db.cursor()
        query = f'''SELECT * FROM hr_payments_extra WHERE 
        employee_name="%s" AND 
        employee_surname="%s" AND 
        payment_amount="%s" AND 
        payment_date="%s" ''' % (employee_name, employee_surname, payment_amount, mysql_timestamp)
        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close()

        total_rows = []
        if len(foundRecords) > 0:
            for row in foundRecords:
                payment_id =                        row[0]
                employee_name =                     row[1]
                employee_surname =                  row[2]
                payment_amount =                    row[3]
                payment_date =                      row[4]
                date_app_string = payment_date.strftime('%d.%m.%Y')

                row_data = {
                    "id" :                  payment_id,
                    "name" :                employee_name,
                    "surname" :             employee_surname,
                    "payment_amount" :      payment_amount,
                    "payment_date" :        payment_date,
                    "date_app_string" :     date_app_string,
                }
                total_rows.append(row_data)

            response_data = {"status" : "ok", "result_rows" : total_rows}
        else:
            response_data = {"status" : "not_found"}

    except Exception as error:
        LogError(error)
        cursor.close()
        print(f"Error While Getting Employees: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Edit_Extra_Payment(data):
    db = get_my_db()
    employee_name =                     data['employee_name']
    employee_surname =                  data['employee_surname']
    payment_amount_old =                data['payment_amount_old']
    payment_date_old =                  data['payment_date_old']
    payment_amount_new =                data['payment_amount_new']
    payment_date_new =                  data['payment_date_new']

    dt_obj = datetime.strptime(payment_date_old, '%d.%m.%Y')
    timestamp_old = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    dt_obj = datetime.strptime(payment_date_new, '%d.%m.%Y')
    timestamp_new = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_payments_extra WHERE 
    employee_name="%s" AND 
    employee_surname="%s" AND 
    payment_amount="%s" AND 
    payment_date="%s" ''' % (employee_name, employee_surname, payment_amount_old, timestamp_old)

    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        response_data = {"status" : "not_found"}
        return response_data
    
    cursor = db.cursor()
    sql = '''UPDATE hr_payments_extra SET employee_name = %s, employee_surname = %s, payment_amount = %s, payment_date = %s'''
    try:
        cursor.execute(sql, (employee_name, employee_surname, payment_amount_new, timestamp_new))
        db.commit()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Updating Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Remove_Extra_Payment(data):
    db = get_my_db()
    employee_name =                     data['employee_name']
    employee_surname =                  data['employee_surname']
    payment_amount =                    data['payment_amount']
    payment_date =                      data['payment_date']
    dt_obj = datetime.strptime(payment_date, '%d.%m.%Y')
    mysql_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_payments_extra WHERE 
    employee_name="%s" AND 
    employee_surname="%s" AND 
    payment_amount="%s" AND 
    payment_date="%s" ''' % (employee_name, employee_surname, payment_amount, mysql_timestamp)

    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM hr_payments_extra WHERE 
        employee_name="%s" AND 
        employee_surname="%s" AND 
        payment_amount="%s" AND 
        payment_date="%s" ''' % (employee_name, employee_surname, payment_amount, mysql_timestamp)
    try:
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        print(error)
        cursor.close()
        db.rollback()
        print(f"Error While Removing Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    return response_data


# endregion

# region PERMISSIONS / VACATIONS


def Add_Permission(data):
    db = get_my_db()
    employee_name =                     data['employee_name']
    employee_surname =                  data['employee_surname']
    permission_date =                   data['permission_date']
    permission_is_paid =                bool(data['permission_is_paid'])
    

    dt_obj = datetime.strptime(permission_date, '%d.%m.%Y')
    mysql_timestamp_permission_start = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    dt_obj = dt_obj.replace(hour=23, minute=59, second=59)
    mysql_timestamp_permission_permission_end = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    sql = '''INSERT INTO hr_vacations_permissions (id, employee_name, employee_surname, vacation_start, vacation_end, is_paid) 
        VALUES (%s, %s, %s, %s, %s, %s)'''
    try:
        cursor.execute(sql, (None, employee_name, employee_surname, mysql_timestamp_permission_start, 
                             mysql_timestamp_permission_permission_end, permission_is_paid))
        db.commit()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Get_Permissions():
    try:
        db = get_my_db()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_vacations_permissions'''
        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close()

        total_rows = []
        if len(foundRecords) > 0:
            for row in foundRecords:
                permission_id =                     row[0]
                employee_name =                     row[1]
                employee_surname =                  row[2]
                permission_start =                  row[3]
                permission_end =                    row[4]
                permission_is_paid =                row[5]

                date_string_start = permission_start.strftime('%d.%m.%Y')
                date_string_end = permission_end.strftime('%d.%m.%Y')

                row_data = {
                    "id" :                      permission_id,
                    "name" :                    employee_name,
                    "surname" :                 employee_surname,
                    "permission_start" :        permission_start,
                    "permission_end" :          date_string_start,
                    "permission_is_paid" :      date_string_end
                }
                total_rows.append(row_data)

            response_data = {"status" : "ok", "result_rows" : total_rows}
        else:
            response_data = {"status" : "not_found"}

    except Exception as error:
        LogError(error)
        cursor.close()
        print(f"Error While Getting Permissions: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Get_Specific_Permission(data):
    try:
        db = get_my_db()
        employee_name =                     data['employee_name']
        employee_surname =                  data['employee_surname']
        permission_start =                  data['permission_start']
        permission_end =                    data['permission_end']
        permission_is_paid =                bool(data['permission_is_paid'])

        dt_obj = datetime.strptime(permission_start, '%d.%m.%Y')
        mysql_timestamp_permission_start = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

        dt_obj = datetime.strptime(permission_end, '%d.%m.%Y')
        mysql_timestamp_permission_permission_end = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

        cursor = db.cursor()
        query = f'''SELECT * FROM hr_vacations_permissions WHERE 
        employee_name="%s" AND 
        employee_surname="%s" AND 
        permission_start="%s" AND 
        permission_end="%s" AND
        is_paid=%s ''' % (employee_name, employee_surname, mysql_timestamp_permission_start, mysql_timestamp_permission_permission_end, permission_is_paid)
        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close()

        total_rows = []
        if len(foundRecords) > 0:
            for row in foundRecords:
                permission_id =                     row[0]
                employee_name =                     row[1]
                employee_surname =                  row[2]
                permission_start =                  row[3]
                permission_end =                    row[4]
                permission_is_paid =                row[5]

                date_string_start = permission_start.strftime('%d.%m.%Y')
                date_string_end = permission_end.strftime('%d.%m.%Y')

                row_data = {
                    "id" :                      permission_id,
                    "name" :                    employee_name,
                    "surname" :                 employee_surname,
                    "permission_start" :        permission_start,
                    "permission_end" :          date_string_start,
                    "permission_is_paid" :      date_string_end
                }
                total_rows.append(row_data)

            response_data = {"status" : "ok", "result_rows" : total_rows}
        else:
            response_data = {"status" : "not_found"}

    except Exception as error:
        LogError(error)
        cursor.close()
        print(f"Error While Getting Permission: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Edit_Permission(data):
    db = get_my_db()
    employee_name =                         data['employee_name']
    employee_surname =                      data['employee_surname']
    permission_start_old =                  data['permission_start_old']
    permission_end_old =                    data['permission_end_old']
    permission_is_paid_old =                bool(data['permission_is_paid_old'])

    permission_start_new =                  data['permission_start_new']
    permission_end_new =                    data['permission_end_new']
    permission_is_paid_new =                bool(data['permission_is_paid_new'])

    dt_obj = datetime.strptime(permission_start_old, '%d.%m.%Y')
    timestamp_start_old = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
    dt_obj = datetime.strptime(permission_end_old, '%d.%m.%Y')
    timestamp_end_old = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    dt_obj = datetime.strptime(permission_start_new, '%d.%m.%Y')
    timestamp_start_new = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
    dt_obj = datetime.strptime(permission_end_new, '%d.%m.%Y')
    timestamp_end_new = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_vacations_permissions WHERE 
    employee_name="%s" AND 
    employee_surname="%s" AND 
    permission_start="%s" AND 
    permission_end="%s" AND
    is_paid="%s" ''' % (employee_name, employee_surname, timestamp_start_old, timestamp_end_old, permission_is_paid_old)

    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        response_data = {"status" : "not_found"}
        return response_data
    
    cursor = db.cursor()
    sql = '''UPDATE hr_vacations_permissions SET employee_name = %s, employee_surname = %s, vacation_start = %s, vacation_end = %s, is_paid = %s'''
    try:
        cursor.execute(sql, (employee_name, employee_surname, timestamp_start_new, timestamp_end_new, permission_is_paid_new))
        db.commit()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Updating Permission: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Remove_Permission(data):
    db = get_my_db()
    employee_name =                         data['employee_name']
    employee_surname =                      data['employee_surname']
    permission_start =                      data['permission_start']
    permission_end =                        data['permission_end']
    permission_is_paid =                    bool(data['permission_is_paid'])

    dt_obj = datetime.strptime(permission_start, '%d.%m.%Y')
    timestamp_start = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
    dt_obj = datetime.strptime(permission_end, '%d.%m.%Y')
    timestamp_end = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_vacations_permissions WHERE 
        employee_name="%s" AND 
        employee_surname="%s" AND 
        vacation_start="%s" AND 
        vacation_end="%s" AND
        is_paid="%s" ''' % (employee_name, employee_surname, timestamp_start, timestamp_end, permission_is_paid)

    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM hr_vacations_permissions WHERE 
        employee_name="%s" AND 
        employee_surname="%s" AND 
        vacation_start="%s" AND 
        vacation_end="%s" AND
        is_paid="%s" ''' % (employee_name, employee_surname, timestamp_start, timestamp_end, permission_is_paid)
    try:
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        print(error)
        cursor.close()
        db.rollback()
        print(f"Error While Removing Permission: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    return response_data


#endregion

# region SPECIAL HOLIDAYS

def Add_Special_Holiday(data):
    db = get_my_db()
    holiday_name =  data['new_ozelgun_adi']
    holiday_year = data['new_ozelgun_yili']
    holiday_month =   data['new_ozelgun_ayi']
    holiday_day =   data['new_ozelgun_gunu']
    holiday_work_percent =   data['new_ozelgun_mesai_orani']

    cursor = db.cursor()
    sql = '''INSERT INTO hr_special_holidays (id, holiday_name, holiday_year, holiday_month, holiday_day, holiday_work_percent) 
        VALUES (%s, %s, %s, %s, %s, %s)'''
    try:
        cursor.execute(sql, (None, holiday_name, holiday_year, holiday_month, holiday_day, holiday_work_percent))
        db.commit()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Holiday: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Get_Special_Holidays():
    try:
        db = get_my_db()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_special_holidays'''
        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close()

        total_rows = []
        if len(foundRecords) > 0:
            for row in foundRecords:
                holiday_id =             row[0]
                holiday_name =           row[1]
                holiday_year =           row[2]
                holiday_month =          row[3]
                holiday_day =            row[4]
                holiday_work_percent =   row[5]


                row_data = {
                    "id" :                      holiday_id,
                    "holiday_name" :            holiday_name,
                    "holiday_year" :            holiday_year,
                    "holiday_month" :           holiday_month,
                    "holiday_day" :             holiday_day,
                    "holiday_work_percent" :    holiday_work_percent
                }
                total_rows.append(row_data)

            response_data = {"status" : "ok", "result_rows" : total_rows}
        else:
            response_data = {"status" : "not_found"}

    except Exception as error:
        LogError(error)
        try:
            cursor.close()
            db.close()
        except:
            pass
        print(f"Error While Getting Special Holidays: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def Edit_Special_Holiday(data):
    db = get_my_db()
    holiday_name_old =   data['initial_ozelgun_adi']
    holiday_name_new =   data['new_ozelgun_adi']

    holiday_year_old =  ""
    holiday_year_new =    data['new_ozelgun_yili']

    holiday_month_old =   data['initial_ozelgun_ayi']
    holiday_month_new =   data['new_ozelgun_ayi']

    holiday_day_old =  data['initial_ozelgun_gunu']
    holiday_day_new =    data['new_ozelgun_gunu']

    holiday_work_percent_old =   data['initial_ozelgun_mesai_orani'].replace("%","")
    holiday_work_percent_new =   data['new_ozelgun_mesai_orani'].replace("%","")

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_special_holidays WHERE 
    holiday_name="%s" AND 
    holiday_month="%s" AND
    holiday_day="%s" ''' % (holiday_name_old, holiday_month_old, holiday_day_old)

    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    print(foundRecords)
    if len(foundRecords) <= 0:
        response_data = {"status" : "not_found"}
        return response_data
    
    print(foundRecords)
    
    cursor = db.cursor()
    sql = '''UPDATE hr_special_holidays SET holiday_name = %s, holiday_year = %s, holiday_month = %s, holiday_day = %s, holiday_work_percent = %s '''
    try:
        cursor.execute(sql, (holiday_name_new, holiday_year_new, holiday_month_new, holiday_day_new, holiday_work_percent_new))
        db.commit()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Updating Special Holiday: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

#TODO
def Remove_Special_Holiday(data):
    db = get_my_db()
    holiday_name =  data['holiday_name']
    holiday_start = data['holiday_start']
    holiday_end =   data['holiday_end']

    dt_obj = datetime.strptime(holiday_start, '%d.%m.%Y')
    timestamp_start = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    dt_obj = datetime.strptime(holiday_end, '%d.%m.%Y')
    timestamp_end = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_special_holidays WHERE 
        holiday_name="%s" AND 
        holiday_start="%s" AND 
        holiday_end="%s" ''' % (holiday_name, timestamp_start, timestamp_end)

    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM hr_special_holidays WHERE 
        holiday_name="%s" AND 
        holiday_start="%s" AND 
        holiday_end="%s" ''' % (holiday_name, timestamp_start, timestamp_end)
    try:
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        print(error)
        cursor.close()
        db.rollback()
        print(f"Error While Removing Special Holiday: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    return response_data


# endregion


#endregion


