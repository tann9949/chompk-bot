import json
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas import Series
from requests.models import Response


class CoinGecko:
    base_url: str = "https://api.coingecko.com"

    @staticmethod
    def get_btc_dominance():
        url: str = f"{CoinGecko.base_url}/api/v3/global"
        response = requests.get(url)
        data = json.loads(response.text)
        return data["data"]["market_cap_percentage"]["btc"]


class CoinGlassAPI:
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
        url: str = f"{CoinGlassAPI.base_url}/api/openInterest/v3/chart?symbol=BTC&timeType=0&exchangeName=&type=0"
        r = os.popen(f'curl -X GET "{url}"').read()
        data = json.loads(r)["data"]

        aggregated_oi = {}
        for exchange, oi_data in data["dataMap"].items():
            oi_data = pd.Series(
                oi_data,
                index=[CoinGlassAPI.format_unix_time(d) for d in data["dateList"]],
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


class AltCoinIndexAPI:
    api_url: str = "https://www.blockchaincenter.net/altcoin-season-index/"

    @staticmethod
    def get_historical_altcoin_index():
        soup: BeautifulSoup = BeautifulSoup(
            requests.get(AltCoinIndexAPI.api_url).text,
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
    def get_historical_data(days: int = 300) -> Series:
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
