import json
import re
import time
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.models import Response


class OkexAPI:

    base_url: str = "https://www.okex.com"

    @staticmethod
    def generate_candle_data(instrument_id: str) -> pd.DataFrame:
        r = requests.get(f"{OkexAPI.base_url}/api/spot/v3/instruments/{instrument_id}/candles")
        klines = json.loads(r.text)
        candle_data = []
        timestamp = []
        for l in klines:
            open_time = l[0]
            timestamp.append(open_time)
            volume = l[5]
            high, low, op, close = l[2], l[3], l[1], l[4]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(candle_data, columns=["open", "close", "high", "low", "volume"], index=timestamp)
        return candle_data

    def get_btc_tickers() -> List[str]:
        r = requests.get(f"{OkexAPI.base_url}/api/spot/v3/instruments/ticker")
        tickers = json.loads(r.text)
        return [
            ticker["instrument_id"]
            for ticker in tickers
            if (
                ticker["instrument_id"][:3] != "BTC"
                and "USD" not in ticker["instrument_id"] 
                and "BTC" in ticker["instrument_id"]
                and "DOWN" not in ticker["instrument_id"]
                and "BEAR" not in ticker["instrument_id"]
                and "BULL" not in ticker["instrument_id"]
                and "DAI" not in ticker["instrument_id"]
            )
        ]


class BinanceAPI:

    base_url: str = "https://api.binance.com"

    @staticmethod
    def format_unixtime(unix_time: int):
        return datetime.utcfromtimestamp(int(str(unix_time)[:-3]))

    @staticmethod
    def generate_candle_data(
        symbol: str, 
        interval: str = "1d") -> pd.DataFrame:
        r = requests.get(f"{BinanceAPI.base_url}/api/v3/klines", {"symbol": symbol, "interval": interval})
        klines = json.loads(r.text)
        candle_data = []
        timestamp = []
        for l in klines:
            assert len(l) == 12, f"{symbol}: {len(l)}"
            open_time = BinanceAPI.format_unixtime(l[0])
            timestamp.append(open_time)
            # end_time = datetime.utcfromtimestamp(l[6])
            volume = l[5]
            high, low, op, close = l[2], l[3], l[1], l[4]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(candle_data, columns=["open", "close", "high", "low", "volume"], index=timestamp)
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
            )
        ]


class CoinGecko:

    base_url: str = "https://api.coingecko.com"

    @staticmethod
    def get_btc_dominance():
        url: str = f"{CoinGecko.base_url}/api/v3/global"
        response = requests.get(url)
        data = json.loads(response.text)
        return data["data"]["market_cap_percentage"]["btc"]


class TheBlockAPI:

    base_url: str = "https://data.tbstat.com"
    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.theblockcrypto.com/',
            'sec-ch-ua-platform': '"macOS"',
            'sec-ch-ua-mobile': '?0',
            'authority': 'data.tbstat.com',
            'accept-language': 'en-US,en;q=0.9\''
        }

    @staticmethod
    def format_unix_time(unix_time: int) -> datetime:
        return datetime.utcfromtimestamp(unix_time)

    @staticmethod
    def get_open_interset():
        current_time: int = int(time.time())
        url: str = f"{TheBlockAPI.base_url}/dashboard/markets_futures_aggregatedopeninterestofbitcoinfutures_daily_bybt.json?v={current_time}"
        
        response: Response = requests.get(
            url,
            headers=TheBlockAPI.headers,
        )
        data: Dict[str, Any] = json.loads(response.text)["Series"]

        aggregated_oi = {}
        for exchange, oi_data in data.items():
            oi_data = pd.Series(
                [d["Result"] for d in oi_data["Data"]],
                index=[TheBlockAPI.format_unix_time(d["Timestamp"]) for d in oi_data["Data"]],
                name=f"{exchange} Open Interest"
            )
            aggregated_oi[exchange] = oi_data

        return aggregated_oi


class AltcoinIndexAPI:

    api_url: str = "https://www.blockchaincenter.net/altcoin-season-index/"

    @staticmethod
    def get_historical_altcoin_index():
        soup: BeautifulSoup = BeautifulSoup(
            requests.get(AltcoinIndexAPI.api_url).text,
            "html.parser"
        )
        for sc in soup.find_all("script"):
            if len(sc) != 1:
                continue
            if "var chartdata" in sc.contents[0]:
                break
        chart_data = json.loads(re.findall(r'chartdata = \{.+\}', sc.contents[0])[0].replace("chartdata = ", ""))
        timestamp = [
            datetime.strptime(t, "%Y-%m-%d")
            for t in chart_data["labels"]["year"]
        ]
        value = [int(v) for v in chart_data["values"]["year"]]
        return pd.Series(value, index=timestamp, name="Altcoin Season Index")


class FearAndGreedAPI:

    api_url: str = "https://alternative.me/api/crypto/fear-and-greed-index/history";

    @staticmethod
    def get_historical_data(days: int = 300) -> pd.DataFrame:
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
