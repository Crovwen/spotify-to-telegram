import asyncio
import time
from telethon.sync import TelegramClient
from telethon import functions
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# ⚙️ اطلاعات شما
api_id = 20292726
api_hash = '86902140c904c0de4a5813813c9a2409'
phone = '+989056072099'

client_id = '433d131ec419444a91fb9faf9f72ae59'
client_secret = 'd99a700855e44d12ad1f865fa48fa303'
redirect_uri = 'http://127.0.0.1:8888/callback'
scope = 'user-read-playback-state user-read-currently-playing'

sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    open_browser=True
))

def format_time(seconds):
    return f"{seconds // 60:02}:{seconds % 60:02}"

async def main():
    while True:  # اگر تلگرام قطع شد، دوباره تلاش کن
        try:
            async with TelegramClient('session', api_id, api_hash) as client:
                await client.start(phone=phone)

                last_progress = 0
                last_update = time.time()
                last_song_id = None

                while True:
                    try:
                        current = sp.current_playback()

                        if current and current.get('is_playing') and current.get('item'):
                            track = current['item']
                            song = track['name']
                            artist = track['artists'][0]['name']
                            duration = track['duration_ms'] // 1000
                            progress = current['progress_ms'] // 1000
                            song_id = track['id']

                            if song_id != last_song_id:
                                last_song_id = song_id
                                last_progress = progress
                                last_update = time.time()
                            else:
                                elapsed = int(time.time() - last_update)
                                last_progress += elapsed
                                last_update = time.time()

                            bio = f"🎧 {song} - {artist}\n{format_time(last_progress)} / {format_time(duration)}"
                        else:
                            bio = "🎧 Spotify is paused"

                        await client(functions.account.UpdateProfileRequest(about=bio))

                    except Exception as e:
                        print("⚠️ خطا در حلقه:", e)

                    await asyncio.sleep(5)

        except Exception as e:
            print("⚠️ خطا در اتصال تلگرام:", e)
            print("⏳ دوباره تلاش می‌کنم...")
            await asyncio.sleep(10)

asyncio.run(main())