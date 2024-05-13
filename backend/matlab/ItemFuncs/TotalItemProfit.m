function total_item_profit = TotalItemProfit(item, memoBSBD)
profit = Profit(item, 0, memoBSBD);
sold_amount = SoldAmount(item);
total_item_profit = profit * sold_amount;
end