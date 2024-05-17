import json
import math
import os
from datetime import datetime

import matlab.engine
import numpy as np
import psutil

from .beautify import beautify
from .map_to_table import map_to_table
from .prepare_file import main as prepare_file
from .write_out_table import write_out_table
from .fill_formulas import main as fill_formulas


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return float(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(CustomJSONEncoder, self).default(obj)


class GeneticAlgorithm:
    def __init__(self, config_path, host=None, port=None):
        self._lb = None
        self._data_table = None
        self._single = None
        self._solution = None
        self._matlab_output = None
        self._data = None
        self._max_budget = None
        self._min_budget = None
        self._num_cores = psutil.cpu_count(logical=False)

        self._host = "" if not host else host
        self._port = "" if not port else str(port)

        self._max_investment_period = None
        self.selected_file = None

        self._config = None
        self._load_config(config_path)

        self._eng = matlab.engine.start_matlab()
        self._make_matlab_config()

    @property
    def solutions_amount(self):
        return len(self._solution.get('fbests', {}))

    @property
    def max_investment_period(self):
        return self._max_investment_period

    @max_investment_period.setter
    def max_investment_period(self, value):
        self._max_investment_period = float(value)

    @property
    def data(self):
        return self._data

    def precalculate(self, selected_file, max_investment_period):
        self.selected_file = selected_file
        self.max_investment_period = max_investment_period

        self._data_table = prepare_file(self.selected_file)

        data, deals_arr, items_arr, items = beautify(self._data_table,
                                                     self.max_investment_period)
        data_str = json.dumps(data, cls=CustomJSONEncoder)

        min_budget, max_budget, data_str, lb, *args = self._eng.Precalculation(data_str,
                                                                               self.max_investment_period,
                                                                               nargout=7)
        self._min_budget = min_budget
        self._max_budget = max_budget
        self._data = json.loads(data_str)
        self._lb = lb
        self._matlab_output = args

        return min_budget, max_budget

    def _matlab_main_func(self, matlab_map_order, budget, budget_credit,
                          pop_multiplier, max_gen_multiplier, max_stall_gen_multiplier, *args):
        xbest, fbest, total_budget, deals_variants, check_ub, order = self._eng.MainFunc(
            float(budget),
            budget_credit,
            matlab_map_order,
            self._lb,
            *args,
            self._host,
            self._port,
            pop_multiplier,
            max_gen_multiplier,
            max_stall_gen_multiplier,
            nargout=6
        )

        return xbest, fbest, total_budget, deals_variants, check_ub, order

    def _main_func(self, min_budget, max_budget, step, single, budget_credit,
                   pop_multiplier, max_gen_multiplier, max_stall_gen_multiplier, *args):
        matlab_map_order = self._eng.OrderToMap(json.dumps(self._data,
                                                           cls=CustomJSONEncoder),
                                                nargout=1)

        xbests = {}
        fbests = {}

        self._start_par_pool()

        if (single and len(self._lb)) or not len(self._lb):
            print(f"Running for {max_budget}$...")

            xbest, fbest, total_budget, deals_variants, check_ub, order = self._matlab_main_func(
                matlab_map_order,
                max_budget,
                budget_credit,
                pop_multiplier,
                max_gen_multiplier,
                max_stall_gen_multiplier,
                *args
            )

            xbest = [i for i in xbest[0]] if not isinstance(xbest, float) else [xbest]

            xbests[total_budget] = xbest
            fbests[total_budget] = -fbest
        else:
            print(f"Running for {min_budget}-{max_budget}$ with step={step}...")
            deals_variants = None
            check_ub = [[None]]
            order = None
            budget_range = list(np.arange(min_budget, max_budget, step))
            budget_range.append(max_budget)
            for budget in budget_range:
                print(f"Running for {budget}$...")

                xbest, fbest, total_budget, deals_variants, check_ub, order = self._matlab_main_func(
                    matlab_map_order,
                    budget,
                    budget_credit,
                    pop_multiplier,
                    max_gen_multiplier,
                    max_stall_gen_multiplier,
                    *args
                )

                last_key = list(fbests.keys())[-1] if fbests else None
                if not last_key or (last_key and fbests[last_key] != -fbest):
                    xbest = [i for i in xbest[0]] if not isinstance(xbest, float) else [xbest]

                    xbests[total_budget] = xbest
                    fbests[total_budget] = -fbest
                print(f"Finished for {budget}$ with Profit: {fbest}$")

        self._stop_par_pool()

        deals_variants = self._eng.MapToJson(deals_variants, nargout=1)
        order = self._eng.MapToJson(order, nargout=1)
        check_ub = [bool(i) for i in check_ub[0]] if not isinstance(check_ub, float) else [bool(check_ub)]

        return xbests, fbests, deals_variants, check_ub, order

    def run(self, max_budget, min_budget=0, step=0, single=True, budget_credit=False,
            pop_multiplier=4, max_gen_multiplier=20, max_stall_gen_multiplier=3):
        self._single = single
        xbests, fbests, deals_variants, check_ub, data_str = self._main_func(
            float(min_budget),
            float(max_budget),
            float(step),
            single,
            budget_credit,
            pop_multiplier,
            max_gen_multiplier,
            max_stall_gen_multiplier,
            *self._matlab_output
        )

        self._data = json.loads(data_str)

        deals_variants = json.loads(deals_variants)

        self._solution = {
            'xbests': xbests,
            'fbests': fbests,
            'deals_variants': deals_variants,
            'check_ub': check_ub
        }

    def save_solution(self, selected_dir, budget=None):
        xbests = self._solution['xbests']
        fbests = self._solution['fbests']
        deals_variants_all = self._solution['deals_variants']
        check_ub = self._solution['check_ub']

        min_budget = min(list(fbests.keys()))
        max_budget = max(list(fbests.keys()))

        for i, (choosed_budget, fbest) in enumerate(fbests.items()):
            if len(fbests) > 1 and not self._single and budget:
                choosed_budget = budget
                if choosed_budget < self._min_budget:
                    choosed_budget = self._min_budget
                elif choosed_budget > self._max_budget:
                    choosed_budget = self._max_budget
                choosed_budget = math.ceil(choosed_budget)

            xbest = xbests[choosed_budget]
            xbest = [xbest] if not isinstance(xbest, list) else xbest

            k = 0
            deals_variants_all_keys = list(deals_variants_all.keys())
            for j, key in enumerate(self._data.keys()):
                if check_ub[j]:
                    deal_vars = deals_variants_all[deals_variants_all_keys[k]]
                    self._data[key] = deal_vars[f'x{int(xbest[k])}']
                    k += 1

            choosed_budget = float(choosed_budget.replace('x', '')) if isinstance(choosed_budget, str) \
                else choosed_budget

            table_out, second_table, third_table = map_to_table(self._data, fbest, self.max_investment_period)

            self.selected_file = self.selected_file.replace('/', '\\')
            dotIndex = self.selected_file.rfind('.')
            part1 = self.selected_file[:dotIndex]
            lastSlashIndex = part1.rfind('\\')
            part1 = part1[lastSlashIndex + 1:]

            correct_dir = os.path.join(selected_dir, datetime.today().strftime('%d.%m.%Y'), str(part1))
            if not budget and len(fbests) > 1 and not self._single:
                correct_dir = os.path.join(correct_dir,
                                           f"{self.max_investment_period} days "
                                           f"{int(min_budget)}-{int(max_budget)}$")

            if not os.path.exists(correct_dir):
                os.makedirs(correct_dir)
            elif not os.path.isdir(correct_dir):
                correct_dir += ' (1)'
                os.makedirs(correct_dir)

            out_name = os.path.join(correct_dir, f"{part1} {self.max_investment_period} days "
                                                 f"(P - {round(fbest)}$  B - {round(choosed_budget)}$) "
                                                 f"{datetime.today().strftime('%d.%m.%Y')}")

            write_out_table(table_out, self._data_table, second_table, third_table, f'{out_name}.xlsx')

            fill_formulas(f'{out_name}.xlsx')

            if budget or self._single:
                break

    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            self._config = json.load(f)

    def _make_matlab_config(self, engine=None):
        if not engine:
            engine = self._eng
        engine.cd(self._config['main_path'], nargout=0)
        for path in self._config['other_paths']:
            engine.addpath(path, nargout=0)

    def _start_par_pool(self, engine=None, num_cores=None):
        if not num_cores:
            num_cores = self._num_cores
        if not engine:
            engine = self._eng
        engine.eval(f"parpool({num_cores});", nargout=0)

    def _stop_par_pool(self, engine=None):
        if not engine:
            engine = self._eng
        engine.eval("delete(gcp('nocreate'));", nargout=0)
