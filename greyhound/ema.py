# ema.py
import numpy as np
import pandas as pd
from .utils import read_config
from .applogger import get_logger


class EMA:
    """
    Calculate trading signal using Exponetial Moving Average patterns.
    """

    def __init__(self, stock_obj, *args, **kwargs):
        
        self.stock = stock_obj
        self.name = 'ema'
        
        self.ema_config = self.stock.config['strategy']['ema']
        log_level   = self.stock.config['logging']['log_level']
        self.logger = get_logger(f'ema-{self.stock.symbol}', log_level)

        self.signal_df = pd.DataFrame(index=self.stock.ohlc.index, dtype='float64')

        self._calc_basic_ema()
        self._calc_normalized_ema()
        #self._calc_signal_basic_ema()
        self._calc_signal_stupid_ema()

        self.stock.signals['ema'] = self.signal_df

    def _calc_basic_ema(self):

        col_name = self.stock.config['data_map']['column_name']
        window   = self.ema_config['window']
        self.signal_df['ema'] = self.stock.ohlc[col_name].ewm(span=window).mean()
        self.signal_df['histogram'] = self.stock.ohlc[col_name] - self.signal_df['ema']
        self.logger.info(f'{self.stock.symbol.upper()}: EMA calculated')
        
    def _calc_normalized_ema(self):

        window = self.ema_config['window']

        h = self.signal_df['histogram']
        self.signal_df['hist_norm'] = (h - h.min()) / (h.max() - h.min())
        self.signal_df['ema_norm'] = self.signal_df['hist_norm'].ewm(span=window).mean()
        self.logger.info(f'{self.stock.symbol.upper()}: Normalized EMA calculated')

    '''
    def _calc_signal_basic_ema(self):
        """
        Buy signal is when price crosses above EMA. Sell signal is when price crosses below EMA.
        This will create +1/-1 for buy/sell when raw_signal is diff'd.
        Crazy simple and worthless signal.
        """
        col_name = self.stock.config['data_map']['column_name']

        raw_signal = np.where(self.stock.tsdb['ema'] > self.stock.tsdb[col_name], 1.0, 0.0)
        self.stock.tsdb['signal'] = raw_signal
        self.stock.tsdb['signal'] = self.stock.tsdb['signal'].diff()
        self.logger.info(f'{self.stock.symbol.upper()}: Basic EMA signal generated')
    '''

    def _calc_signal_stupid_ema(self):
        """
        Buy signal when hist_norm >= 110% mean.  Sell signal when hist_norm <= 90% mean. This is a 
        stupid signal because is uses future data.
        """
        col_name = self.stock.config['data_map']['column_name']

        hist_mean = self.signal_df['hist_norm'].mean()

        raw_signal = np.where(self.signal_df['hist_norm'] >= (hist_mean * 1.1), -1.0, 0.0)
        raw_signal = np.where(self.signal_df['hist_norm'] <= (hist_mean * 0.9), 1.0, 0.0)
        self.signal_df['signal'] = raw_signal
        self.signal_df['signal'] = self.signal_df['signal'].diff()
        self.logger.info(f'{self.stock.symbol.upper()}: Stupid EMA signal generated')

