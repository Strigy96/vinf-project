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

with open('data/skwiki-latest-pages-articles.xml', encoding='utf-8') as file:
    for line in file:
        if '<title>' in line:
            title = re.search('<title>(.*)</title>', line)
            title = title.group(1)
        if '<text' in line:
            if '>#redirect' in line or '>#REDIRECT' in line or '>#PRESMERUJ' in line or '>#presmeruj' in line:        
                odkaz = re.search('\[\[(.*)\]\]', line).group(1)
                presmeruj.write((title + ' - ' + odkaz + '\n'))
            elif '[[' in line:
                odkaz = re.search('\[\[(.*)\]\]', line).group(1)
                link.write((odkaz + '\n'))

presmeruj.close()        