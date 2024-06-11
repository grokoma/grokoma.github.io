# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 11:33:23 2022

@author: Grego
"""
"""
This script is an automated trading algorithm that seeks to find candlestick patterns called "order blocks" as soon as they are formed and places
orders on them.

1. For each given ("pair", "bias") tuple, previous unfilled order blocks on that pair will be found for the "bias" direction. Then trades will be placed on each
of these order blocks.
2. Then in real time, 5 minutes after the closing time of each 1 hour candlestick (5 minutes after since the real time data is provided 5 minutes after
the start of the new hour), for each ("pair", "bias") tuple, it checks if a new order block has formed; if there is a new order block, trades are placed,
otherwise it waits and updates an relevant information stored. This is repeated indefinitely.

The output of this algorithm has been replicated on RStudio code. Thus far it has been shown to be profitable under certain conditions and unprofitable in 
others.
"""




import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from alpha_vantage.foreignexchange import ForeignExchange
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

#Run this at 5 past the hour since that's when the alphavantage 1 hour data updates

api_key = "SPW17EIEP6MALOIC"
fx = ForeignExchange(key= api_key, output_format = "pandas")
#data, meta_data = fx.get_currency_exchange_intraday(from_symbol = "EUR", to_symbol = "USD", interval = "60min", outputsize = "full")
#idata = data.reset_index()
#balance = list(mt5.account_info())[10]

login0 = "Insert MT5 Login"
password0 = "Insert MT5 Password"
server0 = "Insert MT5 Broker Server"

order_blocks = {}
lowest_lows_highest_highs = {}

pair_list = [("EURUSD+s", "short"), ("EURUSD+l", "long")]
potential_order_block = {}
for i in range(len(pair_list)):
    potential_order_block[pair_list[i]] = ["qwerty"]
print(potential_order_block)
    
def lot_size(pair, stop_loss_distance, risk):
    mt5.initialize(login=login0, password=password0, server=server0)
    balance = list(mt5.account_info())[10]
    risk_in_GBP = risk*balance
    if pair[3:6] == "USD":
        GBPUSD_rate = mt5.symbol_info_tick("GBPUSD+")[1]
        position_size = round((risk_in_GBP * GBPUSD_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "JPY":
        GBPJPY_rate = mt5.symbol_info_tick("GBPJPY+")[1]
        position_size = round((risk_in_GBP * GBPJPY_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "CHF":
        GBPCHF_rate = mt5.symbol_info_tick("GBPCHF+")[1]
        position_size = round((risk_in_GBP * GBPCHF_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "CAD":
        GBPCAD_rate = mt5.symbol_info_tick("GBPCAD+")[1]
        position_size = round((risk_in_GBP * GBPCAD_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "NZD":
        GBPNZD_rate = mt5.symbol_info_tick("GBPNZD+")[1]
        position_size = round((risk_in_GBP * GBPNZD_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "AUD":
        GBPAUD_rate = mt5.symbol_info_tick("GBPAUD+")[1]
        position_size = round((risk_in_GBP * GBPAUD_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "SGD":
        GBPSGD_rate = mt5.symbol_info_tick("GBPSGD+")[1]
        position_size = round((risk_in_GBP * GBPSGD_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "CNH":
        GBPUSD_rate = mt5.symbol_info_tick("GBPUSD+")[1]
        USDCNH_rate = mt5.symbol_info_tick("USDCNH+")[1]
        position_size = round((risk_in_GBP * GBPUSD_rate * USDCNH_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "NOK":
        GBPUSD_rate = mt5.symbol_info_tick("GBPUSD+")[1]
        USDNOK_rate = mt5.symbol_info_tick("USDNOK+")[1]
        position_size = round((risk_in_GBP * GBPUSD_rate * USDNOK_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "PLN":
        GBPUSD_rate = mt5.symbol_info_tick("GBPUSD+")[1]
        USDPLN_rate = mt5.symbol_info_tick("USDPLN+")[1]
        position_size = round((risk_in_GBP * GBPUSD_rate * USDPLN_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "SEK":
        GBPUSD_rate = mt5.symbol_info_tick("GBPUSD+")[1]
        USDSEK_rate = mt5.symbol_info_tick("USDSEK+")[1]
        position_size = round((risk_in_GBP * GBPUSD_rate * USDSEK_rate)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "MXN":
        GBPUSD_rate = mt5.symbol_info_tick("GBPUSD+")[1]
        USDMXN_rate = mt5.symbol_info_tick("USDMXN+")[1]
        position_size = round((risk_in_GBP * GBPUSD_rate * USDMXN_rate)/(stop_loss_distance*100000), 2)
        return position_size
    
def past_long_block_finder(pair):
    data, meta_data = fx.get_currency_exchange_intraday(from_symbol = pair[0][0:3], to_symbol = pair[0][3:6], interval = "60min", outputsize = "full")
    idata = data.reset_index()
    for i in range(len(idata)-1, 1, -1):
        j = -1
        k = -1
        m = -1
        first_close_above = i + j
        first_down_candle = i + k
        if idata.loc[i]["1. open"] >= idata.loc[i]["4. close"]:#if it is a down candle
            while idata.loc[i+j]["4. close"] < idata.loc[i]["2. high"] and i + j > 0:#Stops at index of first close above
                j -= 1
                first_close_above = i + j
                
            while idata.loc[i+k]["1. open"] < idata.loc[i+k]["4. close"] and i + k > 0:#Stops at index of first down candle after the one at index i
                k -= 1
                first_down_candle = i + k
                
            if first_down_candle <= first_close_above and first_close_above != 0:#if it closed above at the same time or before another down candle was formed and it actually closed above
                if first_close_above > 1:
                    lows = []
                    for n in range(i, first_close_above - 1, -1):
                        lows.append(idata.loc[n]["3. low"])
                    while idata.loc[i+j+m]["3. low"] > min(lows) and i + j + m > 1:#stops at index of filling of order block
                        m -= 1
                    if idata.loc[i+j+m]["3. low"] > min(lows):#if it hasn't been filled
                        order_blocks[pair].append(idata.loc[i])
                        lowest_lows_highest_highs[pair].append(min(lows))
                elif first_close_above == 1:#if the most recent candle closed above (it can't be filled so we take it to be an orderblock)
                    order_blocks[pair].append(idata.loc[i])
                    lows = []
                    for n in range(i, first_close_above - 1, -1):
                        lows.append(idata.loc[n]["3. low"])
                    lowest_lows_highest_highs[pair].append(min(lows))

def past_long_orders(pair):
    mt5.initialize(login=login0, password=password0, server=server0)
    for v in range(len(order_blocks[pair])-1, -1, -1):
        block_size = (order_blocks[pair][v]["2. high"] - lowest_lows_highest_highs[pair][v])
        sl_distance1 = block_size*0.25
        sl_distance2 = block_size*1
        request1={
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair[0][0:7],
            "volume": lot_size(pair[0], sl_distance1, 0.01),
            "price": order_blocks[pair][v]["2. high"] - 0.5*block_size,
            "sl": order_blocks[pair][v]["2. high"] - 0.5*block_size - sl_distance1,
            "tp": order_blocks[pair][v]["2. high"] - 0.5*block_size + sl_distance1*5,
            "deviation": 10,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        request2={
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair[0][0:7],
            "volume": lot_size(pair[0], sl_distance2, 0.01),
            "price": order_blocks[pair][v]["2. high"] - 1*block_size,
            "sl": order_blocks[pair][v]["2. high"] - 1*block_size - sl_distance2,
            "tp": order_blocks[pair][v]["2. high"] - 1*block_size + 1*sl_distance2,
            "deviation": 10,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        mt5.order_send(request1)
        mt5.order_send(request2)
    mt5.shutdown()

def current_multi_order_block(pair_list):
    #Run this at 5 past the hour
    #Step 1: for each pair, find out if the last down candle is an orderblock (filled or unfilled) or not.
    #Step 2: 1 hour after step 1, a new candle has formed. If step 1 found a non-orderblock down candle,
    #       if the new candle is an up candle that closed aboved the candle from step 1, place a trade.
    #       If step 1 has found an orderblock down candle, the previous function has already placed a trade on it,
    #       so wait for a down candle to form.
    #Step 3: update the potential orderblock with the new data from step 2.
    #Repeat from step 2 with step 3 acting as step 1.
    for pair in pair_list:
        data, meta_data = fx.get_currency_exchange_intraday(from_symbol = pair[0][0:3], to_symbol = pair[0][3:6], interval = "60min", outputsize = "compact")
        idata = data.reset_index()
        if pair[1] == "long":
            #updates all of the potential order blocks in the dict
            print(potential_order_block[pair][0])
            q = 1
            while idata.loc[q]["1. open"] < idata.loc[q]["4. close"]:#Stops at index of latest down candle
                q += 1    
            if q == 1:
                potential_order_block[pair] = idata.loc[q]
                print("1a: most recent candle was a down candle for", pair[0])            
            else:
                r = 1
                while r < q and idata.loc[q-r]["4. close"] < idata.loc[q]["2. high"]:#Stops at index of first close above
                    r += 1
                if r == q:#this means that the latest down candle hasn't been closed above yet
                    potential_order_block[pair] = idata.loc[q]
                    print("1b: most recent down candle has not yet formed an orderblock for", pair[0])
                else:#this means that the latest down candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                    print("1c: last down candle was an orderblock (filled or unfilled) for", pair[0])
                    
            if potential_order_block[pair][0] == "qwerty":
                print("awaiting down candle for", pair[0])
            else:
                print("down candle found for", pair[0])
        elif pair[1] == "short":
            print(potential_order_block[pair][0])
            q = 1
            while idata.loc[q]["1. open"] > idata.loc[q]["4. close"]:#Stops at index of latest up candle
                q += 1    
            if q == 1:
                potential_order_block[pair] = idata.loc[q]
                print("1a: most recent candle was an up candle for", pair[0])            
            else:
                r = 1
                while r < q and idata.loc[q-r]["4. close"] > idata.loc[q]["3. low"]:#Stops at index of first close below
                    r += 1
                if r == q:#this means that the latest up candle hasn't been closed below yet
                    potential_order_block[pair] = idata.loc[q]
                    print("1b: most recent up candle has not yet formed an orderblock for", pair[0])
                else:#this means that the latest up candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                    print("1c: last up candle was an orderblock (filled or unfilled) for", pair[0])
            
            if potential_order_block[pair][0] == "qwerty":
                print("awaiting up candle for", pair[0])
            else:
                print("up candle found for", pair[0])
        print(potential_order_block[pair][0])
    
    sched1 = BlockingScheduler()
    @sched1.scheduled_job('cron', minute = 5)
    def scheduled_job():
        for pair in pair_list:
            #the code below checks if there is a potential order block from the last hour. If there is,
            #it will check if the candle that just closed is a down candle, in which case it will update
            #the potential order block. If not, it will check if it has closed above the potential, in 
            #which case it will place a trade. If not, it will do nothing.
            data, meta_data = fx.get_currency_exchange_intraday(from_symbol = pair[0][0:3], to_symbol = pair[0][3:6], interval = "60min", outputsize = "compact")
            idata = data.reset_index()
            if pair[1] == "long":            
                if potential_order_block[pair][0] == "qwerty":
                    None
                else:
                    orderblock_with_low = []
                    
                    if idata.iloc[1]["1. open"] >= idata.iloc[1]["4. close"]:#if the next candle is a down candle
                        potential_order_block[pair] = idata.iloc[1]
                        print("2a: potential_order_block updated for", pair[0])
                        
                    elif idata.iloc[1]["4. close"] >= potential_order_block[pair]["2. high"]:#If it closed above the high of the last down candle
                        orderblock_with_low.append(potential_order_block[pair])
                        lows = []
                        for i in range(1, list(idata.loc[:, "date"]).index(potential_order_block[pair]["date"])+1):
                            lows.append(idata.iloc[i]["3. low"])
                        orderblock_with_low.append(min(lows)) 
                        #(Send an order to mt5 on this orderblock)
                        mt5.initialize(login=login0, password=password0, server=server0)
                        block_size = orderblock_with_low[0]["2. high"] - orderblock_with_low[1]
                        sl_distance1 = block_size*0.25
                        sl_distance2 = block_size*1
                        request1={
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": pair[0][0:7],
                            "volume": lot_size(pair[0], sl_distance1, 0.01),
                            "price": orderblock_with_low[0]["2. high"] - 0.5*block_size,
                            "sl": orderblock_with_low[0]["2. high"] - 0.5*block_size - sl_distance1,
                            "tp": orderblock_with_low[0]["2. high"] - 0.5*block_size + 5*sl_distance1,
                            "deviation": 10,
                            "type": mt5.ORDER_TYPE_BUY_LIMIT,
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_RETURN,
                            }
                        
                        request2={
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": pair[0][0:7],
                            "volume": lot_size(pair[0], sl_distance2, 0.01),
                            "price": orderblock_with_low[0]["2. high"] - 1*block_size,
                            "sl": orderblock_with_low[0]["2. high"] - 1*block_size - sl_distance2,
                            "tp": orderblock_with_low[0]["2. high"] - 1*block_size + 1*sl_distance2,
                            "deviation": 10,
                            "type": mt5.ORDER_TYPE_BUY_LIMIT,
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_RETURN,
                            }
                        mt5.order_send(request1)
                        mt5.order_send(request2)
                        mt5.shutdown()
                        print("2b: order block created; trade placed for", pair[0])
                        potential_order_block[pair] = ["qwerty"]
                    else:#this means it is an up candle that hasn't closed above the last down candle
                        print("2c: awaiting order block for", pair[0])
                        
                #the code below updates the potential order block      
                q = 1
                while idata.loc[q]["1. open"] < idata.loc[q]["4. close"]:#Stops at index of latest down candle
                    q += 1    
                if q == 1:
                    potential_order_block[pair] = idata.loc[q]
                    print("1a: most recent candle for " + pair[0] + " was a down candle")            
                else:
                    r = 1
                    while r < q and idata.loc[q-r]["4. close"] < idata.loc[q]["2. high"]:#Stops at index of first close above
                        r += 1
                    if r == q:#this means that the latest down candle hasn't been closed above yet
                        potential_order_block[pair] = idata.loc[q]
                        print("1b: most recent down candle has not yet formed an orderblock")
                    else:#this means that the latest down candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                        print("1c: last down candle for " + pair[0] + " was an orderblock (filled or unfilled).")
                        potential_order_block[pair] = ["qwerty"]
                          
                #the code below tells you whether or not a down candle has been found for a pair
                if potential_order_block[pair][0] == "qwerty":
                    print("awaiting down candle for", pair[0])
                else:
                    print("down candle found for", pair[0])
            elif pair[1] == "short":
                if potential_order_block[pair][0] == "qwerty":
                    None
                else:
                    orderblock_with_high = []
                    
                    if idata.iloc[1]["1. open"] <= idata.iloc[1]["4. close"]:#if the next candle is an up candle
                        potential_order_block[pair] = idata.iloc[1]
                        print("2a: potential_order_block updated for", pair[0])
                        
                    elif idata.iloc[1]["4. close"] <= potential_order_block[pair]["3. low"]:#If it closed below the low of the last up candle
                        orderblock_with_high.append(potential_order_block[pair])
                        highs = []
                        for i in range(1, list(idata.loc[:, "date"]).index(potential_order_block[pair]["date"])+1):
                            highs.append(idata.iloc[i]["2. high"])
                        orderblock_with_high.append(max(highs)) 
                        #(Send an order to mt5 on this orderblock)
                        mt5.initialize(login=login0, password=password0, server=server0)
                        block_size = orderblock_with_high[1] - orderblock_with_high[0]["3. low"]
                        sl_distance1 = block_size*0.25
                        sl_distance2 = block_size*1
                        request1={
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": pair[0][0:7],
                            "volume": lot_size(pair[0], sl_distance1, 0.01),
                            "price": orderblock_with_high[0]["3. low"] + 0.5*block_size,
                            "sl": orderblock_with_high[0]["3. low"] + 0.5*block_size + sl_distance1,
                            "tp": orderblock_with_high[0]["3. low"] + 0.5*block_size - 5*sl_distance1,
                            "deviation": 10,
                            "type": mt5.ORDER_TYPE_SELL_LIMIT,
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_RETURN,
                            }
                        
                        request2={
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": pair[0][0:7],
                            "volume": lot_size(pair[0], sl_distance2, 0.01),
                            "price": orderblock_with_high[0]["3. low"] + 1*block_size,
                            "sl": orderblock_with_high[0]["3. low"] + 1*block_size + sl_distance2,
                            "tp": orderblock_with_high[0]["3. low"] + 1*block_size - 1*sl_distance2,
                            "deviation": 10,
                            "type": mt5.ORDER_TYPE_SELL_LIMIT,
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_RETURN,
                            }
                        mt5.order_send(request1)
                        mt5.order_send(request2)
                        mt5.shutdown()
                        print("2b: order block created; trade placed for", pair[0])
                        potential_order_block[pair] = ["qwerty"]
                    else:#this means it is an up candle that hasn't closed above the last down candle
                        print("2c: awaiting order block for", pair[0])
                        
                #the code below updates the potential order block      
                q = 1
                while idata.loc[q]["1. open"] > idata.loc[q]["4. close"]:#Stops at index of latest up candle
                    q += 1    
                if q == 1:
                    potential_order_block[pair] = idata.loc[q]
                    print("1a: most recent candle for " + pair[0] + " was an up candle")            
                else:
                    r = 1
                    while r < q and idata.loc[q-r]["4. close"] > idata.loc[q]["3. low"]:#Stops at index of first close below
                        r += 1
                    if r == q:#this means that the latest up candle hasn't been closed below yet
                        potential_order_block[pair] = idata.loc[q]
                        print("1b: most recent up candle has not yet formed an orderblock for", pair[0])
                    else:#this means that the latest up candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                        print("1c: last up candle for " + pair[0] + " was an orderblock (filled or unfilled).")
                        potential_order_block[pair] = ["qwerty"]
                        
                #the code below tells you whether or not a down candle has been found for a pair
                if potential_order_block[pair][0] == "qwerty":
                    print("awaiting up candle for", pair[0])
                else:
                    print("up candle found for", pair[0])
        print(datetime.now())
        sched2 = BlockingScheduler()
        @sched2.scheduled_job('interval', hours=1)
        def timed_job():
            for pair in pair_list:
                #the code below checks if there is a potential order block from the last hour. If there is,
                #it will check if the candle that just closed is a down candle, in which case it will update
                #the potential order block. If not, it will check if it has closed above the potential, in 
                #which case it will place a trade. If not, it will do nothing.
                data, meta_data = fx.get_currency_exchange_intraday(from_symbol = pair[0][0:3], to_symbol = pair[0][3:6], interval = "60min", outputsize = "compact")
                idata = data.reset_index()
                if pair[1] == "long":            
                    if potential_order_block[pair][0] == "qwerty":
                        None
                    else:
                        orderblock_with_low = []
                        
                        if idata.iloc[1]["1. open"] >= idata.iloc[1]["4. close"]:#if the next candle is a down candle
                            potential_order_block[pair] = idata.iloc[1]
                            print("2a: potential_order_block updated for", pair[0])
                            
                        elif idata.iloc[1]["4. close"] >= potential_order_block[pair]["2. high"]:#If it closed above the high of the last down candle
                            orderblock_with_low.append(potential_order_block[pair])
                            lows = []
                            for i in range(1, list(idata.loc[:, "date"]).index(potential_order_block[pair]["date"])+1):
                                lows.append(idata.iloc[i]["3. low"])
                            orderblock_with_low.append(min(lows)) 
                            #(Send an order to mt5 on this orderblock)
                            mt5.initialize(login=login0, password=password0, server=server0)
                            block_size = orderblock_with_low[0]["2. high"] - orderblock_with_low[1]
                            sl_distance1 = block_size*0.25
                            sl_distance2 = block_size*1
                            request1={
                                "action": mt5.TRADE_ACTION_PENDING,
                                "symbol": pair[0][0:7],
                                "volume": lot_size(pair[0], sl_distance1, 0.01),
                                "price": orderblock_with_low[0]["2. high"] - 0.5*block_size,
                                "sl": orderblock_with_low[0]["2. high"] - 0.5*block_size - sl_distance1,
                                "tp": orderblock_with_low[0]["2. high"] - 0.5*block_size + 5*sl_distance1,
                                "deviation": 10,
                                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_RETURN,
                                }
                            
                            request2={
                                "action": mt5.TRADE_ACTION_PENDING,
                                "symbol": pair[0][0:7],
                                "volume": lot_size(pair[0], sl_distance2, 0.01),
                                "price": orderblock_with_low[0]["2. high"] - 1*block_size,
                                "sl": orderblock_with_low[0]["2. high"] - 1*block_size - sl_distance2,
                                "tp": orderblock_with_low[0]["2. high"] - 1*block_size + 1*sl_distance2,
                                "deviation": 10,
                                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_RETURN,
                                }
                            mt5.order_send(request1)
                            mt5.order_send(request2)
                            mt5.shutdown()
                            print("2b: order block created; trade placed for", pair[0])
                            potential_order_block[pair] = ["qwerty"]
                        else:#this means it is an up candle that hasn't closed above the last down candle
                            print("2c: awaiting order block for", pair[0])
                            
                    #the code below updates the potential order block      
                    q = 1
                    while idata.loc[q]["1. open"] < idata.loc[q]["4. close"]:#Stops at index of latest down candle
                        q += 1    
                    if q == 1:
                        potential_order_block[pair] = idata.loc[q]
                        print("1a: most recent candle for " + pair[0] + " was a down candle")            
                    else:
                        r = 1
                        while r < q and idata.loc[q-r]["4. close"] < idata.loc[q]["2. high"]:#Stops at index of first close above
                            r += 1
                        if r == q:#this means that the latest down candle hasn't been closed above yet
                            potential_order_block[pair] = idata.loc[q]
                            print("1b: most recent down candle has not yet formed an orderblock")
                        else:#this means that the latest down candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                            print("1c: last down candle for " + pair[0] + " was an orderblock (filled or unfilled).")
                            potential_order_block[pair] = ["qwerty"]
                              
                    #the code below tells you whether or not a down candle has been found for a pair
                    if potential_order_block[pair][0] == "qwerty":
                        print("awaiting down candle for", pair[0])
                    else:
                        print("down candle found for", pair[0])
                elif pair[1] == "short":
                    if potential_order_block[pair][0] == "qwerty":
                        None
                    else:
                        orderblock_with_high = []
                        
                        if idata.iloc[1]["1. open"] <= idata.iloc[1]["4. close"]:#if the next candle is an up candle
                            potential_order_block[pair] = idata.iloc[1]
                            print("2a: potential_order_block updated for", pair[0])
                            
                        elif idata.iloc[1]["4. close"] <= potential_order_block[pair]["3. low"]:#If it closed below the low of the last up candle
                            orderblock_with_high.append(potential_order_block[pair])
                            highs = []
                            for i in range(1, list(idata.loc[:, "date"]).index(potential_order_block[pair]["date"])+1):
                                highs.append(idata.iloc[i]["2. high"])
                            orderblock_with_high.append(max(highs)) 
                            #(Send an order to mt5 on this orderblock)
                            mt5.initialize(login=login0, password=password0, server=server0)
                            block_size = orderblock_with_high[1] - orderblock_with_high[0]["3. low"]
                            sl_distance1 = block_size*0.25
                            sl_distance2 = block_size*1
                            request1={
                                "action": mt5.TRADE_ACTION_PENDING,
                                "symbol": pair[0][0:7],
                                "volume": lot_size(pair[0], sl_distance1, 0.01),
                                "price": orderblock_with_high[0]["3. low"] + 0.5*block_size,
                                "sl": orderblock_with_high[0]["3. low"] + 0.5*block_size + sl_distance1,
                                "tp": orderblock_with_high[0]["3. low"] + 0.5*block_size - 5*sl_distance1,
                                "deviation": 10,
                                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_RETURN,
                                }
                            
                            request2={
                                "action": mt5.TRADE_ACTION_PENDING,
                                "symbol": pair[0][0:7],
                                "volume": lot_size(pair[0], sl_distance2, 0.01),
                                "price": orderblock_with_high[0]["3. low"] + 1*block_size,
                                "sl": orderblock_with_high[0]["3. low"] + 1*block_size + sl_distance2,
                                "tp": orderblock_with_high[0]["3. low"] + 1*block_size - 1*sl_distance2,
                                "deviation": 10,
                                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_RETURN,
                                }
                            mt5.order_send(request1)
                            mt5.order_send(request2)
                            mt5.shutdown()
                            print("2b: order block created; trade placed for", pair[0])
                            potential_order_block[pair] = ["qwerty"]
                        else:#this means it is an up candle that hasn't closed above the last down candle
                            print("2c: awaiting order block for", pair[0])
                            
                    #the code below updates the potential order block      
                    q = 1
                    while idata.loc[q]["1. open"] > idata.loc[q]["4. close"]:#Stops at index of latest up candle
                        q += 1    
                    if q == 1:
                        potential_order_block[pair] = idata.loc[q]
                        print("1a: most recent candle for " + pair[0] + " was an up candle")            
                    else:
                        r = 1
                        while r < q and idata.loc[q-r]["4. close"] > idata.loc[q]["3. low"]:#Stops at index of first close below
                            r += 1
                        if r == q:#this means that the latest up candle hasn't been closed below yet
                            potential_order_block[pair] = idata.loc[q]
                            print("1b: most recent up candle has not yet formed an orderblock for", pair[0])
                        else:#this means that the latest up candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                            print("1c: last up candle for " + pair[0] + " was an orderblock (filled or unfilled).")
                            potential_order_block[pair] = ["qwerty"]
                            
                    #the code below tells you whether or not a down candle has been found for a pair
                    if potential_order_block[pair][0] == "qwerty":
                        print("awaiting up candle for", pair[0])
                    else:
                        print("up candle found for", pair[0])
            print(datetime.now())
        sched2.start()    
    sched1.start()

def past_short_block_finder(pair):
    data, meta_data = fx.get_currency_exchange_intraday(from_symbol = pair[0][0:3], to_symbol = pair[0][3:6], interval = "60min", outputsize = "full")
    idata = data.reset_index()
    for i in range(len(idata)-1, 1, -1):
        j = -1
        k = -1
        m = -1
        first_close_below = i + j
        first_up_candle = i + k
        if idata.loc[i]["1. open"] <= idata.loc[i]["4. close"]:#if it is an up candle
            while idata.loc[i+j]["4. close"] > idata.loc[i]["3. low"] and i + j > 0:#Stops at index of first close below
                j -= 1
                first_close_below = i + j
                
            while idata.loc[i+k]["1. open"] > idata.loc[i+k]["4. close"] and i + k > 0:#Stops at index of first up candle after the one at index i
                k -= 1
                first_up_candle = i + k
                
            if first_up_candle <= first_close_below and first_close_below != 0:#if it closed below at the same time or before another up candle was formed and it actually closed below
                if first_close_below > 1:
                    highs = []
                    for n in range(i, first_close_below - 1, -1):
                        highs.append(idata.loc[n]["2. high"])
                    while idata.loc[i+j+m]["2. high"] < max(highs) and i + j + m > 1:#stops at index of filling of order block
                        m -= 1
                    if idata.loc[i+j+m]["2. high"] < max(highs):#if it hasn't been filled
                        order_blocks[pair].append(idata.loc[i])
                        lowest_lows_highest_highs[pair].append(max(highs))
                elif first_close_below == 1:#if the most recent candle closed below (it can't be filled so we take it to be an orderblock)
                    order_blocks[pair].append(idata.loc[i])
                    highs = []
                    for n in range(i, first_close_below - 1, -1):
                        highs.append(idata.loc[n]["2. high"])
                    lowest_lows_highest_highs[pair].append(max(highs))

def past_short_orders(pair):
    mt5.initialize(login=login0, password=password0, server=server0)
    for v in range(len(order_blocks[pair])-1, -1, -1):
        block_size = (lowest_lows_highest_highs[pair][v] - order_blocks[pair][v]["3. low"])
        sl_distance1 = block_size*0.25
        sl_distance2 = block_size*1
        request1={
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair[0][0:7],
            "volume": lot_size(pair[0], sl_distance1, 0.01),
            "price": order_blocks[pair][v]["3. low"] + 0.5*block_size,
            "sl": order_blocks[pair][v]["3. low"] + 0.5*block_size + sl_distance1,
            "tp": order_blocks[pair][v]["3. low"] + 0.5*block_size - 5*sl_distance1,
            "deviation": 10,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        request2={
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair[0][0:7],
            "volume": lot_size(pair[0], sl_distance2, 0.01),
            "price": order_blocks[pair][v]["3. low"] + 1*block_size,
            "sl": order_blocks[pair][v]["3. low"] + 1*block_size + sl_distance2,
            "tp": order_blocks[pair][v]["3. low"] + 1*block_size - 1*sl_distance2,
            "deviation": 10,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        mt5.order_send(request1)
        mt5.order_send(request2)
    mt5.shutdown()

def multitrader(pair_list):
    
    for pair in pair_list:
        order_blocks[pair] = []
        lowest_lows_highest_highs[pair] = []
        
    for pair in pair_list:
        if pair[1] == "long":
            past_long_block_finder(pair)
            past_long_orders(pair)
        elif pair[1] == "short":
            past_short_block_finder(pair)
            past_short_orders(pair)
    
    current_multi_order_block(pair_list)
    
multitrader(pair_list)
