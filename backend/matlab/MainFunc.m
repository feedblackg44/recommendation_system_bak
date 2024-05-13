function [xbests, fbests, deals_variants_all_json, check_ub, order_json] = MainFunc(min_budget, max_budget, step, single, budget_credit, order_json, lb, ub, check_ub, deals_variants_all)
    disp('Begin GA')
    
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

    BudgetFunc = @ItemBudgetOverCredit;
    if ~budget_credit
        BudgetFunc = @ItemBudget;
    end

    memoDSBD = memoize(@DealSumByDeal);

    pop_size = max(50, length(lb) * 4);
    max_generations = max(100, length(lb) * 20);
    max_stall_generations = max(50, length(lb) * 3);

    opts_ga = optimoptions(@ga, ...
                        'MaxGenerations', max_generations, ...
                        'MaxStallGenerations', max_stall_generations, ...
                        'PopulationSize', pop_size, ...
                        'CreationFcn', 'gacreationlinearfeasible', ...
                        'FunctionTolerance', 1e-8, ...
                        ... 'PlotFcn', @gaplotbestf, ...
                        'Display', 'diagnose', ...
                        'CrossoverFcn', 'crossoverlaplace', ...
                        'MutationFcn', 'mutationpower', ...
                        'SelectionFcn', 'selectiontournament', ...
                        'UseParallel', true ...
                        );

    rng("shuffle", "twister");

    xbests = containers.Map('KeyType', 'int32', 'ValueType', 'any');
    fbests = containers.Map('KeyType', 'int32', 'ValueType', 'any');

    if (single && ~isempty(lb)) || isempty(lb)
        if ~isempty(lb)
            [xbest, fbest, ~] = ga( ...
                @(x)Objective(x, order, deals_variants_all, check_ub), ...
                length(lb), ...
                [], [], [], [], ...
                lb, ub, ...
                @(x)Constraints(x, max_budget, order, deals_variants_all, check_ub, BudgetFunc), ...
                1:length(lb), opts_ga);
        else
            disp('No variables to optimize')
            xbest = 0;
            fbest = 0;
        end
        k = 1;
        order_keys = order.keys;
        values = order.values;
        total_budget = 0;
        for i = 1:length(values)
            if check_ub(i)
                deal_vars = deals_variants_all(k);
                order(i) = deal_vars(xbest(k));
                k = k + 1;
            end
            deal = order(order_keys{i});
            deal_v = deal.values;
            for j = 1:length(deal_v)
                item = deal_v{j};
                total_budget = total_budget + BudgetFunc(item, 0, memoDSBD);
                if isempty(lb)
                    fbest = fbest - Eff(item, memoDSBD);
                end
            end
        end
        xbests(max_budget) = xbest;
        fbests(max_budget) = -fbest;
    else
        min_profit = 0;
        budget_range = min_budget:step:max_budget;
        if budget_range(end) ~= max_budget
            budget_range = [budget_range, max_budget];
        end
        budget_range = unique(budget_range);
        for idx = 1:length(budget_range)
            i = budget_range(idx);
            [xbest, fbest, ~] = ga( ...
                @(x)Objective(x, order, deals_variants_all, check_ub), ...
                length(lb), ...
                [], [], [], [], ...
                lb, ub, ...
                @(x)Constraints(x, i, order, deals_variants_all, check_ub, BudgetFunc), ...
                1:length(lb), opts_ga);
            k = 1;
            order_keys = order.keys;
            total_budget = 0;
            for j = 1:length(order_keys)
                if check_ub(j)
                    deal_vars = deals_variants_all(k);
                    order(j) = deal_vars(xbest(k));
                    k = k + 1;
                end
                deal = order(order_keys{j});
                deal_v = deal.values;
                for h = 1:length(deal_v)
                    item = deal_v{h};
                    if i == min_budget
                        min_profit = min_profit + Eff(item, memoDSBD);
                    end
                    total_budget = total_budget + BudgetFunc(item, 0, memoDSBD);
                end
            end

            if length(fbests) < 1
                fbests(total_budget) = -1;
            end
            keys = fbests.keys;
            last = keys{length(keys)};
            if -fbest > fbests(last)
                xbests(total_budget) = xbest;
                fbests(total_budget) = -fbest;
            end
        end
    end
    
    xbests = MapToJson(xbests);
    fbests = MapToJson(fbests);
    order_json = MapToJson(order);
    deals_variants_all_json = MapToJson(deals_variants_all);

    disp('End GA');
end