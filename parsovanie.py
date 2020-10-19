import os.path
import re

if os.path.isfile('data/presmeruj.txt'):
    os.remove("data/presmeruj.txt")
    presmeruj = open("data/presmeruj.txt","w+",encoding='utf-8')
else:
    presmeruj = open("data/presmeruj.txt","w+",encoding='utf-8')

if os.path.isfile('data/link.txt'):
    os.remove("data/link.txt")
    link = open("data/link.txt","w+",encoding='utf-8')
else:
    link = open("data/link.txt","w+",encoding='utf-8')

if os.path.isfile('data/sekcia.txt'):
    os.remove("data/sekcia.txt")
    sekcia = open("data/sekcia.txt","w+",encoding='utf-8')
else:
    sekcia = open("data/sekcia.txt","w+",encoding='utf-8')

pomocna = 0
with open('data/skwiki-latest-pages-articles.xml', encoding='utf-8') as file:
    for line in file:
        if '<title>' in line:
            title = re.search('<title>(.*)</title>', line)
            title = title.group(1)
        if pomocna == 1:
            link.write((line + '\n'))
        if '</text' in line:
            pomocna = 0
        if '<text' in line:
            link.write((line + '\n'))
            pomocna = 1
            if '>#redirect' in line or '>#REDIRECT' in line or '>#PRESMERUJ' in line or '>#presmeruj' in line:        
                odkaz = re.search('\[\[(.*)\]\]', line).group(1)
                if '#' in odkaz:
                    #odkaz na sekciu
                    section = re.search('#(.*)', odkaz).group(1)
                    sekcia.write((title + ' - ' + section + '\n'))
                else:
                    presmeruj.write((title + ' - ' + odkaz + '\n'))

presmeruj.close()        