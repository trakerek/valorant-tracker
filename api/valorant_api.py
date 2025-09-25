# api/valorant_api.py
import os , sys
import pathlib
import math
import json
from urllib.parse import quote
from dotenv import load_dotenv
import requests as rq
import customtkinter as ctk
import tkinter as tk

from utils.cache_utils import cached_request, save_cache
from utils.image_utils import get_valo_char, get_image, set_agent_with_bg, get_map_icon

if getattr(sys, 'frozen', False):  
    BASE_DIR = os.path.dirname(sys.executable)
else:  
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

hen = os.getenv("hen")


def fetch_func_duofunkcja(name,tag):
    from ui.app_ui import duofunkcja
    duofunkcja(name,tag)
# def fetch_func_fetch_data(name,tag):
#     from ui.app_ui import fetch_data
#     fetch_data(name,tag)

def fetch_elem(lframe,rframe,mframe,banerr,ennick,entag):
    global left_frame,right_frame,frame,baner,entry_nick,entry_tag
    left_frame = lframe
    right_frame = rframe
    frame = mframe
    baner = banerr
    entry_nick = ennick
    entry_tag = entag


def show_error(msg, duration=3000):
    error_label = ctk.CTkLabel(baner,text=msg,text_color="red",wraplength=300)
    error_label.place(relx=0.2, rely=0.1, anchor="n")
    error_label.after(duration, error_label.destroy)

def prof(name,tag):
    if not name or not tag:
        return None
    headers = {
        "Authorization": hen
    }

    url = f"https://api.henrikdev.xyz/valorant/v1/account/{quote(name)}/{tag}"
    try:
        data = cached_request(url, headers=headers)
    except Exception as e:
        raise RuntimeError(f"Błąd pobierania statystyk: {e}")
    if data is not None:
        reg= data["data"]["region"]
        img = data["data"]["card"]["wide"]
        return reg, name, tag,img
    else:
        return None

def get_stats(inpname,inptag):

    prof_data = prof(inpname,inptag)
    if not prof_data:
        return "Bład nie znaleziono gracza"
    
    region,name,tag,_ = prof_data
    url= f"https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{name}/{tag}"

    headers = {
        "Authorization": hen
    }

    try:
        data = cached_request(url, headers=headers)
    except Exception as e:
        raise RuntimeError(f"Błąd pobierania statystyk: {e}")
        return
    if not data or "data" not in data:
        return None

    if data is not None:
        ranga = data["data"]["current_data"]["currenttierpatched"]
        mmr = data["data"]["current_data"]["elo"]
        ranga_img = data["data"]["current_data"]["images"]["large"]
        by_season = data["data"]["by_season"]


    seasons = list(by_season.keys())
    num_of_games = None
    num_of_wins = None
    if seasons:
        for s in reversed(seasons):  # od najnowszego
            sdata = by_season.get(s, {}) or {}
            num_of_games = sdata.get("number_of_games")
            num_of_wins = sdata.get("wins")
            # jeśli znalazłeś liczbę gier (może być 0) — przerwij i obsłuż potem
            if num_of_games is not None:
                break

    win_ratio = None
    try:
        if num_of_games and num_of_games > 0 and num_of_wins is not None:
            win_ratio = math.floor(num_of_wins / num_of_games * 100)
        else:
            # brak danych lub zero gier -> win_ratio pozostaje None
            print(f"Brak/zerowa liczba gier dla {name}#{tag} sezon: {seasons[-1] if seasons else 'brak'}")
    except Exception as e:
        win_ratio = None
        raise RuntimeError(f"Błąd pobierania statystyk: {e}")


    # try:
    #     with open('stats.json','w',encoding='utf-8') as f:
    #         json.dump(data, f, ensure_ascii=False, indent=4)
    # except Exception as e:
    #     raise RuntimeError(f"Błąd pobierania statystyk: {e}")
        
    return ranga,mmr,win_ratio,ranga_img

def get_kda(inpname,inptag):
    for w in left_frame.winfo_children():
        w.destroy()
    prof_data = prof(inpname,inptag)
    if not prof_data:
        return "Bład nie znaleziono gracza"
    
    region,name,tag,_ = prof_data
    url = f"https://api.henrikdev.xyz/valorant/v1/stored-matches/{region}/{quote(name)}/{tag}"
    headers = {
        "Authorization": hen
    }
    try:
        data = cached_request(url, headers=headers)
    except Exception as e:
        raise RuntimeError(f"Błąd pobierania statystyk: {e}")

    kills = 0
    deaths = 0
    assists = 0
    played_agent = []
    licznik = {}
    for match in data["data"]:
            kills += match["stats"]["kills"]
            deaths += match["stats"]["deaths"]
            assists += match["stats"]["assists"]
            played_agent.append(match["stats"]["character"]["name"])
    for agent in played_agent:
        if agent in licznik:
            licznik[agent] += 1
        else:
            licznik[agent] = 1
        
    most_played_agent = max(licznik, key=licznik.get)
    kd = round(kills/deaths,2) if deaths else kills
    kda = round((kills+assists)/max(1,deaths),2)
    return kills,deaths,assists,kd,kda,most_played_agent

def pokaz_szczegoly(match_id, nick, tag, region):
    global right_frame, frame, left_frame, entry_nick, entry_tag, baner
    if right_frame is not None:
        right_frame.destroy()
    right_frame = ctk.CTkFrame(frame, fg_color="rosybrown2")
    right_frame.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=5, pady=10)

    for w in left_frame.winfo_children():
        w.destroy()

    # scroll
    right_frame2 = ctk.CTkScrollableFrame(right_frame, fg_color="rosybrown2")
    right_frame2.pack(padx=10, pady=10, fill="both", expand=True)

    # pobierz dane meczu
    url = f"https://api.henrikdev.xyz/valorant/v2/match/{match_id}"
    headers = {"Authorization": hen}
    try:
        data = cached_request(url, headers=headers)
    except Exception as e:
        raise RuntimeError(f"Błąd pobierania statystyk: {e}")

    # pobierz dane gracza i mapy
    # staty = {}
    agent_img_url = None
    for gracz in data["data"]["players"]["all_players"]:
        if gracz["name"].lower() == nick.lower() and gracz["tag"].lower() == tag.lower():
            staty = gracz["stats"]
            agent_img_url = gracz["assets"]["agent"]["full"]
            break

    mapa = data["data"]["metadata"]["map"]
    tryb = data["data"]["metadata"]["mode"]
    url = f"https://api.henrikdev.xyz/valorant/v1/stored-matches/{region}/{quote(nick)}/{tag}"
    headers = {
        "Authorization": hen
    }
    r= rq.get(url,headers=headers)
    r.raise_for_status()
    if r.status_code == 200:
        data2=r.json()

    for match in data2["data"]:
        if match["meta"]["id"] == match_id:
            mapa_img = match["meta"]["map"]["id"]
            agent_url = match["stats"]["character"]["id"]
            break
    _,bg_img_url = get_valo_char(agent_url)



    top_frame = ctk.CTkFrame(right_frame2, fg_color="transparent")
    top_frame.pack(fill="x", pady=10)
    top_frame2 = ctk.CTkFrame(right_frame2, fg_color="transparent")
    top_frame2.pack(fill="x")

    set_agent_with_bg(left_frame, bg_img_url, agent_img_url,
                 bg_size=(300,300), agent_size=(300,300),
                 agent_offset=(20, "center"))
    powrot = ctk.CTkButton(left_frame,text="Powrot",fg_color="brown1",hover_color="#851629",border_color="black",border_width=2,command=lambda name=nick,tagg=tag: fetch_func_duofunkcja(name,tagg))
    powrot.place(anchor="n",relx=0.7,rely=0.02)

    icon = get_map_icon(mapa_img)
    map_label = ctk.CTkLabel(top_frame,text="")
    get_image(icon,600,150,map_label)
    map_label.pack(pady=(0,10))


    podmap_label = ctk.CTkLabel(top_frame2, text=f"Mapa: {mapa}\nTryb: {tryb}", font=("Segoe UI", 16),text_color="gray2")
    podmap_label.pack(side="left", padx=60)

    if staty:
        staty_text = "\n".join([f"{k.capitalize()}: {v}" for k, v in staty.items()])
        staty_label = ctk.CTkLabel(top_frame2, text=staty_text, font=("Segoe UI", 14),text_color="gray2", justify="left")
        staty_label.pack(side="left",padx=50)
    
    wynik_text = "\n".join([f"{team}: {val['rounds_won']}" for team, val in data["data"]["teams"].items()])
    wynik_label = ctk.CTkLabel(top_frame2, text=wynik_text, font=("Segoe UI", 16),text_color="gray2")
    wynik_label.pack(side="right", padx=10)

    # --- drużyny ---
    teams_frame = ctk.CTkFrame(right_frame2, fg_color="transparent")
    teams_frame.pack(fill="both", expand=True, pady=10)

    red_team_frame = ctk.CTkFrame(teams_frame, fg_color="red2", corner_radius=12)
    red_team_frame.pack(side="left", expand=True, fill="both", padx=5)

    blue_team_frame = ctk.CTkFrame(teams_frame, fg_color="deepskyblue3", corner_radius=12)
    blue_team_frame.pack(side="right", expand=True, fill="both", padx=5)

    players = data["data"]["players"]["all_players"]
    for p in players:
        team = p.get("team", "").lower()
        display_name = f"{p.get('name','')}#{p.get('tag','')}"
        name =p.get('name') or ""
        tag = p.get('tag') or ""
        stats = p.get("stats", {})
        kda_text = f"{stats.get('kills',0)}/{stats.get('deaths',0)}/{stats.get('assists',0)}"
        icon_url = p.get("assets", {}).get("agent", {}).get("small")

        target_frame = red_team_frame if team == "red" else blue_team_frame
        row = ctk.CTkFrame(target_frame, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=3)

        icon_lbl = ctk.CTkLabel(row, text="", width=36, height=36)
        icon_lbl.pack(side="left", padx=4)
        if icon_url:
            try:
                get_image(icon_url, 36, 36, icon_lbl)
            except Exception as e:
                raise RuntimeError(f"Błąd pobierania statystyk: {e}")

        def on_player_click(n=name, t=tag):
            if not n or not t:
                show_error(f"Tag dla gracza '{n}' nie jest dostępny.", duration=4000)
                return
            fetch_func_duofunkcja(n, t)

        text_lbl = ctk.CTkButton(row, text=f"{display_name}\n{kda_text}", anchor="w", fg_color="transparent", hover_color="mediumorchid3",command=lambda n=name, t=tag:fetch_func_duofunkcja(n,t))
        text_lbl.pack(side="left", padx=6)
    
    
def lista_meczy(inpname,inptag):
    global right_frame, loader
    if right_frame is not None:
        right_frame.destroy()
    right_frame = ctk.CTkScrollableFrame(frame, fg_color="rosybrown2")
    right_frame.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=5, pady=10)

    for w in right_frame.winfo_children():
        w.destroy()
    prof_data = prof(inpname,inptag)
    if not prof_data:
        return "Bład nie znaleziono gracza"
    
    
    region,name,tag,_ = prof_data
    url = f"https://api.henrikdev.xyz/valorant/v1/stored-matches/{region}/{quote(name)}/{tag}"
    headers = {
        "Authorization": hen
    }
    try:
        data = cached_request(url, headers=headers)
    except Exception as e:
        raise RuntimeError(f"Błąd pobierania statystyk: {e}")

    for widget in right_frame.winfo_children():
        widget.destroy()
    for i, match in enumerate(data["data"],start=1):
        if i > 40: #ilosc wyswietlanych  meczy
            break
        match_id = match["meta"]["id"]
        mapa_nazwa = match["meta"]["map"]["name"]
        match_mode = match["meta"]["mode"]
        match_char = match["stats"]["character"]["name"]
        match_char_id = match["stats"]["character"]["id"]
        match_kills = match["stats"]["kills"]
        match_deaths = match["stats"]["deaths"]
        match_assists = match["stats"]["assists"]
        match_team = match["stats"]["team"]
        match_wynik_red = match["teams"]["red"]
        match_wynik_blue = match["teams"]["blue"]
        wynik = ""
        colork = ""
        if match_team == "red":
            if match_wynik_red > match_wynik_blue:
                wynik = "Win"
                colork= "springgreen1"
            elif match_wynik_red < match_wynik_blue:
                wynik = "Lose"
                colork = "coral3"
            elif match_wynik_blue == match_wynik_red:
                wynik = "Drow"
                colork = "gold"
        else:
            if match_wynik_red < match_wynik_blue:
                wynik = "Win"
                colork = "springgreen1"
            elif match_wynik_red > match_wynik_blue:
                wynik = "Lose"
                colork = "coral3"
            elif match_wynik_blue == match_wynik_red:
                wynik = "Drow"
                colork = "gold"
        
            # get_agent_icon(match_char_id)
        frame_mecz = ctk.CTkFrame(right_frame, corner_radius=10, fg_color="gray25")
        frame_mecz.pack(padx=8, pady=6, fill="x")

        # grid layout: kolumny (index, wynik, ikona, kda, detale, przycisk)
        frame_mecz.grid_columnconfigure(4, weight=1)  # detale rozciągają się

        # 1) numer
        idx = ctk.CTkLabel(frame_mecz, text=f"{i}", font=("Arial Rounded MT Bold", 16))
        idx.grid(row=0, column=0, padx=(10,6), pady=8, sticky="w")

        # 2) wynik z tłem (ustawiam stały rozmiar by wyglądało spójnie)
        result = ctk.CTkLabel(
            frame_mecz,
            text=f"{wynik} {match_wynik_red}/{match_wynik_blue}",
            fg_color=colork,
            text_color="black",
            font=("Comic Sans MS", 18, "bold"),
            corner_radius=6,
            width=140,
            height=36
        )
        result.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        # 3) ikona agenta (fixed box)
        icon_label = ctk.CTkLabel(frame_mecz, text="", width=48, height=48)
        icon_label.grid(row=0, column=2, padx=8, pady=6)

        # pobierz i ustaw ikonę agenta (obsługa wyjątków)
        try:
            agent_icon_url,_ = get_valo_char(match_char_id)
            if agent_icon_url:
                get_image(agent_icon_url, 48, 48, icon_label)
        except Exception as e:
            raise RuntimeError(f"Błąd pobierania statystyk: {e}")

        # 4) K/D/A
        kda_label = ctk.CTkLabel(
            frame_mecz,
            text=f"{match_kills} / {match_deaths} / {match_assists}",
            font=("Arial Rounded MT Bold", 14)
        )
        kda_label.grid(row=0, column=3, padx=8, pady=8, sticky="w")

        # 5) detale (tryb, mapa)
        details_text = f"Tryb: {match_mode}\nMapa: {mapa_nazwa}"
        details = ctk.CTkLabel(frame_mecz, text=details_text, font=("Segoe UI", 13), justify="left", anchor="w", wraplength=300)
        details.grid(row=0, column=4, padx=(10,8), pady=8, sticky="w")

        # 6) przycisk Info po prawej
        info_btn = ctk.CTkButton(
            frame_mecz,
            text="Info",
            width=60,
            height=36,
            font=("Comic Sans MS", 12, "bold"),
            command=lambda mid=match_id, nick=name, tagg=tag, reg=region: pokaz_szczegoly(mid, nick, tagg, reg)
        )
        info_btn.grid(row=0, column=5, padx=(6,12), pady=8, sticky="e")
    