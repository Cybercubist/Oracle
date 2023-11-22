import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from collections import Counter

#define chart character and mood

class chart_nature:
        
    def __init__(self, name, scheme):
        self.name = name
        self.scheme = scheme
        
    def find_likelihood(self, skeleton):
        summ = 0
        for i in range(len(skeleton)):
            a = (self.scheme[i] - skeleton[i])**2
            summ = summ + a
        
        return (len(skeleton)-summ) * (100/len(skeleton))

#establishing our chart schemes

uptrend = chart_nature('uptrend', [0, 0.17, 0.33, 0.5, 0.67, 0.83, 1])
downtrend = chart_nature('downtrend', [1, 0.83, 0.67, 0.5, 0.33, 0.17, 0])
upburst = chart_nature('upburst', [0, 0.06, 0.12, 0.2, 0.32, 0.6, 1])
downburst = chart_nature('downburst', [1, 0.94, 0.88, 0.8, 0.68, 0.4, 0])
stagnation = chart_nature('stagnation', [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
rebound_lately = chart_nature('rebound_lately', [1, 0.8, 0.6, 0.4, 0.2, 0, 0.4])
correction_lately = chart_nature('correction_lately', [0, 0.2, 0.4, 0.6, 0.8, 1, 0.6])
up_and_calm = chart_nature('up_and_calm', [0, 0.3, 0.6, 0.9, 0.9, 0.9, 0.9])
down_and_calm = chart_nature('down_and_calm', [1, 0.7, 0.3, 0.1, 0.1, 0.1, 0.1])
down_and_up = chart_nature('down_and_up', [1, 0.66, 0.33, 0, 0.33, 0.66, 1])
up_and_down = chart_nature('up_and_down', [0, 0.33, 0.66, 1, 0.66, 0.33, 0])

chart_natures = [uptrend, downtrend, upburst, downburst, stagnation, rebound_lately, correction_lately,
                up_and_calm, down_and_calm, down_and_up, up_and_down]

#minmax filter

def MA_filter(price_list):

    MA_list = []

    for i in range (len(price_list)-19):
    
        window_list = price_list[i:i+20]
        average = sum(window_list) / 20
        MA_list.append(average)
        
    return MA_list

def minmax(price_list):
    
    list_min = min(price_list)
    list_max = max(price_list)
    minmax_list = []

    for price in price_list:
        price = (price - list_min)/(list_max - list_min)
        minmax_list.append(price)
        
    return minmax_list

#graining_filter

def graining_filter(price_list, grain_number):
    
    current_price_list = price_list.copy()
    list_min = min(current_price_list)
    list_max = max(current_price_list)

    for i in range(len(current_price_list)):
        
        current_price_list[i] = (current_price_list[i] - list_min) * 100
        
    grain_size = (list_max - list_min) / grain_number * 100
    grained_price_list = [x // grain_size * grain_size for x in current_price_list]
    
    grained_price_list2 = grained_price_list.copy()
    
    for i in range(len(grained_price_list)):
        grained_price_list2[i] = grained_price_list[i] / 100 + list_min
        
    return grained_price_list2

#find chart sceleton

def timeframe_slice(number):
    start_number = number - 1
    step = start_number // 6
    end_number = start_number % step
    
    return end_number, start_number, step

def skeleton_founder(price_list, i, j, k):

    skeleton_slice = slice(i, j+1, k)
    skeleton = price_list[skeleton_slice]
    skeleton = minmax(skeleton)

    return(skeleton)

#finding likelihood to our schemes

def find_nature(skeleton):

    final_nature = ''
    final_likelihood = 0
    likelihood_dict = {}

    for chart_nature in chart_natures:
        likelihood = chart_nature.find_likelihood(skeleton)
        if final_likelihood < likelihood:
            final_likelihood = likelihood
            final_nature = chart_nature.name
        
        likelihood_dict[chart_nature.name] = likelihood   
    
    return final_nature, final_likelihood, likelihood_dict

#define investment, speculative, tension, optimism coeffs

#1. Preprocessing

def pl_preprocessing (open_list, high_list, low_list, close_list):

    price_list = open_list + high_list + low_list + close_list
    processed_list = minmax(price_list)

    #print(processed_list)
    
    my_array = np.array(processed_list)
    my_array = my_array.reshape(4, 260)
    my_array = np.transpose(my_array)

    return my_array
    

def make_isto(array):
    
    isto_array = np.zeros((260, 4))

    for i in range(np.shape(array)[0]):
        invest_aspect = ((array[i,0] + array[i,3])/2 - array[i,2]) + ((array[i,0] + array[i,3])/2 - array[i,1])
        invest_aspect = round(invest_aspect, 3)*100
        
        spec_aspect = (array[i,3] - array[i-1,3])
        spec_aspect = round(spec_aspect, 3)*100
        
        tension_aspect = (array[i,1] - array[i,2])
        tension_aspect = round(tension_aspect, 3)*50-2
        
        optimism_aspect = (array[i,3] - array[i,0])
        optimism_aspect = round(optimism_aspect, 3)*100
        
        isto_array[i, 0] = invest_aspect
        isto_array[i, 1] = spec_aspect
        isto_array[i, 2] = tension_aspect
        isto_array[i, 3] = optimism_aspect
                      
    return isto_array

class candle_emotion:
    def __init__(self, name, number, k_growth, k_acceleration):
        self.name = name
        self.number = number
        self.k_growth = k_growth
        self.k_acceleration = k_acceleration 
        #print(k_acceleration)
        
    def process(self, isto_array, emotion_array, acceleration_array):
        
        emotion_array2 = np.copy(emotion_array)
        acceleration_array2 = np.copy(acceleration_array)
        
        for i in range(260):
                
            acceleration_array[i+1][self.number] = (acceleration_array[i][self.number] + 
                                                 + isto_array[i][self.number] * self.k_acceleration * 0.01 + 0.1)/1.2
                                                
            if acceleration_array[i+1][self.number] < 0:
                acceleration_array[i+1][self.number] = 0
                
            elif acceleration_array[i+1][self.number] > 1:
                acceleration_array[i+1][self.number] = 1
                
                
            emotion_array[i+1][self.number] = (emotion_array[i][self.number] + 
                                            + isto_array[i][self.number] * self.k_growth * 0.01 + 0.1 +
                                            + (acceleration_array[i][self.number] * 0.2-0.1))/1.2
                                            #+ 0)/1.2
            
            #print(acceleration_array[i][self.number] * 0.1-0.05)
            
            if emotion_array[i+1][self.number] < 0:
                emotion_array[i+1][self.number] = 0
                
            elif emotion_array[i+1][self.number] > 1:
                emotion_array[i+1][self.number] = 1

        return emotion_array, acceleration_array
    

def final_isto (isto_array):
    
    emotion_array = np.zeros((260, 4))
    acceleration_array = np.zeros((260, 4))
    
    emotion_array = np.insert(emotion_array, 0, 0.5, axis=0)
    acceleration_array = np.insert(acceleration_array, 0, 0.5, axis=0)

    invest_emotion = candle_emotion('invest_demand', 0, 4, 2)
    spec_emotion = candle_emotion('spec_emotion', 1, 2, 4)
    tension_emotion = candle_emotion('tension_emotion', 2, 4, 2)
    optimism_emotion = candle_emotion('optimism_emotion', 3, 4, -2)

    emotion_array, acceleration_array = invest_emotion.process(isto_array, emotion_array, acceleration_array)
    emotion_array, acceleration_array = spec_emotion.process(isto_array, emotion_array, acceleration_array)
    emotion_array, acceleration_array = tension_emotion.process(isto_array, emotion_array, acceleration_array)
    emotion_array, acceleration_array = optimism_emotion.process(isto_array, emotion_array, acceleration_array)
    
    return emotion_array

def plot_it(close_list):
    fig, ax = plt.subplots() 
    ax.plot([x for x in range (len(close_list))], close_list);

def prepare_candles(open_list, high_list, low_list, close_list):
    
    date_list = []
    for i in range (260):
        date_list.append(i)

    my_array = np.array([open_list, high_list, low_list, close_list])
    my_array = np.transpose(my_array)

    my_array = my_array.reshape(1, 1040)
    my_array_list = my_array.tolist()

    #print(my_array_list)

    my_array = np.array(my_array_list)
    my_array = my_array.reshape(260, 4)

    #building the chart

    df = pd.DataFrame(my_array, columns = ['open', 'high', 'low', 'close'])
    df.insert(loc=0, column='date', value=date_list)
    
    return df

def plot_candles(df):

    fig = go.Figure(data=[go.Candlestick(x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])])

    fig.update_traces(increasing_line_width=1, selector=dict(type='candlestick'))
    fig.update_traces(decreasing_line_width=1, selector=dict(type='candlestick'))

    fig.update_layout(yaxis = dict(
         fixedrange = False))

    fig.show()

def plot_isto(emotion_array):

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(emotion_array[211:261,0], label = 'invest')
    ax.plot(emotion_array[211:261,1], label = 'speculative')
    ax.plot(emotion_array[211:261,2], label = 'tension')
    ax.plot(emotion_array[211:261,3], label = 'optimism')

    ax.legend()
    plt.show()

def support_levels(close_list):
    
    cnt = Counter()
    for numbers in close_list:
        cnt[numbers] +=1

    result = dict(cnt)

    result = sorted(result.items(), key=lambda x:x[1], reverse=True)
    return (dict(result[0:3]))

def calculate_k(likelihood_dict1, likelihood_dict2, emotion_array):

    k = 0
    k1 = (likelihood_dict1['uptrend']*(-0.4) + likelihood_dict1['downtrend']*0.4 + likelihood_dict1['upburst']*(-0.8) +
    + likelihood_dict1['downburst']*0.6 + likelihood_dict1['stagnation']*(-0.6) + likelihood_dict1['rebound_lately']*1 +
    + likelihood_dict1['correction_lately']*(-0.8) + likelihood_dict1['up_and_calm']*(-0.6) + likelihood_dict1['down_and_calm']*1 +
    + likelihood_dict1['down_and_up']*0.4 + likelihood_dict1['up_and_down']*(-0.2)) / 100
    
    k2 = (likelihood_dict2['uptrend']*(-0.2) + likelihood_dict2['downtrend']*0.2 + likelihood_dict2['upburst']*(-0.6) +
    + likelihood_dict2['downburst']*0.2 + likelihood_dict2['stagnation']*0 + likelihood_dict2['rebound_lately']*1 +
    + likelihood_dict2['correction_lately']*(-1) + likelihood_dict2['up_and_calm']*(-0.6) + likelihood_dict2['down_and_calm']*0.8 +
    + likelihood_dict2['down_and_up']*0.6 + likelihood_dict2['up_and_down']*(-0.4)) / 100
    
    k3 = (emotion_array[260, 0] * 0.8 + emotion_array[260, 1] * (-1) + emotion_array[260, 2] * (-0.2) + emotion_array[260, 3] * 0.4) * 4
    
    k = k1 + k2 + k3

    return k1, k2, k3, k

def anomaly_eval (price_array, timeframe1, timeframe2):
    
    high_list = price_array[1]
    low_list = price_array[2]
    
    #average for timeframe1
    
    short_high_list = high_list[-timeframe1-1:-1]
    short_low_list = low_list[-timeframe1-1:-1]
    
    change_list = [short_high_list[i] - short_low_list[i] for i in range (len(short_high_list))]
    
    average_change = sum(change_list) / len(change_list)
    
    #average for timeframe2
    
    short_high_list_t2 = high_list[-timeframe2-1:-1]
    short_low_list_t2 = low_list[-timeframe2-1:-1]
    
    change_list_t2 = [short_high_list_t2[i] - short_low_list_t2[i] for i in range (len(short_high_list_t2))]
    
    average_change_t2 = sum(change_list_t2) / len(change_list_t2)
    
    #anomaly aret calculation
    
    anomaly_rate = average_change_t2 / average_change 
    
    return anomaly_rate

def plot_oracle(df, present_line):

    fig = go.Figure(data=[go.Candlestick(x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])])
    
    fig.update_layout(
        shapes = [dict(x0=present_line, x1=present_line, y0=0, y1=1, xref='x', yref='paper', line_width=2)])

    fig.update_traces(increasing_line_width=1, selector=dict(type='candlestick'))
    fig.update_traces(decreasing_line_width=1, selector=dict(type='candlestick'))

    fig.update_layout(yaxis = dict(
         fixedrange = False))

    fig.show()