import os
import shutil
import secrets
import subprocess


def merge_files(path: str) -> dict:
    """
    :what it does:
        1. create a playlist file for ffmpeg with the details of the files in the path given
        2. create a new directory for ffmpeg mix to be saved
        3. merge all the files in the given "path" and export/save the output to the directory created at pt.2
        4. convert the saved output file on pt.3 to a raw file
        5. get the duration of the file saved on pt.3
        6. remove the directory mentioned on pt.1 and its content since its no more needed
        7. remove the file mentioned on pt.3 as its no more needed 
    :param: 
        path: 
            path to which audio files were downloaded, expects a string value
    :return:
        a dict with abspath to the raw file and its duration
    """
    playlist = f"{path}/playlist.txt"
    for fn in next(os.walk(path))[2]:
        playlist_file = open(playlist, "a")
        playlist_file.write("file '" + os.path.abspath(os.path.join(path, fn)) + "'\n")
        playlist_file.close()

    new_mix_path = f"player/working_dir/{secrets.token_hex(2)}"
    if not os.path.exists(new_mix_path):
        os.mkdir(new_mix_path)

    new_mix = os.path.abspath(os.path.join(new_mix_path, "output.mp3"))
    mix_cmd = f"ffmpeg -v quiet -f concat -safe 0 -i {os.path.abspath(playlist)} -c copy {new_mix}"
    os.system(mix_cmd)

    convert_raw_cmd = f"ffmpeg -v quiet -i {new_mix} -f s16le -ac 2 -ar 48000 -acodec pcm_s16le {new_mix.replace('.mp3', '.raw')}"
    os.system(convert_raw_cmd)

    get_duration_cmd = f"ffprobe -v quiet -of csv=p=0 -show_entries format=duration {new_mix}"
    duration = subprocess.check_output(get_duration_cmd, shell=True)

    if os.path.exists(path):
        shutil.rmtree(path)

    if os.path.exists(new_mix):
        os.remove(new_mix)

    return {'raw_file': new_mix.replace('.mp3', '.raw'), 'duration': float(duration.decode("utf-8").replace('\n', ''))}
