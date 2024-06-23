import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

def convert_currency_to_num(data: pd.Series):
    return data.str.replace("$", "").str.replace(",", "").fillna(0).astype(float)

def find_category_from_autocat(auto_cat):
    res = {'Category': 'others', 'Subcategory': 'others'}
    if not pd.isna(auto_cat):
        auto_cat = auto_cat.lower()
        if auto_cat == 'food & drink':
            auto_cat = 'restaurant'
        elif auto_cat == 'gasoline':
            auto_cat = 'gas'
        res['Category'] = auto_cat
    # 'Entertainment', 'Groceries', 'Food & Drink', 'Travel',
    #    'Travel/ Entertainment', 'Awards and Rebate Credits',
    #    'Restaurants', 'Gasoline', 'Services', 'Education', 'Merchandise',
    #    'Health & Wellness', 'Shopping', 'Payments and Credits', 'Gas',
    #    'Fees & Adjustments', 'Supermarkets', 'Automotive',
    #    'Bills & Utilities', 'Department Stores', 'Personal',
    #    'Gifts & Donations', 'Home', 'Professional Services']
    return pd.Series(res)

def find_category_from_desc(desc, category_info):
    desc = desc.lower()
    desc = ' '.join(desc.strip().split()) # removing extra whitespace
    res = pd.Series({'Category': 'others', 'Subcategory': 'others'})
    max_len = -1
    for _, cat in category_info.iterrows():
        keyword = cat['Keyword'].lower()
        if (keyword in desc) and (len(keyword) > max_len):
            res = cat[['Category', 'Subcategory']]
            max_len = len(keyword)    
    return res

def find_category(row, category_info):
    res = find_category_from_desc(row['Description'], category_info)
    if res['Category'] == 'others':
        res = find_category_from_autocat(row['AutoCategory'])
    return res

def _filter_data_by_date_period(data, date_period):
    if date_period['type'] == 'all':
        return data
    elif date_period['type'] == 'from-to':
        pass
    elif date_period['type'] == 'month':
        mask = (data['Date'].dt.month == date_period['month']) & (data['Date'].dt.year == date_period['year'])
        return data[mask]
    else:
        return data

def _filter_data_by_holder(data, acc_holder):
    if acc_holder == 'any':
        return data
    elif acc_holder in ['sachin', 'nowrin', 'joint']:
        return data.query('AccHolder == @acc_holder')
    else:
        raise NotImplementedError

def filter_data_by_info(data, filter_info):
    data = _filter_data_by_holder(data, filter_info['acc_holder'])
    data = _filter_data_by_date_period(data, filter_info['date_period'])
    return data

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

def visualize_food(data):
    food_data = data.query("Category in ['groceries','restaurant'] ")
    food_data['Amount'] = -food_data['Amount']
    food_data['Date'] = pd.to_datetime(food_data['Date'])
    food_data['YearMonth'] = food_data['Date'].dt.to_period('M')
    groceries_trend = food_data.query("Category == 'groceries'").groupby('YearMonth')['Amount'].sum().reset_index()
    restaurant_trend = food_data.query("Category == 'restaurant'").groupby('YearMonth')['Amount'].sum().reset_index()
    groceries_trend['YearMonth'] = groceries_trend['YearMonth'].dt.to_timestamp()

    _, ax = plt.subplots(figsize=(10, 6))
    ax.plot(groceries_trend['YearMonth'], groceries_trend['Amount'], marker='o', linestyle='-', color='green', label='groceries')
    ax.plot(groceries_trend['YearMonth'], restaurant_trend['Amount'], marker='o', linestyle='-', color='red', label='restaurant')
    ax.text(0.1, 0.95, f"Groceries (median): {groceries_trend['Amount'].median():.0f}$", fontsize=12, horizontalalignment='left',
        verticalalignment='top', transform=ax.transAxes, color='green')
    ax.text(0.1, 0.90, f"Restaurant (median): {restaurant_trend['Amount'].median():.0f}$", fontsize=12, horizontalalignment='left',
        verticalalignment='top', transform=ax.transAxes, color='red')
    ax.set_title('Monthly Food Expenses')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount')
    ax.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def visualize_salary(data):
    salary_data = data.query("Category == 'salary'")
    salary_data['Date'] = pd.to_datetime(salary_data['Date'])
    salary_data['YearMonth'] = salary_data['Date'].dt.to_period('M')
    monthly_sum = salary_data.groupby('YearMonth')['Amount'].sum().reset_index()
    monthly_sum['YearMonth'] = monthly_sum['YearMonth'].dt.to_timestamp()
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_sum['YearMonth'], monthly_sum['Amount'], marker='o', linestyle='-')
    plt.title('Monthly Salary Amounts')
    plt.xlabel('Month')
    plt.ylabel('Total Amount')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

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

def check_string(text, pattern):
    if isinstance(pattern, str):
        return pattern in text
    elif isinstance(pattern, list):
        return any(check_string(text, pat) for pat in pattern)
    else:
        return False
    
def plot_pie(df):
    colors = sns.color_palette('pastel', n_colors = len(df))

    plt.pie(np.abs(df.values.squeeze()),
            labels = df.index + ": $" + np.abs(df.values.squeeze()).astype(int).astype(str),
            colors = colors,
            startangle = 90)
    plt.show()

def write_to_excel(data, filepath):
    data['Date'] = data['Date'].dt.date
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:

        data.to_excel(writer, 
                    index=False,
                    freeze_panes=(1,0),
                    sheet_name='Sheet_1',
                    engine='xlsxwriter')

        workbook  = writer.book
        worksheet = writer.sheets['Sheet_1']
        wrap_format = workbook.add_format({'text_wrap': True})
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 30, wrap_format)
        worksheet.set_column('D:D', 12, wrap_format)
        worksheet.set_column('H:H', 12)

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

class Logger:
    LOG_LEVEL_ORDER = ["DEBUG", "INFO", "WARNING", "ERROR"]

    def __init__(self, log_level="DEBUG", display_time=False):
        self.log_level = log_level
        self.display_time = display_time
        self.log(f"Logging level is: {log_level}", "INFO", forced=True)

    def log(self, message, level, forced=False):
        if not forced and not self.is_logging(level):
            return
        
        msg = f"[{level}] {message}"
        if self.display_time:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{timestamp}] {msg}"
        print(msg)

    def is_logging(self, level):
        try:
            current_level = self.LOG_LEVEL_ORDER.index(level)
            cutoff_level = self.LOG_LEVEL_ORDER.index(self.log_level)
        except ValueError:
            print(f"Invalid Logging Level: {level}")
            return False
        return current_level >= cutoff_level

    def debug(self, message):
        cur_level = "DEBUG"
        self.log(message, cur_level)

    def info(self, message):
        cur_level = "INFO"
        self.log(message, cur_level)

    def warning(self, message):
        cur_level = "WARNING"
        self.log(message, cur_level)

    def error(self, message):
        cur_level = "ERROR"
        self.log(message, cur_level)