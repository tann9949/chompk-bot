import logging
from datetime import datetime
from typing import Dict

import numpy as np
import pandas as pd
from telegram.ext import (
    Updater, 
    CallbackContext,
)

from api import (
    BinanceAPI,
    CoinGecko,
    TheBlockAPI,
    AltcoinIndexAPI,
    FearAndGreedAPI
)
from solver import Solver


class CallBacks:
    @staticmethod
    def dashboard_callback(update: Updater, context: CallbackContext) -> None:
        """
        TODO:
        - Plot fear and greed + open interest + altcoin season index + bitcoin dominance
        - show value fear and greed, open interest, altcoin season index, bitcoin dominance
        - show Pairs that CDC Action zone will have buy/sell or buy more/sell more signal
        """
        logging.info("Calling Dashboard callbacks")
        usdt_tickers = BinanceAPI.get_usdt_tickers()
        # usdt_tickers = ["SKLUSDT", "EOSUSDT"]

        buy_tickers = []
        sell_tickers = []
        buymore_tickers = []
        sellmore_tickers = []
        for ticker in usdt_tickers:
            candle_data = BinanceAPI.generate_candle_data(ticker)
            signal = Solver.get_cdc_signal(candle_data["close"])
            logging.info(f"Ticker ({ticker}) is {signal}")

            if signal == "buy":
                buy_tickers.append(ticker)
            elif signal == "sell":
                sell_tickers.append(ticker)
            elif signal == "buy more":
                buymore_tickers.append(ticker)
            elif signal == "sell more":
                sellmore_tickers.append(ticker)

        btc_dominance: float = CoinGecko.get_btc_dominance()
        open_interest: Dict[str, pd.Series] = TheBlockAPI.get_open_interset()
        altcoin_index: pd.Series = AltcoinIndexAPI.get_historical_altcoin_index()
        fear_and_greed: pd.Series = FearAndGreedAPI.get_historical_data()

        current_time: str = f"{datetime.strftime(datetime.now(), '%d-%m-%Y %H:%M:%S')}"
        cdc_template: str = f"CDC Action Zone V3 \n\n" + \
            "Buy Next Bar 🟢\n" + \
            f"{' '.join(buy_tickers)}\n\n" + \
            "Sell Next Bar 🔴\n" + \
            f"{' '.join(sell_tickers)}\n\n"
        
        aggregated_oi: np.ndarray = np.array([
            x.values 
            for x in open_interest.values()
        ]).sum(0)
        oi_gain: float = (aggregated_oi[-1] - aggregated_oi[-2]) / aggregated_oi[-2]
        oi_gain_fmt: str = f"+{oi_gain*100:.2f}" if oi_gain > 0 else f"{oi_gain*100:.2f}"

        altcoin_idx_gain: float = (float(altcoin_index[-1]) - float(altcoin_index[-2])) / float(altcoin_index[-2])
        altcoin_idx_gain_fmt: str = f"+{altcoin_idx_gain*100:.2f}" if altcoin_idx_gain > 0 else f"{altcoin_idx_gain*100:.2f}"

        fng_gain: float = (fear_and_greed[-1] - fear_and_greed[-2]) / fear_and_greed[-2]
        fng_gain_fmt: str = f"+{fng_gain*100:.2f}" if fng_gain > 0 else f"{fng_gain*100:.2f}"
        btc_template: str = f"(₿) Bitcoin Dashboard\n\n" + \
            f"Bitcoin Dominance:\n" + \
            f"    {btc_dominance:.2f}%\n" + \
            f"Aggregated Open Interest:\n" + \
            f"    ${aggregated_oi[-1]:,} ({oi_gain_fmt}%)\n" + \
            f"Fear and Greed Index\n" + \
            f"    {fear_and_greed[-1]} ({fng_gain_fmt}%)\n" + \
            f"Altcoin Index:\n" + \
            f"    {altcoin_index[-1]} ({altcoin_idx_gain_fmt}%)\n"

        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=current_time
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=cdc_template
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=btc_template
        )

    @staticmethod
    def cdc_callback(update: Updater, context: CallbackContext) -> None:
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

            logging.info(f"computing {symbol} pair...")

            try:
                candle_data = BinanceAPI.generate_candle_data(symbol, interval)
                _, template = Solver.solve_cdc_cross(candle_data["close"])
                context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=template
                )
            except AssertionError as e:
                logging.info(f"cannot compute with the following error message:\n{e}")
                context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=f"Unrecognize pair name `{symbol}` on Binance"
                )
