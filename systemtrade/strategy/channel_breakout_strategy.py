import datetime
import numpy as np

from ..event import SignalEvent
from strategy import Strategy


class ChannelBreakoutStrategy(Strategy):
    """
    Carries out a basic Channel Breakout strategy with a high/low value 
    within the period window. Default period windows for each high/low 
    are 20/20 periods respectively.
    """

    def __init__(self, bars, events, high_window=20, low_window=20):
        """
        Initialises the buy and hold strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        high_window - The high value lookback.
        low_window - The low value lookback.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.high_window = high_window
        self.low_window = low_window
        
        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()
        
    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought

    def _calculate_initial_signal(self):
        """
        Adds keys to the first_signal dictionary for all symbols
        and sets them to True.
        """
        first_signal = {}
        for s in self.symbol_list:
            first_signal[s] = True
        return first_signal

    def calculate_signals(self, event):
        """
        Generates a new set of signals based on the Channel Breakout
        break out the high value within high window meaning a long entry 
        and vice versa for a short entry.    

        Parameters
        event - A MarketEvent object. 
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                max_bar = max(self.high_window, self.low_window)
                bars = self.bars.get_latest_bars_values(s, "close", N=max_bar+1)
                bar_date = self.bars.get_latest_bar_datetime(s)
                if bars is not None and bars != [] :
                    prev_high_max = max(bars[:self.high_window])
                    prev_low_min = min(bars[:self.low_window])
                    curr_close = max(bars[-1:])

                    symbol = s
                    dt = datetime.datetime.utcnow()
                    sig_dir = ""

                    if len(bars) == max_bar+1:
                        if curr_close > prev_high_max and self.bought[s] == "OUT":
                            print "LONG: %s" % bar_date
                            sig_dir = 'LONG'
                            signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'LONG'
                        elif curr_close < prev_low_min and self.bought[s] == "LONG":
                            print "SHORT: %s" % bar_date
                            sig_dir = 'EXIT'
                            signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'OUT'