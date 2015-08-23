import datetime
import numpy as np

from ..event import SignalEvent
from strategy import Strategy

class NewHighStrategy(Strategy):
    """
    New High means All time high
    When close price is greater than all time high, the Buy signal is trigger.
    When close price is lower than EMA 40 days, the Sell signal is trigger.
    """
    def __init__(self, bars, events, ema_window=40):
        """
        Initialises the buy and hold strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        ema_window - EMA window for sell signal (default is 40)
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.ema_window = ema_window
        self.max_bar = 0
                
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
        
    def _calculate_sma(self, data, window):
        """
        Calculate Simple Moveing Average
        """
        if len(data) < window:
            return None
        return sum(data[-window:]) / float(window)

    def _calculate_ema(self, data, window):
        """
        Calculate Exponential Moveing Average
        """
        if len(data) < window * 2:
            return None
        c = 2.0 / float(window + 1)
        current_ema = self._calculate_sma(data[-window * 2: -window], window)
        for value in data[-window:]:
            current_ema = (c * value) + ((1 - c) * current_ema)
        return current_ema
        
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
                self.max_bar += 1 
                bars = self.bars.get_latest_bars_values(s, "close", N=self.max_bar)
                bar_date = self.bars.get_latest_bar_datetime(s)
                if bars is not None and bars != [] :
                    curr_cls = np.max(bars[-1:])
                    hist_max = np.max(bars[:(self.max_bar-1)])
                    sgnl_ema = self._calculate_ema(bars[-(self.ema_window * 2):], self.ema_window)
                    
                    symbol = s
                    dt = datetime.datetime.utcnow()
                    sig_dir = ""

                    if len(bars) == self.max_bar and curr_cls is not None and hist_max is not None and sgnl_ema is not None:
                        if curr_cls > hist_max and self.bought[s] == "OUT":
                            print "LONG: %s" % bar_date
                            sig_dir = 'LONG'
                            signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'LONG'
                        elif curr_cls < sgnl_ema and self.bought[s] == "LONG":
                            print "SHORT: %s" % bar_date
                            sig_dir = 'EXIT'
                            signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'OUT'