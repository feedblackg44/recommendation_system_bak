function PrecalcBadDeals(order, min_moqs)
    keys = order.keys;
    values = order.values;
    for i = 1:length(keys)
        cur_moqs = min_moqs(i);
        deal = values{i};
        items_v = deal.values;
        l_items = containers.Map('KeyType', 'int32', 'ValueType', 'any');
        for j = 1:length(items_v)
            item = items_v{j};
            if item('IncludedDispersion')
                l_items(j) = item;
            end
        end
        GetDealToMOQ(deal, cur_moqs(1))
    end
end

% init_pop = [];
% for i = 1:length(items)
%     item = items(i);
%     if item('IncludedDispersion')
%         init_pop(end+1) = item('OptimizedSuggestedQuantity');
%     end
% end
