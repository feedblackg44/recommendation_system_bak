function PrepareFlag(order, min_moqs, max_days)
    keys = order.keys;
    for i = 1:length(keys)
        sum_totals = 0;
        deal = order(keys{i});
        items_nums = deal.keys;
        for j = 1:length(items_nums)
            item = deal(items_nums{j});
            if item('AverageDailySales') > 0 && floor(item('CanBeSoldTotal'))
                sum_totals = sum_totals + floor(item('CanBeSoldTotal'));
            else
                sum_totals = sum_totals + item('SystemSuggestedQuantity');
            end
        end
        moq = min(min_moqs(keys{i}));
        added = 0;
        while sum_totals + added < moq
            item_min_days = "";
            min_days = inf;
            for j = 1:length(items_nums)
                item = deal(items_nums{j});
                if item('AverageDailySales') > 0
                    days = (floor(item('CanBeSoldTotal')) + item('AddToTotal') ...
                        + item('Inventory') + 1) / item('AverageDailySales');
                    if days < min_days
                        min_days = days;
                        item_min_days = items_nums{j};
                    end
                end
            end
            if min_days < inf
                item = deal(item_min_days);
                item('AddToTotal') = item('AddToTotal') + 1;
                added = added + 1;
            else
                break;
            end
        end
        for j = 1:length(items_nums)
            item = deal(items_nums{j});
            if item('AverageDailySales') > 0
                item('DaysAdd') = item('AddToTotal') / item('AverageDailySales');
            end
            ssq = ceil(item('SystemSuggestedQuantity'));
            inv = item('Inventory');
            ads = item('AverageDailySales');
            if ads > 0
                item('IncludedDispersion') = (inv + ssq) / ads <= max_days + item('DaysAdd');
                item('Included') = (inv + 1 + ssq) / ads <= max_days + item('DaysAdd');
            end
        end
    end
end
