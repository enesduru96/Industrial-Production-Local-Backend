
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


def get_customers_from_db(data):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM wr_customers'''
        cursor.execute(sql_getstring)
        foundRecords = cursor.fetchall(); cursor.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {
                    "id" : tupleRecord[0],
                    "sirket" : tupleRecord[1],
                    "musteri_adi" : tupleRecord[2],
                    "iletisim_kisisi" : tupleRecord[3],
                    "musteri_email" : tupleRecord[4],
                    "musteri_telefon" : tupleRecord[5],
                    "notlar" : tupleRecord[6]
                }
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    return final_data

def add_customer_to_db(data):
    db = GetMyDB()
    sirket = data["sirket"]
    musteri_adi = data["musteri_adi"]
    iletisim_kisisi = data["iletisim_kisisi"]
    email = data["email"]
    telefon = data["telefon"]
    notlar = data["notlar"]

    cursor = db.cursor()
    sql = '''INSERT INTO wr_customers (id, company, customer_name, contact_name, customer_email, customer_phone, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
    try:
        cursor.execute(sql, (None, sirket, musteri_adi, iletisim_kisisi, email, telefon, notlar))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "insert",
            "table": "wr_customers",
            "sql_string": Utilities.encode_string(sql),
            "values": [[None, sirket, musteri_adi, iletisim_kisisi, email, telefon, notlar]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        db.close()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    return response_data

def edit_customer(data):
    db = GetMyDB()

    id = data["id"]
    sirket = data["sirket"]
    musteri_adi = data["musteri_adi"]
    iletisim_kisisi = data["iletisim_kisisi"]
    email = data["email"]
    telefon = data["telefon"]
    notlar = data["notlar"]
    
    cursor = db.cursor()
    sql_getstring = "SELECT * FROM wr_customers WHERE id= %s"
    cursor.execute(sql_getstring, (id, ))
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f"UPDATE wr_customers SET company=%s, customer_name=%s, contact_name=%s, customer_email=%s, customer_phone=%s, notes=%s WHERE id = %s"
    try:
        cursor.execute(sql, (sirket, musteri_adi, iletisim_kisisi, email, telefon, notlar, id))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "update",
            "table": "wr_customers",
            "sql_string": Utilities.encode_string(sql),
            "values": [[sirket, musteri_adi, iletisim_kisisi, email, telefon, notlar, id]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        cursor.close()
        db.rollback()
        db.close()
        print(f"Error While Editing Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    return response_data

def remove_customer(data):
    db = GetMyDB()

    customer_name = data['customer_name']

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_customers WHERE customer_name="%s" ''' % customer_name
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM wr_customers WHERE customer_name=%s '''
    try:
        cursor.execute(sql, (customer_name))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "delete",
            "table": "wr_customers",
            "sql_string": Utilities.encode_string(sql),
            "values": [[customer_name]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        print(error)
        cursor.close()
        db.rollback()
        print(f"Error While Deleting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    return response_data