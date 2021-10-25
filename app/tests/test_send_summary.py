import pytest
from app.enums.exchange import Exchange

from send_summary import getPairAndExchange

def test_getPairAndExchange_btc():
    (pair, exchange) = getPairAndExchange("btc")
    assert(pair == 'btc')
    assert(exchange == Exchange.OKEX)


def test_getPairAndExchange_usdt():
    (pair, exchange) = getPairAndExchange("usdt")
    assert(pair == 'usdt')
    assert(exchange == Exchange.BINANCE)