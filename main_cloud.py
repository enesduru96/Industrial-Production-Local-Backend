import traceback, re, os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

from os import path, makedirs
from libs import LocalRequests, CloudRequests, Utilities
from libs.Local_Requests import HR_AttendanceHandler, HR_EmployeeHandler, HR_SalaryCalculator, HR__Departments, HR__SubDepartments, HR__Professions, HR__Workshifts, HR__Companies

from libs.routes_warehouse_cloud import warehouse_routes

from datetime import timedelta


#################################
# For wireless requests outside #
#################################

def LogError(err:Exception):
    if (err in [KeyboardInterrupt, SystemExit]) or (str(err) == "'coroutine' object is not iterable"):
        pass

    print(f"    Traceback: {traceback.format_exc()}")
    print(f"    An Error Occured: {err}")
    pass


def check_user_access(headers):
    access_granted = False   
    if headers["User-Agent"] != "user-companyname" or headers["Connection"] != "keep-alive":
        access_granted = False
    else:
        access_granted = True

    return access_granted


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "companynameflask_1923_2023_xxvxq!!#>£"
jwt = JWTManager(app)
app.register_blueprint(warehouse_routes)


@app.route("/login", methods=["POST"])
def login():
    print(request.headers["User-Agent"])
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Replace this with your user validation logic
    if username != "companyname" or password != "companypassword":
        return jsonify({"msg": "x"}), 401

    # Create JWT token
    access_expires = timedelta(hours=1)  # Örneğin, 1 saat
    access_token = create_access_token(identity={"username": username}, expires_delta=access_expires)

    return {
        "status" : "ok",
        "access_token": access_token
    }


# region HUMAN RESOURCES

# region EMPLOYEES

@app.route('/add-employee', methods=['POST'])
@jwt_required()
def Handle_Add_Employee_To_Database():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def Handle_Get_Employees():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    response_data = HR_EmployeeHandler.Get_Employees_From_Database(data)

    return response_data

@app.route('/edit-employee', methods=['POST'])
@jwt_required()
def Handle_Edit_Employee():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = HR_EmployeeHandler.Edit_Employee(data_received)
    return response_data

@app.route('/set-employee-left', methods=['POST'])
@jwt_required()
def Handle_Set_Employee_Left():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = HR_EmployeeHandler.Set_Employee_Left(data_received)

    response = app.response_class(response=response_data, status=200, mimetype='application/json')
    return response

@app.route('/remove-employee', methods=['POST'])
@jwt_required()
def Hanlde_Remove_Employee():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
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
@jwt_required()
def Handle_Update_Attendance():
    data = request.json
    response_data = HR_AttendanceHandler.Refresh_Employee_Attendance()
    return response_data

@app.route('/get-attendance', methods=['POST'])
@jwt_required()
def Handle_Get_Attendance():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_sent = data['data_sent']

    response_data = HR_AttendanceHandler.Get_Employee_Attendance_From_Database(data_sent)
    return response_data

@app.route('/change-attendance', methods=['POST'])
@jwt_required()
def Handle_Change_Attendance():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_sent = data['data_sent']
    response_data = HR_AttendanceHandler.Change_Employee_Attendance(data_sent)
    return response_data

@app.route('/get-puantaj', methods=['POST'])
@jwt_required()
def Handle_Get_Puantaj():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_sent = data['data_sent']
    employees = data_sent["employees"]
    employees_data = []
    for employee in employees:
        employee_data = HR_AttendanceHandler.Get_Employee_Attendance_From_Database(employee)
        employees_data.append(employee_data)
    
    result_list = []
    for item in employees_data:
        employee_info = {}
        employee_info["puantaj_info"] = []

        for unique_day in item["result"]:
            employee_register_id = item["result"][unique_day][0]["employee_register_id"]
            employee_name = item["result"][unique_day][0]["employee_name"]
            employee_surname = item["result"][unique_day][0]["employee_surname"]
            employee_company = item["result"][unique_day][0]["employee_company"]
            entry = item["result"][unique_day][0]["entry"]
            exit = item["result"][unique_day][0]["exit"]

            employee_info["employee_register_id"] = employee_register_id
            employee_info["employee_name"] = employee_name
            employee_info["employee_surname"] = employee_surname
            employee_info["employee_company"] = employee_company
            
            day_data = {
                "day" : unique_day,
                "entry" : entry,
                "exit" : exit
            }
            employee_info["puantaj_info"].append(day_data)
        

        result_list.append(employee_info)

    result = {"status" : "ok", "result_list" : result_list}
    return result

# endregion

# region DEPARTMENTS

@app.route('/get-departments', methods=['POST'])
@jwt_required()
def Handle_Get_Departments():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    response_data = HR__Departments.Get_Departments_From_Database(data)
    return response_data

@app.route('/add-department', methods=['POST'])
@jwt_required()
def Handle_Add_Department():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = HR__Departments.Add_Department_To_Database(data_received)
    return response_data

@app.route('/edit-department', methods=['POST'])
@jwt_required()
def Handle_Edit_Department():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Departments.Edit_Department(data_received)
    return response_data

@app.route('/remove-department', methods=['POST'])
@jwt_required()
def Handle_Remove_Department():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Departments.Remove_Department(data_received)
    return response_data

# endregion

# region SUB DEPARTMENTS

@app.route('/get-sub-departments', methods=['POST'])
@jwt_required()
def Handle_Get_SubDepartments():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    response_data = HR__SubDepartments.Get_SubDepartments_From_Database(data)
    return response_data

@app.route('/add-sub-department', methods=['POST'])
@jwt_required()
def Handle_Add_SubDepartment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__SubDepartments.Add_SubDepartment_To_Database(data_received)
    return response_data

@app.route('/edit-sub-department', methods=['POST'])
@jwt_required()
def Handle_Edit_SubDepartment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__SubDepartments.Edit_SubDepartment(data_received)
    return response_data

@app.route('/remove-sub-department', methods=['POST'])
@jwt_required()
def Handle_Remove_SubDepartment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__SubDepartments.Remove_SubDepartment(data_received)
    return response_data


# endregion

# region PROFESSIONS

@app.route('/get-professions', methods=['POST'])
@jwt_required()
def Handle_Get_Professions():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    response_data = HR__Professions.Get_Professions_From_Database(data)

    return response_data

@app.route('/add-profession', methods=['POST'])
@jwt_required()
def Handle_Add_Profession():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Professions.Add_Profession_To_Database(data_received)
    return response_data

@app.route('/edit-profession', methods=['POST'])
@jwt_required()
def Handle_Edit_Profession():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Professions.Edit_Profession(data_received)
    return response_data

@app.route('/remove-profession', methods=['POST'])
@jwt_required()
def Handle_Remove_Profession():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Professions.Remove_Profession(data_received)
    return response_data

# endregion

# region WORKSHIFTS

@app.route('/get-workshifts', methods=['POST'])
@jwt_required()
def Handle_Get_Workshifts():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    try:
        data = request.json
        response_data = HR__Workshifts.Get_Workshifts_From_Database(data)
        return response_data
    except Exception as error:
        LogError(error)

@app.route('/add-workshift', methods=['POST'])
@jwt_required()
def Handle_Add_Workshift():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = HR__Workshifts.Add_Workshift_To_Database(data_received)
    return response_data

@app.route('/edit-workshift', methods=['POST'])
@jwt_required()
def Handle_Edit_Workshift():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Workshifts.Edit_Workshift(data_received)
    return response_data

@app.route('/remove-workshift', methods=['POST'])
@jwt_required()
def Handle_Remove_Workshift():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent']
    response_data = HR__Workshifts.Remove_Workshift(data_received)
    return response_data

# endregion

# region COMPANIES

@app.route('/get-companies', methods=['POST'])
@jwt_required()
def Handle_Get_Companies():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    response_data = HR__Companies.Get_Companies_From_Database(data)
    print("**************")
    return response_data

# endregion

# region SALARY CALCULATION
@app.route('/calculate-salaries', methods=['POST'])
@jwt_required()
def Handle_Calculate_Salary():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    #print(data_received)
    response_data = HR_SalaryCalculator.calculate_salaries(data_received)
    return response_data


#Genel bordro
@app.route('/calculate-general-personnel-expenses', methods=['POST'])
@jwt_required()
def Handle_Calculate_General_Personnel_Expenses():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = HR_SalaryCalculator.calculate_general_expenses(data_received)
    return response_data

# endregion

# region TERMINATE EMPLOYEE
@app.route('/calculate-terminated-employee', methods=['POST'])
@jwt_required()
def Handle_Calculate_Terminated_Employee():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = HR_SalaryCalculator.calculate_terminated_employee_payment(data_received)
    return response_data

@app.route('/terminate-employee', methods=['POST'])
@jwt_required()
def Handle_Terminate_Employee():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = HR_EmployeeHandler.Set_Employee_Left(data_received)
    return response_data
# endregion


# region GENERAL HR STATISTICS

@app.route('/get-today-worker-statistics', methods=['POST'])
@jwt_required()
def Handle_Get_Today_Worker_Statistics():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    response_data = HR_EmployeeHandler.Get_Absent_Employees_From_Database_Today(data)
    return response_data

@app.route('/get-this-week-attendance-statistics', methods=['POST'])
@jwt_required()
def Handle_Get_This_Week_Attendance_Statistics():
    pass

@app.route('/get-overall-real-work-hour-statistics', methods=['POST'])
@jwt_required()
def Handle_Get_Overall_Real_Work_Hour_Statistics():
    pass

@app.route('/get-monthly-total-personnel-expenses', methods=['POST'])
@jwt_required()
def Handle_Get_Monthly_Total_Personnel_Expenses():
    pass

@app.route('/get-highest-rating-employee-statistics', methods=['POST'])
@jwt_required()
def Handle_Get_Highest_Rating_Employee_Statistics():
    pass


# endregion


# BELOW THIS PART IS STILL USING LOCALREQUESTS MAIN FILE

# region ADVANCE PAYMENTS

@app.route('/add-advance-payment', methods=['POST'])
@jwt_required()
def Handle_Add_Advance_payment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Add_Advance_Payment(data_received)
    return response_data

@app.route('/get-advance-payments', methods=['POST'])
@jwt_required()
def Handle_Get_Advance_Payments():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Get_Advance_Payments(data_received)
    return response_data

@app.route('/get-advance-payment-specific', methods=['POST'])
@jwt_required()
def Handle_GET_Advance_Payment_Specific():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Get_Specific_Advance_Payment(data_received)
    return response_data

@app.route('/edit-advance-payment', methods=['POST'])
@jwt_required()
def Handle_Edit_Advance_Payment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Edit_Advance_Payment(data_received)
    return response_data

@app.route('/remove-advance-payment', methods=['POST'])
@jwt_required()
def Handle_Remove_Advance_Payment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Remove_Advance_Payment(data_received)
    return response_data

# endregion

# region EXTRA PAYMENTS

@app.route('/add-extra-payment', methods=['POST'])
@jwt_required()
def Handle_Add_Extra_payment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Add_Extra_Payment(data_received)
    return response_data

@app.route('/get-extra-payments', methods=['POST'])
@jwt_required()
def Handle_Get_Extra_Payments():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Get_Extra_Payments(data_received)
    return response_data

@app.route('/get-extra-payment-specific', methods=['POST'])
@jwt_required()
def Handle_GET_Extra_Payment_Specific():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Get_Specific_Extra_Payment(data_received)
    return response_data

@app.route('/edit-extra-payment', methods=['POST'])
@jwt_required()
def Handle_Edit_Extra_Payment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Edit_Extra_Payment(data_received)
    return response_data

@app.route('/remove-extra-payment', methods=['POST'])
@jwt_required()
def Handle_Remove_Extra_Payment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Remove_Extra_Payment(data_received)
    return response_data

# endregion

# region PERMISSIONS - VACATIONS

@app.route('/add-permission', methods=['POST'])
@jwt_required()
def Handle_Add_Permission():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Add_Permission(data_received)
    return response_data

@app.route('/get-permissions', methods=['POST'])
@jwt_required()
def Handle_Get_Permissions():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Get_Permissions(data_received)
    return response_data

@app.route('/get-permission-specific', methods=['POST'])
@jwt_required()
def Handle_GET_Permission_Specific():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Get_Specific_Permission(data_received)
    return response_data

@app.route('/edit-permission', methods=['POST'])
@jwt_required()
def Handle_Edit_Permission():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Edit_Permission(data_received)
    return response_data

@app.route('/remove-permission', methods=['POST'])
@jwt_required()
def Handle_Remove_Permission():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Remove_Permission(data_received)
    return response_data

# endregion

# region SPECIAL HOLIDAYS

@app.route('/add-special-holiday', methods=['POST'])
@jwt_required()
def Handle_Add_Special_Holiday():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    try:
        data = request.json
        data_received = data['data_sent'] #TODO Handle sent data
        response_data = LocalRequests.Add_Special_Holiday(data_received)
        return response_data
    except Exception as error:
        LogError(error)

@app.route('/get-special-holidays', methods=['POST'])
@jwt_required()
def Handle_Get_Special_Holidays():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    response_data = LocalRequests.Get_Special_Holidays()
    print(response_data)
    return response_data

@app.route('/edit-special-holiday', methods=['POST'])
@jwt_required()
def Handle_Edit_Special_Holiday():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Edit_Special_Holiday(data_received)
    return response_data

@app.route('/remove-special-holiday', methods=['POST'])
@jwt_required()
def Handle_Remove_Special_Holiday():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_received = data['data_sent'] #TODO Handle sent data
    response_data = LocalRequests.Remove_Special_Holiday(data_received)
    return response_data


# endregion



# endregion


@app.route('/notifications', methods=['POST'])
@jwt_required()
def NotificationRequest():
    data = request.json

    print(data)

    if data['requestName'] == 'CheckNotifications':
        localResult = LocalRequests.Handle_Notification_Checked(data)
        cloudResult = CloudRequests.Handle_Notification_Checked(data)
    

    return localResult






#CLOUD SYNC
@app.route('/check-changes-1923ccxqw3m', methods=['POST'])
@jwt_required()
def Check_Changes():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    response_data = CloudRequests.Get_Changes_From_Database()
    return response_data



@app.route('/save-changes-1923ccxqw3m', methods=['POST'])
@jwt_required()
def Save_Changes():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_sent = data["data_sent"]

    response_data = CloudRequests.Handle_Save_New_Changes_To_Database(data_sent)
    return response_data


@app.route('/json-to-excel', methods=['POST'])
@jwt_required()
def HandleExcelConversion():
    data = request.json

    data_sent = data["data_sent"]
    main_header = data["header"]

    localResult = Utilities.convert_data_to_XLSX(data_sent, main_header)
    return localResult


if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as error:
        LogError(error)