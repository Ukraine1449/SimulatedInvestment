import random
import time

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
    stock_position = next((position for position in client.portfolio.stock_portfolio if position.symbol == ticker), None)

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


stockList = ["MSFT", "AAPL","NVDA", "GOOGL"]
portfolio_dict = {}
for i in stockList:
    portfolio_dict[i]=0
for position in p.stock_portfolio:
    portfolio_dict[position.symbol] = position.quantity
prices = {}
for i in stockList:
    prices[i] = getPrice(finnhub_client.quote(i))
while True:
    print("restarting")
    time.sleep(30)
    current_prices = {}
    for i in stockList:
        current_prices[i] = getPrice(finnhub_client.quote(i))
    print("updated stock values")
    for i in stockList:
        if portfolio_dict[i] >0:
            if prices[i] - current_prices[i] >=2:
                sell_stock(i, stockList[i])
                print("Selling stocks")
        else:
             if current_prices[i] < prices[i]:
                 buy_stock(i, random.randint(1,10))
                 print("Buying stocks")