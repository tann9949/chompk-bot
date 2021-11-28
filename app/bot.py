import logging
import os
from datetime import datetime
from functools import partial

import telegram
from telegram.ext import CommandHandler, Dispatcher, Updater
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler

from .callback import CallBacks, get_bitcion_template, get_cdc_template
from .enums.exchange import Exchange
from .enums.pairs import Pairs


class Bot:
    def __init__(self, token: str) -> None:
        self.token: str = token

    def send_message_to_chat(self, chat_id: str, exchange: Exchange, img_path: str = "tmp.png") -> None:
        bot: telegram.Bot = telegram.Bot(token=self.token)
        logging.info("Calling Dashboard callbacks")
        
        if exchange != Exchange.BITKUB:
            cdc_usdt_template = get_cdc_template(Pairs.USDT, exchange)
            cdc_btc_template = get_cdc_template(Pairs.BTC, exchange)
            # btc_template = get_bitcion_template(img_path)

            current_time: str = f"🕒 (UTC) {datetime.strftime(datetime.now(), '%d-%m-%Y %H:%M:%S')}"
            bot.send_message(chat_id=chat_id, text=current_time)
            bot.send_message(chat_id=chat_id, text=cdc_usdt_template)
            bot.send_message(chat_id=chat_id, text=cdc_btc_template)
        else:
            cdc_thb_template = get_cdc_template(Pairs.THB, exchange)
            # btc_template = get_bitcion_template(img_path)

            current_time: str = f"🕒 (UTC) {datetime.strftime(datetime.now(), '%d-%m-%Y %H:%M:%S')}"
            bot.send_message(chat_id=chat_id, text=current_time)
            bot.send_message(chat_id=chat_id, text=cdc_thb_template)
        
        # bot.send_message(chat_id=chat_id, text=btc_template)
        # bot.send_photo(chat_id=chat_id, photo=open(img_path, "rb"))
        # os.remove(img_path)
        
        # donate_template: str = "Buy developers some coffee ☕ or tea 🍵 :" + \
        #     "(BEP-20 / ERC-20)" + \
        #     "    0xc7b16d2e1cDB9FD6B59A55e110D75d8aADA446E0\n" + \
        #     "\nAny donation is appreciated 🤗" + \
        #     "\nHave a great day!" + \
        #     '\n\n"Comes for the price. Stay for the principle" - The legendary Piranya33 🐟'
        # bot.send_message(chat_id=chat_id, text=donate_template)

    def run(self) -> None:
        logging.info(f"Starting bot...")
        updater: Updater = Updater(token=self.token, use_context=True)
        dispatcher: Dispatcher = updater.dispatcher

        dispatcher.add_handler(
            CommandHandler(
                "dashboard",
                CallBacks.dashboard_callback
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "cdc",
                CallBacks.cdc_callback
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "cdcaction",
                partial(CallBacks.cdc_callback, is_current=False)
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "open_interest",
                partial(CallBacks.open_interest_callback)
            )
        )

        updater.start_polling()
        updater.idle()
