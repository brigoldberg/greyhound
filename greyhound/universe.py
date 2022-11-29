# universe.py
from .stock import Stock
from .utils import iterate_basket, read_config
from .applogger import get_logger


class Universe:
    """
    Create a 'basket'  of Stock object from list of symbols.
    Load data into dataframe inside stock objects.
    """
    def __init__(self, symbol_list, date_start, date_end, **kwargs):

        self.stocks = {}

        _config =  kwargs.get('config', {})
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        log_level   = self.config['logging']['log_level']
        self.logger = get_logger(f'universe', log_level)

        for symbol in symbol_list:
            self.stocks[symbol] = Stock(symbol, date_start, date_end, config=self.config)
            self.logger.info(f'adding {symbol} to universe')


    def get_tickers(self):
        """ Return list of stock tickers in universe """
        return list(self.stocks.keys())


    def calc_held_share_value(self, trade_date=None):
        """
        Calculate value of held shares of all tickers in basket.
        Return dict of each ticker:pnl.
        """
        held_share_value = {}
        for k,v in self.stocks.items():
            held_share_value[k] = v.get_held_share_value(trade_date)

        return held_share_value


    def calc_basket_cash_position(self, trade_date=None):
        
        cash_pos = {}
        for k,v in self.stocks.items():
            cash_pos[k] = v.get_cash_position(trade_date)

        return cash_pos


    def calc_basket_pnl(self, trade_date=None):
        pass
