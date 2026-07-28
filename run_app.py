import sys
import os
from streamlit.web import cli as stcli

def main():
    # Sprawdzenie, czy skrypt jest uruchamiany jako spakowany .exe
    if getattr(sys, 'frozen', False):
        dirname = sys._MEIPASS
    else:
        dirname = os.path.dirname(os.path.abspath(__file__))
    
    app_path = os.path.join(dirname, 'app.py')
    
    # Uruchomienie Streamlita wewnątrz pliku exe
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())

if __name__ == '__main__':
    main()