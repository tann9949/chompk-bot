import json
from datetime import datetime
from typing import Dict, List

import pandas as pd
import requests

from exchanges.base_exchange import ExchangeAPI


class FtxAPI(ExchangeAPI):
    base_url: str = "https://ftx.com/api"
    reso_mapping: Dict[str, int] = {
        "15min": 900,
        "30min": 1800,
        "1h": 3600,
        "4h": 14400,
        "12h": 43200,
        "1d": 86400,
        "1W": 604800,
        "1M": 2678400
    }

    @staticmethod
    def generate_candle_data(
            market_name: str,
            resolution: str = "1d") -> pd.DataFrame:
        timeframe = FtxAPI.reso_mapping[resolution]

        url: str = f"{FtxAPI.base_url}/markets/{market_name}/candles?resolution={timeframe}"  # &start_time={start_time}&end_time={end_time}"
        r = requests.get(url)

        klines = json.loads(r.text)["result"]

        candle_data = []
        timestamp = []
        for line in klines:
            open_time = datetime.strptime(line["startTime"], "%Y-%m-%dT%H:%M:%S+00:00")
            timestamp.append(open_time)
            volume = line["volume"]
            high, low, op, close = line["high"], line["low"], line["open"], line["close"]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(candle_data, columns=["open", "close", "high", "low", "volume"], index=timestamp)
        return candle_data.astype(float).resample("1D").mean()

    @staticmethod
    def get_usdt_tickers() -> List[str]:
        r = requests.get(f"{FtxAPI.base_url}/markets")
        tickers = json.loads(r.text)
        return [
            ticker["name"]
            for ticker in tickers["result"]
            if (
                    ticker["name"][:3] != "USD"
                    and "USD" in ticker["name"]
                    and "USDT" not in ticker["name"]
                    and "UP" not in ticker["name"]
                    and "DOWN" not in ticker["name"]
                    and "HALF/" not in ticker["name"]
                    and "HEDGE/" not in ticker["name"]
                    and "BEAR" not in ticker["name"]
                    and "BULL" not in ticker["name"]
                    and ticker["name"].count("USD") == 1
                    and "DAI" not in ticker["name"]
            )
        ]

    @staticmethod
    def get_perp_tickers() -> List[str]:
        r = requests.get(f"{FtxAPI.base_url}/markets")
        tickers = json.loads(r.text)
        return [
            ticker["name"]
            for ticker in tickers["result"]
            if "PERP" in ticker["name"]
        ]

    @staticmethod
    def get_btc_tickers() -> List[str]:
        r = requests.get(f"{FtxAPI.base_url}/markets")
        tickers = json.loads(r.text)

        return [
            ticker["name"]

            for ticker in tickers["result"]
            if (
                    ticker["name"][:3] != "BTC"
                    and "USD" not in ticker["name"]
                    and "BTC" in ticker["name"]
                    and "UP" not in ticker["name"]
                    and "DOWN" not in ticker["name"]
                    and "BEAR" not in ticker["name"]
                    and "BULL" not in ticker["name"]
                    and ticker["name"].count("BTC") == 1
                    and "DAI" not in ticker["name"]
                    and "-" not in ticker["name"]
            )
        ]
