import re
from typing import Optional, Tuple

import numpy as np

from indicator import Indicator


class Solver:

    @staticmethod
    def solve_cdc_cross(
        data: np.ndarray,
        max_trial: int = 100000) -> Tuple[Optional[float], str]:
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
            A price that causes golden/death cross betwenn
            EMA12, EMA26. If return None, solution cannot be found
            within given range of `delta` and `resolution`
        """
        fast_ema: np.ndarray = Indicator.ema(data["close"].values, 12)
        slow_ema: np.ndarray = Indicator.ema(data["close"].values, 26)
        ema_diff: float = fast_ema[-1] - slow_ema[-1]
        current_price: float = data["close"].values[-1]

        assert current_price > 0
        if abs(current_price) >= 1:
            degree: int = len(str(current_price).split(".")[0]) - 1
            decimal_place: int = 4
        else:
            regex_zero: int = len(re.findall(r"0\.0+", f"{current_price:.20f}")[0].split(".")[-1])
            degree: int = -int(regex_zero)-1
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
            if result_price < 0. or n_trial > max_trial:
                template += "Could not solve for a solution!"
                return template
            data.iloc[-1]["close"] = result_price
            fast_ema: np.ndarray = Indicator.ema(data["close"].values, 12)
            slow_ema: np.ndarray = Indicator.ema(data["close"].values, 26)
            diff: float = fast_ema[-1] - slow_ema[-1]
            # print(result_price, diff)
            if abs(diff) < abs(delta) / 10:
                if ema_diff > 0:
                    template += f"If today's price closed at $" + f"%.{decimal_place}f" % result_price + ", CDC V3 Action Zone will be bearish"
                else:
                    template += f"If today's price closed at $" + f"%.{decimal_place}f" % result_price + ", CDC V3 Action Zone will be bullish"
                price_diff: float = result_price - current_price
                sign: str = "+" if price_diff > 0 else "-"
                percent_diff: float = price_diff / current_price
                template += f"\nThat will be {sign}$" + f"%.{decimal_place}f" % abs(result_price - current_price) + \
                            f" ({sign}" + f"%.2f" % abs(percent_diff*100) + \
                            f"%) from the current price ($" + f"%.{decimal_place}f" % current_price + ")"
                return result_price, template
            result_price += delta
            n_trial += 1 