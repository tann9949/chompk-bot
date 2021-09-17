from telegram.ext import Updater, CommandHandler

from api import BinanceAPI
from solver import Solver


class Bot:
    def __init__(self, token: str) -> None:
        self.token = token

    def run(self) -> None:
        updater = Updater(token=self.token, use_context=True)
        dispatcher = updater.dispatcher

        cdc_handler = CommandHandler("cdc", Bot.cdc_callback)
        dispatcher.add_handler(cdc_handler)

        updater.start_polling()

    @staticmethod
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
