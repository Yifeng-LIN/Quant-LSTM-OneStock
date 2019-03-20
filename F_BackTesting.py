from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import backtrader as bt


# Parameters
sigfile = 'Allsignal.csv'
logfile = 'Log-BackTest.txt'
figfile = 'Fig-BackTest.png'


def PrintLog(logfile, overwrite, txt):
    #with open(logfile, overwrite) as f:
    #    print(txt, file=f)
    #print(txt)
    return ()


def BackTesting(fromdate=None):
    
    # Datafeed from file
    class MyCSVData(bt.feeds.GenericCSVData):
        params = (
            ('nullvalue', float('NaN')),
            ('dtformat', '%Y-%m-%d'),
            ('datetime', 0),
            ('time', -1),
            ('open', 2),
            ('high', -1),
            ('low', -1),
            ('close', 1),
            ('volume', -1),
            ('openinterest', 3),
        )


    # Create a Stratey
    class TestStrategy(bt.Strategy):
    
        def __init__(self):
            # Keep a reference to the "close" line in the data[0] dataseries
            self.dataclose = self.datas[0].close
            self.dataopen = self.datas[0].open
            self.openinterest = self.datas[0].openinterest
            
            # To keep track of pending orders
            self.order = None
            self.target = 0

        def notify_order(self, order):
            if order.status in [order.Submitted, order.Accepted]:
                # Buy/Sell order submitted/accepted to/by broker - Nothing to do
                return
    
            # Check if an order has been completed
            # Attention: broker could reject order if not enough cash
            if order.status in [order.Completed]:
                if order.isbuy():
                    #self.log('BUY EXECUTED, %.2f' % order.executed.price)
                    self.ExecText = 'BUY EXECUT,  '
                elif order.issell():
                    #self.log('SELL EXECUTED, %.2f' % order.executed.price)
                    self.ExecText = 'SEL EXECUT,  '
    
                self.bar_executed = len(self)
    
            elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                #self.log('Order Canceled/Margin/Rejected')
                self.ExecText = 'ORD CANCAL,  '
    
            # Write down: no pending order
            self.order = None
    
        def next(self):
            # Simply log the closing price of the series from the reference
            PriceText = ', Open: %.2f, Close: %.2f, Signal: %.0f => ' % (self.dataopen[0], self.dataclose[0], self.openinterest[0])
            OperText = '             '
            CashValue = 'Cash: %.2f, ' % cerebro.broker.getcash()
            PortoValue = 'Porto: %.2f' % cerebro.broker.getvalue()
            dt = self.datas[0].datetime.date(0)
            
            # Check if an order is pending ... if yes, we cannot send a 2nd one
            if self.order:
                return

            # Check if we are in the market
            if self.openinterest[0] == 1:

                if self.position.size <= 0:

                    OperText = 'BUY CREATE,  '
    
                    # Keep track of the created order to avoid a 2nd order
                    self.target = cerebro.broker.getvalue() * 0.95 / self.dataopen
                    self.order = self.order_target_size(target=self.target)

            if self.openinterest[0] == -1:

                if self.position.size >= 0:
    
                    OperText = 'SEL CREATE,  '
    
                    # Keep track of the created order to avoid a 2nd order
                    self.target = -cerebro.broker.getvalue() * 0.95 / self.dataopen
                    self.order = self.order_target_size(target=self.target)

            if self.openinterest[0] == 0:

                if self.position.size != 0:
    
                    OperText = 'EMPTY CREATE,  '
    
                    # Keep track of the created order to avoid a 2nd order
                    self.target = 0
                    self.order = self.order_target_size(target=self.target)

            # Print the line
            LineText = str(dt.isoformat()) + str(PriceText) + str(OperText) + str(CashValue) + str(PortoValue)
            PrintLog(logfile, 'a', LineText)
            #log('%s, %s' % (self.dt.isoformat(), LineText))
    
    
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, sigfile)

    # Create a Data Feed
    data = MyCSVData(dataname=datapath, fromdate=fromdate)
    
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)
    
    # Print out the starting conditions
    LineText = ('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    PrintLog(logfile, 'w', LineText)
    print (LineText)

    # Run over everything
    cerebro.run()

    # Print out the final result
    FinalValue = cerebro.broker.getvalue()
    LineText = ('Final Portfolio Value: %.2f' % FinalValue)
    PrintLog(logfile, 'a', LineText)
    print (LineText)

    # Plot the result
    figure = cerebro.plot(volume=False)[0][0]
    figure.savefig(figfile)
    
    return (FinalValue)