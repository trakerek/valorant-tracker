import customtkinter as ctk
import requests as rq
from PIL import Image
from io import BytesIO
import webbrowser as wb
import tkinter as tk

from api.valorant_api import get_stats, get_kda, lista_meczy, prof,fetch_elem,show_error
from utils.image_utils import get_image


def fetch_data(nick=None,tag=None):
    global right_frame
    if right_frame is not None and right_frame.winfo_exists():
        for w in right_frame.winfo_children():
            w.destroy()

    print(nick,tag)
    for w in left_frame.winfo_children():
        w.destroy()
    if(nick is None):
        nick = entry_nick.get()
    if(tag is None):
        tag = entry_tag.get()

    if not nick or not tag:
        show_error("❌ Proszę podać zarówno nick, jak i tag!")
        return

    try:
        stats = get_stats(nick, tag)
        if stats is None:
            raise ValueError("Nie znaleziono gracza lub błąd API",duration=3000)
        ranga, mmr, win_ratio, ranga_img_url = stats

        kda_data = get_kda(nick, tag)
        if kda_data is None:
            raise ValueError("Nie udało się pobrać KDA gracza",duration=3000)
        kills, deaths, assists, kd, kda, agent = kda_data

        if win_ratio is None:
            win_ratio = "N/A"
        else:
            win_ratio = f"{win_ratio} %"
        result_label = ctk.CTkLabel(left_frame, text="", font=("Segoe UI",14), wraplength=200)
        result_label.place(relx=0.5, rely=0.05, anchor="n")
        result_label.configure(
            text=f"Ranga: {ranga} \n\nMMR: {mmr} \n\nWin Ratio: {win_ratio} \n\n{kills}/{deaths}/{assists} \n\nKD: {kd}  KDA: {kda}\n\nNajczęściej grany agent: {agent}",
            font=("Comic Sans MS", 15, "bold")
        )

        _, _, _, url = prof(nick, tag)
        get_image(url, 700, 200, bg_label)
        get_image(ranga_img_url, 200, 200, ranga_label)

        lista_meczy(nick, tag)

    except Exception as e:
        show_error(f"❌ Błąd {e}!")
        print(f"Bład: {e}")
    

def duofunkcja(name,tag):
    lista_meczy(name,tag)
    fetch_data(name,tag)
    entry_nick.delete(0, tk.END)
    entry_nick.insert(0, name)
    entry_tag.delete(0, tk.END)
    entry_tag.insert(0, tag)
    entry_nick.focus()

def create_main_window():
    global app, left_frame, right_frame, entry_nick, entry_tag, baner, bg_label, ranga_label,frame
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    logo= "https://media.valorant-api.com/sprays/936f33fb-49d9-277c-496d-cd9ef04a34cc/fullicon.png"

    r = rq.get(logo)
    r.raise_for_status()
    img = Image.open(BytesIO(r.content))
    ico_path = "logo.ico"
    img.save(ico_path,format="ICO",sizes=[(256,256)])

    app = ctk.CTk()
    app.geometry("900x600")
    app.title("Valorant Tracker by traker")
    app.iconbitmap(ico_path)



    frame = ctk.CTkFrame(app)
    frame.pack(fill="both",expand=True)
    frame.grid_rowconfigure(1,weight=1)
    frame.grid_columnconfigure(0,weight=1)
    frame.grid_columnconfigure((1),weight=2)
    frame.grid_columnconfigure((2),weight=2)

    baner= ctk.CTkFrame(frame,fg_color="gray20")
    baner.grid(row=0,column=0,columnspan=3,sticky="nsew",pady=10)



    left_frame = ctk.CTkFrame(frame, fg_color="royalblue1")
    left_frame.grid(row=1,column=0,sticky="nsew",padx=5,pady=10)

    right_frame = ctk.CTkFrame(frame,fg_color="rosybrown2")
    right_frame.grid(row=1,column=1,columnspan=2,sticky="nsew",padx=5,pady=10)


    valo= "https://media.valorant-api.com/sprays/2527155b-4ba6-632b-c745-71900a25ab80/fulltransparenticon.png"
    ggwp= "https://media.valorant-api.com/sprays/89565f02-495e-e6f0-5f67-959626122909/fulltransparenticon.png"
    pingwin= "https://media.valorant-api.com/sprays/7ad73709-4692-decb-ebea-31b637657065/fulltransparenticon.png"
    pho= "https://media.valorant-api.com/sprays/4c08026b-4f56-9494-0d71-3dbb291c4d7f/fulltransparenticon.png"

    valo_label = ctk.CTkLabel(right_frame,text="")
    get_image(valo,550,400,valo_label)
    valo_label.pack(pady=10)

    r_gg = rq.get(ggwp)
    img_ggwp = Image.open(BytesIO(r_gg.content)).convert("RGBA")
    rotated = img_ggwp.rotate(45, expand=True)
    ctk_img = ctk.CTkImage(light_image=rotated, dark_image=rotated, size=(250,200))

    ggwp_label = ctk.CTkLabel(baner,text="",image=ctk_img)
    ggwp_label.place(anchor="n",relx=0.12,rely=0.02)

    pho_label = ctk.CTkLabel(baner,text="")
    get_image(pho,300,200,pho_label)
    pho_label.place(anchor="e",relx=0.95,rely=0.5)

    pin_label = ctk.CTkLabel(left_frame,text="")
    get_image(pingwin,100,100,pin_label)
    pin_label.place(anchor="n",relx=0.5,rely=0.7)



    github = "https://cdn-icons-png.flaticon.com/512/25/25231.png"
    r = rq.get(github)   
    img_data = BytesIO(r.content) 
    git_image = ctk.CTkImage(light_image=Image.open(img_data),dark_image=Image.open(img_data),size=(35,35))

    git_button = ctk.CTkButton(baner,width=40,height=50,fg_color="indigo",hover_color="purple4",corner_radius=10,image=git_image,text="",border_width=1,border_color="black",
                            command=lambda: wb.open("https://github.com/trakerek"))
    git_button.place(relx=0.95, rely=0.05, anchor="n") 

    left_label = ctk.CTkLabel(left_frame,text="Witaj w Valorant Trackerze!\n✦ Podaj nick i tag\n✦ Kliknij 'Pobierz statystyki'\n✦ Zobacz swoje mecze",
                            font=("Segoe UI", 18),justify="center").place(anchor="n",relx=0.5,rely=0.2)

    bg_label = ctk.CTkLabel(baner, text="")
    bg_label.place(relx=0.6, rely=0.5, anchor="center") 

    input_frame = ctk.CTkFrame(baner, corner_radius=15)
    input_frame.place(relx=0.5, rely=0.5, anchor="center")


    ranga_label = ctk.CTkLabel(baner,text="")
    ranga_label.place(relx=0,rely=0.5, anchor="w") 


    label = ctk.CTkLabel(input_frame,text="Podaj nick i tag ",font=("Segoe UI", 20))
    label.pack(pady=10,padx=10)

    entry_nick = ctk.CTkEntry(input_frame,placeholder_text="Nick",text_color="white",border_width=2,font=("Segoe UI",16))
    entry_nick.pack(pady=10,padx=10)

    entry_tag = ctk.CTkEntry(input_frame,placeholder_text="Tag",text_color="white",border_width=2,font=("Segoe UI",16))
    entry_tag.pack(pady=10,padx=10)


    button = ctk.CTkButton(input_frame, text="Pobierz statystyki",fg_color="#B6374C",hover_color="#851629",command=fetch_data)
    button.pack(pady=10,padx=10)
    fetch_elem(left_frame,right_frame,frame,baner,entry_nick,entry_tag)
    return app