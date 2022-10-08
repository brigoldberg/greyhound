#!/usr/bin/env python3
# test_universe_backtest.py

import locale
import sys
import os
import numpy as np
app_path = os.path.join(os.path.expanduser('~/sandbox/greyhound/'))
sys.path.append(app_path)
from greyhound import EMA
from greyhound import Simulation
from greyhound import Stock
from greyhound import Universe

locale.setlocale(locale.LC_ALL, 'en_US') 

date_start = '2015-01-01'
date_end   = '2015-12-31'
symbols = ['aapl', 'nvda', 'spy']

universe = Universe(symbols, date_start, date_end, config='../config.toml')

for stock in universe.stocks.keys():
    ema = EMA(universe.stocks[stock])
    sim = Simulation(universe.stocks[stock])
    sim.paper_trade('ema')

def test_universe_trades():
    assert 900.0 < universe.get_basket_pnl() < 970.0

if __name__ == '__main__':

    print(locale.currency(universe.get_basket_pnl(), grouping=True))
