# sorry, python was the only way i know to reliably get self botting working

import cydoomgeneric as cdg
import discord

from PIL import Image
import asyncio
import io
import threading
import time
import os
import sys

from collections import deque


resx = 640
resy = 400

bindings = [("🔼", cdg.Keys.UPARROW),
            ("🔽", cdg.Keys.DOWNARROW),
            ("◀", cdg.Keys.LEFTARROW),
            ("▶", cdg.Keys.RIGHTARROW),
            ("⏹", cdg.Keys.ENTER),
            ("⏺", cdg.Keys.USE),
            ("💥", cdg.Keys.FIRE)]



client = discord.Client()
chan = None
display = None

loop = asyncio.new_event_loop()

last_upd = 0.0
key_buf: deque[tuple[int, int]] = deque()




def press(key):
    key_buf.append((1, key))
    key_buf.append(None)
    key_buf.append((0, key))
    key_buf.append(None)

@client.event
async def on_ready():
    global chan
    print("mraowww logged in1!1")

    chan = client.get_channel(int(sys.argv[1]))


async def button(payload):
    global bindings
    
    print(payload.emoji)
    for bind in bindings:
        if(str(payload.emoji) == bind[0]):
            press(bind[1])
            print(bind)

@client.event
async def on_raw_reaction_add(payload):
    await button(payload)

@client.event
async def on_raw_reaction_remove(payload):
    await button(payload)

#     
# @client.event
# async def on_reaction_remove(payload):




def draw_frame(pixels: np.ndarray) -> None:
    global last_upd
    global display

    now = time.monotonic()
    
    if chan is None:
        return
    
    if (now - last_upd) < 1.0:
        return
    last_upd = now

    rgb = pixels[:, :, 2::-1]
    img = Image.fromarray(rgb, mode="RGB") 

    png = io.BytesIO()
    img.save(png, format="PNG")
    png.seek(0)

    file = discord.File(fp=png, filename="clip.png")
    if display:
        future = asyncio.run_coroutine_threadsafe(display.edit(attachments=[file]), loop)
        result = future.result()
        display = result
    else:
        future = asyncio.run_coroutine_threadsafe(chan.send(file=file), loop)
        result = future.result()
        display = result

        for bind in bindings:
            asyncio.run_coroutine_threadsafe(display.add_reaction(bind[0]), loop)

def get_key() -> Optional[tuple[int, int]]: 
    if key_buf:
        return key_buf.popleft()
    return None




def start_discord(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)

    loop.run_until_complete(client.start(os.environ['TOKEN']))
threading.Thread(target=start_discord, args=(loop,), daemon=True).start()

cdg.init(
    resx,
    resy,
    draw_frame,
    get_key,
); cdg.main(["doom", "-iwad", "DOOM1.WAD", "-warp", "1", "1"])

