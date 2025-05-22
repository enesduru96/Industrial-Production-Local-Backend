import os
import base64
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


# TOP LOGO LEFT
topLeftLogoScaleWidth = 232
topLeftLogoScaleHeight = 88
topLeftPosX = -40
topLeftPosY = 745

# TOP LOGO RIGHT
topRightLogoScaleWidth = 63.2
topRightLogoScaleHeight = 48
topRightPosX = 500
topRightPosY = 765

# HEADER SEPARATOR
headerSeparatorScaleWidth = 600
headerSeparatorScaleHeight = 1.5
headerSeparatorPosX = 10
headerSeparatorPosY = 755

# MAIN LEFT SIDE
earningsPosX = 50
leftDayPosX = 150
leftHourPosX = 195
leftAmountPosX = 240

# MAIN RIGHT SIDE
kesintilerPosX = 310
rightDayPosX = 410
rightHourPosX = 455
rightAmountPosX = 500

# BOTTOM SIDE
totalDayPosX = 40
totalHourPosX = 220
totalEarnPosX = 420
employeeSignaturePosX = 60
employerSignaturePosX = 450

# FIRST MANUAL SEPARATOR
firstSeparatorStartX = 50
firstSeparatorStartY = 735
firstSeparatorTargetX = 570
firstSeparatorTargetY = 735

# SECOND MANUAL SEPARATOR
secondSeparatorStartX = 50
secondSeparatorStartY = 688
secondSeparatorTargetX = 570
secondSeparatorTargetY = 688

# MAIN MID SEPARATOR
midSeparatorStartY = 675
midSeparatorTargetY = 500

# BOTTOM MANUAL SEPARATOR
bottomSeparatorStartX = 50
bottomSeparatorStartY = 480
bottomSeparatorTargetX = 580
bottomSeparatorTargetY = 480

# DEBUG
showCoordinates = True
def add_header(cb:canvas):
    try:
        cb.saveState()

        image_url_top_right = os.path.join('PrinterPictures', 'top-right-logo.png')
        img_top_right = ImageReader(image_url_top_right)
        cb.drawImage(image=img_top_right, x=topRightPosX, y=topRightPosY, width=topRightLogoScaleWidth, height=topRightLogoScaleHeight, mask='auto', preserveAspectRatio=True)

        image_header_separator = os.path.join('PrinterPictures', 'header-separator.png')
        img_header_separator = ImageReader(image_header_separator)
        cb.drawImage(image=img_header_separator, x=headerSeparatorPosX, y=headerSeparatorPosY, width=headerSeparatorScaleWidth, height=headerSeparatorScaleHeight, mask='auto', preserveAspectRatio=True)
        cb.restoreState()

    except Exception as error:
        print(error)

def format_float(float):
    rounded_total = round(float, 2)
    total_string = str(rounded_total)
    parts = total_string.split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else ''
    formatted_integer_part = '{:,}'.format(int(integer_part)).replace(',', ' ')
    formatted_decimal_part = decimal_part.replace('.', ',')
    formatted_total = formatted_integer_part + ',' + formatted_decimal_part
    return formatted_total

def Print_General_Personnel_Expenses(salary_data, year, month_name):
    data = []

    total_normal_work_rate = 0.00
    total_weekday_off_rate = 0.00
    total_extra_work_rate = 0.00
    total_advance_rate = 0.00
    total_absence_rate = 0.00
    total_to_be_paid_to_personnel = 0.00
    total_salaries_amount = 0.00
    total_including_advances = 0.00

    sorted_salary_data = sorted(salary_data["result_list"], key=lambda x: x["employee_company"])


    administrative_staff_list = []
    worker_staff_list = []

    final_liste = []
    for item in sorted_salary_data:
        is_administrative = False
        #print(item)
        sicilNo = item["employee_register_number"]
        name = item["employee_name"]
        surname = item["employee_surname"]
        salary = item["base_salary"]

        company = item["employee_company"]

        total_salaries_amount += salary

        normal_work_rate = item["weekday_normal_work_earned_salary"]
        total_normal_work_rate += normal_work_rate

        weekend_holiday = item["weekend_base_earned_salary"]
        total_weekday_off_rate += weekend_holiday

        extra_work_hours = item["total_ek_mesai_hours"]
        extra_work_rate = item["total_ek_mesai_earned_salary"]
        total_extra_work_rate += extra_work_rate

        advance = item["avans_kesintisi_value"]
        total_advance_rate += advance

        department = item["employee_department"]
        if department == "İDARİppppp":
            net_earned = salary
            net_earned -= advance
        else:
            net_earned = item["total_final_earned"]
        

        absence = item["total_absent_lost_price"]
        if department == "İDARİppppp":
            total_absence_rate += 0
            final_absence = 0
        else:
            total_absence_rate += absence
            final_absence = absence



        if department == "İDARİ":
            is_administrative = True
        else:
            is_administrative = False

        
        total_to_be_paid_to_personnel += net_earned

        if len(name) >= 12:
            name_text = f"{name[0:12].strip()}..."
        else:
            name_text = name
        
        if len(surname) >= 12:
            surname_text = f"{surname[0:12].strip()}..."
        else:
            surname_text = surname

        if is_administrative == True:
            administrative_staff_list.append([name_text, surname_text, f"{company[0:5]}...", format_float(float(salary)), format_float(float(normal_work_rate)), format_float(float(weekend_holiday)), format_float(float(extra_work_hours)), format_float(float(extra_work_rate)), format_float(float(advance)), format_float(float(final_absence)), format_float(float(net_earned)), ""])

        else:
            worker_staff_list.append([name_text, surname_text, f"{company[0:5]}...", format_float(float(salary)), format_float(float(normal_work_rate)), format_float(float(weekend_holiday)), format_float(float(extra_work_hours)), format_float(float(extra_work_rate)), format_float(float(advance)), format_float(float(final_absence)), format_float(float(net_earned)), ""])


    total_including_advances = total_to_be_paid_to_personnel + total_advance_rate

    total_normal_work_rate = format_float(total_normal_work_rate)
    total_weekday_off_rate = format_float(total_weekday_off_rate)
    total_extra_work_rate = format_float(total_extra_work_rate)
    total_advance_rate = format_float(total_advance_rate)
    total_absence_rate = format_float(total_absence_rate)
    total_to_be_paid_to_personnel = format_float(total_to_be_paid_to_personnel)
    total_salaries_amount = format_float(total_salaries_amount)
    total_including_advances = format_float(total_including_advances)


    administrative_staff_list = sorted(administrative_staff_list, key=lambda x: x[2])
    worker_staff_list = sorted(worker_staff_list, key=lambda x: x[2])

    for item in administrative_staff_list:
        data.append(item)
    for item in worker_staff_list:
        data.append(item)

    data.insert(0, ["Adı", "Soyadı", "Şirketi", "Maaşı", "NÇS", "HT", "FMS", "FMÜ", "Avans", "Dev", "Net", "İmza"])

    pdfmetrics.registerFont(TTFont('Regular', 'c:\\windows\\fonts\\calibri.ttf'))
    pdfmetrics.registerFont(TTFont('Bold', 'c:\\windows\\fonts\\calibrib.ttf'))
    pdf_path = os.path.join("PrinterTemp", "tempgeneralpersonnelexpenses.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    elements = []
    c.setAuthor('3M')
    c.setCreator('Test Creator')
    c.setKeywords('Test Keyword')
    c.setSubject('Test Subject')
    c.setTitle('Test Title')
    add_header(c)


    margin = 731
    page_width = c._pagesize[0]
    middle = page_width / 2

    today = datetime.today()
    today_string = today.strftime("%d.%m.%Y")

    c.setFont("Bold", 16)
    c.drawCentredString(middle, margin, f"{month_name} {year} GENEL ÜCRET BORDROSU")

    c.setFont("Bold", 8)
    c.drawCentredString(middle + 200, margin, f"Rapor Tarihi: {today_string}")


    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"), # Align Names
        ("ALIGN", (0, 1), (0, -1), "LEFT"), # Align Names
        ("FONTSIZE", (1, 1), (1, -1), 5), # Fontsize for Names
        ("FONTNAME", (0, 0), (-1, 0), "Bold"),  # Use the 'Bold' font for the table header
        ("FONTNAME", (0, 1), (-1, -1), "Regular"),  # Use the 'Regular' font for the table content
        ("FONTSIZE", (0, 0), (-1, 0), 12),  # Font size for table headers
        ("FONTSIZE", (0, 1), (-1, -1), 9),  # Font size for table content
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ])


    num_rows = len(data)
    rows_per_page = 25
    for start in range(0, num_rows, rows_per_page):
        end = start + rows_per_page
        table_data = data[start:end]
        if end > 25:
            c.showPage()
            table_data.insert(0, ["Adı", "Soyadı", "Şirketi", "Maaşı", "NÇS", "HT", "FMS", "FMÜ", "Avans", "Dev", "Net", "İmza"])
            add_header(c)


        table1 = Table(table_data, style=style, repeatRows=1, vAlign="TOP")
        table1.hAlign = 'LEFT'
        table1.spaceBefore = 10
        w, h = table1.wrapOn(c, 0, 0)

        if end <= 25:
            table1.drawOn(c, 20, margin - h - 20)
        else:
            table1.drawOn(c, 20, margin - h)
        

    # BOTTOM TOTAL PART
    if c._pageNumber == 1:
        final_margin = margin - h - 30
    else:
        final_margin = margin - h - 5

    final_margin -= 15

    c.setFont("Bold", 10)
    c.drawString(60, final_margin, "TOP. N.Ç. ÜCRETİ")
    c.setFont("Regular", 10)

    width = c.stringWidth(f"{total_normal_work_rate}", "Regular", 10)
    c.drawString(200 - width, final_margin, f"{total_normal_work_rate} TRY")

    c.setFont("Bold", 10)
    c.drawString(60, final_margin - 15, "TOP. H.T. ÜCRETİ")
    c.setFont("Regular", 10)

    width = c.stringWidth(f"{total_weekday_off_rate}", "Regular", 10)
    c.drawString(200 - width, final_margin - 15, f"{total_weekday_off_rate} TRY")

    c.setFont("Bold", 10)
    c.drawString(60, final_margin - 30, "TOP. FAZLA MESAİ")
    c.setFont("Regular", 10)

    width = c.stringWidth(f"{total_extra_work_rate}", "Regular", 10)
    c.drawString(200 - width, final_margin - 30, f"{total_extra_work_rate} TRY")



    c.setFont("Bold", 10)
    c.drawString(330, final_margin, "total AVANS")
    c.setFont("Regular", 10)

    width = c.stringWidth(f"{total_advance_rate}", "Regular", 10)
    c.drawString(480 - width, final_margin, f"{total_advance_rate} TRY")

    c.setFont("Bold", 10)
    c.drawString(330, final_margin - 15, "TOP. DEVAMSIZ ÜCR.")
    c.setFont("Regular", 10)

    width = c.stringWidth(f"{total_absence_rate}", "Regular", 10)
    c.drawString(480 - width, final_margin - 15, f"{total_absence_rate} TRY")

    c.setFont("Bold", 10)
    c.drawString(60, final_margin - 65, "total Taban Çalışan Maaşı:")
    c.setFont("Regular", 10)
    width = c.stringWidth(f"{total_salaries_amount} TRY.", "Regular", 10)
    c.drawString(60, final_margin - 85, f"{total_salaries_amount} TRY.")

    c.setFont("Bold", 10)
    c.drawString(230, final_margin - 65, "Avanslar Dahil total Gider:")
    c.setFont("Regular", 10)
    width = c.stringWidth(f"{total_including_advances} TRY.", "Regular", 10)
    c.drawString(230, final_margin - 85, f"{total_including_advances} TRY.")

    c.setFont("Bold", 10)
    c.drawString(390, final_margin - 65, "Personele Ödenecek Ücret (Kalan):")
    c.setFont("Regular", 10)
    width = c.stringWidth(f"{total_to_be_paid_to_personnel} TRY.", "Regular", 10)
    c.drawString(390, final_margin - 85, f"{total_to_be_paid_to_personnel} TRY.")
    
    c.save()
    file = open(pdf_path, "rb")
    pdf_bytes = file.read()
    file.close()
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    return {"status": "ok", "pdf": encoded_pdf}



def Print_Terminated_Employee_Signed(debt_info):
    pdfmetrics.registerFont(TTFont('Regular', 'c:\\windows\\fonts\\calibri.ttf'))
    pdfmetrics.registerFont(TTFont('Bold', 'c:\\windows\\fonts\\calibrib.ttf'))
    pdf_path = os.path.join("PrinterTemp", "temptermination.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setAuthor('3M')
    c.setCreator('Test Creator')
    c.setKeywords('Test Keyword')
    c.setSubject('Test Subject')
    c.setTitle('Test Title')
    add_header(c)


    margin = 721
    page_width = c._pagesize[0]
    middle = page_width / 2

    today = datetime.today()
    today_string = today.strftime("%d.%m.%Y")

    c.setFont("Bold", 18)
    c.drawCentredString(middle, margin, "PERSONEL ÇIKIŞ ÖDEME BİLGİSİ")

    margin -= 28
    c.setFont("Bold", 10)
    c.drawString(450, margin, "Rapor Tarihi:")
    c.setFont("Regular", 10)
    c.drawString(510, margin, today_string)


    c.setLineWidth(1)
    c.line(50, 685, 570, 685)


    top_margin_header_text = 670

    c.setFont("Bold", 12)
    c.drawString(60, top_margin_header_text, "Adı:")
    c.setFont("Regular", 12)
    employee_name = debt_info["employee_name"]
    c.drawString(130, top_margin_header_text, employee_name)


    c.setFont("Bold", 12)
    c.drawString(220, top_margin_header_text, "Departman:")
    c.setFont("Regular", 12)
    department = debt_info["employee_department"]
    c.drawString(310, top_margin_header_text, department)


    c.setFont("Bold", 12)
    c.drawString(410, top_margin_header_text, "Net Maaş:")
    c.setFont("Regular", 12)
    salary = debt_info["base_salary"]
    c.drawString(480, top_margin_header_text, f"{salary} TRY")

    top_margin_header_text -= 20

    c.setFont("Bold", 12)
    c.drawString(60, top_margin_header_text, "Soyadı:")
    c.setFont("Regular", 12)
    employee_surname = debt_info["employee_surname"]
    c.drawString(130, top_margin_header_text, employee_surname)

    c.setFont("Bold", 12)
    c.drawString(220, top_margin_header_text, "Görevi:")
    c.setFont("Regular", 12)
    gorevi = debt_info["employee_profession"]
    c.drawString(310, top_margin_header_text, gorevi)

    c.setFont("Bold", 12)
    c.drawString(410, top_margin_header_text, "Hourly Rate:")
    c.setFont("Regular", 12)
    saatlik_ucreti = str(debt_info["salary_hourly"])
    c.drawString(480, top_margin_header_text, saatlik_ucreti)

    c.setLineWidth(1)
    c.line(50, 638, 570, 638)


    # region ADDING MAIN LEFT SIDE

    top_margin_header_text -= 50

    c.setFont("Bold", 13)
    c.drawString(earningsPosX, top_margin_header_text, "KAZANÇLAR")
    c.setFont("Bold", 11)
    c.drawString(earningsPosX, top_margin_header_text - 25, "Normal Çalışma")
    c.drawString(earningsPosX, top_margin_header_text - 50, "Hafta Tatili")
    c.drawString(earningsPosX, top_margin_header_text - 75, "Ücretli İzin")
    c.drawString(earningsPosX, top_margin_header_text - 100, "Ekstra Kazanç")
    c.drawString(earningsPosX, top_margin_header_text - 125, "Fazla Mesai")

    c.setFont("Bold", 13)
    c.drawString(leftDayPosX, top_margin_header_text, "Gün")

    c.setFont("Regular", 10)
    c.drawString(leftDayPosX, top_margin_header_text - 25, f"{debt_info['weekday_normal_work_days_value']}")
    c.drawString(leftDayPosX, top_margin_header_text - 50, f"{debt_info['weekend_base_days_value']}")
    c.drawString(leftDayPosX, top_margin_header_text - 75, f"{debt_info['ucretli_izin_days_value']}")
    c.drawString(leftDayPosX, top_margin_header_text - 100, f"{debt_info['ek_kazanc_value']}")
    c.drawString(leftDayPosX, top_margin_header_text - 125, f"{debt_info['total_ek_mesai_days_value']}")



    c.setFont("Bold", 13)
    c.drawString(leftHourPosX, top_margin_header_text, "Hour")

    c.setFont("Regular", 10)
    c.drawString(leftHourPosX, top_margin_header_text - 25, f"{debt_info['weekday_normal_work_hours']}")
    c.drawString(leftHourPosX, top_margin_header_text - 50, f"{debt_info['weekend_base_hours']}")
    c.drawString(leftHourPosX, top_margin_header_text - 75, f"{debt_info['ucretli_izin_hours']}")
    c.drawString(leftHourPosX, top_margin_header_text - 100, "-")
    c.drawString(leftHourPosX, top_margin_header_text - 125, f"{debt_info['total_ek_mesai_hours']}")



    c.setFont("Bold", 13)
    c.drawString(leftAmountPosX, top_margin_header_text, "Tutarlar")

    c.setFont("Regular", 10)
    c.drawString(leftAmountPosX, top_margin_header_text - 25, f"{debt_info['weekday_normal_work_earned_salary']} TRY")
    c.drawString(leftAmountPosX, top_margin_header_text - 50, f"{debt_info['weekend_base_earned_salary']} TRY")
    c.drawString(leftAmountPosX, top_margin_header_text - 75, f"{debt_info['ucretli_izin_earned_salary']} TRY")
    c.drawString(leftAmountPosX, top_margin_header_text - 100, f"{debt_info['ek_kazanc_value']} TRY")
    c.drawString(leftAmountPosX, top_margin_header_text - 125, f"{debt_info['total_ek_mesai_earned_salary']} TRY")
    
    # endregion


    # region MID SEPARATOR
    c.setLineWidth(1)
    c.line(middle, 625, middle, 450)

    # endregion

    # region ADDING MAIN RIGHT SIDE

    c.setFont("Bold", 13)
    c.drawString(kesintilerPosX, top_margin_header_text, "KESİNTİLER")
    c.setFont("Bold", 11)
    c.drawString(kesintilerPosX, top_margin_header_text - 25, "Devamsızlık")
    c.drawString(kesintilerPosX, top_margin_header_text - 50, "Ücretsiz İzin")
    c.drawString(kesintilerPosX, top_margin_header_text - 75, "Avans Kesintisi")
    c.drawString(kesintilerPosX, top_margin_header_text - 100, "Ek Kesinti")

    c.setFont("Bold", 13)
    c.drawString(rightDayPosX, top_margin_header_text, "Gün")

    c.setFont("Regular", 10)
    c.drawString(rightDayPosX, top_margin_header_text - 25, f"{debt_info['total_absent_days_value']}")
    c.drawString(rightDayPosX, top_margin_header_text - 50, f"{debt_info['ucretsiz_izin_days']}")
    c.drawString(rightDayPosX, top_margin_header_text - 75, "-")
    c.drawString(rightDayPosX, top_margin_header_text - 100, "-")


    c.setFont("Bold", 13)
    c.drawString(rightHourPosX, top_margin_header_text, "Hour")

    c.setFont("Regular", 10)
    c.drawString(rightHourPosX, top_margin_header_text - 25, f"{debt_info['total_absent_hours']}")
    c.drawString(rightHourPosX, top_margin_header_text - 50, f"{debt_info['ucretsiz_izin_hours']}")
    c.drawString(rightHourPosX, top_margin_header_text - 75, "-")
    c.drawString(rightHourPosX, top_margin_header_text - 100, "-")



    c.setFont("Bold", 13)
    c.drawString(rightAmountPosX, top_margin_header_text, "Tutarlar")

    c.setFont("Regular", 10)
    c.drawString(rightAmountPosX, top_margin_header_text - 25, f"{debt_info['total_absent_lost_price']} TRY")
    c.drawString(rightAmountPosX, top_margin_header_text - 50, f"{debt_info['ucretsiz_izin_price']} TRY")
    c.drawString(rightAmountPosX, top_margin_header_text - 75, f"{debt_info['avans_kesintisi_value']} TRY")
    c.drawString(rightAmountPosX, top_margin_header_text - 100, f"{debt_info['ek_kesinti_value']} TRY")

    # endregion

    # region BOTTOM SEPARATOR
    c.setLineWidth(1)
    c.line(50, 420, 570, 420)
    # endregion

    # region ADDING MAIN BOTTOM SIDE
    top_margin_header_text -= 170

    c.setFont("Bold", 12)
    c.drawString(totalDayPosX, top_margin_header_text, "total GÜN")
    c.setFont("Regular", 11)
    c.drawString(totalDayPosX + 100, top_margin_header_text, f"{debt_info['total_worked_day_value']}")

    c.setFont("Bold", 12)
    c.drawString(totalHourPosX, top_margin_header_text, "total SAAT")
    c.setFont("Regular", 11)
    c.drawString(totalHourPosX + 100, top_margin_header_text, f"{debt_info['total_worked_hours']}")

    c.setFont("Bold", 12)
    c.drawString(totalEarnPosX, top_margin_header_text, "total HAKEDİŞ")
    c.setFont("Regular", 11)
    c.drawString(totalEarnPosX + 100, top_margin_header_text, f"{debt_info['total_final_earned']}")
    # endregion


    # region ADDING SIGNATURES
    top_margin_header_text -= 50
    c.setFont("Bold", 11)
    c.drawString(employeeSignaturePosX, top_margin_header_text, "Çalışan İmza")
    c.drawString(employerSignaturePosX, top_margin_header_text, "İşveren İmza")




    # endregion


    c.showPage()
    c.save()
    file = open(pdf_path, "rb")
    pdf_bytes = file.read()
    file.close()
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    return {"status": "ok", "pdf": encoded_pdf}




def print_material_delivery_report(malzemeler, teslim_alan):
    data = []
    malzeme_listesi = []

    final_liste = []
    for item in malzemeler:
        material_id = item["id"]
        material_name = item["adi"]
        delivered_amount = float(item["miktar"])
        delivery_text = ""
        if delivered_amount.is_integer():
            delivery_text = f"{int(delivered_amount)}"
        else:
            delivery_text = f"{delivered_amount:.2f}"

        malzeme_listesi.append([material_id, material_name, delivery_text, "                                              "])


    for item in malzeme_listesi:
        data.append(item)
    data.sort(key=lambda x: float(x[2]), reverse=True)
    data.insert(0, ["Malzeme ID", "Malzeme Adı", "Verilen Miktar", "Notlar"])

    pdfmetrics.registerFont(TTFont('Regular', 'c:\\windows\\fonts\\calibri.ttf'))
    pdfmetrics.registerFont(TTFont('Bold', 'c:\\windows\\fonts\\calibrib.ttf'))
    pdf_path = os.path.join("PrinterTemp", "tempmalzemeteslim.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    elements = []
    c.setAuthor('3M')
    c.setCreator('Depo Yazılım')
    c.setKeywords('Depo Malzeme Teslim')
    c.setSubject('Malzeme Teslim')
    c.setTitle('Depo Malzeme Teslim Raporu')
    add_header(c)


    margin = 731
    page_width = c._pagesize[0]
    middle = page_width / 2

    # Set font sizes
    today = datetime.today()
    today_string = today.strftime("%d.%m.%Y")

    c.setFont("Bold", 16)
    c.drawCentredString(middle, margin, f"Depo Malzeme Teslim Raporu")

    c.setFont("Bold", 8)
    c.drawCentredString(middle + 200, margin, f"Rapor Tarihi: {today_string}")


    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (1, 1), (1, -1), 11), # Fontsize for Names
        ("FONTNAME", (0, 0), (-1, 0), "Bold"),  # Use the 'Bold' font for the table header
        ("FONTNAME", (0, 1), (-1, -1), "Regular"),  # Use the 'Regular' font for the table content
        ("FONTSIZE", (0, 0), (-1, 0), 12),  # Font size for table headers
        ("FONTSIZE", (0, 1), (-1, -1), 11),  # Font size for table content
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),  # BottomPadding for table content
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ])


    num_rows = len(data)
    rows_per_page = 25
    for start in range(0, num_rows, rows_per_page):
        end = start + rows_per_page
        table_data = data[start:end]
        if end > 25:
            c.showPage()
            table_data.insert(0, ["Malzeme ID", "Malzeme Adı", "Verilen Miktar", "Notlar"])
            add_header(c)


        table1 = Table(table_data, style=style, repeatRows=1, vAlign="TOP")
        table1.hAlign = 'LEFT'
        table1.spaceBefore = 10
        w, h = table1.wrapOn(c, 0, 0)

        if end <= 25:
            table1.drawOn(c, 100, margin - h - 20)
        else:
            table1.drawOn(c, 100, margin - h)
        


    # BOTTOM TOTAL PART
    if c._pageNumber == 1:
        final_margin = margin - h - 30
    else:
        final_margin = margin - h - 5


    final_margin -= 60

    c.setFont("Bold", 12)
    teslim_alan_yazisi = "Teslim Alan: "
    teslim_alan_yazisi_genislik = c.stringWidth(teslim_alan_yazisi, "Regular", 12)
    c.drawString(100, final_margin, teslim_alan_yazisi)
    c.setFont("Regular", 12)

    width = c.stringWidth(f"{teslim_alan}", "Regular", 12)
    c.drawString(120 + teslim_alan_yazisi_genislik, final_margin, f"{teslim_alan}")


    final_margin -= 15
    c.setFont("Bold", 12)
    c.drawString(100, final_margin, "İmza: ")
    
    c.save()
    file = open(pdf_path, "rb")
    pdf_bytes = file.read()
    file.close()
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    return {"status": "ok", "pdf_bytes": encoded_pdf}



def is_day_weekend(tarih_str):
    tarih = datetime.strptime(tarih_str, '%d-%m-%Y')
    hafta_gunu = tarih.weekday()
    return hafta_gunu >= 5
def get_month_name(sayi):
    aylar = {
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
    return aylar.get(sayi, "Geçersiz ay numarası")

def convert_to_hours_minutes(decimal_time):
    hours = int(decimal_time)
    minutes = int((decimal_time - hours) * 60)
    return f"{hours} saat {minutes} dakika"

def Print_Attendance(employees_data, year, month):
    month_name = get_month_name(int(month))

    pdfmetrics.registerFont(TTFont('Regular', 'c:\\windows\\fonts\\calibri.ttf'))
    pdfmetrics.registerFont(TTFont('Bold', 'c:\\windows\\fonts\\calibrib.ttf'))
    pdf_path = os.path.join("PrinterTemp", "temppuantaj.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setAuthor('3M')
    c.setCreator('3M Grup')
    c.setKeywords('Puantaj')
    c.setSubject('Puantaj')
    c.setTitle('Çalışan Puantaj Bilgileri')

    style_weekend = TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.lightgreen),
    ])
    style_absent = TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.red),
    ])

    final_liste = []
    for employee in employees_data:
        if employee == employees_data[0]:
            pass
        else:
            c.showPage()

        employee_table = []
        sicilNo = employee["register_number"]
        name = employee["name"]
        surname = employee["surname"]
        entry_exit_info = employee["salary_details"]
        company = employee["company"]

        total_extra_work_hours = employee["total_ek_mesai_hours"]
        total_absent_hours = employee["total_absent_hours"]

        for day in entry_exit_info:
            if is_day_weekend(day["date"]):
                day["is_weekend"] = True
            
            if day["start"] == None and day["end"] == None:
                day["not_worked"] = True
                day_entry_text = "-"
                day_exit_text = "-"
                total_worked_text = "-"
            else:
                day["not_worked"] = False
                day_entry_text = day["start"]
                day_exit_text = day["end"]
                total_worked_text = convert_to_hours_minutes(float(day["total_worked"]))

            day_date = day["date"].replace("-","/")
            employee_table.append([day_date, day_entry_text, day_exit_text, total_worked_text])
        
        # Stil ayarlamaları
        style_list = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 1), (1, -1), "CENTER"),  # Align Names
            ("ALIGN", (0, 1), (0, -1), "CENTER"),  # Align Names
            ("FONTSIZE", (1, 1), (1, -1), 12),  # Fontsize for Names
            ("FONTNAME", (0, 0), (-1, 0), "Bold"),  # Use the 'Bold' font for the table header
            ("FONTNAME", (0, 1), (-1, -1), "Regular"),  # Use the 'Regular' font for the table content
            ("FONTSIZE", (0, 0), (-1, 0), 14),  # Font size for table headers
            ("FONTSIZE", (0, 1), (-1, -1), 12),  # Font size for table content
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]


        margin = 731
        page_width = c._pagesize[0]
        middle = page_width / 2

        # Set font sizes
        today = datetime.today()
        today_string = today.strftime("%d/%m/%Y")

        c.setFont("Bold", 16)
        c.drawCentredString(middle, margin, f"{month_name} {year} PUANTAJ TABLOSU")
        c.setFont("Bold", 10)
        c.drawCentredString(middle + 200, margin, f"Rapor Tarihi: {today_string}")


        margin -= 40

        c.setFont("Bold", 12)
        c.drawString(120, margin, f"ADI: ")

        c.setFont("Regular", 12)
        c.drawString(170, margin , f"{name}")

        c.setFont("Bold", 12)
        c.drawString(120, margin - 15, f"SOYADI: ")

        c.setFont("Regular", 12)
        c.drawString(170, margin - 15, f"{surname}")


        c.drawString(120, 60, f"total Absent Hours: {convert_to_hours_minutes(float(total_absent_hours))}")
        c.drawString(120, 45, f"total Extra Work Hours: {convert_to_hours_minutes(float(total_extra_work_hours))}")

        num_rows = len(employee_table)
        start = 0
        while start < num_rows:
            end = min(start + (num_rows - start), num_rows)

            table_data = employee_table[start:end]
            if end > 25:
                table_data.insert(0, ["Date", "Giriş Saati", "Entry Hour", "Total Worked Hours"])


                for i, row in enumerate(table_data):
                    if i == 0:
                        continue  # Skip the header row

                    day_date = row[0]
                    day_is_weekend = is_day_weekend(day_date.replace("/","-"))
                    day_not_worked = row[3] == "-"

                    if (day_is_weekend or day_date == "01/01/2024"):
                        background_color = colors.lightgreen
                    
                    elif (day_not_worked and day_date != "01/01/2024"):
                        background_color = colors.red

                    else:
                        background_color = colors.white


                    style_list.append(('BACKGROUND', (0, i), (-1, i), background_color))
                
                style = TableStyle(style_list)



            table1 = Table(table_data, style=style, repeatRows=1, vAlign="TOP")
            table1.hAlign = 'CENTER'
            table1.spaceBefore = 10
            w, h = table1.wrapOn(c, 0, 0)

            table1.drawOn(c, 120, 80)

            start = end

    c.save()
    file = open(pdf_path, "rb")
    pdf_bytes = file.read()
    file.close()
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    return {"status": "ok", "pdf": encoded_pdf}