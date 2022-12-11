#!/usr/bin/env python3
# stock-backtest.py

import argparse
import locale
import sys
import os

app_path = os.path.join(os.path.expanduser('~/sandbox/greyhound/'))
sys.path.append(app_path)
from greyhound import Simulation
from greyhound import StrategyFactory
from greyhound import Stock

locale.setlocale(locale.LC_ALL, 'en_US')

DATE_START = '2014-01-01'
DATE_END   = '2021-06-30'

def cli_args():
    parser = argparse.ArgumentParser(description='MuliProc Dogger')
    parser.add_argument('-s', dest='symbol', action='store', required=True)
    parser.add_argument('-c', dest='config', action='store', required=True)
    return parser.parse_args()

def display_pnl(ticker):
    pnl = locale.currency(ticker.calc_pnl(), grouping=True)
    max_draw = locale.currency(ticker.get_max_drawdown(), grouping=True)
    print(ticker.trade_log)
    print(f"{ticker.symbol} pnl/max-draw: {pnl}/{max_draw}")

if __name__ == '__main__':
    args = cli_args()

    ticker = Stock(args.symbol, DATE_START, DATE_END, config='../config.toml')

    strat_factory = StrategyFactory()
    signal_name = 'ema'
    strat_factory.create_strategy(ticker, signal_name)
    sim = Simulation(ticker)
    sim.paper_trade(signal_name)

    display_pnl(ticker)