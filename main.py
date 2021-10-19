import os
import logging
from typing import Any, Dict

from dotenv import load_dotenv

from bot import Bot


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def init_dotenv():
    load_dotenv()

    token = os.getenv("TOKEN", "TOKEN")
    chat_id = os.getenv("CHAT_ID", "CHAT_ID")
    return {"token": token, "chat_id": chat_id}

def main():
    # load .env and unpack
    env = init_dotenv()

    bot = Bot(token=env["token"])
    # bot.send_message_to_chat(env["chat_id"])  # to directly send to chat
    bot.run()  # for listening to /dashboard


if __name__ == "__main__":
    main()
