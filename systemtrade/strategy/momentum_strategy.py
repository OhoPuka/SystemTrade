import datetime
import numpy as np

from ..event import SignalEvent
from strategy import Strategy

class MomentumStrategy(Strategy):
    
    def __init__(self, bars, events, window=80):
        
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.window = window
                
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
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.    

        Parameters
        event - A MarketEvent object. 
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars_values(s, "close", N=self.window+1)
                bar_date = self.bars.get_latest_bar_datetime(s)
                if bars  is not None and bars  != [] :
                    prev_close_price = max(bars[:1])
                    curr_close_price = max(bars[-1:])

                    symbol = s
                    dt = datetime.datetime.utcnow()
                    sig_dir = ""

                    if len(bars) == self.window+1:
                        if curr_close_price > prev_close_price and self.bought[s] == "OUT":
                            print "LONG: %s" % bar_date
                            sig_dir = 'LONG'
                            signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'LONG'
                        elif curr_close_price < prev_close_price and self.bought[s] == "LONG":
                            print "SHORT: %s" % bar_date
                            sig_dir = 'EXIT'
                            signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'OUT'