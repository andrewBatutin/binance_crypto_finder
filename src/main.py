from src.binance.binance_api import list_fiat_trades, BinanceFiatList, get_best_trade, get_best_crypto_type

best_t = get_best_crypto_type(buy_currency="UAH", sell_currency="EUR", amount=39000, crypto_list=["USDT", "BTC", "BUSD", "BNB", "ETH", "SHIB"])

print(best_t)
