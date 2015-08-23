import datetime
import numpy as np

from ..event import SignalEvent
from strategy import Strategy


class MACDStrategy(Strategy):
    """
    Moving Average Convergence/Divergence
    When MACD Line is higher than MACD Signal, the Buy signal is trigger.
    When MACD Line is lower than MACD Signal, the Sell signal is trigger.
    *** In the opinion, if both MACD Line and Signal is higher than 0, the price will be run.
    """

    def __init__(self, bars, events, long_window=26, shrt_window=12, sgnl_window=9):
        """
        Initialises the buy and hold strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        long_window - MACD long window (default is 26)
        shrt_window - MACD short window (default is 12)
        sgnl_window - MACD signal window (default is 9)
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.long_window = long_window
        self.shrt_window = shrt_window
        self.sgnl_window = sgnl_window
        self.macd_bars = None
                
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
                max_bar = self.long_window * 2 + self.sgnl_window
                bars = self.bars.get_latest_bars_values(s, "close", N=max_bar)
                bar_date = self.bars.get_latest_bar_datetime(s)
                if bars is not None and bars != [] :
                    long_ema = self._calculate_ema(bars[-(self.long_window * 2):], self.long_window)
                    shrt_ema = self._calculate_ema(bars[-(self.shrt_window * 2):], self.shrt_window)
                    sgnl_ema = None                        
                    
                    if shrt_ema is not None and long_ema is not None:
                        if self.macd_bars is None:
                            self.macd_bars = np.array([shrt_ema - long_ema])
                        else:
                            self.macd_bars = np.append(self.macd_bars, [shrt_ema - long_ema])
                    
                        sgnl_ema = self._calculate_ema(self.macd_bars[-(self.sgnl_window * 2):], self.sgnl_window)
                                                
                        symbol = s
                        dt = datetime.datetime.utcnow()
                        sig_dir = ""

                    if len(bars) == max_bar and sgnl_ema is not None:
                        if (shrt_ema - long_ema) > sgnl_ema and sgnl_ema > 0 and self.bought[s] == "OUT":
                            print "LONG: %s" % bar_date
                            sig_dir = 'LONG'
                            signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'LONG'
                        elif (shrt_ema - long_ema) < sgnl_ema and self.bought[s] == "LONG":
                            print "SHORT: %s" % bar_date
                            sig_dir = 'EXIT'
                            signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'OUT'