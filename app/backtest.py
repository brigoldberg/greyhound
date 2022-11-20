#!/usr/bin/env python3
# backtest.py

import argparse
import locale
import multiprocessing as mp
import sys
import os

app_path = os.path.join(os.path.expanduser('~/sandbox/greyhound/'))
sys.path.append(app_path)
from greyhound import Simulation
from greyhound import StrategyFactory
from greyhound import Universe

locale.setlocale(locale.LC_ALL, 'en_US')

DATE_START = '2014-01-01'
DATE_END   = '2021-06-30'

def cli_args():
    parser = argparse.ArgumentParser(description='MuliProc Dogger')
    parser.add_argument('-f', dest='ticker_file', action='store', required=True)
    parser.add_argument('-c', dest='config', action='store', required=True)
    return parser.parse_args()

def read_ticker_file(ticker_file):
    symbols = []
    with open(ticker_file, 'r') as fh:
        lines = fh.readlines()
        for line in lines:
            symbols.append(line.rstrip().lower())
    return symbols

def queue_count(stock_list):
    # MP-Queue count must be no greater than amount of tickers being
    # analyzed. Return lesser of ticker count or processor count.
    if len(stock_list) < mp.cpu_count():
        return len(stock_list)
    return mp.cpu_count()

def worker(wq, rq):
    strat_factory = StrategyFactory()
    while True:
        stock = wq.get()
        if stock is None:
            wq.task_done()
            break
        signal_name = 'ema'
        strat_factory.create_strategy(stock, signal_name)
        sim = Simulation(stock)
        sim.paper_trade(signal_name)
        rq.put(sim.stock)

if __name__ == '__main__':
    args = cli_args()

    universe = Universe(read_ticker_file(args.ticker_file),
                        DATE_START, DATE_END, config=args.config)

    NUM_QUEUES = queue_count(universe.stocks)

    work_queue = mp.JoinableQueue()
    result_queue = mp.Queue()	

    for ticker, stock_obj in universe.stocks.items():
        work_queue.put(stock_obj)
    for _ in range(NUM_QUEUES):
        work_queue.put(None)

    for _ in range(NUM_QUEUES):
        p = mp.Process(target=worker, args=(work_queue, result_queue))
        p.start()

    for stock_name, stock_obj in universe.stocks.items():
        result = result_queue.get()
        universe.stocks[result.symbol] = result

    print(f'{locale.currency(universe.get_basket_pnl(), grouping=True)}')


