# stock.py
import locale
import os
import sys
import pandas as pd
import toml
from .utils import read_config
from .applogger import get_logger
pd.options.mode.chained_assignment = None
locale.setlocale(locale.LC_ALL, 'en_US')


class Stock:
    """
    Create object for storing both historical OHLC data but also
    trading/sim data such as trade logs, PnL and shares held.

    Can be instantiated on its own but is typically called from a
    Universe object and the configuration is passed into the Stock
    object.
    """

    def __init__(self, symbol, date_start, date_end, **kwargs):
        """
        Create object -> Load data -> Snip dates
        """
        self.symbol     = symbol.lower()
        self.ohlc       = None              # df OHLC prices
        self.trade_log  = None              # df shares traded
        self.signals    = {}                # dict of dfs per strategy (ema, macd, etc)

        self._read_config(kwargs)
        self._load_data()
        self._snip_dates(date_start, date_end)

        # The trade_log holds all transactions and position & PnL is calculated
        # from this data structure.
        self.trade_log = pd.DataFrame(index=self.ohlc.index, dtype='float64')
        self.trade_log['shares']      = 0
        self.trade_log['trade_price'] = 0


    def _read_config(self, kwargs):
        """  Every stock object should read/get configuration """
        _config =  kwargs.get('config', {})
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        log_level     = self.config['logging']['log_level']
        self.logger   = get_logger(f'stock-{self.symbol}', log_level)
        self.tick_ds  = self.config['data_source']['hdf5_file']
        self.col_name = self.config['data_map']['column_name']

    def _load_data(self):
        """ Load data from HDF5 source and create associated time series. """
        self.ohlc = pd.read_hdf(self.tick_ds, key=f'/{self.symbol}')
        self.ohlc['pct_ret'] = self.ohlc[self.col_name].pct_change()

    def _snip_dates(self, date_start, date_end):
        """ Prune rows from beginning and/or ends of the TSDB. """
        self.ohlc = self.ohlc.loc[date_start:date_end]
        self.logger.info(f'{self.symbol.upper()}: pruned dates {date_start} to {date_end}')

    def get_price(self, trade_date, **kwargs):
        """ Return stock price for specified date """
        col_name = kwargs.get('col_name', self.config['data_map']['column_name'])
        stock_price = self.ohlc[col_name].loc[trade_date]
        return stock_price

    def get_trades(self):
        """ Return list of all logged trades """
        return self.trade_log[self.trade_log.shares != 0]

    def log_trade(self, trade_date, shares, price):
        if trade_date not in self.trade_log.index:
            raise Exception(f'{trade_date} not in time series')
        self.trade_log.loc[trade_date, ['shares', 'trade_price']] = [shares, price]

    def get_book_value(self, trade_date):
        """ Return dollar value of all shares at specified trade_date """
        shares = self.trade_log['shares'].loc[:trade_date].sum()
        spot_price = self.ohlc[self.col_name].loc[trade_date]
        book_value = shares * spot_price
        self.logger.info(f'{self.symbol.upper()}: book value {shares}@${spot_price} is ${book_value:0.2f}')
        return book_value

    def get_book_cost(self, trade_date):
        """ Return cost of all stock purchases up to submitted date """
        total_book_cost = self.trade_log['shares'] * self.trade_log['trade_price']
        book_cost = total_book_cost.loc[:trade_date].sum()
        self.logger.info(f'{self.symbol.upper()}: book cost ${book_cost:0.2f}')
        return book_cost

    def get_book_pnl(self, trade_date, pretty=False):
        """ Return PnL of all trades up to submitted trade date """
        book_pnl = self.get_book_value(trade_date) - self.get_book_cost(trade_date)
        self.logger.info(f'{self.symbol.upper()}: book PnL ${book_pnl:0.2f}')
        return book_pnl
