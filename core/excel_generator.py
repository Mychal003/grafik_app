import io
import calendar
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generuj_plik_excel(wyniki, rok, miesiac):
    if not wyniki:
        return None

    num_days = calendar.monthrange(rok, miesiac)[1]
    
    shift_names = {
        0: "WOLNE", 
        1: "07:00-15:00 (1)", 
        2: "13:00-21:00 (2)", 
        3: "10:00-18:00 (M)",
        -1: "URLOP"
    }

    wb = Workbook()
    ws = wb.active
    
    # Nazwy miesięcy po polsku
    miesiace_pl = ["", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", 
                   "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
    ws.title = f"{miesiace_pl[miesiac]} {rok}"
    
    h_font = Font(bold=True, color="FFFFFF")
    h_fill = PatternFill(start_color="333333", end_color="333333", fill_type="solid")
    urlop_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
    wolne_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    sum_fill_1 = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid") 
    sum_fill_2 = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid") 
    sum_fill_m = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid") 
    
    ramka = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    headers = ["Pracownik"] + [str(d) for d in range(1, num_days + 1)] + [
        "Godziny Zrealizowane", "Godziny Zlecane (Cel)", "Ilość: (1)", "Ilość: (2)", "Ilość: (M)"
    ]
    
    ws.append(headers)
    for cell in ws[1]:
        cell.font = h_font
        cell.fill = h_fill
        cell.alignment = align
        cell.border = ramka

    for emp in wyniki:
        wiersz = [emp["imie"]]
        licznik_1, licznik_2, licznik_m = 0, 0, 0
        
        for d in range(1, num_days + 1):
            kod_zmiany = emp["dni"].get(d, 0)
            wiersz.append(shift_names[kod_zmiany])
            
            if kod_zmiany == 1: licznik_1 += 1
            elif kod_zmiany == 2: licznik_2 += 1
            elif kod_zmiany == 3: licznik_m += 1
            
        wiersz.append(emp["suma_godzin"])
        wiersz.append(emp["etat_docelowy"])
        wiersz.append(licznik_1)
        wiersz.append(licznik_2)
        wiersz.append(licznik_m)
        ws.append(wiersz)

    ostatni_rzad = len(wyniki) + 1
    wiersz_suma_1 = ["Podsumowanie Otwarcie (1)"]
    wiersz_suma_2 = ["Podsumowanie Zamknięcie (2)"]
    wiersz_suma_m = ["Podsumowanie Międzyzmiana (M)"]

    for d in range(1, num_days + 1):
        kolumna = get_column_letter(d + 1)
        wiersz_suma_1.append(f'=COUNTIF({kolumna}2:{kolumna}{ostatni_rzad}, "{shift_names[1]}")')
        wiersz_suma_2.append(f'=COUNTIF({kolumna}2:{kolumna}{ostatni_rzad}, "{shift_names[2]}")')
        wiersz_suma_m.append(f'=COUNTIF({kolumna}2:{kolumna}{ostatni_rzad}, "{shift_names[3]}")')

    for _ in range(5):
        wiersz_suma_1.append("")
        wiersz_suma_2.append("")
        wiersz_suma_m.append("")

    ws.append(wiersz_suma_1)
    ws.append(wiersz_suma_2)
    ws.append(wiersz_suma_m)

    ws.column_dimensions['A'].width = 30
    ws.freeze_panes = "B2"

    for r_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column), start=2):
        for cell in row:
            cell.alignment = align
            cell.border = ramka
            
            if r_idx == 2:
                if 1 < cell.column <= num_days + 1: ws.column_dimensions[get_column_letter(cell.column)].width = 16
                elif cell.column > num_days + 1: ws.column_dimensions[get_column_letter(cell.column)].width = 22
            
            if r_idx <= ostatni_rzad:
                if cell.value == "URLOP": cell.fill = urlop_fill
                elif cell.value == "WOLNE": cell.fill = wolne_fill
                
                # Zaznacz błędy w zgodności godzin
                if cell.column == num_days + 2:
                    cel_godzin = row[num_days + 2].value
                    if cell.value != cel_godzin:
                         cell.font = Font(color="FF0000", bold=True)
                    else:
                         cell.font = Font(color="008000", bold=True)
            else:
                cell.font = Font(bold=True)
                if cell.column == 1:
                    cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
                elif 1 < cell.column <= num_days + 1:
                    if r_idx == ostatni_rzad + 1: cell.fill = sum_fill_1
                    elif r_idx == ostatni_rzad + 2: cell.fill = sum_fill_2
                    elif r_idx == ostatni_rzad + 3: cell.fill = sum_fill_m

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output