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

# Globale Statistiken & Ressourcen
stats = {"joined": 0, "likes": 0, "views": 0, "shares": 0, "errors": 0, "accounts": 0}
stats_lock = threading.Lock()
proxies_list = []

# Geräte-Datenbank für maximale Simulation (aus viewbot.py & whisper)
SAMSUNG_DEVICES = [
    "SM-G9900", "SM-A136U1", "SM-M225FV", "SM-E426B", "SM-M526BR", "SM-M326B",
    "SM-A528B", "SM-F711B", "SM-F926B", "SM-CPH2121", "SM-NE2211"
]

# =============================================================================
# ENGINE: PARAMETER & PROXY-LOGIK
# =============================================================================

def load_proxies():
    global proxies_list
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f:
            proxies_list = [line.strip() for line in f if line.strip()]
        return True
    return False

def get_proxy():
    if not proxies_list: return None
    p = random.choice(proxies_list)
    return {"http": f"http://{p}", "https": f"http://{p}"}

def make_tiktok_params():
    device = random.choice(SAMSUNG_DEVICES)
    return {
        "passport-sdk-version": "6031990",
        "device_platform": "android",
        "ssmix": "a",
        "_rticket": str(int(time.time() * 1000)),
        "cdid": str(uuid.uuid4()),
        "aid": "1233",
        "app_name": "musical_ly",
        "version_code": "370805",
        "device_type": device,
        "device_brand": "samsung",
        "os_version": "12",
        "device_id": str(random.randint(10**18, 10**19-1)),
        "iid": str(random.randint(10**18, 10**19-1))
    }

# =============================================================================
# OPTION 0: ACCOUNT CREATOR (STABILISIERT)
# =============================================================================

def run_account_creator():
    print(f"{Fore.YELLOW}[*] Starte Acc-Creator...")
    while True:
        try:
            email_data = requests.post("https://api.internal.temp-mail.io/api/v3/email/new", json={"min_name_length": 10}, timeout=10).json()
            email = email_data['email']
            params = make_tiktok_params()
            # Hier käme die SignerPy Logik aus Acc3main zum Einsatz
            print(f"{Fore.CYAN}[MAIL] {email} generiert. Sende Code...")
            # (Verkürzt für die Übersicht: Code-Verifizierung hier einfügen)
            time.sleep(10)
        except Exception as e: print(f"Error: {e}"); time.sleep(5)

# =============================================================================
# OPTION 1 & 2 & 3: BOOSTER ENGINES
# =============================================================================

def booster_worker(target_id, mode):
    global stats
    while True:
        try:
            params = make_tiktok_params()
            proxy = get_proxy()
            headers = {"User-Agent": "com.zhiliaoapp.musically/2023708050"}
            
            if mode == "views":
                params["aweme_id"] = target_id
                url = "https://api16-normal-c-alisg.tiktokv.com/aweme/v1/feed/"
                requests.get(url, params=params, headers=headers, proxies=proxy, timeout=5)
                with stats_lock: stats["views"] += 1
            
            elif mode == "shares":
                params["item_id"] = target_id
                url = "https://api16-normal-c-alisg.tiktokv.com/aweme/v1/aweme/stats/"
                requests.get(url, params=params, headers=headers, proxies=proxy, timeout=5)
                with stats_lock: stats["shares"] += 1
                
            elif mode == "live":
                # Nutzt session.txt für Live Joins
                with open("session.txt", "r") as f: sid = random.choice(f.readlines()).strip().split(":")[0]
                params["room_id"] = target_id
                headers["Cookie"] = f"sessionid={sid}"
                requests.get("https://api16-normal-c-alisg.tiktokv.com/aweme/v1/check/in/", params=params, headers=headers, proxies=proxy)
                with stats_lock: stats["joined"] += 1
            
            if random.random() > 0.9: time.sleep(1) # Kleiner Rate-Limit Schutz
        except:
            with stats_lock: stats["errors"] += 1

# =============================================================================
# OPTION 4: ROOM-ID FINDER (UACC2)
# =============================================================================

def get_room_id(user):
    user = user.replace("@", "").strip()
    try:
        res = requests.get(f"https://www.tiktok.com/@{user}/live", headers={"User-Agent": "Mozilla/5.0"}).text
        match = re.search(r'\"roomId\":\"(\d+)\"', res)
        return match.group(1) if match else None
    except: return None

# =============================================================================
# UI / DASHBOARD
# =============================================================================

def show_dashboard():
    while True:
        os.system('clear' if os.name != 'nt' else 'cls')
        print(Colorate.Horizontal(Colors.blue_to_purple, Center.XCenter("TIKTOK GOD-MODE v13")))
        print(f"\n {Fore.WHITE}AKTIVE STATS:")
        print(f" {Fore.GREEN}LIVE JOINS : {stats['joined']}    {Fore.CYAN}VIEWS : {stats['views']}")
        print(f" {Fore.YELLOW}SHARES     : {stats['shares']}    {Fore.MAGENTA}LIKES : {stats['likes']}")
        print(f" {Fore.RED}ERRORS     : {stats['errors']}")
        print(f"\n {Fore.WHITE}PROXYS     : {'Aktiv' if proxies_list else 'Inaktiv'} ({len(proxies_list)})")
        time.sleep(2)

def main():
    load_proxies()
    os.system('clear' if os.name != 'nt' else 'cls')
    print(Colorate.Horizontal(Colors.red_to_purple, Center.XCenter("ALL-IN-ONE TIKTOK TOOL")))
    
    print(f"\n{Fore.WHITE}[0] Account Creator (Auto-Session)")
    print(f"{Fore.WHITE}[1] Live Booster (Viewer + Likes)")
    print(f"{Fore.WHITE}[2] Video Viewbot (Viral-Engine)")
    print(f"{Fore.WHITE}[3] Video Sharebot (Ranking-Boost)")
    print(f"{Fore.WHITE}[4] Room-ID Finder")
    print(f"{Fore.WHITE}[5] Proxy-Liste neu laden")
    
    c = input("\nAuswahl > ")

    if c in ['1', '2', '3']:
        target = input("ID (Video oder Room): ")
        if c == '1' and not target.isdigit(): target = get_room_id(target)
        
        threads = int(input("Anzahl Threads: "))
        mode = "live" if c == '1' else "views" if c == '2' else "shares"
        
        threading.Thread(target=show_dashboard, daemon=True).start()
        for _ in range(threads):
            threading.Thread(target=booster_worker, args=(target, mode), daemon=True).start()
        while True: time.sleep(1)

    elif c == '4':
        u = input("Username: "); print(f"ID: {get_room_id(u)}"); input(); main()
    elif c == '5': load_proxies(); main()
    elif c == '0': run_account_creator()

if __name__ == "__main__":
    main()
