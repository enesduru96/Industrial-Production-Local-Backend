
import traceback
from libs import LocalRequests

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass

def GetMyDB():
    db = LocalRequests.get_my_db()
    return db

def get_warehouse_config():
    db = GetMyDB()
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_config'''
    cursor.execute(sql_getstring)
    config_data = cursor.fetchone()

    new_data = {
        "id" : config_data[0], 
        "api_url" : config_data[1],
        "com_port" : config_data[2],
        "baud_rate" : config_data[3],
        "debug_mode" : config_data[4],
        "warehouse_passwd" : config_data[5]
    }
    cursor.close()
    db.close()
    final_data = {"status" : "ok", "data" : new_data}
    print(final_data)
    return final_data
