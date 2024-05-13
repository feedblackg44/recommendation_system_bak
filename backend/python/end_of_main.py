import math
import os
from datetime import datetime
from tkinter.filedialog import askdirectory

from fill_formulas import main as fill_formulas
from map_to_table import map_to_table
from write_out_table import write_out_table
from util import ask_integer


def end_of_main(min_budget, max_budget, single, xbests, fbests, order, check_ub, deals_variants_all,
                max_investment_period, filename, table_in, save_all):
    for i, (choosed_budget, fbest) in enumerate(fbests.items()):
        if len(fbests) > 1 and not single and not save_all:
            choosed_budget = ask_integer(f"Choose budget to spend from {min_budget}$ to {max_budget}$")
            if choosed_budget < min_budget:
                choosed_budget = min_budget
            elif choosed_budget > max_budget:
                choosed_budget = max_budget
            choosed_budget = math.ceil(choosed_budget)

        xbest = xbests[choosed_budget]
        xbest = [xbest] if not isinstance(xbest, list) else xbest

        k = 0
        deals_variants_all_keys = list(deals_variants_all.keys())
        for j, key in enumerate(order.keys()):
            if check_ub[j]:
                deal_vars = deals_variants_all[deals_variants_all_keys[k]]
                order[key] = deal_vars[f'x{xbest[k]}']
                k += 1

        choosed_budget = float(choosed_budget.replace('x', ''))

        print(f"Saving file with profit = {fbest} and budget = {choosed_budget}")

        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.abspath(os.path.join(current_path, os.pardir))

        selected_dir = askdirectory(title="Choose directory to save results",
                                    initialdir=parent_path)

        table_out, second_table, third_table = map_to_table(order, fbest, max_investment_period)

        dotIndex = filename.rfind('.')
        part1 = filename[:dotIndex]
        out_name = os.path.join(selected_dir, f"{part1} {max_investment_period} days "
                                              f"(P - {round(fbest)}$  B - {round(choosed_budget)}$) "
                                              f"{datetime.today().strftime('%d.%m.%Y')}")

        write_out_table(table_out, table_in, second_table, third_table, f'{out_name}.xlsx')

        fill_formulas(f'{out_name}.xlsx')

        if not save_all:
            break
