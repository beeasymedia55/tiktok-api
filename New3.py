import requests
import re
import time
import random
import string
import os
import threading
import sys
import uuid
import SignerPy
from pystyle import Colors, Colorate, Center
from colorama import Fore, init

init(autoreset=True)

# Globale Statistiken
stats = {"joined": 0, "likes": 0, "views": 0, "shares": 0, "errors": 0}
stats_lock = threading.Lock()
proxies_list = []
use_proxies = False

# Webcast & API Domains
WEBCAST_DOMAINS = [
    "https://webcast16-normal-c-alisg.tiktokv.com",
    "https://webcast16-normal-useast2a.tiktokv.com"
]

SAMSUNG_DEVICES = ["SM-G9900", "SM-A528B", "SM-F711B", "SM-F926B", "SM-N976N", "SM-A525F"]

# =============================================================================
# ENGINE: FIX FÜR KEYERROR 'version_name'
# =============================================================================

def make_tiktok_params(aid="1233"):
    device = random.choice(SAMSUNG_DEVICES)
    return {
        "passport-sdk-version": "6031990",
        "device_platform": "android",
        "os": "android",
        "ssmix": "a",
        "_rticket": str(int(time.time() * 1000)),
        "cdid": str(uuid.uuid4()),
        "aid": aid,
        "app_name": "musical_ly",
        "version_code": "370805",
        "version_name": "37.8.5",      # Fix: Wichtig für SignerPy
        "manifest_version_code": "370805",
        "update_version_code": "370805",
        "device_brand": "samsung",
        "device_type": device,
        "os_version": "12",
        "device_id": str(random.randint(7000000000000000000, 7999999999999999999)),
        "iid": str(random.randint(7000000000000000000, 7999999999999999999)),
        "resolution": "1080*1920",
        "dpi": "480"
    }

# =============================================================================
# PROXY & UTILS
# =============================================================================

def load_proxies():
    global proxies_list
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f:
            proxies_list = [line.strip() for line in f if line.strip()]
        return True
    return False

def get_proxy():
    if not use_proxies or not proxies_list: return None
    p = random.choice(proxies_list)
    return {"http": f"http://{p}", "https": f"http://{p}"}

def grab_room_id(username):
    username = username.replace("@", "").strip()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(f"https://www.tiktok.com/@{username}/live", headers=headers, timeout=10).text
        match = re.search(r'\"roomId\":\"(\d+)\"', res)
        if match:
            return match.group(1)
    except: pass
    return None

# =============================================================================
# LIVE STREAM LOGIK (WEBCAST)
# =============================================================================

def enter_live_room(sid, room_id, proxy):
    domain = random.choice(WEBCAST_DOMAINS)
    url = f"{domain}/webcast/room/enter/"
    params = make_tiktok_params(aid="1988")
    params.update({"room_id": room_id, "scene": "live_room"})
    
    headers = {"Cookie": f"sessionid={sid}", "User-Agent": "com.zhiliaoapp.musically/2023708050"}
    payload = {"room_id": str(room_id)} # Dictionary Payload für bessere Kompatibilität
    
    try:
        sig = SignerPy.sign(params=params, payload=payload)
        headers.update({"X-Gorgon": sig.get("x-gorgon"), "X-Khronos": sig.get("x-khronos")})
        r = requests.post(url, params=params, data=payload, headers=headers, proxies=proxy, timeout=10)
        return r.status_code == 200
    except: return False

def live_worker(sid, room_id):
    global stats
    time.sleep(random.uniform(0.5, 12.0)) # Random Spreader
    proxy = get_proxy()
    
    if enter_live_room(sid, room_id, proxy):
        with stats_lock: stats["joined"] += 1
        domain = random.choice(WEBCAST_DOMAINS)
        while True:
            try:
                params = make_tiktok_params(aid="1988")
                params["room_id"] = room_id
                headers = {"Cookie": f"sessionid={sid}", "User-Agent": "com.zhiliaoapp.musically/2023708050"}
                requests.get(f"{domain}/webcast/room/ping/", params=params, headers=headers, proxies=proxy, timeout=7)
                if random.random() > 0.8:
                    requests.post(f"{domain}/webcast/stats/heart/", params=params, headers=headers, proxies=proxy)
                    with stats_lock: stats["likes"] += 1
                time.sleep(random.randint(15, 25))
            except: break
    else:
        with stats_lock: stats["errors"] += 1

# =============================================================================
# DASHBOARD & MENU
# =============================================================================

def dashboard_thread():
    while True:
        os.system('clear' if os.name != 'nt' else 'cls')
        print(Colorate.Horizontal(Colors.blue_to_purple, Center.XCenter("TIKTOK OVERLORD v15")))
        print(f"\n {Fore.GREEN}LIVE VIEWERS: {stats['joined']} | {Fore.MAGENTA}LIKES: {stats['likes']}")
        print(f" {Fore.RED}ERRORS: {stats['errors']}")
        print(f"\n {Fore.WHITE}PROXYS: {'AN' if use_proxies else 'AUS'} | ACCOUNTS AKTIV: {threading.active_count()-2}")
        time.sleep(2)

def main():
    global use_proxies
    os.system('clear' if os.name != 'nt' else 'cls')
    load_proxies()
    
    print(Colorate.Horizontal(Colors.purple_to_red, Center.XCenter("ULTIMATE MENU")))
    print(f"\n[1] Live Booster (mit Room Grabber)")
    print(f"[2] Nur Room-ID finden")
    print(f"[3] Account Creator")
    print(f"[E] Exit")
    
    choice = input("\nAuswahl > ")

    if choice == '1':
        target = input("Username (@user) oder Room-ID: ")
        if not target.isdigit():
            print(f"{Fore.YELLOW}[*] Suche Room-ID für {target}...")
            target = grab_room_id(target)
        
        if not target:
            print(f"{Fore.RED}[!] Room-ID nicht gefunden! Ist der User live?"); time.sleep(2); main()
        
        use_proxies = input(f"{Fore.CYAN}[?] Proxys benutzen? (y/n): ").lower() == 'y'
        
        try:
            with open("session.txt", "r") as f:
                sessions = [l.strip().split(":")[0] for l in f if l.strip()]
            
            threading.Thread(target=dashboard_thread, daemon=True).start()
            for sid in sessions:
                threading.Thread(target=live_worker, args=(sid, target), daemon=True).start()
            
            while True: time.sleep(1)
        except FileNotFoundError:
            print(f"{Fore.RED}[!] session.txt fehlt!"); time.sleep(2); main()

    elif choice == '2':
        u = input("Username: ")
        rid = grab_room_id(u)
        print(f"{Fore.GREEN}[+] Room-ID: {rid if rid else 'Nicht gefunden'}")
        input("\nEnter drücken..."); main()

if __name__ == "__main__":
    main()
