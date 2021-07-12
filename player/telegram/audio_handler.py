import os
import re
import random
import shutil
import secrets
import asyncio
import logging
import datetime
import pytgcalls
import player.telegram
from pathlib import Path
from random import randrange
from pyrogram.raw import functions
from player.helpers.retry_deco import retry
from player.helpers.ffmpeg_handler import convert_audio_to_raw

group_call = pytgcalls.GroupCall(None, path_to_log_file='')


@retry(Exception, tries=4)
async def download_random_message() -> dict:
    """
    :what it does:
        1. get the history count of the intended chat and select a random message id
        2. get the associated message for the selected random message id at step.1
        3. until the selected message contains an audio file or the audio file doesn't have the extension mp3 
            get a different message by either increasing the random message id by one or decreasing it by one
        4. create a temp directory and download the audio file in the message selected to this directory
    :return:
        a dict with the keys:
            audio_file: the mp3 file that was downloaded
            title: the title of the mp3 file (special charectors are removed from the tile)
            duration: of the mp3 file
    """
    try:
        history_count = await player.telegram.Audio_Master.get_history_count(player.telegram.audio_channel)
        random_msg_id = randrange(1, history_count)


        msg = await player.telegram.Audio_Master.get_messages(player.telegram.audio_channel, random_msg_id)

        while (not msg.audio) or (not msg.audio.file_name.endswith('.mp3')):
            await asyncio.sleep(3)
            msg = await player.telegram.Audio_Master.get_messages(
                    chat_id=player.telegram.audio_channel, 
                    message_ids=random_msg_id - 1 if random_msg_id >= history_count else random_msg_id + 1
                )
        
        logging.info(f"About to start downloading the song: {msg.audio.title} from message: {msg.message_id}")
        new_directory = f"player/working_dir/{secrets.token_hex(2)}"
        audio_file = f"{new_directory}/{secrets.token_hex(2)}.mp3"
        logging.info(f"Creating the temporary directory {new_directory} to save the audio file")

        if not os.path.exists(new_directory):
            os.mkdir(new_directory)

        logging.info(f"Downloading the file: {msg.audio.file_name} from message: {msg.message_id} to {new_directory}")
        await msg.download(file_name=audio_file.replace('player/', ''))
        logging.info(f"Finished with Downloading process!")
    except Exception as e:
        logging.error(e)
        raise
    try:
        title = re.sub(r"[^a-zA-Z0-9]+", ' ', msg.audio.title)
    except Exception as e:
        title = secrets.token_hex(2)

    return {'audio_file': audio_file, 'title': title, 'duration': msg.audio.duration if msg.audio.duration else 1}


async def start_player():
    """
    :what it does:
        1. check if the chat has a voice chat already started, if not keep trying 
            until a voice chat can be started
        2. prepare and get the audio file for the initial song by calling the 
            function prepare_audio_files()
        3. start playing the audio file within the voice chat/call
        4. update the title of the voice chat with the title of audio file that we got 
            at step.2, by calling the function change_voice_chat_title(*args)
        5. add change_player_song() as a handler to group call, to trigger at playout_end action 
    """
    peer = await player.telegram.Audio_Master.resolve_peer(player.telegram.voice_chat)
    chat = await player.telegram.Audio_Master.send(functions.channels.GetFullChannel(channel=peer))
    voice_chat_details = await player.telegram.Audio_Master.get_chat(player.telegram.voice_chat)
    
    while not chat.full_chat.call:
        await asyncio.sleep(3)
        logging.info(f"Trying to starting a group voice chat at {voice_chat_details.title} call since there isn't")
        await player.telegram.Audio_Master.send(
            functions.phone.CreateGroupCall(
                peer=peer,
                random_id=random.randint(1,99)
            )
        )

        chat = await player.telegram.Audio_Master.send(functions.channels.GetFullChannel(channel=peer))

    audio_file_details = await prepare_audio_files()

    group_call = pytgcalls.GroupCall(
        client=player.telegram.Audio_Master, 
        input_filename=audio_file_details['audio_file'],
        play_on_repeat=False
    )

    player.telegram.group_call = group_call

    await group_call.start(player.telegram.voice_chat)
    await change_voice_chat_title(audio_file_details['title'])
    logging.info(
        f"Playing {audio_file_details['title']} of duration {str(datetime.timedelta(seconds=audio_file_details['duration']))}"
    )

    group_call.add_handler(
        change_player_song,
        pytgcalls.GroupCallAction.PLAYOUT_ENDED
    )


async def prepare_audio_files():
    """
    :what it does:
        1. download a mp3 file from a random message by calling the function download_random_message()
        2. convert the downloaded mp3 file to a raw file by calling the function 
            convert_audio_to_raw(*args) from player.helpers.ffmpeg_handler
    :returns:
        a dict with the keys:
            audio_file: raw file that was generated
            title: title of the audio file that was downloaded
            duration: duration of the audio file in seconds
    """
    audio_download_proc = await download_random_message()
    audio_file = audio_download_proc['audio_file']

    converted_audio_file = await convert_audio_to_raw(audio_file)

    raw_file = converted_audio_file['raw_file']
    player.telegram.raw_file_path = Path(raw_file)

    return {'audio_file': raw_file, 'title': audio_download_proc['title'], 'duration': audio_download_proc['duration']}


async def change_player_song(group_call, raw_file):
    """
    :what it does:
        1. prepare a new audio file to be played at the voice chat by 
            calling prepare_audio_files()
        2. change the current playing audio file with the new file that we got at step.1
        3. update the title of the voice chat with the title of the audio file that we got 
            from the dict at step.1
        4. remove the old raw audio file from disk as it is not required anymore
    """
    audio_file_details = await prepare_audio_files()
    group_call.input_filename = audio_file_details['audio_file']
    await change_voice_chat_title(audio_file_details['title'])
    logging.info(
        f"Playing {audio_file_details['title']} of duration {str(datetime.timedelta(seconds=audio_file_details['duration']))}"
    )

    old_raw_file_path = Path(raw_file)
    try:
        if old_raw_file_path.exists():
            logging.info(f"Removing old raw file {raw_file}")
            shutil.rmtree(old_raw_file_path.parent)
    except Exception as e:
        logging.error(e)


async def change_voice_chat_title(title: str):
    """
    :what it does:
        this function basically updates the title of the voice chat with the value of argument 
        title that was provided
    :params:
        title: String value expected
            this is the title of the file that is being played at the voice chat
    """
    peer = await player.telegram.Audio_Master.resolve_peer(player.telegram.voice_chat)
    chat = await player.telegram.Audio_Master.send(functions.channels.GetFullChannel(channel=peer))

    await player.telegram.Audio_Master.send(
        functions.phone.EditGroupCallTitle(
            call = chat.full_chat.call,
            title = f"Playing: 🎙️ {title if title else secrets.token_hex(2)}"
        )
    )
