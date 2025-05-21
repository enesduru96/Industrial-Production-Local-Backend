
import traceback, base64
from libs import LocalRequests, CloudRequests, Utilities


def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass

def GetMyDB():
    db = LocalRequests.get_my_db()
    return db



def Get_Departments_From_Database(data):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM hr_departments'''
        cursor.execute(sql_getstring)
        foundRecords = cursor.fetchall(); cursor.close(); db.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {"id" : tupleRecord[0], "department_name" : tupleRecord[1]}
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    return final_data

def Add_Department_To_Database(data):
    db = GetMyDB()

    department_name = data['department_name']

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_departments WHERE department_name="%s" ''' % (department_name)
    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) > 0:
        response_data = {"status" : "duplicate"}
        return response_data
    
    cursor = db.cursor()
    sql = '''INSERT INTO hr_departments (id, department_name) VALUES (%s, %s)'''
    try:
        cursor.execute(sql, (None, department_name))
        db.commit()
        cursor.close()

        sync_data = {
            "type": "insert",
            "table": "hr_departments",
            "sql_string": Utilities.encode_string(sql),
            "values": [[None, department_name]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    try:
        db.close()
    except:
        pass
    return response_data

def Edit_Department(data):
    db = GetMyDB()

    old_department_name = data['old_department_name']
    new_department_name = data['new_department_name']
    
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM hr_departments WHERE department_name="%s" ''' % (old_department_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM hr_departments WHERE department_name="%s" ''' % (new_department_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) > 0:
        return {"status" : "duplicate"}
            

    cursor = db.cursor()
    sql = f"UPDATE hr_departments SET department_name = %s WHERE department_name = %s"
    try:
        cursor.execute(sql, (new_department_name, old_department_name))
        db.commit()
        cursor.close()


        sync_data = {
            "type": "update",
            "table": "hr_departments",
            "sql_string": Utilities.encode_string(sql),
            "values": [[new_department_name, old_department_name]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)
        
        response_data = {"status" : "ok"}
    except Exception as error:
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    try:
        db.close()
    except:
        pass
    return response_data

def Remove_Department(data):
    db = GetMyDB()

    department_name = data['department_name']

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM hr_departments WHERE department_name="%s" ''' % (department_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM hr_departments WHERE department_name=%s '''
    try:
        cursor.execute(sql, (department_name,))
        db.commit()
        cursor.close()

        sync_data = {
            "type": "delete",
            "table": "hr_departments",
            "sql_string": Utilities.encode_string(sql),
            "values": [[department_name]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        print(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}


    try:
        db.close()
    except:
        pass
    return response_data