from ortools.sat.python import cp_model

def rozwiaz_grafik(pracownicy, kalendarz):
    num_employees = len(pracownicy)
    num_days = kalendarz["liczba_dni"]
    LIDERS = [i for i, p in enumerate(pracownicy) if p.get("is_leader", False)]

    # 0: Wolne, 1: Rano (07-15), 2: Zamknięcie (13-21), 3: Międzyzmiana (10-18)
    shifts = [0, 1, 2, 3]
    shift_hours = {0: 0, 1: 8, 2: 8, 3: 8}

    working_days = kalendarz["dni_robocze"] + kalendarz["soboty"]
    wolne_odgorne = kalendarz["niedziele"] + kalendarz["swieta"]
    
    model = cp_model.CpModel()
    work = {}

    for e in range(num_employees):
        for d in range(1, num_days + 1):
            for s in shifts:
                work[(e, d, s)] = model.NewBoolVar(f'w_{e}_{d}_{s}')

    for e, emp in enumerate(pracownicy):
        for d in range(1, num_days + 1):
            model.AddExactlyOne(work[(e, d, s)] for s in shifts)

        # NOWE: Odgórne wolne + urlopy + dni wolne na żądanie
        wymuszone_wolne = set(wolne_odgorne + emp.get("urlopy", []) + emp.get("dni_wolne", []))
        
        for d in wymuszone_wolne:
            if 1 <= d <= num_days:
                model.Add(work[(e, d, 0)] == 1)

        # 11h Odpoczynku
        for d in range(1, num_days):
            model.AddImplication(work[(e, d, 2)], work[(e, d+1, 1)].Not())

        # Wymiar etatu - uwaga: odejmujemy tylko URLOPY, a dni wolne zmuszają 
        # algorytm do rozbicia tych 8 godzin na pozostałe dni robocze
        urlopy_w_robocze = len([day for day in emp.get("urlopy", []) if day in working_days and 1 <= day <= num_days])
        etat_docelowy = kalendarz["baza_etatu"] - (urlopy_w_robocze * 8)
        
        suma_godzin = sum(work[(e, d, s)] * shift_hours[s] for d in range(1, num_days + 1) for s in shifts)
        model.Add(suma_godzin == etat_docelowy)

    # Wymagania sklepowe
    # =====================================================================
    # NOWE REGUŁY OBSADY (ZASADA 2 - 2 - Reszta na M) Z PODZIAŁEM NA SOBOTY
    # =====================================================================
    for d in working_days:
        # Minimum 1 Lider każdego dnia na sklepie
        model.Add(sum(work[(e, d, s)] for e in LIDERS for s in [1, 2, 3]) >= 1)
        
        # Zawsze 2 osoby na otwarciu (07:00-15:00) niezależnie od dnia
        model.Add(sum(work[(e, d, 1)] for e in range(num_employees)) == 2)
        
        # Zawsze 2 osoby na zamknięciu (13:00-21:00) niezależnie od dnia
        model.Add(sum(work[(e, d, 2)] for e in range(num_employees)) == 2)
        
        if d in kalendarz["soboty"]:
            # W SOBOTY: Mocne wzmocnienie! Minimum 2 osoby na międzyzmianie (łącznie min. 6 osób)
            model.Add(sum(work[(e, d, 3)] for e in range(num_employees)) >= 2)
        else:
            # W TYGODNIU: Wystarczy minimum 1 osoba na międzyzmianie (łącznie min. 5 osób)
            model.Add(sum(work[(e, d, 3)] for e in range(num_employees)) >= 1)
            
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0 
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        wyniki = []
        for e, emp in enumerate(pracownicy):
            urlopy_w_robocze = len([day for day in emp.get("urlopy", []) if day in working_days and 1 <= day <= num_days])
            pracownik_dane = {
                "imie": emp["imie"],
                "dni": {},
                "suma_godzin": 0,
                "etat_docelowy": kalendarz["baza_etatu"] - (urlopy_w_robocze * 8)
            }
            for d in range(1, num_days + 1):
                if d in emp.get("urlopy", []):
                    pracownik_dane["dni"][d] = -1 # -1 oznacza urlop
                else:
                    for s in shifts:
                        if solver.BooleanValue(work[(e, d, s)]):
                            pracownik_dane["dni"][d] = s
                            pracownik_dane["suma_godzin"] += shift_hours[s]
            wyniki.append(pracownik_dane)
        return wyniki
    return None