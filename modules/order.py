def openLong(client, symbol, qty, price):
    params = {
        'symbol': symbol,
        'side': 'BUY',
        'positionSide': 'LONG',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': qty,
        'price': price,
        }
    return client.new_order(**params)

def openLongMarket(client, symbol, qty):
    params = {
        'symbol': symbol,
        'side': 'BUY',
        'positionSide': 'LONG',
        'type': 'MARKET',
        'quantity': qty,
        }
    return client.new_order(**params)

def closeLong(client, symbol, qty, price):
    params = {
        'symbol': symbol,
        'side': 'SELL',
        'positionSide': 'LONG',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': qty,
        'price': price,
        }
    return client.new_order(**params)

def openShort(client, symbol, qty, price):
    params = {
        'symbol': symbol,
        'side': 'SELL',
        'positionSide': 'SHORT',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': qty,
        'price': price,
        }
    return client.new_order(**params)

def openShortMarket(client, symbol, qty):
    params = {
        'symbol': symbol,
        'side': 'SELL',
        'positionSide': 'SHORT',
        'type': 'MARKET',
        'quantity': qty,
        }
    return client.new_order(**params)

def closeShort(client, symbol, qty, price):
    params = {
        'symbol': symbol,
        'side': 'BUY',
        'positionSide': 'SHORT',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': qty,
        'price': price,
        }
    return client.new_order(**params)

def checkOrderStatus(client, symbol, orderId):
    return client.query_order(symbol, orderId)['status']

def getCloseInfomation(client, symbol, orderId):
    result = client.query_order(symbol, orderId)
    return float(result['origQty']), float(result['price'])

def getPositions(client):
    longP, longA = 0, 0
    shortP, shortA = 0, 0
    positions = client.account()['positions']
    for p in positions:
        if p['symbol'] == 'BTCUSDT':
            if p['positionSide'] == 'LONG':
                longP = p['entryPrice']
                longA = p['positionAmt']
            if p['positionSide'] == 'SHORT':
                shortP = p['entryPrice']
                shortA = p['positionAmt']
    return float(longP), float(longA), float(shortP), float(shortA)