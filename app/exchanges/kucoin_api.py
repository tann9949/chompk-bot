import json
import logging
import time
from datetime import datetime
from typing import List

import pandas as pd
import requests

from app.exchanges.base_exchange import ExchangeAPI


class KucoinAPI(ExchangeAPI):
    base_url: str = "https://api.kucoin.com"

    @staticmethod
    def generate_candle_data(
            symbol: str,
            interval: str = "1day",
            max_attempt: int = 10) -> pd.DataFrame:
        r = requests.get(f"{KucoinAPI.base_url}/api/v1/market/candles", {"symbol": symbol, "type": interval})
        klines = json.loads(r.text)

        n_attempt = 0
        while klines["code"] != "200000":
            if n_attempt > max_attempt:
                return None

            logging.warning(f"Error fetching API. Retrying in 0.1 seconds")

            time.sleep(0.1)
            r = requests.get(f"{KucoinAPI.base_url}/api/v1/market/candles", {"symbol": symbol, "type": interval})
            klines = json.loads(r.text)
            n_attempt += 1

        candle_data = []
        timestamp = []
        for l in klines["data"]:
            open_time = (datetime.utcfromtimestamp(int(l[0])).strftime('%Y-%m-%d %H:%M:%S'))
            timestamp.append(open_time)
            # end_time = datetime.utcfromtimestamp(l[6])
            volume = l[5]
            high, low, op, close = l[3], l[4], l[1], l[2]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(candle_data, columns=["open", "close", "high", "low", "volume"], index=timestamp)
        return candle_data.astype(float)[::-1]

    @staticmethod
    def get_usdt_tickers() -> List[str]:
        r = requests.get(f"{KucoinAPI.base_url}/api/v1/symbols")
        tickers = json.loads(r.text)
        return [
            ticker["symbol"]
            for ticker in tickers["data"]
            if (
                    ticker["symbol"][:4] != "USDT"
                    and "USDT" in ticker["symbol"]
                    and "UP" not in ticker["symbol"]
                    and "DOWN" not in ticker["symbol"]
                    and "BEAR" not in ticker["symbol"]
                    and "BULL" not in ticker["symbol"]
                    and "3L" not in ticker["symbol"]
                    and "3S" not in ticker["symbol"]
                    and ticker["symbol"].count("USD") == 1
                    and "DAI" not in ticker["symbol"]
            )
        ]

    @staticmethod
    def get_btc_tickers() -> List[str]:
        r = requests.get(f"{KucoinAPI.base_url}/api/v1/symbols")
        tickers = json.loads(r.text)
        return [
            ticker["symbol"]
            for ticker in tickers["data"]
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
