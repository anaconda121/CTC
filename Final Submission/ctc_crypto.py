# -*- coding: utf-8 -*-
"""Copy of CryptoBacktester.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1X_lOYmDeQ2apG_-DIKOvY0LH-rttOvst
"""

import pandas as pd
import matplotlib as plt
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import statsmodels.api as sm
import numpy as np
import random
from datetime import datetime, timedelta

"""# Cryptocurrency Case Study Backtester"""

#importing data !
b1 = pd.read_csv('./BTC_Futures1.csv')
b2 = pd.read_csv('./BTC_Futures2.csv')
b3 = pd.read_csv('./BTC_Futures3.csv')
b4 = pd.read_csv('./BTC_Futures4.csv')
b5 = pd.read_csv('./BTC_Futures5.csv')
b6 = pd.read_csv('./BTC_Futures6.csv')
b7 = pd.read_csv('./BTC_Futures7.csv')
b8 = pd.read_csv('./BTC_Futures8.csv')
b9 = pd.read_csv('./BTC_Futures9.csv')
b10 = pd.read_csv('./BTC_Futures10.csv')
b11 = pd.read_csv('./BTC_Futures11.csv')
b12 = pd.read_csv('./BTC_Futures12.csv')
b13 = pd.read_csv('./BTC_Futures13.csv')
b14 = pd.read_csv('./BTC_Futures14.csv')
b15 = pd.read_csv('./BTC_Futures15.csv')
b16 = pd.read_csv('./BTC_Futures16.csv')
b17 = pd.read_csv('./BTC_Futures17.csv')
b18 = pd.read_csv('./BTC_Futures18.csv')
b19 = pd.read_csv('./BTC_Futures19.csv')
b20 = pd.read_csv('./BTC_Futures20.csv')
b21 = pd.read_csv('./BTC_Futures21.csv')
b22 = pd.read_csv('./BTC_Futures22.csv')
b23 = pd.read_csv('./BTC_Futures23.csv')
b24 = pd.read_csv('./BTC_Futures24.csv')

def regression(train_data):
  data = train_data
  bid_size = data['bid_sz_00'].to_numpy()
  ask_size = data['ask_sz_00'].to_numpy()
  bid_price = data['bid_px_00'].to_numpy()
  ask_price = data['ask_px_00'].to_numpy()

  bid_size = (bid_size - np.mean(bid_size))/np.std(bid_size)
  ask_size = (ask_size - np.mean(ask_size))/np.std(ask_size)
  bid_price = (bid_price - np.mean(bid_price))/np.std(bid_price)
  ask_price = (ask_price - np.mean(ask_price))/np.std(ask_price)

  center = 0.5*(bid_price+ask_price)

  independent = np.column_stack((bid_size[:-1], ask_size[:-1], ask_price[:-1], bid_price[:-1]))

  x = independent
  x=sm.add_constant(x)

  #offset by 1 for future value
  y = center[1:]-center[:-1]

  mod = sm.OLS(y,x)
  res=mod.fit()

  return(res)

def get_params(test_data):
  data = test_data
  bid_size = data['bid_sz_00'].to_numpy()
  ask_size = data['ask_sz_00'].to_numpy()
  bid_price = data['bid_px_00'].to_numpy()
  ask_price = data['ask_px_00'].to_numpy()
  center = 0.5*(bid_price+ask_price)
  size_diff = ask_size-bid_size
  price_diff = ask_price-bid_price

  independent = np.column_stack((bid_size, ask_size, ask_price, bid_price))

  mean = np.mean(independent)
  std = np.std(independent)
  independent = (independent - mean)/std

  x = independent
  x=sm.add_constant(x)
  return(x)

#add your positions here

def run_strategy_crypto(test_data):

  train_data = pd.concat([b11, b12], ignore_index=True)
  x = get_params(test_data)
  res = regression(train_data)
  results = res.predict(x)

  position = []
  count = 0

  for row in test_data.index:

    if(results[count] > 0):
      position.append(1)
    elif(results[count] < 0):
      position.append(-1)
    else:
      position.append(0)
    count+=1


  positions = pd.DataFrame({
      "DATETIME": test_data.iloc[:,0],
      "POSITION": position})

  return(positions)

def private_test_crypto():
  crypto_file_list = pd.concat([b10], ignore_index=True)
  crypto_file_list['ts_event'] = pd.to_datetime(crypto_file_list['ts_event'])
  positions = run_strategy_crypto(crypto_file_list)
  pnl = []
  backtest(crypto_file_list, positions, pnl)

private_test_crypto()

'''
Given a dataframe of positions check that the dates and positions are valid.
'''

def check_crypto_output(marketdata, positions):
    # check if positions is a dataframe
    assert isinstance(positions, pd.DataFrame), "positions should be a dataframe"
    assert "DATETIME" in positions.columns, "positions dataframe does not have 'DATETIME' column, please read naming specifications"

    # check whether every value in 'DATETIME' is a datetime object
    assert positions['DATETIME'].apply(lambda x: isinstance(x, pd.Timestamp)).all(), "every element in 'DATETIME' column of positions should be a datetime object"

    # check if right number of dates, and that they are equal
    assert marketdata['ts_event'].equals(positions['DATETIME']), "the 'DATETIME' column of positions should match 'ts_recv' of marketdata column"

    # check if all outputs are valid
    assert all(positions['POSITION'].isin([-1, 0, 1])), "all values in 'DATETIME' column need to be either -1, 0 or 1"

'''
Overview: given a list of positions use provided market data to find the
overall pnl.
'''

def backtest(marketdata: pd.DataFrame, positions: pd.DataFrame, y_list) -> None:
   check_crypto_output(marketdata, positions)
   return check_pnl(marketdata, positions, y_list)


def check_pnl(marketdata: pd.DataFrame, positions: pd.DataFrame, y_list) -> None:
    pnl = 0  # inital capital is 0 dollars
    curpos = 0 # setting initial position to neutral
    spread_cost = 0 # track total spread

    for index, row in marketdata.iterrows():
        bid_price = row['bid_px_00'] / 1e-9
        ask_price = row['ask_px_00'] / 1e-9
        signal = positions.loc[index, 'POSITION'] # whether we buy or sell

        # calculate spread cost
        spread = (ask_price - bid_price)/2

        #Note: You effectively trade at the midpoint at each time period,
        #and are compensated for the spread when you both open and close a position.

        # return to neutral
        if curpos == -1:
            pnl -= ask_price
        elif curpos == 1:
            pnl += bid_price

        # add spread
        if curpos != 0:
            spread_cost += spread

        # perform trade
        if signal == 1:
            pnl -= ask_price
        elif signal == -1:
            pnl += bid_price

        # add spread
        if signal != 0:
            spread_cost += spread

        # update position
        curpos = signal


        #Calculate PNL if we were to close - for graph
        pnl_close=pnl
        spread_close=spread_cost

        if curpos == -1:
            pnl_close -= ask_price
        elif curpos == 1:
            pnl_close += bid_price
        if curpos != 0:
            spread_close += spread

        y_list.append(pnl_close+spread_close)


    # return to neutral
    if curpos == -1:
        pnl -= ask_price
    elif curpos == 1:
        pnl += bid_price

    # add spread
    if curpos != 0:
        spread_cost += spread

    return (pnl + spread_cost)

#plt.plot(ts_recv, pnl_on_day)
plt.plot(pnl_on_day)
plt.title('Timestamps vs. PNL')
plt.xlabel('Timestamps')
plt.ylabel('PNL')