import os, asyncio
import aria2p
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, MAX_FILE_SIZE, OWNER_ID
from utils import sizeof_fmt, progress_bar
from db import add_user, log_download, get_stats

aria2 = aria2p.API(
    aria2p.Client(host="http://localhost", port=6800, secret="")
)

app = Client("premium_torrent_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & filters.command("start"))
async def start_cmd(_, m: Message):
    add_user(m.from_user.id)
    await m.reply("👋 Welcome to **Premium Torrent Bot**.\nSend a magnet or `.torrent` file to get started!")

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(_, m: Message):
    stats = get_stats()
    await m.reply(f"📊 **Bot Stats**:\n👥 Users: `{stats['total_users']}`\n📁 Downloads: `{stats['total_downloads']}`")

@app.on_message(filters.document & filters.private)
async def torrent_file(_, m: Message):
    if not m.document.file_name.endswith(".torrent"):
        return await m.reply("❌ Not a valid `.torrent` file.")
    path = await m.download()
    try:
        download = aria2.add_torrent(path)
        await handle_download(m, download)
    except Exception as e:
        await m.reply(f"❌ Error: {e}")

@app.on_message(filters.text & filters.private)
async def magnet(_, m: Message):
    if not m.text.startswith("magnet:?xt="):
        return await m.reply("⚠️ Invalid magnet link.")
    try:
        download = aria2.add_magnet(m.text.strip())
        await handle_download(m, download)
    except Exception as e:
        await m.reply(f"❌ Error: {e}")

async def handle_download(m: Message, download):
    status = await m.reply("📥 Starting download...")
    while not download.is_complete:
        await asyncio.sleep(5)
        download.update()
        await status.edit(
            f"📂 `{download.name}`\n✅ {download.progress_string()} | {sizeof_fmt(download.download_speed)}/s"
        )
    await status.edit("✅ Download complete. Uploading...")

    for root, _, files in os.walk(download.dir):
        for file in files:
            filepath = os.path.join(root, file)
            await send_file(m, filepath)
            log_download(m.from_user.id, file)
    aria2.remove([download], force=True, files=True)

async def send_file(m: Message, path: str):
    size = os.path.getsize(path)
    name = os.path.basename(path)
    if size > MAX_FILE_SIZE:
        await m.reply(f"⚠️ Splitting `{name}` due to size > 2GB...")
        parts = await split_large(path)
        for part in parts:
            await upload(m, part)
            os.remove(part)
    else:
        await upload(m, path)
        os.remove(path)

async def upload(m, path):
    msg = await m.reply(f"📤 Uploading `{os.path.basename(path)}`...")
    await m.reply_document(
        document=path,
        caption=os.path.basename(path),
        progress=progress_bar,
        progress_args=(msg,)
    )
    await msg.delete()

async def split_large(path, chunk_size=1900 * 1024 * 1024):
    import math
    parts = []
    size = os.path.getsize(path)
    total_parts = math.ceil(size / chunk_size)
    with open(path, "rb") as f:
        for i in range(total_parts):
            part = f"{path}.part{i+1}"
            with open(part, "wb") as pf:
                pf.write(f.read(chunk_size))
            parts.append(part)
    return parts

app.run()
