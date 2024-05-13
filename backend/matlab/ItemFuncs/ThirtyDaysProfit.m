function thirty_days_profit = ThirtyDaysProfit(item, memoBSBD)
avg_daily_sales = item('AverageDailySales');
inventory = item('Inventory');
sold_amount = SoldAmount(item);
profit = Profit(item, 0, memoBSBD);

quantity = min(sold_amount, max(30 * avg_daily_sales - inventory, 0));
if profit < 0 && quantity > 0
    thirty_days_profit = 100 / (profit * quantity);
else
    thirty_days_profit = profit * quantity;
end
end