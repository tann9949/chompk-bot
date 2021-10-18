import logging
from datetime import time

from telegram.ext import (
    Updater, 
    CommandHandler, 
    CallbackContext,
    Dispatcher,
)
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler

from callback import CallBacks


class Bot:
    def __init__(self, token: str) -> None:
        self.token = token

    def run(self) -> None:
        logging.info(f"Starting bot...")
        updater: Updater = Updater(token=self.token, use_context=True)
        dispatcher: Dispatcher = updater.dispatcher

        # cdc_handler = CommandHandler("cdc", CallBacks.cdc_callback)
        # dispatcher.add_handler(cdc_handler)

        dispatcher.add_handler(
            MessageHandler(
                Filters.text,
                Bot.reminder,
                pass_job_queue=True
            )
        )

        updater.start_polling()
        updater.idle()

    @staticmethod
    def reminder(update: Updater, context: CallbackContext) -> None:
        context.job_queue.run_daily(
            CallBacks.dashboard_callback,
            context=update.effective.chat_id,
            days=(0, 1, 2, 3, 4, 5, 6),  # run everyday
            time=time(hour=6, minute=55, second=0)  # send at 6:55 as market close at 7:00
        )
