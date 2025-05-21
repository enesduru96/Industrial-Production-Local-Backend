from datetime import datetime, timedelta
from hijri_converter import convert
import json, calendar, traceback, os
from libs.Local_Requests import HR_InternalGetters

logs_folder_name = 'flask_logs'
wr_folder = 'warehouse'
material_delivery_folder = 'malzeme_teslim'
hr_folder = 'human_resources'
cloud_folder = 'cloud_server'
main_folder = 'main'

error_folder = 'error'
event_folder = 'event'

desktop_path = os.path.expanduser("~/Desktop")
warehouse_error_path = os.path.join(desktop_path, logs_folder_name, wr_folder, error_folder)
warehouse_event_path = os.path.join(desktop_path, logs_folder_name, wr_folder, event_folder)
malzemeteslim_error_path = os.path.join(desktop_path, logs_folder_name, wr_folder, material_delivery_folder, error_folder)
hr_error_path = os.path.join(desktop_path, logs_folder_name, hr_folder, error_folder)
hr_event_path = os.path.join(desktop_path, logs_folder_name, hr_folder, event_folder)
cloud_error_path = os.path.join(desktop_path, logs_folder_name, cloud_folder, error_folder)
main_error_path = os.path.join(desktop_path, logs_folder_name, main_folder, error_folder)


def log_error_wr(error_string):
    now = datetime.now()
    formatted_time = now.strftime("%d-%m-%Y %H:%M")

    os.makedirs(warehouse_error_path, exist_ok=True)
    today = datetime.today().strftime('%Y-%m-%d')
    log_file_path = os.path.join(warehouse_error_path, f'{today}.json')

    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as f:
            json.dump([], f)

    with open(log_file_path, 'r') as f:
        log_json = json.load(f)

    log_entry = {
        "time": formatted_time,
        "error": str(error_string),
        "traceback": str(traceback.format_exc())
    }
    log_json.append(log_entry)

    with open(log_file_path, 'w') as f:
        json.dump(log_json, f, indent=4)

def log_error_material_delivery(error_string, notes, step):
    now = datetime.now()
    formatted_time = now.strftime("%d-%m-%Y %H:%M")

    os.makedirs(malzemeteslim_error_path, exist_ok=True)
    today = datetime.today().strftime('%Y-%m-%d')
    log_file_path = os.path.join(malzemeteslim_error_path, f'{today}.json')

    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as f:
            json.dump([], f)

    with open(log_file_path, 'r') as f:
        log_json = json.load(f)

    log_entry = {
        "time": formatted_time,
        "error": str(error_string),
        "traceback": str(traceback.format_exc()),
        "notes": notes,
        "step": step
    }
    log_json.append(log_entry)

    with open(log_file_path, 'w') as f:
        json.dump(log_json, f, indent=4)

def log_error_cloud(error_string, notes=None):
    now = datetime.now()
    formatted_time = now.strftime("%d-%m-%Y %H:%M")

    os.makedirs(cloud_error_path, exist_ok=True)
    today = datetime.today().strftime('%Y-%m-%d')
    log_file_path = os.path.join(cloud_error_path, f'{today}.json')

    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as f:
            json.dump([], f)

    with open(log_file_path, 'r') as f:
        log_json = json.load(f)

    log_entry = {
        "time": formatted_time,
        "error": str(error_string),
        "traceback": str(traceback.format_exc()),
        "notes": notes
    }
    log_json.append(log_entry)

    with open(log_file_path, 'w') as f:
        json.dump(log_json, f, indent=4)
    
def log_error_main(error_string):
    now = datetime.now()
    formatted_time = now.strftime("%d-%m-%Y %H:%M")

    os.makedirs(main_error_path, exist_ok=True)
    today = datetime.today().strftime('%Y-%m-%d')
    log_file_path = os.path.join(main_error_path, f'{today}.json')

    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as f:
            json.dump([], f)

    with open(log_file_path, 'r') as f:
        log_json = json.load(f)

    log_entry = {
        "time": formatted_time,
        "error": str(error_string),
        "traceback": str(traceback.format_exc())
    }
    log_json.append(log_entry)

    with open(log_file_path, 'w') as f:
        json.dump(log_json, f, indent=4)


class ScaleMaterialMapper():
    name = "v01"
    count = "v02"
    weight_per_object = "v03"
    total_weight = "v04"
    weighed_date = "v05"


def get_religious_days(year):
    normal_date = convert.Gregorian(year, 1, 1).to_hijri()
    hijri_year = int(str(normal_date).split("-")[0])

    ramazan_date = convert.Hijri(hijri_year, 9, 1).to_gregorian()
    ramazan_bayram_date = convert.Hijri(hijri_year, 10, 1).to_gregorian()
    kurban_date = convert.Hijri(hijri_year, 12, 10, True).to_gregorian()

    ramazan_baslangici = datetime(ramazan_date.year, ramazan_date.month, ramazan_date.day)
    ramazan_bayram_tarihi = datetime(ramazan_bayram_date.year, ramazan_bayram_date.month, ramazan_bayram_date.day)
    kurban_bayram_tarihi = datetime(kurban_date.year, kurban_date.month, kurban_date.day)

    return {
        "ramazan_baslangici" : ramazan_baslangici.strftime('%d-%m-%Y'),
        "ramazan_bayrami" : ramazan_bayram_tarihi.strftime('%d-%m-%Y'),
        "kurban_bayrami" : kurban_bayram_tarihi.strftime('%d-%m-%Y')
    }

def get_all_days_of_month(year, month):
    calendar.setfirstweekday(calendar.MONDAY)
    month_calendar = calendar.monthcalendar(year, month)
    weeks = []
    for week in month_calendar:
        weekdays = {}
        for i, day in enumerate(week):
            if day != 0:
                date_str = f'{day:02d}-{month:02d}-{year}'
                weekdays[date_str] = {
                    "day_name": calendar.day_name[i].lower(),
                    "weekday": i < 5
                }
        if weekdays:
            weeks.append(weekdays)

    return json.dumps(weeks, indent=2, default=str)

def get_weekdays_of_month(year, month):
    calendar.setfirstweekday(calendar.MONDAY)
    month_calendar = calendar.monthcalendar(year, month)
    weeks = []
    for week in month_calendar:
        weekdays = {}
        for i, day in enumerate(week[:5]):
            if day != 0:
                date_str = f'{day:02d}-{month:02d}-{year}'
                weekdays[date_str] = calendar.day_name[i].lower()
        if weekdays:
            weeks.append(weekdays)

    return json.dumps(weeks, indent=2, default=str)

def get_weekend_days_of_month(year, month):
    calendar.setfirstweekday(calendar.MONDAY)
    month_calendar = calendar.monthcalendar(year, month)

    weekend_days = []
    for week in month_calendar:
        for day in week[5:]:
            if day != 0:
                date_str = f'{day:02d}-{month:02d}-{year}'
                weekend_days.append(date_str)

    return json.dumps(weekend_days, indent=2, default=str)

def get_distance_to_end_of_month(date):
    year, month = date.year, date.month
    last_day_of_month = datetime(year, month, 1) + timedelta(days=32)
    last_day_of_month = last_day_of_month.replace(day=1) - timedelta(days=1)
    
    distance = last_day_of_month - date
    
    days = distance.days + 1

    return days

def get_dates_in_week(year, week_number):
    d = datetime.strptime(f'{year}-W{int(week_number )- 1}-1', "%Y-W%W-%w")
    dates = []
    for i in range(5):
        dates.append((d + timedelta(days=i)).strftime("%d-%m-%Y"))
    return dates

def get_week_number(date_str, format_str="%d-%m-%Y"):
    return datetime.strptime(date_str, format_str).isocalendar()[1]



def calculate_day_worked_hours(start_time, end_time, company_entry_hour, company_exit_hour, break_start, break_end, entry_tolerance, exit_tolerance, guy_worked_twice, is_manager:bool = False):
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")

    morning_hours = HR_InternalGetters.Internal_Get_Morning_Workshift_Hours()
    night_hours = HR_InternalGetters.Internal_Get_Night_Workshift_Hours()

    entry_hour = start.hour
    entry_minute = start.minute
    entry_timeobj = entry_hour + entry_minute / 60.0

    morning_hour = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").hour
    morning_minute = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M").minute
    morning_entry = morning_hour + morning_minute / 60.0

    night_hour = datetime.strptime(night_hours["data"][0]["workshift_start"], "%H:%M").hour
    night_minute = datetime.strptime(night_hours["data"][0]["workshift_start"], "%H:%M").minute
    night_entry = night_hour + night_minute / 60.0

    difference_to_morning_entry = abs(round(entry_timeobj - morning_entry, 2))
    difference_to_night_entry = abs(round(entry_timeobj - night_entry, 2))

    if difference_to_morning_entry < difference_to_night_entry:
        company_start = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M")
        company_end = datetime.strptime(morning_hours["data"][0]["workshift_end"], "%H:%M")

        if (start - datetime.combine(start.date(), company_start.time())) <= timedelta(minutes=entry_tolerance):
            start = datetime.combine(start.date(), company_start.time())

        if company_end > end and (datetime.combine(end.date(), company_end.time()) - end) <= timedelta(minutes=exit_tolerance):
            end = datetime.combine(end.date(), company_end.time())


        difference = end - start

        if start.time() <= break_start.time() and end.time() <= break_start.time(): # Morning (no deduction)
            break_time = timedelta(hours=0)
        
        elif start.time() >= break_end.time() and end.time() >= break_end.time(): # Afternoon (no deduction)
            break_time = timedelta(hours=0)
        
        elif start.time() <= break_start.time() and end.time() >= break_end.time(): # Full break
            break_time = break_end - break_start

        else: # Partial break
            break_time = timedelta(hours=break_end.time().hour - max(start.time().hour, break_start.time().hour),
                                minutes=break_end.time().minute - max(start.time().minute, break_start.time().minute))

        if guy_worked_twice:
            pass
        else:
            difference -= break_time

        if is_manager == True:
            if (difference.total_seconds() / 60 / 60) > 0:
                return float((difference.total_seconds() / 60 / 60) + 1)
        return float(difference.total_seconds() / 60 / 60)
    
    else:
        company_start = datetime.strptime(morning_hours["data"][0]["workshift_start"], "%H:%M")
        company_end = datetime.strptime(morning_hours["data"][0]["workshift_end"], "%H:%M")

        time_diff = end - start
        total_minutes = time_diff.seconds // 60
        worked_amount = round(total_minutes / 60, 3)

        if guy_worked_twice:
            pass
        else:
            worked_amount -= 1

        return worked_amount

def calculate_total_work_hours_of_month(workdays, company_entry_hour, company_exit_hour, break_start, break_end):
    total_hours = 0
    for day in workdays:
        start = datetime.strptime(company_entry_hour, "%H:%M")
        end = datetime.strptime(company_exit_hour, "%H:%M")

        difference = end - start
        break_time = break_end - break_start
        difference -= break_time

        total_hours += float(difference.total_seconds() / 60 / 60)
    
    return total_hours

