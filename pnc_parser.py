## PNC

import re
import pdfplumber
import pandas as pd
import glob

def parse_pnc_transaction(filename):
    def extract_transactions(pdf_path):
        transactions = []
        trans_period = None
        mmdd_pattern = re.compile(r"\d{2}/\d{2}")
        mmddyyyy_pattern = re.compile(r"\d{2}/\d{2}/\d{4}")

        def is_transaction(line):
            def is_daily_balance_detail(line):
                dates_in_line = mmdd_pattern.findall(line)
                return len(dates_in_line) > 1

            has_date = mmdd_pattern.match(line)
            return has_date and not is_daily_balance_detail(line)

        def parse_transaction(line_0, line_1, line_2):
            if is_transaction(line_1):
                return line_0
            else:
                if not is_transaction(line_2):
                    return line_0
                else:
                    return line_0 + ' ' + line_1
        
        def is_period(line):
            return line.startswith('For the period')

        def parse_period(line):
            dates_in_line = mmddyyyy_pattern.findall(line)
            return dates_in_line

        def is_credit(credit, line):
            if line.startswith("Deposits and Other Additions"):
                credit = True
            elif line.startswith("Banking/Debit Card Withdrawals and Purchases") or line.startswith("Online and Electronic Banking Deductions"):
                credit = False
            return credit
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split("\n")
                
                N = len(lines)
                credit = None
                for i in range(N-2):
                    credit = is_credit(credit, lines[i])
                    if is_transaction(lines[i]):
                        assert(credit is not None)
                        trans = parse_transaction(lines[i], lines[i+1], lines[i+2])
                        if credit:
                            trans = "+ " + trans
                        else:
                            trans = "- " + trans
                        transactions.append(trans)

                if trans_period is None:
                    for line in lines:
                        if is_period(line):
                            trans_period = parse_period(line)
        
        if trans_period is None:
            print("Error finding transaction period")

        return transactions, trans_period

    transactions, trans_period = extract_transactions(filename)

    mm_yy_map = {}
    for trans in trans_period:
        mm_yy_map[trans[:2]] = trans[-4:]

    data = []
    for transaction in transactions:
        credit, date, amount, *description = transaction.split(' ')
        date += '/' + mm_yy_map[date[:2]]
        amount = credit + amount.replace(",", "")
        description = ' '.join(description)
        data.append((date, amount, description))

    df = pd.DataFrame(data, columns=["Date", "Amount", "Description"])
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df["Amount"] = pd.to_numeric(df["Amount"])
    df = df.sort_values(by=['Date', 'Amount'])
    return df

def sync_pnc_data(root_dir):
    for name in ['nowrin', 'sachin']:
        pnc_filename = 'Statement_*.pdf'
        matched_files = glob.glob(f'{root_dir}/pnc/{name}/{pnc_filename}')
        dataframes = []

        for filename in matched_files:
            df = parse_pnc_transaction(filename)
            dataframes.append(df)
        pnc_df = pd.concat(dataframes, ignore_index=True)
        pnc_df = pnc_df.sort_values(by=['Date', 'Amount'])

        pnc_df.to_csv(f'{root_dir}/pnc/{name}.csv', index=False)
