import io
import calendar
import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def generuj_plik_excel(wyniki, rok, miesiac, obiekt="", wersja=1, wydrukowal=""):
    if not wyniki:
        return None

    num_days = calendar.monthrange(rok, miesiac)[1]

    # Kod zmiany -> (linia1, linia2) do wyświetlenia w komórce (jak w PDF: godzina/godzina)
    shift_display = {
        0: ("WOLNE", ""),
        1: ("07:00", "15:00"),
        2: ("13:00", "21:00"),
        3: ("10:00", "18:00"),
        -1: ("URLOP", ""),
    }
    # Do liczenia / filtrowania (bez zmian względem oryginału)
    shift_names = {
        0: "WOLNE",
        1: "07:00-15:00 (1)",
        2: "13:00-21:00 (2)",
        3: "10:00-18:00 (M)",
        -1: "URLOP",
    }

    dni_tygodnia_pl = ["Pn", "Wt", "Śr", "Cz", "Pt", "Sb", "Nd"]  # calendar.weekday: 0=Pn ... 6=Nd
    miesiace_pl = ["", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
                   "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]

    wb = Workbook()
    ws = wb.active
    ws.title = f"{miesiace_pl[miesiac]} {rok}"

    # ---------- style ----------
    thin = Side(style='thin', color="000000")
    ramka = Border(left=thin, right=thin, top=thin, bottom=thin)
    align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center")

    tytul_font = Font(bold=True, size=14)
    podtytul_font = Font(size=10)
    h_font = Font(bold=True, color="000000")
    h_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")   # jasny nagłówek jak w PDF
    sob_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")  # sobota - szary
    nd_fill = PatternFill(start_color="F4B6C2", end_color="F4B6C2", fill_type="solid")   # niedziela/święto - różowy/czerwony
    urlop_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
    wolne_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    sum_fill_1 = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    sum_fill_2 = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
    sum_fill_m = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    legenda_naglowek_fill = PatternFill(start_color="BFBFBF", end_color="BFBFBF", fill_type="solid")

    total_cols = 1 + num_days + 5  # pracownik + dni + 4 kolumny sumaryczne + zapas
    last_col_letter = get_column_letter(total_cols)

    # ---------- nagłówek dokumentu (jak w PDF: Grafik / Obiekt / Wersja) ----------
    ws.merge_cells(f"A1:{last_col_letter}1")
    ws["A1"] = f"Grafik planowany za okres: {miesiac} / {rok}"
    ws["A1"].font = tytul_font
    ws["A1"].alignment = align_left

    ws.merge_cells(f"A2:{last_col_letter}2")
    ws["A2"] = f"Obiekt: {obiekt}" if obiekt else ""
    ws["A2"].font = podtytul_font
    ws["A2"].alignment = align_left

    ws.merge_cells(f"A3:{last_col_letter}3")
    ws["A3"] = f"Wersja: {wersja}"
    ws["A3"].font = podtytul_font
    ws["A3"].alignment = align_left

    ws.append([])  # wiersz 4 - odstęp

    # ---------- dwuwierszowy nagłówek tabeli (wiersz 5: numer dnia, wiersz 6: dzień tygodnia) ----------
    header_row_1 = 5
    header_row_2 = 6

    ws.cell(row=header_row_1, column=1, value="Pracownik")
    ws.merge_cells(start_row=header_row_1, start_column=1, end_row=header_row_2, end_column=1)

    weekday_of_day = {}  # d -> 0..6 (Pn..Nd)
    for d in range(1, num_days + 1):
        col = d + 1
        wd = calendar.weekday(rok, miesiac, d)  # 0=Pn ... 6=Nd
        weekday_of_day[d] = wd

        c1 = ws.cell(row=header_row_1, column=col, value=d)
        c2 = ws.cell(row=header_row_2, column=col, value=dni_tygodnia_pl[wd])

        for c in (c1, c2):
            c.font = h_font
            c.alignment = align
            c.border = ramka
            if wd == 5:      # sobota
                c.fill = sob_fill
            elif wd == 6:    # niedziela
                c.fill = nd_fill
            else:
                c.fill = h_fill

    # kolumny podsumowania - też w dwuwierszowym nagłówku (scalone pionowo)
    summary_headers = ["Godziny\nZrealizowane", "Godziny\nZlecane (Cel)", "Ilość: (1)", "Ilość: (2)", "Ilość: (M)"]
    start_summary_col = num_days + 2
    for i, txt in enumerate(summary_headers):
        col = start_summary_col + i
        ws.merge_cells(start_row=header_row_1, start_column=col, end_row=header_row_2, end_column=col)
        cell = ws.cell(row=header_row_1, column=col, value=txt)
        cell.font = h_font
        cell.fill = h_fill
        cell.alignment = align
        cell.border = ramka
        # obramowanie dolnej scalonej komórki też
        ws.cell(row=header_row_2, column=col).border = ramka

    for c in ws[header_row_1] + ws[header_row_2]:
        if c.border is None or c.border.left is None:
            c.border = ramka

    # ---------- wiersze pracowników ----------
    first_data_row = header_row_2 + 1
    for r_offset, emp in enumerate(wyniki):
        r = first_data_row + r_offset
        licznik_1, licznik_2, licznik_m = 0, 0, 0

        name_cell = ws.cell(row=r, column=1, value=emp["imie"])
        name_cell.font = Font(bold=True)
        name_cell.alignment = align_left
        name_cell.border = ramka

        for d in range(1, num_days + 1):
            col = d + 1
            kod = emp["dni"].get(d, 0)
            linia1, linia2 = shift_display[kod]
            wartosc = f"{linia1}\n{linia2}" if linia2 else linia1

            cell = ws.cell(row=r, column=col, value=wartosc)
            cell.alignment = align
            cell.border = ramka

            if kod == -1:
                cell.fill = urlop_fill
            elif kod == 0:
                cell.fill = wolne_fill
            # dni robocze zostają białe - tak jak w PDF (kolor tylko w nagłówku weekendu)

            if kod == 1:
                licznik_1 += 1
            elif kod == 2:
                licznik_2 += 1
            elif kod == 3:
                licznik_m += 1

        wartosci_sum = [emp["suma_godzin"], emp["etat_docelowy"], licznik_1, licznik_2, licznik_m]
        for i, val in enumerate(wartosci_sum):
            col = start_summary_col + i
            cell = ws.cell(row=r, column=col, value=val)
            cell.alignment = align
            cell.border = ramka
            if col == start_summary_col:  # Godziny zrealizowane vs cel
                cel_godzin = emp["etat_docelowy"]
                cell.font = Font(color="008000", bold=True) if val == cel_godzin else Font(color="FF0000", bold=True)

    last_data_row = first_data_row + len(wyniki) - 1

    # ---------- wiersze podsumowania dziennego (COUNTIF) ----------
    suma_row_1 = last_data_row + 1
    suma_row_2 = last_data_row + 2
    suma_row_3 = last_data_row + 3

    ws.cell(row=suma_row_1, column=1, value="Podsumowanie Otwarcie (1)").font = Font(bold=True)
    ws.cell(row=suma_row_2, column=1, value="Podsumowanie Zamknięcie (2)").font = Font(bold=True)
    ws.cell(row=suma_row_3, column=1, value="Podsumowanie Międzyzmiana (M)").font = Font(bold=True)

    for d in range(1, num_days + 1):
        col = d + 1
        kolumna = get_column_letter(col)
        ws.cell(row=suma_row_1, column=col,
                value=f'=COUNTIF({kolumna}{first_data_row}:{kolumna}{last_data_row}, "{shift_display[1][0]}*")')
        ws.cell(row=suma_row_2, column=col,
                value=f'=COUNTIF({kolumna}{first_data_row}:{kolumna}{last_data_row}, "{shift_display[2][0]}*")')
        ws.cell(row=suma_row_3, column=col,
                value=f'=COUNTIF({kolumna}{first_data_row}:{kolumna}{last_data_row}, "{shift_display[3][0]}*")')

    for row_idx, fill in ((suma_row_1, sum_fill_1), (suma_row_2, sum_fill_2), (suma_row_3, sum_fill_m)):
        for col in range(1, num_days + 2):
            cell = ws.cell(row=row_idx, column=col)
            cell.fill = fill
            cell.font = Font(bold=True)
            cell.alignment = align
            cell.border = ramka

    # ---------- legenda (jak w PDF: Nieobecność / Szkolenia-Delegacje / Specjalne) ----------
    legenda_row = suma_row_3 + 2

    def dodaj_legende(row, etykieta, tresc):
        ws.cell(row=row, column=1, value=etykieta).font = Font(bold=True)
        ws.cell(row=row, column=1).fill = legenda_naglowek_fill
        ws.cell(row=row, column=1).border = ramka
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=min(total_cols, 20))
        c = ws.cell(row=row, column=2, value=tresc)
        c.alignment = align_left
        c.border = ramka

    dodaj_legende(legenda_row, "Legenda zmian:",
                  "WOLNE - dzień wolny  |  URLOP - urlop  |  (1) - zmiana 07:00-15:00  |  "
                  "(2) - zmiana 13:00-21:00  |  (M) - zmiana międzyzmianowa 10:00-18:00")

    # ---------- stopka ----------
    stopka_row = legenda_row + 2
    teraz = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.cell(row=stopka_row, column=1,
            value=f"Przygotował: | Zatwierdził: | Wydrukował: {wydrukowal} {teraz}").font = Font(italic=True, size=9)

    # ---------- szerokości kolumn i wysokości wierszy ----------
    ws.column_dimensions['A'].width = 24
    for d in range(1, num_days + 1):
        ws.column_dimensions[get_column_letter(d + 1)].width = 9
    for i in range(5):
        ws.column_dimensions[get_column_letter(start_summary_col + i)].width = 16

    ws.row_dimensions[header_row_1].height = 18
    ws.row_dimensions[header_row_2].height = 18
    for r in range(first_data_row, last_data_row + 1):
        ws.row_dimensions[r].height = 30  # miejsce na dwie linie tekstu (godziny)

    ws.freeze_panes = ws.cell(row=first_data_row, column=2).coordinate

    # ---------- ustawienia wydruku (opcjonalnie, zbliżone do PDF) ----------
    ws.print_title_rows = f'{header_row_1}:{header_row_2}'
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output