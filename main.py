from elasticsearch import Elasticsearch
es = Elasticsearch(['localhost'],port=9200)

#FUNKCIA KTORÁ VYHĽADÁ SEKCIU MEDZI REDIRECTMI A ODKAZMI NA SEKCIE 
def vyhladaj_sekciu():
    print("\nZadaj názov sekcie, ktorú chceš vyhľadať a stlač ENTER:")
    nazov_sekcie = input()
    res = es.search(index="linkandredindex", body=
    {
        "size": 1000,
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "section": {
                            "query": 
                                nazov_sekcie,
                                "operator": "and"
                        }
                    }
                }
            }
        }
    })
    return res

#FUNKCIA KTORÁ VRÁTI SAMOTNÚ SEKCIU PO ZADANÍ NÁZVU SEKCIE A NÁZVU ČLÁNKU V KTOROM SA SEKCIA VYSKYTUJE
def vypis_sekciu(sekciasekcia, sekciasekcia_clanok):  
    res = es.search(index="sectionindex", body=
    {
        "size": 1000,
        "query": {
            "bool": {
                "must": [
                    { "match": { "section.name": {"query": sekciasekcia, "operator": "and"}}},
                    { "match": { "title": {"query": sekciasekcia_clanok, "operator": "and"}}}
                ]
            }
        }
    })
    return res

res = vyhladaj_sekciu()
match = res['hits']['total']['value']

while match == 0:
    print("Nenašli sa žiadne sekcie, skús ešte raz!")
    res = vyhladaj_sekciu()
    match = res['hits']['total']['value']

dictionary = {}
dictionary2 = {}
odkaz = 0
redir = 0
for hit in res['hits']['hits']:
    if hit['_source']['type'] == 'odkaz':
        odkaz +=1
    else:
        redir +=1
print("_______________________________________________________________________________________")
print("\nPodarilo sa nájsť %dx presmerovanie na sekciu a %dx odkaz na sekciu." %(redir, odkaz))
print("Napíšte 1 pre vypísanie redirectov na sekcie alebo 2 pre vypísanie sekcií z odkazov, následne stlačte ENTER")
odkaz_alebo_redir = input()
print("_______________________________________________________________________________________")

# PARAMETER JE 1 AK POUŽÍVATEĽ CHCE VYHĽADÁVAŤ V REDIREKTOCH
if odkaz_alebo_redir == "1":
    print("Nájdené sekcie z presmerovania sú:")
    pocitadlo = 0
    pocitadlo2 = 0
    for hit in res['hits']['hits']:
        pocitadlo += 1
        pocitadlo2 += 1 
        if hit['_source']['type'] == 'redirect':
            print("%d. Sekcia s názvom %s presmerovaná na článok s názvom %s" % ( pocitadlo2, hit['_source']['section'], hit['_source']['section_title'] ))
            dictionary[str(pocitadlo2)] = hit['_source']['section']
            dictionary2[str(pocitadlo2)] = hit['_source']['section_title']
        else:
            pocitadlo -= 1
            pocitadlo2 -= 1
            continue
        if pocitadlo == 10:
            print("_______________________________________________________________________________________")
            print("Prajete si pokračovať? (A - áno, N - nie)")
            pokracovanie = input()
            if pokracovanie == 'A':
                pocitadlo = 0
                continue
            elif pokracovanie == 'N':
                break
    print("Vypísať text sekcie? (A - áno, N - nie)")
    vypisanie = input()
    if vypisanie == 'N':
        exit()
    else:
        print("Vyberte číslo sekcie, ktorú chcete vypísať.")
        vypis_text = input()

        resres = vypis_sekciu(dictionary[vypis_text], dictionary2[vypis_text])
        print("_______________________________________________________________________________________")
        print("Článok s názvom %s\n" % resres['hits']['hits'][0]['_source']['title'])
        print("Sekcia úrovne %d s názvom %s" % (resres['hits']['hits'][0]['_source']['section'][0]['level'], resres['hits']['hits'][0]['_source']['section'][0]['name']))
        print("Obsah sekcie:")
        print("%s" % resres['hits']['hits'][0]['_source']['section'][1]['content'])
        print("_______________________________________________________________________________________")

# PARAMETER JE 2 AK CHCE POUZIVATEL VYHLADAVAT V ODKAZOCH NA SEKCIE
elif odkaz_alebo_redir == "2":
    print("Nájdené sekcie z odkazov sú:")
    pocitadlo = 0
    pocitadlo2 = 0
    for hit in res['hits']['hits']:
        pocitadlo += 1
        pocitadlo2 += 1 
        if hit['_source']['type'] == 'odkaz':
            print("%d. Link na sekciu s názvom %s ktorá sa nachádza v článku s názvom %s" % ( pocitadlo2, hit['_source']['section'], hit['_source']['section_title'] ))
            dictionary[str(pocitadlo2)] = hit['_source']['section']
            dictionary2[str(pocitadlo2)] = hit['_source']['section_title']
        else:
            pocitadlo -= 1
            pocitadlo2 -= 1
            continue
        if pocitadlo == 10:
            print("_______________________________________________________________________________________")
            print("Prajete si pokračovať? (A - áno, N - nie)")
            pokracovanie = input()
            if pokracovanie == 'A':
                pocitadlo = 0
                continue
            elif pokracovanie == 'N':
                break
    print("Vypísať text sekcie? (A - áno, N - nie)")
    vypisanie = input()
    if vypisanie == 'N':
        exit()
    else:
        print("Vyberte číslo sekcie, ktorú chcete vypísať.")
        vypis_text = input()

        resres = vypis_sekciu(dictionary[vypis_text], dictionary2[vypis_text])
        print("_______________________________________________________________________________________")
        print("Článok s názvom %s\n" % resres['hits']['hits'][0]['_source']['title'])
        print("Sekcia úrovne %d s názvom %s" % (resres['hits']['hits'][0]['_source']['section'][0]['level'], resres['hits']['hits'][0]['_source']['section'][0]['name']))
        print("Obsah sekcie:")
        print("%s" % resres['hits']['hits'][0]['_source']['section'][1]['content'])
        print("_______________________________________________________________________________________")

else:
    print("Toto číslo je nesprávne!!")
    exit()