# macd.py
import numpy as np
import pandas as pd
from .applogger import get_logger


class MACD:
    
    CLOSE = 'close'

    def __init__(self, stock_obj, *args, **kwargs):

        self.stock = stock_obj
        self.name       = 'macd'

        self.macd_cfg = self.stock.config['strategy']['macd']
        log_level = self.stock.config['logging']['log_level']
        self.logger = get_logger(f'macd-{self.stock.symbol}', log_level)

        self.signal_df = pd.DataFrame(index=self.stock.ohlc.index, dtype='float64')

        self._calc_macd()
        self._calc_signal()

        self.stock.signals['macd'] = self.signal_df

    def _calc_macd(self):

        FAST_SPAN = self.macd_cfg['macd_fast']
        SLOW_SPAN = self.macd_cfg['macd_slow']
        SIGNAL = self.macd_cfg['macd_sig']

        self.signal_df['macd_fast'] = self.stock.ohlc[self.CLOSE].ewm(span=FAST_SPAN).mean()
        self.signal_df['macd_slow'] = self.stock.ohlc[self.CLOSE].ewm(span=SLOW_SPAN).mean()
        self.signal_df['macd']      = self.signal_df['macd_fast'] - self.signal_df['macd_slow']

        self.signal_df['macd_sig']  = self.signal_df['macd'].ewm(span=SIGNAL).mean()
        self.signal_df['histogram'] = self.signal_df['macd'] - self.signal_df['macd_sig']
        self.logger.info(f'{self.stock.symbol.upper()}: MACD calculated')

    def _calc_signal(self):

        HIST_MAX = self.macd_cfg['histogram_max']
        HIST_MIN = self.macd_cfg['histogram_min']

        self.signal_df['signal'] = np.where(self.signal_df['histogram'] >= HIST_MAX, -1.0, 0.0)
        self.signal_df['signal'] = np.where(self.signal_df['histogram'] <= HIST_MIN, 1.0, 0.0)

        self.logger.info(f'{self.stock.symbol.upper()}: Signal calculated')
