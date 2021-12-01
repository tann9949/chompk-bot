import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from telegram.ext import CallbackContext, Updater

from .api import (AltcoinIndexAPI, BinanceAPI, BitkubAPI, ByBtAPI, CoinGecko,
                  FearAndGreedAPI, FtxAPI, KucoinAPI, OkexAPI)
from .enums.exchange import Exchange
from .enums.pairs import Pairs
from .solver import Solver
from .technical_analysis import TechnicalAnalysis as ta
from .utils import send_message, send_photo


class CallBacks:
    @staticmethod
    def dashboard_callback(
        update: Updater, 
        context: CallbackContext, 
        img_path: str = "tmp.png", 
        chat_id: Optional[str] = None) -> None:
        """
        - Plot fear and greed + open interest + altcoin season index + bitcoin dominance
        - show value fear and greed, open interest, altcoin season index, bitcoin dominance
        - show Pairs that CDC Action zone will have buy/sell or buy more/sell more signal
        """
        logging.info("Calling Dashboard callbacks")
        chat_id: str = update.effective_chat.id if chat_id is None else chat_id
        
        current_time: str = f"{datetime.strftime(datetime.now(), '%d-%m-%Y %H:%M:%S')}"
        btc_template = get_bitcion_template(img_path)

        send_message(
            chat_id,
            context,
            message=current_time
        )
        send_photo(
            chat_id,
            context,
            img_path
        )
        send_message(
            update.effective_chat.id,
            context,
            message=btc_template
        )
        os.remove(img_path)

    @staticmethod
    def open_interest_callback(
        update: Updater,
        context: CallbackContext,
        img_path: str = "oi.png",
    ) -> None:
        args: List[str] = context.args
        if len(args) != 1:
            send_message(update.effective_chat.id, context, "Please parse exchange as an argument!")
            return

        exchange: str = args[0].lower().strip()
        oi_data: Dict[str, pd.Series] = ByBtAPI.get_open_interest()
        if exchange not in oi_data.keys():
            send_message(update.effective_chat.id, context, f"Unrecognize exchange: {exchange}")
            return
        oi: pd.Series = oi_data[exchange][-300:]
        
        logging.info(f"Calling Open Interest Callback on {exchange}")

        # format text
        oi_gain: float = (oi[-1] - oi[-2]) / oi[-2]
        oi_gain_fmt: str = f"+{oi_gain*100:.2f}" if oi_gain > 0 else f"{oi_gain*100:.2f}"

        exchange = exchange[0].upper() + exchange[1:]
        template = f"💰 {exchange} Future Open Interest:\n" + \
        f"    ${oi[-1]:,} ({oi_gain_fmt}%)\n\n"

        # format image
        btcusdt: pd.Series = BinanceAPI.generate_candle_data("BTCUSDT")["close"][-300:]
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(oi.index, oi.values)
        ax.axhline(oi[-1], linestyle="--", alpha=0.4, color="black", label="Future Open Interest (USD)")
        ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, p: format(int(x), ','))
        )

        ax2 = ax.twinx()
        ax2.plot(btcusdt.index, btcusdt.values, color="orange", alpha=0.7, label="BTCUSDT (close)")
        ax2.axhline(btcusdt.values[-1], linestyle="--", alpha=0.2, color="brown")
        ax2.get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, p: format(int(x), ','))
        )

        ax.label_outer()
        fig.suptitle(f'{exchange} Open Interest', fontweight="bold", fontsize=24)
        lgd = fig.legend()
        plt.savefig(img_path, bbox_extra_artists=(lgd,), bbox_inches='tight')

        send_photo(update.effective_chat.id, context, img_path)
        send_message(update.effective_chat.id, context, template)
        os.remove(img_path)

    @staticmethod
    def cdc_callback(update: Updater, context: CallbackContext, is_current: bool = True) -> None:
        args = context.args
        if len(args) == 0:
            pair = "usdt"
        else:
            pair = args[0].lower().strip()
        if pair not in ["usdt", "btc"]:
            send_message(update.effective_chat.id, context, f"Unrecognized argument: {pair}. Only usdt|btc available")
            return

        
        send_message(
            update.effective_chat.id,
            context,
            message=f"Computing XXX{pair.upper()} pairs. This could take a few minutes 🙇‍♂️ ..."
        )
        template = get_cdc_template(pair, current=is_current)
        send_message(
            update.effective_chat.id,
            context,
            message=template
        )
        if pair == "btc":
            template = get_cdc_template(pair, Exchange.OKEX, is_current)
            send_message(
                update.effective_chat.id,
                context,
                message=template
            )

    @staticmethod
    def solve_cdc_callback(update: Updater, context: CallbackContext) -> None:
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
        latest_value = None
        for d in data[col].values[::-1]:
            if d == d:
                latest_value = d
                break
        axs[i].axhline(latest_value, linestyle="--", alpha=0.4, color="black")
        axs[i].get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, p: format(int(x), ','))
        )
        
        ax2 = axs[i].twinx()
        if i == 0:
            ax2.plot(data.index, data["close"].values, color="orange", alpha=0.7, label="BTCUSDT (close)")
        else:
            ax2.plot(data.index, data["close"].values, color="orange", alpha=0.7)
        ax2.axhline(data["close"].values[-1], linestyle="--", alpha=0.2, color="brown")
        ax2.get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, p: format(int(x), ','))
        )
    for ax in axs:
        ax.label_outer()

    lgd = fig.legend(loc="lower right", bbox_to_anchor=(1.22, 0.45))
    plt.savefig(save_path, bbox_extra_artists=(lgd,), bbox_inches='tight')


def get_cdc_template(
    pair: str = "usdt", 
    exchange: Exchange = Exchange.BINANCE,
    current: bool = True) -> str:
    if exchange == Exchange.OKEX:
        tickers = OkexAPI.get_usdt_tickers() if pair == "usdt" else OkexAPI.get_btc_tickers()
    elif exchange == Exchange.BINANCE:
        tickers = BinanceAPI.get_usdt_tickers() if pair == "usdt" else BinanceAPI.get_btc_tickers()
    elif exchange == Exchange.FTX:
        tickers = FtxAPI.get_usdt_tickers() if pair == "usdt" else FtxAPI.get_btc_tickers()
    elif exchange == Exchange.KUCOIN:
        tickers = KucoinAPI.get_usdt_tickers() if pair == "usdt" else KucoinAPI.get_btc_tickers()
    elif exchange == Exchange.BITKUB:
        assert pair == Pairs.THB
        tickers = BitkubAPI.get_thb_tickers()
        

    tickers = sorted(tickers)

    buy_tickers = []
    sell_tickers = []
    buymore_tickers = []
    sellmore_tickers = []
    for ticker in tickers:
        if exchange == Exchange.OKEX:
            candle_data = OkexAPI.generate_candle_data(ticker)
        elif exchange == Exchange.FTX:
            candle_data = FtxAPI.generate_candle_data(ticker)
        elif exchange == Exchange.BINANCE:
            candle_data = BinanceAPI.generate_candle_data(ticker)
        elif exchange == Exchange.KUCOIN:
            candle_data = KucoinAPI.generate_candle_data(ticker)
        elif exchange == Exchange.BITKUB:
            candle_data = BitkubAPI.generate_candle_data(ticker)
        else:
            raise KeyError(f"Unknown exchange: {exchange}")
        
        if candle_data is None:
            continue

        signal = Solver.get_cdc_signal(candle_data["close"], current=current)
        logging.info(f"Ticker ({ticker}) is {signal}")

        if signal == "buy":
            buy_tickers.append(re.sub(r"-|/|_", "", ticker))
        elif signal == "sell":
            sell_tickers.append(re.sub(r"-|/|_", "", ticker))
        elif signal == "buy more":
            buymore_tickers.append(re.sub(r"-|/|_", "", ticker))
        elif signal == "sell more":
            sellmore_tickers.append(re.sub(r"-|/|_", "", ticker))

    cdc_template: str = f"[{exchange.upper()}]\n" + \
        f"CDC Action Zone V3 \n\n" + \
        "(Buy Next Bar) - buy now! 🟢\n" + \
        f"{' '.join(buy_tickers)}\n\n" + \
        "(Sell Next Bar) - sell now! 🔴\n" + \
        f"{' '.join(sell_tickers)}\n\n" + \
        "(Buy More Next Bar) - buy the dip / take long position now! 🔼\n" + \
        f"{' '.join(buymore_tickers)}\n\n" + \
        "(Sell More Next Bar) -  short now! 🔽\n" + \
        f"{' '.join(sellmore_tickers)}\n\n"

    return cdc_template


def get_bitcion_template(img_path: str) -> str:
    btc_dominance: float = CoinGecko.get_btc_dominance()
    logging.info("Fetching BTC Price...")
    btcusdt: pd.DataFrame = BinanceAPI.generate_candle_data("BTCUSDT")
    logging.info("Fetching Altcoin Index...")
    oi: Dict[str, pd.Series] = ByBtAPI.get_open_interest()
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
        index=oi["binance"].resample("1D").mean().index,
        name="Aggregated Open Interest"
    )

        
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
        f"Bitcoin Price\n" + \
        f"    ${btcusdt['close'].iloc[-1]:,.2f}\n\n" + \
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
    generate_image(dataset.iloc[-300:], img_path)
    return btc_template
