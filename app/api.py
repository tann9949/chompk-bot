import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.models import Response


class OkxAPI:

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
        print(klines)
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

    def get_usdt_tickers() -> List[str]:
        r = requests.get(f"{OkxAPI.base_url}/api/v5/market/tickers?instType=SPOT")
        tickers = json.loads(r.text)['data']
        #print(tickers)
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
                and ticker["symbol"].count("BTC") == 1
            )
        ]

class FtxAPI:
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
        for l in klines:
            open_time = datetime.strptime(l["startTime"], "%Y-%m-%dT%H:%M:%S+00:00")
            timestamp.append(open_time)
            volume = l["volume"]
            high, low, op, close = l["high"], l["low"], l["open"], l["close"]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(candle_data, columns=["open", "close", "high", "low", "volume"], index=timestamp)
        return candle_data.astype(float).resample("1D").mean()

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
        
    def get_perp_tickers() -> List[str]:
        r = requests.get(f"{FtxAPI.base_url}/markets")
        tickers = json.loads(r.text)
        return [
            ticker["name"]
            for ticker in tickers["result"]
            if "PERP" in ticker["name"]
        ]
        
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


class KucoinAPI:

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

class BitkubAPI:

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
            high, low, op, close = klines["h"][T],klines["l"][T],klines["o"][T],klines["c"][T]
            candle_data.append([op, close, high, low, volume])
        candle_data = pd.DataFrame(candle_data, columns=["open", "close", "high", "low", "volume"], index=timestamp)
        return candle_data.astype(float)
    
    @staticmethod
    def get_thb_tickers() -> List[str]:
        r = requests.get(f"{BitkubAPI.base_url}/api/market/symbols")
        tickers = json.loads(r.text)
        return [
            str(ticker["symbol"][4:]+"_"+ticker["symbol"][:3])
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

class CoinGecko:

    base_url: str = "https://api.coingecko.com"

    @staticmethod
    def get_btc_dominance():
        url: str = f"{CoinGecko.base_url}/api/v3/global"
        response = requests.get(url)
        data = json.loads(response.text)
        return data["data"]["market_cap_percentage"]["btc"]


class CoinglassAPI:

    base_url: str = "https://fapi.coinglass.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.coinglass.com/',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua-mobile': '?0',
        'authority': 'fapi.coinglass.com',
        'accept-language': 'en-US,en;q=0.9'
    }

    @staticmethod
    def format_unix_time(unix_time: int):
        return datetime.utcfromtimestamp(int(str(unix_time)[:-3]))

    @staticmethod
    def get_open_interest(fill_na: bool = True):
        url: str = f"{CoinglassAPI.base_url}/api/openInterest/v3/chart?symbol=BTC&timeType=0&exchangeName=&type=0"
        r = os.popen(f'curl -X GET "{url}"').read()
        data = json.loads(r)["data"]

        aggregated_oi = {}
        for exchange, oi_data in data["dataMap"].items():
            oi_data = pd.Series(
                oi_data,
                index=[CoinglassAPI.format_unix_time(d) for d in data["dateList"]],
                name=f"{exchange} Open Interest"
            )
            if fill_na:
                oi_data = oi_data.fillna(0)
            aggregated_oi[exchange.lower().strip()] = oi_data
        return aggregated_oi



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
        'accept-language': 'en-US,en;q=0.9'
    }

    @staticmethod
    def format_unix_time(unix_time: int) -> datetime:
        return datetime.utcfromtimestamp(unix_time)

    @staticmethod
    def get_open_interest():
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
            if "chartdata" in sc.contents[0] and '"labels"' in sc.contents[0]:
                break
        chart_data = json.loads(re.findall(r" = (\{.+\})", sc.contents[0])[0])
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
