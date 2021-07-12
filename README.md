# MvEargasmDJ:
This is my submission for the Telegram Radio Project of Baivaru. Which required a userbot to continiously play random audio files from the famous telegram music channel @mveargasm in a voice chat.

## Available Commands to Control the Playlist:
Only members with access to amend/change voice chat options are allowed to use the following commands.
    1. **!vnext** - skips the current playing song and play a new one.
    2. **!vpause** - pause the current playing song.
    3. **!resume** - resume a paused song.
    4. **!restart** - restart the current playing song.

## Cloning and Run:
1. `git clone https://github.com/eyaadh/mveargasmdj.git`, to clone the repository.
2. `cd mveargasmdj`, to enter the directory.
3. `pip3 install -r requirements.txt`, to install rest of the dependencies/requirements.
4. Create a new `config.ini` using the sample available at `config.ini.sample`.
5. Insall ffmpeg `apt install ffmpeg`
5. Run with `python3.8 -m player`, stop with <kbd>CTRL</kbd>+<kbd>C</kbd>.
> It is recommended to use [virtual environments](https://docs.python-guide.org/dev/virtualenvs/) while running the app, this is a good practice you can use at any of your python projects as virtualenv creates an isolated Python environment which is specific to your project.
