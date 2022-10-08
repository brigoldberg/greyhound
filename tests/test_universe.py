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

universe = Universe(symbols, date_start, date_end, config='../config.toml')

def test_universe_obj_creation():
    # There should be 252 days in each stock time series.  Sum of all three symbols 
    # should be 504
    total_days = 0
    for k,v in universe.stocks.items():
        total_days = total_days + len(universe.stocks[k].ohlc)

    assert total_days == 504

def test_universe_pnl():
    # PnL for universe should be -$84.69. This can vary based on when you
    # pull the OHLC df because of splits, dividend calcs, etc.
    for trade_log_entry in trades:
        sym, trade_date, shares_traded = trade_log_entry
        trade_price = universe.stocks[sym].get_price(trade_date)
        universe.stocks[sym].log_trade(trade_date, shares_traded, trade_price)

    universe_pnl = universe.get_basket_pnl()
    assert -84.00 < universe_pnl < -78.00

