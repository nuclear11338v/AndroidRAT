import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import StreamAudio

# Telegram credentials
API_ID = 27152769
API_HASH = "b98dff566803b43b3c3120eec537fc1d"
BOT_TOKEN = "7910848214:AAHVBM9OhbpsH8GPx3zDzHe3_OzLoOhg_sQ"

# Bot aur Voice Chat client initialize karo
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = PyTgCalls(app)  # PyTgCalls instance

# Audio file jo play karna hai
AUDIO_FILE = "audio.mp3"

# /start command
@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply("Hello! Main ek VC music bot hoon. Group mein /play use karo!")

# /play command - VC mein audio play karo
@app.on_message(filters.command("play") & filters.group)
async def play_command(client: Client, message: Message):
    chat_id = message.chat.id
    
    if not os.path.exists(AUDIO_FILE):
        await message.reply("Audio file nahi mili!")
        return
    
    try:
        await vc.join_group_call(chat_id, StreamAudio(AUDIO_FILE))
        await message.reply("Music play ho raha hai VC mein!")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

# Bot chalu karo
if __name__ == "__main__":
    print("Bot starting...")
    app.run()
