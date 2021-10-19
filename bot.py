import logging
from datetime import datetime
import os
import telegram

from telegram.ext import (
    Updater, 
    Dispatcher,
    CommandHandler
)
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler

from callback import (
    CallBacks,
    get_bitcion_template,
    get_cdc_tickers
)


class Bot:
    def __init__(self, token: str) -> None:
        self.token: str = token

    def send_message_to_chat(self, chat_id: str, img_path: str = "tmp.png") -> None:
        bot: telegram.Bot = telegram.Bot(token=self.token)
        logging.info("Calling Dashboard callbacks")
        
        current_time: str = f"{datetime.strftime(datetime.now(), '%d-%m-%Y %H:%M:%S')}"
        # cdc_template = get_cdc_tickers()
        btc_template = get_bitcion_template(img_path)

        # bot.send_message(chat_id=chat_id, text=current_time)
        # bot.send_message(chat_id=chat_id, text=cdc_template)
        # bot.send_message(chat_id=chat_id, text=btc_template)
        bot.send_photo(chat_id=chat_id, photo=open(img_path, "rb"))
        os.remove(img_path)

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
            MessageHandler(
                Filters.text,
                Bot.reminder,
                pass_job_queue=True
            )
        )

        updater.start_polling()
        updater.idle()
