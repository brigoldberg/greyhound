#!/usr/bin/env python3
# test_universe.py

import sys
import os
import numpy as np
app_path = os.path.join(os.path.expanduser('~/sandbox/greyhound/'))
sys.path.append(app_path)
from greyhound import Stock
from greyhound import Universe

symbols = ['nvda', 'spy']
date_start = '2015-01-01'
date_end = '2015-12-31'

trades = [ ['nvda', '2015-01-02', 100], ['nvda', '2015-08-27', -50],
           ['spy', '2015-06-16', 200], ['spy', '2015-11-09', -100] ]
'''
DATE        TICKER  SHARES  CLOSE
2015-01-02  nvda    100     4.83778
2015-06-16  spy     200     184.014
2015-08-27  nvda    -50     5.50764
2015-11-09  spy     -100    183.944

2015-06-01  nvda            5.42405
            spy             185.169
2015-12-31  nvda            8.0522
            spy             181.325
'''

universe = Universe(symbols, date_start, date_end, config='../config.toml')

# Load data
for trade in trades:
    ticker, dt, shares = trade
    price = universe.stocks[ticker].ohlc.loc[dt]['close']
    universe.stocks[ticker].log_trade(dt, shares, price)

def test_universe_obj_creation():
    # There should be 252 days in each stock time series.  Sum of 
    # both symbols should be 504
    total_days = 0
    for k,v in universe.stocks.items():
        total_days = total_days + len(universe.stocks[k].ohlc)

    assert total_days == 504

def test_calc_basket_share_value():
    pass
