import sys
import re
import os
import urllib.request
import urllib.parse
import threading
from datetime import datetime
import argparse
import json
from html import unescape

try:
    from googlesearch import search
except ImportError:
    print("[!] Nessun modulo chiamato \"google\" trovato")
    print("    Perfavore installalo usando:")
    print("\n    python3 -m pip install google")
    exit()

    

GROUP_NAME_REGEX = re.compile(r'(og:title\" content=\")(.*?)(\")')
GROUP_IMAGE_REGEX = re.compile(r'(og:image\" content=\")(.*?)(\")')
lock = threading.Lock()

SAVE = "scrapped_%s.txt" % datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
availabledom = ["pastebin",
                "throwbin",
                "pastr",
                "pasteio",
                "paste2",
                "paste"]
site_urls = ["https://www.whatsapgrouplinks.com/",
             "https://whatsgrouplink.com/",
             "https://realgrouplinks.com/",
             "https://appgrouplink.com/",
             "https://whatsfunda.com/",
             "https://whatzgrouplink.com/latest-whatsapp-group-links/",
             "https://allinonetrickz.com/new-whatsapp-groups-invite-links/",
             "https://www.itgruppi.com/whatsapp"]


def linkcheck(url):
    print("\nProvando URL:", url, end='\r')
    group_info = {"name": None, "url": url, "image": None}
    try:
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        req = urllib.request.Request(url, headers=hdr)
        resp = urllib.request.urlopen(req)
    except Exception:
        return group_info
    if (resp.getcode() != 404):
        resp = resp.read().decode("utf-8")
        group_info["name"] = unescape(GROUP_NAME_REGEX.search(resp).group(2))
        group_info["image"] = unescape(GROUP_IMAGE_REGEX.search(resp).group(2))
    return group_info


def pad(s):
    if "invite" not in s:
        p = s.find(".com")
        s = s[:p + 4] + "/invite" + s[p + 4:]
    return s


def scrape(txt, download_image=False):
    if isinstance(txt, bytes):
        txt = txt.decode("utf-8")
    match = []
    match2 = re.findall(
        r"(https:\/\/chat\.whatsapp\.com\/(invite\/)?[a-zA-Z0-9]{22})", txt)
    match = [item[0] for item in match2]
    match = list(set(match))
    for lmt in match:
        lmt = pad(lmt)
        info = linkcheck(lmt)
        if info['name']:
            print("[i] Nome Gruppo:  ", info['name'])
            print("[i] Link Gruppo:  ", info['url'])
            print("[i] Immagine Gruppo: ", info['image'])
            lock.acquire()
            if SAVE.endswith(".json"):
                with open(SAVE, "r+", encoding='utf-8') as jsonFile:
                    data = json.load(jsonFile)
                    data.append(info)
                    jsonFile.seek(0)
                    json.dump(data, jsonFile)
                    jsonFile.truncate()
            else:
                with open(SAVE, "a", encoding='utf-8') as f:
                    write_data = " | ".join(info.values())+"\n"
                    f.write(write_data)
            if download_image:
                image_path = urllib.parse.urlparse(info['image'])
                path, _ = urllib.request.urlretrieve(
                    info["image"], os.path.basename(image_path.path))
                print("[i] Image Path: ", path)
            lock.release()


def scrap_from_google(index):
    print("[*] Inizializzando...")
    if index >= len(availabledom):
        return
    query = "intext:chat.whatsapp.com inurl:" + availabledom[index]
    print("[*] Querying Google By Dorks ...")
    for url in search(query, tld="com", num=10, stop=None, pause=2):
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        req = urllib.request.Request(url, headers=hdr)
        txt = urllib.request.urlopen(req).read().decode("utf8")
        scrape(txt)


def scrap_from_link(index):
    print("[*] Inizializzando...")
    if index >= len(site_urls):
        return
    r = urllib.request.urlopen(site_urls[index]).read().decode()
    scrape(r)


def update_tool():
    print("[*] Aggiornando...")
    try:
        txt = urllib.request.urlopen(
            "https://github.com/hopnetgalaxy/WhatsLink/raw/main/whatscraper.py").read()
        with open(sys.argv[0], "wb") as f:
            f.write(txt)
        print("[$] Aggiornamento eseguito con successo")
        print("[i] Avvia " + sys.argv[0] + " Ancora..")
    except Exception:
        print("[!] Aggiornamento Fallito !!!")
    sys.exit(0)


def initialize_google_scrapper():
    threads = []
    size = len(availabledom)
    prompt = "[#] Inserisci il numero di threads(1-" + str(size) + "):- "
    thread_count = min(size, int(input(prompt)))
    for i in range(thread_count):
        thread = threading.Thread(target=scrap_from_google, args=(i,))
        thread.start()
        threads.append(thread)
    for i in threads:
        i.join()


def initialize_site_scrapper():
    threads = []
    size = len(site_urls)
    prompt = "[#] Inserisci il numero di threads(1-" + str(size) + "):- "
    thread_count = min(size, int(input(prompt)))
    for i in range(thread_count):
        thread = threading.Thread(target=scrap_from_link, args=(i,))
        thread.start()
        threads.append(thread)

    for i in threads:
        i.join()


def initialize_file_scrapper():
    threads = []
    path = input("[#] Inserisci il percorso del file contenente i link: ").strip()
    if not os.path.isfile(path):
        print("\t[!] Nessun cazzo di file trovato...")
        exit()
    thn = int(input("[#] Inserisci il numero di threads: "))
    op = open(path, "rb").read().decode("utf-8")
    op = op.count('\n') // thn
    with open(path, "r", encoding='utf-8') as strm:
        for _ in range(thn - 1):
            head = [next(strm) for x in range(op)]
            thread = threading.Thread(
                target=scrape, args=(b'\n'.join(head),))
            thread.start()
            threads.append(thread)
        thread = threading.Thread(target=scrape, args=(strm.read(),))
        thread.start()
        threads.append(thread)
    for i in threads:
        i.join()


def main():
    global SAVE
    
    
    print(r"""\
#  **_****_************************_***********************************
#  *|*|**|*|**********************|*|**********************************
#  *|*|__|*|*___**_*__**_*__***___|*|_*********************************
#  *|**__**|/*_*\|*'_*\|*'_*\*/*_*|*__|********************************
#  *|*|**|*|*(_)*|*|_)*|*|*|*|**__|*|_*********************************
#  *|_|**|_|\___/|*.__/|_|*|_|\___|\__|********************************
#  **************|*|***************************************************
#  *__**********_|_|**********_********_____***************************
#  *\*\********/*|*|*********|*|******/*____|**************************
#  **\*\**/\**/*/|*|__***__*_|*|_*___|*|*****_*__*__*_*_*__***___*_*__*
#  ***\*\/**\/*/*|*'_*\*/*_`*|*__/*__|*|****|*'__/*_`*|*'_*\*/*_*|*'__|
#  ****\**/\**/**|*|*|*|*(_|*|*|_\__*|*|____|*|*|*(_|*|*|_)*|**__|*|***
#  *****\/**\/***|_|*|_|\__,_|\__|___/\_____|_|**\__,_|*.__/*\___|_|***
#  ***************************************************|*|**************
#  ***************************************************|_|**************
            """)

    print(r"""\


""")


    parser = argparse.ArgumentParser(description="Scrap Whatsapp Group Links")
    parser.add_argument("-j", "--json", action="store_true",
                        help="Returns a JSON file instead of a text")
    parser.add_argument("-l", "--link", action="store",
                        help="Shows Group Info from group link")
    parser.add_argument("-u", "--update", action="store_true",
                        help="Update WhatScrapper")
    args = parser.parse_args()
    if args.update:
        update_tool()
    if args.link:
        scrape(args.link, download_image=True)
        return
    if args.json:
        SAVE = SAVE.split(".")[0]+".json"
        with open(SAVE, "w", encoding='utf-8') as jsonFile:
            json.dump([], jsonFile)
    print("""
    1> Fotti Google
    2> Fotti da siti contenenti Link[MIGLIORE]
    3> Fotti da un file
    4> Aggiorna sto cazzo di tool
    """)

    try:
        inp = int(input("[#] SCEGLI: "))
    except Exception:
        print("\t[!] Sei scemo? Scelta non valida..")
        exit()

    if inp == 1:
        initialize_google_scrapper()
    elif inp == 2:
        initialize_site_scrapper()
    elif inp == 3:
        initialize_file_scrapper()
    elif inp == 4:
        update_tool()
    else:
        print("[!] Sei scemo? Scelta non valida..")


if __name__ == "__main__":
    main()
