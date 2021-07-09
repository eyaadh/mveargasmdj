import time
import shutil
import random
import logging
import asyncio
import datetime
import pytgcalls
from pathlib import Path
from pyrogram import idle
from pyrogram.raw import functions, types
from player.helpers.ffmpeg_handler import merge_files
from player.telegram.audio_handler import download_random_messages
from player.telegram import Audio_Master, voice_chat, number_of_tracks_to_download

raw_file_path = None

async def main():
    global raw_file_path
    await Audio_Master.start()
    while not Audio_Master.is_connected:
        await asyncio.sleep(1)

    audio_download_proc = await download_random_messages(number_of_tracks_to_download)
    audio_download_path = audio_download_proc['directory']
    audio_titles = audio_download_proc['titles']

    master_loop = asyncio.get_event_loop()
    proc_merge_files = master_loop.run_in_executor(None, merge_files, audio_download_path)
    resp_merge_files = await proc_merge_files

    initiate_time = time.time()
    mix_duration = resp_merge_files['duration']
    raw_file = resp_merge_files['raw_file']

    group_call = pytgcalls.GroupCall(Audio_Master, raw_file)
    
    peer = await Audio_Master.resolve_peer(voice_chat)
    chat = await Audio_Master.send(functions.channels.GetFullChannel(channel=peer))

    await group_call.start(voice_chat)
    logging.info(f"Playing mix of duration {str(datetime.timedelta(seconds=resp_merge_files['duration']))}")

    while True:
        await asyncio.sleep(5)
        if (time.time() - initiate_time) > (mix_duration - 5):
            audio_download_proc = await download_random_messages(number_of_tracks_to_download)
            audio_download_path = audio_download_proc['directory']
            audio_titles = audio_download_proc['titles']

            master_loop = asyncio.get_event_loop()
            proc_merge_files = master_loop.run_in_executor(None, merge_files, audio_download_path)
            resp_new_merge_files = await proc_merge_files
            
            new_raw_file = resp_new_merge_files['raw_file']
            initiate_time = time.time()
            mix_duration = resp_new_merge_files['duration']
            
            logging.info(f"Playing mix of duration {str(datetime.timedelta(seconds=resp_new_merge_files['duration']))}")
            group_call.input_filename = new_raw_file

            raw_file_path = Path(raw_file)
            if raw_file_path.exists():
                shutil.rmtree(raw_file_path.parent)

            raw_file = new_raw_file
        else:
            await Audio_Master.send(
                functions.phone.EditGroupCallTitle(
                    call = chat.full_chat.call,
                    title = f"Mix has: 🎙️{random.choice(audio_titles)}"
                )
            )

    
    await idle()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt as e:
        loop.stop()
    finally:
        if raw_file_path:
            logging.info("Removing temporary files and closing the loop!")
            if raw_file_path.exists():
                shutil.rmtree(raw_file_path.parent)
