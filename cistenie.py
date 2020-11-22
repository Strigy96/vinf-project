import os.path

def create_or_clear_link_na_sekciu():
    if os.path.isfile('data/link_na_sekciu.txt'):
        os.remove("data/link_na_sekciu.txt")
        link_na_sekciu = open("data/link_na_sekciu.txt","w+",encoding='utf-8')
    else:
        link_na_sekciu = open("data/link_na_sekciu.txt","w+",encoding='utf-8')
    return link_na_sekciu

def create_or_clear_redirect_na_sekciu(): 
    if os.path.isfile('data/redirect_na_sekciu.txt'):
        os.remove("data/redirect_na_sekciu.txt")
        redirect_na_sekciu = open("data/redirect_na_sekciu.txt","w+",encoding='utf-8')
    else:
        redirect_na_sekciu = open("data/redirect_na_sekciu.txt","w+",encoding='utf-8')
    return redirect_na_sekciu

def create_or_clear_sekcia_text():
    if os.path.isfile('data/sekcia_text.txt'):
        os.remove("data/sekcia_text.txt")
        sekcia_text = open("data/sekcia_text.txt","w+",encoding='utf-8')
    else:
        sekcia_text = open("data/sekcia_text.txt","w+",encoding='utf-8')
    return sekcia_text

def create_or_clear_vsetky_sekcie():
    if os.path.isfile('data/vsetky_sekcie.txt'):
        os.remove("data/vsetky_sekcie.txt")
        vsetky_sekcie = open("data/vsetky_sekcie.txt","w+",encoding='utf-8')
    else:
        vsetky_sekcie = open("data/vsetky_sekcie.txt","w+",encoding='utf-8')
    return vsetky_sekcie