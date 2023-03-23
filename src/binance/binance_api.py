import json
import os
from datetime import date

from forex_python.converter import CurrencyRates
import requests
from dataclasses import dataclass
from typing import List

@dataclass
class BinanceFiatList:
    payTypes: List[str]
    countries: List[str]
    asset: str
    fiat: str
    tradeType: str
    transAmount: float

@dataclass
class Trade:
    price: float
    asset: str
    fiat: str
    trader_name: str
    payTypes: [str]
    min_limit: float
    max_limit: float

@dataclass
class BuySellTrade:
    buy: Trade
    sell: Trade
    output: float


def list_fiat_trades(params: BinanceFiatList) -> dict:
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "authority": 'p2p.binance.com',
        "accept": '*/*',
        "accept-language": 'en-US,en;q=0.9,ru;q=0.8,uk;q=0.7,tr;q=0.6',
        "content-type": 'application/json',
        "lang": 'en',
        "origin": 'https://p2p.binance.com',
        "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    payload = {
        "proMerchantAds": False,
        "page": 1,
        "rows": 10,
        "payTypes": params.payTypes,
        "countries": params.countries,
        "publisherType": None,
        "asset": params.asset,
        "fiat": params.fiat,
        "tradeType": params.tradeType,
        "transAmount": params.transAmount,
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def map_trades(trades):
    top_trades = []
    for item in trades["data"]:
        price = float(item["adv"]["price"])
        trade_methods = [method["identifier"] for method in item["adv"]["tradeMethods"]]
        name = item["advertiser"]["nickName"]
        min_amount = float(item["adv"]["minSingleTransAmount"])
        max_amount = float(item["adv"]["dynamicMaxSingleTransAmount"])
        trade = Trade(price=price,asset=item["adv"]["asset"], fiat=item["adv"]["fiatUnit"],  trader_name=name, payTypes=trade_methods, min_limit=min_amount, max_limit=max_amount)
        top_trades.append(trade)
    return top_trades


def get_best_trade(fiat: BinanceFiatList):
    trades = list_fiat_trades(fiat)
    top_trades = map_trades(trades)
    top_trade = min(top_trades, key=lambda x: x.price)
    return top_trade


def get_exchange_rate(base_currency, target_currency):
    """Get the exchange rate between two currencies"""
    return 0.12


def get_best_crypto_type(buy_currency:str, sell_currency:str, amount:float, crypto_list=None):
    if crypto_list is None:
        crypto_list = ["BTC", "USDT"]
    buy_sell_trades = []
    for crypto in crypto_list:
        buy_crypto_trade = BinanceFiatList(payTypes=[], countries=[], asset=crypto, fiat=buy_currency, tradeType="BUY", transAmount=amount)
        best_buy = get_best_trade(buy_crypto_trade)

        ex_rate = get_exchange_rate(buy_currency, sell_currency)
        est_sell_amount = float(amount) * ex_rate

        sell_crypto_trade = BinanceFiatList(payTypes=[], countries=[], asset=crypto, fiat=sell_currency, tradeType="SELL", transAmount=est_sell_amount)
        best_sell = get_best_trade(sell_crypto_trade)

        output = (amount / best_buy.price) * best_sell.price
        bs_trade = BuySellTrade(buy=best_buy, sell=best_sell, output=output)
        buy_sell_trades.append(bs_trade)

    return max(buy_sell_trades, key=lambda x: x.output)


def get_best_exchange_rate(buy_currency, sell_currency, amount, base_currency='USDT'):
    # Replace YOUR_API_KEY with your own API key
    api_key = os.getenv("BINANCE_KEY")
    base_url = 'https://api.binance.com'
    headers = {'X-MBX-APIKEY': api_key}

    # Get current exchange rates
    ticker_url = base_url + '/api/v3/ticker/price?symbol=' + buy_currency + base_currency
    ticker_response = requests.get(ticker_url, headers=headers)
    ticker_data = json.loads(ticker_response.text)
    buy_price = float(ticker_data['price'])

    ticker_url = base_url + '/api/v3/ticker/price?symbol=' + sell_currency + base_currency
    ticker_response = requests.get(ticker_url)
    ticker_data = json.loads(ticker_response.text)
    sell_price = float(ticker_data['price'])

    # Calculate amount of crypto to buy
    buy_amount = amount / buy_price

    # Get list of all available symbols
    exchange_info_url = base_url + '/api/v3/exchangeInfo'
    exchange_info_response = requests.get(exchange_info_url)
    exchange_info_data = json.loads(exchange_info_response.text)
    symbols = exchange_info_data['symbols']

    # Find best symbol with highest bid price and lowest ask price
    best_bid_price = 0
    best_ask_price = float('inf')
    best_symbol = ''
    for symbol in symbols:
        if symbol['baseAsset'] == buy_currency and symbol['quoteAsset'] == sell_currency:
            bid_price = float(symbol['bidPrice'])
            ask_price = float(symbol['askPrice'])
            if bid_price > best_bid_price and ask_price < best_ask_price:
                best_bid_price = bid_price
                best_ask_price = ask_price
                best_symbol = symbol['symbol']

    # Calculate amount of money to receive after selling crypto
    sell_amount = buy_amount * best_ask_price * sell_price
    return (best_symbol, sell_amount)