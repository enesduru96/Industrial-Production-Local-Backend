
import traceback
from libs import LocalRequests
from libs.Helpers import ScaleMaterialMapper

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass

def GetMyDB():
    db = LocalRequests.get_my_db()
    return db


def Handle_Scale_Weighed_Materials(data):
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



def Handle_Define_Stock_Material(data):
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
    
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_stock WHERE name="%s" OR plu_code="%s"''' % (adi, plu)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    for tupleRecord in foundRecords:
        for item in tupleRecord:
            print(item, type(item))
    print(foundRecords)
    cursor.close()

    print(len(foundRecords))

    if len(foundRecords) == 0:
        cursor = db.cursor()
        sql = "INSERT INTO wr_material_stock (id,name,plu_code,amount,critical_threshold,material_type,unit_price,category,company,provider_info,photo_guid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(sql, (None, adi, plu, miktar, kritik_esik, malzeme, fiyat, kategori, sirket, tedarikci, foto_id))
            db.commit()
            cursor.close()
            response_data = {"status" : "ok"}
        except Exception as error:
            LogError(error)
            cursor.close()
            print(f"Error While Inserting Data: {type(error).__name__} - {error}")
            response_data = {"status" : "error", "error_text" : {error}}      
    else:
        response_data = {"status" : "duplicate"}
    
    return response_data

def Handle_Edit_Stock_Material(data):
    db = GetMyDB()
    id = data['id']
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
    
    cursor = db.cursor()
    sql_getstring = f'''SELECT * FROM wr_material_stock WHERE id="%s" ''' % (id)
    cursor.execute(sql_getstring)
    foundRecords = cursor.fetchall()
    for tupleRecord in foundRecords:
        for item in tupleRecord:
            print(item, type(item))
    print(foundRecords)
    cursor.close()

    print(len(foundRecords))

    if len(foundRecords) <= 0:
        return "Not Found"
            
    else:
        cursor = db.cursor()
        already_count = foundRecords[0][0]
        print(f"Already Saved: {already_count}")

        sql = f"UPDATE wr_material_stock SET name = %s, plu_code = %s, amount = %s, critical_threshold = %s, material_type = %s, unit_price = %s, category = %s, company = %s, provider_info = %s, photo_guid = %s WHERE id = %s"
        try:
            cursor.execute(sql, (adi, plu, miktar, kritik_esik, malzeme, fiyat, kategori, sirket, tedarikci, foto_id, id))
            db.commit()
            cursor.close()
            db.close()
        except Exception as error:
            cursor.close()
            db.close()
            print(f"Error While Inserting Data: {type(error).__name__} - {error}")
            return f"Error|{error}"

        return {
            "status" : "ok"
        }

def Handle_Get_Stock(data):
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

def Get_Largest_PLU():
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