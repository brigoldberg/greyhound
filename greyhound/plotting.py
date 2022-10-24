# plotting.py

import matplotlib.pyplot as plt

class Plotter:

    price_col = 'close'

    def __init__(self, stock_obj):
        self.symbol = stock_obj.symbol
        self.stock_obj = stock_obj

    def plot_price(self):
        """ Plot stock price and volume """
        fig = plt.figure(figsize=(18,10))
        ax1 = plt.subplot2grid((3,3), (0,0), colspan=3, rowspan=2)
        ax2 = plt.subplot2grid((3,3), (2,0), colspan=3, rowspan=1)

        ax1.set_title('Price')
        ax2.set_title('Volume')
        ax1.plot(self.stock_obj.ohlc['close'])
        ax2.bar(self.stock_obj.ohlc.index, self.stock_obj.ohlc['volume'])

        ax1.set_ylabel('Price')
        ax2.set_ylabel('Volume')

    def plot_price_signal(self, signal_name):
        """
        Plot price and volume.  Plot markers showing buy and
        sell signals
        """
        signal_name = signal_name.lower()

        fig = plt.figure(figsize=(18,10))
        ax1 = plt.subplot2grid((3,3), (0,0), colspan=3, rowspan=2)
        ax2 = plt.subplot2grid((3,3), (2,0), colspan=3, rowspan=1)

        ax1.set_title('Price')
        ax2.set_title('Volume')
        ax1.plot(self.stock_obj.ohlc['close'])
        ax2.bar(self.stock_obj.ohlc.index, self.stock_obj.ohlc['volume'])

        ax1.set_ylabel('Price')
        ax2.set_ylabel('Volume')

        signal = self.stock_obj.signals[signal_name].signal
        price = self.stock_obj.ohlc['close']

        ax1.plot(signal.loc[signal == 1].index,
                price.loc[signal == 1], '^', markersize=10,
                color='green')
        ax1.plot(signal.loc[signal == -1].index,
                price.loc[signal == -1], 'v', markersize=10,
                color='red')
