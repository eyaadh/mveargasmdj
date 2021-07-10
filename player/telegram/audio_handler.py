import os
import re
import time
import random
import shutil
import secrets
import asyncio
import logging
import datetime
from pyrogram.types.messages_and_media import message
import pytgcalls
import player.telegram
from pathlib import Path
from random import randrange
from pyrogram.raw import functions
from player.helpers.ffmpeg_handler import merge_files

raw_file_path = None


async def download_random_messages(count: int = 2) -> dict:
    """
    :what it does:
        1. get history count
        2. chose a random message based on the count
        3. create a start and an end point for the counter based on the arge count 
        4. create a new directory for the files to be downloaded
        5. try downloading the audio of the messages based on the counter that was decided at pt.3
        6. if the message doesn't contain an audio increase the msg_id thats being checked to download and try downloading once again
    :param: 
        count: 
            int expected, defaults to 2, this is basically the number of messages that the function will try download.
    :return:
        a dict with the path at which the files were downloaded and the titles of the files downloaded.
        we also remove the special charectors from the titles list that is returned
    """
    history_count = await player.telegram.Audio_Master.get_history_count(player.telegram.audio_channel)
    random_msg_id = randrange(count, history_count)
    msg_counter_start = random_msg_id if (random_msg_id > count) else (random_msg_id+count)
    msg_counter_end = msg_counter_start + count

    logging.info(f"Randomly downloading the next {count} messages starting from {msg_counter_start}")
    new_folder = f"player/working_dir/{secrets.token_hex(2)}"
    logging.info(f"Creating the temporary directory {new_folder}")
    if not os.path.exists(new_folder):
        os.mkdir(new_folder)

    titles = []
    while msg_counter_start != msg_counter_end:
        msg_counter_start = msg_counter_start + 1
        try:
            msg = await player.telegram.Audio_Master.get_messages(player.telegram.audio_channel, msg_counter_start)
            
            while (not msg.audio) or (not msg.audio.file_name.endswith('.mp3')):
                msg = await player.telegram.Audio_Master.get_messages(
                        player.telegram.audio_channel, 
                        msg_counter_start + 1 if msg_counter_start < history_count else msg_counter_start - 1
                    )
  

            logging.info(f"Downloading the file from message {msg.message_id} - audio file: {msg.audio.file_name}")
            titles.append(msg.audio.title)
            await msg.download(file_name=f"{new_folder.replace('player/', '')}/{secrets.token_hex(2)}.mp3")

        except Exception as e:
            logging.error(e)

    logging.info("Finished with downloading process!")

    try:
        titles = [re.sub(r"[^a-zA-Z0-9]+", ' ', _) for _ in titles]
    except Exception as e:
        logging.error(e)
        titles = [secrets.token_hex(2) for _ in range(0, count)]

    return {'directory': new_folder, 'titles': titles}


async def start_player():
    """
    :what it does:
        1. call download_random_messages(*args) to download the desired audio files
        2. on a executor run the merge files operation by calling the function merge_files(*args) 
            from player.helpers with the path from the dict that was returned at step.1
        3. check if there is already a voice call if not start a group voice chat
        4. start playing the raw file from step. 2 within the call
        5. start an indefenite loop within which:
            a. check if the time passed since step 4. is less than the duration of the 
                raw file mentioned at step 4, here duration we get from the dict returned from
                the step 2.
            b. if the time passed is less then update the voice chat title with a random item from 
                titles list from dict returned at step 1
            c. otherwise:
                i. repeat the steps 1-2
                ii. update the variables initate_time and mix_duration with the relavent data that is 
                    returend from performing step 5.c.ii
                iii. remove the old raw_file and its directory as its not needed any more
                iv. asign the variable raw_file with the new file
    """

    audio_download_proc = await download_random_messages(player.telegram.number_of_tracks_to_download)
    audio_download_path = audio_download_proc['directory']
    audio_titles = audio_download_proc['titles']

    master_loop = asyncio.get_event_loop()
    proc_merge_files = master_loop.run_in_executor(None, merge_files, audio_download_path)
    resp_merge_files = await proc_merge_files

    initiate_time = time.time()
    mix_duration = resp_merge_files['duration']
    raw_file = resp_merge_files['raw_file']
    player.telegram.raw_file_path = Path(raw_file)

    group_call = pytgcalls.GroupCall(player.telegram.Audio_Master, raw_file)
    
    peer = await player.telegram.Audio_Master.resolve_peer(player.telegram.voice_chat)
    chat = await player.telegram.Audio_Master.send(functions.channels.GetFullChannel(channel=peer))


    if not chat.full_chat.call:
        await player.telegram.Audio_Master.send(
            functions.phone.CreateGroupCall(
                peer=peer,
                random_id=random.randint(0,10)
            )
        )
        chat = await player.telegram.Audio_Master.send(functions.channels.GetFullChannel(channel=peer))

    await group_call.start(player.telegram.voice_chat)
    logging.info(f"Playing mix of duration {str(datetime.timedelta(seconds=mix_duration))}")

    while True:
        await asyncio.sleep(5)
        if (time.time() - initiate_time) > (mix_duration - 5):
            audio_download_proc = await download_random_messages(player.telegram.number_of_tracks_to_download)
            audio_download_path = audio_download_proc['directory']
            audio_titles = audio_download_proc['titles']

            master_loop = asyncio.get_event_loop()
            proc_merge_files = master_loop.run_in_executor(None, merge_files, audio_download_path)
            resp_new_merge_files = await proc_merge_files
            
            new_raw_file = resp_new_merge_files['raw_file']
            initiate_time = time.time()
            mix_duration = resp_new_merge_files['duration']
            
            logging.info(f"Playing mix of duration {str(datetime.timedelta(seconds=mix_duration))}")
            group_call.input_filename = new_raw_file

            player.telegram.raw_file_path = Path(raw_file)
            try:
                if raw_file_path.exists():
                    shutil.rmtree(raw_file_path.parent)
            except Exception as e:
                logging.error(e)

            raw_file = new_raw_file
        else:
            audio_title = random.choice(audio_titles)
            await player.telegram.Audio_Master.send(
                functions.phone.EditGroupCallTitle(
                    call = chat.full_chat.call,
                    title = f"Mix has: 🎙️{audio_title if audio_title else secrets.token_hex(2)}"
                )
            )
