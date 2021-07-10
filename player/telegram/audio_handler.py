import os
import re
import logging
import secrets
from random import randrange
from player.telegram import Audio_Master, audio_channel


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
    history_count = await Audio_Master.get_history_count(audio_channel)
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
            msg = await Audio_Master.get_messages(audio_channel, msg_counter_start)
            while True:
                if msg.audio:
                    if msg.audio.file_name.endswith('.mp3'):
                        logging.info(f"Downloading the file from message {msg.message_id} - audio file: {msg.audio.file_name}")
                        titles.append(msg.audio.title)
                        await msg.download(file_name=f"{new_folder.replace('player/', '')}/{secrets.token_hex(2)}.mp3")
                        break
                    else:
                        msg = await Audio_Master.get_messages(audio_channel, msg_counter_start + 1)
                else:
                    msg = await Audio_Master.get_messages(audio_channel, msg_counter_start + 1)

        except Exception as e:
            logging.error(e)

    logging.info("Finished with downloading process!")

    try:
        titles = [re.sub(r"[^a-zA-Z0-9]+", ' ', _) for _ in titles]
    except Exception as e:
        logging.error(e)
        titles = []
        for i in range(0,count):
            titles.append(secrets.token_hex(2))

    return {'directory': new_folder, 'titles': titles}
