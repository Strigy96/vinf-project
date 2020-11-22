import os.path
import re
import cistenie as ci

#FUNKCIA NA ODSTRÁNENIE PREFIXU Z REŤAZCA
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

#NA RYCHLEJSIE HLADANIE VYUZIVAM DICTIONARY
link_na_sekciu_dict = {}
redirect_na_sekciu_dict = {}

#ZADEFINOVANIE PREMENNYCH
riadok = ''
pomocna = 0
mam_redirect = 0
extrakcia_textu = 0
riadky_citacie = 0
token = '\[\[(.*)\]\]'

sekcia_text_token_level1 = '=(.*)='
sekcia_text_token_level2 = '==(.*)=='
sekcia_text_token_level3 = '===(.*)==='
sekcia_text_token_level4 = '====(.*)===='
sekcia_text_token_level5 = '=====(.*)====='
sekcia_text_token_level6 = '======(.*)======'

link_na_sekciu = ci.create_or_clear_link_na_sekciu()
redirect_na_sekciu = ci.create_or_clear_redirect_na_sekciu()
sekcia_text = ci.create_or_clear_sekcia_text()
vsetky_sekcie = ci.create_or_clear_vsetky_sekcie()

with open('data/skwiki-latest-pages-articles.xml', encoding='utf-8') as file:
    for line in file:
        mam_redirect = 0

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
            sekcia_text.write(upraveny_riadok)
        else:
            extrakcia_textu = 0

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
                        section = re.search('#(.*)', odkaz).group(1)
                        redirect_na_sekciu.write((title + '#&&#' + section + '\n'))
        
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
                        odkaz_na_kat = re.search('#(.*)',odkaz_na_kat).group(1)
                        if '#' not in odkaz_na_kat and '&quot' not in odkaz_na_kat and '&gt' not in odkaz_na_kat:
                            if '|' in odkaz_na_kat:
                                odkaz_na_kat = re.search('(.*)\|',odkaz_na_kat).group(1)
                            link_na_sekciu.write((title + '#&&#' + odkaz_na_kat + '\n'))
                            link_na_sekciu_dict[title] = odkaz_na_kat
                else:
                    
                    #znamena ze dany link nema koncove ]], musim teda nadpojit string
                    if x == oddel[-1]:
                        riadok = x
        
        # EXTRAHOVANIE SAMOTNYCH KATEGORII
        if line[0] == '=' and mam_redirect == 0:
            pomocnepocitadlo = 0
            for i in line:
                if i == '=':
                    pomocnepocitadlo += 1
                else:
                    continue
            pomocnepocitadlo /= 2

            if pomocnepocitadlo == 1:
                if (re.search(sekcia_text_token_level1,line)) != None:
                    extrakcia_textu = 1
                    nazov_sekcie = re.search(sekcia_text_token_level1,line).group(1)
                    nazov_sekcie = nazov_sekcie.strip()
                    if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                        extrakcia_textu = 0
                        continue
                    else:
                        sekcia_text.write('Sekcia úrovne 1 v článku s názvom ' + title + ': ' + nazov_sekcie + '\n')
                        vsetky_sekcie.write(title + '#&&#' + nazov_sekcie + '\n')
            elif pomocnepocitadlo == 2:
                if (re.search(sekcia_text_token_level2,line)) != None:
                    extrakcia_textu = 1
                    nazov_sekcie = re.search(sekcia_text_token_level2,line).group(1)
                    nazov_sekcie = nazov_sekcie.strip()
                    if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                        extrakcia_textu = 0
                        continue
                    else:
                        sekcia_text.write('Sekcia úrovne 2 v článku s názvom ' + title + ': ' + nazov_sekcie + '\n')
                        vsetky_sekcie.write(title + '#&&#' + nazov_sekcie + '\n')
            elif pomocnepocitadlo == 3:
                if (re.search(sekcia_text_token_level3,line)) != None:
                    extrakcia_textu = 1
                    nazov_sekcie = re.search(sekcia_text_token_level3,line).group(1)
                    nazov_sekcie = nazov_sekcie.strip()
                    if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                        extrakcia_textu = 0
                        continue
                    else:
                        sekcia_text.write('Sekcia úrovne 3 v článku s názvom ' + title + ': ' + nazov_sekcie + '\n')
                        vsetky_sekcie.write(title + '#&&#' + nazov_sekcie + '\n')
            elif pomocnepocitadlo == 4:
                if (re.search(sekcia_text_token_level4,line)) != None:
                    extrakcia_textu = 1
                    nazov_sekcie = re.search(sekcia_text_token_level4,line).group(1)
                    nazov_sekcie = nazov_sekcie.strip()
                    if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                        extrakcia_textu = 0
                        continue
                    else:
                        sekcia_text.write('Sekcia úrovne 4 v článku s názvom ' + title + ': ' + nazov_sekcie + '\n')
                        vsetky_sekcie.write(title + '#&&#' + nazov_sekcie + '\n')
            elif pomocnepocitadlo == 5:
                if (re.search(sekcia_text_token_level5,line)) != None:
                    extrakcia_textu = 1
                    nazov_sekcie = re.search(sekcia_text_token_level5,line).group(1)
                    nazov_sekcie = nazov_sekcie.strip()
                    if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                        extrakcia_textu = 0
                        continue
                    else:
                        sekcia_text.write('Sekcia úrovne 5 v článku s názvom ' + title + ': ' + nazov_sekcie + '\n')
                        vsetky_sekcie.write(title + '#&&#' + nazov_sekcie + '\n')
            elif pomocnepocitadlo == 6:
                if (re.search(sekcia_text_token_level6,line)) != None:
                    extrakcia_textu = 1
                    nazov_sekcie = re.search(sekcia_text_token_level6,line).group(1)
                    nazov_sekcie = nazov_sekcie.strip()
                    if nazov_sekcie == 'Referencie' or nazov_sekcie == 'Pozri aj' or nazov_sekcie == 'Iné projekty' or nazov_sekcie == 'Externé odkazy':
                        extrakcia_textu = 0
                        continue
                    else:
                        sekcia_text.write('Sekcia úrovne 6 v článku s názvom ' + title + ': ' + nazov_sekcie + '\n')
                        vsetky_sekcie.write(title + '#&&#' + nazov_sekcie + '\n')
            else:
                continue

link_na_sekciu.close()
sekcia_text.close()
redirect_na_sekciu.close()
vsetky_sekcie.close()
#print("Zadaj sekciu, ktorú chceš vyhľadať: ")
#input1 = input()

print('\ndone\n')