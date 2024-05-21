function days_for_sale = DaysForSale(item)
avg_daily_sales = item('AverageDailySales');
inventory = item('Inventory');
best_sq = item('BestSuggestedQuantity');

days_for_sale = 0;
if avg_daily_sales ~= 0
    days_for_sale = (best_sq + inventory) / avg_daily_sales;
end
end