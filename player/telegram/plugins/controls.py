import shutil
import logging
import datetime
import player.telegram
from pathlib import Path
from pyrogram.types import Message
from pyrogram import Client, filters
from player.telegram.audio_handler import prepare_audio_files, change_voice_chat_title


async def vc_admins_filter_func(_, c: Client, m: Message):
    member_details = await c.get_chat_member(
        player.telegram.voice_chat, m.from_user.id)
    return member_details.can_manage_voice_chats

vc_admins_filter = filters.create(vc_admins_filter_func)


@Client.on_message(vc_admins_filter & 
                   filters.command("vnext", prefixes="!") & 
                   (filters.chat(player.telegram.voice_chat) | filters.private))
async def next_song_handler(_, m: Message):
    """
    :what it does:
        this filter is used to skip the current song and play a new one.
    """
    group_call = player.telegram.group_call
    raw_file = group_call.input_filename

    await m.delete()

    logging.info("Skipping the current song at playout on request!")
    audio_file_details = await prepare_audio_files()
    group_call.input_filename = audio_file_details['audio_file']
    await change_voice_chat_title(audio_file_details['title'])
    logging.info(
        f"Playing {audio_file_details['title']} of duration {str(datetime.timedelta(seconds=audio_file_details['duration']))}"
    )

    if str(raw_file).endswith(".raw"):
        old_raw_file_path = Path(raw_file)
        try:
            if old_raw_file_path.exists():
                logging.info(f"Removing old raw file {raw_file}")
                shutil.rmtree(old_raw_file_path.parent)
        except Exception as e:
            logging.error(e)


@Client.on_message(vc_admins_filter & 
                   filters.command("vpause", prefixes="!") & 
                   (filters.chat(player.telegram.voice_chat) | filters.private))
async def pause_song_handler(_, m: Message):
    """
    :what it does:
        this filter is used to pause the current playing song.
    """
    group_call = player.telegram.group_call

    await m.delete()

    logging.info("Pausing the current song at playout on request!")
    group_call.pause_playout()


@Client.on_message(vc_admins_filter & 
                   filters.command("vresume", prefixes="!") & 
                   (filters.chat(player.telegram.voice_chat) | filters.private))
async def resume_song_handler(_, m: Message):
    """
    :what it does:
        this filter is used to resume a paused song.
    """
    group_call = player.telegram.group_call

    await m.delete()

    logging.info("Resuming the current song at playout on request!")
    group_call.resume_playout()


@Client.on_message(vc_admins_filter & 
                   filters.command("vrestart", prefixes="!") & 
                   (filters.chat(player.telegram.voice_chat) | filters.private))
async def restart_song_handler(_, m: Message):
    """
    :what it does:
        this filter is used to restart the current playing song.
    """
    group_call = player.telegram.group_call

    await m.delete()

    logging.info("Restarting the current song at playout on request!")
    group_call.restart_playout()
