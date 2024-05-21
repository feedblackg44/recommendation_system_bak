function sold_amount = SoldAmount(item)
best_sq = item('BestSuggestedQuantity');
% can_be_sold_total = item('CanBeSoldTotal');

% sold_amount = min(best_sq, can_be_sold_total);
sold_amount = best_sq;
end