# strategy.py
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class Strategy(ABC):

    @abstractmethod
    def create_factors(self):
        pass

    @abstractmethod
    def create_signal(self):
        pass


class EMA(Strategy):

    def __init__(self, stock_object, strategy_name):
        self.stock_obj = stock_object
        self.signal_df = pd.DataFrame(index=self.stock_obj.ohlc.index, dtype='float64')

        self.create_factors()
        self.create_signal()

        self.stock_obj.signals[strategy_name] = self.signal_df

    def create_factors(self):
        self.signal_df['ema'] = self.stock_obj.ohlc['close'].ewm(span=30).mean()
        self.signal_df['histogram'] = self.stock_obj.ohlc['close'] - self.signal_df['ema']
        self.signal_df['hist_norm'] = ((self.signal_df['histogram'] - self.signal_df['histogram'].min()) 
                            / (self.signal_df['histogram'].max() - self.signal_df['histogram'].min()))

    def create_signal(self):
        hist_mean = self.signal_df['hist_norm'].mean()
        self.signal_df['signal'] = np.where(self.signal_df['hist_norm'] >= (hist_mean * 1.1), -1.0, 0.0)
        self.signal_df['signal'] = np.where(self.signal_df['hist_norm'] <= (hist_mean * 1.1), 1.0, 0.0)


class MACD(Strategy):

    def __init__(self, stock_object, strategy_name):
        self.stock_obj = stock_object
        self.signal_df = pd.DataFrame(index=self.stock_obj.ohlc.index, dtype='float64')

        self.create_factors()
        self.create_signal()

        self.stock_obj.signals[strategy_name] = self.signal_df

    def create_factors(self):
        self.signal_df['macd_fast'] = self.stock_obj.ohlc['close'].ewm(span=12).mean()
        self.signal_df['macd_slow'] = self.stock_obj.ohlc['close'].ewm(span=26).mean()
        self.signal_df['macd']      = self.signal_df['macd_fast'] - self.signal_df['macd_slow']
        self.signal_df['macd_sig']  = self.signal_df['macd'].ewm(span=9).mean()
        self.signal_df['histogram'] = self.signal_df['macd'] - self.signal_df['macd_sig']
        
    def create_signal(self):
        self.signal_df['signal'] = np.where(self.signal_df['histogram'] >= 0.3, -1.0, 0.0)
        self.signal_df['signal'] = np.where(self.signal_df['histogram'] <= -0.3, 1.0, 0.0)


class StrategyFactory:

    strategies = {
                'ema': EMA,
                'macd': MACD
            }

    def create_strategy(self, stock_obj, name):
        try:
            func = self.strategies[name]
            return func(stock_obj, name)
        except KeyError:
            raise AssertionError("Strategy undefined")

