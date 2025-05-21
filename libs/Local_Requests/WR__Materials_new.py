
import traceback, json, os, base64
from libs import LocalRequests, CloudRequests, Utilities, Helpers
from libs.Helpers import ScaleMaterialMapper
from libs.Local_Requests import Printer_Master
from datetime import datetime

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass

def GetMyDB():
    db = LocalRequests.get_my_db()
    return db


def handle_scale_weighed_materials(data):
    db = GetMyDB()
    material_name = data[ScaleMaterialMapper.name]
    material_count = data[ScaleMaterialMapper.count]
    material_totalWeight = data[ScaleMaterialMapper.total_weight]
    material_perWeight = data[ScaleMaterialMapper.weight_per_object]
    material_weighedDate = data[ScaleMaterialMapper.weighed_date]

    # GET THE CURRENT ITEM COUNT
    cursor = db.cursor()
    sql_getstring = f'''SELECT count FROM raw_materials WHERE name="%s" ''' % (material_name)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    for tupleRecord in foundRecords:
        for item in tupleRecord:
            print(item, type(item))
    print(foundRecords)
    cursor.close()

    # INSERT NEW VALUES
    cursor = db.cursor()
    name = "testname2"
    company = 1
    count = 5
    sql = "INSERT INTO raw_materials (id,name,company,count) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(sql, (None, name, company, count))
        db.commit()
    except Exception as error:
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
    finally:
        cursor.close()

    exit()

    # sql_getstring = f"SELECT count FROM raw_materials WHERE name='%s'"
    # result = cursor.execute(_mysql.escape_string(sql_getstring))
    # print(result)
    # cursor.close()



    # response = app.response_class(
    #     response=json.dumps(data),
    #     status=200,
    #     mimetype='application/json'
    # )

def define_stock_material(data):
    db = GetMyDB()
    adi = data['adi']
    plu = data['plu']
    miktar = data['miktar']
    kritik_esik = data['kritik_esik']
    kategori = data['kategori']
    sirket = data['sirket']
    malzeme = data['malzeme']
    fiyat = data['fiyat']
    tedarikci = data['tedarikci']
    foto_id = data['foto_id']
    is_yari_urun = data['is_yari_urun']
    
    cursor = db.cursor()
    sql_getstring = '''SELECT * FROM wr_material_stock WHERE name="%s" OR plu_code="%s"'''
    cursor.execute(sql_getstring, (adi, plu))
    foundRecords = cursor.fetchall()
    for tupleRecord in foundRecords:
        for item in tupleRecord:
            print(item, type(item))
    print(foundRecords)
    cursor.close()

    print(len(foundRecords))

    if len(foundRecords) == 0:
        cursor = db.cursor()
        sql = "INSERT INTO wr_material_stock (id,name,plu_code,amount,critical_threshold,material_type,unit_price,category,company,provider_info,photo_guid,is_yari_urun) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(sql, (None, adi, plu, miktar, kritik_esik, malzeme, fiyat, kategori, sirket, tedarikci, foto_id, is_yari_urun))
            db.commit()
            cursor.close()
            db.close()

            sync_data = {
                "type": "insert",
                "table": "wr_material_stock",
                "sql_string": Utilities.encode_string(sql),
                "values": [[None, adi, plu, miktar, kritik_esik, malzeme, fiyat, kategori, sirket, tedarikci, foto_id, is_yari_urun]]
            }
            CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

            response_data = {"status" : "ok"}
        except Exception as error:
            LogError(error)
            cursor.close()
            print(f"Error While Inserting Data: {type(error).__name__} - {error}")
            response_data = {"status" : "error", "error_text" : {error}}      
    else:
        response_data = {"status" : "duplicate"}
    
    return response_data

def edit_stock_material(data):
    db = GetMyDB()

    fiyat_variable = data['fiyat']

    try:
        fiyat_variable = float(fiyat_variable)
    except:
        fiyat_variable = 0.0

    updated_data = {
        "id" : data['id'],
        "name" : data['adi'],
        "plu_code" : data['plu'],
        "amount" : float(data['miktar']),
        "critical_threshold" :  data['kritik_esik'],
        "material_type" : data['malzeme'],
        "unit_price" : fiyat_variable,
        "category" : data['kategori'],
        "company" : data['sirket'],
        "provider_info" : data['tedarikci'],
        "photo_guid" : data['foto_id'],
        "is_yari_urun": bool(data['is_yari_urun'])
    }

    
    cursor = db.cursor()
    sql_getstring = "SELECT * FROM wr_material_stock WHERE id = %s"
    cursor.execute(sql_getstring, (data["id"], ))
    original_record = cursor.fetchone()
    if original_record is None:
        cursor.close()
        db.close()
        return "Not Found"
    
    try:
        unit_price_variable = float(original_record[6])
    except:
        unit_price_variable = 0.0

    original_dict = {
        "id": original_record[0],
        "name" : original_record[1],
        "plu_code" : original_record[2],
        "amount" : float(original_record[3]),
        "critical_threshold" :  original_record[4],
        "material_type" : original_record[5],
        "unit_price" : unit_price_variable,
        "category" : original_record[7],
        "company" : original_record[8],
        "provider_info" : original_record[9],
        "photo_guid" : original_record[10],
        "is_yari_urun": bool(original_record[11])
    }
    
    changes = {}
    for key, value in updated_data.items():
        if str(original_dict[key]) != str(value):
            print(f"Not matched: {original_dict[key]}({type(original_dict[key])}) - {value}({type(value)})")
            changes[key] = {'old': original_dict[key], 'new': value}


    if not changes:
        cursor.close()
        db.close()
        return {"status": "no change"}


    update_parts = [f"{key} = %s" for key in updated_data.keys()]
    sql_update = f"UPDATE wr_material_stock SET {', '.join(update_parts)} WHERE id = %s"
    try:
        update_values = list(updated_data.values()) + [data["id"]]
        cursor.execute(sql_update, update_values)
        db.commit()

        sync_data = {
            "type": "update",
            "table": "wr_material_stock",
            "sql_string": Utilities.encode_string(sql_update),
            "values": [update_values]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)


        now = datetime.now()
        formatted_date = now.strftime("%d-%m-%Y %H:%M")




        sql_audit = "INSERT INTO wr_material_stock_logs (id, date, material_id, material_name, changes) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql_audit, (None, formatted_date, int(data["id"]), data["adi"], json.dumps(changes)))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "insert",
            "table": "wr_material_stock_logs",
            "sql_string": Utilities.encode_string(sql_audit),
            "values": [[None, formatted_date, int(data["id"]), data["adi"], json.dumps(changes)]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)



    except Exception as error:
        cursor.close()
        db.close()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        return f"Error|{error}"

    return {
        "status" : "ok"
    }

def get_materials(data):
    db = GetMyDB()
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_stock'''
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    data_list = []
    for tupleRecord in foundRecords:
        new_data = {
            "id" : tupleRecord[0], 
            "name" : tupleRecord[1],
            "plu_code" : tupleRecord[2],
            "amount" : tupleRecord[3],
            "critical_threshold" : tupleRecord[4],
            "material_type" : tupleRecord[5],
            "unit_price" : tupleRecord[6],
            "category" : tupleRecord[7],
            "company" : tupleRecord[8],
            "provider_info" : tupleRecord[9],
            "photo_guid" : tupleRecord[10],
            "is_yari_urun": tupleRecord[11]
        }

        data_list.append(new_data)

    cursor.close()
    db.close()
    
    final_data = {
        "result" : {
            "items" : data_list
        }
    }
    return final_data



def save_pdf_locally(base64_pdf_string, filename):
    try:
        images_folder = 'flask_files'
        wr_folder = "warehouse"
        malzeme_folder = "malzeme_teslim"

        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, images_folder, wr_folder, malzeme_folder)
        os.makedirs(folder_path, exist_ok=True)
        file_data = base64.b64decode(base64_pdf_string)
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        return True
        
    except Exception as error:
        Helpers.log_error_wr(error)
        return False

def get_pdf_locally(uuid):
    try:
        images_folder = 'flask_files'
        wr_folder = "warehouse"
        malzeme_folder = "malzeme_teslim"

        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, images_folder, wr_folder, malzeme_folder)
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"{uuid}.pdf")
        with open(file_path, 'rb') as f:
            pdf_content = f.read()
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            return pdf_base64
        
    except Exception as error:
        Helpers.log_error_wr(error)
        return False


def add_material_delivery(data):
    date_string = data["date_string"]
    hour_string = data["hour_string"]
    teslim_alan = data["teslim_alan"]
    malzemeler = data["malzemeler"]
    rapor_uuid = data["rapor_uuid"]
    company_name = data["company_name"]

    db = GetMyDB()
    cursor = db.cursor()

    #region STEP 1 - Save Delivery to Database

    sql = "INSERT INTO wr_material_delivery (id,date,hour,taker,items,report_uuid,company_name) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(sql, (None, date_string, hour_string, teslim_alan, json.dumps(malzemeler), rapor_uuid, company_name))
        db.commit()

        sync_data = {
            "type": "insert",
            "table": "wr_material_delivery",
            "sql_string": Utilities.encode_string(sql),
            "values": [[None, date_string, hour_string, teslim_alan, json.dumps(malzemeler), rapor_uuid, company_name]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

    except Exception as error:
        Helpers.log_error_wr(str(error))
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
        return response_data

    #endregion


    #region STEP 2 - Drop Stock of Delivered Materials From Database

    for malzeme in malzemeler:
        malzeme_id = malzeme["id"]
        malzeme_adi = malzeme["adi"]
        teslim_edilen_miktar = float(malzeme["miktar"])

        sql_getstring = "SELECT * FROM wr_material_stock WHERE id = %s"
        cursor.execute(sql_getstring, (malzeme_id, ))
        original_record = cursor.fetchone()
        if original_record is None:
            cursor.close()
            db.close()
            return "Not Found"

        try:
            unit_price_variable = float(original_record[6])
        except:
            unit_price_variable = 0.0
        original_dict = {
            "id": original_record[0],
            "name" : original_record[1],
            "plu_code" : original_record[2],
            "amount" : float(original_record[3]),
            "critical_threshold" :  original_record[4],
            "material_type" : original_record[5],
            "unit_price" : unit_price_variable,
            "category" : original_record[7],
            "company" : original_record[8],
            "provider_info" : original_record[9],
            "photo_guid" : original_record[10],
            "is_yari_urun": original_record[11]
        }

        current_miktar = original_dict["amount"]
        new_miktar = current_miktar - teslim_edilen_miktar

        sql_update = "UPDATE wr_material_stock SET amount = %s WHERE id = %s"
        try:
            cursor.execute(sql_update, (new_miktar, malzeme_id))
            db.commit()
            sync_data = {
                "type": "update",
                "table": "wr_material_stock",
                "sql_string": Utilities.encode_string(sql_update),
                "values": [[new_miktar, malzeme_id]]
            }
            CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        except Exception as error:
            print(traceback.format_exc())
            Helpers.log_error_material_delivery(str(error), f"malzeme_id: {malzeme_id}, old_miktar: {current_miktar}, teslim_edilen_miktar: {teslim_edilen_miktar}", "update_counts")


        try:
            changes = {
                "amount" : {"old": current_miktar, "new": new_miktar}
            }
            now = datetime.now()
            formatted_date = now.strftime("%d-%m-%Y %H:%M")
            sql_audit = "INSERT INTO wr_material_stock_logs (id, date, material_id, material_name, changes) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql_audit, (None, formatted_date, int(malzeme_id), malzeme_adi, json.dumps(changes)))
            db.commit()
            sync_data = {
                "type": "insert",
                "table": "wr_material_stock_logs",
                "sql_string": Utilities.encode_string(sql_audit),
                "values": [[new_miktar, malzeme_id]]
            }
            CloudRequests.Save_New_Cloud_Sync_Task(sync_data)
        except Exception as error:
            print(traceback.format_exc())
            Helpers.log_error_material_delivery(str(error), sync_data, "save_audit_logs")

    #endregion
    

    #region STEP 3 - Create, Save PDF Locally and Return a Copy in Bytes Format
    
    pdf_result = Printer_Master.print_material_delivery_report(malzemeler, teslim_alan)
    if pdf_result["status"] == "ok":
        pdf_bytes = pdf_result["pdf_bytes"]
        rapor_save_result = save_pdf_locally(pdf_bytes, f"{rapor_uuid}.pdf")
    else:
        pdf_bytes = ""

    #endregion
    try:
        cursor.close()
        db.close()
    except:
        pass
    

    response_data = {
        "status" : "ok",
        "rapor_b64string" : pdf_bytes
    }


    return response_data

def get_material_delivery_history():
    db = GetMyDB()
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_delivery'''
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    data_list = []
    for tupleRecord in foundRecords:
        new_data = {
            "id" : tupleRecord[0], 
            "date" : tupleRecord[1],
            "hour" : tupleRecord[2],
            "teslim_alan" : tupleRecord[3],
            "malzemeler" : json.loads(tupleRecord[4]),
            "report_uuid" : tupleRecord[5],
            "sirket": tupleRecord[6]
        }
        data_list.append(new_data)

    cursor.close()
    db.close()
    
    final_data = {
        "result" : {
            "items" : data_list
        }
    }
    return final_data

def get_largest_plu():
    db = GetMyDB()
    cursor = db.cursor()
    sql_getstring = f'''SELECT MAX(plu_code) FROM wr_material_stock'''
    cursor.execute(sql_getstring)
    foundRecord = cursor.fetchone()
    if foundRecord and foundRecord[0]:
        final_data = {
            "status" : "ok",
            "data" : foundRecord[0]
        }
    else:
        final_data = {
            "status" : "not_found"
        }

    cursor.close()
    db.close()

    return final_data