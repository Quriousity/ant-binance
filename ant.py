import json
import pickle
import requests
import schedule

from datetime import datetime
from time import sleep

from modules.tools import getCandleRecent, getAvailableQty
from modules.order import openLongMarket, closeLong, openShortMarket, closeShort, checkOrderStatus, getCloseInfomation, getPositions
from modules.antTunnels import openLongAnt, openShortAnt, closeLongAnt, closeShortAnt

from binance.um_futures import UMFutures


# Configuration 불러오기
with open('./data/conf.json') as f:
    conf = json.load(f)
key = conf['key']
secret = conf['secret']
symbol = conf['symbol']
tp = conf['tp']
client = UMFutures(key=key, secret=secret)
t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
print(t, symbol, tp, 'Start!')
# Discord
with open('./data/discordWebhook.json') as fr:
    conf = json.load(fr)
hook = conf['URL']
if hook:
    print('Discord is ON!')

currentPositions = (0,0,0,0)
with open("./data/currentPositions.pickle", "wb") as fw:
    pickle.dump(currentPositions, fw)

switchOpenPosition = 1
switchClosePosition = 0
switchCheckClose = 0

position = getPositions(client)
if position[1] != 0 or position[3] != 0:
    switchOpenPosition = 0
    switchClosePosition = 1
    switchCheckClose = 0

with open("./data/switchOpenPosition.pickle", "wb") as fw:
    pickle.dump(switchOpenPosition, fw)
with open("./data/switchClosePosition.pickle", "wb") as fw:
    pickle.dump(switchClosePosition, fw)
with open("./data/switchCheckClose.pickle", "wb") as fw:
    pickle.dump(switchCheckClose, fw)

longAntClose = closeLongAnt()
with open("./data/longAntClose.pickle", "wb") as fw:
    pickle.dump(longAntClose, fw)
shortAntClose = closeShortAnt()
with open("./data/shortAntClose.pickle", "wb") as fw:
    pickle.dump(shortAntClose, fw)



def openPosition():
    t = datetime.now()
    if t.second == 0 or t.second == 1:
        pass
    else:
        t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        with open("./data/switchOpenPosition.pickle", "rb") as fr:
            switchOpenPosition = pickle.load(fr)
        if switchOpenPosition == 1:
            df = getCandleRecent(client, symbol, '1m', 60)
            vma = df['volume'].ewm(60).mean()
            volumePeak = df['volume'][-1]/vma[-1]
            position = df['close'][-1] - df['open'][-1]
            if volumePeak > 10:
                quantity = getAvailableQty(client, symbol)
                if position > 0:
                    openLongMarket(client, symbol, quantity)
                    message = '{} {} {}'.format(symbol, t, 'Open Long')
                    print(message)
                    requests.post(hook, {'content': message})
                elif position < 0:
                    openShortMarket(client, symbol, quantity)
                    message = '{} {} {}'.format(symbol, t, 'Open Short')
                    print(message)
                    requests.post(hook, {'content': message})
                switchOpenPosition = 0
                with open("./data/switchOpenPosition.pickle", "wb") as fw:
                    pickle.dump(switchOpenPosition, fw)
                switchClosePosition = 1
                with open("./data/switchClosePosition.pickle", "wb") as fw:
                    pickle.dump(switchClosePosition, fw)
                    

def closePosition():
    with open("./data/switchClosePosition.pickle", "rb") as fr:
        switchClosePosition = pickle.load(fr)
    if switchClosePosition == 1:
        t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        with open("./data/currentPositions.pickle", "rb") as fr:
            currentPositions = pickle.load(fr)
        newPositions = getPositions(client)

        if currentPositions != newPositions:
            client.cancel_open_orders('BTCUSDT')
            # Order (Close Long)
            if newPositions[1] != 0:
                qty = newPositions[1]
                price = round(newPositions[0]*(1+tp), 1)

                orderLong = closeLong(client, symbol, qty, price)

                longAnt = closeLongAnt()
                longAnt.orderId = orderLong['orderId']
                longAnt.size = qty
                longAnt.price = price

                with open("./data/longAntClose.pickle", "wb") as fw:
                    pickle.dump(longAnt, fw)

                message = '{} {} {}'.format(symbol, t, 'Close Long (Submitted)')
                print(message)

            # Order (Close Short)
            if newPositions[3] != 0:
                qty = -newPositions[3]
                price = round(newPositions[2]*(1-tp), 1)

                orderShort = closeShort(client, symbol, qty, price)

                shortAnt = closeShortAnt()
                shortAnt.orderId = orderShort['orderId']
                shortAnt.size = qty
                shortAnt.price = price

                with open("./data/shortAntClose.pickle", "wb") as fw:
                    pickle.dump(shortAnt, fw)

                message = '{} {} {}'.format(symbol, t, 'Close Short (Submitted)')
                print(message)

            with open("./data/currentPositions.pickle", "wb") as fw:
                pickle.dump(newPositions, fw)
            switchClosePosition = 0
            with open("./data/switchClosePosition.pickle", "wb") as fw:
                pickle.dump(switchClosePosition, fw)
            switchCheckClose = 1
            with open("./data/switchCheckClose.pickle", "wb") as fw:
                pickle.dump(switchCheckClose, fw)

def checkClose():
    with open("./data/switchCheckClose.pickle", "rb") as fr:
        switchCheckClose = pickle.load(fr)
    if switchCheckClose == 1:
        t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        with open("./data/longAntClose.pickle", "rb") as fr:
            longAnt = pickle.load(fr)
            if longAnt.orderId != 0:
                if checkOrderStatus(client, symbol, longAnt.orderId) == 'FILLED':
                    sleep(50)
                    longAnt.orderId = 0
                    with open("./data/longAntClose.pickle", "wb") as fw:
                        pickle.dump(longAnt, fw)
                    longAntOpen = openLongAnt()
                    with open("./data/longAntOpen.pickle", "wb") as fw:
                        pickle.dump(longAntOpen, fw)

                    message = '{} {} {}'.format(symbol, t, 'Close Long')
                    print(message)
                    requests.post(hook, {'content': message})
                    switchCheckClose = 0
                    with open("./data/switchCheckClose.pickle", "wb") as fw:
                        pickle.dump(switchCheckClose, fw)
                    switchOpenPosition = 1
                    with open("./data/switchOpenPosition.pickle", "wb") as fw:
                        pickle.dump(switchOpenPosition, fw)
                else:
                    qty, price = getCloseInfomation(client, symbol, longAnt.orderId)
                    price = round(price*0.9999, 1)
                    client.cancel_open_orders('BTCUSDT')

                    orderLong = closeLong(client, symbol, qty, price)
                    longAnt = closeLongAnt()
                    longAnt.orderId = orderLong['orderId']
                    longAnt.size = qty
                    longAnt.price = price

                    with open("./data/longAntClose.pickle", "wb") as fw:
                        pickle.dump(longAnt, fw)

                    message = '{} {} {}'.format(symbol, t, 'Close Long (Changed)')
                    print(message)

        with open("./data/shortAntClose.pickle", "rb") as fr:
            shortAnt = pickle.load(fr)
            if shortAnt.orderId != 0:
                if checkOrderStatus(client, symbol, shortAnt.orderId) == 'FILLED':
                    sleep(50)
                    shortAnt.orderId = 0
                    with open("./data/shortAntClose.pickle", "wb") as fw:
                        pickle.dump(shortAnt, fw)
                    shortAntOpen = openShortAnt()
                    with open("./data/shortAntOpen.pickle", "wb") as fw:
                        pickle.dump(shortAntOpen, fw)

                    message = '{} {} {}'.format(symbol, t, 'Close Short')
                    print(message)
                    requests.post(hook, {'content': message})
                    switchCheckClose = 0
                    with open("./data/switchCheckClose.pickle", "wb") as fw:
                        pickle.dump(switchCheckClose, fw)
                    switchOpenPosition = 1
                    with open("./data/switchOpenPosition.pickle", "wb") as fw:
                        pickle.dump(switchOpenPosition, fw)
                else:
                    qty, price = getCloseInfomation(client, symbol, shortAnt.orderId)
                    price = round(price*1.0001, 1)
                    client.cancel_open_orders('BTCUSDT')

                    orderShort = closeShort(client, symbol, qty, price)
                    shortAnt = closeShortAnt()
                    shortAnt.orderId = orderShort['orderId']
                    shortAnt.size = qty
                    shortAnt.price = price

                    with open("./data/shortAntClose.pickle", "wb") as fw:
                        pickle.dump(shortAnt, fw)

                    message = '{} {} {}'.format(symbol, t, 'Close Short (Changed)')
                    print(message)

# 스케줄 등록
schedule.every(1).seconds.do(openPosition)
schedule.every(1).seconds.do(closePosition)
schedule.every(1).minute.at(':59').do(checkClose)

while True:
    schedule.run_pending()
    sleep(1)