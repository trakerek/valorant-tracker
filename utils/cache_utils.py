import time
import json
import os
import requests as rq


cache = {}


CACHE_FILE = "cache.json"
CACHE_TTL = 300

# wczytaj cache przy starcie
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        try:
            cache = json.load(f)
        except:
            cache = {}
else:
    cache = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

def cached_request(url, headers=None):
    now = time.time()
    
    # sprawdź czy w cache
    if url in cache and (now - cache[url]["time"]) < CACHE_TTL:
        print("✅ Cache hit:", url)
        return cache[url]["data"]
    
    # jak nie ma w cache -> normalny request
    r = rq.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        cache[url] = {"data": data, "time": now}
        save_cache()
        return data
    else:
        r.raise_for_status()
