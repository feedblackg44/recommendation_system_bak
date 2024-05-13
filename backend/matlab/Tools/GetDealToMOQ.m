function GetDealToMOQ(deal, desired_moq)
    items = deal.values;
    % for i = 1:length(items)
    %     item = items{i};
    %     item('OptimizedSuggestedQuantity') = item('SystemSuggestedQuantity');
    % end
    
    memoDSBD = @DealSumByDeal;
    
    if memoDSBD(deal) < desired_moq
        l_items = containers.Map('KeyType', 'int32', 'ValueType', 'any');
        for i = 1:length(items)
            item = items{i};
            if item('IncludedDispersion') && Profit(item, desired_moq, memoDSBD) > 0
                l_items(i) = item;
            end
        end
        if isempty(l_items)
            return
        end
        while memoDSBD(deal) < desired_moq
            minimum = inf;
            index = 0;
            i_keys = l_items.keys;
            for j = 1:length(i_keys)
                item = l_items(i_keys{j});
                item('OptimizedSuggestedQuantity') = item('OptimizedSuggestedQuantity') + 1;
                current_days = DispersionByDeal(item('Deal'), desired_moq);
                item('OptimizedSuggestedQuantity') = item('OptimizedSuggestedQuantity') - 1;
                if current_days < minimum
                    minimum = current_days;
                    index = i_keys{j};
                end
            end
            needed_item = l_items(index);
            needed_item('OptimizedSuggestedQuantity') = needed_item('OptimizedSuggestedQuantity') + 1;
        end
    end
end