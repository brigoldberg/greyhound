#!/usr/bin/env python3
# test_stock.py

import sys
import os
from pytest import approx
app_path = os.path.join(os.path.expanduser('~/sandbox/greyhound/'))
sys.path.append(app_path)
from greyhound import Stock


symbol = 'spy'
date_start = '2015-01-01'
date_end = '2015-01-31'
trades = {
    '2015-01-02': 50,
    '2015-01-07': -50,
    '2015-01-12': 56,
    '2015-01-21': -56,
    '2015-01-27': 56 }
"""
DATE        PRICE
2015-01-02  179.005
2015-01-07  176.267
2015-01-12  176.566
2015-01-21  176.984
2015-01-27  176.655
"""

stock = Stock(symbol, date_start, date_end, config='../config.toml')

#------------------------------------#
#   Stock object unit tests
#------------------------------------#
def test_stock_obj_creation():
    """ This tests:
          - Object initialization
          - reading config
          - loading OHLC
          - snipping dates
    """
    assert len(stock.ohlc) == 20 


def test_tick_data():
    """ Test fetching stock price from OHLC DF """
    assert stock.ohlc.loc['2015-01-20']['high'] == 176.636 


def test_log_trade():
    """ 
    Log trades and confirm held share count and trade cost
    is correct.
    """
    for trade_date, shares in trades.items():
        stock_price = stock.ohlc.loc[trade_date]['close']
        stock.log_trade(trade_date, shares, stock_price)

    shares = stock.trade_log['shares'].sum()
    trade_cost_sum = stock.trade_log['trade_cost'].sum() 

    assert shares == 56 and trade_cost_sum == approx(-10006, rel=1)

def test_get_held_share_value():
    """
    Check calculation of the value of held shares at a specific date.
    """
    test_result = []
    test_result.append(stock.get_held_share_value('2015-01-15'))
    test_result.append(stock.get_held_share_value())

    assert test_result == approx([9731.6, 9711.5], rel=1)


def test_get_cash_position():
    """
    Check returned cash position.
    """
    test_result = []
    for dt in ['2015-01-15', '2015-01-22']:
        test_result.append(stock.trade_log.loc[:dt]['trade_cost'].sum())

    assert test_result == approx([-10024.6, -113.5], rel=1)


def test_get_max_drawdown():
    """
    Check for lowest cash position throughout trading date range
    """
    test_result = []
    for dt in ['2015-01-06', '2015-01-15', '2015-01-22']:
        test_result.append(stock.get_max_drawdown(dt))
    
    assert test_result == approx([-8950, -10025, -10025], rel=1)


def test_calc_pnl():
    """
    Check PnL of traded symbol at various dates
    """
    test_result = []
    for dt in ['2015-01-02', '2015-01-12', '2015-01-21', '2015-01-30']:
        test_result.append(stock.calc_pnl(dt))

    assert test_result == approx([0.0, -136.9, -113.5, -274.6], rel=1)
