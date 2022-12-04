import os

from dotenv import load_dotenv

from app.callback import get_cdc_template
from app.enums.exchange import Exchange
from app.enums.pairs import Pairs


def test_okex():
    get_cdc_template(Pairs.USDT, Exchange.OKEX)
    get_cdc_template(Pairs.BTC, Exchange.OKEX)


def test_bitkub():
    get_cdc_template(Pairs.THB, Exchange.BITKUB)


def test_binance():
    get_cdc_template(Pairs.USDT, Exchange.BINANCE)
    get_cdc_template(Pairs.BTC, Exchange.BINANCE)


def test_kucoin():
    get_cdc_template(Pairs.USDT, Exchange.KUCOIN)
    get_cdc_template(Pairs.BTC, Exchange.KUCOIN)
