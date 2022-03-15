import pandas as pd
import random


def get_prevalences(filename)-> dict:
    df = pd.read_excel(filename, index_col=0)
    prev_range = df.to_dict()['prevalence']
    prevs = dict()
    for k, v in prev_range.items():
        item_ = dict()
        if type(v) == str:
            item_['min'], item_['max'] = [float(_) for _ in v.split('-')]
        else:
            item_['min'] = v
            item_['max'] = item_['min']
        prevs[k] = item_
    return prevs


def get_rec_rates(filename='recovery_rates.xlsx')-> pd.DataFrame:
    df = pd.read_excel(filename, index_col=0)
    return df
