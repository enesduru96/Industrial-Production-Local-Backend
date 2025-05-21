
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


def get_material_providers_from_db(data):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM wr_material_providers'''
        cursor.execute(sql_getstring)
        foundRecords = cursor.fetchall(); cursor.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {
                    "id" : tupleRecord[0],
                    "items_bought" : tupleRecord[1],
                    "provider_name" : tupleRecord[2],
                    "contact_name" : tupleRecord[3],
                    "provider_email" : tupleRecord[4],
                    "provider_phone" : tupleRecord[5],
                    "notes" : tupleRecord[6]
                }
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    return final_data

def add_material_provider_to_db(data):
    db = GetMyDB()
    alinan_hammadde = data["alinan_hammadde"]
    tedarikci_adi = data["tedarikci_adi"]
    iletisim_kisisi = data["iletisim_kisisi"]
    email = data["email"]
    telefon = data["telefon"]
    notlar = data["notlar"]

    
    cursor = db.cursor()
    sql = '''INSERT INTO wr_material_providers (id, items_bought, provider_name, contact_name, provider_email, provider_phone, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
    try:
        cursor.execute(sql, (None, alinan_hammadde, tedarikci_adi, iletisim_kisisi, email, telefon, notlar))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "insert",
            "table": "wr_material_providers",
            "sql_string": Utilities.encode_string(sql),
            "values": [[None, alinan_hammadde, tedarikci_adi, iletisim_kisisi, email, telefon, notlar]]
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

def edit_material_provider(data):
    db = GetMyDB()

    id = data["id"]
    alinan_hammadde = data["alinan_hammadde"]
    tedarikci_adi = data["tedarikci_adi"]
    iletisim_kisisi = data["iletisim_kisisi"]
    email = data["email"]
    telefon = data["telefon"]
    notlar = data["notlar"]
    
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_providers WHERE id="%s" ''' % id
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f"UPDATE wr_material_providers SET items_bought=%s, provider_name=%s, contact_name=%s, provider_email=%s, provider_phone=%s, notes=%s WHERE id = %s"
    try:
        cursor.execute(sql, (alinan_hammadde, tedarikci_adi, iletisim_kisisi, email, telefon, notlar, id))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "update",
            "table": "wr_material_providers",
            "sql_string": Utilities.encode_string(sql),
            "values": [[alinan_hammadde, tedarikci_adi, iletisim_kisisi, email, telefon, notlar, id]]
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

def remove_material_provider(data):
    db = GetMyDB()

    provider_name = data['provider_name']

    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_providers WHERE provider_name="%s" ''' % provider_name
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f'''DELETE FROM wr_material_providers WHERE provider_name=%s '''
    try:
        cursor.execute(sql, (provider_name))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "delete",
            "table": "wr_material_providers",
            "sql_string": Utilities.encode_string(sql),
            "values": [[provider_name]]
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