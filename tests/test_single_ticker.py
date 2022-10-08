#!/usr/bin/env python3
# test_stock.py

import sys
import os
import numpy as np
app_path = os.path.join(os.path.expanduser('~/sandbox/greyhound/'))
sys.path.append(app_path)
from greyhound import Stock

from greyhound import EMA
from greyhound import Simulation

date_start = '2015-01-01'
date_end   = '2015-12-31'
ticker = 'spy'

stock = Stock(ticker, date_start, date_end, config='../config.toml')
ema = EMA(stock)
sim = Simulation(stock)
sim.paper_trade('ema')

def test_full_run():
    assert 3.0 < stock.get_book_pnl(date_end) < 5.0

def test_trade_book_len():
    assert 30 < len(stock.get_trades()) < 34
