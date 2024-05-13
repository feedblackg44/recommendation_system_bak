function result = DispersionByDeal(deal, moq)
values = deal.values;
inv_sum = 0;
total_sum = 0;
for i = 1:length(values)
    item = values{i};
    if item('IncludedDispersion')
        inv_sum = inv_sum + item('Inventory');
        total_sum = total_sum + item('CanBeSoldTotal');
    end
end
full_sum = inv_sum + total_sum;

arr_delta = -1 * ones(1, length(values));
for i = 1:length(values)
    item = values{i};
    if item('IncludedDispersion')
        osq = (moq + inv_sum) / full_sum * (item('Inventory') + item('CanBeSoldTotal')) / item('AverageDailySales');
        days_current = (DaysForSale(item) - osq) ^ 2;
        arr_delta(i) = days_current;
    end
end
arr_delta(arr_delta == -1) = [];
result = 0;
if ~isempty(arr_delta)
    result = mean(arr_delta) / length(arr_delta);
end
end