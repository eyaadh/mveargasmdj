import shutil
import logging
import asyncio
import player.telegram
from pyrogram import idle
from player.telegram.audio_handler import start_player


async def main():
    await player.telegram.Audio_Master.start()

    while not player.telegram.Audio_Master.is_connected:
        await asyncio.sleep(1)

    await start_player()
    await idle()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt as e:
        loop.stop()
    finally:
        if player.telegram.raw_file_path:
            logging.info("Removing temporary files and closing the loop!")
            if player.telegram.raw_file_path.exists():
                shutil.rmtree(player.telegram.raw_file_path.parent)
