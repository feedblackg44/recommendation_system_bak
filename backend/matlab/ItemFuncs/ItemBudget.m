function item_budget = ItemBudget(item, moq, memoBSBD)
optimized_sq = item('OptimizedSuggestedQuantity');
purchase_price = PurchasePrice(item, moq, memoBSBD);
item_budget = optimized_sq * purchase_price;
end