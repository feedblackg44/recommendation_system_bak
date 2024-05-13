function sold_amount = SoldAmount(item)
optimized_sq = item('OptimizedSuggestedQuantity');
% can_be_sold_total = item('CanBeSoldTotal');

% sold_amount = min(optimized_sq, can_be_sold_total);
sold_amount = optimized_sq;
end