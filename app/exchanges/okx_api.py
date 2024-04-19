import json
from datetime import datetime
from typing import Dict, List

import pandas as pd
import requests

from app.exchanges.base_exchange import ExchangeAPI


class OkxAPI(ExchangeAPI):
    base_url: str = "https://www.okx.com"
    gran_mapping: Dict[str, int] = {
        "15min": 900,
        "30min": 1800,
        "1h": 3600,
        "4h": 14400,
        "12h": 43200,
        "1D": 86400,
        "1W": 604800,
        "1M": 2678400
    }

    def format_unixtime(unix_time: int):
        return datetime.utcfromtimestamp(int(str(unix_time)[:-3]))

    @staticmethod
    def generate_candle_data(
            instrument_id: str,
            granularity: str = "1D") -> pd.DataFrame:
        timeframe = OkxAPI.gran_mapping[granularity]
        payload = {'instId': instrument_id, 'bar': '1D'}

        r = requests.get(f"{OkxAPI.base_url}/api/v5/market/history-candles", params=payload)

        klines = json.loads(r.text)['data']
        # print(klines)
        candle_data = []
        timestamp = []
        for l in klines:
            open_time = OkxAPI.format_unixtime(l[0])
            timestamp.append(open_time)
            volume = l[5]
            high, low, op, close = l[2], l[3], l[1], l[4]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(candle_data, columns=["open", "close", "high", "low", "volume"], index=timestamp)
        return candle_data.astype(float).resample("1D").mean()

    @staticmethod
    def get_usdt_tickers() -> List[str]:
        r = requests.get(f"{OkxAPI.base_url}/api/v5/market/tickers?instType=SPOT")
        tickers = json.loads(r.text)['data']

        return [
            ticker["instId"]
            for ticker in tickers
            if (
                    ticker["instId"][:3] != "USDT"
                    and "USDT" in ticker["instId"]
                    and "DOWN" not in ticker["instId"]
                    and "BEAR" not in ticker["instId"]
                    and "BULL" not in ticker["instId"]
                    and "DAI" not in ticker["instId"]
                    and ticker["instId"].count("USDT") == 1
            )
        ]

    @staticmethod
    def get_btc_tickers() -> List[str]:
        r = requests.get(f"{OkxAPI.base_url}/api/v5/market/tickers?instType=SPOT")
        tickers = json.loads(r.text)['data']

        return [
            ticker["instId"]
            for ticker in tickers
            if (
                    ticker["instId"][:3] != "BTC"
                    and "USD" not in ticker["instId"]
                    and "BTC" in ticker["instId"]
                    and "DOWN" not in ticker["instId"]
                    and "BEAR" not in ticker["instId"]
                    and "BULL" not in ticker["instId"]
                    and "DAI" not in ticker["instId"]
                    and ticker["instId"].count("BTC") == 1
            )
        ]
