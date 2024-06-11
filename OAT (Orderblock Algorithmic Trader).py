# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 11:33:23 2022

@author: Grego
"""

"""
This algorithm is a variant of Complete Automated Trader that trades in both bias directions (long and short), but has the ability customize trades placed,
something that Complete Automated Trader cannot do. These two projects can be merged to form a more general algorithm that can have a specific directional 
bias as well as the ability to customize the trades placed on these order blocks.

This script is an automated trading algorithm that seeks to find candlestick patterns called "order blocks" as soon as they are formed and places
orders on them.

1. For each given ("pair", comboList) tuple, previous unfilled order blocks on that pair will be found for both directions. Then trades will be placed on each
of these order blocks.
2. Then in real time, 5 minutes after the closing time of each 1 hour candlestick (5 minutes after since the real time data is provided 5 minutes after
the start of the new hour), for each "pair", it checks if a new order block has formed; if there is a new order block, trades are placed according to comboList,
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
risk = 0.01

pair_list = [("EURUSD+", [[1,1,1]]), ("USDJPY+", [[1,0.5,0.75]]), ("AUDUSD+", [[1,1,1]]), ("GBPUSD+", [[1,0.75,1]]), ("USDCHF+", [[1,1,1]])]
# pair_list entries have the form ("pair", combo_list). combo_list entries have the form [rewardRatio, entry_depth, sl_depth] where rewardRatio
# is the reward-to-risk ratio; entry_depth is how far into the order block your entry is placed and sl_depth is how far into the order block the
# stop loss is placed.
    
def lot_size(pair, stop_loss_distance, risk):
    mt5.initialize(login=login0, password=password0, server=server0)
    balance = list(mt5.account_info())[10]
    risk_in_GBP = risk*balance
    if pair[3:6] == "GBP":
        position_size = round((risk_in_GBP)/(stop_loss_distance*100000), 2)
        return position_size
    elif pair[3:6] == "USD":
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
    
def past_block_finder(pair):
    data, meta_data = fx.get_currency_exchange_intraday(from_symbol = pair[0][0:3], to_symbol = pair[0][3:6], interval = "60min", outputsize = "full")
    idata = data.reset_index()
    order_blocks[pair[0] + "long"] = []
    order_blocks[pair[0] + "short"] = []
    lowest_lows_highest_highs[pair[0] + "long"] = []
    lowest_lows_highest_highs[pair[0] + "short"] = []
    # long
    for i in range(len(idata)-1, 1, -1):
        if idata.loc[i]["1. open"] > idata.loc[i]["4. close"]:#if it is a down candle
            j = -1
            k = -1
            m = -1
            first_close_above = i + j
            first_down_candle = i + k
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
                        order_blocks[pair[0] + "long"].append(idata.loc[i])
                        lowest_lows_highest_highs[pair[0] + "long"].append(min(lows))
                elif first_close_above == 1:#if the most recent candle closed above (it can't be filled so we take it to be an orderblock)
                    order_blocks[pair[0] + "long"].append(idata.loc[i])
                    lows = []
                    for n in range(i, first_close_above - 1, -1):
                        lows.append(idata.loc[n]["3. low"])
                    lowest_lows_highest_highs[pair[0] + "long"].append(min(lows))
                    
        elif idata.loc[i]["1. open"] < idata.loc[i]["4. close"]:#if it is an up candle
            j = -1
            k = -1
            m = -1
            first_close_below = i + j
            first_up_candle = i + k
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
                        order_blocks[pair[0] + "short"].append(idata.loc[i])
                        lowest_lows_highest_highs[pair[0] + "short"].append(max(highs))
                elif first_close_below == 1:#if the most recent candle closed below (it can't be filled so we take it to be an orderblock)
                    order_blocks[pair[0] + "short"].append(idata.loc[i])
                    highs = []
                    for n in range(i, first_close_below - 1, -1):
                        highs.append(idata.loc[n]["2. high"])
                    lowest_lows_highest_highs[pair[0] + "short"].append(max(highs))

def past_orders(pair):
    mt5.initialize(login=login0, password=password0, server=server0)
    for v in range(len(order_blocks[pair[0] + "long"])-1, -1, -1):
        block_size = order_blocks[pair[0] + "long"][v]["2. high"] - lowest_lows_highest_highs[pair[0] + "long"][v]
        for combo in pair[1]:
            sl_distance = combo[2]*block_size
            tp_distance = sl_distance*combo[0]
            entry_depth = combo[1]*block_size
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": pair[0][0:7],
                "volume": lot_size(pair[0], sl_distance, risk),
                "price": order_blocks[pair[0] + "long"][v]["2. high"] - entry_depth,
                "sl": order_blocks[pair[0] + "long"][v]["2. high"] - entry_depth - sl_distance,
                "tp": order_blocks[pair[0] + "long"][v]["2. high"] - entry_depth + tp_distance,
                "deviation": 10,
                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            mt5.order_send(request)
    for v in range(len(order_blocks[pair[0] + "short"])-1, -1, -1):
        block_size = lowest_lows_highest_highs[pair[0] + "short"][v] - order_blocks[pair[0] + "short"][v]["3. low"]
        for combo in pair[1]:
            sl_distance = combo[2]*block_size
            tp_distance = sl_distance*combo[0]
            entry_depth = combo[1]*block_size
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": pair[0][0:7],
                "volume": lot_size(pair[0], sl_distance, risk),
                "price": order_blocks[pair[0] + "short"][v]["3. low"] + entry_depth,
                "sl": order_blocks[pair[0] + "short"][v]["3. low"] + entry_depth + sl_distance,
                "tp": order_blocks[pair[0] + "short"][v]["3. low"] + entry_depth - tp_distance,
                "deviation": 10,
                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            mt5.order_send(request)
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
    potential_order_block = {}
    for pair in pair_list:
        potential_order_block[pair[0] + "long"] = ["qwerty"]
        potential_order_block[pair[0] + "short"] = ["qwerty"]
        data, meta_data = fx.get_currency_exchange_intraday(from_symbol = pair[0][0:3], to_symbol = pair[0][3:6], interval = "60min", outputsize = "compact")
        idata = data.reset_index()
        # long
        q = 1
        while idata.loc[q]["1. open"] <= idata.loc[q]["4. close"]:#Stops at index of latest down candle
            q += 1
        if q == 1:
            potential_order_block[pair[0] + "long"] = idata.loc[q]
            print("1a: most recent candle was a down candle for", pair[0] + "long")
            print("down candle found for", pair[0] + "long")
        else:
            r = 1
            while r < q and idata.loc[q-r]["4. close"] < idata.loc[q]["2. high"]:#Stops at index of first close above
                r += 1
            if r == q:#this means that the latest down candle hasn't been closed above yet
                potential_order_block[pair[0] + "long"] = idata.loc[q]
                print("1b: most recent down candle has not yet formed an orderblock for", pair[0] + "long")
                print("down candle found for", pair[0] + "long")
            else:#this means that the latest down candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                print("1c: last down candle was an orderblock (filled or unfilled) for", pair[0] + "long")
                print("awaiting down candle for", pair[0] + "long")
        # short
        while idata.loc[q]["1. open"] >= idata.loc[q]["4. close"]:#Stops at index of latest up candle
            q += 1
        if q == 1:
            potential_order_block[pair[0] + "short"] = idata.loc[q]
            print("1a: most recent candle was an up candle for", pair[0] + "short")
            print("up candle found for", pair[0] + "short")
        else:
            r = 1
            while r < q and idata.loc[q-r]["4. close"] > idata.loc[q]["3. low"]:#Stops at index of first close below
                r += 1
            if r == q:#this means that the latest up candle hasn't been closed below yet
                potential_order_block[pair[0] + "short"] = idata.loc[q]
                print("1b: most recent up candle has not yet formed an orderblock for", pair[0] + "short")
                print("up candle found for", pair[0] + "short")
            else:#this means that the latest up candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                print("1c: last up candle was an orderblock (filled or unfilled) for", pair[0] + "short")
                print("awaiting up candle for", pair[0] + "short")
        time.sleep(12)
    sched1 = BlockingScheduler()
    @sched1.scheduled_job('cron', minute = 5, second = 5, misfire_grace_time = 3599)
    def scheduled_job():
        for pair in pair_list:
            data, meta_data = fx.get_currency_exchange_intraday(from_symbol = pair[0][0:3], to_symbol = pair[0][3:6], interval = "60min", outputsize = "compact")
            idata = data.reset_index()
            # long
            if potential_order_block[pair[0] + "long"][0] == "qwerty":
                None
            elif idata.loc[1]["4. close"] >= potential_order_block[pair[0] + "long"]["2. high"]:#If it closed above the high of the last down candle
                orderblock_with_low = []
                orderblock_with_low.append(potential_order_block[pair[0] + "long"])
                lows = []
                for i in range(1, list(idata.loc[:, "date"]).index(potential_order_block[pair[0] + "long"]["date"])+1):
                    lows.append(idata.loc[i]["3. low"])
                orderblock_with_low.append(min(lows))
                #(Send orders to mt5 on this orderblock)
                mt5.initialize(login=login0, password=password0, server=server0)
                block_size = orderblock_with_low[0]["2. high"] - orderblock_with_low[1]
                for combo in pair[1]:
                    sl_distance = combo[2]*block_size
                    tp_distance = sl_distance*combo[0]
                    entry_depth = combo[1]*block_size
                    request = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": pair[0][0:7],
                        "volume": lot_size(pair[0], sl_distance, risk),
                        "price": orderblock_with_low[0]["2. high"] - entry_depth,
                        "sl": orderblock_with_low[0]["2. high"] - entry_depth - sl_distance,
                        "tp": orderblock_with_low[0]["2. high"] - entry_depth + tp_distance,
                        "deviation": 10,
                        "type": mt5.ORDER_TYPE_BUY_LIMIT,
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                    }
                    mt5.order_send(request)
                mt5.shutdown()
                print("2a: order block created; trade placed for", pair[0] + "long")
                potential_order_block[pair[0] + "long"] = ["qwerty"]
            elif idata.loc[1]["1. open"] > idata.loc[1]["4. close"]:# another down candle formed
                potential_order_block[pair[0] + "long"] = idata.loc[1]
                print("2b: potential_order_block updated for", pair[0] + "long")
            else:
                print("2c: awaiting order block for", pair[0] + "long")
            #the code below updates the potential order block
            q = 1
            while idata.loc[q]["1. open"] <= idata.loc[q]["4. close"]:#Stops at index of latest down candle
                q += 1
            if q == 1:
                potential_order_block[pair[0] + "long"] = idata.loc[q]
                print("1a: most recent candle for " + pair[0] + "long" + " was a down candle")            
            else:
                r = 1
                while r < q and idata.loc[q-r]["4. close"] < idata.loc[q]["2. high"]:#Stops at index of first close above
                    r += 1
                if r == q:#this means that the latest down candle hasn't been closed above yet
                    potential_order_block[pair[0] + "long"] = idata.loc[q]
                    print("1b: most recent down candle has not yet formed an orderblock")
                else:#this means that the latest down candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                    print("1c: last down candle for " + pair[0] + "long" + " was an orderblock (filled or unfilled).")
                    potential_order_block[pair[0] + "long"] = ["qwerty"]
            #the code below tells you whether or not a down candle has been found for a pair
            if potential_order_block[pair[0] + "long"][0] == "qwerty":
                print("awaiting down candle for", pair[0] + "long")
            else:
                print("down candle found for", pair[0] + "long")
            # short
            if potential_order_block[pair[0] + "short"][0] == "qwerty":
                None
            elif idata.loc[1]["4. close"] <= potential_order_block[pair[0] + "short"]["3. low"]:#If it closed below the low of the last up candle
                orderblock_with_high = []
                orderblock_with_high.append(potential_order_block[pair[0] + "short"])
                highs = []
                for i in range(1, list(idata.loc[:, "date"]).index(potential_order_block[pair[0] + "short"]["date"])+1):
                    highs.append(idata.loc[i]["2. high"])
                orderblock_with_high.append(max(highs))
                #(Send orders to mt5 on this orderblock)
                mt5.initialize(login=login0, password=password0, server=server0)
                block_size = orderblock_with_high[1] - orderblock_with_high[0]["3. low"]
                for combo in pair[1]:
                    sl_distance = combo[2]*block_size
                    tp_distance = sl_distance*combo[0]
                    entry_depth = combo[1]*block_size
                    request = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": pair[0][0:7],
                        "volume": lot_size(pair[0], sl_distance, risk),
                        "price": orderblock_with_high[0]["3. low"] + entry_depth,
                        "sl": orderblock_with_high[0]["3. low"] + entry_depth + sl_distance,
                        "tp": orderblock_with_high[0]["3. low"] + entry_depth - tp_distance,
                        "deviation": 10,
                        "type": mt5.ORDER_TYPE_SELL_LIMIT,
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                    }
                    mt5.order_send(request)
                mt5.shutdown()
                print("2a: order block created; trade placed for", pair[0] + "short")
                potential_order_block[pair[0] + "short"] = ["qwerty"]
            elif idata.loc[1]["1. open"] < idata.loc[1]["4. close"]:# another up candle formed
                potential_order_block[pair[0] + "short"] = idata.loc[1]
                print("2b: potential_order_block updated for", pair[0] + "short")
            else:
                print("2c: awaiting order block for", pair[0] + "short")
            #the code below updates the potential order block
            q = 1
            while idata.loc[q]["1. open"] >= idata.loc[q]["4. close"]:#Stops at index of latest up candle
                q += 1    
            if q == 1:
                potential_order_block[pair[0] + "short"] = idata.loc[q]
                print("1a: most recent candle for " + pair[0] + "short" + " was an up candle")            
            else:
                r = 1
                while r < q and idata.loc[q-r]["4. close"] > idata.loc[q]["3. low"]:#Stops at index of first close below
                    r += 1
                if r == q:#this means that the latest up candle hasn't been closed below yet
                    potential_order_block[pair[0] + "short"] = idata.loc[q]
                    print("1b: most recent up candle has not yet formed an orderblock")
                else:#this means that the latest up candle was an order block, hence the other function would have found it (or it has already been filled and we aren't going to place an order on it regardless
                    print("1c: last up candle for " + pair[0] + "short" + " was an orderblock (filled or unfilled).")
                    potential_order_block[pair[0] + "short"] = ["qwerty"]
            #the code below tells you whether or not a down candle has been found for a pair
            if potential_order_block[pair[0] + "short"][0] == "qwerty":
                print("awaiting up candle for", pair[0] + "short")
            else:
                print("up candle found for", pair[0] + "short")
            time.sleep(12)
        print(datetime.now())
        time.sleep(60)
    sched1.start()

def multitrader(pair_list):
    mt5.initialize(login=login0, password=password0, server=server0)
    for i in range(0, mt5.orders_total()):
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": mt5.orders_get()[0][0],
        }
        mt5.order_send(request)
    for pair in pair_list:
        past_block_finder(pair)
        past_orders(pair)
        time.sleep(12)
    current_multi_order_block(pair_list)
    
multitrader(pair_list)
