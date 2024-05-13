function FixResultMOQs(order, items, max_budget)

memoDSBD = memoize(@DealSumByDeal);

arr_order = [];
for i = 1:length(order)
    arr_order = [arr_order, {order(i)}];
end

functionValues = arrayfun(@DailySales, arr_order);
[~, sortedIndices] = sort(functionValues);
sorted_order = arr_order(sortedIndices);

flag_break = ceil(length(sorted_order) * 0.85);
for i = 1:length(sorted_order)
    if i >= flag_break
        total_budget = 0;
        for idx = 1:length(items)
            total_budget = total_budget + ItemBudget(items, idx, [], memoDSBD);
        end
        if total_budget > max_budget
            break;
        end
    end

    deal = sorted_order(i);
    deal = deal{1};
    items_v = deal.values;
    credit_amount = 0;
    current_amount = 0;
    for k = 1:length(items_v)
        item = items_v{k};
        if item('AverageDailySales') > 0 && ceil(item('CanBeSoldCredit'))
            credit_amount = credit_amount + ceil(item('CanBeSoldCredit'));
        else
            credit_amount = credit_amount + item('SystemSuggestedQuantity');
        end
        current_amount = current_amount + item('OptimizedSuggestedQuantity');
    end
    all_moqs = ValidMOQs(deal);
    moqs_credit = all_moqs(all_moqs <= credit_amount);
    min_valid_moq = max(moqs_credit);
    if current_amount < min_valid_moq
        l_items = containers.Map('KeyType', 'int32', 'ValueType', 'any');
        for j = 1:length(items_v)
            item = items_v{j};
            if item('Included')
                l_items(j) = item;
            end
        end
        while DealSumByDeal(deal, items_v, []) < min_valid_moq
            minimum = inf;
            index = 0;
            i_keys = l_items.keys;
            for j = 1:length(i_keys)
                item = l_items(i_keys{j});
                current_days = DaysForSale(l_items, i_keys{j}, []) + ...
                    1 / item('AverageDailySales');
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

for i = 1:length(sorted_order)
    total_budget = 0;
    for idx = 1:length(items)
        total_budget = total_budget + ItemBudget(items, idx, [], memoDSBD);
    end
    if total_budget > max_budget
        break;
    end

    deal = sorted_order(i);
    deal = deal{1};
    items_v = deal.values;
    current_amount = 0;
    for k = 1:length(items_v)
        item = items_v{k};
        current_amount = current_amount + item('OptimizedSuggestedQuantity');
    end
    all_moqs = ValidMOQs(deal);
    min_valid_moq = max(all_moqs);
    if current_amount < min_valid_moq
        l_items = containers.Map('KeyType', 'int32', 'ValueType', 'any');
        for j = 1:length(items_v)
            item = items_v{j};
            if item('Included')
                l_items(j) = item;
            end
        end
        while DealSumByDeal(deal, items_v, []) < min_valid_moq
            minimum = inf;
            index = 0;
            i_keys = l_items.keys;
            for j = 1:length(i_keys)
                item = l_items(i_keys{j});
                current_days = DaysForSale(l_items, i_keys{j}, []) + ...
                    1 / item('AverageDailySales');
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

backwards_order = flipud(sorted_order);

for i = 1:length(backwards_order)
    total_budget = 0;
    for idx = 1:length(items)
        total_budget = total_budget + ItemBudget(items, idx, [], memoDSBD);
    end
    if total_budget < max_budget
        break;
    end

    deal = backwards_order(i);
    deal = deal{1};
    min_moq = MinMOQByDeal(deal);
    items_v = deal.values;
    current_amount = 0;
    for k = 1:length(items_v)
        item = items_v{k};
        current_amount = current_amount + item('OptimizedSuggestedQuantity');
    end
    all_moqs = ValidMOQs(deal);
    valid_moqs = all_moqs(all_moqs >= min_moq);
    min_valid_moq = min(valid_moqs);
    if current_amount > min_valid_moq
        l_items = containers.Map('KeyType', 'int32', 'ValueType', 'any');
        for j = 1:length(items_v)
            item = items_v{j};
            if item('Included')
                l_items(j) = item;
            end
        end
        while DealSumByDeal(deal, items_v, []) > min_valid_moq
            maximum = -inf;
            index = 0;
            i_keys = l_items.keys;
            for j = 1:length(i_keys)
                item = l_items(i_keys{j});
                current_days = DaysForSale(l_items, i_keys{j}, []) - ...
                    1 / item('AverageDailySales');
                if current_days > maximum
                    maximum = current_days;
                    index = i_keys{j};
                end
            end
            needed_item = l_items(index);
            needed_item('OptimizedSuggestedQuantity') = needed_item('OptimizedSuggestedQuantity') - 1;
        end
    end
end
end