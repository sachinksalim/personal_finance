import pandas as pd

def convert_currency_to_num(data: pd.Series):
    return data.str.replace("$", "").str.replace(",", "").fillna(0).astype(float)

def filter_data_by_date(data, year, month):
    mask = (data['Date'].dt.month == month) & (data['Date'].dt.year == year)
    return data[mask]