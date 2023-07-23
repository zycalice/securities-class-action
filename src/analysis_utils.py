import os
import pandas as pd
import seaborn as sns
import datetime
import sys

sys.path.append("..")


# Top 10 count
def top10_count(data, var, sort, top=10):
    return data.groupby(var).count().sort_values(by=sort, ascending=False).head(top)


# Create month, year, month_year variables
def create_date_intervals(data, var):
    data['year_' + var] = pd.to_datetime(data[var]).dt.to_period('Y')
    data['yearmonth_' + var] = pd.to_datetime(data[var]).dt.to_period('M')
    try:
        data['month_' + var] = data[var].apply(lambda x: datetime.datetime.strptime(x, "%m/%d/%Y").month)
    except:
        data['month_' + var] = data[var].apply(lambda x: datetime.datetime.strptime(x, "%m/%d/%y").month)


# Time series for month_year
def time_series(data, date_interval, var):
    if date_interval.split("_")[0] in ["yearmonth"]:
        data.groupby(date_interval).count()[var].plot()
    else:
        data.groupby(date_interval).count()[var].plot(kind='bar')
