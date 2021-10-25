import os
import logging
import sys

from dotenv import load_dotenv

from bot import Bot
from exchange import Exchange


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def init_dotenv():
    load_dotenv()

    token = os.getenv("TOKEN", "TOKEN")
    chat_id = os.getenv("CHAT_ID", "CHAT_ID")
    return {"token": token, "chat_id": chat_id}

def main():
    # load .env and unpack
    env = init_dotenv()
    pair_arg = sys.argv[1]
    
    (pair, exchange) = getPairAndExchange(pair_arg)
    logging.info(f"sending summary for {pair} pairs from {exchange}")
    
    bot = Bot(token=env["token"])
    bot.send_message_to_chat(env["chat_id"], pair, exchange)

def getPairAndExchange(pair_arg: str):
    if pair_arg.lower == "btc":
        return ("btc", Exchange.OKEX)
    else:
        return ("usdt", Exchange.BINANCE)

if __name__ == "__main__":
    main()
