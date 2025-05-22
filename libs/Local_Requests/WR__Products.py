
import traceback, os, base64
from libs import LocalRequests, CloudRequests, Utilities
import pprint
from libs.Local_Requests import WR___InternalGetters
from libs.Helpers import log_error_wr


def GetMyDB():
    db = LocalRequests.get_my_db()
    return db

def get_products(data):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM wr_products'''
        cursor.execute(sql_getstring)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        data_list = []
        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                print(tupleRecord)
                new_data = {
                    "id" : tupleRecord[0], 
                    "name" : tupleRecord[1],
                    "company" : tupleRecord[2],
                    "amount" : tupleRecord[3],
                    "photo_uuid" : tupleRecord[4],
                }

                data_list.append(new_data)
            response_data = {
                "result" : {
                    "status" : "ok",
                    "items" : data_list
                }
            }
        else:
            response_data = {
                "result" :{
                    "status" : "not_found"
                }
            }
    except Exception as error:
        log_error_wr(error)
        print(f"Error While Getting Urunler: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
     
    try:db.close(); cursor.close()
    except:pass 
    return response_data


def get_base64_product_photo(data):
    try:
        uuid = data["uuid"]
        images_folder = 'flask_images'
        wr_folder = "warehouse"
        products_folder = "products"

        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, images_folder, wr_folder, products_folder)
        file_path = os.path.join(folder_path, f"{uuid}.jpg")
        if os.path.exists(file_path):
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return {
                    "status": "ok",
                    "resim64" : encoded_string
                }
        else:
            return {
                "status" : "not_found"
            }
    except Exception as error:
        log_error_wr(error)
        print(error)
        return {
            "status" : "error",
            "error_text" : str(error)
        }

def save_photo_locally(base64_photo_string, filename):
    try:
        images_folder = 'flask_images'
        wr_folder = "warehouse"
        products_folder = "products"

        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, images_folder, wr_folder, products_folder)
        os.makedirs(folder_path, exist_ok=True)
        _, base64_string = base64_photo_string.split(',', 1)
        img_data = base64.b64decode(base64_string)
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'wb') as f:
            f.write(img_data)
        return True
        
    except Exception as error:
        log_error_wr(error)
        return False


def add_product(data):
    db = GetMyDB()
    cursor = db.cursor()

    urun_sirketi = data['urun_sirketi']
    urun_adi = data['urun_adi']
    urun_miktari = data['urun_miktari']
    urun_foto_base64 = data['urun_foto']
    urun_foto_uuid = data['urun_foto_uuid']
    urun_bilesenleri = data['urun_bilesenleri']

    query = "SELECT * FROM wr_products WHERE product_name = %s"
    cursor.execute(query, (urun_adi,))
    existing_product = cursor.fetchone()
    if existing_product:
        cursor.close()
        db.close()
        return {"status": "duplicate"}

    try:
        query = "INSERT INTO wr_products (id, product_name, company, amount, photo_uuid) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (None, urun_adi, urun_sirketi, urun_miktari, urun_foto_uuid))

        sync_data = {
            "type": "insert",
            "table": "wr_products",
            "sql_string": Utilities.encode_string(query),
            "values": [[None, urun_adi, urun_sirketi, urun_miktari, urun_foto_uuid]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        product_id = cursor.lastrowid
    except Exception as error:
        log_error_wr(error)
        db.rollback()
        response_data = {"status": "error", "error_text": str(error)}
        return response_data

    photo_save_result = save_photo_locally(urun_foto_base64, f"{urun_foto_uuid}.jpg")

    bilesen_data = []
    for bilesen in urun_bilesenleri:
        bilesen_adi = bilesen["adi"]
        bilesen_miktari = bilesen["miktar"]
        bilesen_id = WR___InternalGetters.Internal_Get_Hammadde_ID_With_Name(bilesen_adi)
        bilesen_data.append((None, product_id, urun_adi, bilesen_id, bilesen_adi, bilesen_miktari))

    try:
        query = "INSERT INTO wr_product_recipes (id, product_id, product_name, material_id, material_name, material_count) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.executemany(query, bilesen_data)
        db.commit()

        sync_data = {
            "type": "insert",
            "table": "wr_product_recipes",
            "sql_string": Utilities.encode_string(query),
            "values": [bilesen_data]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status": "ok"}
    except Exception as error:
        log_error_wr(error)
        db.rollback()
        response_data = {"status": "error", "error_text": str(error)}
    finally:
        try:cursor.close(); db.close()
        except:pass

    return response_data


def edit_product(data):
    db = GetMyDB()
    cursor = db.cursor()

    product_id = data['urun_id']
    product_company = data['urun_sirketi']
    product_name = data['urun_adi']
    product_amount = data['urun_miktari']
    product_photo_base64 = data['urun_foto']
    product_photo_uuid = data['urun_foto_uuid']
    product_elements = data['urun_bilesenleri']


    try:
        query = "UPDATE wr_products SET product_name = %s, company = %s, amount = %s, photo_uuid = %s WHERE id = %s"
        cursor.execute(query, (product_name, product_company, product_amount, product_photo_uuid, product_id))

        sync_data = {
            "type": "update",
            "table": "wr_products",
            "sql_string": Utilities.encode_string(query),
            "values": [[product_name, product_company, product_amount, product_photo_uuid, product_id]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        photo_save_result = save_photo_locally(product_photo_base64, f"{product_photo_uuid}.jpg")


        query = "DELETE FROM wr_product_recipes WHERE product_id = %s"
        cursor.execute(query, (product_id,))

        sync_data = {
            "type": "delete",
            "table": "wr_product_recipes",
            "sql_string": Utilities.encode_string(query),
            "values": [[product_id]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        bilesen_data = []
        for bilesen in product_elements:
            bilesen_adi = bilesen["adi"]
            bilesen_miktari = bilesen["miktar"]
            bilesen_id = WR___InternalGetters.Internal_Get_Hammadde_ID_With_Name(bilesen_adi)
            bilesen_data.append((None, product_id, product_name, bilesen_id, bilesen_adi, bilesen_miktari))

        query = "INSERT INTO wr_product_recipes (id, product_id, product_name, material_id, material_name, material_count) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.executemany(query, bilesen_data)

        sync_data = {
            "type": "insert",
            "table": "wr_product_recipes",
            "sql_string": Utilities.encode_string(query),
            "values": [bilesen_data]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)
        
        db.commit()
        response_data = {"status": "ok"}
    except Exception as error:
        log_error_wr(error)
        db.rollback()
        response_data = {"status": "error", "error_text": str(error)}
    finally:
        try: cursor.close(); db.close()
        except: pass

    return response_data

def get_product_components_single(data):
    db = GetMyDB()
    cursor = db.cursor()

    urun_id = data["urun_id"]
    urun_adi = data["urun_adi"]

    query = "SELECT * FROM wr_product_recipes WHERE product_id = %s AND product_name = %s"
    cursor.execute(query, (urun_id, urun_adi,))
    foundRecords = cursor.fetchall()

    return_list = []
    if len(foundRecords) > 0:
        for tupleRecord in foundRecords:
            new_data = {
                "id" : tupleRecord[0],
                "product_id" : tupleRecord[1],
                "product_name" : tupleRecord[2],
                "hammadde_id" : tupleRecord[3],
                "hammadde_name" : tupleRecord[4],
                "hammadde_amount" : tupleRecord[5]
            }
            return_list.append(new_data)

        cursor.close()
        db.close()
        return {
            "status" : "ok",
            "data" : return_list
        }