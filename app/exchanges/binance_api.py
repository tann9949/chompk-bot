import json
from datetime import datetime
from typing import List

import pandas as pd
import requests
from loguru import logger

from app.exchanges.base_exchange import ExchangeAPI


class BinanceAPI(ExchangeAPI):
    base_url: str = "https://api.binance.com"

    @staticmethod
    def format_unixtime(unix_time: int):
        return datetime.utcfromtimestamp(int(str(unix_time)[:-3]))

    @staticmethod
    def generate_candle_data(symbol: str, interval: str = "1d") -> pd.DataFrame:
        r = requests.get(
            f"{BinanceAPI.base_url}/api/v3/klines",
            {"symbol": symbol, "interval": interval},
        )
        klines = json.loads(r.text)
        candle_data = []
        timestamp = []
        for line in klines:
            assert len(line) == 12, f"{symbol}: {len(line)}"
            open_time = BinanceAPI.format_unixtime(line[0])
            timestamp.append(open_time)
            # end_time = datetime.utcfromtimestamp(line[6])
            volume = line[5]
            high, low, op, close = line[2], line[3], line[1], line[4]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(
            candle_data,
            columns=["open", "close", "high", "low", "volume"],
            index=timestamp,
        )
        return candle_data.astype(float)

    @staticmethod
    def get_usdt_tickers() -> List[str]:
        r = requests.get(f"{BinanceAPI.base_url}/api/v3/ticker/price")
        logger.debug("binance response:", r)
        tickers = json.loads(r.text)
        return [
            ticker["symbol"]
            for ticker in tickers
            if (
                ticker["symbol"][:4] != "USDT"
                and "USDT" in ticker["symbol"]
                and "UP" not in ticker["symbol"]
                and "DOWN" not in ticker["symbol"]
                and "BEAR" not in ticker["symbol"]
                and "BULL" not in ticker["symbol"]
                and ticker["symbol"].count("USD") == 1
                and "DAI" not in ticker["symbol"]
            )
        ]

    @staticmethod
    def get_btc_tickers() -> List[str]:
        r = requests.get(f"{BinanceAPI.base_url}/api/v3/ticker/price")
        tickers = json.loads(r.text)
        return [
            ticker["symbol"]
            for ticker in tickers
            if (
                ticker["symbol"][:3] != "BTC"
                and "USD" not in ticker["symbol"]
                and "BTC" in ticker["symbol"]
                and "DOWN" not in ticker["symbol"]
                and "BEAR" not in ticker["symbol"]
                and "BULL" not in ticker["symbol"]
                and "DAI" not in ticker["symbol"]
                and ticker["symbol"].count("BTC") == 1
            )
        ]
