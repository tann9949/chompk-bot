from typing import Dict

from app.enums.exchange import Exchange
from app.exchanges import (ExchangeAPI, BinanceAPI,
                           BitkubAPI, OkxAPI, FtxAPI, KucoinAPI)


class ExchangeAPINotFoundException(Exception):
    pass


class ExchangeProvider:
    exchangeMapper: Dict[Exchange, ExchangeAPI] = {
        Exchange.BINANCE: BinanceAPI,
        Exchange.OKEX: OkxAPI,
        Exchange.FTX: FtxAPI,
        Exchange.KUCOIN: KucoinAPI,
        Exchange.BITKUB: BitkubAPI,
    }

    @staticmethod
    def provide(exchange: Exchange) -> ExchangeAPI:
        if exchange not in ExchangeProvider.exchangeMapper:
            raise ExchangeAPINotFoundException(
                f"{exchange} not found in mapper")

        return ExchangeProvider.exchangeMapper[exchange]
