from src.binance.binance_api import list_fiat_trades, BinanceFiatList, get_best_trade, get_best_crypto_type


def test_binance_api():
    b_fiat = BinanceFiatList(payTypes=[], countries=[], asset="USDT", fiat="UAH", tradeType="BUY")
    o_json = list_fiat_trades(b_fiat)
    assert o_json is not None


def test_get_best_trade():
    b_fiat = BinanceFiatList(payTypes=[], countries=[], asset="USDT", fiat="PLN", tradeType="SELL", transAmount=560)
    b_trade = get_best_trade(b_fiat)
    assert b_trade is not None


def test_best_full_trade():
    best_t = get_best_crypto_type(buy_currency="UAH", sell_currency="PLN", amount=20000)
    assert best_t is not None