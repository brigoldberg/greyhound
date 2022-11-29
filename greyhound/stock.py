# stock.py
import pandas as pd
from .utils import read_config
from .applogger import get_logger
pd.options.mode.chained_assignment = None


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
        self.trade_log = pd.DataFrame(index=[self.ohlc.index[0],], dtype='float64')
        self.trade_log['shares']      = 0
        self.trade_log['trade_price'] = 0
        self.trade_log['trade_cost'] = 0
        self.trade_log['cash_position'] = 0
        self.trade_log['share_value'] = 0
        self.trade_log['book_value'] = 0


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

    
    def _validate_trade_date(self, trade_date):
        """
        Make sure trade date is last date or a valid date in OHLC index.
        """
        if not trade_date:
            return self.ohlc.index[-1]
        
        if trade_date not in self.ohlc.index: 
           raise Exception(f'{trade_date} not in time series') 
        else:
            return trade_date


    def log_trade(self, trade_date, shares, price):
        '''
        Record traded share count and update cash position with trade
        cost. Keep cash position updated in a running manner.
        '''       
        if trade_date not in self.ohlc.index:
            raise Exception(f'{trade_date} not in time series')
        
        trade_cost = (shares * price) * -1
        self.trade_log.loc[trade_date,['shares', 'trade_price', 'trade_cost']] = [shares, price, trade_cost]


    def get_held_shares(self, trade_date=None):
        """ Return shares held at specific date """
        trade_date = self._validate_trade_date(trade_date)
        return self.trade_log['shares'].loc[:trade_date].sum()

    
    def get_held_share_value(self, trade_date=None, ohlc_col='close'):
        """ 
        Return dollar value of held shares at specified trade_date. Value
        is calculated as the current (or submitted trade_date) stock price
        """
        trade_date = self._validate_trade_date(trade_date)

        share_count = self.trade_log.loc[:trade_date]['shares'].sum()
        share_price = self.ohlc.loc[trade_date][ohlc_col]
        return (share_count * share_price)


    def get_cash_position(self, trade_date=None):
        """
        Return cash position. This is the sum of all buy and sell transactions.
        """
        trade_date = self._validate_trade_date(trade_date)
        return self.trade_log['trade_cost'].loc[:trade_date].sum()

    
    def get_max_drawdown(self, trade_date=None):
        """
        Return max draw down of the ticker throught it traded period.
        """
        trade_date = self._validate_trade_date(trade_date)

        return self.trade_log.loc[:trade_date]['cash_position'].min()        


    def calc_pnl(self, trade_date=None):
        """
        Calculate PnL based upon cash position and shares held
        """
        trade_date = self._validate_trade_date(trade_date)
        book_value = self.get_held_share_value(trade_date)
        cash_position = self.get_cash_position(trade_date)

        pnl = book_value + cash_position
        return pnl


    def calc_ror(self, trade_date=None):
        """
        Calculate the annual rate of return. This will be the percent return
        on the max_position_risk which is set in the configuration file.
        TBD TBD TBD
        """
        pass