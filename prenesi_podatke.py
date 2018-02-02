import csv
import re
import requests

prva_stran_nepremicnine = "https://www.nepremicnine.net/oglasi-oddaja/"
stran = requests.get(prva_stran_nepremicnine).text
# print(stran)

re_naslednje_strani = re.compile(
    r'<a href=\"(?P<naslednja_stran>\/oglasi-oddaja\/\d+\/)\" class=\"next\">', flags=re.DOTALL
)

# Vsak oglas se zacne z oglas_container, in konca z clearer divom
re_bloka_oglasa = re.compile(
   r'oglas_container'
   r'[\s\S]*?'
   r'<div class=\"clearer\"></div>'
   ,
   flags=re.DOTALL
)

    
#   r'[\s\S]*?'
#   r'(<span class=\"atribut\">Nadstropje: <strong>(?P<nadstropje>.*?)</strong>)'
#   r'[\s\S]*?'

# Tukaj je bil kdaj itemqrop kdaj pa itemprop, zato sta zajeti obe moznosti
re_url_oglasa = re.compile(r'<h2 item[pq]rop=\"name\" data-href=\"(?P<url_oglasa>.*?)\">', flags=re.DOTALL)

re_naslova = re.compile(r'<span class=\"title\">(?P<ime_oglasa>.*?)</span>', flags=re.DOTALL)

re_imena = re.compile(r'<span class=\"title\">(?P<ime_oglasa>.*?)</span>', flags=re.DOTALL)

re_vrste = re.compile(r'<span class=\"vrsta\">(?P<vrsta_stanovanja>.*?)</span>', flags=re.DOTALL)

re_nadstropja = re.compile(r'<span class=\"atribut\">Nadstropje: <strong>(?P<nadstropje>.*?)</strong>', flags=re.DOTALL)

re_leta = re.compile(r'<span class="atribut leto">Leto: <strong>(?P<leto>.*?)</strong>', flags=re.DOTALL)

re_velikosti = re.compile(r'<span class="velikost">(?P<velikost>.*?) m2</span>', flags=re.DOTALL)

re_cene = re.compile(r'<span class="cena">(?P<cena>.*?)</span>', flags=re.DOTALL)

re_ponudnika = re.compile(r'<div class="prodajalec_o" title="(?P<ponudnik>.*?)">')

re_cene_na_m2 = re.compile(r'(?P<cena>.*?) (€|&euro;)/m2/mesec')
re_cene_brez_m2 = re.compile(r'(?P<cena>.*?) (€|&euro;)/mesec')
# Ker se med oglasi za oddajo znajde tudi kaksen, ki se prodaja moramo
# biti pripravljeni tudi na take oglase
re_cene_za_nakup = re.compile(r'(?P<cena>.*?) (€|&euro;)$')

re_podrobnosti_nadstropja = re.compile(r'([a-zA-Z0-9+]*)(/([a-zA-Z0-9]*))?')

def string_to_float(number):
    return float(number.replace('.', '').replace(',', '.'))

def parsaj_ceno(cena, velikost):
    if re_cene_na_m2.search(cena):
        return velikost * string_to_float(re_cene_na_m2.search(cena).group(1))
    elif re_cene_brez_m2.search(cena):
        return string_to_float(re_cene_brez_m2.search(cena).group(1))

def parsaj_oglas(blok):
    stanovanje = {}
    stanovanje['naslov'] = re_naslova.search(blok).group(1)
    stanovanje['kraj'] = stanovanje['naslov'].split(',')[0]
    stanovanje['ime'] = re_imena.search(blok).group(1) 
    stanovanje['vrsta'] = re_vrste.search(blok).group(1)
    stanovanje['url'] = re_url_oglasa.search(blok).group(1)
    stanovanje['ponudnik'] = re_ponudnika.search(blok).group(1)

    nadstropje = re_nadstropja.search(blok)
    if nadstropje:
        stanovanje['nadstropje'] = nadstropje.group(1)

    leto = re_leta.search(blok)
    if leto:
        stanovanje['leto'] = str(int(leto.group(1)))
        stanovanje['mesec'] = 1
        stanovanje['dan'] = 1

    velikost = re_velikosti.search(blok)
    if velikost:
        stanovanje['velikost'] = string_to_float(velikost.group(1))
        velikost = string_to_float(velikost.group(1))

    cena = re_cene.search(blok)
    if cena and not re_cene_za_nakup.search(cena.group(1)):
        stanovanje['cena'] = parsaj_ceno(cena.group(1), velikost)
    return stanovanje

oglasi = []
while stran:
    for blok_ujemanje in re_bloka_oglasa.finditer(stran):
        blok = blok_ujemanje.group()
        oglasi.append(parsaj_oglas(blok))
    if re_naslednje_strani.search(stran):
        print('Obdelujem:', 'https://www.nepremicnine.net' + re_naslednje_strani.search(stran).group(1))
        stran = requests.get('https://www.nepremicnine.net' + re_naslednje_strani.search(stran).group(1)).text
    else:
        break

with open('oglasi.csv', 'w') as datoteka:
        pisalec = csv.DictWriter(datoteka, ['url', 'naslov', 'kraj', 'ime', 'vrsta', 'nadstropje', 'leto', 'velikost', 'cena', 'ponudnik', 'dan', 'mesec'], extrasaction='ignore')
        pisalec.writeheader()
        for oglas in oglasi:
            pisalec.writerow(oglas)
