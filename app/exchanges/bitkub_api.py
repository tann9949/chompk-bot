import json
import time
from datetime import datetime
from typing import List, Dict

import pandas as pd
import requests

from app.exchanges.base_exchange import ExchangeAPI


class BitkubAPI(ExchangeAPI):
    base_url: str = "https://api.bitkub.com"
    reso_mapping: Dict[str, int] = {
        "15min": 900,
        "30min": 1800,
        "1h": 3600,
        "4h": 14400,
        "12h": 43200,
        "1D": 86400,
        "1W": 604800,
        "1M": 2678400
    }

    @staticmethod
    def generate_candle_data(
            symbol: str,
            lookback: int = 100,  # numbers of candles to lookback
            interval: str = "1D") -> pd.DataFrame:
        # format start, end time
        end = int(time.time())
        start = end - BitkubAPI.reso_mapping[interval] * lookback

        r = requests.get(
            f"{BitkubAPI.base_url}/tradingview/history",
            {
                "symbol": symbol,
                "resolution": interval,
                "from": start,
                "to": end
            }
        )
        klines = json.loads(r.text)
        candle_data = []
        timestamp = []
        if klines["s"] == "no_data":
            return None
        for T in range(len(klines["t"])):
            open_time = (datetime.utcfromtimestamp(int(klines["t"][T])).strftime('%Y-%m-%d %H:%M:%S'))
            timestamp.append(open_time)
            # end_time = datetime.utcfromtimestamp(l[6])
            volume = klines["v"][T]
            high, low, op, close = klines["h"][T], klines["l"][T], klines["o"][T], klines["c"][T]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(candle_data, columns=["open", "close", "high", "low", "volume"], index=timestamp)
        return candle_data.astype(float)

    @staticmethod
    def get_thb_tickers() -> List[str]:
        r = requests.get(f"{BitkubAPI.base_url}/api/market/symbols")
        tickers = json.loads(r.text)
        return [
            str(ticker["symbol"][4:] + "_" + ticker["symbol"][:3])
            for ticker in tickers["result"]
            if (
                    ticker["symbol"][:4] != "USDT"
                    and "THB" in ticker["symbol"]
                    and "USD" not in ticker["symbol"]
                    and "DOWN" not in ticker["symbol"]
                    and "BEAR" not in ticker["symbol"]
                    and "BULL" not in ticker["symbol"]
                    and "DAI" not in ticker["symbol"]
                    and ticker["symbol"].count("THB") == 1
            )
        ]
