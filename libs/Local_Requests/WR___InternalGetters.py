from flask import Flask, Request, jsonify
import mysql.connector, mysql, json, traceback, logging, requests, calendar, pprint
from MySQLdb import _mysql
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from datetime import datetime, timedelta
from hijri_converter import convert

from config_setter import DEVICE_URL


from libs import LocalRequests

from libs.Helpers import log_error_wr

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass


def GetMyDB():
    db = LocalRequests.get_my_db()
    return db

def Internal_Get_Hammadde_ID_With_Name(hammadde_name):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = '''SELECT * FROM wr_material_stock WHERE 
        name = %s'''

        cursor.execute(query, (hammadde_name,)); found_record = cursor.fetchone()
        data_list = []

        if found_record:
            return found_record[0]
        else:
            return False

    except Exception as error:
        log_error_wr(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    try:
        cursor.close()
        db.close()
    except:
        pass

    return final_data

def Internal_Get_Urun_ID_With_Name(urun_name):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = "SELECT * FROM wr_products WHERE product_name = %s"

        cursor.execute(query, (urun_name,)); found_record = cursor.fetchone()
        data_list = []

        if found_record:
            return found_record[0]
        else:
            return False

    except Exception as error:
        log_error_wr(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    try:
        cursor.close()
        db.close()
    except:
        pass

    return final_data