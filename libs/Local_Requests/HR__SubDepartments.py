
import traceback
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



def Get_SubDepartments_From_Database(data):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM hr_sub_departments'''
        cursor.execute(sql_getstring)
        foundRecords = cursor.fetchall(); cursor.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {"id" : tupleRecord[0], "sub_department_name" : tupleRecord[1]}
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    try:
        db.close()
    except:
        pass
    return final_data

def Add_SubDepartment_To_Database(data):
    db = GetMyDB()

    sub_department_name = data['sub_department_name']

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_sub_departments WHERE sub_department_name="%s" ''' % (sub_department_name)
    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) > 0:
        response_data = {"status" : "duplicate"}
        return response_data
    
    cursor = db.cursor()
    sql = '''INSERT INTO hr_sub_departments (id, sub_department_name) VALUES (%s, %s)'''
    try:
        cursor.execute(sql, (None, sub_department_name))
        db.commit()
        cursor.close()

        sync_data = {
            "type": "insert",
            "table": "hr_sub_departments",
            "sql_string": Utilities.encode_string(sql),
            "values": [[None, sub_department_name]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    try:db.close()
    except:pass
    return response_data

def Edit_SubDepartment(data):
    db = GetMyDB()

    old_sub_department_name = data['old_sub_department_name']
    new_sub_department_name = data['new_sub_department_name']
    
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM hr_sub_departments WHERE sub_department_name="%s" ''' % (old_sub_department_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM hr_sub_departments WHERE sub_department_name="%s" ''' % (new_sub_department_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) > 0:
        return {"status" : "duplicate"}
            

    cursor = db.cursor()
    sql = f"UPDATE hr_sub_departments SET sub_department_name = %s WHERE sub_department_name = %s"
    try:
        cursor.execute(sql, (new_sub_department_name, old_sub_department_name))
        db.commit()
        cursor.close()

        sync_data = {
            "type": "update",
            "table": "hr_sub_departments",
            "sql_string": Utilities.encode_string(sql),
            "values": [[new_sub_department_name, old_sub_department_name]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    try:db.close()
    except:pass
    return response_data

def Remove_SubDepartment(data):
    db = GetMyDB()

    sub_department_name = data['sub_department_name']

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM hr_sub_departments WHERE sub_department_name="%s" ''' % (sub_department_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM hr_sub_departments WHERE sub_department_name=%s '''
    try:
        cursor.execute(sql, (sub_department_name,))
        db.commit()
        cursor.close()

        sync_data = {
            "type": "delete",
            "table": "hr_sub_departments",
            "sql_string": Utilities.encode_string(sql),
            "values": [[sub_department_name]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        print(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    try:db.close()
    except:pass
    return response_data
