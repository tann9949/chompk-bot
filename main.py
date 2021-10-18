import os
import logging
from typing import Any, Dict

from dotenv import load_dotenv

from bot import Bot


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def init_dotenv():
    load_dotenv()

    token = os.getenv("TOKEN", "TOKEN")
    return {"token": token}

def main():
    # load .env and unpack
    env = init_dotenv()

    bot = Bot(
        token=env["token"],
    )
    bot.run()


if __name__ == "__main__":
    main()
