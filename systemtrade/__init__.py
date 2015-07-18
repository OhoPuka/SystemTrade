import datetime

import data_handler as data
import strategy
import portfolio as port
import execution_handler as execute
import backtest as test

def main():
    csv_dir = "D:\\Works\\Trading System\\04) System Development\\20150711_Three Companies Backtesting\\data\\"
    symbol_list = ['BBL']
    initial_capital = 100000.0
    start_date = datetime.datetime(1992, 1, 2, 0, 0, 0)
    periods = "D"
    heartbeat = 0.0

    backtest = test.BacktestEqualWeightPortFromCSV(
                        csv_dir, 
                        symbol_list, 
                        initial_capital, 
                        start_date,
                        data.HistoricCSVDataHandler, 
                        execute.SimulatedExecutionHandler, 
                        port.EqualWeightedPortfolio, 
                        strategy.MovingAverageCrossStrategy, 
                        periods, 
                        heartbeat,
                        header_format="mine", 
                        max_iters=None
    )
    backtest.simulate_trading()

if __name__ == "__main__":
    main()
