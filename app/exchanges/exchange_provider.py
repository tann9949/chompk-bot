from typing import Dict

from enums.exchange import Exchange
from exchanges.base_exchange import ExchangeAPI
from exchanges.binance_api import BinanceAPI
from exchanges.bitkub_api import BitkubAPI
from exchanges.ftx_api import FtxAPI
from exchanges.kucoin_api import KucoinAPI
from exchanges.okx_api import OkxAPI


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
