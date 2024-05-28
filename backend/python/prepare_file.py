import argparse
import pandas as pd
from openpyxl import load_workbook


def main(file_name=None):
    if not file_name:
        parser = argparse.ArgumentParser()
        parser.add_argument("--excelname", help="Excel file name")
        args = parser.parse_args()
        filename = args.excelname
    else:
        filename = file_name

    wb = load_workbook(filename)
    sheet = wb.active
    sheet.title = 'Sheet1'

    data = sheet.values
    columns = next(data)[0:]
    data = list(data)
    data = pd.DataFrame(data, columns=columns)

    if 'Replenishment Template Code' in data.columns:
        data = data.drop(columns=['Replenishment Template Code'])

    if 'Minimum Purchase UoM Quantity' in data.columns:
        data = data.rename(columns={'Minimum Purchase UoM Quantity': 'Minimum Order Quantity'})

    if 'Item No.' in data.columns:
        data = data.rename(columns={'Item No.': 'Item No'})

    duplicated_items = data.groupby('Item No').filter(lambda x: x['Deal ID'].nunique() > 1)['Item No'].unique()

    if len(duplicated_items) > 0:
        raise ValueError(f'Item No {duplicated_items} is associated with multiple Deal ID')

    negative_profit_deals = data.groupby('Item No').filter(lambda x: x['Profit'].max() <= 0)['Item No'].unique()

    if len(negative_profit_deals) > 0:
        raise ValueError(f'Item No {negative_profit_deals} have all Profit values less than or equal to 0')

    data = data.groupby('Deal ID').filter(lambda x: x['System Suggested Quantity'].sum() != 0)

    sorted_data = data.sort_values(by=['Deal ID', 'Item No', 'Minimum Order Quantity']).reset_index(drop=True)

    wb.close()

    return sorted_data
