import traceback, re, os, logging
from flask import Flask, request
from os import path, makedirs
from libs import LocalRequests, CloudRequests, Utilities
from libs.Local_Requests import HR_AttendanceHandler, HR_EmployeeHandler, HR_SalaryCalculator, HR__Departments, HR__SubDepartments, HR__Professions, HR__Workshifts, HR__Companies, Printer_Master
from config_setter import is_home

from libs.routes_warehouse import warehouse_routes

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass


app = Flask(__name__)
app.register_blueprint(warehouse_routes)


@app.route('/')
def hello_world():
    return ''



#################################
# For local connections on-site #
#################################


# region HUMAN RESOURCES

# region EMPLOYEES

@app.route('/add-employee', methods=['POST'])
def Handle_Add_Employee_To_Database():
    try:
        data = request.json
    except Exception as error:
        print(error)
    data_received = data['data_sent']
    response_data = HR_EmployeeHandler.Add_Employee_To_Database(data_received)
    return response_data



def sanitize_filename(filename):
    return re.sub(r'\W+', '_', filename)


@app.route('/upload-personnel-file', methods=['POST'])
def Handle_Personnel_File_Upload():
    form_data = request.form


    sender = form_data.get('sender')
    device_uuid = form_data.get('itkn')
    file_type = form_data.get("file_type")

    print(form_data)
    print(request.data)

    if 'pdf_file' not in request.files:
        response_data = {"status" : "failed"}
    else:
        pdf_file = request.files['pdf_file']

        file_name = pdf_file.filename
        file_name = file_name.replace("=5F","_").replace("?utf-8?Q?","").replace("=C4=B0","I").replace("?=","").replace("=","")
        sanitized_name = file_name


        print(sanitized_name)
        print(file_type)

        if not path.exists(f"local_storage/personnel_files/{sanitized_name.replace(f'{file_type}.pdf','')}/"):
            makedirs(f"local_storage/personnel_files/{sanitized_name.replace(f'{file_type}.pdf','')}/")

        pdf_file.save(f"local_storage/personnel_files/{sanitized_name.replace(f'{file_type}.pdf','')}/{sanitized_name}")


        response_data = {"status" : "ok"}

    return response_data


@app.route('/upload-photo-file', methods=['POST'])
def Handle_Photo_File_Upload():
    form_data = request.form

    sender = form_data.get('sender')
    device_uuid = form_data.get('itkn')

    if 'image' not in request.files:
        response_data = {"status" : "failed"}
    else:
        image_file = request.files['image']
        image_file.save('local_storage/employee_photos/' + image_file.filename)
        response_data = {"status" : "ok"}


    return response_data



@app.route('/get-employees', methods=['POST'])
def Handle_Get_Employees():
    data = request.json
    response_data = HR_EmployeeHandler.Get_Employees_From_Database(data)

    return response_data

@app.route('/edit-employee', methods=['POST'])
def Handle_Edit_Employee():
    data = request.json
    data_received = data['data_sent']
    response_data = HR_EmployeeHandler.Edit_Employee(data_received)
    return response_data

@app.route('/set-employee-left', methods=['POST'])
def Handle_Set_Employee_Left():
    data = request.json
    data_received = data['data_sent']
    response_data = HR_EmployeeHandler.Set_Employee_Left(data_received)

    response = app.response_class(response=response_data, status=200, mimetype='application/json')
    return response

@app.route('/remove-employee', methods=['POST'])
def Hanlde_Remove_Employee():
    data = request.json
    data_received = data['data_sent']
    response_data = HR_EmployeeHandler.Remove_Employee_From_Database(data_received)

    response = app.response_class(response=response_data, status=200, mimetype='application/json')
    return response

# endregion

# region EMPLOYEE ATTENDANCE

import subprocess, psutil, time, os

def restart_app(app_name, wait_time):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == app_name:
            print(proc.info)
            proc.kill()
            print("killed")
            time.sleep(1)
            break
    
    try:
        current_directory = os.getcwd()
        filename = 'startface.bat'
        file_path = os.path.join(current_directory, filename)
        subprocess.run(file_path)

    except Exception as error:
        LogError(error)

    time.sleep(wait_time)
    
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == app_name:
            print(f"restarted")
            return

    print("not running")

@app.route('/update-attendance', methods=['POST'])
def Handle_Update_Attendance():
    data = request.json

    try:
        if not is_home:
            restart_app("FaceRecognitionTerminal_v1_0.exe", 5)
    except Exception as error:
        print(error)

    response_data = HR_AttendanceHandler.Refresh_Employee_Attendance()
    return response_data

@app.route('/get-attendance', methods=['POST'])
def Handle_Get_Attendance():
    data = request.json
    data_sent = data['data_sent']
    print(data)

    response_data = HR_AttendanceHandler.Refresh_Employee_Attendance()
    print(response_data)
    
    response_data = HR_AttendanceHandler.Get_Employee_Attendance_From_Database(data_sent)
    return response_data

@app.route('/change-attendance', methods=['POST'])
def Handle_Change_Attendance():
    data = request.json
    data_sent = data['data_sent']
    response_data = HR_AttendanceHandler.Change_Employee_Attendance(data_sent)
    return response_data

@app.route('/calculate-puantaj-secilenler', methods=['POST'])
def Handle_Get_Puantaj():
    data = request.json
    data_sent = data['data_sent']
    employees = data_sent["employees"]
    employees_data = []

    # print(data_sent)
    for employee in employees:
        
        employee["type"] = "salary_month"
        employee["year"] = data_sent["year"]
        employee["month"] = data_sent["month"]

        result = HR_SalaryCalculator.calculate_employee_salary(employee, data_sent["year"], data_sent["month"])

        new_data = {
            "name": result["employee_name"],
            "surname": result["employee_surname"],
            "register_number": result["employee_register_number"],
            "company": result["employee_company"],
            "salary_details": result["salary_details"],
            "total_ek_mesai_hours": result["total_ek_mesai_hours"],
            "total_absent_hours": result["total_absent_hours"]
        }
        hourly_salary = result["salary_hourly"]


        employees_data.append(new_data)
    
    print_result = Printer_Master.Print_Attendance(employees_data, data_sent["year"], data_sent["month"])
    result = {"status" : "ok", "pdf" : print_result["pdf"]}
    return result


# endregion

# region DEPARTMENTS

@app.route('/get-departments', methods=['POST'])
def Handle_Get_Departments():
    data = request.json
    response_data = HR__Departments.Get_Departments_From_Database(data)
    return response_data

@app.route('/add-department', methods=['POST'])
def Handle_Add_Department():
    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = HR__Departments.Add_Department_To_Database(data_received)
    return response_data

@app.route('/edit-department', methods=['POST'])
def Handle_Edit_Department():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Departments.Edit_Department(data_received)
    return response_data

@app.route('/remove-department', methods=['POST'])
def Handle_Remove_Department():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Departments.Remove_Department(data_received)
    return response_data

# endregion

# region SUB DEPARTMENTS

@app.route('/get-sub-departments', methods=['POST'])
def Handle_Get_SubDepartments():
    data = request.json
    response_data = HR__SubDepartments.Get_SubDepartments_From_Database(data)
    return response_data

@app.route('/add-sub-department', methods=['POST'])
def Handle_Add_SubDepartment():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__SubDepartments.Add_SubDepartment_To_Database(data_received)
    return response_data

@app.route('/edit-sub-department', methods=['POST'])
def Handle_Edit_SubDepartment():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__SubDepartments.Edit_SubDepartment(data_received)
    return response_data

@app.route('/remove-sub-department', methods=['POST'])
def Handle_Remove_SubDepartment():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__SubDepartments.Remove_SubDepartment(data_received)
    return response_data


# endregion

# region PROFESSIONS

@app.route('/get-professions', methods=['POST'])
def Handle_Get_Professions():
    data = request.json
    response_data = HR__Professions.Get_Professions_From_Database(data)

    return response_data

@app.route('/add-profession', methods=['POST'])
def Handle_Add_Profession():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Professions.Add_Profession_To_Database(data_received)
    return response_data

@app.route('/edit-profession', methods=['POST'])
def Handle_Edit_Profession():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Professions.Edit_Profession(data_received)
    return response_data

@app.route('/remove-profession', methods=['POST'])
def Handle_Remove_Profession():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Professions.Remove_Profession(data_received)
    return response_data

# endregion

# region WORKSHIFTS

@app.route('/get-workshifts', methods=['POST'])
def Handle_Get_Workshifts():
    try:
        data = request.json
        response_data = HR__Workshifts.Get_Workshifts_From_Database(data)
        return response_data
    except Exception as error:
        LogError(error)

@app.route('/add-workshift', methods=['POST'])
def Handle_Add_Workshift():
    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = HR__Workshifts.Add_Workshift_To_Database(data_received)
    return response_data

@app.route('/edit-workshift', methods=['POST'])
def Handle_Edit_Workshift():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Workshifts.Edit_Workshift(data_received)
    return response_data

@app.route('/remove-workshift', methods=['POST'])
def Handle_Remove_Workshift():
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Workshifts.Remove_Workshift(data_received)
    return response_data

# endregion

# region COMPANIES

@app.route('/get-companies', methods=['POST'])
def Handle_Get_Companies():
    data = request.json
    response_data = HR__Companies.Get_Companies_From_Database(data)
    print("**************")
    return response_data

# endregion

# region SALARY CALCULATION
@app.route('/calculate-salaries', methods=['POST'])
def Handle_Calculate_Salary():
    data = request.json
    data_received = data['data_sent']
    response_data = HR_SalaryCalculator.calculate_salaries(data_received)
    return response_data


@app.route('/calculate-general-personnel-expenses', methods=['POST'])
def Handle_Calculate_General_Personnel_Expenses():
    data = request.json
    data_received = data['data_sent']
    response_data = HR_SalaryCalculator.calculate_general_expenses(data_received)
    return response_data

# endregion

# region TERMINATE EMPLOYEE
@app.route('/calculate-terminated-employee', methods=['POST'])
def Handle_Calculate_Terminated_Employee():
    data = request.json
    data_received = data['data_sent']
    response_data = HR_SalaryCalculator.calculate_terminated_employee_payment(data_received)
    return response_data

@app.route('/terminate-employee', methods=['POST'])
def Handle_Terminate_Employee():
    data = request.json
    data_received = data['data_sent']
    response_data = HR_EmployeeHandler.Set_Employee_Left(data_received)
    return response_data
# endregion


# region GENERAL HR STATISTICS

@app.route('/get-today-worker-statistics', methods=['POST'])
def Handle_Get_Today_Worker_Statistics():
    data = request.json
    response_data = HR_EmployeeHandler.Get_Absent_Employees_From_Database_Today(data)
    return response_data

@app.route('/get-this-week-attendance-statistics', methods=['POST'])
def Handle_Get_This_Week_Attendance_Statistics():
    pass

@app.route('/get-overall-real-work-hour-statistics', methods=['POST'])
def Handle_Get_Overall_Real_Work_Hour_Statistics():
    pass

@app.route('/get-monthly-total-personnel-expenses', methods=['POST'])
def Handle_Get_Monthly_Total_Personnel_Expenses():
    pass

@app.route('/get-highest-rating-employee-statistics', methods=['POST'])
def Handle_Get_Highest_Rating_Employee_Statistics():
    pass


# endregion



# region ADVANCE PAYMENTS

@app.route('/add-advance-payment', methods=['POST'])
def Handle_Add_Advance_payment():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Add_Advance_Payment(data_received)
    return response_data

@app.route('/get-advance-payments', methods=['POST'])
def Handle_Get_Advance_Payments():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Get_Advance_Payments(data_received)
    return response_data

@app.route('/get-advance-payment-specific', methods=['POST'])
def Handle_GET_Advance_Payment_Specific():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Get_Specific_Advance_Payment(data_received)
    return response_data

@app.route('/edit-advance-payment', methods=['POST'])
def Handle_Edit_Advance_Payment():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Edit_Advance_Payment(data_received)
    return response_data

@app.route('/remove-advance-payment', methods=['POST'])
def Handle_Remove_Advance_Payment():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Remove_Advance_Payment(data_received)
    return response_data

# endregion

# region EXTRA PAYMENTS

@app.route('/add-extra-payment', methods=['POST'])
def Handle_Add_Extra_payment():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Add_Extra_Payment(data_received)
    return response_data

@app.route('/get-extra-payments', methods=['POST'])
def Handle_Get_Extra_Payments():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Get_Extra_Payments(data_received)
    return response_data

@app.route('/get-extra-payment-specific', methods=['POST'])
def Handle_GET_Extra_Payment_Specific():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Get_Specific_Extra_Payment(data_received)
    return response_data

@app.route('/edit-extra-payment', methods=['POST'])
def Handle_Edit_Extra_Payment():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Edit_Extra_Payment(data_received)
    return response_data

@app.route('/remove-extra-payment', methods=['POST'])
def Handle_Remove_Extra_Payment():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Remove_Extra_Payment(data_received)
    return response_data

# endregion

# region PERMISSIONS - VACATIONS

@app.route('/add-permission', methods=['POST'])
def Handle_Add_Permission():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Add_Permission(data_received)
    return response_data

@app.route('/get-permissions', methods=['POST'])
def Handle_Get_Permissions():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Get_Permissions(data_received)
    return response_data

@app.route('/get-permission-specific', methods=['POST'])
def Handle_GET_Permission_Specific():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Get_Specific_Permission(data_received)
    return response_data

@app.route('/edit-permission', methods=['POST'])
def Handle_Edit_Permission():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Edit_Permission(data_received)
    return response_data

@app.route('/remove-permission', methods=['POST'])
def Handle_Remove_Permission():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Remove_Permission(data_received)
    return response_data

# endregion

# region SPECIAL HOLIDAYS

@app.route('/add-special-holiday', methods=['POST'])
def Handle_Add_Special_Holiday():
    try:
        data = request.json
        data_received = data['data_sent']
        response_data = LocalRequests.Add_Special_Holiday(data_received)
        return response_data
    except Exception as error:
        LogError(error)

@app.route('/get-special-holidays', methods=['POST'])
def Handle_Get_Special_Holidays():
    data = request.json
    response_data = LocalRequests.Get_Special_Holidays()
    print(response_data)
    return response_data

@app.route('/edit-special-holiday', methods=['POST'])
def Handle_Edit_Special_Holiday():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Edit_Special_Holiday(data_received)
    return response_data

@app.route('/remove-special-holiday', methods=['POST'])
def Handle_Remove_Special_Holiday():
    data = request.json
    data_received = data['data_sent']
    response_data = LocalRequests.Remove_Special_Holiday(data_received)
    return response_data


# endregion



# endregion


@app.route('/notifications', methods=['POST'])
def NotificationRequest():
    data = request.json

    print(data)

    if data['requestName'] == 'CheckNotifications':
        localResult = LocalRequests.Handle_Notification_Checked(data)
        cloudResult = CloudRequests.Handle_Notification_Checked(data)
    

    return localResult

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)





@app.route('/json-to-excel', methods=['POST'])
def HandleExcelConversion():
    data = request.json

    data_sent = data["data_sent"]
    main_header = data["header"]

    localResult = Utilities.convert_data_to_XLSX(data_sent, main_header)
    return localResult



if __name__ == '__main__':
    try:
        if not is_home:
            restart_app("FaceRecognitionTerminal_v1_0.exe", 1)
        app.run(host='192.168.1.11', port=5000, debug=True)
        pass

    except Exception as error:
        LogError(error)