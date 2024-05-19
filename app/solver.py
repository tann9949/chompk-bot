import re
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from .enums.signal import Signal

from ta import trend, momentum


class Solver:
    @staticmethod
    def get_cdc_signal(src: pd.Series, current: bool = True) -> Optional[Signal]:
        curr_idx = -1
        prev_idx = -2
        if not current:
            curr_idx -= 1
            prev_idx -= 1

        # Buy/Sell
        if len(src) < 30:
            return None

        macd = trend.MACD(src).macd()
        current_diff: float = macd[curr_idx]
        prev_diff: float = macd[prev_idx]

        if prev_diff < 0 < current_diff:  # cross over
            return Signal.Buy
        elif prev_diff > 0 > current_diff:  # cross under
            return Signal.Sell

        # Buymore sell more
        # todo: check this
        rsi = momentum.rsi(src, 14)
        stoch_rsi = momentum.stoch(rsi, rsi, rsi, 14).values
        k = trend.sma_indicator(stoch_rsi, 3)
        d = trend.sma_indicator(k, 3)
        current_kd_diff = k[curr_idx] - d[curr_idx]
        prev_kd_diff = k[prev_idx] - d[prev_idx]

        if current_diff > 0:
            if (
                current_kd_diff > 0 > prev_kd_diff and k[-1] < 30 and current_diff > 0
            ):  # cross over
                return Signal.BuyMore

            return Signal.Bullish
        else:
            if (
                current_kd_diff < 0 < prev_kd_diff and k[-1] > 70 and current_diff < 0
            ):  # cross under
                return Signal.SellMore
            return Signal.Bearish

    @staticmethod
    def solve_cdc_cross(
        src: pd.Series, max_trial: int = 100000
    ) -> Tuple[Optional[float], str]:
        """
        Solve (brute force search) for EMA 12, EMA 26
        crosses up/down given historical data

        Arguments
        ---------
        data: np.ndarray
            A candlestick data loaded from `generate_candle_data` function
        max_trial: np.ndarray
            Maximum number of trial to be done during search

        Return
        ------
        result_price: Optional[float]
            A price that causes golden/death cross between
            EMA12, EMA26. If return None, solution cannot be found
            within given range of `delta` and `resolution`
        """
        fast_ema: np.ndarray = trend.ema_indicator(src.values, 12).values
        slow_ema: np.ndarray = trend.ema_indicator(src.values, 26).values
        ema_diff: float = fast_ema[-1] - slow_ema[-1]
        current_price: float = src.values[-1]

        assert current_price > 0
        if abs(current_price) >= 1:
            degree: int = len(str(current_price).split(".")[0]) - 1
            decimal_place: int = 4
        else:
            regex_zero: int = len(
                re.findall(r"0\.0+", f"{current_price:.20f}")[0].split(".")[-1]
            )
            degree: int = -int(regex_zero) - 1
            decimal_place: int = -degree + 4
        resolution: float = 10**degree

        delta: float = resolution / 1000

        if ema_diff >= 0:
            # bullish, gradually step down price
            delta = -delta

        result_price: float = current_price
        n_trial: int = 1
        template: str = ""
        while True:
            if result_price < 0.0 or n_trial > max_trial:
                template += "Could not solve for a solution!"
                return template
            src.iloc[-1] = result_price
            fast_ema: np.ndarray = trend.ema_indicator(src.values, 12).values
            slow_ema: np.ndarray = trend.ema_indicator(src.values, 26).values
            diff: float = fast_ema[-1] - slow_ema[-1]
            # print(result_price, diff)
            if abs(diff) < abs(delta) / 10:
                if ema_diff > 0:
                    template += (
                        "If today's price closed at $"
                        + f"%.{decimal_place}f" % result_price
                        + ", CDC V3 Action Zone will be bearish"
                    )
                else:
                    template += (
                        "If today's price closed at $"
                        + f"%.{decimal_place}f" % result_price
                        + ", CDC V3 Action Zone will be bullish"
                    )
                price_diff: float = result_price - current_price
                sign: str = "+" if price_diff > 0 else "-"
                percent_diff: float = price_diff / current_price
                template += (
                    f"\nThat will be {sign}$"
                    + f"%.{decimal_place}f" % abs(result_price - current_price)
                    + f" ({sign}"
                    + "%.2f" % abs(percent_diff * 100)
                    + "%) from the current price ($"
                    + f"%.{decimal_place}f" % current_price
                    + ")"
                )
                return result_price, template
            result_price += delta
            n_trial += 1
