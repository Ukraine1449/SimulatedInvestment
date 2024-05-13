import random
import time
import sqlite3
import wsj_scrape

from investopedia_api import InvestopediaApi, StockTrade, OptionTrade, Expiration, OrderLimit, TransactionType, \
    OptionScope, OptionChain
import json
from datetime import datetime, timedelta
import finnhub

finnhub_client = finnhub.Client(api_key="colr5kpr01qqra7g7oagcolr5kpr01qqra7g7ob0")
credentials = {}
with open('credentials.json') as ifh:
    credentials = json.load(ifh)
client = InvestopediaApi(credentials)

p = client.portfolio
print("Portfolio Value: %s" % p.account_value)
print("Cash: %s" % p.cash)
print("Buying Power: %s" % p.buying_power)
print("Annual Return Percent: %s" % p.annual_return_pct)
print("\nOpen Orders:")
for open_order in p.open_orders:
    print("-------------------------------------------------")
    print("Trade Type: %s" % open_order.trade_type)
    print("Symbol: %s" % open_order.symbol)
    print("Quantity: %s" % open_order.quantity)
    print("Price: %s" % open_order.order_price)
    print("-------------------------------------------------")
print("-------------------------------------------------")

print("\nStock Portfolio Details:")
print("-------------------------------------------------")
print("Market Value: %s" % p.stock_portfolio.market_value)
print("Today's Gain: %s (%s%%)" % (p.stock_portfolio.day_gain_dollar, p.stock_portfolio.day_gain_percent))
print("Total Gain: %s (%s%%)" % (p.stock_portfolio.total_gain_dollar, p.stock_portfolio.total_gain_percent))
print("-------------------------------------------------")

print("\nLong Positions:")
for position in p.stock_portfolio:
    print("-------------------------------------------------")
    print("Company: %s (%s)" % (position.description, position.symbol))
    print("Shares: %s" % position.quantity)
    print("Purchase Price: %s" % position.purchase_price)
    print("Current Price: %s" % position.current_price)
    print("Today's Gain: %s (%s%%)" % (position.day_gain_dollar, position.day_gain_percent))
    print("Total Gain: %s (%s%%)" % (position.total_gain_dollar, position.total_gain_percent))
    print("Market/Total Value: %s" % position.market_value)
    print("\t------------------------------")
    print("\tQuote")
    print("\t------------------------------")
    quote = position.quote
    for k, v in quote.__dict__.items():
        print("\t%s: %s" % (k, v))
    print("\t------------------------------")
    print("-------------------------------------------------")

print("\nShort Positions:")
for position in p.short_portfolio:
    print("-------------------------------------------------")
    print("Company: %s (%s)" % (position.description, position.symbol))
    print("Shares: %s" % position.quantity)
    print("Purchase Price: %s" % position.purchase_price)
    print("Current Price: %s" % position.current_price)
    print("Today's Gain: %s (%s%%)" % (position.day_gain_dollar, position.day_gain_percent))
    print("Total Gain: %s (%s%%)" % (position.total_gain_dollar, position.total_gain_percent))
    print("Market/Total Value: %s" % position.market_value)
    print("\t------------------------------")
    print("\tQuote")
    print("\t------------------------------")
    quote = position.quote
    for k, v in quote.__dict__.items():
        print("\t%s: %s" % (k, v))
    print("\t------------------------------")
    print("-------------------------------------------------")

print("\nOption Positions:")
for position in p.option_portfolio:
    print("-------------------------------------------------")
    print("Company: %s (%s)" % (position.description, position.underlying_symbol))
    print("Symbol: %s" % position.symbol)
    print("Contracts: %s" % position.quantity)
    print("Purchase Price: %s" % position.purchase_price)
    print("Current Price: %s" % position.current_price)
    print("Today's Gain: %s (%s%%)" % (position.day_gain_dollar, position.day_gain_percent))
    print("Total Gain: %s (%s%%)" % (position.total_gain_dollar, position.total_gain_percent))
    print("Market/Total Value: %s" % position.market_value)
    print("\t------------------------------")
    print("\tQuote")
    print("\t------------------------------")
    quote = position.quote
    for k, v in quote.__dict__.items():
        print("\t%s: %s" % (k, v))
    print("\t------------------------------")
    print("-------------------------------------------------")


def sell_stock(ticker, shares):
    from investopedia_api import StockTrade, TransactionType, OrderLimit, Expiration
    client.portfolio.refresh()
    stock_position = next((position for position in client.portfolio.stock_portfolio if position.symbol == ticker),
                          None)

    if stock_position is not None:
        shares_to_sell = min(shares, stock_position.quantity)
        trade = StockTrade(portfolio_id=client.portfolio.portfolio_id,
                           symbol=ticker,
                           quantity=shares_to_sell,
                           transaction_type=TransactionType.SELL,
                           order_limit=OrderLimit.MARKET(),
                           expiration=Expiration.GOOD_UNTIL_CANCELLED())
        trade.validate()
        trade.execute()
    else:
        print("No shares of {} found in the portfolio.".format(ticker))


def read_database_to_dict():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT ticker, price FROM stocks')
    data = {ticker: price for ticker, price in cursor.fetchall()}
    conn.close()
    return data


def update_database_from_dict(update_dict):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    for ticker, price in update_dict.items():
        cursor.execute('UPDATE stocks SET price = ? WHERE ticker = ?', (price, ticker))
    conn.commit()
    conn.close()


def add_to_database_from_dict(new_data_dict):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    for ticker, price in new_data_dict.items():
        cursor.execute('INSERT OR IGNORE INTO stocks (ticker, price) VALUES (?, ?)', (ticker, price))
    conn.commit()
    conn.close()


def create_database():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT PRIMARY KEY,
            price REAL
        )
    ''')
    conn.commit()
    conn.close()


def buy_stock(ticker, shares):
    from investopedia_api import StockTrade, TransactionType, OrderLimit, Expiration

    trade = StockTrade(portfolio_id=client.portfolio.portfolio_id,
                       symbol=ticker,
                       quantity=shares,
                       transaction_type=TransactionType.BUY,
                       order_limit=OrderLimit.MARKET(),
                       expiration=Expiration.GOOD_UNTIL_CANCELLED())
    trade.validate()
    trade.execute()


def getPrice(data):
    return data.get('c', None)


stockList = ["MSFT", "AAPL", "NVDA", "GOOGL"]
portfolio_dict = {}
for i in stockList:
    portfolio_dict[i] = 0
for position in p.stock_portfolio:
    portfolio_dict[position.symbol] = position.quantity
prices = {}
for i in stockList:
    prices[i] = getPrice(finnhub_client.quote(i))
stock_recs = wsj_scrape.estimate(stockList)
print(stock_recs)

def constantRun():
    while True:
        print("restarting")
        time.sleep(30)
        current_prices = {}
        for i in stockList:
            current_prices[i] = getPrice(finnhub_client.quote(i))
        print("updated stock values")
        for i in stockList:
            if portfolio_dict.get(i) > 0:
                if stock_recs.get(i)[0] - stock_recs.get(i)[1] > 5 & portfolio_dict.get(i) < 15:
                    buy_stock(i, 15 - portfolio_dict.get(i))
                elif stock_recs.get(i)[0] < 5:
                    sell_stock(i, portfolio_dict.get(i))
            else:
                if stock_recs.get(i)[0] - stock_recs.get(i)[1] > 5:
                    buy_stock(i, 15 - portfolio_dict.get(i))

#constantRun()