from typing import List

import pandas as pd
import numpy as np


class TechnicalAnalysis:

    @staticmethod
    def sma(data: np.ndarray, period: int) -> np.ndarray:
        return pd.Series(data).rolling(window=period).mean().fillna(0).values

    @staticmethod
    def rma(data: np.ndarray, period: int) -> np.ndarray:
        alpha: float = 1 / period;
        prev_d_t: float = 0.

        averages: List[float] = [];
        for d in data:
            d_t: float = alpha * d + (1 - alpha) * prev_d_t;
            averages.append(d_t);
            prev_d_t = d_t;
        return np.array(averages);

    @staticmethod
    def ema(data: np.ndarray, period: int) -> np.ndarray:
        alpha: float = 2 / (period + 1)
        prev_d_t: float = 0.

        averages: List[float] = [];
        for d in data:
            if not isinstance(d, float):
                d = float(d)
            d_t: float = alpha * d + (1 - alpha) * prev_d_t;
            averages.append(d_t);
            prev_d_t = d_t;
        return np.array(averages);  

    @staticmethod
    def rsi(src: pd.Series, period: int = 14) -> np.ndarray:
        # if duration < period
        if len(src) < period + 1:
            return pd.Series([np.nan for _ in range(len(src))], name="rsi");

        # unpack
        close_price: np.ndarray = src.values;

        # compute RSI
        close_t: np.ndarray = close_price;
        close_t_1: np.ndarray = np.concatenate(
            (np.zeros(1), close_price[: -1])
        );
        change: np.ndarray = close_t - close_t_1;

        u: np.ndarray = np.array([max(0, diff) for diff in change]);
        d: np.ndarray = np.array([max(0, -diff) for diff in change]);
        avg_u: float = TechnicalAnalysis.rma(u, period);
        avg_d: float = TechnicalAnalysis.rma(d, period);

        relative_strength: np.ndarray = avg_u / avg_d;
        rsi: np.ndarray = 100. - (100. / (1 + relative_strength));
        return rsi

    @staticmethod
    def stoch(src: pd.Series, high: pd.Series, low: pd.Series, length: int) -> np.ndarray:
        # TODO:
        pass