import os
import logging
from typing import Any, Dict

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler

from api import BinanceAPI
from solver import Solver

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def cdc_callback(update, context) -> None:
    args = context.args

    if len(args) > 1:
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Please parse only one argument!"
        )
    else:
        coin: str = args[0].upper().strip()

        symbol = coin+"USDT"
        interval = "1d"

        try:
            candle_data = BinanceAPI.generate_candle_data(symbol, interval)
            _, template = Solver.solve_cdc_cross(candle_data)
            context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=template
            )
        except AssertionError:
            context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=f"Unrecognize pair name `{symbol}` on Binance"
            )


def init_dotenv() -> Dict[str, Any]:
    load_dotenv()

    token = os.getenv("TOKEN", "TOKEN")
    return {"token": token}

def main():
    # load .env and unpack
    env = init_dotenv()
    TOKEN = env["token"]

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    cdc_handler = CommandHandler("cdc", cdc_callback)
    dispatcher.add_handler(cdc_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
