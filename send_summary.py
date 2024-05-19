import asyncio
import os
import os.path
import sys

import click
from dotenv import load_dotenv
from loguru import logger

from app.bot import Bot

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def init_dotenv():
    load_dotenv()

    token = os.getenv("TOKEN", "TOKEN")
    binance_chat_id = os.getenv("BINANCE_CHAT_ID", "BINANCE_CHAT_ID")
    okex_chat_id = os.getenv("OKEX_CHAT_ID", "OKEX_CHAT_ID")
    kucoin_chat_id = os.getenv("KUCOIN_CHAT_ID", "KUCOIN_CHAT_ID")
    bitkub_chat_id = os.getenv("BITKUB_CHAT_ID", "BITKUB_CHAT_ID")
    return {
        "token": token,
        "chat_id": {
            "binance": binance_chat_id,
            "okex": okex_chat_id,
            "kucoin": kucoin_chat_id,
            "bitkub": bitkub_chat_id,
        }
    }


@click.command()
@click.option('--exchange', default="binance", help='pair binance/okex')
def main(exchange: str):
    # load .env and unpack
    env = init_dotenv()
    exchange = exchange.lower().strip()

    logger.info(f"sending summary from {exchange}")

    bot = Bot(token=env["token"])

    asyncio.run(bot.send_message_to_chat(env["chat_id"][exchange], exchange))


if __name__ == "__main__":
    main()
