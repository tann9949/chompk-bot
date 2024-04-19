import os

from dotenv import load_dotenv

from app.bot import Bot


def init_dotenv():
    load_dotenv()

    token = os.getenv("BOT_TOKEN", "TOKEN")
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
