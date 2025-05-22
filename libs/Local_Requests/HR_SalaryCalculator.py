
import json, traceback
from datetime import datetime, timedelta
from libs import Helpers
from libs.Local_Requests import HR_AttendanceHandler
from libs.Local_Requests import HR_InternalGetters, HR_EmployeeHandler, Printer_Master
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

def Calculate_Employee_Salary_Main(employee_info_payload, employee_work_data, year, month):

    ucretli_izin_day_value = 0

    ucretsiz_izin_days = 0
    ucretsiz_izin_hours = 0
    ucretsiz_izin_price = 0

    ek_kesinti_value = 0

    ek_kazanc_value = 0

    total_employee_worked_days = 0
    total_employee_worked_hours = 0
    employee_exit_missing_days = []
    employee_entry_missing_days = []
    both_missing_days = []
    salary_details = []

    employee_name = employee_info_payload["employee_name"]
    employee_surname = employee_info_payload["employee_surname"]
    employee_department = employee_info_payload["employee_department"]
    employee_profession = employee_info_payload["employee_profession"]
    employee_register_number = employee_info_payload["employee_register_number"]
    workshift_name = employee_info_payload["workshift_name"]
    part_time = employee_info_payload["part_time"]
    salary_hourly = employee_info_payload["salary_hourly"]

    company_entry_hour = employee_info_payload["entry_hour"]
    company_exit_hour = employee_info_payload["exit_hour"]
    company_break_start = employee_info_payload["break_start"]
    company_break_end = employee_info_payload["break_end"]
    entry_tolerance_minutes = employee_info_payload["entry_tolerance"]
    exit_tolerance_minutes = employee_info_payload["exit_tolerance"]
    extra_hour_multiplier = employee_info_payload["extra_percentage"]
    base_salary = employee_info_payload["base_salary"]


    employee_company = employee_info_payload["employee_company"]

    if part_time == True:
        hourly_salary = salary_hourly
    else:
        hourly_salary = base_salary / 225

    weekday_normal_work_earned_salary = base_salary

    break_start = datetime.strptime(company_break_start, "%H:%M")
    break_end = datetime.strptime(company_break_end, "%H:%M")
    break_amount = break_end - break_start


    entry_time = datetime.strptime(company_entry_hour, "%H:%M")
    exit_time = datetime.strptime(company_exit_hour, "%H:%M")

    daily_total_hours = timedelta(hours=((exit_time - entry_time).seconds // 3600))

    daily_hours_after_break_subtracted = daily_total_hours - break_amount

    total_daily_work_hour = float(daily_hours_after_break_subtracted.seconds / 60 / 60)


    is_manager = False
    if employee_department == "İDARİ":
        total_daily_work_hour += 1
        is_manager = True

    total_workdays_in_month = []
    weeks_with_workdays = json.loads(Helpers.get_weekdays_of_month(year, month))
    for week in weeks_with_workdays:
        for day in week:
            total_workdays_in_month.append(day)
    

    total_work_hours_in_month = Helpers.calculate_total_work_hours_of_month(total_workdays_in_month, company_entry_hour, company_exit_hour, break_start, break_end)


    # CREATE SALARY DATA
    for day in employee_work_data:
        date_of_day = datetime.strptime(day["date"], "%d-%m-%Y")

        if date_of_day.month != month:
            continue

        if date_of_day.year != year:
            continue

        clock_in_hour = day["start_time"]
        departure_hour = day["end_time"]

        if "is_extra" in day:
            guy_worked_twice = day["is_extra"]
        else:
            guy_worked_twice = False


        total_employee_worked_days += 1
        if (clock_in_hour == None and departure_hour == None):
            both_missing_days.append(day)
            total_employee_worked_days -= 1
            detail_data = {
                "date" : day["date"],
                "weekday" : is_weekday_date(day["date"]),
                "start" : None,
                "end" : None,
                "total_worked" : 0,
                "is_extra" : False
            }
            salary_details.append(detail_data)
            continue

        elif (clock_in_hour == None and departure_hour != None):

            employee_entry_missing_days.append(day)
            continue

        elif (clock_in_hour != None and departure_hour == None):
            employee_exit_missing_days.append(day)
            continue


        worked_hours_in_day = Helpers.calculate_day_worked_hours(clock_in_hour, departure_hour, company_entry_hour, company_exit_hour, break_start, break_end, entry_tolerance_minutes, exit_tolerance_minutes, guy_worked_twice, is_manager)

        detail_data = {
            "date" : day["date"],
            "weekday" : is_weekday_date(day["date"]),
            "start" : clock_in_hour,
            "end" : departure_hour,
            "total_worked" : round(worked_hours_in_day, 3),
            "is_extra" : day["is_extra"]
        }

        salary_details.append(detail_data)
        total_employee_worked_hours += worked_hours_in_day
    
    ucretli_izin_days = []
    ucretli_izin_result = HR_InternalGetters.Internal_Get_Employee_Paid_Vacations(employee_name, employee_surname, year, month)
    data_list = ucretli_izin_result["data"]
    if len(data_list) > 0:
        for item in data_list:
            id = item["id"]
            name = item["name"]
            surname = item["surname"]
            vacation_start = item["vacation_start"]
            vacation_end = item["vacation_end"]

            vacation_datestring = datetime.strftime(vacation_start, '%d.%m.%Y')
            ucretli_izin_days.append(vacation_datestring)  


    hourly_salary = round(base_salary / 270, 3)

    weekday_normal_work_earned_salary = 0
    weekday_extra_earned_salary = 0

    lost_due_to_absence = 0
    total_lost = 0
    total_worked_hours = 0
    weekend_hour_count = 0

    weekday_work_hours = 0
    weekday_extra_hours = 0
    weekend_extra_hours = 0

    not_worked_days = 0


    special_days_payload = LocalRequests.Get_Special_Holidays()
    if "result_rows" in special_days_payload:
        special_days_result = special_days_payload["result_rows"]
        special_days = {}
        for day in special_days_result:
            dayday = f"{day['holiday_day']:02}"
            daymonth = f"{day['holiday_month']:02}"
            if day["holiday_year"].lower() == "her yıl":
                dayyear = year
            else:
                dayyear = f"{day['holiday_year']:04}"

            special_days[f"{dayday}-{daymonth}-{dayyear}"] = day["holiday_work_percent"] / 100
    else:
        special_days = {}
    
    religious_days = Helpers.get_religious_days(year)
    ramazan_bayrami_days = get_following_days(religious_days["ramazan_bayrami"], 3)
    kurban_bayrami_days = get_following_days(religious_days["kurban_bayrami"], 4)

    for day in salary_details:
        day_is_ramazan_bayrami = False
        day_is_kurban_bayrami = False
        day_is_special = False
        day_is_simple = False

        is_weekday = day["weekday"]
        worked_hours_in_day = day["total_worked"]
        
        total_extras = 0

        is_extra = day["is_extra"]
        day_date = day["date"]

        if day_date in ramazan_bayrami_days:
            day_is_ramazan_bayrami = True
            extra_multiplier = 2
            day["ramazan_bayrami"] = True
            day["extra_multiplier"] = extra_multiplier

        elif day_date in kurban_bayrami_days:
            day_is_kurban_bayrami = True 
            extra_multiplier = 2
            day["kurban_bayrami"] = True
            day["extra_multiplier"] = extra_multiplier

        elif day_date in special_days:
            day_is_special = True
            extra_multiplier = special_days[day_date]
            day["special_day"] = True
            day["extra_multiplier"] = extra_multiplier

        elif day_date in ucretli_izin_days:
            base_earned = total_daily_work_hour * hourly_salary
            weekday_normal_work_earned_salary += base_earned
            ucretli_izin_day_value += 1

        else:
            day_is_simple = True
            extra_multiplier = 1.5


        if is_weekday == True:
            if worked_hours_in_day > total_daily_work_hour:
                if (day_is_ramazan_bayrami or day_is_kurban_bayrami or day_is_special):
                    print(f"{employee_name} Special Day: {hourly_salary} - {extra_multiplier}")
                    base_earned = total_daily_work_hour * (hourly_salary)
                    extra_earned = (worked_hours_in_day - total_daily_work_hour) * (hourly_salary * extra_multiplier)
                    extra_earned += (worked_hours_in_day * hourly_salary * 2)
                
                else:
                    base_earned = total_daily_work_hour * hourly_salary
                    extra_earned = (worked_hours_in_day - total_daily_work_hour) * (hourly_salary * extra_multiplier)

                weekday_extra_hours += (worked_hours_in_day - total_daily_work_hour)
                weekday_normal_work_earned_salary += base_earned
                weekday_extra_earned_salary += extra_earned
                total_worked_hours += worked_hours_in_day
                weekday_work_hours += worked_hours_in_day

            elif (worked_hours_in_day <= total_daily_work_hour and worked_hours_in_day != 0):
                if is_extra:
                    extra_earned = worked_hours_in_day * (hourly_salary * extra_multiplier)
                    weekday_extra_hours += worked_hours_in_day
                    weekday_extra_earned_salary += extra_earned
                    total_worked_hours += worked_hours_in_day
                    weekday_work_hours += worked_hours_in_day

                else:
                    if (day_is_ramazan_bayrami or day_is_kurban_bayrami or day_is_special):
                        print(f"{employee_name} Special Day: {hourly_salary} - {extra_multiplier}")
                        print(hourly_salary, extra_multiplier, worked_hours_in_day)
                        if extra_multiplier == 2:
                            base_earned = worked_hours_in_day * (hourly_salary * 1)
                            extra_earned = worked_hours_in_day * (hourly_salary * 2)
                            weekday_extra_hours += worked_hours_in_day

                            print(f"{employee_name} = {base_earned} + {extra_earned} = {base_earned + extra_earned}")

                    else:
                        base_earned = worked_hours_in_day * hourly_salary
                        extra_earned = 0

                    weekday_normal_work_earned_salary += base_earned
                    weekday_extra_earned_salary += extra_earned
                    lost_due_to_absence = (total_daily_work_hour - worked_hours_in_day) * hourly_salary
                    total_lost += lost_due_to_absence
                    total_worked_hours += worked_hours_in_day
                    weekday_work_hours += worked_hours_in_day

            elif worked_hours_in_day == 0:
                if (day_is_ramazan_bayrami or day_is_kurban_bayrami or day_is_special):
                    base_earned = total_daily_work_hour * hourly_salary
                    weekday_normal_work_earned_salary += base_earned
                else:
                    not_worked_days += 1
                    base_earned = 0
                    lost_due_to_absence = total_daily_work_hour * hourly_salary
                    total_lost += lost_due_to_absence
                
        elif is_weekday == False:
            if worked_hours_in_day > 0:
                if part_time == False:
                    weekend_hour_count += total_daily_work_hour
                total_worked_hours += worked_hours_in_day
                weekend_extra_hours += worked_hours_in_day

            elif worked_hours_in_day == 0:
                if part_time == False:
                    total_worked_hours += worked_hours_in_day
                    weekend_hour_count += total_daily_work_hour


    weekends = json.loads(Helpers.get_weekend_days_of_month(year, month))
    weekend_day_count = len(weekends)

    total_day_count  = len(total_workdays_in_month) + weekend_day_count
    difference_to_30 = 30 - total_day_count

    weekend_base_hours = weekend_hour_count
    weekend_base_earned = weekend_base_hours * hourly_salary
    weekend_30day_equalization = ((difference_to_30) * total_daily_work_hour)
    weekend_base_final_earned = weekend_base_earned + (weekend_30day_equalization * hourly_salary)
    weekend_extra_work_earn = weekend_extra_hours * (hourly_salary * 2)

    weekday_total_earned = weekday_normal_work_earned_salary + weekday_extra_earned_salary
    final_earning = weekday_total_earned + weekend_base_final_earned + weekend_extra_work_earn


    total_absent_days_value = round((total_lost / hourly_salary) / total_daily_work_hour, 2)
    if total_day_count == 31:
        if weekday_work_hours > 45:
            if total_absent_days_value > 1:
                weekday_work_hours += total_daily_work_hour
                weekday_normal_work_earned_salary += total_daily_work_hour * hourly_salary


    advance_payment_amount = 0

    advance_payment_data = HR_InternalGetters.Internal_Get_Employee_Advance_Payments_Month(employee_name, employee_surname, year, month)
    if advance_payment_data["status"] == "ok":
        for item in advance_payment_data["data"]:
            advance_payment_amount += item["payment_amount"]
    
    final_earning = final_earning - advance_payment_amount


    return {
        "employee_register_number" : employee_register_number,
        "employee_name" : employee_name,
        "employee_surname" : employee_surname,
        "employee_company" : employee_company,
        "employee_department" : employee_department,
        "employee_profession" : employee_profession,
        "part_time" : part_time,

        "workshift_name" : workshift_name,
        "workshift_start" : company_entry_hour,
        "workshift_end" : company_exit_hour,
        "workshift_break_start" : company_break_start,
        "workshift_break_end" : company_break_end,
        "workshift_entry_tolerance" : entry_tolerance_minutes,
        "workshift_exit_tolerance" : exit_tolerance_minutes,

        "entry_missing_days" : employee_entry_missing_days,
        "exit_missing_days" : employee_exit_missing_days,
        "both_missing_days" : both_missing_days,

        "base_salary" : base_salary,
        "salary_hourly" : round(hourly_salary, 2),

        #Left Row
        "weekday_normal_work_days_value" : round(weekday_work_hours / total_daily_work_hour, 2),
        "weekday_normal_work_hours" : round(weekday_work_hours, 2),
        "weekday_normal_work_earned_salary" : round(weekday_normal_work_earned_salary, 2),
        "weekday_ek_mesai_hours" : round(weekday_extra_hours, 2),
        "weekday_ek_mesai_earned_salary" : round(weekday_extra_earned_salary, 2),
        
        "weekend_base_days_value" : round((weekend_base_hours + weekend_30day_equalization) / total_daily_work_hour, 2),
        "weekend_base_hours" : round(weekend_base_hours + weekend_30day_equalization, 2),
        "weekend_base_earned_salary" : round(weekend_base_final_earned, 2),
        "weekend_ek_mesai_hours" : round(weekend_extra_hours, 2),
        "weekend_ek_mesai_earned_salary" : round(weekend_extra_work_earn, 2),

        "ucretli_izin_days_value" : ucretli_izin_day_value,
        "ucretli_izin_hours" : ucretli_izin_day_value * total_daily_work_hour,
        "ucretli_izin_earned_salary" : ucretli_izin_day_value * total_daily_work_hour * salary_hourly,

        "total_ek_mesai_days_value" : round((weekday_extra_hours + weekend_extra_hours) / total_daily_work_hour, 2),
        "total_ek_mesai_hours" : round(weekday_extra_hours + weekend_extra_hours, 2),
        "total_ek_mesai_earned_salary" : round(weekday_extra_earned_salary + weekend_extra_work_earn),

        "ek_kazanc_value" : round(ek_kazanc_value, 2),

        #Right Row
        "total_absent_days_value" : round((total_lost / hourly_salary) / total_daily_work_hour, 2),
        "total_absent_hours" : round(total_lost / hourly_salary, 2),
        "total_absent_lost_price" : round(total_lost, 2),
        "total_fully_absent_day_count" : not_worked_days,
        "total_absent_day_value" : round(total_lost / hourly_salary / total_daily_work_hour, 2),

        "ucretsiz_izin_days" : round(ucretsiz_izin_days, 2),
        "ucretsiz_izin_hours" : round(ucretsiz_izin_hours, 2),
        "ucretsiz_izin_price" : round(ucretsiz_izin_price, 2),

        "avans_kesintisi_value" : round(advance_payment_amount, 2),

        "ek_kesinti_value" : round(ek_kesinti_value, 2),

        #Bottom Row Totals
        "total_worked_day_value" : round((weekday_work_hours + weekday_extra_hours + weekend_extra_hours + weekend_base_hours) / total_daily_work_hour, 2),
        "total_worked_hours" : round(weekday_work_hours + weekday_extra_hours + weekend_extra_hours + weekend_base_hours, 2),
        "total_final_earned" : round(final_earning, 2),

        #Extra Info
        "day_equalization_day_count" : difference_to_30,
        "day_equalization_price" : difference_to_30 * total_daily_work_hour,

        "total_real_workdays_in_month" : len(total_workdays_in_month),
        "total_real_work_hours_in_month" : total_work_hours_in_month,
        "employee_total_worked_days" : len(total_workdays_in_month) - not_worked_days,
        "total_weekend_days_in_month" : weekend_day_count,
        "salary_details" : salary_details,
        "employee_statistics_of_month" : []
    }

def calculate_employee_salary(employee_data, year, month):
    year = int(year)
    month = int(month)

    employee_register_number = str(employee_data["employee_register_number"])
    employee_result = HR_EmployeeHandler.Get_Specific_Employee_From_Database(employee_register_number)
    employee_details = employee_result["result_rows"][0]

    workshift_id = employee_details["shift_group_id"]
    workshift_details = HR_InternalGetters.Internal_Get_Employee_Workshift_Details(workshift_id)

    base_salary = employee_details["salary"]
    employee_name = employee_details["name"]
    employee_surname = employee_details["surname"]
    employee_department = employee_details["department_name"]
    employee_profession = employee_details["profession_name"]
    part_time = employee_details["part_time"]
    salary_hourly = employee_details["salary_hourly"]
    workshift_name = workshift_details[1]
    workshift_start = workshift_details[2]
    workshift_end = workshift_details[3]
    break_start = workshift_details[4]
    break_end = workshift_details[5]
    entry_tolerance = workshift_details[6]
    exit_tolerance = workshift_details[7]
    extra_percent = workshift_details[8]


    employee_company = employee_details["company_name"]

    employee_info_payload = {
        "employee_name" : employee_name,
        "employee_surname" : employee_surname,
        "employee_register_number" : employee_register_number,
        "employee_department" : employee_department,
        "employee_profession" : employee_profession,
        "part_time" : part_time,
        "salary_hourly" : salary_hourly,
        "workshift_name" : workshift_name,
        "entry_hour" : workshift_start,
        "exit_hour" : workshift_end,
        "break_start" : break_start,
        "break_end" : break_end,
        "entry_tolerance" : entry_tolerance,
        "exit_tolerance" : exit_tolerance,
        "extra_percentage" : extra_percent,
        "base_salary" : base_salary,
        "employee_company" : employee_company
    }

    employee_work_data = []

    data = {
        "type" : "salary_month",
        "employee_register_number" : employee_register_number,
        "year" : year,
        "month" : month
    }

    get_result = HR_AttendanceHandler.Get_Employee_Attendance_From_Database(data)

    attendance_info = get_result["result"]
    if attendance_info == None:
        pass #TODO FIX
    else:
        for unique_day in attendance_info:
            for item in attendance_info[unique_day]:
                if item["employee_register_id"] != employee_register_number:
                    continue
                if str(employee_register_number) == "16":
                    pass
                
                try:
                    try:
                        date_datetime_obj = datetime.strptime(item["entry"], '%Y-%m-%d %H:%M:%S')
                        date = date_datetime_obj.strftime('%d-%m-%Y')
                        if str(employee_register_number) == "16":
                            pass
                    except Exception as error:
                        if str(employee_register_number) == "16":
                            print(error)
                        print(error)
                        try:
                            date_datetime_obj = datetime.strptime(item["exit"], '%Y-%m-%d %H:%M:%S')
                            date = date_datetime_obj.strftime('%d-%m-%Y')
                            if str(employee_register_number) == "16":
                                print(date)
                        except Exception as error:
                            if str(employee_register_number) == "16":
                                print(f"NOTHING HAPPENED BRUH {item}")
                            pass
                    
                    try:
                        start_datetime_obj = datetime.strptime(item["entry"], '%Y-%m-%d %H:%M:%S')
                        start_time = start_datetime_obj.strftime('%H:%M')
                    except Exception as error:
                        start_time = None

                    try:
                        end_datetime_obj = datetime.strptime(item["exit"], '%Y-%m-%d %H:%M:%S')
                        end_time = end_datetime_obj.strftime('%H:%M')
                    except Exception as error:
                        end_time = None

                    if "is_extra" in item:
                        if item["is_extra"] == True:
                            data_to_append = {
                                "date" : date,
                                "start_time" : start_time,
                                "end_time" : end_time,
                                "weekday" : is_weekday(unique_day),
                                "is_extra" : True
                            }
                    else:
                        data_to_append = {
                            "date" : date,
                            "start_time" : start_time,
                            "end_time" : end_time,
                            "weekday" : is_weekday(unique_day),
                            "is_extra" : False
                        }

                    employee_work_data.append(data_to_append)
                except:
                    pass
    working_days = []
    all_days_of_month = json.loads(Helpers.get_all_days_of_month(year, month))

    for week in all_days_of_month:
        for day in week:
            date_info = {
                "date" : day,
                "weekday" : week[day]["weekday"]
            }
            working_days.append(date_info)


    for day in working_days:
        if any(item['date'] == day['date'] for item in employee_work_data):
            pass
        else:
            data_to_append = {
                "date" : day["date"],
                "start_time" : None,
                "end_time" : None,
                "weekday" : day["weekday"]
            }
            employee_work_data.append(data_to_append)

    sorted_employee_work_data = sorted(employee_work_data, key=lambda d: parse_date(d['date']))

    result = Calculate_Employee_Salary_Main(employee_info_payload, sorted_employee_work_data, year, month)
    return result


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, '%d-%m-%Y')
    except Exception:
        return datetime.strptime(date_string, '%d.%m.%Y')

def is_weekday(date_string):
    date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    if date.weekday() < 5:
        return True
    else:
        return False
    
def is_weekday_date(date_string):
    try:
        date = datetime.strptime(date_string, '%d-%m-%Y')
    except Exception:
        date = datetime.strptime(date_string, '%d.%m.%Y')


    if date.weekday() < 5:
        return True
    else:
        return False

def get_week_number(date_string):
    date = datetime.strptime(date_string, "%d-%m-%Y")
    return date.isocalendar()[1] 

def get_following_days(date_str, num_days):
    date_format = "%d-%m-%Y"
    start_date = datetime.strptime(date_str, date_format)
    date_list = [start_date + timedelta(days=i) for i in range(num_days)]
    return [date.strftime(date_format) for date in date_list]

def calculate_salaries(data):
    update_result = HR_AttendanceHandler.Refresh_Employee_Attendance()

    year = data["year"]
    month = data["month"]
    employees = data["employees"]


    result_list = []
    for employee_data in employees:
        result = calculate_employee_salary(employee_data, year, month)
        result_list.append(result)
    
    json_result = {
        "status" : "ok",
        "result_list" : result_list
    }

    return json_result




def calculate_terminated_employee_main(employee_info_payload, employee_work_data, year, month):

    ucretsiz_izin_days = 0
    ucretsiz_izin_hours = 0
    ucretsiz_izin_price = 0

    ucretli_izin_day_value = 0

    ek_kesinti_value = 0

    ek_kazanc_value = 0

    total_employee_worked_days = 0
    total_employee_worked_hours = 0
    employee_exit_missing_days = []
    employee_entry_missing_days = []
    both_missing_days = []
    salary_details = []

    employee_name = employee_info_payload["employee_name"]
    employee_surname = employee_info_payload["employee_surname"]
    employee_department = employee_info_payload["employee_department"]
    employee_profession = employee_info_payload["employee_profession"]
    employee_register_number = employee_info_payload["employee_register_number"]
    workshift_name = employee_info_payload["workshift_name"]
    part_time = employee_info_payload["part_time"]
    salary_hourly = employee_info_payload["salary_hourly"]

    company_entry_hour = employee_info_payload["entry_hour"]
    company_exit_hour = employee_info_payload["exit_hour"]
    company_break_start = employee_info_payload["break_start"]
    company_break_end = employee_info_payload["break_end"]
    entry_tolerance_minutes = employee_info_payload["entry_tolerance"]
    exit_tolerance_minutes = employee_info_payload["exit_tolerance"]
    extra_hour_multiplier = employee_info_payload["extra_percentage"]
    base_salary = employee_info_payload["base_salary"]

    if part_time == True:
        hourly_salary = salary_hourly
    else:
        hourly_salary = base_salary / 225

    weekday_normal_work_earned_salary = base_salary

    break_start = datetime.strptime(company_break_start, "%H:%M")
    break_end = datetime.strptime(company_break_end, "%H:%M")
    break_amount = break_end - break_start

    entry_time = datetime.strptime(company_entry_hour, "%H:%M")
    exit_time = datetime.strptime(company_exit_hour, "%H:%M")

    daily_total_hours = exit_time - entry_time
    daily_hours_after_break_subtracted = daily_total_hours - break_amount
    total_daily_work_hour = float(daily_hours_after_break_subtracted.seconds / 60 / 60)

    is_manager = False
    if employee_department == "İDARİ":
        total_daily_work_hour += 1
        is_manager = True

    # CREATE SALARY DATA

    for day in employee_work_data:
        try:
            date_of_day = datetime.strptime(day["date"], "%d-%m-%Y")
        except Exception:
            date_of_day = datetime.strptime(day["date"], "%d.%m.%Y")


        clock_in_hour = day["start_time"]
        departure_hour = day["end_time"]

        total_employee_worked_days += 1
        if (clock_in_hour == None and departure_hour == None):
            both_missing_days.append(day)
            total_employee_worked_days -= 1
            detail_data = {
                "date" : day["date"],
                "weekday" : is_weekday_date(day["date"]),
                "start" : None,
                "end" : None,
                "total_worked" : 0,
                "is_extra" : False
            }
            salary_details.append(detail_data)
            continue

        elif (clock_in_hour == None and departure_hour != None):
            employee_entry_missing_days.append(day)
            continue

        elif (clock_in_hour != None and departure_hour == None):
            employee_exit_missing_days.append(day)
            continue
        
        worked_hours_in_day = Helpers.calculate_day_worked_hours(clock_in_hour, departure_hour, company_entry_hour, company_exit_hour, break_start, break_end, entry_tolerance_minutes, exit_tolerance_minutes, is_manager)
        
        detail_data = {
            "date" : day["date"],
            "weekday" : is_weekday_date(day["date"]),
            "start" : clock_in_hour,
            "end" : departure_hour,
            "total_worked" : round(worked_hours_in_day, 3),
            "is_extra" : day["is_extra"]
        }
        salary_details.append(detail_data)

        total_employee_worked_hours += worked_hours_in_day
        
    ucretli_izin_days = []
    ucretli_izin_result = HR_InternalGetters.Internal_Get_Employee_Paid_Vacations(employee_name, employee_surname, year, month)
    data_list = ucretli_izin_result["data"]
    if len(data_list) > 0:
        for item in data_list:
            id = item["id"]
            name = item["name"]
            surname = item["surname"]
            vacation_start = item["vacation_start"]
            vacation_end = item["vacation_end"]

            vacation_datestring = datetime.strftime(vacation_start, '%d.%m.%Y')
            ucretli_izin_days.append(vacation_datestring)


    ### DAILY CALCULATION START
    hourly_salary = round(base_salary / 270, 3)

    weekday_normal_work_earned_salary = 0
    weekday_extra_earned_salary = 0

    lost_due_to_absence = 0
    total_lost = 0
    total_worked_hours = 0
    weekend_hour_count = 0

    weekday_work_hours = 0
    weekday_extra_hours = 0
    weekend_extra_hours = 0

    not_worked_days = 0


    special_days_payload = LocalRequests.Get_Special_Holidays()
    if "result_rows" in special_days_payload:
        special_days_result = special_days_payload["result_rows"]
        special_days = {}
        for day in special_days_result:
            dayday = f"{day['holiday_day']:02}"
            daymonth = f"{day['holiday_month']:02}"
            if day["holiday_year"].lower() == "her yıl":
                dayyear = year
            else:
                dayyear = f"{day['holiday_year']:04}"

            special_days[f"{dayday}-{daymonth}-{dayyear}"] = day["holiday_work_percent"] / 100
    else:
        special_days = {}
    religious_days = Helpers.get_religious_days(year)
    ramazan_bayrami_days = get_following_days(religious_days["ramazan_bayrami"], 3)
    kurban_bayrami_days = get_following_days(religious_days["kurban_bayrami"], 4)
    #TODO: Add permission days too


    for day in salary_details:
        day_is_ramazan_bayrami = False
        day_is_kurban_bayrami = False
        day_is_special = False
        day_is_simple = False

        is_weekday = day["weekday"]
        worked_hours_in_day = day["total_worked"]
        is_extra = day["is_extra"]
        day_date = day["date"]

        if day_date in ramazan_bayrami_days:
            day_is_ramazan_bayrami = True
            extra_multiplier = 2
            day["ramazan_bayrami"] = True
            day["extra_multiplier"] = extra_multiplier

        elif day_date in kurban_bayrami_days:
            day_is_kurban_bayrami = True 
            extra_multiplier = 2
            day["kurban_bayrami"] = True
            day["extra_multiplier"] = extra_multiplier

        elif day_date in special_days:
            day_is_special = True
            extra_multiplier = special_days[day_date]
            day["special_day"] = True
            day["extra_multiplier"] = extra_multiplier
        
        elif day_date in ucretli_izin_days:
            base_earned = total_daily_work_hour * hourly_salary
            weekday_normal_work_earned_salary += base_earned
            ucretli_izin_day_value += 1


        else:
            day_is_simple = True
            extra_multiplier = 1.5


        if is_weekday == True:
            if worked_hours_in_day > total_daily_work_hour:
                if (day_is_ramazan_bayrami or day_is_kurban_bayrami or day_is_special):
                    base_earned = total_daily_work_hour * (hourly_salary * extra_multiplier)
                    extra_earned = (worked_hours_in_day - total_daily_work_hour) * (hourly_salary * extra_multiplier)
                
                else:
                    base_earned = total_daily_work_hour * hourly_salary
                    extra_earned = (worked_hours_in_day - total_daily_work_hour) * (hourly_salary * extra_multiplier)

                weekday_extra_hours += (worked_hours_in_day - total_daily_work_hour)
                weekday_normal_work_earned_salary += base_earned
                weekday_extra_earned_salary += extra_earned
                total_worked_hours += worked_hours_in_day
                weekday_work_hours += worked_hours_in_day

            elif (worked_hours_in_day <= total_daily_work_hour and worked_hours_in_day != 0):
                if is_extra:
                    extra_earned = worked_hours_in_day * (hourly_salary * extra_multiplier)
                    weekday_extra_hours += worked_hours_in_day
                    weekday_extra_earned_salary += extra_earned
                    total_worked_hours += worked_hours_in_day
                    weekday_work_hours += worked_hours_in_day

                else:
                    if (day_is_ramazan_bayrami or day_is_kurban_bayrami or day_is_special):
                        base_earned = worked_hours_in_day * (hourly_salary * extra_multiplier)
                        print("DAY IS EXTRA")
                        print(hourly_salary, extra_multiplier, worked_hours_in_day)
                        if extra_multiplier == 2:
                            base_earned = worked_hours_in_day * (hourly_salary * 1)
                            extra_earned = worked_hours_in_day * (hourly_salary * 1)
                            weekday_extra_hours += worked_hours_in_day
                    else:
                        base_earned = worked_hours_in_day * hourly_salary

                    weekday_normal_work_earned_salary += base_earned
                    lost_due_to_absence = (total_daily_work_hour - worked_hours_in_day) * hourly_salary
                    total_lost += lost_due_to_absence
                    total_worked_hours += worked_hours_in_day
                    weekday_work_hours += worked_hours_in_day

            elif worked_hours_in_day == 0:
                if (day_is_ramazan_bayrami or day_is_kurban_bayrami or day_is_special):
                    base_earned = total_daily_work_hour * hourly_salary
                    weekday_normal_work_earned_salary += base_earned
                else:
                    not_worked_days += 1
                    base_earned = 0
                    lost_due_to_absence = total_daily_work_hour * hourly_salary
                    total_lost += lost_due_to_absence

        elif is_weekday == False:
            if worked_hours_in_day > 0:
                if part_time == False:
                    weekend_hour_count += total_daily_work_hour
                total_worked_hours += worked_hours_in_day
                weekend_extra_hours += worked_hours_in_day

            elif worked_hours_in_day == 0:
                if part_time == False:
                    total_worked_hours += worked_hours_in_day
                    weekend_hour_count += total_daily_work_hour


    weekend_base_hours = weekend_hour_count
    weekend_base_earned = weekend_base_hours * hourly_salary

    weekend_base_final_earned = weekend_base_earned * hourly_salary
    weekend_extra_work_earn = weekend_extra_hours * (hourly_salary * 2)

    weekday_total_earned = weekday_normal_work_earned_salary + weekday_extra_earned_salary
    final_earning = weekday_total_earned + weekend_base_final_earned + weekend_extra_work_earn

    advance_payment_amount = 0

    advance_payment_data = HR_InternalGetters.Internal_Get_Employee_Advance_Payments_Month(employee_name, employee_surname, year, month)
    if advance_payment_data["status"] == "ok":
        for item in advance_payment_data["data"]:
            advance_payment_amount += item["payment_amount"]
    
    final_earning = final_earning - advance_payment_amount

    
    return {
        "employee_name" : employee_name,
        "employee_surname" : employee_surname,
        "employee_department" : employee_department,
        "employee_profession" : employee_profession,
        "part_time" : part_time,

        "workshift_name" : workshift_name,
        "workshift_start" : company_entry_hour,
        "workshift_end" : company_exit_hour,
        "workshift_break_start" : company_break_start,
        "workshift_break_end" : company_break_end,
        "workshift_entry_tolerance" : entry_tolerance_minutes,
        "workshift_exit_tolerance" : exit_tolerance_minutes,

        "entry_missing_days" : employee_entry_missing_days,
        "exit_missing_days" : employee_exit_missing_days,
        "both_missing_days" : both_missing_days,

        "base_salary" : base_salary,
        "salary_hourly" : round(hourly_salary, 2),

        #Left Row
        "weekday_normal_work_days_value" : round(weekday_work_hours / total_daily_work_hour, 2),
        "weekday_normal_work_hours" : round(weekday_work_hours, 2),
        "weekday_normal_work_earned_salary" : round(weekday_normal_work_earned_salary, 2),
        "weekday_ek_mesai_hours" : round(weekday_extra_hours, 2),
        "weekday_ek_mesai_earned_salary" : round(weekday_extra_earned_salary, 2),
        
        "weekend_base_days_value" : round(weekend_base_hours / total_daily_work_hour, 2),
        "weekend_base_hours" : weekend_base_hours,
        "weekend_base_earned_salary" : round(weekend_base_final_earned, 2),
        "weekend_ek_mesai_hours" : round(weekend_extra_hours, 2),
        "weekend_ek_mesai_earned_salary" : round(weekend_extra_work_earn, 2),

        "ucretli_izin_days_value" : ucretli_izin_day_value,
        "ucretli_izin_hours" : ucretli_izin_day_value * total_daily_work_hour,
        "ucretli_izin_earned_salary" : ucretli_izin_day_value * total_daily_work_hour * salary_hourly,

        "total_ek_mesai_days_value" : round((weekday_extra_hours + weekend_extra_hours) / total_daily_work_hour, 2),
        "total_ek_mesai_hours" : round(weekday_extra_hours + weekend_extra_hours, 2),
        "total_ek_mesai_earned_salary" : round(weekday_extra_earned_salary + weekend_extra_work_earn),

        "ek_kazanc_value" : round(ek_kazanc_value, 2),

        #Right Row
        "total_absent_days_value" : round((total_lost / hourly_salary) / total_daily_work_hour, 2),
        "total_absent_hours" : round(total_lost / hourly_salary, 2),
        "total_absent_lost_price" : round(total_lost, 2),
        "total_fully_absent_day_count" : not_worked_days,
        "total_absent_day_value" : round(total_lost / hourly_salary / total_daily_work_hour, 2),

        "ucretsiz_izin_days" : round(ucretsiz_izin_days, 2),
        "ucretsiz_izin_hours" : round(ucretsiz_izin_hours, 2),
        "ucretsiz_izin_price" : round(ucretsiz_izin_price, 2),

        "avans_kesintisi_value" : round(advance_payment_amount, 2),

        "ek_kesinti_value" : round(ek_kesinti_value, 2),

        #Bottom Row Totals
        "total_worked_day_value" : round((weekday_work_hours + weekday_extra_hours + weekend_extra_hours + weekend_base_hours) / total_daily_work_hour, 2),
        "total_worked_hours" : round(weekday_work_hours + weekday_extra_hours + weekend_extra_hours + weekend_base_hours, 2),
        "total_final_earned" : round(final_earning, 2),

        #Extra Info
        "salary_details" : salary_details,
        "employee_statistics_of_month" : []
    }

def calculate_terminated_employee_payment(data):
    employee_register_number = data["employee_register_number"]
    employee_result = HR_EmployeeHandler.Get_Specific_Employee_From_Database(employee_register_number)
    employee_details = employee_result["result_rows"][0]

    workshift_id = employee_details["shift_group_id"]
    workshift_details = HR_InternalGetters.Internal_Get_Employee_Workshift_Details(workshift_id)

    base_salary = employee_details["salary"]
    employee_name = employee_details["name"]
    employee_surname = employee_details["surname"]
    employee_department = employee_details["department_name"]
    employee_profession = employee_details["profession_name"]
    part_time = employee_details["part_time"]
    salary_hourly = employee_details["salary_hourly"]
    workshift_name = workshift_details[1]
    workshift_start = workshift_details[2]
    workshift_end = workshift_details[3]
    break_start = workshift_details[4]
    break_end = workshift_details[5]
    entry_tolerance = workshift_details[6]
    exit_tolerance = workshift_details[7]
    extra_percent = workshift_details[8]

    employee_info_payload = {
        "employee_name" : employee_name,
        "employee_surname" : employee_surname,
        "employee_register_number" : employee_register_number,
        "employee_department" : employee_department,
        "employee_profession" : employee_profession,
        "part_time" : part_time,
        "salary_hourly" : salary_hourly,
        "workshift_name" : workshift_name,
        "entry_hour" : workshift_start,
        "exit_hour" : workshift_end,
        "break_start" : break_start,
        "break_end" : break_end,
        "entry_tolerance" : entry_tolerance,
        "exit_tolerance" : exit_tolerance,
        "extra_percentage" : extra_percent,
        "base_salary" : base_salary
    }

    employee_work_data = []



    employee_name = data["employee_name"]
    employee_surname = data["employee_surname"]
    exit_date_string = data["exit_date"]
    will_calculate_former_month = not bool(data["will_calculate_former_month"])
    
    exit_date = datetime.strptime(exit_date_string, '%d.%m.%Y')

    year = exit_date.year
    month = exit_date.month

    if will_calculate_former_month:
        previous_month = exit_date.month - 1
        if previous_month == 0:
            previous_month = 12
        first_day = exit_date.replace(month=previous_month, day=1, hour=0, minute=0, second=0)
        while first_day.weekday() > 4:
            first_day = first_day.replace(day=first_day.day + 1)

        start_datestring = first_day.strftime('%Y-%m-%d %H:%M:%S')
        exit_date = exit_date.replace(hour=23, minute=59, second=59)
        end_datestring = exit_date.strftime('%Y-%m-%d %H:%M:%S')

    else:
        first_day = exit_date.replace(day=1, hour=0, minute=0, second=0)
        while first_day.weekday() > 4:
            first_day = first_day.replace(day=first_day.day + 1)
        start_datestring = first_day.strftime('%Y-%m-%d %H:%M:%S')
        exit_date = exit_date.replace(hour=23, minute=59, second=59)
        end_datestring = exit_date.strftime('%Y-%m-%d %H:%M:%S')

    data = {
        "type" : "attendance_general2",
        "employee_register_number" : employee_register_number,
        "start_date_string" : start_datestring,
        "end_date_string" : end_datestring
    }

    get_result = HR_AttendanceHandler.Get_Employee_Attendance_From_Database(data)

    attendance_info = get_result["result"]
    if attendance_info == None:
        pass
    else:
        for unique_day in attendance_info:
            for item in attendance_info[unique_day]:
                if str(item["employee_register_id"]) != str(employee_register_number):
                    continue
                
                try:
                    try:
                        date_datetime_obj = datetime.strptime(item["entry"], '%Y-%m-%d %H:%M:%S')
                        date = date_datetime_obj.strftime('%d.%m.%Y')
                    except Exception as error:
                        print("SERIOUS PROBLEM 1")
                        LogError(error)
                    
                    try:
                        start_datetime_obj = datetime.strptime(item["entry"], '%Y-%m-%d %H:%M:%S')
                        start_time = start_datetime_obj.strftime('%H:%M')
                    except Exception as error:
                        start_time = None

                    try:
                        end_datetime_obj = datetime.strptime(item["exit"], '%Y-%m-%d %H:%M:%S')
                        end_time = end_datetime_obj.strftime('%H:%M')
                    except Exception as error:
                        end_time = None

                    data_to_append = {
                        "date" : date,
                        "start_time" : start_time,
                        "end_time" : end_time,
                        "weekday" : is_weekday(unique_day)
                    }

                    employee_work_data.append(data_to_append)
                except:
                    pass
    
    between_days = []
    
    date1 = datetime.strptime(start_datestring, '%Y-%m-%d %H:%M:%S')
    date2 = datetime.strptime(end_datestring, '%Y-%m-%d %H:%M:%S')
    total_days = (date2 - date1).days
    for i in range(total_days + 1):
        current_date = date1 + timedelta(days=i)
        date_dict = {
            "date": current_date.strftime("%d.%m.%Y"),
            "weekday": current_date.weekday() < 5
        }
        between_days.append(date_dict)
    
    for day in between_days:
        if any(item['date'] == day['date'] for item in employee_work_data):
            pass
        else:
            data_to_append = {
                "date" : day["date"],
                "start_time" : None,
                "end_time" : None,
                "weekday" : day["weekday"]
            }
            employee_work_data.append(data_to_append)


    sorted_employee_work_data = sorted(employee_work_data, key=lambda d: parse_date(d['date']))
    debt_result = calculate_terminated_employee_main(employee_info_payload, sorted_employee_work_data, year, month)

    final_result = Printer_Master.Print_Terminated_Employee_Signed(debt_result)
    return final_result

def get_month_name(month_number):
    months = {
        1: "Ocak",
        2: "Şubat",
        3: "Mart",
        4: "Nisan",
        5: "Mayıs",
        6: "Haziran",
        7: "Temmuz",
        8: "Ağustos",
        9: "Eylül",
        10: "Ekim",
        11: "Kasım",
        12: "Aralık"
    }

    return months.get(month_number, "Invalid month")

def calculate_general_expenses(data):
    year = int(data["year"])
    month = int(data["month"])
    employees = HR_EmployeeHandler.Get_Employees_From_Database(data)

    all_employees = []
    for employee in employees["result_rows"]:
        if employee["left"] == "false":
            employee_data = {
                "employee_register_number" : employee["register_number"],
                "employee_company" : employee["company_name"]
            }
            all_employees.append(employee_data)
    
    final_data = {
        "year" : year,
        "month" : month,
        "employees" : all_employees
    }
    salaries_result = calculate_salaries(final_data)

    month_name = get_month_name(month)
    print_result = Printer_Master.Print_General_Personnel_Expenses(salaries_result, year, month_name)
    return print_result