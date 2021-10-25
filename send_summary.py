import os
import logging
import sys
import click

from dotenv import load_dotenv

from bot import Bot
from exchange import Exchange


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def init_dotenv():
    load_dotenv()

    token = os.getenv("TOKEN", "TOKEN")
    chat_id = os.getenv("CHAT_ID", "CHAT_ID")
    return {"token": token, "chat_id": chat_id}

@click.command()
@click.option('--pair', default="usdt", help='pair usdt/btc')
def main(pair: str):
    # load .env and unpack
    env = init_dotenv()
    
    (_pair, exchange) = getPairAndExchange(pair)
    logging.info(f"sending summary for {_pair} pairs from {exchange}")
    
    bot = Bot(token=env["token"])
    bot.send_message_to_chat(env["chat_id"], _pair, exchange)

def getPairAndExchange(pair_arg: str):
    if pair_arg.lower == "btc":
        return ("btc", Exchange.OKEX)
    else:
        return ("usdt", Exchange.BINANCE)

if __name__ == "__main__":
    main()
