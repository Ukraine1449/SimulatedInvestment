# https://algotrading101.com/learn/yahoo-finance-api-guide/
import time
import yfinance as yf

def estimate(tickers):
    rets = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        try:
            recommendations = stock.recommendations
            if recommendations is not None and not recommendations.empty:
                latest = recommendations.iloc[-1]
                strongBuy = int(latest.get('strongBuy', 0))
                buy = int(latest.get('buy', 0))
                hold = int(latest.get('hold', 0))
                sell = int(latest.get('sell', 0))
                strongSell = int(latest.get('strongSell', 0))
                net_recommendation = (strongBuy + buy) - (sell + strongSell)
                rets[ticker] = [net_recommendation, hold]
            else:
                rets[ticker] = [None, None]
        except Exception as e:
            print(f"Failed to fetch or process data for {ticker}: {str(e)}")
            rets[ticker] = [None, None]
        time.sleep(5)

    print(rets)