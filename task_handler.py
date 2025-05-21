import PyPDF2
import os
from datetime import date
import asyncio
from libs.Local_Requests.WR__LazerStockTasks import check_and_insert_stock_drop_logs, get_logged_used_sheets, Update_Stock_Counts

def is_today(date_string):
    day, month, year = map(int, date_string.split('-'))
    today = date.today()
    return date(year, month, day) == today

def extract_pages_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            if len(pdf_reader.pages) == 0:
                return None
            pages = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                pages.append(page_text)
        return pages
    except Exception as error:
        print(error)
        print(file)
        with open("broken_pdfs.txt","a+",encoding="utf-8") as f:
            f.write(f"{file}\n")
        return None
        
def get_folders_from_path(path):
    return [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]

def get_report_files_of_day(path):
    return [os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and file.endswith('.pdf')]

def get_sheet_size(string_parts):
    try:
        for index, part in enumerate(string_parts):
            if part.lower() == "x":
                size_1 = string_parts[index - 1]
                size_2 = string_parts[index + 1]
                return f"{int(float(size_1))}x{int(float(size_2))}"
    except Exception as error:
        print(error)

def get_sheet_main_data_from_file_name(file_name):
    data_parts = file_name.split("-")
    thickness = data_parts[0].replace("mm","MM").replace(",",".")
    material_type = data_parts[1]
    size = data_parts[2]
    instance_number = int(data_parts[3].replace(".pdf",""))
    fason = data_parts[-1].replace(".pdf","")
    is_fason = False
    if fason.lower() == "f":
        is_fason = True

    return thickness, material_type, size, is_fason, instance_number

def scrape_daily_data(file):
    day_data = {"used_sheets" : []}
    pages = extract_pages_from_pdf(file)
    if pages == None:
        return None
    sheet_numbers = []
    for page in pages:
        lines = page.splitlines()
        sheet_data = {}
        for index, line in enumerate(lines):
            if "MaterialName" in line and "Thickness" in line and "SheetSize" in line and "CuttingSize" in line and "NumOfSheet" in line:
                if index + 1 < len(lines):
                    next_line = lines[index + 1]
                    line_parts = next_line.split(" ")
                    sheet_count = int(line_parts[-1])
                    sheet_data["sheet_count"] = sheet_count

            if "PlateNum" in line:
                line = line.replace("ClientName: ", "").strip()
                line = line.replace("PlateNum: ", "").strip()
                if line == "/": continue
                sheet_number = line.split("/")[0].replace("S","")
                sheet_numbers.append(sheet_number)
                sheet_data["number"] = sheet_number
            elif "MaterialName" in line and "SheetSize" in line:
                if index + 1 < len(lines):
                    next_line = lines[index + 1]
                    line_parts = next_line.split(" ")
                    sheet_size = get_sheet_size(line_parts)
                    sheet_data["sheet_size"] = sheet_size
        if not sheet_data == {}:
            day_data["used_sheets"].append(sheet_data)
    return day_data

def string_to_date(date_string):
    day, month, year = map(int, date_string.split('-'))
    return date(year, month, day)
 
async def regular_check_report_files():
    already_logged_items = await get_logged_used_sheets()
    if already_logged_items["status"] == "ok":
        logged_items = [item for item in already_logged_items["data"]]
        already_logged_datestrings = [item["date"] for item in already_logged_items["data"]]
    else:
        already_logged_datestrings = []

    reports_path = "H:\Diğer bilgisayarlar\Dizustu Bilgisayarim\BODOR LAZER\RAPORLAR"
    year_folders = get_folders_from_path(reports_path)
    final_dictionary = {"daily_reports" : []}
    for year in year_folders:
        month_folders = get_folders_from_path(os.path.join(reports_path, year))

        for month in month_folders:
            day_folders = get_folders_from_path(os.path.join(reports_path, year, month))

            for day in day_folders:
                date_string = f"{day}-{month}-{year}"

                daily_data = {}
                report_files_of_day = get_report_files_of_day(os.path.join(reports_path, year, month, day))
                for file in report_files_of_day:
                    daily_data = scrape_daily_data(file)
                    if daily_data == None:
                        continue
                    file_name = os.path.basename(file)
                    thickness, material_type, size, is_fason, instance_number = get_sheet_main_data_from_file_name(file_name)

                    daily_data["date"] = date_string
                    daily_data["thickness"] = thickness
                    daily_data["material_type"] = material_type
                    daily_data["sheet_size"] = size
                    daily_data["is_fason"] = is_fason
                    daily_data["instance_number"] = instance_number
                    daily_data["is_subtracted"] = False

                    final_dictionary["daily_reports"].append(daily_data)


    result = await check_and_insert_stock_drop_logs(final_dictionary)
    print(result)

async def main():
    while True:
        await regular_check_report_files()
        await Update_Stock_Counts()

        print("Interval done, sleeping 300 seconds...")
        await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(main())