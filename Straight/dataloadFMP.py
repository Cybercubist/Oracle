import requests

def Load_HP (ticker):
    
    url = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
    API_Key = 'YOUR_API_KEY'
    
    url1 = url + ticker + '?apikey=' + API_Key
    response = requests.request("GET", url1)
    hist_prices = response.json()
    hist_prices = hist_prices['historical']
    
    data_list, open_list, high_list, low_list, close_list = [], [], [], [], []
    
    for i in range (260):
        
        open_list.append(hist_prices[i]['open'])
        high_list.append(hist_prices[i]['high'])
        low_list.append(hist_prices[i]['low'])
        close_list.append(hist_prices[i]['close'])
        
    open_list.reverse()
    high_list.reverse()
    low_list.reverse()
    close_list.reverse()
    
    return [open_list, high_list, low_list, close_list]