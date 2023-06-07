from time import mktime
from datetime import datetime, timedelta
import pandas as pd

def getAvailableQty(client, symbol):
    wallet = client.balance()
    for w in wallet:
        if w['asset'] == 'USDT':
            balance = float(w['balance'])
    markPrice = float(client.mark_price(symbol)['markPrice'])
    qty = round(balance*15/markPrice*0.9, 3)
    return qty

def getSymbols(client):
    raw_data = client.exchange_info()
    
    symbols = []
    for s in raw_data['symbols']:
        symbols.append(s['symbol'])
    return symbols

def getSymbolsUSDT(client):
    raw_data = client.exchange_info()
    
    symbols = []
    for s in raw_data['symbols']:
        if s['symbol'][-4:] == 'USDT':
            symbols.append(s['symbol'])
        if 'PERP' in s['symbol']:
            symbols.append(s['symbol'])
    return symbols


def getCandleRecent(client, symbol, interval, limit):
    raw_data = client.klines(symbol=symbol, interval=interval, limit=limit)
    opentime = []
    data = {'open': [],
            'high': [],
            'low': [],
            'close': [],
            'volume': []}
    
    for raw in raw_data:
        opentime.append(datetime.fromtimestamp(raw[0]/1000).strftime('%Y-%m-%d %H:%M:%S'))
        data['open'].append(float(raw[1]))
        data['high'].append(float(raw[2]))
        data['low'].append(float(raw[3]))
        data['close'].append(float(raw[4]))
        data['volume'].append(float(raw[5]))
    
    df = pd.DataFrame(data, index=opentime)
    return df

def getCandleDataLimit(client, symbol, interval, start, limit):
    raw_data = client.klines(symbol=symbol, interval=interval, startTime=start, limit=limit)
    opentime = []
    data = {'open': [],
            'high': [],
            'low': [],
            'close': [],
            'volume': []}
    
    for raw in raw_data:
        opentime.append(datetime.fromtimestamp(raw[0]/1000).strftime('%Y-%m-%d %H:%M:%S'))
        data['open'].append(float(raw[1]))
        data['high'].append(float(raw[2]))
        data['low'].append(float(raw[3]))
        data['close'].append(float(raw[4]))
        data['volume'].append(float(raw[5]))
    
    df = pd.DataFrame(data, index=opentime)
    return df
# interval, 1m, 5m, 1h, 4d, 1d, ...
# limit, defalut 500, max 1000
# start, int, ms timestamp
# endt, int, ms timestamp
def getCandleData(client, symbol, interval, start, end):
    if interval == '1m':
        n = countCandle(start, end)
    if interval == '3m':
        n = int(countCandle(start, end) / 3)
    if interval == '5m':
        n = int(countCandle(start, end) / 5)
    if interval == '15m':
        n = int(countCandle(start, end) / 15)
    if interval == '1h':
        n = int(countCandle(start, end) / 60)
    if interval == '4h':
        n = int(countCandle(start, end) / 240)
    if interval == '6h':
        n = int(countCandle(start, end) / 360)
    if interval == '1d':
        n = int(countCandle(start, end) / 1440)
        
    if n <= 1000:
        startTime = strToTimestamp(start)
        df = getCandleDataLimit(client, symbol, interval, startTime, n)
        return df

    else:
        startTime = strToTimestamp(start)
        df = getCandleDataLimit(client, symbol, interval, startTime, 1000)        
        start = strToDatetime(start)
        for i in range(int(n/1000)-1):
            if interval == '1m':
                start += timedelta(minutes=1000)
            if interval == '3m':
                start += timedelta(minutes=1000*3)
            if interval == '5m':
                start += timedelta(minutes=1000*5)
            if interval == '15m':
                start += timedelta(minutes=1000*15)
            if interval == '1h':
                start += timedelta(minutes=1000*60)
            if interval == '4h':
                start += timedelta(minutes=1000*240)
            if interval == '6h':
                start += timedelta(minutes=1000*360)
            if interval == '1d':
                start += timedelta(minutes=1000*1440)
            startTime = datetimeToTimestamp(start)
            df2 = getCandleDataLimit(client, symbol, interval, startTime, 1000)  
            df = pd.concat([df,df2])
        
        if n %1000 == 0:
            return df
        else:
            if interval == '1m':
                start += timedelta(minutes=1000)
            if interval == '3m':
                start += timedelta(minutes=1000*3)
            if interval == '5m':
                start += timedelta(minutes=1000*5)
            if interval == '15m':
                start += timedelta(minutes=1000*15)
            if interval == '1h':
                start += timedelta(minutes=1000*60)
            if interval == '4h':
                start += timedelta(minutes=1000*240)
            if interval == '6h':
                start += timedelta(minutes=1000*360)
            if interval == '1d':
                start += timedelta(minutes=1000*1440)
            startTime = datetimeToTimestamp(start)
            df2 = getCandleDataLimit(client, symbol, interval, startTime, int(n%1000))  
            df = pd.concat([df,df2])
            return df

def strToDatetime(t):
    return datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
def datetimeToStr(t):
    return datetime.strftime(t, '%Y-%m-%d %H:%M:%S')
# for Binance Timestamp
def datetimeToTimestamp(t):
    return int(mktime(t.timetuple())*1000)
def strToTimestamp(t):
    t = strToDatetime(t)
    return int(mktime(t.timetuple())*1000)
    
def countCandle(t1, t2):
    t1 = strToDatetime(t1)
    t2 = strToDatetime(t2)
    return int((t2-t1).total_seconds() / 60)
    
    
    