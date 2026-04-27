import yfinance as yf
import datetime as dt 
import pandas as pd
import numpy as np
from scipy import stats
import json 
import math
import matplotlib.pyplot as plt 
from statsmodels.tsa.stattools import acf
'''

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

with open(r"data/config.json","w") as f:
    json.dump({"last_path": des_file},f)

'''


with open(r"data/config.json","r") as f:
    config = json.load(f)
    dest_file = config["last_path"]

#after this we will calculate the compounding rolling return 
def calculate_the_return(value):
    #here value is list or series of the data points of days
    retrn = value[-1]/value[0] - 1
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
            '''rolling_12m = (
    (1 + daily_returns)
    .rolling(252)
    .apply(np.prod, raw=True) - 1
    this is the panda method to do and it is shortcut method
)'''
        
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

r = final["Rolling_Return"]
d = final["Daily_return_pct"]
#now ploting the returns for looking at the distribution and normality 
def moments(datas):
    data = datas.dropna().values
    mu = data.mean()
    s = data.std(ddof = 1)
    d = data - mu
    n = len(data)
    skew = np.mean(d**3)/s**3
    ex_kurt = np.mean(d**4)/s**4 -3 
    acf_value = acf(data, nlags = 252, fft = True )[1:]
    n_eff = n/(1 + 2 * np.sum(acf_value))
    JB = skew**2*(n_eff/6) + ex_kurt**2*(n_eff/24)
    p_value = 1 - stats.chi2.cdf(JB, df=2)
    return skew, ex_kurt, JB, p_value
skew_d, kurt_d, JB_d, p_value_d = moments(d)
skew_r, kurt_r, JB_r, p_value_r= moments(r)

fig, axes = plt.subplots(2,2, figsize=(18,18))
fig.set_facecolor("#a39f9f")

ax1 = axes[0][0]#rolling return plot
ax1.patch.set_facecolor("#330202CE")
ax1.hist(r, bins = 80,density = True, color ="crimson", label = "Emperical",edgecolor = "silver", zorder= 2)
x_range = np.linspace(r.min(), r.max(), 500)
x_normal = stats.norm.pdf(x_range, r.mean(), r.std())
ax1.plot(x_range, x_normal, lw = 2, color = "#98ce03", label = "Normal fit", zorder = 3)
ax1.legend()
ax1.grid(True,alpha = 0.5)
ax1.set_title('Rolling returns of 12 months \n' \
                f'excess kurtosis: {kurt_r:.3f}, skweness = {skew_r:.3f}\n  JB value:{JB_r:.3f}, p_value = {p_value_r:.3f}')

ax2 = axes[0][1]#daily returns
ax2.patch.set_facecolor("#330202CE")
ax2.hist(final["Daily_return_pct"], bins = 150, density = True,label ="emperical", color = "#a30101", edgecolor = "silver", zorder = 2)
x_range = np.linspace(d.min(), d.max(), 500)
x_normal = stats.norm.pdf(x_range, d.mean(), d.std())
ax2.plot(x_range, x_normal, lw = 2, color = "#98ce03", label = "Normal fit", zorder = 3)
ax2.legend()
ax2.grid(True, alpha = 0.5)
ax2.set_title('Daily returns \n' \
                f'excess kurtosis: {kurt_d:.3f}, skweness = {skew_d:.3f}\n  JB value:{JB_d:.3f}, p_value = {p_value_d:.3f}')


import sympy as sp 

def error_function(x):
    t = sp.Symbol('t')
    f = sp.exp(-(t**2))
    result = 2/sp.sqrt(sp.pi)  * sp.integrate(f,(t, 0, x ))
    return result

def inv_error(t):
    x = sp.Symbol('x')
    y = sp.Symbol('y')
    f = error_function(x)
    inverse_list = sp.solve(sp.Eq(y, f),x)
    inv_err = inverse_list[0].subs(y,t)
    result = inv_err.evalf()
    return float(result)

def inverse_cdf(p):
    return math.sqrt(2)*inv_error(2*p-1)

def theoretical_qunatiles(data):
    data = data.dropna()
    sorted_data = sorted(data.tolist())
    n = len(data)
    rank = np.arange(1,n+1)
    probabilities = (rank-0.5)/n
    theoretical_quantiles = [inverse_cdf(p)for p in probabilities]
    mean = np.mean(sorted_data)
    sd = np.std(sorted_data)
    x = np.linspace(np.min(theoretical_quantiles), np.max(theoretical_quantiles),100)
    y = x * sd + mean
    return theoretical_quantiles, sorted_data, x, y
#now creating some of visuals 
theoretical_qunatiles_r, sorted_data_r, x_r, y_r = theoretical_qunatiles(r)
theoretical_qunatiles_d, sorted_data_d, x_d, y_d = theoretical_qunatiles(d)

ax3 = axes[1][0]
ax3.patch.set_facecolor("#3d0000")

#(osm, osr), (slope, intercept, _) = stats.probplot(sorted_data, dist='norm')
#osm = np.array(osm); osr = np.array(osr)

ax3.scatter(theoretical_qunatiles_r, sorted_data_r, color="#ffffff", alpha=0.25, s=3,
            label='Data quantiles', zorder=2)
ax3.plot(x_r,y_r,
         color="#98ce03", lw=2, label='Normal reference', zorder=3)

ax3.set_xlabel("Theoretical Quantiles")
ax3.set_ylabel("Sample Quantiles")
ax3.set_title("Q-Q Plot for rolling return")
ax3.legend()
ax3.grid(True, alpha = 0.5)

ax4 = axes[1][1]
ax4.patch.set_facecolor("#3d0000")
ax4.scatter(theoretical_qunatiles_d, sorted_data_d, color = "#ffffff",alpha = 0.25, s = 3, label = 'Data Quantiles', zorder = 2)
ax4.plot(x_d, y_d, color = "#98ce30" , lw =2, label = 'Normal reference', zorder = 3)
ax4.set_xlabel("Theoretical Quantiles")
ax4.set_ylabel("Sample Quantiles")
ax4.set_title("Q-Q plot for daily return")
ax4.legend()
ax4.grid(True, alpha = 0.5)

plt.show()















