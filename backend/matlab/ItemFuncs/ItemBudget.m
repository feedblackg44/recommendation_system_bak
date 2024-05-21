function item_budget = ItemBudget(item, moq, memoBSBD)
best_sq = item('BestSuggestedQuantity');
purchase_price = PurchasePrice(item, moq, memoBSBD);
item_budget = best_sq * purchase_price;
end