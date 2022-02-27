from abc import ABC, abstractmethod
from typing import List

import pandas as pd


class PairNotSupportedException(Exception):
    pass


class ExchangeAPI(ABC):
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

    @classmethod
    def get_perp_tickers(cls) -> List[str]:
        raise PairNotSupportedException(f'perp ticker is not supported or not implemented by {cls.__name__}')

    @classmethod
    def get_thb_tickers(cls) -> List[str]:
        raise PairNotSupportedException(f'thb ticker is not supported or not implemented by {cls.__name__}')
