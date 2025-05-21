
import traceback, os, base64, json
from libs import LocalRequests, CloudRequests, Utilities

from libs.Local_Requests import WR___InternalGetters
from libs.Helpers import log_error_wr


def GetMyDB():
    db = LocalRequests.get_my_db()
    return db

def get_shipments(data):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM wr_shipments'''
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
                    "sirket" : tupleRecord[1],
                    "musteri" : tupleRecord[2],
                    "tarih" : tupleRecord[3],
                    "saat" : tupleRecord[4],
                    "fatura_uuid" : tupleRecord[5],
                    "irsaliye_uuid" : tupleRecord[6],
                    "urunler" : json.loads(tupleRecord[7]),
                    "durum": tupleRecord[8]
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
        cursor.close()
        print(f"Error While Getting Urunler: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
   
    try:db.close()
    except:pass 
    return response_data


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

def save_pdf_locally(base64_pdf_string, filename):
    try:
        images_folder = 'flask_files'
        wr_folder = "warehouse"
        shipments_folder = "shipments"

        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, images_folder, wr_folder, shipments_folder)
        os.makedirs(folder_path, exist_ok=True)
        _, base64_string = base64_pdf_string.split(',', 1)
        file_data = base64.b64decode(base64_string)
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        return True
        
    except Exception as error:
        log_error_wr(error)
        return False

def get_pdf_locally(uuid):
    try:
        images_folder = 'flask_files'
        wr_folder = "warehouse"
        shipments_folder = "shipments"

        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, images_folder, wr_folder, shipments_folder)
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"{uuid}.pdf")
        with open(file_path, 'rb') as f:
            pdf_content = f.read()
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            return pdf_base64
        
    except Exception as error:
        log_error_wr(error)
        return False

def add_shipment(data):
    db = GetMyDB()
    cursor = db.cursor()

    sirket = data['sirket']
    musteri = data['musteri']
    urunler = data['urunler']
    tarih = data['tarih']
    saat = data['saat']
    fatura_uuid = data['fatura_uuid']
    fatura_b64 = data['fatura_b64']
    irsaliye_uuid = data['irsaliye_uuid']
    irsaliye_b64 = data['irsaliye_b64']

    for urun in urunler:
        try:
            urun_adi = urun['adi']
            query = "SELECT photo_uuid FROM wr_products WHERE product_name = %s"
            cursor.execute(query, (urun_adi,))
            found_item = cursor.fetchone()
            photo_uuid = found_item[0]
            urun['photo_uuid'] = photo_uuid
        except Exception as error:
            print(error)
            log_error_wr(error)

    try:
        query = "SELECT * FROM wr_shipments WHERE sirket = %s AND musteri = %s AND tarih = %s AND saat = %s AND urunler = %s"
        cursor.execute(query, (sirket, musteri, tarih, saat, json.dumps(urunler)))
        existing_product = cursor.fetchone()
        if existing_product:
            cursor.close()
            db.close()
            return {"status": "duplicate"}
    except Exception as error:
        print("1")
        print(error)
        print(traceback.format_exc())
        log_error_wr(error)
        db.rollback()
        response_data = {"status": "error", "error_text": str(error)}
        try:cursor.close(); db.close()
        except:pass
        return response_data

    try:
        query = "INSERT INTO wr_shipments (id, sirket, musteri, tarih, saat, fatura_uuid, irsaliye_uuid, urunler, durum) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (None, sirket, musteri, tarih, saat, fatura_uuid, irsaliye_uuid, json.dumps(urunler), "beklemede"))

        sync_data = {
            "type": "insert",
            "table": "wr_shipments",
            "sql_string": Utilities.encode_string(query),
            "values": [[None, sirket, musteri, tarih, saat, fatura_uuid, irsaliye_uuid, json.dumps(urunler), "beklemede"]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        shipment_id = cursor.lastrowid
    except Exception as error:
        print(traceback.format_exc())
        log_error_wr(error)
        db.rollback()
        response_data = {"status": "error", "error_text": str(error)}
        return response_data

    irsaliye_save_result = save_pdf_locally(irsaliye_b64, f"{irsaliye_uuid}.pdf")
    fatura_save_result = save_pdf_locally(fatura_b64, f"{fatura_uuid}.pdf")

    sevkiyat_urunleri_data = []
    for urun in urunler:
        print(urun)
        urun_adi = urun["adi"]
        urun_miktari = urun["miktar"]
        urun_id = WR___InternalGetters.Internal_Get_Urun_ID_With_Name(urun_adi)
        sevkiyat_urunleri_data.append((None, shipment_id, urun_adi, urun_id, urun_miktari))

        print(sevkiyat_urunleri_data)

    try:
        query = "INSERT INTO wr_shipped_products (id, shipment_id, product_name, product_id, product_count) VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(query, sevkiyat_urunleri_data)
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "insert",
            "table": "wr_shipped_products",
            "sql_string": Utilities.encode_string(query),
            "values": [sevkiyat_urunleri_data]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status": "ok"}
    except Exception as error:
        print(traceback.format_exc())
        log_error_wr(error)
        db.rollback()
        response_data = {"status": "error", "error_text": str(error)}
    finally:
        try:cursor.close(); db.close()
        except:pass

    return response_data

def get_invoice(data):
    print(data)
    try:
        uuid = data["uuid"]
        pdf_encoded_string = get_pdf_locally(uuid)
        print(pdf_encoded_string)
        response = {"status": "ok", 
                    "result": {
                        "b64pdf" : pdf_encoded_string,
                        "uuid" : uuid
                        }
                    }
    except Exception as error:
        log_error_wr(error)
        response = {"status" : "error", "error_text": str(error)}
    
    return response

def get_shipment_components_single(data):
    db = GetMyDB()
    cursor = db.cursor()

    sevkiyat_id = data["sevkiyat_id"]


    query = "SELECT * FROM wr_shipped_products WHERE shipment_id = %s"
    cursor.execute(query, (sevkiyat_id,))
    foundRecords = cursor.fetchall()

    return_list = []
    if len(foundRecords) > 0:
        for tupleRecord in foundRecords:
            new_data = {
                "id" : tupleRecord[0],
                "sevkiyat_id" : tupleRecord[1],
                "urun_adi" : tupleRecord[2],
                "urun_id" : tupleRecord[3],
                "urun_adet" : tupleRecord[4]
            }
            return_list.append(new_data)

        cursor.close()
        db.close()
        return {
            "status" : "ok",
            "data" : return_list
        }