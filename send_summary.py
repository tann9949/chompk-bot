import os
import logging
import click

from dotenv import load_dotenv

from app.bot import Bot
from app.enums.exchange import Exchange


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def init_dotenv():
    load_dotenv()

    token = os.getenv("TOKEN", "TOKEN")
    binance_chat_id = os.getenv("BINANCE_CHAT_ID", "BINANCE_CHAT_ID")
    okex_chat_id = os.getenv("OKEX_CHAT_ID", "OKEX_CHAT_ID")
    return {"token": token, "chat_id": { "binance": binance_chat_id, "okex": okex_chat_id }}

@click.command()
@click.option('--exchange', default="binance", help='pair binance/okex')
def main(exchange: str):
    # load .env and unpack
    env = init_dotenv()
    exchange = exchange.lower().strip()
    
    logging.info(f"sending summary from {exchange}")
    
    bot = Bot(token=env["token"])
    bot.send_message_to_chat(env["chat_id"][exchange], exchange)
    

if __name__ == "__main__":
    main()
