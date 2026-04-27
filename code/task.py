import yfinance as yf
import datetime as dt 
import pandas as pd
import json 



file =r"C:\Users\BROTHER COMPUTER\Desktop\GIT_Project\Quant\S&P500\data\stocks.xlsx"

#if you want to extract and clean the data then only use this part


#after this we will calculate the rooling return 
def calculate_the_return(value):
    #here value is list or series of the data points of days
    retrn = value[0] - value[-1]
    return retrn

def rolling_return(data, window_period):
    return_data = []
    data = data.tolist()
    for i in range(len(data)):
        if i < window_period-1:
            return_data.append(None)
        else:
            value = data[ i - window_period + 1: i + 1]
            result = calculate_the_return(value)
            return_data.append(result)
        
    return return_data
def daily_return(data):
    daily_return = []
    data = data.tolist()
    for i in range(len(data)):
        if i > 0:
            pct_change = (data[i]-data[i-1])/(data[i-1])*100
            daily_return.append(pct_change)
        else:
            daily_return.append(None)
        
    return daily_return

df = pd.read_excel(file)
df["Date"] = pd.to_datetime(df["Date"])
df_sorted = df.sort_values(by = 'Date', inplace=True)
print(df_sorted)

wnd_period = 2
roll_retrns =pd.DataFrame( rolling_return(data, wnd_period))
daily_retrn = pd.DataFrame(daily_return(data))
concat_data = [df["Date"],df["Close"],roll_retrns,daily_retrn]
final = pd.concat(concat_data,axis = 1, ignore_index=True)
final.columns = ["Date", "Close", "Rolling_Return", "Daily_return_pct"]
final.to_excel(r"C:\Users\BROTHER COMPUTER\Desktop\GIT_Project\Quant\S&P500\data\rolling_stocks.xlsx", index = False)
print("Thus the data is ready for plot")

#now creating some of visuals 
import matplotlib.pyplot as plt 

















