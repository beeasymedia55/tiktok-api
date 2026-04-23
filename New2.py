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

# Webcast Domains für stabilen Room-Join
WEBCAST_DOMAINS = [
    "https://webcast16-normal-c-alisg.tiktokv.com",
    "https://webcast16-normal-useast2a.tiktokv.com"
]

# Samsung Geräte-Liste für Simulation
SAMSUNG_DEVICES = ["SM-G9900", "SM-A528B", "SM-F711B", "SM-F926B", "SM-N976N", "SM-A525F"]

# =============================================================================
# HILFSFUNKTIONEN & PARAMETER
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

def make_tiktok_params(aid="1233"):
    device = random.choice(SAMSUNG_DEVICES)
    return {
        "passport-sdk-version": "6031990",
        "device_platform": "android",
        "ssmix": "a",
        "_rticket": str(int(time.time() * 1000)),
        "cdid": str(uuid.uuid4()),
        "aid": aid,
        "device_type": device,
        "device_brand": "samsung",
        "os_version": "12",
        "device_id": str(random.randint(10**18, 10**19-1)),
        "iid": str(random.randint(10**18, 10**19-1))
    }

# =============================================================================
# WEBCAST ROOM JOIN ENGINE
# =============================================================================

def enter_live_room(sid, room_id, proxy):
    domain = random.choice(WEBCAST_DOMAINS)
    url = f"{domain}/webcast/room/enter/"
    
    params = make_tiktok_params(aid="1988") # Webcast App ID
    params.update({"room_id": room_id, "scene": "live_room"})
    
    headers = {
        "Cookie": f"sessionid={sid}",
        "User-Agent": "com.zhiliaoapp.musically/2023708050"
    }
    
    payload = f"room_id={room_id}"
    sig = SignerPy.sign(params=params, payload=payload)
    headers.update({"X-Gorgon": sig.get("x-gorgon"), "X-Khronos": sig.get("x-khronos")})

    try:
        r = requests.post(url, params=params, data=payload, headers=headers, proxies=proxy, timeout=10)
        return r.status_code == 200 and r.json().get("status_code") == 0
    except:
        return False

def live_worker(sid, room_id):
    global stats
    
    # Zufälliger Delay beim Start (Spreader), damit nicht alle gleichzeitig joinen
    time.sleep(random.uniform(0.5, 15.0))
    
    proxy = get_proxy()
    
    # 1. Room Enter
    if enter_live_room(sid, room_id, proxy):
        with stats_lock: stats["joined"] += 1
        
        # 2. Keep-Alive Loop (Ping)
        domain = random.choice(WEBCAST_DOMAINS)
        while True:
            try:
                params = make_tiktok_params(aid="1988")
                params["room_id"] = room_id
                headers = {"Cookie": f"sessionid={sid}", "User-Agent": "com.zhiliaoapp.musically/2023708050"}
                
                # Sende Ping um Zuschauer-Status zu halten
                requests.get(f"{domain}/webcast/room/ping/", params=params, headers=headers, proxies=proxy, timeout=7)
                
                # Zufällige Likes (Interaktion)
                if random.random() > 0.8:
                    requests.post(f"{domain}/webcast/stats/heart/", params=params, headers=headers, proxies=proxy)
                    with stats_lock: stats["likes"] += 1
                
                # Wartezeit zwischen Pings (TikTok Standard)
                time.sleep(random.randint(15, 25))
            except:
                with stats_lock: stats["errors"] += 1
                break
    else:
        with stats_lock: stats["errors"] += 1

# =============================================================================
# DASHBOARD & MAIN
# =============================================================================

def dashboard():
    while True:
        os.system('clear' if os.name != 'nt' else 'cls')
        print(Colorate.Horizontal(Colors.blue_to_purple, Center.XCenter("TIKTOK OVERLORD v14")))
        print(f"\n {Fore.GREEN}LIVE VIEWERS: {stats['joined']} | {Fore.MAGENTA}LIKES: {stats['likes']}")
        print(f" {Fore.RED}ERRORS: {stats['errors']}")
        print(f"\n {Fore.WHITE}PROXYS: {'AN' if use_proxies else 'AUS'} | THREADS AKTIV: {threading.active_count()-2}")
        time.sleep(2)

def main():
    global use_proxies
    os.system('clear' if os.name != 'nt' else 'cls')
    
    load_proxies()
    print(f"{Fore.CYAN}[?] Proxys benutzen? (y/n): ", end="")
    use_proxies = input().lower() == 'y'
    
    print(f"\n{Fore.WHITE}[1] Live Booster (Webcast Engine)")
    print(f"{Fore.WHITE}[2] Video Viewbot")
    print(f"{Fore.WHITE}[3] Account Creator")
    
    choice = input("\nAuswahl > ")

    if choice == '1':
        room_id = input("Room-ID: ")
        try:
            with open("session.txt", "r") as f:
                # Format in session.txt -> sessionid:token
                sessions = [l.strip().split(":")[0] for l in f if l.strip()]
            
            print(f"Starte {len(sessions)} Viewer Threads mit Random-Delay...")
            threading.Thread(target=dashboard, daemon=True).start()
            
            for sid in sessions:
                threading.Thread(target=live_worker, args=(sid, room_id), daemon=True).start()
            
            while True: time.sleep(1)
        except FileNotFoundError:
            print("session.txt nicht gefunden!")

if __name__ == "__main__":
    main()
