import yfinance as yf
import datetime as dt 
import pandas as pd
import json 

"""
#if you want to download the data the only use this part
#Downloading the data of S&P 500 from yfinance
start = dt.datetime.now() - dt.timedelta(days = 365*10)
end = dt.datetime.now()
file ="data/S&P500.xlsx"
SP = yf.download("^GSPC", start = start, end =  end,auto_adjust=False)
SP.to_excel(file)

#if you want to extract and clean the data then only use this part
# after this we will use model importer (a python program which search the module and append it in the system)
import module_importer as mi
mi.find_and_add_module("data_refine")

#after that we will refine the excel file to another new excel file extracting the required columns only 
import data_refine as dr
des_file = dr.choose()

with open("config.json","w") as f:
    json.dump({"last_path": des_file},f)
    
"""
with open("config.json","r") as f:
    config = json.load(f)
    dest_file = config["last_path"]

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

df = pd.read_excel(dest_file)
data = df["Adj Close"]
wnd_period = 252
roll_retrns =pd.DataFrame( rolling_return(data, wnd_period))
daily_retrn = pd.DataFrame(daily_return(data))
concat_data = [df["Date"],df["Adj Close"],roll_retrns,daily_retrn]
final = pd.concat(concat_data,axis = 1, ignore_index=True)
final.columns = ["Date", "Adj Close", "Rolling_Return", "Daily_return_pct"]
final.to_excel(dest_file, index = False)
print("Thus the data is ready for plot")

#now creating some of visuals 
import matplotlib.pyplot as plt 

















