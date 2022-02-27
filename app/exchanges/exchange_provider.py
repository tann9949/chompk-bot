from typing import Dict

from enums.exchange import Exchange
from exchanges import (ExchangeAPI, BitkubAPI, BinanceAPI, OkxAPI, KucoinAPI, FtxAPI)


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
            raise ExchangeAPINotFoundException(f"{exchange} not found in mapper")

        return ExchangeProvider.exchangeMapper[exchange]
