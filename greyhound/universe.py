# universe.py
from .stock import Stock
from .utils import iterate_basket, read_config
from .applogger import get_logger

class Universe:
    """
    Create a 'basket'  of Stock object from list of symbols.
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

    @iterate_basket
    def list_basket(self, stock_obj):
        print(f'{stock_obj.symbol}')

    def get_basket_pnl(self, **kwargs):
        universe_pnl = 0
        for symbol,stock_obj in self.stocks.items():

            # use last date in OHLC if no date_end passed.
            date_end = kwargs.get('date_end', stock_obj.ohlc.index[-1])

            #symbol_pnl = stock_obj.get_book_pnl(date_end)
            symbol_pnl = stock_obj.get_book_pnl()
            universe_pnl = universe_pnl + symbol_pnl
            self.logger.info(f'{symbol} {symbol_pnl}')

        return universe_pnl

    def get_basket_sharpe(self, stock_obj, date_end):
        pass

    def plot_basket_pnl(self, stock_obj, date_end):
        pass
