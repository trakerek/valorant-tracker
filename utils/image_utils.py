import customtkinter as ctk
import requests as rq
from PIL import Image
from io import BytesIO

def get_image(img_url,x,y,label):
    r = rq.get(img_url)   
    img_data = BytesIO(r.content) 
    bg_image = ctk.CTkImage(light_image=Image.open(img_data),dark_image=Image.open(img_data),size=(x,y))
    label.configure(image=bg_image)

def get_valo_char(agentUuid):
    url = f"https://valorant-api.com/v1/agents/{agentUuid}"
    r= rq.get(url)
    data = r.json()
    return data["data"]["displayIcon"], data["data"]["background"]

def get_map_icon(mapUuid):
    url = f"https://valorant-api.com/v1/maps/{mapUuid}"
    r = rq.get(url)
    data = r.json()
    return data["data"]["listViewIcon"]

def set_agent_with_bg(left_container, bg_img_url, agent_img_url,
                     bg_size=(400,400), agent_size=(300,300),
                     agent_offset=(20, "center")):
    try:
        try:
            color_name = left_container.cget("fg_color")
            r, g, b = left_container.winfo_rgb(color_name)
            bg_color = (r // 256, g // 256, b // 256)
        except Exception:
            bg_color = (255, 255, 255)

        r1 = rq.get(bg_img_url, timeout=10); r1.raise_for_status()
        r2 = rq.get(agent_img_url, timeout=10); r2.raise_for_status()
        pil_bg = Image.open(BytesIO(r1.content)).convert("RGBA")
        pil_fg = Image.open(BytesIO(r2.content)).convert("RGBA")

        # --- resizey ---
        pil_bg = pil_bg.resize(bg_size, Image.LANCZOS)
        pil_fg = pil_fg.resize(agent_size, Image.LANCZOS)

        canvas = Image.new("RGBA", bg_size, bg_color + (255,)) 

        canvas.paste(pil_bg, (0, 0), pil_bg)

        x_off, y_off = agent_offset
        if y_off == "center":
            y_off = (bg_size[1] - agent_size[1]) // 2

        canvas.paste(pil_fg, (x_off, y_off), pil_fg)

        final_img = canvas.convert("RGB")

        ctki = ctk.CTkImage(light_image=final_img, dark_image=final_img, size=bg_size)

        lbl = ctk.CTkLabel(left_container, text="")
        lbl.place(relx=0, rely=0.5, anchor="w")
        lbl.configure(image=ctki)
        lbl.image = ctki

        return lbl

    except Exception as e:
        print("Błąd podczas składania obrazów:", e)
        return None
