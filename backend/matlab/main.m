clc
clear

input_file = '';
max_period = 0;
budget_mode = '';
work_mode = '';
choosed_budget = 0;
step_input = 0;
save_all = false;

[max_budget, min_budget, step, single, xbests, fbests, order, check_ub, deals_variants_all, ...
    choice_func, items, max_investment_period, filename, table1, x, y, z] = MainFunc(...
        input_file, max_period, budget_mode, work_mode, choosed_budget, step_input, save_all);

draw = false;
save_all = false;
dir_out = '';

EndOfMain(max_budget, min_budget, step, single, xbests, fbests, order, check_ub, deals_variants_all, ...
    choice_func, items, max_investment_period, filename, table1, x, y, z, draw, save_all, dir_out)

% func for getting another result from same data

get_result = @()EndOfMain(max_budget, min_budget, step, single, xbests, fbests, order, check_ub, deals_variants_all, ...
    choice_func, items, max_investment_period, filename, table1, x, y, z, true, false, '');
