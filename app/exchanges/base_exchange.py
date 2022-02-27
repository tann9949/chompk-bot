from abc import ABC, abstractmethod
from typing import List

import pandas as pd


class BaseExchange(ABC):
    base_url: str

    @staticmethod
    @abstractmethod
    def generate_candle_data(
            symbol: str,
            interval: str = "1d") -> pd.DataFrame:
        pass

    @staticmethod
    @abstractmethod
    def get_usdt_tickers() -> List[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_btc_tickers() -> List[str]:
        pass
