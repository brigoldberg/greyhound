#!/usr/bin/env python3
# test_stock.py

import sys
import os
import numpy as np
app_path = os.path.join(os.path.expanduser('~/sandbox/greyhound/'))
sys.path.append(app_path)
from greyhound import Stock


symbol = 'spy'
date_start = '2015-01-01'
date_end = '2015-12-31'
trades = {
    '2015-01-02': 250,
    '2015-08-27': -100,
    '2015-10-02': 75 }

stock = Stock(symbol, date_start, date_end, config='../config.toml')

def test_stock_obj_creation():
    """ This tests:
          - Object initialization
          - reading config
          - loading OHLC
          - snipping dates
    """
    assert len(stock.ohlc) == 252 and len(stock.trade_log)

def test_get_price():
    """ Test fetching stock price from OHLC DF """
    assert stock.get_price('2015-03-20', col_name='high') == 184.671

def test_log_trade():
    """ Log 3 trades and confirm data exists and is correct. """
    for trade_date, shares in trades.items():
        stock_price = stock.ohlc.loc[trade_date]['close']
        stock.log_trade(trade_date, shares, stock_price)

    assert stock.trade_log.shares.sum() == 225

def test_get_book_cost():
    """ Calc cost of purchased stock at date in middle of trade log. """
    #assert stock.get_book_cost('2015-09-15') == 40600.25
    assert 27000 < stock.get_book_cost('2015-09-15') < 28000.00

def test_get_book_value():
    """ Calc total book value at end of year. """
    assert 40000.00 < stock.get_book_value('2015-12-31') < 42000.00

def test_get_book_pnl():
    """ Test PnL of held positions. """
    assert  630.00 < stock.get_book_pnl('2015-12-31') <  650.00
