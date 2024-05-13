function margin = WeightedAverageThirtyDayProfitMargin(items, item, memoBSBD)
sum_sales = 0;
item_names = items.keys;
for i = 1:length(item_names)
    sum_sales = sum_sales + ThirtyDaysSales(item);
end

margin = 0;
if sum_sales > 0
    margin = ThirtyDaysProfit(item, memoBSBD) / sum_sales;
end
end