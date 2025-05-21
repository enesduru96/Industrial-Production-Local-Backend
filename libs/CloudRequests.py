
import traceback, json
from libs import LocalRequests, Utilities
from libs.Helpers import ScaleMaterialMapper, log_error_cloud
from datetime import datetime
from mysql.connector.errors import ProgrammingError

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass

def GetMyDB():
    db = LocalRequests.get_my_db()
    return db


def Get_Changes_From_Database():
    try:
        row_ids = []
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM z_cloud_tasks WHERE is_completed = 0'''
        cursor.execute(sql_getstring)
        foundRecords = cursor.fetchall()
        data_list = []
        for tupleRecord in foundRecords:
            row_ids.append(tupleRecord[0])
            new_data = {
                "id" : tupleRecord[0], 
                "data" : json.loads(tupleRecord[1])
            }
            data_list.append(new_data)
        
        for id in row_ids:
            sql_updatestring = '''UPDATE z_cloud_tasks SET is_completed=%s WHERE id=%s'''
            cursor.execute(sql_updatestring, (1,id))
            db.commit()

        cursor.close()
        db.close()
        final_data = {
            "status": "ok",
            "data_list" : data_list
        }
    except Exception as error:
        log_error_cloud(str(error))
        final_data = {
            "status": "error",
            "error_text": str(error)
        }
    return final_data

def Save_New_Cloud_Sync_Task(data):
    db = GetMyDB()
    cursor = db.cursor()
    sql = "INSERT INTO z_cloud_tasks (id,data,is_completed) VALUES (%s, %s, %s)"
    try:
        cursor.execute(sql, (None, json.dumps(data), False))
        db.commit()
        cursor.close()
        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}      
    
    return response_data

def Handle_Save_New_Changes_To_Database(data_list):

    successful_queries = []
    failed_queries = []

    for data in data_list:
        table_name = data["table"]
        query = Utilities.decode_string(data["sql_string"])
        all_values = data["values"]

        db = GetMyDB()
        cursor = db.cursor()

        for value_list in all_values:
            try:
                cursor.execute(query, tuple(value_list))
                db.commit()

                result = {
                    "query": query,
                    "values": value_list
                }
                successful_queries.append(result)

            except ProgrammingError as error:
                print(f"Cursor Error, {error}")
                log_error_cloud(str(error))
                if "cursor is not connected" in str(error).lower():
                    if not db.is_connected():
                        db.reconnect()
                    
                    cursor = db.cursor()
                    cursor.execute(query, tuple(value_list))


            except Exception as error:
                print(error)
                log_error_cloud(str(error), value_list)

                result = {
                    "query": query,
                    "values": value_list,
                    "error": str(error),
                    "traceback": str(traceback.format_exc())
                }

                failed_queries.append(result)

    try:
        cursor.close()
        db.close()
    except:
        pass
        
    return {
        "status": "ok",
        "successful": successful_queries,
        "failed": failed_queries
    }

def Handle_Save_New_Changes_To_Database_Dictionary(data):

    successful_queries = []
    failed_queries = []
    
    table_name = data["table"]
    query = Utilities.decode_string(data["sql_string"])
    all_values = data["values"]

    db = GetMyDB()
    cursor = db.cursor()

    for value_list in all_values:
        try:
            cursor.execute(query, tuple(value_list))
            db.commit()


            result = {
                "query": query,
                "values": value_list
            }
            successful_queries.append(result)

        except ProgrammingError as error:
            print(f"Cursor Error, {error}")
            log_error_cloud(str(error))
            if "cursor is not connected" in str(error).lower():
                if not db.is_connected():
                    db.reconnect()
                
                cursor = db.cursor()
                cursor.execute(query, tuple(value_list))
        except Exception as error:
            print(error)
            log_error_cloud(str(error))

            result = {
                "query": query,
                "values": value_list,
                "error": str(error),
                "traceback": str(traceback.format_exc())
            }

            failed_queries.append(result)
    

    try:
        cursor.close()
        db.close()
    except:
        pass

    return {
        "status": "ok",
        "successful": successful_queries,
        "failed": failed_queries
    }

