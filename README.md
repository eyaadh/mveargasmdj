# MvEargasmDJ:
This is my submission for the Radio Project of Baivaru. Which required a userbot to continiously play random audio files from the famous telegram music channel @mveargasm in a voice chat.

## Cloning and Run:
1. `git clone https://github.com/eyaadh/mveargasmdj.git`, to clone the repository.
2. `cd mveargasmdj`, to enter the directory.
3. `pip3 install -r requirements.txt`, to install rest of the dependencies/requirements.
4. Create a new `config.ini` using the sample available at `config.ini.sample`.
5. Insall ffmpeg `apt install ffmpeg`
5. Run with `python3.8 -m player`, stop with <kbd>CTRL</kbd>+<kbd>C</kbd>.
> It is recommended to use [virtual environments](https://docs.python-guide.org/dev/virtualenvs/) while running the app, this is a good practice you can use at any of your python projects as virtualenv creates an isolated Python environment which is specific to your project.
> You do require to manually start a voice chat on intended group where the script will be playing the files - in our case we define this chat as voice_chat on config.ini.
