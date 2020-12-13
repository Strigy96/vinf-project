import os.path
import re
from elasticsearch import Elasticsearch
from elasticsearch import helpers
es = Elasticsearch(['localhost'],port=9200)

# FUNKCIA RETURNUJE YIELD KTORY JE POTREBNY NA BULK IMPORT DO ELASTICSEARCHU
def import_sekcii():

    #NA RYCHLEJSIE HLADANIE VYUZIVAM DICTIONARY
    link_na_sekciu_dict = {}
    redirect_na_sekciu_dict = {}
    section_dict = {}

    #ZADEFINOVANIE POMOCNYCH PREMENNYCH
    riadok = ''
    text = ''
    id_sekcie = 0
    pomocna = 0
    mam_redirect = 0
    extrakcia_textu = 0
    riadky_citacie = 0
    counter = 0
    token = '\[\[(.*)\]\]'

    # VYTVORENIE TOKENOV NA PARSOVANIE SEKCIE
    sekcia_text_token_level1 = '=(.*)='
    sekcia_text_token_level2 = '==(.*)=='
    sekcia_text_token_level3 = '===(.*)==='
    sekcia_text_token_level4 = '====(.*)===='
    sekcia_text_token_level5 = '=====(.*)====='
    sekcia_text_token_level6 = '======(.*)======'

    with open('data/skwiki-latest-pages-articles.xml', encoding='utf-8') as file:
        
        # PRECHADZANIE RIADOK PO RIADKU
        for line in file:
            mam_redirect = 0

            # AK SA NACHADZAME V TEXTE, PARSUJEME HO CELY
            if extrakcia_textu == 1 and line[0] != '=':
                upraveny_riadok = line
                if riadky_citacie == 1:
                    if '&lt;/ref&gt;' not in line:
                        continue
                    else:
                        rozdelenie = re.split('&lt;/ref&gt;',upraveny_riadok)
                        if rozdelenie[1] != None:
                            upraveny_riadok = rozdelenie[1]
                        else:
                            upraveny_riadok = '\n'
                        riadky_citacie = 0
                if '&lt;ref&gt;{{' in upraveny_riadok:
                    rozdelenie = re.split('&lt;ref&gt;{{',upraveny_riadok)
                    upraveny_riadok = rozdelenie[0]
                    if '&lt;/ref&gt;' in rozdelenie[1]:
                        rozdelenie2 = re.split('&lt;/ref&gt;',rozdelenie[1])
                        if rozdelenie2[1] != None:
                            upraveny_riadok = rozdelenie[0] + ' ' + rozdelenie2[1]
                        else:
                            upraveny_riadok = rozdelenie[0] + '\n'
                    else:
                        riadky_citacie = 1
                if '&lt;ref name' in upraveny_riadok:
                    if (re.search('&lt;ref name(.*)&lt;/ref&gt;', upraveny_riadok)) != None:
                        referencia_s_menom = re.search('&lt;ref name(.*)&lt;/ref&gt;', upraveny_riadok).group(1)
                        upraveny_riadok.replace(referencia_s_menom,'')
                    else:
                        referencia_s_menom = re.search('&lt;ref name(.*)', upraveny_riadok).group(1)
                        upraveny_riadok.replace(referencia_s_menom,'')

                if '&quot;' in upraveny_riadok:
                    rozdelenie = re.split('&quot;',upraveny_riadok)
                    upraveny_riadok = ''.join(rozdelenie)
                if '</text>' in upraveny_riadok:
                    rozdelenie = re.split('</text',upraveny_riadok)
                    upraveny_riadok = rozdelenie[0] + '\n'
                    extrakcia_textu = 0
                text += upraveny_riadok
            
            # AK SME Z TEXTU VYSTUPILI, INSERTNE SA ZAZNAM DO ELASTICU
            elif extrakcia_textu == 1 and line[0] == '=':
                extrakcia_textu = 0
                objekt = {}
                objekt["content"] = text
                section_dict["section"].append(objekt)
                yield{
                    "_index": "sectionindex",
                    "_type": "_doc",
                    "_id": id_sekcie,
                    "_source" : section_dict
                }
                text = ''

            else:
                extrakcia_textu = 0

            # UKLADANIE TITLOV A DEFINOVANIE KEDY SA NACHÁDZAME V TEXTE
            if '<title>' in line:
                title = re.search('<title>(.*)</title>', line)
                title = title.group(1)
            if '</text' in line or '</comment' in line:
                pomocna = 0
            if '<text' in line or '<comment' in line:
                pomocna = 1
            
            #RIEŠENIE REDIRECTOV NA SEKCIE
            if '>#redirect' in line or '>#REDIRECT' in line or '>#PRESMERUJ' in line or '>#presmeruj' in line:
                mam_redirect = 1
                if pomocna == 1:
                    if '[[' in line and ']]' in line:        
                        odkaz = re.search(token, line).group(1)
                        if '#' in odkaz:
                            #odkaz na sekciu
                            title_sectioning = re.search('(.*)#', odkaz).group(1)
                            if title_sectioning == '':
                                title_sectioning = title
                            sectioning = re.search('#(.*)', odkaz).group(1)
                            redirect_na_sekciu_dict["type"] = "redirect"
                            redirect_na_sekciu_dict["title"] = title
                            redirect_na_sekciu_dict["section"] = sectioning
                            redirect_na_sekciu_dict["section_title"] = title_sectioning
                            counter += 1
                            yield{
                                "_index": "linkandredindex",
                                "_type": "_doc",
                                "_id": counter,
                                "_source" : redirect_na_sekciu_dict
                            }
            
            #RIEŠENIE ODKAZOV
            if '[[' in line and mam_redirect == 0:
                if riadok != '':
                    oddel = re.split('\[\[',riadok + line)
                    riadok = ''
                else:
                    oddel = re.split('\[\[',line)
                for x in oddel:
                    if ']]' in x:
                        oddel2 = re.split('\]\]',x)
                        odkaz_na_kat = oddel2[0]
                        if '#' in odkaz_na_kat:
                            title_odkaz = re.search('(.*)#',odkaz_na_kat).group(1)
                            if title_odkaz == '':
                                title_odkaz = title    
                            odkaz_na_kat = re.search('#(.*)',odkaz_na_kat).group(1)
                            if '#' not in odkaz_na_kat and '&quot' not in odkaz_na_kat and '&gt' not in odkaz_na_kat:
                                if '|' in odkaz_na_kat:
                                    odkaz_na_kat = re.search('(.*)\|',odkaz_na_kat).group(1)
                                link_na_sekciu_dict["type"] = "odkaz"
                                link_na_sekciu_dict["title"] = title
                                link_na_sekciu_dict["section"] = odkaz_na_kat
                                link_na_sekciu_dict["section_title"] = title_odkaz
                                counter += 1
                                yield{
                                    "_index": "linkandredindex",
                                    "_type": "_doc",
                                    "_id": counter,
                                    "_source" : link_na_sekciu_dict
                                }
                    else:
                        
                        # znamena ze dany link nema koncove ]], musim teda nadpojit string
                        if x == oddel[-1]:
                            riadok = x
            
            # EXTRAHOVANIE SAMOTNYCH SEKCII
            if line[0] == '=' and mam_redirect == 0:
                pomocnepocitadlo = 0
                for i in line:
                    if i == '=':
                        pomocnepocitadlo += 1
                    else:
                        continue
                pomocnepocitadlo /= 2

                # PREMENNA POMOCNE POCITADLO MI HOVORI O AKU UROVEN SEKCIE SA JEDNA. NA ZAKLADE TOHO POTOM SPRACUJEM SEKCIU
                if pomocnepocitadlo == 1:
                    if (re.search(sekcia_text_token_level1,line)) != None:
                        extrakcia_textu = 1
                        nazov_sekcie = re.search(sekcia_text_token_level1,line).group(1)
                        nazov_sekcie = nazov_sekcie.strip()
                        if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                            extrakcia_textu = 0
                            continue
                        else:
                            id_sekcie += 1
                            objekt = {}
                            section_dict["title"] = title
                            section_dict["section"] = []
                            objekt["level"] = 1
                            objekt["name"] = nazov_sekcie
                            section_dict["section"].append(objekt)
                elif pomocnepocitadlo == 2:
                    if (re.search(sekcia_text_token_level2,line)) != None:
                        extrakcia_textu = 1
                        nazov_sekcie = re.search(sekcia_text_token_level2,line).group(1)
                        nazov_sekcie = nazov_sekcie.strip()
                        if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                            extrakcia_textu = 0
                            continue
                        else:
                            id_sekcie += 1
                            objekt = {}
                            section_dict["title"] = title
                            section_dict["section"] = []
                            objekt["level"] = 2
                            objekt["name"] = nazov_sekcie
                            section_dict["section"].append(objekt)
                elif pomocnepocitadlo == 3:
                    if (re.search(sekcia_text_token_level3,line)) != None:
                        extrakcia_textu = 1
                        nazov_sekcie = re.search(sekcia_text_token_level3,line).group(1)
                        nazov_sekcie = nazov_sekcie.strip()
                        if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                            extrakcia_textu = 0
                            continue
                        else:
                            id_sekcie += 1
                            objekt = {}
                            section_dict["title"] = title
                            section_dict["section"] = []
                            objekt["level"] = 3
                            objekt["name"] = nazov_sekcie
                            section_dict["section"].append(objekt)
                elif pomocnepocitadlo == 4:
                    if (re.search(sekcia_text_token_level4,line)) != None:
                        extrakcia_textu = 1
                        nazov_sekcie = re.search(sekcia_text_token_level4,line).group(1)
                        nazov_sekcie = nazov_sekcie.strip()
                        if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                            extrakcia_textu = 0
                            continue
                        else:
                            id_sekcie += 1
                            objekt = {}
                            section_dict["title"] = title
                            section_dict["section"] = []
                            objekt["level"] = 4
                            objekt["name"] = nazov_sekcie
                            section_dict["section"].append(objekt)
                elif pomocnepocitadlo == 5:
                    if (re.search(sekcia_text_token_level5,line)) != None:
                        extrakcia_textu = 1
                        nazov_sekcie = re.search(sekcia_text_token_level5,line).group(1)
                        nazov_sekcie = nazov_sekcie.strip()
                        if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                            extrakcia_textu = 0
                            continue
                        else:
                            id_sekcie += 1
                            objekt = {}
                            section_dict["title"] = title
                            section_dict["section"] = []
                            objekt["level"] = 5
                            objekt["name"] = nazov_sekcie
                            section_dict["section"].append(objekt)
                elif pomocnepocitadlo == 6:
                    if (re.search(sekcia_text_token_level6,line)) != None:
                        extrakcia_textu = 1
                        nazov_sekcie = re.search(sekcia_text_token_level6,line).group(1)
                        nazov_sekcie = nazov_sekcie.strip()
                        if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                            extrakcia_textu = 0
                            continue
                        else:
                            id_sekcie += 1
                            objekt = {}
                            section_dict["title"] = title
                            section_dict["section"] = []
                            objekt["level"] = 6
                            objekt["name"] = nazov_sekcie
                            section_dict["section"].append(objekt)
                else:
                    continue

# TRY EXCEPT SKUSI INSERTNUT DATA A AK BY NIECO ZLYHALO, VYPISE SA CHYBA
try:
    helpers.bulk(es,import_sekcii())
except Exception as e:
    print("\nError: ",e)