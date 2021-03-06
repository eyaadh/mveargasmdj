import pytgcalls
import configparser
from pyrogram import Client

Audio_Master = Client(
    session_name="audio_bot",
    workers=200,
    workdir="player/working_dir",
    config_file="player/working_dir/config.ini",
    plugins=dict(root="player/telegram/plugins")
)

app_config = configparser.ConfigParser()
app_config.read("player/working_dir/config.ini")
audio_channel = int(app_config.get("audio-master", "audio_channel"))
voice_chat = int(app_config.get("audio-master", "voice_chat"))

raw_file_path = None

group_call = pytgcalls.GroupCall(None, path_to_log_file='')
