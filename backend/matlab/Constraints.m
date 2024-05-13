function [c, ceq] = Constraints(x, max_budget, l_order, all_variants, check, BudgetFunc)

memoBSBD = memoize(@DealSumByDeal);
budgetFunc = BudgetFunc;

order_copy = containers.Map('KeyType', 'double', 'ValueType', 'any');
k = 1;
values = l_order.values;
for i = 1:length(values)
    if check(i)
        deal_vars = all_variants(k);
        order_copy(i) = deal_vars(x(k));
        k = k + 1;
    else
        order_copy(i) = values{i};
    end
end

total_budget = 0;
values_c = order_copy.values;
for i = 1:length(values_c)
    deal = values_c{i};
    deal_v = deal.values;
    for j = 1:length(deal_v)
        item = deal_v{j};
        total_budget = total_budget + budgetFunc(item, 0, memoBSBD);
    end
end
cons3 = total_budget - max_budget;

% All nonlinear constraints
c = cons3;

% No equality constraints
ceq = [];

% disp('С')