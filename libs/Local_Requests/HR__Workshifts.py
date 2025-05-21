
import traceback
from libs import LocalRequests, Utilities, CloudRequests

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass

def GetMyDB():
    db = LocalRequests.get_my_db()
    return db




def Get_Workshifts_From_Database(data):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM hr_workshifts'''
        cursor.execute(sql_getstring)
        foundRecords = cursor.fetchall(); cursor.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {
                    "id" : tupleRecord[0],
                    "workshift_name" : tupleRecord[1],
                    "workshift_start" : tupleRecord[2],
                    "workshift_end" : tupleRecord[3],
                    "break_start" : tupleRecord[4],
                    "break_end" : tupleRecord[5],
                    "entry_tolerance_minutes" : tupleRecord[6],
                    "exit_tolerance_minutes" : tupleRecord[7],
                    "extra_percent" : tupleRecord[8]
                    }
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    try:db.close()
    except:pass
    return final_data

def Add_Workshift_To_Database(data):
    db = GetMyDB()

    workshift_name = data['workshift_name']
    workshift_start = data['workshift_start']
    workshift_end = data['workshift_end']
    break_start = data['break_start']
    break_end = data['break_end']
    entry_tolerance = int(data['entry_tolerance'])
    exit_tolerance = int(data['exit_tolerance'])
    extra_percent = int(data['extra_percent'])

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_workshifts WHERE workshift_name="%s" ''' % (workshift_name)
    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) > 0:
        response_data = {"status" : "duplicate"}
        return response_data
    
    cursor = db.cursor()
    sql = '''INSERT INTO hr_workshifts (id, workshift_name, workshift_start, workshift_end, break_start, break_end, entry_tolerance_minutes, exit_tolerance_minutes, extra_work_percent)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    try:
        cursor.execute(sql, (None, workshift_name, workshift_start, workshift_end, break_start, break_end, entry_tolerance, exit_tolerance, extra_percent))
        db.commit()
        cursor.close()


        sync_data = {
            "type": "insert",
            "table": "hr_workshifts",
            "sql_string": Utilities.encode_string(sql),
            "values": [[None, workshift_name, workshift_start, workshift_end, break_start, break_end, entry_tolerance, exit_tolerance, extra_percent]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    try:db.close()
    except:pass
    return response_data

def Edit_Workshift(data):
    db = GetMyDB()

    old_workshift_name = data['old_workshift_name']
    old_workshift_start = data['old_workshift_start']
    old_workshift_end = data['old_workshift_end']
    old_break_start = data['old_break_start']
    old_break_end = data['old_break_end']
    old_entry_tolerance = int(data['old_entry_tolerance'])
    old_exit_tolerance = int(data['old_exit_tolerance'])
    old_extra_percent = int(data['old_extra_percent'])

    new_workshift_name = data['new_workshift_name']
    new_workshift_start = data['new_workshift_start']
    new_workshift_end = data['new_workshift_end']
    new_break_start = data['new_break_start']
    new_break_end = data['new_break_end']
    new_entry_tolerance = int(data['new_entry_tolerance'])
    new_exit_tolerance = int(data['new_exit_tolerance'])
    new_extra_percent = int(data['new_extra_percent'])


    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM hr_workshifts WHERE workshift_name="%s" ''' % (old_workshift_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM hr_workshifts WHERE workshift_name="%s" ''' % (new_workshift_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if (len(foundRecords) > 0 and new_workshift_name != old_workshift_name):
        return {"status" : "duplicate"}
            

    cursor = db.cursor()
    sql = f"UPDATE hr_workshifts SET workshift_name=%s, workshift_start=%s, workshift_end=%s, break_start=%s, break_end=%s, entry_tolerance_minutes=%s, exit_tolerance_minutes=%s, extra_work_percent=%s  WHERE workshift_name = %s"
    try:
        cursor.execute(sql, (new_workshift_name, new_workshift_start, new_workshift_end, new_break_start, new_break_end, new_entry_tolerance, new_exit_tolerance, new_extra_percent, old_workshift_name))
        db.commit()
        cursor.close()

        sync_data = {
            "type": "update",
            "table": "hr_workshifts",
            "sql_string": Utilities.encode_string(sql),
            "values": [[new_workshift_name, new_workshift_start, new_workshift_end, new_break_start, new_break_end, new_entry_tolerance, new_exit_tolerance, new_extra_percent, old_workshift_name]]
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

def Remove_Workshift(data):
    db = GetMyDB()

    workshift_name = data['workshift_name']

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM hr_workshifts WHERE workshift_name="%s" ''' % (workshift_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM hr_workshifts WHERE workshift_name=%s '''
    try:
        cursor.execute(sql, (workshift_name))
        db.commit()
        cursor.close()

        sync_data = {
            "type": "delete",
            "table": "hr_workshifts",
            "sql_string": Utilities.encode_string(sql),
            "values": [[workshift_name]]
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