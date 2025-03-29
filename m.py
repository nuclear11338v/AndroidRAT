import os
from pyrogram import Client, filters
from pytgcalls import GroupCallFactory

# Telegram credentials
API_ID = 27152769
API_HASH = "b98dff566803b43b3c3120eec537fc1d"
BOT_TOKEN = "7910848214:AAHVBM9OhbpsH8GPx3zDzHe3_OzLoOhg_sQ"

# Bot aur GroupCall initialize karo
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
group_call = GroupCallFactory(app).get_file_group_call()

# Audio file jo play karna hai
AUDIO_FILE = "audio.mp3"  # Apni audio file ka path daalo

# /start command
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await message.reply("Hello! Main ek VC music bot hoon. Group mein /play use karo!")

# /play command - VC mein audio play karo
@app.on_message(filters.command("play") & filters.group)
async def play_command(client, message):
    chat_id = message.chat.id
    
    # Check if audio file exists
    if not os.path.exists(AUDIO_FILE):
        await message.reply("Audio file nahi mili!")
        return
    
    # VC join karo aur play shuru karo
    try:
        group_call.input_filename = AUDIO_FILE
        await group_call.start(chat_id)
        await message.reply("Music play ho raha hai VC mein!")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

# Bot chalu karo
if __name__ == "__main__":
    print("Bot starting...")
    app.run()
