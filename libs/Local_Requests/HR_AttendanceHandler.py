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

from libs.Local_Requests import HR_InternalGetters

from libs import LocalRequests, CloudRequests, Utilities


def GetMyDB():
    db = LocalRequests.get_my_db()
    return db

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass


def Get_Employee_Attendance_From_Database(data):

    employees_whole_info = HR_InternalGetters.Internal_GetALL_Employee_Infos()
    all_companies_info = HR_InternalGetters.Internal_GetAll_Company_Names()
    all_workshifts_info = HR_InternalGetters.Internal_GetAll_Workshift_Names()


    if data["type"] == "salary_month":
        employee_register_number = data["employee_register_number"]
        year = int(data["year"])
        month = int(data["month"])
        sql_getstring = "SELECT * FROM hr_employee_attendance WHERE MONTH(entry_date) = %s AND YEAR(entry_date) = %s AND device_user_id = %s"
        sql_values = (month, year, employee_register_number)

    elif data["type"] == "attendance_general":
        year = int(data["year"])
        month = int(data["month"])
        sql_getstring = "SELECT * FROM hr_employee_attendance WHERE MONTH(entry_date) = %s AND YEAR(entry_date) = %s"
        sql_values = (month, year)

    
    elif data["type"] == "attendance_general2":
        start_datestring = data["start_date_string"]
        end_datestring = data["end_date_string"]
        try:
            start_date = datetime.strptime(start_datestring, '%Y-%m-%d %H:%M:%S')
            end_date = datetime.strptime(end_datestring, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            start_date = datetime.strptime(start_datestring, '%d-%m-%Y')
            end_date = datetime.strptime(end_datestring, '%d-%m-%Y')

        start_date_formatted = start_date.strftime('%d-%m-%Y')
        end_date_formatted = end_date.strftime('%d-%m-%Y')

        start_date = datetime.strptime(start_date_formatted, '%d-%m-%Y').replace(hour=0, minute=0, second=0)
        end_date = datetime.strptime(end_date_formatted, '%d-%m-%Y').replace(hour=23, minute=59, second=59)

        sql_getstring = "SELECT * FROM hr_employee_attendance WHERE entry_date BETWEEN %s AND %s"
        sql_values = (start_date, end_date)

    elif data["type"] == "puantaj":
        employee_card_number = data["employee_register_number"]
        year = int(data["year"])
        month = int(data["month"])
        sql_getstring = "SELECT * FROM hr_employee_attendance WHERE MONTH(entry_date) = %s AND YEAR(entry_date) = %s AND device_user_id = %s"
        sql_values = (month, year, employee_card_number)

    try:
        db = GetMyDB()
        cursor = db.cursor()

        cursor.execute(sql_getstring, sql_values)
        existing_entries = cursor.fetchall()


        morning_hours = HR_InternalGetters.Internal_Get_Morning_Workshift_Hours()
        night_hours = HR_InternalGetters.Internal_Get_Night_Workshift_Hours()

        if len(existing_entries) > 0:
            results = []
            for row in existing_entries:
                row_data = {
                    "id" : row[0],
                    "employee_register_number" : row[1],
                    "entry_date" : row[2],
                    "device_user_id" : row[3],
                    "device_verify_type" : row[4],
                    "device_verify_state" : row[5]
                }
                results.append(row_data)


            if data["type"] == "salary_month":
                first_day = datetime(year, month, 1)
                _, last_day_num = calendar.monthrange(year, month)
                last_day = datetime(year, month, last_day_num)
                start_date = datetime.strptime(str(first_day), '%Y-%m-%d %H:%M:%S').replace(hour=0, minute=0, second=0)
                end_date = datetime.strptime(str(last_day), '%Y-%m-%d %H:%M:%S').replace(hour=23, minute=59, second=59)
                one_day = timedelta(days=1)
                all_dates = []

            elif data["type"] == "attendance_general":
                try:
                    first_day = datetime(year, month, 1)
                    _, last_day_num = calendar.monthrange(year, month)
                    last_day = datetime(year, month, last_day_num)
                    start_date = datetime.strptime(str(first_day), '%Y-%m-%d %H:%M:%S').replace(hour=0, minute=0, second=0)
                    end_date = datetime.strptime(str(last_day), '%Y-%m-%d %H:%M:%S').replace(hour=23, minute=59, second=59)
                    one_day = timedelta(days=1)
                    all_dates = []
                   
                except Exception as error:
                    LogError(error)

            elif data["type"] == "attendance_general2":
                try:
                    start_date = datetime.strptime(start_date_formatted, '%d-%m-%Y').replace(hour=0, minute=0, second=0)
                    end_date = datetime.strptime(end_date_formatted, '%d-%m-%Y').replace(hour=23, minute=59, second=59)
                    one_day = timedelta(days=1)
                    all_dates = []
                except Exception as error:
                    LogError(error)
            
            elif data["type"] == "puantaj":
                first_day = datetime(year, month, 1)
                _, last_day_num = calendar.monthrange(year, month)
                last_day = datetime(year, month, last_day_num)
                start_date = datetime.strptime(str(first_day), '%Y-%m-%d %H:%M:%S').replace(hour=0, minute=0, second=0)
                end_date = datetime.strptime(str(last_day), '%Y-%m-%d %H:%M:%S').replace(hour=23, minute=59, second=59)
                one_day = timedelta(days=1)
                all_dates = []

            while start_date <= end_date:
                all_dates.append(start_date.strftime('%Y-%m-%d %H:%M:%S'))
                start_date += one_day
            
            all_dates.remove(all_dates[-1])
            all_dates.append(end_date.strftime('%Y-%m-%d %H:%M:%S'))
            

            total_dates_data = {}
            for one_day_string in all_dates:
                total_dates_data[one_day_string] = []

                one_day_datetime = datetime.strptime(one_day_string, '%Y-%m-%d %H:%M:%S')
                end_of_day = datetime(one_day_datetime.year, one_day_datetime.month, one_day_datetime.day, 23, 59, 59)
                end_of_day_string = end_of_day.strftime('%Y-%m-%d %H:%M:%S')


                this_day_unique_users = {}
                for entry_result in results:
                    entry_date_string = datetime.strftime(entry_result['entry_date'], '%Y-%m-%d %H:%M:%S')
                    entry_user_id = entry_result["device_user_id"]
                    entry_date = datetime.strptime(entry_date_string, '%Y-%m-%d %H:%M:%S')

                    if str(entry_user_id) not in this_day_unique_users:
                        this_day_unique_users[str(entry_user_id)] = []

                    if (entry_date.date() == one_day_datetime.date() and entry_date_string not in this_day_unique_users[str(entry_user_id)]):
                        this_day_unique_users[str(entry_user_id)].append(entry_date_string)

                for item in this_day_unique_users:
                    if this_day_unique_users[item] != []:
                        temp_data = {item : this_day_unique_users[item]}
                        total_dates_data[one_day_string].append(temp_data)
            

            final_data = {}
            for unique_day in total_dates_data:
                final_data[unique_day] = []
                for unique_user_day_data in total_dates_data[unique_day]:

                    for key in unique_user_day_data:
                        user_id = key

                        # user_info = HR_InternalGetters.Internal_Get_Employee_Name_Surname_Company_With_Card_Number(user_id)
                        for user in employees_whole_info:
                            if str(user_id) == str(user["employee_register_number"]):
                                user_info = (user["employee_name"], user["employee_surname"], user["employee_company_id"], user["employee_workshift_id"])
                                break

                        if user_info == None:
                            continue

                        employee_name = user_info[0]

                        employee_surname = user_info[1]
                        
                        employee_company_id = user_info[2]

                        for company in all_companies_info:
                            if employee_company_id == company["company_id"]:
                                employee_company_string = company["company_name"]
                                break

                        employee_workshift_id = user_info[3]

                        
                        for workshift in all_workshifts_info:
                            if employee_workshift_id == workshift["workshift_id"]:
                                employee_workshift_name = workshift["workshift_name"]


                        employee_nightci = False
                        if "night" in str(employee_workshift_name).lower():
                            employee_nightci = True

                        if employee_company_string == None:
                            continue

                        if len(unique_user_day_data[key]) == 1:

                            def is_last_day_of_month(date_string):
                                date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
                                next_day = date_obj + timedelta(days=1)
                                return next_day.month != date_obj.month
                                
                            if is_last_day_of_month(unique_day) == False:
                                entry_time = unique_user_day_data[key][0]

                                entry_datetime_obj = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
                                earliest_attendance_hour = entry_datetime_obj.hour
                                earliest_attendance_min = entry_datetime_obj.minute
                                earliest_attendance_entry = earliest_attendance_hour + earliest_attendance_min / 60.0

                                morning_hour = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").hour
                                morning_minute = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").minute
                                morning_entry = morning_hour + morning_minute / 60.0

                                night_exit_hour = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").hour
                                night_exit_minute = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").minute
                                night_exit = night_exit_hour + night_exit_minute / 60.0 - 0.1

                                difference_to_morning_entry = abs(round(earliest_attendance_entry - morning_entry, 2))
                                difference_to_night_exit = abs(round(night_exit - earliest_attendance_entry, 2))

                            else:
                                entry_time = unique_user_day_data[key][0]
                                entry_datetime_obj = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
                                earliest_attendance_hour = entry_datetime_obj.hour
                                earliest_attendance_min = entry_datetime_obj.minute
                                earliest_attendance_entry = earliest_attendance_hour + earliest_attendance_min / 60.0

                                morning_hour = datetime.strptime(morning_hours["data"][0]["workshift_end"], "%H:%M").hour
                                morning_minute = datetime.strptime(morning_hours["data"][0]["workshift_end"], "%H:%M").minute
                                morning_exit = morning_hour + morning_minute / 60.0

                                night_exit_hour = datetime.strptime(night_hours["data"][0]["workshift_start"], "%H:%M").hour
                                night_exit_minute = datetime.strptime(night_hours["data"][0]["workshift_start"], "%H:%M").minute
                                night_entry = night_exit_hour + night_exit_minute / 60.0

                                difference_to_morning_entry = abs(round(earliest_attendance_entry - morning_exit, 2))
                                difference_to_night_exit = abs(round(earliest_attendance_entry - night_entry, 2))

                            if difference_to_morning_entry < difference_to_night_exit:
                                refined_data = {
                                    "day" : unique_day,
                                    "employee_register_id" : key,
                                    "employee_name" : employee_name,
                                    "employee_surname" : employee_surname,
                                    "employee_company" : employee_company_string,
                                    "entry" : entry_time,
                                    "exit" : None,
                                    "note" : "Eksik Veri"
                                }
                                final_data[unique_day].append(refined_data)
                            else:
                                if is_last_day_of_month(unique_day) == False:
                                    workshift_entry_hour = HR_InternalGetters.Internal_Get_Workshift_Entry_Hour_String_With_Workshift_ID(employee_workshift_id)
                                    datetime1 = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
                                    time2 = datetime.strptime(workshift_entry_hour, "%H:%M").time()
                                    new_datetime = datetime(datetime1.year, datetime1.month, datetime1.day, time2.hour, time2.minute, time2.second)
                                    new_new_datetime = new_datetime - timedelta(days=1)

                                    min_time = new_new_datetime - timedelta(hours=2)
                                    max_time = new_new_datetime + timedelta(hours=5)

                                    min_time_string = min_time.strftime("%Y-%m-%d %H:%M:%S")
                                    max_time_string = max_time.strftime("%Y-%m-%d %H:%M:%S")

                                    previous_evening_entry = HR_InternalGetters.Internal_Get_Nightshift_Employee_Previous_Day_Entry(user_id, min_time_string, max_time_string)

                                    if previous_evening_entry == None:
                                        note = "Eksik Veri"
                                        new_unique_day_string = unique_day
                                        refined_data = {
                                            "day" : unique_day,
                                            "employee_register_id" : key,
                                            "employee_name" : employee_name,
                                            "employee_surname" : employee_surname,
                                            "employee_company" : employee_company_string,
                                            "entry" : entry_time,
                                            "exit" : None,
                                            "note" : note
                                        }

                                    else:
                                        note = "OK"
                                        new_unique_day = datetime.strptime(unique_day, "%Y-%m-%d %H:%M:%S") - timedelta(days=1)
                                        new_unique_day_string = datetime.strftime(new_unique_day, "%Y-%m-%d %H:%M:%S")

                                        refined_data = {
                                            "day" : unique_day,
                                            "employee_register_id" : key,
                                            "employee_name" : employee_name,
                                            "employee_surname" : employee_surname,
                                            "employee_company" : employee_company_string,
                                            "entry" : previous_evening_entry,
                                            "exit" : entry_time,
                                            "note" : note
                                        }

                                else:
                                    workshift_entry_hour = HR_InternalGetters.Internal_Get_Workshift_Exit_Hour_String_With_Workshift_ID(employee_workshift_id)
                                    datetime1 = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
                                    time2 = datetime.strptime(workshift_entry_hour, "%H:%M").time()
                                    new_datetime = datetime(datetime1.year, datetime1.month, datetime1.day, time2.hour, time2.minute, time2.second)
                                    new_new_datetime = new_datetime + timedelta(days=1)

                                    min_time = new_new_datetime - timedelta(hours=5)
                                    max_time = new_new_datetime + timedelta(hours=1.5)

                                    min_time_string = min_time.strftime("%Y-%m-%d %H:%M:%S")
                                    max_time_string = max_time.strftime("%Y-%m-%d %H:%M:%S")

                                    next_morning_exit = HR_InternalGetters.Internal_Get_Nightshift_Employee_Next_Morning_Exit(user_id, min_time_string, max_time_string)

                                    if next_morning_exit == None:
                                        note = "Eksik Veri"
                                    else:
                                        note = "OK"

                                    refined_data = {
                                        "day" : unique_day,
                                        "employee_register_id" : key,
                                        "employee_name" : employee_name,
                                        "employee_surname" : employee_surname,
                                        "employee_company" : employee_company_string,
                                        "entry" : entry_time,
                                        "exit" : next_morning_exit,
                                        "note" : note
                                    }

                                final_data[unique_day].append(refined_data)

                        elif len(unique_user_day_data[key]) == 2:
                            entry_time = unique_user_day_data[key][0]
                            exit_time = unique_user_day_data[key][1]

                            entry_datetime_obj = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
                            earliest_attendance_hour = entry_datetime_obj.hour
                            earliest_attendance_min = entry_datetime_obj.minute
                            earliest_attendance_entry = earliest_attendance_hour + earliest_attendance_min / 60.0

                            morning_hour = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").hour
                            morning_minute = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").minute
                            morning_entry = morning_hour + morning_minute / 60.0

                            night_exit_hour = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").hour
                            night_exit_minute = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").minute
                            night_exit = night_exit_hour + (night_exit_minute / 60.0) - 0.1

                            difference_to_morning_entry = abs(round(earliest_attendance_entry - morning_entry, 2))
                            difference_to_night_exit = abs(round(earliest_attendance_entry - night_exit, 2))

                            print(difference_to_night_exit)
                            print(difference_to_morning_entry)

                            if difference_to_morning_entry < difference_to_night_exit:
                                refined_data = {
                                    "day" : unique_day,
                                    "employee_register_id" : key,
                                    "employee_name" : employee_name,
                                    "employee_surname" : employee_surname,
                                    "employee_company" : employee_company_string,
                                    "entry" : entry_time,
                                    "exit" : exit_time,
                                    "note" : "OK"
                                }
                            else:
                                workshift_entry_hour = HR_InternalGetters.Internal_Get_Workshift_Entry_Hour_String_With_Workshift_ID(employee_workshift_id)
                                datetime1 = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
                                time2 = datetime.strptime(workshift_entry_hour, "%H:%M").time()
                                new_datetime = datetime(datetime1.year, datetime1.month, datetime1.day, time2.hour, time2.minute, time2.second)
                                new_new_datetime = new_datetime - timedelta(days=1)

                                if earliest_attendance_entry < 2:
                                    min_time = datetime1 - timedelta(hours = 7)
                                    max_time = datetime1 + timedelta(hours = 1)
                                else:
                                    min_time = new_new_datetime - timedelta(hours=1.5)
                                    max_time = new_new_datetime + timedelta(hours=5)

                                min_time_string = min_time.strftime("%Y-%m-%d %H:%M:%S")
                                max_time_string = max_time.strftime("%Y-%m-%d %H:%M:%S")


                                previous_evening_entry = HR_InternalGetters.Internal_Get_Nightshift_Employee_Previous_Day_Entry(user_id, min_time_string, max_time_string)


                                if previous_evening_entry == None:
                                    note = "Eksik Veri"
                                    new_unique_day_string = unique_day

                                else:
                                    note = "OK"
                                    new_unique_day = datetime.strptime(unique_day, "%Y-%m-%d %H:%M:%S") - timedelta(days=1)
                                    new_unique_day_string = datetime.strftime(new_unique_day, "%Y-%m-%d %H:%M:%S")

                                refined_data = {
                                    "day" : unique_day,
                                    "employee_register_id" : key,
                                    "employee_name" : employee_name,
                                    "employee_surname" : employee_surname,
                                    "employee_company" : employee_company_string,
                                    "entry" : previous_evening_entry,
                                    "exit" : entry_time,
                                    "note" : note
                                }

                            final_data[unique_day].append(refined_data)

                        elif len(unique_user_day_data[key]) == 3:

                            entry_time = unique_user_day_data[key][0]
                            exit_time = unique_user_day_data[key][1]

                            possible_reentry_time = unique_user_day_data[key][2]

                            entry_datetime_obj = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
                            earliest_attendance_hour = entry_datetime_obj.hour
                            earliest_attendance_min = entry_datetime_obj.minute
                            earliest_attendance_entry = earliest_attendance_hour + earliest_attendance_min / 60.0

                            morning_hour = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").hour
                            morning_minute = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").minute
                            morning_entry = morning_hour + morning_minute / 60.0

                            night_exit_hour = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").hour
                            night_exit_minute = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").minute
                            night_exit = night_exit_hour + (night_exit_minute / 60.0) - 0.1

                            difference_to_morning_entry = abs(round(earliest_attendance_entry - morning_entry, 2))
                            difference_to_night_exit = abs(round(earliest_attendance_entry - night_exit, 2))


                            if difference_to_morning_entry < difference_to_night_exit:

                                refined_data = {
                                    "day" : unique_day,
                                    "employee_register_id" : key,
                                    "employee_name" : employee_name,
                                    "employee_surname" : employee_surname,
                                    "employee_company" : employee_company_string,
                                    "entry" : entry_time,
                                    "exit" : exit_time,
                                    "note" : "OK"
                                }
                                final_data[unique_day].append(refined_data)

                                reentry_datetime = datetime.strptime(possible_reentry_time, "%Y-%m-%d %H:%M:%S")
                                min_time = reentry_datetime + timedelta(minutes=5)
                                max_time = reentry_datetime + timedelta(hours=5)
                                min_time_string = min_time.strftime("%Y-%m-%d %H:%M:%S")
                                max_time_string = max_time.strftime("%Y-%m-%d %H:%M:%S")
                                next_day_exit = HR_InternalGetters.Internal_Get_Nightshift_Employee_Next_Morning_Exit(user_id, min_time_string, max_time_string)
                                if next_day_exit != None:
                                    refined_data2 = {
                                        "day" : f"{unique_day}(2)",
                                        "employee_register_id" : key,
                                        "employee_name" : employee_name,
                                        "employee_surname" : employee_surname,
                                        "employee_company" : employee_company_string,
                                        "entry" : possible_reentry_time,
                                        "exit" : next_day_exit,
                                        "note" : "OK",
                                        "is_extra" : True
                                    }
                                    final_data[f"{unique_day}"].append(refined_data2)

                            else:
                                pass

                        elif len(unique_user_day_data[key]) == 4:
                            entry_1 = unique_user_day_data[key][0]
                            entry_2 = unique_user_day_data[key][1]
                            entry_3 = unique_user_day_data[key][2]
                            entry_4 = unique_user_day_data[key][3]

                            entry_datetime_obj = datetime.strptime(entry_1, "%Y-%m-%d %H:%M:%S")
                            earliest_attendance_hour = entry_datetime_obj.hour
                            earliest_attendance_min = entry_datetime_obj.minute
                            earliest_attendance_entry = earliest_attendance_hour + earliest_attendance_min / 60.0

                            morning_hour = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").hour
                            morning_minute = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").minute
                            morning_entry = morning_hour + morning_minute / 60.0

                            night_exit_hour = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").hour
                            night_exit_minute = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").minute
                            night_exit = night_exit_hour + night_exit_minute / 60.0 - 0.1

                            difference_to_morning_entry = abs(round(earliest_attendance_entry - morning_entry, 2))
                            difference_to_night_exit = abs(round(earliest_attendance_entry - night_exit, 2))

                            if difference_to_morning_entry < difference_to_night_exit:
                                refined_data = {
                                    "day" : unique_day,
                                    "employee_register_id" : key,
                                    "employee_name" : employee_name,
                                    "employee_surname" : employee_surname,
                                    "employee_company" : employee_company_string,
                                    "entry" : entry_2,
                                    "exit" : entry_3,
                                    "note" : "İlk Giriş"
                                }

                                final_data[unique_day].append(refined_data)

                                refined_data2 = {
                                    "day" : unique_day,
                                    "employee_register_id" : key,
                                    "employee_name" : employee_name,
                                    "employee_surname" : employee_surname,
                                    "employee_company" : employee_company_string,
                                    "entry" : entry_4,
                                    "exit" : entry_1,
                                    "note" : "İkinci Giriş",
                                    "is_extra" : True
                                }
                                final_data[unique_day].append(refined_data2)

                            else:
                                refined_data = {
                                    "day" : unique_day,
                                    "employee_register_id" : key,
                                    "employee_name" : employee_name,
                                    "employee_surname" : employee_surname,
                                    "employee_company" : employee_company_string,
                                    "entry" : entry_2,
                                    "exit" : entry_3,
                                    "note" : "İlk Giriş"
                                }

                                final_data[unique_day].append(refined_data)

                                refined_data2 = {
                                    "day" : unique_day,
                                    "employee_register_id" : key,
                                    "employee_name" : employee_name,
                                    "employee_surname" : employee_surname,
                                    "employee_company" : employee_company_string,
                                    "entry" : entry_4,
                                    "exit" : entry_1,
                                    "note" : "İkinci Giriş",
                                    "is_extra" : True
                                }

                                final_data[unique_day].append(refined_data2)


                if final_data[unique_day] == []:
                    del final_data[unique_day]
                

            for key in final_data:
                if final_data[key] == []:
                    print("EMPTY")
            
            
            return_data = {
                "status" : "ok",
                "result" : final_data
            }
        else:
            return_data = {
                "status" : "not_found",
                "result" : None
            }
            try:
                cursor.close()
            except:
                pass
            try:
                db.close()
            except:
                pass
            return return_data
    except Exception as error:
        LogError(error)
        return_data = {
            "status" : "error",
            "error_type" : str(type(error).__name__),
            "error_text" : error
        }

    try:
        cursor.close()
    except:
        pass
    try:
        db.close()
    except:
        pass
    return return_data




def Refresh_Employee_Attendance():

    db = GetMyDB()
    attendance_error = None
    try:
        device_result = HR_InternalGetters.Internal_Get_Employee_Attendance_From_Device()
        if device_result["ret"] == 0:
            print("ret 0")
            return "No new entry in device" #TODO
        
        elif device_result["ret"] == "connection_error":
            print(device_result["error_text"])

            return {
                "status" : "error",
                "error_text" : device_result['error_text']
            }
        
        elif (device_result["ret"] != 1 and device_result["ret"] != 0):
            print(f"ret error: {device_result['ret']}")
            return "Error while getting device entries" #TODO


        updated_entry_count = 0
        device_entries = device_result["results"]

        cursor = db.cursor()

        cloud_insert_queries = []
        for entry in device_entries:
            # print(entry)

            user_id = entry["user_id"]
            verify_date = entry["verify_date"]
            verify_type = entry["verify_type"]
            verfy_state = entry["verify_state"]
            work_code = entry["work_code"]

            date_obj = datetime.strptime(verify_date, "%d-%m-%Y %H:%M:%S")
            verify_date_mysql_timestamp = date_obj.strftime("%Y-%m-%d %H:%M:%S")

            # print(verify_date_mysql_timestamp)

            check_edited_device_entry = "SELECT * FROM hr_logs_employee_date_changes WHERE employee_id = %s AND old_date = %s"
            cursor.execute(check_edited_device_entry, (user_id, verify_date_mysql_timestamp))
            query_result = cursor.fetchall()

            if len(query_result) == 0:
                check_row_query = "SELECT * FROM hr_employee_attendance WHERE entry_date = %s"
                cursor.execute(check_row_query, (verify_date_mysql_timestamp,))
                query_result = cursor.fetchall()

                if len(query_result) == 0:
                    sql_insert_query = '''INSERT INTO hr_employee_attendance (id,employee_register_number,entry_date,device_user_id,device_verify_type,device_verify_state) VALUES (%s, %s, %s, %s, %s, %s)'''
                    try:
                        cursor.execute(sql_insert_query, (None, user_id, verify_date_mysql_timestamp, user_id, verify_type, verfy_state))
                        db.commit()
                        updated_entry_count += 1
                        cloud_insert_queries.append([None, user_id, verify_date_mysql_timestamp, user_id, verify_type, verfy_state])
                        sync_data = {
                            "type": "insert",
                            "table": "hr_employee_attendance",
                            "sql_string": Utilities.encode_string(sql_insert_query),
                            "values": cloud_insert_queries
                        }
                        CloudRequests.Save_New_Cloud_Sync_Task(sync_data)
                    except Exception as error:
                        print(error)
                else:
                    pass
                    # print(f"Already inserted {verify_date_mysql_timestamp}")
            


        cursor.close()
        try:db.close()
        except:pass
        return {
            "status" : "ok",
            "update_count" : updated_entry_count,
            "error" : attendance_error
        }
    except Exception as error:
        attendance_error = error
        return {
            "status" : "error",
            "error" : attendance_error,
            "traceback": str(traceback.format_exc())
        }

def Change_Employee_Attendance(data):
    db = GetMyDB()

    pprint.pprint(data)

    employee_register_number = int(data["employee_register_number"])
    initial_entry = data["initial_entry"]
    initial_exit = data["initial_exit"]
    new_entry = data["new_entry"]
    new_exit = data["new_exit"]
    date_text = data["date"]


    morning_hours = HR_InternalGetters.Internal_Get_Morning_Workshift_Hours()
    night_hours = HR_InternalGetters.Internal_Get_Night_Workshift_Hours()


    morning_hour_exit = datetime.strptime(morning_hours["data"][0]["workshift_end"], "%H:%M").hour
    morning_minute = datetime.strptime(morning_hours["data"][0]["workshift_end"], "%H:%M").minute
    morning_exit = morning_hour_exit + morning_minute / 60.0

    night_hour_exit = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").hour
    night_minute = datetime.strptime(night_hours["data"][0]["workshift_end"], "%H:%M").minute
    night_exit = night_hour_exit + night_minute / 60.0


    morning_hour_entry = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").hour
    morning_minute = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").minute
    morning_entry = morning_hour_entry + morning_minute / 60.0

    night_hour_entry = datetime.strptime(night_hours["data"][0]["workshift_start"], "%H:%M").hour
    night_minute = datetime.strptime(night_hours["data"][0]["workshift_start"], "%H:%M").minute
    night_entry = night_hour_entry + night_minute / 60.0
    
    #Var olan giriş değişiyor
    if initial_entry != "":
        dt = datetime.strptime(initial_entry, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime("2000-01-01 " + new_entry + ":00", "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(hour=dt2.hour, minute=dt2.minute)
        new_entry_fullstring = dt.strftime("%Y-%m-%d %H:%M:%S")

    #Var olmayan giriş ekleniyor
    else:
        new_exit_hour = datetime.strptime(new_exit, "%H:%M").hour
        difference_to_morning_exit = abs(round(new_exit_hour - morning_exit, 2))
        difference_to_night_exit = abs(round(new_exit_hour - night_exit, 2))

        if difference_to_morning_exit < difference_to_night_exit:
            # Entry aynı gün içinde olacak
            dt = datetime.strptime(initial_exit, "%Y-%m-%d %H:%M:%S")
            dt2 = datetime.strptime("2000-01-01 " + new_entry + ":00", "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(hour=dt2.hour, minute=dt2.minute, second=dt2.second)
            new_entry_fullstring = dt.strftime("%Y-%m-%d %H:%M:%S")
            
        else:
            # Entry önceki gün içinde olcak
            dt = datetime.strptime(initial_exit, "%Y-%m-%d %H:%M:%S") - timedelta(days=1)
            dt2 = datetime.strptime("2000-01-01 " + new_entry + ":00", "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(hour=dt2.hour, minute=dt2.minute)
            new_entry_fullstring = dt.strftime("%Y-%m-%d %H:%M:%S")


    #Var olan çıkış değişiyor
    if initial_exit != "":
        dt = datetime.strptime(initial_exit, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime("2000-01-01 " + new_exit + ":00", "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(hour=dt2.hour, minute=dt2.minute)
        new_exit_fullstring = dt.strftime("%Y-%m-%d %H:%M:%S")
    
    #Var olmayan çıkış ekleniyor
    else:
        new_entry_hour = datetime.strptime(new_entry, "%H:%M").hour
        difference_to_morning_entry = abs(round(new_entry_hour - morning_entry, 2))
        difference_to_night_entry = abs(round(new_entry_hour - night_entry, 2))


        if difference_to_morning_entry < difference_to_night_entry:
            # Entry aynı gün içinde olacak
            dt = datetime.strptime(initial_entry, "%Y-%m-%d %H:%M:%S")

            if new_exit != "":
                dt2 = datetime.strptime("2000-01-01 " + new_exit + ":00", "%Y-%m-%d %H:%M:%S")
            else:
                dt2 = datetime.strptime("2000-01-01 " + "00:00" + ":00", "%Y-%m-%d %H:%M:%S")

            dt = dt.replace(hour=dt2.hour, minute=dt2.minute)
            new_exit_fullstring = dt.strftime("%Y-%m-%d %H:%M:%S")

 
        else:
            # Entry önceki gün içinde olcak
            dt = datetime.strptime(initial_entry, "%Y-%m-%d %H:%M:%S") - timedelta(days=1)
            dt2 = datetime.strptime("2000-01-01 " + new_exit + ":00", "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(hour=dt2.hour, minute=dt2.minute)
            new_exit_fullstring = dt.strftime("%Y-%m-%d %H:%M:%S")


    try:

        if new_exit != "" and initial_exit != new_exit_fullstring and initial_entry == new_entry_fullstring: # ONLY EXIT CHANGED
            print("OPTIMUS 1")
            if initial_exit == "":
                sql = '''INSERT IGNORE INTO hr_employee_attendance (
                    id, employee_register_number, entry_date, device_user_id, device_verify_type, device_verify_state) 
                    VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor = db.cursor()
                cursor.execute(sql, (None, employee_register_number, new_exit_fullstring, employee_register_number, 15, 0))
                db.commit()
                cursor.close()
                db.close()

                sync_data = {
                    "type": "insert",
                    "table": "hr_employee_attendance",
                    "sql_string": Utilities.encode_string(sql),
                    "values": [[None, employee_register_number, new_exit_fullstring, employee_register_number, 15, 0]]
                }
                CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

                response_data = {"status" : "ok"}
            else:
                sql_update_string = '''UPDATE hr_employee_attendance SET entry_date=%s WHERE device_user_id=%s AND entry_date=%s'''
                cursor = db.cursor()
                cursor.execute(sql_update_string, (new_exit_fullstring, employee_register_number, initial_exit))
                db.commit()
                cursor.close()
                db.close()

                sync_data = {
                    "type": "update",
                    "table": "hr_employee_attendance",
                    "sql_string": Utilities.encode_string(sql_update_string),
                    "values": [[new_exit_fullstring, employee_register_number, initial_exit]]
                }
                CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

                db = GetMyDB()
                cursor = db.cursor()
                sql_log_string = '''INSERT INTO hr_logs_employee_date_changes (id, employee_id, old_date, new_date) VALUES (%s, %s, %s, %s)'''
                cursor.execute(sql_log_string, (None, int(employee_register_number), initial_exit, new_exit_fullstring))
                db.commit()
                cursor.close()
                db.close()

                sync_data = {
                    "type": "update",
                    "table": "hr_logs_employee_date_changes",
                    "sql_string": Utilities.encode_string(sql_log_string),
                    "values": [[None, int(employee_register_number), initial_exit, new_exit_fullstring]]
                }
                CloudRequests.Save_New_Cloud_Sync_Task(sync_data)
                
                response_data = {"status" : "ok"}


        elif new_entry != "" and initial_entry != new_entry_fullstring and initial_exit == new_exit_fullstring: # ONLY ENTRY CHANGED BUT WE ALSO HAVE EXIT HOUR
            print("OPTIMUS 2")
            if initial_entry == "":
                sql = '''INSERT IGNORE INTO hr_employee_attendance (
                    id, employee_register_number, entry_date, device_user_id, device_verify_type, device_verify_state) 
                    VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor = db.cursor()
                cursor.execute(sql, (None, employee_register_number, new_entry_fullstring, employee_register_number, 15, 0))
                db.commit()
                cursor.close()
                db.close()

                sync_data = {
                    "type": "insert",
                    "table": "hr_employee_attendance",
                    "sql_string": Utilities.encode_string(sql),
                    "values": [[None, employee_register_number, new_entry_fullstring, employee_register_number, 15, 0]]
                }
                CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

                response_data = {"status" : "ok"}
            else:
                sql_update_string = '''UPDATE hr_employee_attendance SET entry_date=%s WHERE device_user_id=%s AND entry_date=%s'''
                cursor = db.cursor()
                cursor.execute(sql_update_string, (new_entry_fullstring, employee_register_number, initial_entry))
                db.commit()
                cursor.close()
                db.close()

                sync_data = {
                    "type": "update",
                    "table": "hr_employee_attendance",
                    "sql_string": Utilities.encode_string(sql_update_string),
                    "values": [[new_entry_fullstring, employee_register_number, initial_entry]]
                }
                CloudRequests.Save_New_Cloud_Sync_Task(sync_data)



                db = GetMyDB()
                cursor = db.cursor()
                sql_log_string = '''INSERT INTO hr_logs_employee_date_changes (id, employee_id, old_date, new_date) VALUES (%s, %s, %s, %s)'''
                cursor.execute(sql_log_string, (None, int(employee_register_number), initial_entry, new_entry_fullstring))
                db.commit()
                cursor.close()
                db.close()

                sync_data = {
                    "type": "update",
                    "table": "hr_logs_employee_date_changes",
                    "sql_string": Utilities.encode_string(sql_log_string),
                    "values": [[None, int(employee_register_number), initial_entry, new_entry_fullstring]]
                }
                CloudRequests.Save_New_Cloud_Sync_Task(sync_data)



                response_data = {"status" : "ok"}
        

        elif new_entry != "" and initial_entry != new_entry_fullstring and initial_exit == "" and new_exit == "": # ONLY ENTRY CHANGED AND THERE IS NO EXIT HOUR YET
            print("OPTIMUS 3")
            if initial_entry == "":
                print("OPTIMUS 3-1")
                sql = '''INSERT IGNORE INTO hr_employee_attendance (
                    id, employee_register_number, entry_date, device_user_id, device_verify_type, device_verify_state) 
                    VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor = db.cursor()
                cursor.execute(sql, (None, employee_register_number, new_entry_fullstring, employee_register_number, 15, 0))
                db.commit()
                cursor.close()
                db.close()

                sync_data = {
                    "type": "insert",
                    "table": "hr_employee_attendance",
                    "sql_string": Utilities.encode_string(sql),
                    "values": [[None, employee_register_number, new_entry_fullstring, employee_register_number, 15, 0]]
                }
                CloudRequests.Save_New_Cloud_Sync_Task(sync_data)

                response_data = {"status" : "ok"}
            else:
                print("OPTIMUS 3-2")
                sql_update_string = '''UPDATE hr_employee_attendance SET entry_date=%s WHERE device_user_id=%s AND entry_date=%s'''
                cursor = db.cursor()
                cursor.execute(sql_update_string, (new_entry_fullstring, employee_register_number, initial_entry))
                db.commit()
                cursor.close()
                db.close()

                sync_data = {
                    "type": "insert",
                    "table": "hr_employee_attendance",
                    "sql_string": Utilities.encode_string(sql_update_string),
                    "values": [[new_entry_fullstring, employee_register_number, initial_entry]]
                }
                CloudRequests.Save_New_Cloud_Sync_Task(sync_data)


                db = GetMyDB()
                cursor = db.cursor()
                sql_log_string = '''INSERT INTO hr_logs_employee_date_changes (id, employee_id, old_date, new_date) VALUES (%s, %s, %s, %s)'''
                cursor.execute(sql_log_string, (None, int(employee_register_number), initial_entry, new_entry_fullstring))
                db.commit()
                cursor.close()
                db.close()

                sync_data = {
                    "type": "update",
                    "table": "hr_logs_employee_date_changes",
                    "sql_string": Utilities.encode_string(sql_log_string),
                    "values": [[None, int(employee_register_number), initial_entry, new_entry_fullstring]]
                }
                CloudRequests.Save_New_Cloud_Sync_Task(sync_data)



                response_data = {"status" : "ok"}



        elif (initial_entry != new_entry_fullstring and initial_exit != new_exit_fullstring and new_entry != '' and new_exit != ''): # BOTH CHANGED
            print("OPTIMUS 4")

            if (initial_entry == ''):  # Giriş saati yok, yani oluşturulacak
                sql_update_string1 = '''INSERT IGNORE INTO hr_employee_attendance (
                    id, employee_register_number, entry_date, device_user_id, device_verify_type, device_verify_state) 
                    VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor = db.cursor()
                cursor.execute(sql_update_string1, (None, employee_register_number, new_entry_fullstring, employee_register_number, 15, 0))
                db.commit()
                cursor.close()
                db.close()
            else: # Giriş saati var, değiştirilecek
                sql_update_string1 = '''UPDATE hr_employee_attendance SET entry_date=%s WHERE device_user_id=%s AND entry_date=%s'''
                cursor = db.cursor()
                cursor.execute(sql_update_string1, (new_entry_fullstring, employee_register_number, initial_entry))
                db.commit()
                cursor.close()
                db.close()

            sync_data = {
                "type": "update",
                "table": "hr_employee_attendance",
                "sql_string": Utilities.encode_string(sql_update_string1),
                "values": [[new_entry_fullstring, employee_register_number, initial_entry]]
            }
            CloudRequests.Save_New_Cloud_Sync_Task(sync_data)


            db = GetMyDB()
            cursor = db.cursor()
            sql_log_string = '''INSERT INTO hr_logs_employee_date_changes (id, employee_id, old_date, new_date) VALUES (%s, %s, %s, %s)'''
            cursor.execute(sql_log_string, (None, int(employee_register_number), initial_entry, new_entry_fullstring))
            db.commit()
            cursor.close()
            db.close()

            sync_data = {
                "type": "update",
                "table": "hr_logs_employee_date_changes",
                "sql_string": Utilities.encode_string(sql_log_string),
                "values": [[None, int(employee_register_number), initial_entry, new_entry_fullstring]]
            }
            CloudRequests.Save_New_Cloud_Sync_Task(sync_data)
            

            if (initial_exit == ''): # Çıkış yok, yeni oluşturulacak
                print("Çıkış yok yenisi ekleniyor.")

                sql_update_string2 = '''INSERT IGNORE INTO hr_employee_attendance (
                    id, employee_register_number, entry_date, device_user_id, device_verify_type, device_verify_state) 
                    VALUES (%s, %s, %s, %s, %s, %s)'''
                db = GetMyDB()
                cursor = db.cursor()
                cursor.execute(sql_update_string2, (None, employee_register_number, new_exit_fullstring, employee_register_number, 15, 0))
                db.commit()
                cursor.close()
                db.close()
            else: # Çıkış var, değiştirilecek
                sql_update_string2 = '''UPDATE hr_employee_attendance SET entry_date=%s WHERE device_user_id=%s AND entry_date=%s'''
                db = GetMyDB()
                cursor = db.cursor()
                cursor.execute(sql_update_string2, (new_exit_fullstring, employee_register_number, initial_exit))
                db.commit()
                cursor.close()
                db.close()

            sync_data = {
                "type": "update",
                "table": "hr_employee_attendance",
                "sql_string": Utilities.encode_string(sql_update_string2),
                "values": [[new_exit_fullstring, employee_register_number, initial_exit]]
            }
            CloudRequests.Save_New_Cloud_Sync_Task(sync_data)



            db = GetMyDB()
            cursor = db.cursor()
            sql_log_string = '''INSERT INTO hr_logs_employee_date_changes (id, employee_id, old_date, new_date) VALUES (%s, %s, %s, %s)'''
            cursor.execute(sql_log_string, (None, int(employee_register_number), initial_exit, new_exit_fullstring))
            db.commit()
            cursor.close()
            db.close()

            sync_data = {
                "type": "update",
                "table": "hr_logs_employee_date_changes",
                "sql_string": Utilities.encode_string(sql_log_string),
                "values": [[None, int(employee_register_number), initial_exit, new_exit_fullstring]]
            }
            CloudRequests.Save_New_Cloud_Sync_Task(sync_data)




            response_data = {"status" : "ok"}

        else: # NONE CHANGED
            print("OPTIMUS 5")
            response_data = {"status" : "no_change"}

    except Exception as error:
        LogError(error)
        cursor.close()
        db.rollback()
        print(f"Error While Updating Attendance Data: {type(error).__name__} - {error}")
        response_data = {"status" : "error", "error_text" : {error}}
    

    try:cursor.close()
    except:pass
    try:db.close()
    except:pass 
    return response_data
