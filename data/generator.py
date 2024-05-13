import math
import random

import pandas as pd


def generate_random_name():
    parts = ['Pro', 'Max', 'Tech', 'Data', 'Net', 'Core', 'Flex', 'Ultra', 'Nano', 'Smart', 'Alpha', 'Mega', 'Mini',
             'Hyper', 'Super']
    suffix = ['drive', 'wave', 'ware', 'link', 'byte', 'deck', 'box', 'sphere', 'grid', 'works', 'port', 'scan',
              'motion', 'frame', 'track']
    return random.choice(parts) + random.choice(suffix)


def generate_deals(deals_amount, max_items_per_deal):
    order = {}
    # Generate unique deal names
    deal_names = set()
    while len(deal_names) < deals_amount:
        deal_names.add(generate_random_name())

    items_count = 1
    for deal_name in deal_names:
        num_items = random.randint(1, max_items_per_deal)
        items = {}
        for _ in range(num_items):
            item_name = generate_random_name()

            system_coverage_days = 14
            average_daily_sales = random.randint(1, 200) / 100
            needed_quantity = system_coverage_days * average_daily_sales
            inventory = random.randint(1, math.ceil(needed_quantity * 1.2))
            system_suggested_quantity = max(0, math.ceil(needed_quantity - inventory))
            credit_terms = 45

            moq = {1: round(random.uniform(5, 100), 2)}
            additional_quantities = sorted(
                random.sample(range(2, (system_suggested_quantity + inventory) * max_items_per_deal),
                              k=random.randint(1, 4))
            )
            last_price = moq.get(1)
            min_purchase_price = last_price
            to_set = True
            for idx, quantity in enumerate(additional_quantities):
                new_price = round(last_price - random.uniform(0.5, 1.5), 2)
                if new_price < 1:
                    new_price = round(last_price - 0.1, 2)
                moq[quantity] = new_price
                last_price = new_price

                if idx >= len(additional_quantities) - 1 and to_set:
                    min_purchase_price = new_price
                    to_set = False

            sale_price = round(random.uniform(min_purchase_price, min_purchase_price * 1.3), 2)

            items[items_count] = {
                'Item Name': item_name,
                'Minimum Purchase UoM Quantity': list(moq.keys()),
                'Purchase Price': list(moq.values()),
                'Sale Price': sale_price,
                'Average Daily Sales': average_daily_sales,
                'Inventory': inventory,
                'System Suggested Quantity': system_suggested_quantity,
                'System Coverage Days': system_coverage_days,
                'Credit Terms': credit_terms
            }
            items_count += 1
        order[deal_name] = items

    return order


def convert_order_to_excel_rows(order):
    excel_rows = []
    for deal_name, items in order.items():
        for item_no, item_details in items.items():
            min_purchase_uom_quantity = item_details['Minimum Purchase UoM Quantity']
            purchase_price = item_details['Purchase Price']
            for qty, price in zip(min_purchase_uom_quantity, purchase_price):
                profit = item_details['Sale Price'] - price
                row = [
                    deal_name,
                    item_no,
                    item_details['Item Name'],
                    qty,
                    price,
                    item_details['Sale Price'],
                    profit,
                    item_details['Average Daily Sales'],
                    item_details['Inventory'],
                    item_details['System Suggested Quantity'],
                    item_details['System Coverage Days'],
                    item_details['Credit Terms']
                ]
                excel_rows.append(row)

    df = pd.DataFrame(excel_rows, columns=[
        'Deal ID',
        'Item No',
        'Item Name',
        'Minimum Purchase UoM Quantity',
        'Purchase Price',
        'Sale Price',
        'Profit',
        'Average Daily Sales',
        'Inventory',
        'System Suggested Quantity',
        'System Coverage Days',
        'Credit Terms'
    ])
    return df


def main():
    order = generate_deals(30, 10)
    df = convert_order_to_excel_rows(order)
    df.to_excel('data.xlsx', index=False)


if __name__ == '__main__':
    main()
