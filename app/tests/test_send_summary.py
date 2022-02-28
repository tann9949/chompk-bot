import os

from dotenv import load_dotenv

from app.bot import Bot


def test_initenv():
    global env
    load_dotenv()

    token = os.getenv("TOKEN", "TOKEN")
    binance_chat_id = os.getenv("BINANCE_CHAT_ID", "BINANCE_CHAT_ID")
    okex_chat_id = os.getenv("OKEX_CHAT_ID", "OKEX_CHAT_ID")
    ftx_chat_id = os.getenv("FTX_CHAT_ID", "FTX_CHAT_ID")
    kucoin_chat_id = os.getenv("KUCOIN_CHAT_ID", "KUCOIN_CHAT_ID")
    bitkub_chat_id = os.getenv("BITKUB_CHAT_ID", "BITKUB_CHAT_ID")
    env = {
        "token": token,
        "chat_id": {
            "binance": binance_chat_id,
            "okex": okex_chat_id,
            "ftx": ftx_chat_id,
            "kucoin": kucoin_chat_id,
            "bitkub": bitkub_chat_id,
        }
    }


def test_okex():
    exchange = "okex"
    bot = Bot(token=env["token"])
    bot.send_message_to_chat(env["chat_id"][exchange], exchange)


def test_bitkub():
    exchange = "bitkub"
    bot = Bot(token=env["token"])
    bot.send_message_to_chat(env["chat_id"][exchange], exchange)


def test_binance():
    exchange = "binance"
    bot = Bot(token=env["token"])
    bot.send_message_to_chat(env["chat_id"][exchange], exchange)


def test_ftx():
    exchange = "ftx"
    bot = Bot(token=env["token"])
    bot.send_message_to_chat(env["chat_id"][exchange], exchange)


def test_kucoin():
    exchange = "kucoin"
    bot = Bot(token=env["token"])
    bot.send_message_to_chat(env["chat_id"][exchange], exchange)
