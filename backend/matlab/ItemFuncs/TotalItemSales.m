function total_item_sales = TotalItemSales(item)
sale_price = item('SalePrice');
sold_amount = item('OptimizedSuggestedQuantity');
total_item_sales = sale_price * sold_amount;
end