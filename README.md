# Open-quant
Open-source LSTM chain for quant


This is an open source chain for testing trading oppotunities, it allows to:
- Get financial information from Quandl, and definte wanted financial technical indicators,
- Set up a LSTM model to "learn the knowledge" from the training set,
- Then make prediction in order to provide trading signal for the test set,
- And run Backtrader to test the strategy preformance.

The chain includes the following modulus:
1) Main.py is the main code to run the different modules;
2) A_Parameters.py defintes the parameters (buy/short threshold, superparameters, train/test set etc.) for iterate testings;
3) B_SourceData.py defintes the sources of financial information and technical indicators, needed for the machine learning model;
4) C_StructureData.py is the module allowing restructure the data, definting the variables and labeds for the supervised learning;
5) D_ModelTrain.py defintes the LSTM model architecture, and runs the training process;
6) E_PredicAll.py allows to makes prediction for the test data set;
7) F_BackTesting.py allows to run the backtrader program, and provide backtesting result for the training and testing data sets.

In order the run this chain, you need to:
- get an Quandl key and put it in the B_SourceData.py,
- set up python 3.5 environment
- install libraries (keras, numpy, pandas, quandl, talib, matplotlib, sklearn, datetime, backtrader)
