
import traceback, os, base64, json
from libs import LocalRequests, CloudRequests, Utilities
from datetime import date
from libs.Helpers import log_error_wr
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


async def get_logged_used_sheets():
    try:
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM wr_logs_lazer_stock'''
        cursor.execute(sql_getstring)
        foundRecords = cursor.fetchall(); cursor.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {
                    "id" : tupleRecord[0],
                    "date" : tupleRecord[1],
                    "material_type" : tupleRecord[2],
                    "sheet_size" : tupleRecord[3],
                    "thickness" : tupleRecord[4],
                    "sheet_count" : tupleRecord[5],
                    "is_fason" : tupleRecord[6],
                    "instance_number" : tupleRecord[7],
                    "is_subtracted" : tupleRecord[8]
                }
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    return final_data


async def check_and_insert_stock_drop_logs(data_dict):
    response_data = {"update_count" : 0}
    data_list = data_dict["daily_reports"]
    for data in data_list:
        date_string = data["date"]
        is_fason = data["is_fason"]
        instance_number = data["instance_number"]
        material_type = data["material_type"]
        sheet_size = data["sheet_size"]
        thickness = data["thickness"]
        sheet_count = 0
        for item in data["used_sheets"]:
            sheet_count += item["sheet_count"]
        is_subtracted = bool(data["is_subtracted"])
        db = GetMyDB()
        cursor = db.cursor()

        if (material_type == "DKP" and float(str(thickness).lower().replace("mm","")) > 2):
            material_type = "SYH"

        # Check if already added

        print("debug")
        print(f"{date_string} {material_type} {sheet_size} {thickness} {sheet_count} {is_fason} {instance_number} 1")
        print("debug")

        try:
            sql_getstring = """
            SELECT * FROM wr_logs_lazer_stock
            WHERE date = %s AND material_type = %s AND sheet_size = %s AND thickness = %s AND sheet_count = %s AND is_fason = %s AND instance_number = %s
            """
            cursor.execute(sql_getstring, (date_string, material_type, sheet_size, thickness, sheet_count, int(is_fason), instance_number))
            foundRecords = cursor.fetchall()

            if len(foundRecords) > 0:
                print("Already added to DB")
                continue

        except Exception as error:
            LogError(error)
    
        try:
            sql = '''INSERT INTO wr_logs_lazer_stock (id, date, material_type, sheet_size, thickness, sheet_count, is_fason, instance_number, is_subtracted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            execution_tuple = (None, date_string, material_type, sheet_size, thickness, sheet_count, is_fason, instance_number, is_subtracted)
            cursor.execute(sql, execution_tuple)
            db.commit()
            cursor.close()
            db.close()

            sync_data = {
                "type": "insert",
                "table": "wr_logs_lazer_stock",
                "sql_string": Utilities.encode_string(sql),
                "values": [[None, date_string, material_type, sheet_size, thickness, sheet_count, is_fason, instance_number, is_subtracted]]
            }
            CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

            response_data["update_count"] += 1
        except Exception as error:
            LogError(error)
            cursor.close()
            db.rollback()
            db.close()
            print(f"Error While Inserting Data: {type(error).__name__} - {error}")
            response_data = {"update_count" : "error", "error_text" : {error}}
    try:   
        cursor.close()
        db.close()
    except:
        pass
    return response_data


async def update_new_material_count(id, old_amount, new_amount):
    db = GetMyDB()
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_stock WHERE id="%s" ''' % id
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f"UPDATE wr_material_stock SET amount=%s WHERE id = %s"
    try:
        cursor.execute(sql, (new_amount, id))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "update",
            "table": "wr_material_stock",
            "sql_string": Utilities.encode_string(sql),
            "values": [[new_amount, id]]
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

async def set_log_subtracted(id):

    db = GetMyDB()
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_logs_lazer_stock WHERE id="%s" ''' % id
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        return {"status" : "not_found"}
    
    cursor = db.cursor()
    sql = f"UPDATE wr_logs_lazer_stock SET is_subtracted=%s WHERE id = %s"
    try:
        cursor.execute(sql, (True, id))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "update",
            "table": "wr_logs_lazer_stock",
            "sql_string": Utilities.encode_string(sql),
            "values": [[True, id]]
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

async def log_the_update(material_data, old_amount, new_amount):
    mat_name = material_data["name"]
    data = {
        "date": str(datetime.now()),
        "name": mat_name,
        "old_amount": old_amount,
        "new_amount": new_amount
    }

    with open("auto_report_logs.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    json_data.append(data)
    with open("auto_report_logs.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    return "logged the change to auto_report_logs.json"

async def Update_Stock_Counts():
    all_logs = await get_logged_used_sheets()

    if all_logs["status"] != "ok":
        print(all_logs)
        return

    for log in all_logs["data"]:
        if bool(log["is_subtracted"]) == True:
            continue

        log_id = log["id"]
        sac_turu = log["material_type"]
        is_fason = bool(log["is_fason"])
        thickness = log["thickness"]
        sheet_count = log["sheet_count"]
        sheet_size = str(log["sheet_size"])

        sheet_size = sheet_size.replace("x","*")

        if sac_turu.lower() == "glv":
            tur_adi = "GALVANİZ"
        elif sac_turu.lower() == "syh":
            tur_adi = "SİYAH"
        elif sac_turu.lower() == "dkp":
            tur_adi = "DKP"
        elif sac_turu.lower() == "psl":
            tur_adi = "PASLANMAZ"
        
        try:
            if (float(str(thickness).replace("MM","")) > 2 and tur_adi == "DKP"):
                tur_adi = "SİYAH"
        except Exception as error:
            LogError(error)
        
        if is_fason == True:
            target_name = f"(FASON) {thickness} {tur_adi} SAC-{sheet_size}"
        elif is_fason == False:
            target_name = f"{thickness} {tur_adi} SAC-{sheet_size}"
        
        db = GetMyDB()
        cursor = db.cursor()
        sql_getstring = f'''SELECT * FROM wr_material_stock WHERE name="%s"''' % target_name
        try:
            cursor.execute(sql_getstring)
            foundRecord = cursor.fetchone(); cursor.close(); db.close()
            if foundRecord:
                material_data = {
                    "id" : foundRecord[0],
                    "name" : foundRecord[1],
                    "plu_code" : foundRecord[2],
                    "amount" : foundRecord[3],
                    "critical_threshold" : foundRecord[4],
                    "materia_type" : foundRecord[5],
                    "unit_price" : foundRecord[6],
                    "category" : foundRecord[7],
                    "company" : foundRecord[8],
                    "provider_info" : foundRecord[9]
                }
                amount = material_data["amount"]
                new_amount = amount - sheet_count
                result = await update_new_material_count(material_data["id"], amount, new_amount)
                result2 = await set_log_subtracted(log_id)
                result_log = await log_the_update(material_data, amount, new_amount)

                print(result)
                print(result2)
                print(result_log)

        except Exception as error:
            LogError(error)




def get_report_file(file_name, date_string):
    file_name = file_name.replace("MM","mm")
    try:
        reports_path = os.path.join("H:", "Diğer bilgisayarlar", "Dizustu Bilgisayarim", "BODOR LAZER", "RAPORLAR")

        date_parts = date_string.split("-")

        year_part = date_parts[2]
        year_path = os.path.join(reports_path, year_part)

        month_part = date_parts[1]
        month_path = os.path.join(year_path, month_part)

        day_part = date_parts[0]
        day_path = os.path.join(month_path, day_part)

        file_path = os.path.join(day_path, f"{file_name}.pdf")

        with open(file_path, 'rb') as f:
            pdf_content = f.read()
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            response = {
                "status": "ok", 
                "result": {
                    "b64pdf" : pdf_base64
                }
            }
            return response
    except Exception as error:
        log_error_wr(error)
        response = {"status" : "error", "error_text": str(error)}
    
    return response