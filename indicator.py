from typing import List

import numpy as np


class Indicator:

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