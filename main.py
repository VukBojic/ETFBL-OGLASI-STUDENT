from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re

# Definišite apsolutnu putanju do sent_ads.txt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Direktorijum u kome se nalazi skripta
SENT_ADS_PATH = os.path.join(BASE_DIR, "sent_ads.txt")  # Apsolutna putanja do sent_ads.txt

# Konfiguracija
URL = "https://efee.etf.unibl.org/oglasi/"

# Lista korisnika sa njihovim emailovima i predmetima koje prate
KORISNICI = [
    {
        "email": "vuk.bojic@student.etf.unibl.org",
        "predmeti": [
            "Formalne metode u softverskom inženjerstvu",
            "Математика 4",
            "Основи комуникација и теорија информација",
            "Програмски језици 2",
            "Основи оперативних система",
            "Основи електротехнике 1",
            "Основи електротехнике 2"
        ]
    },
    {
        "email": "akidobra@gmail.com",
        "predmeti": [
            "Програмски језици 2",
            "Основи оперативних система",
            "Програмски језици 1",
            "Математика 4",
            "Основи комуникација и теорија информација",
            "Formalne metode u softverskom inženjerstvu",
            "Основи софтверског инжењерства",
            "Основи електронике и дигиталне технике"
        ]
    },
    # Dodajte više korisnika po potrebi
]

# Funkcija za slanje emaila
def posalji_email(subject, body, to_email):
    from_email = "vuk.bojic2023@gmail.com"  # Unesite vaš email
    from_password = "ftlf cfge ozcp jagd"  # Unesite vašu email lozinku

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Koristimo HTML format umjesto plain text
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Email uspešno poslat na {to_email}!")
    except Exception as e:
        print(f"Greška pri slanju emaila na {to_email}: {e}")

# Funkcija za formatiranje oglasa
def formatiraj_oglas(oglas_text):
    lines = oglas_text.split('\n')
    if len(lines) < 2:
        return oglas_text  # Ako oglas nema dovoljno redova, vrati ga neformatiranog

    # Prva linija je naziv predmeta
    predmet = lines[0].strip()
    # Druga linija je datum i vrijeme
    datum_vrijeme = lines[1].strip()
    # Ostale linije su sadržaj oglasa
    sadrzaj = "<br>".join(lines[2:]).strip()

    # Formatiranje u HTML
    formatiran_oglas = (
        f"<b>{predmet}</b><br>"
        f"Datum i vrijeme: {datum_vrijeme}<br>"
        f"{sadrzaj}<br>"
        "<hr>"
    )
    return formatiran_oglas

# Funkcija za normalizaciju oglasa
def normalizuj_oglas(oglas_text):
    # Uklanja višestruke razmake i specijalne karaktere
    oglas_text = re.sub(r'\s+', ' ', oglas_text)  # Zamena višestrukih razmaka jednim razmakom
    oglas_text = oglas_text.strip()  # Uklanja početne i krajnje razmake
    return oglas_text

# Funkcija za dobijanje oglasa sa stranice
def get_oglasi():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(URL)

    try:
        # Čekamo da se učita stranica i svi <ul> tagovi
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ul_id_1"))  # Prva godina
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ul_id_2"))  # Druga godina
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ul_id_3"))  # Treća godina
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ul_id_4"))  # Četvrta godina
        )
        print("✅ Oglasi su učitani!")
    except:
        print("⚠️ Oglasi nisu učitani na vreme!")
        driver.quit()
        return {}

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    oglasi_po_godinama = {
        "prva_godina": [],
        "druga_godina": [],
        "treca_godina": [],
        "cetvrta_godina": []
    }

    # Čitanje oglasa za prvu godinu (ul_id_1)
    ul_tag_prva_godina = soup.find("ul", id="ul_id_1")
    if ul_tag_prva_godina and ul_tag_prva_godina.find_all("li"):
        for li in ul_tag_prva_godina.find_all("li"):
            oglas_text = li.get_text(separator="\n").strip()
            oglasi_po_godinama["prva_godina"].append(oglas_text)

    # Čitanje oglasa za drugu godinu (ul_id_2)
    ul_tag_druga_godina = soup.find("ul", id="ul_id_2")
    if ul_tag_druga_godina and ul_tag_druga_godina.find_all("li"):
        for li in ul_tag_druga_godina.find_all("li"):
            oglas_text = li.get_text(separator="\n").strip()
            oglasi_po_godinama["druga_godina"].append(oglas_text)

    # Čitanje oglasa za treću godinu (ul_id_3)
    ul_tag_treca_godina = soup.find("ul", id="ul_id_3")
    if ul_tag_treca_godina and ul_tag_treca_godina.find_all("li"):
        for li in ul_tag_treca_godina.find_all("li"):
            oglas_text = li.get_text(separator="\n").strip()
            oglasi_po_godinama["treca_godina"].append(oglas_text)

    # Čitanje oglasa za četvrtu godinu (ul_id_4)
    ul_tag_cetvrta_godina = soup.find("ul", id="ul_id_4")
    if ul_tag_cetvrta_godina and ul_tag_cetvrta_godina.find_all("li"):
        for li in ul_tag_cetvrta_godina.find_all("li"):
            oglas_text = li.get_text(separator="\n").strip()
            oglasi_po_godinama["cetvrta_godina"].append(oglas_text)

    return oglasi_po_godinama

# Funkcija za učitavanje poslatih oglasa iz fajla
def ucitaj_poslate_oglasa():
    if not os.path.exists(SENT_ADS_PATH):
        return {}  # Ako fajl ne postoji, vraćamo prazan rečnik

    poslate_oglasa = {}
    with open(SENT_ADS_PATH, "r", encoding="utf-8") as f:
        for line in f.read().splitlines():
            if ":" in line:
                email, oglasi = line.split(":", 1)
                poslate_oglasa[email] = set(oglasi.split("|"))
    return poslate_oglasa

# Funkcija za čuvanje poslatih oglasa u fajl
def sacuvaj_poslate_oglasa(poslate_oglasa):
    with open(SENT_ADS_PATH, "w", encoding="utf-8") as f:
        for email, oglasi in poslate_oglasa.items():
            f.write(f"{email}:{'|'.join(oglasi)}\n")

# Glavna funkcija
def main():
    # Provera da li sent_ads.txt postoji, ako ne, kreiraj ga
    if not os.path.exists(SENT_ADS_PATH):
        with open(SENT_ADS_PATH, "w", encoding="utf-8") as f:
            f.write("")

    poslate_oglasa = ucitaj_poslate_oglasa()  # Učitamo poslednje oglase iz fajla
    oglasi_po_godinama = get_oglasi()  # Dobijamo trenutne oglase grupisane po godinama

    # Normalizujemo trenutne oglase za poređenje
    trenutni_oglasi_normalizovani = set()
    for godina, oglasi in oglasi_po_godinama.items():
        for oglas in oglasi:
            trenutni_oglasi_normalizovani.add(normalizuj_oglas(oglas))

    # Prolazimo kroz sve korisnike i šaljemo im odgovarajuće oglase
    for korisnik in KORISNICI:
        email = korisnik["email"]
        predmeti_korisnika = korisnik["predmeti"]

        # Inicijalizujemo skup poslatih oglasa za ovog korisnika ako ne postoji
        if email not in poslate_oglasa:
            poslate_oglasa[email] = set()

        # Pronalaženje novih oglasa za ovog korisnika
        novi_oglasi = []
        for godina, oglasi in oglasi_po_godinama.items():
            for oglas in oglasi:
                oglas_normalizovan = normalizuj_oglas(oglas)
                if oglas_normalizovan not in poslate_oglasa[email]:
                    for predmet in predmeti_korisnika:
                        if predmet in oglas:
                            novi_oglasi.append(oglas)
                            poslate_oglasa[email].add(oglas_normalizovan)
                            break

        if novi_oglasi:
            print(f"Pronađeno {len(novi_oglasi)} novih oglasa za {email}!")

            # Formatiranje i slanje emaila
            body = "<html><body>"
            for godina, oglasi in oglasi_po_godinama.items():
                if oglasi:  # Ako postoje oglasi za ovu godinu
                    body += f"<h2>Obaveštenja za {godina.replace('_', ' ').capitalize()}:</h2><br>"
                    for oglas in oglasi:
                        if normalizuj_oglas(oglas) in poslate_oglasa[email]:
                            for predmet in predmeti_korisnika:
                                if predmet in oglas:
                                    body += formatiraj_oglas(oglas)
                                    break
            body += "</body></html>"

            posalji_email("Novi oglasi za vaše predmete", body, email)
        else:
            print(f"Nema novih oglasa za {email}.")

    # Čuvanje ažuriranih poslatih oglasa u fajl
    sacuvaj_poslate_oglasa(poslate_oglasa)

# Pokretanje glavne funkcije
if __name__ == "__main__":
    main()
