function [min_budget, max_budget, order_json, lb, ub, check_ub, deals_variants_all] = Precalculation(order_json, max_investment_period)
    order = JsonToMap(order_json);

    order_keys = order.keys;
    for i = 1:length(order_keys)
        deal = order(order_keys{i});
        deal_v = deal.values;
        for j = 1:length(deal_v)
            item = deal_v{j};
            item('Deal') = deal;
        end
    end

    min_moqs = PrepareMinMOQs(order);
    PrepareFlag(order, min_moqs, max_investment_period);
    PrecalcBadDeals(order, min_moqs);

    lb = [];
    ub = [];
    check_ub = [];

    deals_variants_all = containers.Map('KeyType', 'double', 'ValueType', 'any');
    k = 1;
    deals = order.values;
    for i = 1:length(deals)
        vars_map = GetAllDealVariants(deals{i});
        if length(vars_map) > 1
            lb(end+1) = 1;
            ub(end+1) = length(vars_map);
            check_ub(end+1) = true;
            deals_variants_all(k) = vars_map;
            k = k + 1;
        else
            check_ub(end+1) = false;
        end
    end

    min_budget = 0;
    max_budget = 0;
    k = 1;
    order_keys = order.keys;
    for i = 1:length(order_keys)
        deal = order(order_keys{i});
        deal_v = deal.values;
        for j = 1:length(deal_v)
            item = deal_v{j};
            min_budget = min_budget + ItemBudget(item, 0, @DealSumByDeal);
        end
        if check_ub(i)
            deal_vars = deals_variants_all(k);
            v_keys = deal_vars.keys;
            order(i) = deal_vars(v_keys{length(v_keys)});
            k = k + 1;
        end
        deal = order(order_keys{i});
        deal_v = deal.values;
        for j = 1:length(deal_v)
            item = deal_v{j};
            max_budget = max_budget + ItemBudget(item, 0, @DealSumByDeal);
        end
    end

    max_budget = ceil(max_budget);
    min_budget = ceil(min_budget);

    order_json = MapToJson(order);
end