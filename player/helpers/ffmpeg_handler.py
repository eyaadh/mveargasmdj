import os
import shutil
import logging
import secrets
import asyncio
from pathlib import Path


async def convert_audio_to_raw(audio_file: str) -> dict:
    """
    :what it does:
        1. create a temporary directory to save the output of the converted raw file
        2. run ffmpeg externally to convert given mp3 audio_file to a raw file:
            Note: since ffmpeg is run externally we took the abspath of the audio file at the very
                beginning of the function
        3. remove the given audio file and its directory since it is not needed any more
    :params:
        audio_file: a string value expected
            path of the mp3 audio file that requires to be converted to a raw file
    :return:
        a dict with the key 'raw_file' for the path of the raw file that was generated.
    """
    audio_file_abspath = os.path.abspath(audio_file)

    audio_covertion_directory = f"player/working_dir/{secrets.token_hex(2)}"
    logging.info(f"Creating temp directory {audio_covertion_directory} for audio converting process")
    if not os.path.exists(audio_covertion_directory):
        os.mkdir(audio_covertion_directory)

    raw_file = os.path.join(audio_covertion_directory, f"{secrets.token_hex(2)}.raw")
    logging.info(f"Converting {audio_file} to raw: {raw_file}")

    process_cmd = [
        "ffmpeg", 
        "-v", 
        "quiet", 
        '-i', 
        audio_file_abspath, 
        "-f", 
        "s16le", 
        "-ac", 
        "2", 
        "-ar", 
        "48000", 
        "-acodec",
        "pcm_s16le", 
        raw_file
    ]

    process = await asyncio.create_subprocess_exec(*process_cmd, stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)
    
    _, _ = await process.communicate()

    audio_file_path = Path(audio_file)
    if os.path.exists(audio_file):
        logging.info(f"Finished converting and Removing {audio_file}")
        shutil.rmtree(audio_file_path.parent)

    return {'raw_file': raw_file}
