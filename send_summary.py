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
    usdt_chat_id = os.getenv("USDT_CHAT_ID", "USDT_CHAT_ID")
    btc_chat_id = os.getenv("BTC_CHAT_ID", "BTC_CHAT_ID")
    return {"token": token, "chat_id": { "usdt": usdt_chat_id, "btc": btc_chat_id }}

@click.command()
@click.option('--exchange', default="binance", help='pair binance/okex')
@click.option('--pair', default="binance", help='pair btc/usdt')
def main(exchange: str, pair: str):
    # load .env and unpack
    env = init_dotenv()
    
    logging.info(f"sending summary from {exchange}")
    
    bot = Bot(token=env["token"])
    bot.send_message_to_chat(env["chat_id"][pair.lower().strip()], exchange, pair.lower().strip())
    

if __name__ == "__main__":
    main()
