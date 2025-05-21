from flask import Flask, Request, jsonify
import mysql.connector, mysql, json, traceback, logging, requests, calendar, pprint
from MySQLdb import _mysql
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from datetime import datetime, timedelta
from hijri_converter import convert

from config_setter import DEVICE_URL


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

#region ID GETTERS WITH NAME

def Internal_Get_Employee_Department_ID(department_name):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT id FROM hr_departments WHERE department_name="%s" ''' % (department_name)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return int(foundRecords[0][0])
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_SubDepartment_ID(sub_department_name):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT id FROM hr_sub_departments WHERE sub_department_name="%s" ''' % (sub_department_name)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return int(foundRecords[0][0])
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_Profession_ID(profession_name):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT id FROM hr_professions WHERE profession_name="%s" ''' % (profession_name)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return int(foundRecords[0][0])
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_Company_ID(company_name):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT id FROM general_companies WHERE company_name="%s" ''' % (company_name)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return int(foundRecords[0][0])
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_ShiftGroup_ID(shift_name):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT id FROM hr_workshifts WHERE workshift_name='%s' ''' % (shift_name)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return int(foundRecords[0][0])
        else:
            print("NO RECORDS")
    except Exception as error:
        LogError(error)

#endregion


#region NAME GETTERS WITH ID

def Internal_Get_Employee_Department_Name(department_id):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT department_name FROM hr_departments WHERE id="%s" ''' % (department_id)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0][0]
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_SubDepartment_Name(sub_department_id):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT sub_department_name FROM hr_sub_departments WHERE id="%s" ''' % (sub_department_id)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0][0]
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_Profession_Name(profession_id):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT profession_name FROM hr_professions WHERE id="%s" ''' % (profession_id)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0][0]
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_Company_Name(comany_id):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT company_name FROM general_companies WHERE id="%s" ''' % (comany_id)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0][0]
        else:
            return None
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_Workshift_Name(workshift_id):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT workshift_name FROM hr_workshifts WHERE id="%s" ''' % (workshift_id)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0][0]
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_Workshift_Details(workshift_id):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_workshifts WHERE id="%s" ''' % (workshift_id)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0]
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_PartTime_Info(employee_register_number):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT part_time FROM hr_employee_info WHERE employee_register_number="%s" ''' % employee_register_number
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0]
    except Exception as error:
        LogError(error)

#endregion


#region OTHER GETTERS

def Internal_Get_Employee_Attendance_From_Device():
    try:
        request_data = {
            "request" : "GetAttendanceData"
        }
        device_result = requests.post(DEVICE_URL, json=request_data)
        result_json = device_result.json()
    except Exception as error:
        result_json = {
            "ret" : "connection_error",
            "error_text" : str(error)
        }

    return result_json

def Internal_Get_Workshift_ID_With_Card_Number(card_number):
    db = GetMyDB()
    try:
        cursor = db.cursor()
        query = f'''SELECT employee_workshift_id FROM hr_employee_info WHERE employee_register_number="%s" ''' % (card_number)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0][0]
        else:
            return None
    except Exception as error:
        LogError(error)

def Internal_Get_Workshift_Exit_Hour_String_With_Workshift_ID(workshift_id):
    db = GetMyDB()
    try:
        cursor = db.cursor()
        query = f'''SELECT workshift_end FROM hr_workshifts WHERE id="%s" ''' % (workshift_id)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0][0]
        else:
            return None
    except Exception as error:
        LogError(error)
        return None

def Internal_Get_Workshift_Entry_Hour_String_With_Workshift_ID(workshift_id):
    db = GetMyDB()
    try:
        cursor = db.cursor()
        query = f'''SELECT workshift_start FROM hr_workshifts WHERE id="%s" ''' % (workshift_id)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0][0]
        else:
            return None
    except Exception as error:
        LogError(error)
        return None

def Internal_Get_Employee_Name_Surname_Company_With_Card_Number(card_number):
    db = GetMyDB()
    try:
        cursor = db.cursor()
        query = f'''SELECT employee_name, employee_surname, employee_company_id FROM hr_employee_info WHERE employee_register_number="%s" ''' % (card_number)
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            return foundRecords[0]
        else:
            return None
    except Exception as error:
        LogError(error)

def Internal_Get_Employee_Paid_Vacations(employee_name, employee_surname, year, month):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_vacations_permissions WHERE 
        employee_name="%s" AND 
        employee_surname="%s" AND 
        YEAR(vacation_start)="%s" AND
        MONTH(vacation_start)="%s" ''' % (employee_name, employee_surname, year, month)

        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close(); db.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {
                    "id" : tupleRecord[0],
                    "name" : tupleRecord[1],
                    "surname" : tupleRecord[2],
                    "vacation_start" : tupleRecord[3],
                    "vacation_end" : tupleRecord[4]
                    }
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    return final_data

def Internal_Get_Employee_Advance_Payments_Month(employee_name, employee_surname, year, month):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_payments_advance WHERE 
        employee_name="%s" AND 
        employee_surname="%s" AND 
        YEAR(payment_date)="%s" AND
        MONTH(payment_date)="%s" ''' % (employee_name, employee_surname, year, month)

        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close(); db.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {
                    "id" : tupleRecord[0],
                    "name" : tupleRecord[1],
                    "surname" : tupleRecord[2],
                    "payment_amount" : tupleRecord[3],
                    "payment_date" : tupleRecord[4]
                    }
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    return final_data


def Internal_Get_Nightshift_Employee_Previous_Day_Entry(user_id, min_time, max_time):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT entry_date FROM hr_employee_attendance WHERE 
        employee_register_number="%s" AND 
        device_user_id="%s" AND 
        entry_date BETWEEN "%s" AND "%s" 
        ORDER BY entry_date ASC LIMIT 1 ''' % (user_id, user_id, min_time, max_time)

        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close(); db.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                return str(tupleRecord[0])
        else:
            return None

    except Exception as error:
        LogError(error)
        return None

def Internal_Get_Nightshift_Employee_Next_Morning_Exit(user_id, min_time, max_time):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT entry_date FROM hr_employee_attendance WHERE 
        employee_register_number="%s" AND 
        device_user_id="%s" AND 
        entry_date BETWEEN "%s" AND "%s" 
        ORDER BY entry_date DESC LIMIT 1 ''' % (user_id, user_id, min_time, max_time)

        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close(); db.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                return str(tupleRecord[0])
        else:
            return None

    except Exception as error:
        LogError(error)
        return None

def Internal_Get_Morning_Workshift_Hours():
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_workshifts WHERE workshift_name LIKE %s '''

        search_string_with_wildcard = f"%gündüz%"
        cursor.execute(query, (search_string_with_wildcard, ))

        foundRecords = cursor.fetchall(); cursor.close(); db.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {
                    "id" : tupleRecord[0],
                    "workshift_name" : tupleRecord[1],
                    "workshift_start" : tupleRecord[2],
                    "workshift_end" : tupleRecord[3],
                    "break_start" : tupleRecord[4],
                    "break_end" : tupleRecord[5],
                    "entry_tolerance" : tupleRecord[6],
                    "exit_tolerance" : tupleRecord[7],
                    }
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    return final_data

def Internal_Get_Night_Workshift_Hours():
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_workshifts WHERE workshift_name LIKE %s '''

        search_string_with_wildcard = f"%night%"
        cursor.execute(query, (search_string_with_wildcard, ))

        foundRecords = cursor.fetchall(); cursor.close(); db.close()
        data_list = []

        if len(foundRecords) > 0:
            for tupleRecord in foundRecords:
                new_data = {
                    "id" : tupleRecord[0],
                    "workshift_name" : tupleRecord[1],
                    "workshift_start" : tupleRecord[2],
                    "workshift_end" : tupleRecord[3],
                    "break_start" : tupleRecord[4],
                    "break_end" : tupleRecord[5],
                    "entry_tolerance" : tupleRecord[6],
                    "exit_tolerance" : tupleRecord[7],
                    }
                data_list.append(new_data)

            final_data = {"status" : "ok", "error_text" : None, "data" : data_list}
        else:
            final_data = {"status" : "not_found", "error_text" : None, "data" : []}

    except Exception as error:
        LogError(error)
        final_data = {"status" : "error", "error_type" : "unknown", "error_text" : error, "data" : []}

    return final_data


#endregion




def Internal_GetALL_Employee_Infos():
    db = GetMyDB()
    returnData = []
    try:
        cursor = db.cursor()
        query = f'''SELECT employee_name, employee_surname, employee_company_id, employee_register_number, employee_workshift_id FROM hr_employee_info'''
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            # print(foundRecords[0])
            for record in foundRecords:
                data = {
                    "employee_name": record[0],
                    "employee_surname": record[1],
                    "employee_company_id": record[2],
                    "employee_register_number": record[3],
                    "employee_workshift_id": record[4]
                }
                returnData.append(data)
        else:
            pass
        return returnData
    except Exception as error:
        LogError(error)
        return None


def Internal_GetAll_Company_Names():
    returnData = []
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT * FROM general_companies'''
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            for record in foundRecords:
                data = {
                    "company_id": record[0],
                    "company_name": record[1]
                }
                returnData.append(data)
            return returnData
        else:
            return None
    except Exception as error:
        LogError(error)


def Internal_GetAll_Workshift_Names():
    returnData = []
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_workshifts'''
        cursor.execute(query)
        foundRecords = cursor.fetchall()
        cursor.close()
        db.close()
        if len(foundRecords) > 0:
            for record in foundRecords:
                data = {
                    "workshift_id": record[0],
                    "workshift_name": record[1]
                }
                returnData.append(data)
            return returnData
        else:
            return None
    except Exception as error:
        LogError(error)