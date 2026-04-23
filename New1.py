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

# Global Stats
stats = {"joined": 0, "likes": 0, "views": 0, "shares": 0, "errors": 0}
stats_lock = threading.Lock()
proxies_list = []

# =============================================================================
# GERÄTE-DATABASE (Aus viewbot.py übernommen)
# =============================================================================
SAMSUNG_DEVICES = [
    "SM-G9900","SM-A136U1", "SM-M225FV", "SM-E426B", "SM-M526BR", "SM-M326B",
    "SM-A528B","SM-F711B","SM-F926B","SM-A037G","SM-A225F","SM-M325FV",
    "SM-A226B","SM-M426B","SM-A525F","SM-N976N","SM-M526B","SM-A520F"
]

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
        "device_id": str(random.randint(7000000000000000000, 7999999999999999999)),
        "iid": str(random.randint(7000000000000000000, 7999999999999999999))
    }

# =============================================================================
# PROXY-LOADER (Aus viewbot.py Logik)
# =============================================================================
def load_proxies():
    global proxies_list
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f:
            proxies_list = [line.strip() for line in f if line.strip()]
        print(f"{Fore.GREEN}[+] {len(proxies_list)} Proxys geladen.")
    else:
        print(f"{Fore.YELLOW}[!] Keine proxies.txt gefunden. Nutze eigene IP.")

def get_proxy():
    if not proxies_list:
        return None
    p = random.choice(proxies_list)
    return {"http": f"http://{p}", "https": f"http://{p}"}

# =============================================================================
# WORKER FUNKTIONEN (Views, Shares, Live)
# =============================================================================

def video_worker(video_id, mode):
    """Mode 1: Views, Mode 2: Shares"""
    global stats
    while True:
        try:
            params = make_tiktok_params()
            proxy = get_proxy()
            headers = {"User-Agent": "com.zhiliaoapp.musically/2023708050"}
            
            if mode == "views":
                params["aweme_id"] = video_id
                url = "https://api16-normal-c-alisg.tiktokv.com/aweme/v1/feed/"
            else:
                params["item_id"] = video_id
                url = "https://api16-normal-c-alisg.tiktokv.com/aweme/v1/aweme/stats/"

            r = requests.get(url, params=params, headers=headers, proxies=proxy, timeout=5)
            
            with stats_lock:
                if r.status_code == 200:
                    if mode == "views": stats["views"] += 1
                    else: stats["shares"] += 1
                else:
                    stats["errors"] += 1
        except:
            with stats_lock: stats["errors"] += 1

# =============================================================================
# UI & DASHBOARD
# =============================================================================

def dashboard():
    while True:
        os.system('clear' if os.name != 'nt' else 'cls')
        print(Colorate.Horizontal(Colors.blue_to_purple, Center.XCenter("TIKTOK ULTIMATE DASHBOARD v12")))
        print(f"\n {Fore.CYAN}VIDEO VIEWS : {stats['views']}")
        print(f" {Fore.YELLOW}VIDEO SHARES: {stats['shares']}")
        print(f" {Fore.MAGENTA}LIVE JOINS  : {stats['joined']}")
        print(f" {Fore.RED}ERRORS      : {stats['errors']}")
        print(f"\n {Fore.WHITE}Proxys aktiv: {len(proxies_list) > 0}")
        print(f" {Fore.WHITE}Beenden mit STRG+C")
        time.sleep(2)

# =============================================================================
# MAIN
# =============================================================================

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    load_proxies()
    
    print(f"\n{Fore.WHITE}[0] Account Creator")
    print(f"{Fore.CYAN}[1] Live Booster (Viewer/Likes)")
    print(f"{Fore.CYAN}[2] Video Viewbot")
    print(f"{Fore.CYAN}[3] Video Sharebot")
    print(f"{Fore.GREEN}[4] Proxys neu laden")
    
    choice = input("\nAuswahl > ")

    if choice in ['2', '3']:
        v_id = input("Video ID: ")
        num_threads = int(input("Threads (z.B. 100): "))
        mode = "views" if choice == '2' else "shares"
        
        threading.Thread(target=dashboard, daemon=True).start()
        for _ in range(num_threads):
            threading.Thread(target=video_worker, args=(v_id, mode), daemon=True).start()
        
        while True: time.sleep(1)

    elif choice == '4':
        load_proxies()
        main()

if __name__ == "__main__":
    main()
