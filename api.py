from datetime import datetime
import json
from typing import Any, Dict, List

import pandas as pd
import requests
from requests.models import Response

class BinanceAPI:

    base_url: str = "https://api.binance.com"

    @staticmethod
    def generate_candle_data(
        symbol: str, 
        interval: str = "1d") -> pd.DataFrame:
        r = requests.get(f"{BinanceAPI.base_url}/api/v3/klines", {"symbol": symbol, "interval": interval})
        klines = json.loads(r.text)
        candle_data = []
        for l in klines:
            assert len(l) == 12, len(l)
            open_time, end_time = l[0], l[6]
            volume = l[5]
            high, low, op, close = l[2], l[3], l[1], l[4]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(candle_data, columns=["open", "close", "high", "low", "volume"])
        return candle_data.astype(float)

    @staticmethod
    def get_usdt_tickers() -> List[str]:
        r = requests.get(f"{BinanceAPI.base_url}/api/v3/ticker/price")
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
            )
        ]


class FearAndGreedAPI:

    api_url: str = "https://alternative.me/api/crypto/fear-and-greed-index/history";

    @staticmethod
    def get_historical_data(days: int = 30) -> pd.DataFrame:
        response: Response = requests.post(
            FearAndGreedAPI.api_url,
            data=json.dumps({
                "days": days
            }),
            headers={
                "content-type": "application/json"
            }
        )

        if response.status_code != 200:
            raise ConnectionError(f"Cannot fetch Fear and Greed Index: " + response.text)

        data: Dict[str, Any] = json.loads(response.text)["data"]

        fear_n_greed: List[int] = data["datasets"][0]["data"]
        date: List[datetime] = [
            datetime.strptime(dt, "%d %b, %Y")
            for dt in data["labels"]
        ]
        assert len(fear_n_greed) == len(date)
        return pd.Series(fear_n_greed, index=date, name="Fear and Greed Index")
