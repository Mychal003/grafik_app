# Generator Grafików Pracy - Dokumentacja Techniczna

## 1. Wprowadzenie
Niniejsza dokumentacja opisuje architekturę, zasady działania algorytmu optymalizacyjnego oraz instrukcję uruchomienia aplikacji do automatycznego tworzenia harmonogramów czasu pracy. Aplikacja została zbudowana w języku Python z wykorzystaniem biblioteki Google OR-Tools do rozwiązywania problemów optymalizacyjnych oraz frameworka Streamlit dla interfejsu użytkownika.

## 2. Zasady działania algorytmu

Algorytm rozwiązuje problem przydziału zmian jako problem programowania w liczbach całkowitych (Constraint Programming), spełniając zbiór twardych reguł biznesowych oraz prawnych.

### 2.1. Wymiar czasu pracy (Norma Kodeksowa)
System automatycznie wylicza nominalny czas pracy na podstawie podanego roku i miesiąca:
* Mnoży liczbę dni roboczych (od poniedziałku do piątku) przez 8 godzin.
* Odejmuje 8 godzin za każde święto państwowe przypadające w sobotę.
* Święta przypadające w niedzielę nie obniżają wymiaru czasu pracy.

### 2.2. Reguły obsady stanowisk (Struktura 2-2-Rezerwa)
Harmonogram jest budowany na sztywnym szkielecie skrajnych zmian, podczas gdy tak zwana międzyzmiana pełni funkcję bufora pochłaniającego pozostałe roboczogodziny.
* **Otwarcie (07:00-15:00):** Wymagane obsadzenie przez dokładnie 2 pracowników każdego dnia pracującego.
* **Zamknięcie (13:00-21:00):** Wymagane obsadzenie przez dokładnie 2 pracowników każdego dnia pracującego.
* **Międzyzmiana (10:00-18:00):** W dni powszednie przypisywana jest minimum 1 osoba (łącznie minimum 5 osób na obiekcie). W soboty przypisywane są minimum 2 osoby (łącznie minimum 6 osób na obiekcie).

### 2.3. Przerwy dobowe i wymogi kadrowe
* **11 godzin odpoczynku:** Algorytm kategorycznie blokuje możliwość przypisania pracownika do zmiany porannej, jeśli w dniu poprzednim realizował zmianę zamykającą.
* **Obecność lidera:** System gwarantuje obecność co najmniej jednego pracownika o statusie "Lider" każdego dnia pracującego, na dowolnej ze zmian.

### 2.4. Urlopy i dni wolne na żądanie
* **Urlop:** Każdy dzień urlopu przypadający w dniu roboczym proporcjonalnie obniża nominalny wymiar czasu pracy danego pracownika o 8 godzin.
* **Dni wolne:** Wymuszają brak przypisania zmiany w danym dniu, jednak nie obniżają całkowitej puli godzin do wypracowania. Pozostałe godziny są kumulowane w innych dostępnych dniach roboczych w danym miesiącu.

## 3. Struktura projektu

Aplikacja została podzielona modułowo w celu separacji logiki od warstwy wizualnej:
* `app.py` - Główny plik interfejsu użytkownika (Streamlit). Odpowiada za przyjmowanie parametrów wejściowych oraz prezentację wyników.
* `run_app.py` - Skrypt rozruchowy (wrapper) umożliwiający uruchomienie aplikacji jako skompilowany plik wykonywalny bez konieczności obsługi terminala.
* `core/calendar_utils.py` - Moduł odpowiedzialny za dynamiczne wyliczanie dni roboczych, świąt ruchomych i stałych oraz norm czasu pracy.
* `core/scheduler.py` - Główny silnik optymalizacyjny oparty na bibliotece OR-Tools.
* `core/excel_generator.py` - Moduł formatowania i eksportu wyliczonego harmonogramu do postaci pliku arkusza kalkulacyjnego (.xlsx).

## 4. Instrukcja uruchomienia

### Opcja A: Uruchomienie ze skompilowanego pliku (.exe na systemach Windows)
Wersja przeznaczona dla stacji roboczych bez zainstalowanego środowiska Python.

1. Przenieś kompletny folder docelowy (zawierający plik wykonywalny `run_app.exe`) na dowolny nośnik pamięci lub dysk lokalny komputera. Ważne: nie należy wyodrębniać samego pliku wykonywalnego poza strukturę folderu bazowego.
2. Wewnątrz folderu uruchom plik `run_app.exe`.
3. Zostanie uruchomione okno konsoli (wiersz poleceń), które inicjuje lokalny serwer aplikacji.
4. Domyślna przeglądarka internetowa uruchomi się automatycznie i wyświetli interfejs graficzny pod adresem lokalnym (zazwyczaj `http://localhost:8501`).
5. Zakończenie pracy z programem wymaga zamknięcia karty w przeglądarce oraz ręcznego zamknięcia okna konsoli.

### Opcja B: Uruchomienie ze środowiska deweloperskiego (kod źródłowy)
Wymaga zainstalowanego interpretera Python oraz narzędzia do zarządzania pakietami (na przykład `uv`).

1. Otwórz terminal roboczy w głównym katalogu projektu.
2. Aktywuj wirtualne środowisko poleceniem odpowiednim dla systemu operacyjnego.
3. Zainstaluj wymagane pakiety uruchamiając polecenie:
   `uv pip install streamlit ortools pandas openpyxl`
4. Uruchom serwer aplikacji poleceniem:
   `streamlit run app.py`
