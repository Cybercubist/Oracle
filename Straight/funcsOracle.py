import dataloadFMP as dataload
import funcs as funcs
import numpy as np
import pandas as pd
import random

def calculate_volatility(price_array):

    df_old = price_array

    old_open_list = df_old['open'].values.tolist()
    old_close_list = df_old['close'].values.tolist()
    old_high_list = df_old['high'].values.tolist()
    old_low_list = df_old['low'].values.tolist()

    #AVERAGE DIFF

    diff_list = []

    for i in range (len(old_close_list)-1):

        price_diff = old_close_list[i+1] / old_close_list[i] - 1
        diff_list.append(price_diff)

    average_diff = sum(diff_list) / len(diff_list)

    #AVERAGE GAP

    gap_list = []

    for i in range (len(old_close_list)-1):

        price_gap = abs(old_open_list[i+1] - old_close_list[i]) / old_close_list[i] 
        gap_list.append(price_gap)

    average_gap = sum(gap_list) / len(gap_list)

    #AVERAGE SMALL VOLATILITY

    low_volatility_list = []

    for i in range (len(old_close_list)):

        low_price_volatility = abs(old_close_list[i] - old_open_list[i]) / old_open_list[i]   
        low_volatility_list.append(low_price_volatility)

    average_low_volatility = sum(low_volatility_list) / len(low_volatility_list)

    #AVERAGE HIGH VOLATILITY

    high_volatility_list = []

    for i in range (len(old_high_list)):

        high_price_volatility = abs(old_high_list[i] - old_low_list[i]) / old_low_list[i]     
        high_volatility_list.append(high_price_volatility)

    average_high_volatility = sum(high_volatility_list) / len(high_volatility_list)

    #30D VOLATILITY

    print(max(old_high_list[210:260]), min(old_low_list[210:260]))
    monthly_volatility = max(old_high_list[210:260])/min(old_low_list[210:260])-1
    
    volatility_list = [average_diff, average_gap, average_low_volatility, average_high_volatility, monthly_volatility]
    
    return volatility_list

def define_main_chart(CH_result, volatility_list):

    ustt_formula = CH_result[2] / 5 * 2.1 + CH_result[1] / 5 * 0.9
    current_price = CH_result[3]['close'][259]
    main_ustt = [i * volatility_list[2]  * ustt_formula for i in range (5)]

    stt_formula = CH_result[2] / 5 * 0.9 + CH_result[1] / 5 * 1.5 + CH_result[0] / 5 * 0.6 
    short_term_trend = [i * volatility_list[2] * stt_formula for i in range (5)]

    mtt_formula = CH_result[2] / 5 * 0.6 + CH_result[1] / 5 * 0.9 + CH_result[0] / 5 * 1.5
    mid_term_trend = [i * volatility_list[2] * mtt_formula for i in range (5)]

    united_main = main_ustt.copy()

    trend_number = 0

    for i in range(15):
    
        step1 = short_term_trend[4] / 5
    
        trend_number = trend_number + step1
        united_main.append(trend_number+united_main[4])

    trend_number = 0

    for i in range(30):
    
        step1 = mid_term_trend[4] / 10
    
        trend_number = trend_number + step1
        united_main.append(trend_number+united_main[19])

    print('united main:', united_main)
    
    return(united_main)

def add_fair_price(CH_result, united_main, fair_price):
    
    current_price = CH_result[3]['close'][259]
    distance_to_fp = (fair_price/current_price - 1)
    
    united_main_faired = []
    
    for i in range(len(united_main)):
        fp_balancer = (distance_to_fp - united_main[i])/200 #fair price in 200 days
        faired_price = united_main[i] + fp_balancer*i
        united_main_faired.append(faired_price)
        
    print('united main faired:', united_main_faired)

    funcs.plot_it(united_main_faired)
        
    return united_main_faired

def intraday_volatility(volatility_list):

    intraday_volatility_list = []

    for i in range(50):
    
        random_number = random.randint(-5, 5)
        random_movement = volatility_list[2] * random_number / 5
    
        intraday_volatility_list.append(random_movement)
    
    return intraday_volatility_list

def monthly_volatility(volatility_list):

    monthly_volatility_list = []

    for i in range(5):

        random_number = random.randint(-10, 10)
        random_movement = volatility_list[4] * random_number / 20
    
        monthly_volatility_list.append(random_movement)

    final_monthly_volatility = []
    volatility = 0

    for i in range (5):
    
        if i == 0:
        
            step = (monthly_volatility_list[i]-0)/10
        
        else:
     
            step = (monthly_volatility_list[i]-monthly_volatility_list[i-1])/10
    
        print(step)
    
        for j in range (10):
        
            volatility = volatility + step
            final_monthly_volatility.append(volatility)
        
    return final_monthly_volatility

def randomize_price_list(united_main, intraday_volatility_list, final_monthly_volatility):

    randomized_price_list = []

    for i in range(50):
    
        a = united_main[i] + intraday_volatility_list[i] + final_monthly_volatility[i]
        randomized_price_list.append(a)
    
    return randomized_price_list

def make_ohcl(randomized_price_list, volatility_list):

    print(randomized_price_list)

    open_list = randomized_price_list[0:49].copy()
    close_list = randomized_price_list[0:50].copy()

    open_list.insert(0, 0)

    print(open_list, close_list)
    
    def add_gaps(close_list, volatility_list):
        
        new_close_list = []
        
        for i in range (len(close_list)):
            
            gapped_price = close_list[i] + random.randint(-10, 10) * volatility_list[1] / 10
            
            new_close_list.append(gapped_price)
            
        return new_close_list
    
    gapped_close_list = add_gaps(close_list, volatility_list)

    def add_highs(open_list, close_list):
    
        high_list, low_list = [], []
    
        for i in range (len(open_list)):
        
            if open_list[i] > close_list[i]:
            
                high_price = open_list[i] + random.randint(0, 10) * (volatility_list[3] - volatility_list[2]) / 10
                low_price = close_list[i] - random.randint(0, 10) * (volatility_list[3] - volatility_list[2]) / 10
            
                high_list.append(high_price)
                low_list.append(low_price)
            
            else:
            
                high_price = close_list[i] + random.randint(0, 10) * (volatility_list[3] - volatility_list[2]) / 10
                low_price = open_list[i] - random.randint(0, 10) * (volatility_list[3] - volatility_list[2]) / 10
            
                high_list.append(high_price)
                low_list.append(low_price)
    
        return high_list, low_list

    high_list, low_list = add_highs(open_list, gapped_close_list)
    
    ohcl_list = [open_list, high_list, low_list, gapped_close_list]
    
    return ohcl_list

def add_price(CH_result, ohcl_list):
    
    last_price = CH_result[3]['close'][259]
    print(last_price)

    final_open_list = [ohcl_list[0][i] * last_price + last_price for i in range(len(ohcl_list[0]))]
    final_close_list = [ohcl_list[3][i] * last_price + last_price for i in range(len(ohcl_list[3]))]
    final_high_list = [ohcl_list[1][i] * last_price + last_price for i in range(len(ohcl_list[1]))]
    final_low_list = [ohcl_list[2][i] * last_price + last_price for i in range(len(ohcl_list[2]))]
    
    final_ohcl_list = [final_open_list, final_high_list, final_low_list, final_close_list]
    
    return(final_ohcl_list)

def make_df(final_ohcl_list):
    
    my_array = np.array([final_ohcl_list[0], final_ohcl_list[1], final_ohcl_list[2], final_ohcl_list[3]])
    my_array = np.transpose(my_array)

    date_list = [i+260 for i in range (50)]

    df_new = pd.DataFrame(my_array, columns = ['open', 'high', 'low', 'close'])
    df_new.insert(loc=0, column='date', value=date_list)

    return df_new

def concat_charts(CH_result, df_new):

    print(CH_result[3])
    print(df_new)

    df_final = pd.concat([CH_result[3], df_new])

    return df_final