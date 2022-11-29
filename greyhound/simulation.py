# simulation.py
import locale
import math
from .utils import read_config
from .applogger import get_logger

class Simulation:
    """
    Step thru each price tick in a stock and perform the following:
      - Determine if there is a buy/sell signal
      - Calculate existing risk on current position and determine size of risk
        desired to be added or removed from current position.
      - Trade stock and update book and log trade.
    """
    def __init__(self, stock_obj):

        self.stock = stock_obj

        log_level = self.stock.config['logging']['log_level']
        self.col_name   = self.stock.config['data_map']['column_name']
        self.risk_limit = self.stock.config['strategy']['max_position_risk']
        self.buy_signal_boundary  = self.stock.config['strategy']['buy_signal_boundary']
        self.sell_signal_boundary = self.stock.config['strategy']['sell_signal_boundary']
        self.logger = get_logger(f'simul-{self.stock.symbol}', log_level)

    def _risk_check(self, signal, trade_date):

        existing_position_risk = self.stock.get_held_share_value(trade_date)
        risk_allowed = self.risk_limit - abs(existing_position_risk)
        self.logger.info(f'{self.stock.symbol.upper()}  Allowed risk: ${locale.format_string("%.2f", risk_allowed)}')

        if signal == 'buy' and risk_allowed > 0:
            trade_size = self._calc_trade_size(risk_allowed, trade_date)
            self.logger.info(f'{self.stock.symbol.upper()} Buy {trade_size} shares on {trade_date}.')
            return trade_size

        elif signal == 'sell':
            # dump entire position
            trade_size = self.stock.trade_log.shares.loc[:trade_date].sum()
            self.logger.info(f'{self.stock.symbol.upper()} Sell {trade_size} shares on {trade_date}.')
            return trade_size

        return 0

    def _calc_trade_size(self, risk_allowed, trade_date):

        spot_price = self.stock.ohlc[self.col_name].loc[trade_date]

        return math.floor(risk_allowed / spot_price)

    def paper_trade(self, signal_name):
        ''' signal check -> risk check -> get trade size -> log trade '''
        symbol = self.stock.symbol
        signal = self.stock.signals[signal_name].signal

        for trade_date in self.stock.ohlc.index:

            spot_price = self.stock.ohlc[self.col_name].loc[trade_date]

            if signal.loc[trade_date] >= self.buy_signal_boundary: # Buy signal
                trade_shares = self._risk_check('buy', trade_date)
                self.logger.info(f'{self.stock.symbol.upper()} traded {trade_shares} @ {spot_price} on {trade_date}')
                self.stock.log_trade(trade_date, trade_shares, spot_price)

            elif signal.loc[trade_date] <= self.buy_signal_boundary:   # Sell signal
                trade_shares = self._risk_check('sell', trade_date)
                self.logger.info(f'{self.stock.symbol.upper()} traded {trade_shares} @ {spot_price} on {trade_date}')
                self.stock.log_trade(trade_date, (trade_shares * -1), spot_price)
