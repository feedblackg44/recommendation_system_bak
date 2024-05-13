function total_item_budget = TotalItemBudget(items, item_num, x, memoBSBD)
item_budget = ItemBudget(items, item_num, x, memoBSBD);
days_for_sale = DaysForSale(items, item_num, x);
item = items(item_num);
credit_terms = item('CreditTerms');
loc_interest_rate = item('LocInterestRate');

total_item_budget = 0;
if days_for_sale ~= 0
    total_item_budget = ((item_budget / days_for_sale) * ...
        (min(credit_terms, days_for_sale) + ...
        max(days_for_sale - credit_terms, 0) * ...
        (1 + loc_interest_rate / 365 * ...
        max(days_for_sale - credit_terms, 0))));
end
end

% ((Q2/T2)*(MIN(45;T2)+MAX(T2-45;0)*(1+0,1/365*MAX(T2-45;0))))