#!/usr/bin/env python3
# test_simulation.py

import sys
import os
import pandas as pd
app_path = os.path.join(os.path.expanduser('~/sandbox/greyhound/'))
sys.path.append(app_path)
from greyhound import Stock
from greyhound import Simulation

# create stock obj and load data
symbol = 'spy'
date_start = '2015-01-01'
date_end = '2015-12-31'
stock = Stock(symbol, date_start, date_end, config='../config.toml')

# load singals into stock object for testing
stock.signals['ema'] = pd.DataFrame(index=stock.ohlc.index, dtype='float64')
stock.signals['ema']['signal'] = 0
signals = {
    '2015-01-21': 1,    # 178.93
    '2015-02-11': -1,   # 182.29
    '2015-05-12': 1,    # 185.82
    '2015-07-20': -1,    # 189.04
    }

for k,v in signals.items():
    stock.signals['ema']['signal'].loc[v] = v

# load trades into stock object
trades = {
    '2015-01-21': 30,
    '2015-02-11': -30,
    '2015-05-12': 2000,
    '2015-07-20': -30
    }

for trade_date, shares in trades.items():
    stock_price = stock.ohlc.loc[k]['close']
    stock.log_trade(trade_date, shares, stock_price)

sim = Simulation(stock)

def test_risk_check_buy():
    """
    Given exising positions in the trade_log, calculate the ability to perform a risk
    check with a buy signal on a specific date.
    """
    assert 25 < sim._risk_check('buy', '2015-01-28') < 32

def test_risk_check_buy_no_shares():
    """
    Already have too many shares, do not add to position.
    """
    assert sim._risk_check('buy', '2015-05-14') == 0

def test_risk_check_sell():
    """
    Given existing positions in the trade_log, calculate the amount of shares to
    transact if a sell signale is generated
    """
    assert 24 < sim._risk_check('sell', '2015-01-28') < 32

