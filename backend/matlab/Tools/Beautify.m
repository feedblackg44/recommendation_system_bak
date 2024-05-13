function [correct_dict, deals_arr, items_arr, items] = Beautify(input_table, max_investment_period)
correct_dict = containers.Map('KeyType', 'int32', 'ValueType', 'any');

% deals_delete = ["SG-100"];
% deals_delete = "SG-100";
% input_table(ismember(input_table.DealID, deals_delete), :) = [];

deal_names = input_table.DealID;
items_num = input_table.ItemNo;

items_name = input_table.ItemName;
items_size = input_table.ItemSize;
discount_moq = input_table.MinimumOrderQuantity;
purchase_prices = input_table.PurchasePrice;
sale_prices = input_table.SalePrice;
avg_daily_sales = input_table.AverageDailySales;
inventory = input_table.Inventory;
system_sq = input_table.SystemSuggestedQuantity;
system_cov_days = input_table.SystemCoverageDays;
credit_terms = input_table.CreditTerms;

[items_arr, ~, ~] = unique(items_num, 'stable');
[deals_arr, ~, ~] = unique(deal_names, 'stable');

items_numbers = zeros(size(items_num));
for i = 1:length(items_arr)
    items_numbers(ismember(items_num, items_arr(i))) = i;
end

deals_numbers = zeros(size(deal_names));
for i = 1:length(deals_arr)
    deals_numbers(ismember(deal_names, deals_arr(i))) = i;
end

% disp(items_numbers)

items = containers.Map('KeyType', 'int32', 'ValueType', 'any');

for i = 1:length(deals_numbers)
    if ~isKey(correct_dict, deals_numbers(i))
        correct_dict(deals_numbers(i)) = containers.Map('KeyType', 'int32', 'ValueType', 'any');
    end
    if ~isKey(correct_dict(deals_numbers(i)), items_numbers(i))
        current_deal = correct_dict(deals_numbers(i));
        cur_item = containers.Map;
        cur_item('ItemNum') = items_num(i);
        cur_item('ItemName') = items_name(i);
        cur_item('ItemSize') = items_size(i);
        cur_item('MOQs') = discount_moq(i);
        cur_item('PurchasePrices') = purchase_prices(i);
        cur_item('SalePrice') = sale_prices(i);
        cur_item('AverageDailySales') = avg_daily_sales(i);
        cur_item('Inventory') = max(inventory(i), 0);
        cur_item('SystemSuggestedQuantity') = ceil(max(system_sq(i), ...
            system_cov_days(i) * avg_daily_sales(i) - max(inventory(i), 0)));
        cur_item('OptimizedSuggestedQuantity') = ceil(max(system_sq(i), ...
            system_cov_days(i) * avg_daily_sales(i) - max(inventory(i), 0)));
        cur_item('SystemCoverageDays') = system_cov_days(i);
        cur_item('CreditTerms') = credit_terms(i);
        cur_item('MaxInvestmentPeriod') = max_investment_period;
        cur_item('Deal') = current_deal;
        cur_item('DealName') = deal_names(i);
        cur_item('AddToTotal') = 0;
        cur_item('CanBeSoldTotal') = CanBeSoldTotal(avg_daily_sales(i), ...
            inventory(i), max_investment_period);
        cur_item('CanBeSoldCredit') = CanBeSoldTotal(avg_daily_sales(i), ...
            inventory(i), credit_terms(i));
        cur_item('DaysAdd') = 0;
        cur_item('Included') = false;
        cur_item('IncludedDispersion') = false;
        cur_item('ABC') = 'C';
        current_deal(items_numbers(i)) = cur_item;
        items(items_numbers(i)) = current_deal(items_numbers(i));
    else
        current_deal = correct_dict(deals_numbers(i));
        current_item = current_deal(items_numbers(i));
        
        MOQs = current_item('MOQs');
        MOQs(end+1) = discount_moq(i);
        current_item('MOQs') = MOQs;
        
        PurchasePrices = current_item('PurchasePrices');
        PurchasePrices(end+1) = purchase_prices(i);
        current_item('PurchasePrices') = PurchasePrices;
    end
end
end

