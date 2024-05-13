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
    def __init__(self, config_path):
        self._data_table = None
        self._single = None
        self._solution = None
        self._matlab_output = None
        self._data = None
        self._max_budget = None
        self._min_budget = None
        self._num_cores = psutil.cpu_count(logical=False)

        self._max_investment_period = None
        self.selected_file = None

        self._config = None
        self._load_config(config_path)

        self._eng = matlab.engine.start_matlab()
        self._make_matlab_config()

    @property
    def solutions_amount(self):
        return len(self._solution['xbests'])

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

        min_budget, max_budget, data_str, *args = self._eng.Precalculation(data_str,
                                                                           self.max_investment_period,
                                                                           nargout=7)
        self._min_budget = min_budget
        self._max_budget = max_budget
        self._data = json.loads(data_str)
        self._matlab_output = args

        return min_budget, max_budget

    def run(self, max_budget, min_budget=0, step=0, single=True, budget_credit=False):
        try:
            self._single = single
            self._start_par_pool()
            time_start = datetime.now()
            xbests, fbests, deals_variants, check_ub, data_str = self._eng.MainFunc(
                float(min_budget),
                float(max_budget),
                float(step),
                single,
                budget_credit,
                json.dumps(self._data,
                           cls=CustomJSONEncoder),
                *self._matlab_output,
                nargout=5
            )
            time_elapsed = datetime.now() - time_start
            self._stop_par_pool()
        except Exception as e:
            return str(e)

        self._data = json.loads(data_str)

        xbests = json.loads(xbests)
        fbests = json.loads(fbests)
        deals_variants = json.loads(deals_variants)

        check_ub = [bool(i) for i in check_ub[0]] if not isinstance(check_ub, float) else [bool(check_ub)]

        self._solution = {
            'xbests': xbests,
            'fbests': fbests,
            'deals_variants': deals_variants,
            'check_ub': check_ub
        }

        return "Time elapsed: " + str(time_elapsed)

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
                    self._data[key] = deal_vars[f'x{xbest[k]}']
                    k += 1

            choosed_budget = float(choosed_budget.replace('x', ''))

            table_out, second_table, third_table = map_to_table(self._data, fbest, self.max_investment_period)

            self.selected_file = self.selected_file.replace('/', '\\')
            dotIndex = self.selected_file.rfind('.')
            part1 = self.selected_file[:dotIndex]
            lastSlashIndex = part1.rfind('\\')
            part1 = part1[lastSlashIndex + 1:]

            correct_dir = os.path.join(selected_dir, str(part1), datetime.today().strftime('%d.%m.%Y'))
            if not budget and len(fbests) > 1 and not self._single:
                correct_dir = os.path.join(correct_dir,
                                           f"{self.max_investment_period} days "
                                           f"{min_budget}-{max_budget}$")

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

    def _make_matlab_config(self):
        self._eng.cd(self._config['main_path'], nargout=0)
        for path in self._config['other_paths']:
            self._eng.addpath(path, nargout=0)

    def _start_par_pool(self, num_cores=None):
        if not num_cores:
            num_cores = self._num_cores
        self._eng.eval(f"parpool({num_cores});", nargout=0)

    def _stop_par_pool(self):
        self._eng.eval("delete(gcp('nocreate'));", nargout=0)
