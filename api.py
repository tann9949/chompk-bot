import json

import pandas as pd
import requests

class BinanceAPI:

    @staticmethod
    def generate_candle_data(symbol, interval, base_url="https://api.binance.com"):
        r = requests.get(f"{base_url}/api/v3/klines", {"symbol": symbol, "interval": interval})
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
