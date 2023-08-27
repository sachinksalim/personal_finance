import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def visualize_summary(df):
    # Get unique values in column X and create a colormap
    unique_x_values = df['BankName'].unique()
    num_unique_values = len(unique_x_values)
    color_map = plt.get_cmap('tab10', num_unique_values)
    x_to_color = {x_value: color_map(i) for i, x_value in enumerate(unique_x_values)}
    df['Color'] = df['BankName'].map(x_to_color)

    # Plotting the horizontal bar chart
    plt.figure(figsize=(10, 6))
    plt.barh(df['BankName']+'-'+df['AccHolder']+'-'+df['AccType'], df['End_Date'] - df['Start_Date'],
    left=df['Start_Date'], color=df['Color'])
    plt.xlabel('Date')
    # plt.ylabel('Item')
    plt.title('Start and End Dates of Transactions')
    plt.tight_layout()

    # Formatting date on x-axis
    date_format = '%Y-%m-%d'
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter(date_format))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=3))

    # Adding margin to the left of the x-axis
    margin = timedelta(days=7)  # Adjust the number of days for the desired margin
    x_min = df['Start_Date'].min() - margin
    x_max = df['End_Date'].max() + margin
    plt.gca().set_xlim(x_min, x_max)

    # Inverting y-axis
    plt.gca().invert_yaxis()

    plt.show()

def convert_currency_to_num(data: pd.Series):
    return data.str.replace("$", "").str.replace(",", "").fillna(0).astype(float)

def filter_data_by_date(data, year, month):
    mask = (data['Date'].dt.month == month) & (data['Date'].dt.year == year)
    return data[mask]

def summary_statistics(df_full, AccHolder, BankName, AccType):
    def summary(df):
        no_of_entries = len(df)
        oldest_date = df['Date'].dt.date.min()
        newest_date = df['Date'].dt.date.max()
        summary_data['AccHolder'].append(bank.value)
        summary_data['BankName'].append(owner.value)
        summary_data['AccType'].append(acc_type.value)
        summary_data['Start_Date'].append(oldest_date)
        summary_data['End_Date'].append(newest_date)
        summary_data['Entries'].append(no_of_entries)

    summary_data = {
        'BankName': [],
        'AccHolder': [],
        'AccType': [],
        'Start_Date': [],
        'End_Date': [],
        'Entries': []
    }
    for owner in AccHolder:
        for bank in BankName:
            for acc_type in AccType:
                df = df_full.query('AccHolder == @owner.value and BankName == @bank.value and AccType == @acc_type.value')
                if len(df):
                    summary(df)

    summary_df = pd.DataFrame(summary_data)
    summary_df['Start_Date'] = pd.to_datetime(summary_df['Start_Date'])
    summary_df['End_Date'] = pd.to_datetime(summary_df['End_Date'])
    return summary_df

def visualize_summary(df):
    # Get unique values in column X and create a colormap
    unique_x_values = df['BankName'].unique()
    num_unique_values = len(unique_x_values)
    color_map = plt.get_cmap('tab10', num_unique_values)
    x_to_color = {x_value: color_map(i) for i, x_value in enumerate(unique_x_values)}
    df['Color'] = df['BankName'].map(x_to_color)

    # Plotting the horizontal bar chart
    plt.figure(figsize=(10, 6))
    plt.barh(df['BankName']+'-'+df['AccHolder']+'-'+df['AccType'], df['End_Date'] - df['Start_Date'],
    left=df['Start_Date'], color=df['Color'])
    plt.xlabel('Date')
    # plt.ylabel('Item')
    plt.title('Start and End Dates of Transactions')
    plt.tight_layout()

    # Formatting date on x-axis
    date_format = '%Y-%m-%d'
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter(date_format))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=3))

    # Adding margin to the left of the x-axis
    margin = timedelta(days=7)  # Adjust the number of days for the desired margin
    x_min = df['Start_Date'].min() - margin
    x_max = df['End_Date'].max() + margin
    plt.gca().set_xlim(x_min, x_max)

    # Inverting y-axis
    plt.gca().invert_yaxis()

    plt.show()