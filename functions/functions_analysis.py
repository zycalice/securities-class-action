import os
import pandas as pd
import seaborn as sns
import sys
sys.path.append("..")

# Top 10
def top10(data, var, sort, top=10):
    return data.groupby(var).count().sort_values(by = sort,ascending = False).head(top)

