import calendar
import datetime

def oblicz_wielkanoc(rok):
    a = rok % 19
    b = rok // 100
    c = rok % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    miesiac = (h + l - 7 * m + 114) // 31
    dzien = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(rok, miesiac, dzien)

def pobierz_swieta_polska(rok):
    wielkanoc = oblicz_wielkanoc(rok)
    poniedzialek_wielkanocny = wielkanoc + datetime.timedelta(days=1)
    boze_cialo = wielkanoc + datetime.timedelta(days=60)
    zielone_swiatki = wielkanoc + datetime.timedelta(days=49)
    
    stale = [
        datetime.date(rok, 1, 1), datetime.date(rok, 1, 6),
        datetime.date(rok, 5, 1), datetime.date(rok, 5, 3),
        datetime.date(rok, 8, 15), datetime.date(rok, 11, 1),
        datetime.date(rok, 11, 11), datetime.date(rok, 12, 25),
        datetime.date(rok, 12, 26)
    ]
    ruchome = [wielkanoc, poniedzialek_wielkanocny, zielone_swiatki, boze_cialo]
    return set(stale + ruchome)

def generuj_kalendarz_miesiac(rok, miesiac):
    swieta = pobierz_swieta_polska(rok)
    liczba_dni = calendar.monthrange(rok, miesiac)[1]
    
    niedziele = []
    soboty = []
    dni_swiateczne = []
    dni_robocze_tydzien = []
    
    for dzien in range(1, liczba_dni + 1):
        d = datetime.date(rok, miesiac, dzien)
        wd = d.weekday()
        
        if wd == 6:
            niedziele.append(dzien)
        elif wd == 5:
            if d in swieta:
                dni_swiateczne.append(dzien)
            else:
                soboty.append(dzien)
        else:
            if d in swieta:
                dni_swiateczne.append(dzien)
            else:
                dni_robocze_tydzien.append(dzien)
                
    # POPRAWIONA LOGIKA OBLICZANIA ETATU (Dni robocze Pon-Pt - Święta w Soboty)
    liczba_roboczych_pon_pt = len(dni_robocze_tydzien)
    swieta_w_soboty = len([d for d in dni_swiateczne if datetime.date(rok, miesiac, d).weekday() == 5])
    
    baza_etatu = (liczba_roboczych_pon_pt * 8) - (swieta_w_soboty * 8)
    
    return {
        "liczba_dni": liczba_dni,
        "niedziele": niedziele,
        "soboty": soboty,
        "swieta": dni_swiateczne,
        "dni_robocze": dni_robocze_tydzien,
        "baza_etatu": baza_etatu
    }