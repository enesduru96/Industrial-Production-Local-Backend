
from flask import Flask, Request, jsonify
import mysql.connector, mysql, json, traceback, logging, requests, calendar, pprint
from MySQLdb import _mysql
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from datetime import datetime, timedelta
from hijri_converter import convert

from config_setter import DEVICE_URL
from sqlalchemy.exc import OperationalError


from libs import Helpers
from libs.Helpers import ScaleMaterialMapper

from libs import LocalRequests, CloudRequests, Utilities

from libs.Local_Requests import HR_InternalGetters, HR_AttendanceHandler

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass


def GetMyDB():
    db = LocalRequests.get_my_db()
    return db

def Get_Employees_From_Database(data):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = f'''SELECT * FROM hr_employee_info'''
        cursor.execute(query); foundRecords = cursor.fetchall(); cursor.close()

        total_rows = []
        if len(foundRecords) > 0:
            for row in foundRecords:
                employee_id =                       row[0]
                employee_name =                     row[1]
                employee_surname =                  row[2]
                employee_register_number =          row[3]
                employee_date_of_employment =       row[4]
                employee_shift_group_id =           row[5]
                employee_salary =                   row[6]
                employee_salary_hourly =            row[7]
                employee_address =                  row[8]
                employee_notes =                    row[9]
                employee_department_id =            row[10]
                employee_sub_department_id =        row[11]
                employee_profession_id =            row[12]
                employee_company_id =               row[13]
                employee_ssk_number =               row[14]
                employee_personnel_file_uuid =      row[15]
                employee_photo_file_uuid =          row[16]
                employee_left =                     row[17]
                employee_leave_date =               row[18]
                employee_leave_reason =             row[19]
                employee_part_time =                row[20]

                employee_shift_group_name =         HR_InternalGetters.Internal_Get_Employee_Workshift_Name(employee_shift_group_id)
                employee_department_name =          HR_InternalGetters.Internal_Get_Employee_Department_Name(employee_department_id)
                employee_sub_department_name =      HR_InternalGetters.Internal_Get_Employee_SubDepartment_Name(employee_sub_department_id)
                employee_profession_name =          HR_InternalGetters.Internal_Get_Employee_Profession_Name(employee_profession_id)
                employee_company_name =             HR_InternalGetters.Internal_Get_Employee_Company_Name(employee_company_id)

                date_app_string = employee_date_of_employment.strftime('%d.%m.%Y')

                row_data = {
                    "id" :                  employee_id,
                    "name" :                employee_name,
                    "surname" :             employee_surname,
                    "register_number" :     employee_register_number,
                    "date_of_employment" :  date_app_string,
                    "shift_group_id" :      employee_shift_group_id,
                    "shift_group_name" :    employee_shift_group_name,
                    "salary":               employee_salary,
                    "salary_hourly":        employee_salary_hourly,
                    "address" :             employee_address,
                    "notes" :               employee_notes,
                    "department_id" :       employee_department_id,
                    "department_name" :     employee_department_name,
                    "sub_department_id" :   employee_sub_department_id,
                    "sub_department_name" : employee_sub_department_name,
                    "profession_id" :       employee_profession_id,
                    "profession_name" :     employee_profession_name,
                    "company_id" :          employee_company_id,
                    "company_name" :        employee_company_name,
                    "ssk_number" :          employee_ssk_number,
                    "personnel_file_uuid" : employee_personnel_file_uuid,
                    "photo_file_uuid" :     employee_photo_file_uuid,
                    "left" :                employee_left,
                    "leave_date" :          employee_leave_date,
                    "leave_reason" :        employee_leave_reason,
                    "part_time" :           employee_part_time
                }
                total_rows.append(row_data)


            response_data = {"status" : "ok", "result_rows" : total_rows}
        else:
            response_data = {"status" : "not_found"}

    except Exception as error:
        LogError(error)
        try:
            cursor.close()
            db.close()
        except:
            pass
        print(f"Error While Getting Employees: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
   
    try:db.close()
    except:pass 
    return response_data

def Get_Absent_Employees_From_Database_Today(data):
    try:
        all_employees = Get_Employees_From_Database("")
        employee_count = len(all_employees['result_rows'])
        total_employees = []
        for employee in all_employees['result_rows']:
            if employee["left"] == "false":
                employee_data = {"name" : employee["name"], "surname" : employee["surname"]}
                total_employees.append(employee_data)

        today = datetime.now().date()
        start_timestamp = datetime.combine(today, datetime.min.time())
        end_timestamp = datetime.combine(today, datetime.max.time())
        start_timestamp_str = start_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        end_timestamp_str = end_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        attendance_conditions = {
            "type" : "attendance_general2",
            "start_date_string" : start_timestamp_str,
            "end_date_string" : end_timestamp_str
        }
        today_attendance_data = HR_AttendanceHandler.Get_Employee_Attendance_From_Database(attendance_conditions)

        attended_employees = []
        if today_attendance_data["status"] == "ok":
            for item in today_attendance_data["result"]:
                employees = today_attendance_data["result"][item]
                for employee in employees:
                    employee_data = {"name" : employee["employee_name"], "surname" : employee["employee_surname"]}
                    attended_employees.append(employee_data)
                    
        
            absent_employees = [employee for employee in total_employees if employee not in attended_employees]

            response_data = {
                "status" : "ok",
                "total_workers" : len(total_employees),
                "absent_workers" : len(absent_employees),
                "result_rows" : absent_employees
            }

            pprint.pprint(response_data, sort_dicts=False)

            return response_data

        
        response_data = {"status" : "not_found"}
        

    except Exception as error:
        LogError(error)
        # cursor.close()
        print(f"Error While Getting Employees: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    
    return response_data

def Get_Specific_Employee_From_Database(employee_register_number):
    try:
        db = GetMyDB()
        cursor = db.cursor()
        query = "SELECT * FROM hr_employee_info WHERE employee_register_number = %s"
        cursor.execute(query, (str(employee_register_number), )); foundRecords = cursor.fetchall(); cursor.close()

        total_rows = []
        if len(foundRecords) > 0:
            for row in foundRecords:
                employee_id =                       row[0]
                employee_name =                     row[1]
                employee_surname =                  row[2]
                employee_register_number =          row[3]
                employee_date_of_employment =       row[4]
                employee_shift_group_id =           row[5]
                employee_salary =                   row[6]
                employee_salary_hourly =            row[7]
                employee_address =                  row[8]
                employee_notes =                    row[9]
                employee_department_id =            row[10]
                employee_sub_department_id =        row[11]
                employee_profession_id =            row[12]
                employee_company_id =               row[13]
                employee_ssk_number =               row[14]
                employee_personnel_file_uuid =      row[15]
                employee_photo_file_uuid =          row[16]
                employee_left =                     row[17]
                employee_leave_date =               row[18]
                employee_leave_reason =             row[19]
                employee_part_time =                row[20]

                employee_shift_group_name =         HR_InternalGetters.Internal_Get_Employee_Workshift_Name(employee_shift_group_id)
                employee_department_name =          HR_InternalGetters.Internal_Get_Employee_Department_Name(employee_department_id)
                employee_sub_department_name =      HR_InternalGetters.Internal_Get_Employee_SubDepartment_Name(employee_sub_department_id)
                employee_profession_name =          HR_InternalGetters.Internal_Get_Employee_Profession_Name(employee_profession_id)
                employee_company_name =             HR_InternalGetters.Internal_Get_Employee_Company_Name(employee_company_id)

                date_app_string = employee_date_of_employment.strftime('%d.%m.%Y')

                row_data = {
                    "id" :                  employee_id,
                    "name" :                employee_name,
                    "surname" :             employee_surname,
                    "register_number" :     employee_register_number,
                    "date_of_employment" :  date_app_string,
                    "shift_group_id" :      employee_shift_group_id,
                    "shift_group_name" :    employee_shift_group_name,
                    "salary":               employee_salary,
                    "salary_hourly":        employee_salary_hourly,
                    "address" :             employee_address,
                    "notes" :               employee_notes,
                    "department_id" :       employee_department_id,
                    "department_name" :     employee_department_name,
                    "sub_department_id" :   employee_sub_department_id,
                    "sub_department_name" : employee_sub_department_name,
                    "profession_id" :       employee_profession_id,
                    "profession_name" :     employee_profession_name,
                    "company_id" :          employee_company_id,
                    "company_name" :        employee_company_name,
                    "ssk_number" :          employee_ssk_number,
                    "personnel_file_uuid" : employee_personnel_file_uuid,
                    "photo_file_uuid" :     employee_photo_file_uuid,
                    "left" :                employee_left,
                    "leave_date" :          employee_leave_date,
                    "leave_reason" :        employee_leave_reason,
                    "part_time" :           employee_part_time
                }
                total_rows.append(row_data)


            response_data = {"status" : "ok", "result_rows" : total_rows}
        else:
            response_data = {"status" : "not_found"}

    except Exception as error:
        LogError(error)
        cursor.close()
        print(f"Error While Getting Employees: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    try:db.close()
    except:pass 
    return response_data

def Add_Employee_To_Database(data):
    db = GetMyDB()

    employee_name =                     data['employee_name']
    employee_surname =                  data['employee_surname']
    employee_register_number =          data['employee_card_register_number']
    employee_date_of_employment =       data['employee_date_of_employment']
    employee_shift_group =              data['employee_shift_group']
    employee_salary =                   data['employee_salary']
    employee_salary_hourly =            data['employee_salary_hourly']
    employee_address =                  data['employee_address']
    employee_notes =                    data['employee_notes']
    employee_department_string =        data['employee_department']
    employee_sub_department_string =    data['employee_sub_department']
    employee_profession_string =        data['employee_profession']
    employee_company_string =           data['employee_company']
    employee_ssk_number =               data['employee_ssk_number']
    employee_personnel_file_uuid =      data['employee_personnel_file_uuid']
    employee_photo_file_uuid =          data['employee_photo_file_uuid']
    employee_left =                     data['employee_left']
    employee_leave_date =               data['employee_leave_date']
    employee_leave_reason =             data['employee_leave_reason']
    employee_part_time =                data['employee_part_time']

    print(data["employee_part_time"])
    print(employee_part_time)

    employee_shift_group_id =       HR_InternalGetters.Internal_Get_Employee_ShiftGroup_ID(employee_shift_group)
    employee_department_id =        HR_InternalGetters.Internal_Get_Employee_Department_ID(employee_department_string)
    employee_sub_department_id =    HR_InternalGetters.Internal_Get_Employee_SubDepartment_ID(employee_sub_department_string)
    employee_profession_id =        HR_InternalGetters.Internal_Get_Employee_Profession_ID(employee_profession_string)
    employee_company_id =           HR_InternalGetters.Internal_Get_Employee_Company_ID(employee_company_string)
    

    dt_obj = datetime.strptime(employee_date_of_employment, '%d.%m.%Y')
    mysql_employment_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_employee_info WHERE employee_register_number="%s" ''' % (employee_register_number)
    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) > 0:
        name = foundRecords[0][1]
        surname = foundRecords[0][2]
        response_data = {"status" : "duplicate", "owner" : f"{name} {surname}"}
        return response_data
    
    cursor = db.cursor()
    sql = '''INSERT INTO hr_employee_info (
        id, employee_name, employee_surname,
        employee_register_number, employee_start_date, employee_workshift_id,
        employee_salary_monthly, employee_salary_hourly, employee_address, employee_note,
        employee_department_id, employee_sub_department_id, employee_profession_id,
        employee_company_id, employee_ssk_number, employee_personnel_file_uuid,
        employee_photo_uuid, employee_left, employee_leave_date, employee_leave_reason, part_time) 
        
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    try:
        cursor.execute(sql, (None, employee_name, employee_surname, 
                             employee_register_number, mysql_employment_timestamp, employee_shift_group_id,
                             employee_salary, employee_salary_hourly, employee_address, employee_notes,
                             employee_department_id, employee_sub_department_id, employee_profession_id,
                             employee_company_id, employee_ssk_number, employee_personnel_file_uuid,
                             employee_photo_file_uuid, employee_left, employee_leave_date, employee_leave_reason, employee_part_time))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "insert",
            "table": "hr_employee_info",
            "sql_string": Utilities.encode_string(sql),
            "values": [[None, employee_name, employee_surname, 
                             employee_register_number, mysql_employment_timestamp, employee_shift_group_id,
                             employee_salary, employee_salary_hourly, employee_address, employee_notes,
                             employee_department_id, employee_sub_department_id, employee_profession_id,
                             employee_company_id, employee_ssk_number, employee_personnel_file_uuid,
                             employee_photo_file_uuid, employee_left, employee_leave_date, employee_leave_reason, employee_part_time]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Inserting Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    try:db.close()
    except:pass 
    return response_data
            
def Edit_Employee(data):
    db = GetMyDB()

    employee_name =                     data['employee_name']
    employee_surname =                  data['employee_surname']
    employee_register_number =          data['employee_card_register_number']
    employee_date_of_employment =       data['employee_date_of_employment']
    employee_shift_group =              data['employee_shift_group']
    employee_salary =                   data['employee_salary']
    employee_salary_hourly =            data['employee_salary_hourly']
    employee_address =                  data['employee_address']
    employee_notes =                    data['employee_notes']
    employee_department_string =        data['employee_department']
    employee_sub_department_string =    data['employee_sub_department']
    employee_profession_string =        data['employee_profession']
    employee_company_string =           data['employee_company']
    employee_ssk_number =               data['employee_ssk_number']
    employee_personnel_file_uuid =      data['employee_personnel_file_uuid']
    employee_photo_file_uuid =          data['employee_photo_file_uuid']
    employee_part_time =                data['employee_part_time']

    employee_shift_group_id =       HR_InternalGetters.Internal_Get_Employee_ShiftGroup_ID(employee_shift_group)
    employee_department_id =        HR_InternalGetters.Internal_Get_Employee_Department_ID(employee_department_string)
    employee_sub_department_id =    HR_InternalGetters.Internal_Get_Employee_SubDepartment_ID(employee_sub_department_string)
    employee_profession_id =        HR_InternalGetters.Internal_Get_Employee_Profession_ID(employee_profession_string)
    employee_company_id =           HR_InternalGetters.Internal_Get_Employee_Company_ID(employee_company_string)
    

    dt_obj = datetime.strptime(employee_date_of_employment, '%d.%m.%Y')
    mysql_employment_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_employee_info WHERE employee_register_number="%s" ''' % (employee_register_number)
    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        response_data = {"status" : "not_found"}
        return response_data
    
    cursor = db.cursor()
    sql = '''UPDATE hr_employee_info
            SET employee_name = %s, employee_surname = %s, employee_register_number = %s,
                employee_start_date = %s, employee_workshift_id = %s, employee_salary_monthly = %s, employee_salary_hourly = %s,
                employee_address = %s, employee_note = %s, employee_department_id = %s,
                employee_sub_department_id = %s, employee_profession_id = %s, employee_company_id = %s,
                employee_ssk_number = %s, employee_personnel_file_uuid = %s, employee_photo_uuid = %s,
                employee_left = %s, employee_leave_date = %s, employee_leave_reason = %s, part_time = %s
            WHERE employee_register_number = %s'''
    try:
        cursor.execute(sql, (employee_name, employee_surname,
                            employee_register_number, mysql_employment_timestamp, employee_shift_group_id,
                            employee_salary, employee_salary_hourly, employee_address, employee_notes,
                            employee_department_id, employee_sub_department_id, employee_profession_id,
                            employee_company_id, employee_ssk_number, employee_personnel_file_uuid,
                            employee_photo_file_uuid, "false", None, None, employee_part_time, employee_register_number))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "update",
            "table": "hr_employee_info",
            "sql_string": Utilities.encode_string(sql),
            "values": [[employee_name, employee_surname,
                            employee_register_number, mysql_employment_timestamp, employee_shift_group_id,
                            employee_salary, employee_salary_hourly, employee_address, employee_notes,
                            employee_department_id, employee_sub_department_id, employee_profession_id,
                            employee_company_id, employee_ssk_number, employee_personnel_file_uuid,
                            employee_photo_file_uuid, "false", None, None, employee_part_time, employee_register_number]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Updating Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    
    try:db.close()
    except:pass 
    return response_data

#TODO
def Set_Employee_Left(data):
    db = GetMyDB()
    employee_name =                 data['employee_name']
    employee_surname =              data['employee_surname']
    employee_register_number =      data['employee_register_number']
    exit_date =                     data['exit_date']

    dt_obj = datetime.strptime(exit_date, '%d.%m.%Y')
    mysql_employment_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    query = f'''SELECT * FROM hr_employee_info WHERE employee_register_number="%s" ''' % (employee_register_number)
    cursor.execute(query)
    foundRecords = cursor.fetchall()
    cursor.close()

    if len(foundRecords) <= 0:
        response_data = {"status" : "not_found"}
        return response_data
    
    cursor = db.cursor()
    sql = '''UPDATE hr_employee_info
            SET employee_left = %s, employee_leave_date = %s, employee_leave_reason = %s
            WHERE employee_register_number = %s'''
    try:
        cursor.execute(sql, ("true", mysql_employment_timestamp, "", employee_register_number))
        db.commit()
        cursor.close()
        db.close()

        sync_data = {
            "type": "update",
            "table": "hr_employee_info",
            "sql_string": Utilities.encode_string(sql),
            "values": [["true", mysql_employment_timestamp, "", employee_register_number]]
        }
        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

        response_data = {"status" : "ok"}
    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Updating Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}

    try:db.close()
    except:pass 
    return response_data

#TODO
def Remove_Employee_From_Database(data):
    db = GetMyDB()
