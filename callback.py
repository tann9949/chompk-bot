import logging
from datetime import datetime
import os
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from telegram.ext import CallbackContext, Updater

from api import (AltcoinIndexAPI, BinanceAPI, CoinGecko, FearAndGreedAPI,
                 TheBlockAPI)
from solver import Solver
from technical_analysis import TechnicalAnalysis as ta
from utils import send_message, send_photo


class CallBacks:
    @staticmethod
    def dashboard_callback(update: Updater, context: CallbackContext) -> None:
        """
        - Plot fear and greed + open interest + altcoin season index + bitcoin dominance
        - show value fear and greed, open interest, altcoin season index, bitcoin dominance
        - show Pairs that CDC Action zone will have buy/sell or buy more/sell more signal
        """
        logging.info("Calling Dashboard callbacks")
        usdt_tickers = BinanceAPI.get_usdt_tickers()

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
        logging.info("Fetching BTC Price...")
        btcusdt: pd.DataFrame = BinanceAPI.generate_candle_data("BTCUSDT")
        logging.info("Fetching Altcoin Index...")
        oi: Dict[str, pd.Series] = TheBlockAPI.get_open_interset()
        logging.info("Fetching Fear and Greed Index...")
        altcoin_idx: pd.Series = AltcoinIndexAPI.get_historical_altcoin_index()
        logging.info("Fetching Bitcoin Aggregated Open Interest...")
        fng_idx: pd.Series = FearAndGreedAPI.get_historical_data()
        logging.info("Finish fetching!")

        smooth_alt_idx = pd.Series(ta.sma(altcoin_idx, 2), index=altcoin_idx.index, name="Altcoin Season Index")
        aggregated_oi: pd.Series = pd.Series(
            np.array([
                x.resample("1D").mean().values 
                for x in oi.values()
            ]).sum(0),
            index=oi["Binance"].resample("1D").mean().index,
            name="Aggregated Open Interest"
        )

        current_time: str = f"{datetime.strftime(datetime.now(), '%d-%m-%Y %H:%M:%S')}"
        cdc_template: str = f"CDC Action Zone V3 \n\n" + \
            "Buy Next Bar 🟢\n" + \
            f"{' '.join(buy_tickers)}\n\n" + \
            "Sell Next Bar 🔴\n" + \
            f"{' '.join(sell_tickers)}\n\n" + \
            "Buy More Next Bar 🔼\n" + \
            f"{' '.join(buymore_tickers)}\n\n" + \
            "Sell More Next Bar 🔽\n" + \
            f"{' '.join(sellmore_tickers)}\n\n"
            
        oi_gain: float = (aggregated_oi[-1] - aggregated_oi[-2]) / aggregated_oi[-2]
        oi_gain_fmt: str = f"+{oi_gain*100:.2f}" if oi_gain > 0 else f"{oi_gain*100:.2f}"

        altcoin_idx_gain: float = (float(altcoin_idx[-1]) - float(altcoin_idx[-2])) / float(altcoin_idx[-2])
        altcoin_idx_gain_fmt: str = f"+{altcoin_idx_gain*100:.2f}" if altcoin_idx_gain > 0 else f"{altcoin_idx_gain*100:.2f}"
        season: str = ""
        if altcoin_idx[-1] >= 75: # alt party
            season = "It's Alt Party! 🥳"
        elif altcoin_idx[-1] <= 25:
            season = "It's Bitcon Season! 🤩"
        else:
            season = "It's nothing season... 😴"

        fng_gain: float = (fng_idx[-1] - fng_idx[-2]) / fng_idx[-2]
        fng_gain_fmt: str = f"+{fng_gain*100:.2f}" if fng_gain > 0 else f"{fng_gain*100:.2f}"
        fng: str = ""
        if fng_idx[-1] > 65:  # extreme greed
            fng = "Extreme Greed 🤑" 
        elif 55 < fng_idx[-1] < 65: # greed
            fng = "Greed 🥴"
        elif 45 < fng_idx[-1] < 55: # neutral
            fng = "Neutral 🥱"
        elif 35 < fng_idx[-1] < 45: # fear
            fng = "Fear 🤔"
        else: # extreme fear
            fng = "Extreme Fear 😱"

        btc_template: str = f"(₿) Bitcoin Dashboard\n\n" + \
            f"💪🏻 Bitcoin Dominance:\n" + \
            f"    {btc_dominance:.2f}%\n\n" + \
            f"💰 Aggregated Open Interest:\n" + \
            f"    ${aggregated_oi[-1]:,} ({oi_gain_fmt}%)\n\n" + \
            f"Fear and Greed Index\n" + \
            f"    {fng_idx[-1]} ({fng_gain_fmt}%)\n" + \
            f"    {fng}\n\n" + \
            f"Altcoin Index:\n" + \
            f"    {altcoin_idx[-1]} ({altcoin_idx_gain_fmt}%)\n" + \
            f"    {season}\n"

        dataset = btcusdt[["close"]].join(smooth_alt_idx).join(fng_idx).join(aggregated_oi)
        generate_image(dataset.iloc[-300:], "tmp.png")

        send_message(
            update,
            context,
            message=current_time
        )
        send_message(
            update,
            context,
            message=cdc_template
        )
        send_photo(
            update,
            context,
            "tmp.png"
        )
        send_message(
            update,
            context,
            message=btc_template
        )
        os.remove("tmp.png")

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


def generate_image(data: pd.DataFrame, save_path: str) -> None:
    current_time: str = f"{datetime.strftime(datetime.now(), '%d-%m-%Y %H:%M:%S')}"
    fig = plt.figure(figsize=(10, 10))
    gs = fig.add_gridspec(3, hspace=0)
    axs = gs.subplots(sharex=True)
    fig.suptitle(f'Bitcoin Dashboard\n{current_time}', fontweight="bold", fontsize=24)

    # aggregated open interest
    iterator = [
        ("Altcoin Season Index", "red"),
        ("Fear and Greed Index", "green"),
        ("Aggregated Open Interest", "blue"),
    ]
    for i, (col, color) in enumerate(iterator):
        axs[i].plot(data.index, data[col].values, label=col, color=color)
        axs[i].get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, p: format(int(x), ','))
        )
        
        ax2 = axs[i].twinx()
        if i == 0:
            ax2.plot(data.index, data["close"].values, color="orange", alpha=0.7, label="BTCUSDT")
        else:
            ax2.plot(data.index, data["close"].values, color="orange", alpha=0.7)
        ax2.get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, p: format(int(x), ','))
        )
    for ax in axs:
        ax.label_outer()

    fig.legend(loc="lower right", bbox_to_anchor=(1.22, 0.45))
    plt.savefig(save_path)
