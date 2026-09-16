import streamlit as st
import calendar

# Importy z naszego backendu (folder core)
from core.calendar_utils import generuj_kalendarz_miesiac
from core.scheduler import rozwiaz_grafik
from core.excel_generator import generuj_plik_excel

# Konfiguracja strony
st.set_page_config(page_title="Generator Grafików", layout="wide")

# Inicjalizacja stanu (Session State) dla pracowników
# Dzięki temu aplikacja zapamięta zespół między kliknięciami
if "pracownicy" not in st.session_state:
    st.session_state.pracownicy = [
        {"imie": "Anna (Lider)", "is_leader": True, "urlopy": [], "dni_wolne": []},
        {"imie": "Piotr (Lider)", "is_leader": True, "urlopy": [], "dni_wolne": []},
        {"imie": "Krzysztof", "is_leader": False, "urlopy": [], "dni_wolne": []},
        {"imie": "Rafał", "is_leader": False, "urlopy": [], "dni_wolne": []},
        {"imie": "Alicja", "is_leader": False, "urlopy": [], "dni_wolne": []},
        {"imie": "Robert P.", "is_leader": False, "urlopy": [], "dni_wolne": []},
        {"imie": "Robert Z.", "is_leader": False, "urlopy": [], "dni_wolne": []}
    ]

st.title("Automatyczny Generator Grafików")
st.markdown("Skonfiguruj zespół, wybierz datę, przypisz urlopy i wygeneruj gotowy plik Excel jednym kliknięciem.")

# ==========================================
# PANEL BOCZNY: USTAWIENIA DATY
# ==========================================
st.sidebar.header("1. Wybierz okres")
rok = st.sidebar.selectbox("Rok", [2026, 2027, 2028])
miesiace_nazwy = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", 
                  "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
miesiac_nazwa = st.sidebar.selectbox("Miesiąc", miesiace_nazwy, index=5) # Domyślnie Czerwiec (index 5)
miesiac = miesiace_nazwy.index(miesiac_nazwa) + 1

liczba_dni = calendar.monthrange(rok, miesiac)[1]
st.sidebar.info(f"Liczba dni roboczych/wolnych zostanie obliczona automatycznie dla **{liczba_dni} dni**.")

# ==========================================
# EKRAN GŁÓWNY: ZESPÓŁ I URLOPY
# ==========================================
st.header("2. Zarządzanie Zespołem i Urlopami")

# Formularz dodawania pracownika
with st.expander("Dodaj nowego pracownika"):
    with st.form("dodaj_pracownika_form"):
        col1, col2 = st.columns([3, 1])
        nowe_imie = col1.text_input("Imię i Nazwisko")
        nowy_lider = col2.checkbox("Czy to Lider?")
        submitted = st.form_submit_button("Dodaj do zespołu")
        if submitted and nowe_imie:
            st.session_state.pracownicy.append({"imie": nowe_imie, "is_leader": nowy_lider, "urlopy": [], "dni_wolne": []})
            st.success(f"Dodano pracownika: {nowe_imie}")
            st.rerun()

# Lista pracowników z możliwością edycji urlopów i usuwania
st.subheader("Obecny zespół (Wybierz dni urlopu)")
for i, emp in enumerate(st.session_state.pracownicy):
    # Zmieniamy układ na 5 kolumn
    col1, col2, col3, col4, col5 = st.columns([2, 1, 3, 3, 1])
    
    with col1:
        st.write(f"**{emp['imie']}**")
    
    with col2:
        if emp['is_leader']:
            st.markdown("**Lider**")
        else:
            st.write("-")
            
    with col3:
        wybrane_urlopy = st.multiselect(
            f"Urlop - {emp['imie']}",
            options=list(range(1, liczba_dni + 1)),
            default=[d for d in emp.get('urlopy', []) if d <= liczba_dni],
            key=f"urlop_{i}",
            label_visibility="collapsed",
            placeholder="Urlopy..."
        )
        st.session_state.pracownicy[i]['urlopy'] = wybrane_urlopy

    with col4:
        # NOWE: Pasek wyboru żądanych dni wolnych
        wybrane_wolne = st.multiselect(
            f"Wolne - {emp['imie']}",
            options=list(range(1, liczba_dni + 1)),
            default=[d for d in emp.get('dni_wolne', []) if d <= liczba_dni],
            key=f"wolne_{i}",
            label_visibility="collapsed",
            placeholder="Wolne na żądanie..."
        )
        st.session_state.pracownicy[i]['dni_wolne'] = wybrane_wolne
        
    with col5:
        if st.button("Usuń", key=f"usun_{i}"):
            st.session_state.pracownicy.pop(i)
            st.rerun()

st.divider()

# ==========================================
# EKRAN GŁÓWNY: GENEROWANIE GRAFIKU
# ==========================================
st.header("3. Generowanie Grafiku")
if st.button("Wygeneruj Grafik", type="primary", use_container_width=True):
    with st.spinner("Trwa generowanie grafiku zgodnie z regułami Kodeksu Pracy i obsady sklepu..."):

        # 1. Wygeneruj dynamiczny kalendarz i etaty
        dane_kalendarza = generuj_kalendarz_miesiac(rok, miesiac)

        # 2. Uruchom solver matematyczny
        wyniki = rozwiaz_grafik(st.session_state.pracownicy, dane_kalendarza)

        # 3. Sprawdź wynik
        if wyniki:
            st.success("Grafik został wygenerowany zgodnie z regułami Kodeksu Pracy i wymogami obsady sklepu.")

            # 4. Zbuduj Excela w pamięci RAM
            plik_excel_bytes = generuj_plik_excel(wyniki, rok, miesiac)

            if plik_excel_bytes:
                st.download_button(
                    label="Pobierz grafik (plik XLSX)",
                    data=plik_excel_bytes,
                    file_name=f"Grafik_{rok}_{miesiac:02d}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
        else:
            st.error("Nie udało się wygenerować grafiku dla podanych ustawień.")
            st.warning("Najczęstsze przyczyny:\n"
                       "1. Zbyt wiele osób (lub wszyscy liderzy) ma urlop w tym samym czasie.\n"
                       "2. Wybrane urlopy lub dni wolne uniemożliwiają wyrobienie pełnego etatu przez pracownika (w 8-godzinnych blokach).")