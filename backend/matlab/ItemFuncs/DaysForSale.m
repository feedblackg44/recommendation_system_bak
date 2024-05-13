function days_for_sale = DaysForSale(item)
avg_daily_sales = item('AverageDailySales');
inventory = item('Inventory');
optimized_sq = item('OptimizedSuggestedQuantity');

days_for_sale = 0;
if avg_daily_sales ~= 0
    days_for_sale = (optimized_sq + inventory) / avg_daily_sales;
end
end