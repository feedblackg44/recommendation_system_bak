function thirty_days_sales = ThirtyDaysSales(item)
avg_daily_sales = item('AverageDailySales');
inventory = item('Inventory');
sale_price = item('SalePrice');
sold_amount = SoldAmount(item);

thirty_days_sales = 0;
if sold_amount > 0
    thirty_days_sales = sale_price * min(sold_amount, ...
        max(30*avg_daily_sales - inventory, 0));
end
end