import requests
import json
import time

def Load_HP (ticker):

    url = 'https://api.kucoin.com'
    dateFirst = '1650499200'
    
    ts = time.time()
    ts = round(ts)
    dateLast = str(ts)

    hist_prices = requests.get(url + '/api/v1/market/candles?type=1day&symbol='+ ticker + '&startAt='+ dateFirst+ '&endAt=' + dateLast)
    hist_prices = hist_prices.json()
    hist_prices = hist_prices['data']

    data_list, open_list, high_list, low_list, close_list = [], [], [], [], []

    for i in range (260):
    
        price_word = hist_prices[i][1]
        price_float = float(price_word)
        open_list.append(price_float)
        
        price_word = hist_prices[i][3]
        price_float = float(price_word)
        high_list.append(price_float)
        
        price_word = hist_prices[i][4]
        price_float = float(price_word)
        low_list.append(price_float)
        
        price_word = hist_prices[i][2]
        price_float = float(price_word)
        close_list.append(price_float)
                                 
    open_list.reverse()
    high_list.reverse()
    low_list.reverse()
    close_list.reverse()
    
    return [open_list, high_list, low_list, close_list]