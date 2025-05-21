
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


def get_material_types_from_db(data):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM wr_material_types'''
        cursor.execute(sql_getstring)
        foundRecords = cursor.fetchall(); cursor.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {"id" : tupleRecord[0], "material_type" : tupleRecord[1]}
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    return final_data

def add_material_type_to_db(data):
    db = GetMyDB()

    material_type = data['material_type']

    cursor = db.cursor()
    query = f'''SELECT * FROM wr_material_types WHERE material_type="%s" ''' % material_type
    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) > 0:
        response_data = {"status" : "duplicate"}
        return response_data
    
    cursor = db.cursor()
    sql = '''INSERT INTO wr_material_types (id, material_type) VALUES (%s, %s)'''
    try:
        cursor.execute(sql, (None, material_type))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "insert",
            "table": "wr_material_types",
            "sql_string": Utilities.encode_string(sql),
            "values": [[None, material_type]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def edit_material_type(data):
    db = GetMyDB()

    old_material_type_name = data['old_material_type_name']
    new_material_type_name = data['new_material_type_name']
    
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_types WHERE material_type="%s" ''' % old_material_type_name
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_types WHERE material_type="%s" ''' % new_material_type_name
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) > 0:
        return {"status" : "duplicate"}
            

    cursor = db.cursor()
    sql = f"UPDATE wr_material_types SET material_type = %s WHERE material_type = %s"
    try:
        cursor.execute(sql, (new_material_type_name, old_material_type_name))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "update",
            "table": "wr_material_types",
            "sql_string": Utilities.encode_string(sql),
            "values": [[new_material_type_name, old_material_type_name]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    return response_data

def remove_material_type(data):
    db = GetMyDB()

    material_type = data['material_type']

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_types WHERE material_type="%s" ''' % material_type
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM wr_material_types WHERE material_type=%s '''
    try:
        cursor.execute(sql, (material_type,))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "delete",
            "table": "wr_material_types",
            "sql_string": Utilities.encode_string(sql),
            "values": [[material_type]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        print(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    return response_data