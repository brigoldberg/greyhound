#!/usr/bin/env python3
# test_signal_ema.py

import sys
import os
import numpy as np
app_path = os.path.join(os.path.expanduser('~/sandbox/greyhound/'))
sys.path.append(app_path)
from greyhound import Stock
from greyhound import StrategyFactory

symbol = 'spy'
date_start = '2015-01-01'
date_end = '2015-12-31'
stock = Stock(symbol, date_start, date_end, config='../config.toml')

strat_factory = StrategyFactory()
strat_factory.create_strategy(stock, 'ema')

def test_ema_obj_creation():
    """ There should be 5 columns of 252 rows (5 * 252 = 1260) """
    assert stock.signals['ema'].size == 1008

def test_is_signal_loc0_nan():
    """ First record should aloways be NaN """
    stock.signals['ema'].signal.iloc[0] == 1.0

def test_is_signal_loc3_nan():
    """ Anything other than the 1st record should be a Float """
    assert np.isnan(stock.signals['ema'].signal.iloc[3]) == False
