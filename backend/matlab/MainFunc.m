function [xbest, fbest, total_budget, deals_variants_all, check_ub, order] = ...
    MainFunc(budget, budget_credit, order_json, lb, ub, check_ub, deals_variants_all, ...,
    host, port, pop_multiplier, max_gen_multiplier, max_stall_gen_multiplier)

    connect_string = '';
    if ~isempty(host) && ~isempty(port)
        connect_string = strcat('http://', host, ':', num2str(port), '/ga_info');
    end
    if nargin < 10 || pop_multiplier < 1
        pop_multiplier = 4;
    end
    if nargin < 11 || max_gen_multiplier < 1
        max_gen_multiplier = 20;
    end
    if nargin < 12 || max_stall_gen_multiplier < 1
        max_stall_gen_multiplier = 3;
    end

    disp('Begin GA')
    
    if ischar(order_json) || isstring(order_json)
        order = OrderToMap(order_json);
    else
        order = order_json;
    end

    BudgetFunc = @ItemBudgetOverCredit;
    if ~budget_credit
        BudgetFunc = @ItemBudget;
    end

    memoDSBD = memoize(@DealSumByDeal);

    pop_size = max(50, length(lb) * pop_multiplier);
    max_generations = max(100, length(lb) * max_gen_multiplier);
    max_stall_generations = max(50, length(lb) * max_stall_gen_multiplier);

    opts_ga = optimoptions(@ga, ...
                        'MaxGenerations', max_generations, ...
                        'MaxStallGenerations', max_stall_generations, ...
                        'PopulationSize', pop_size, ...
                        'CreationFcn', 'gacreationlinearfeasible', ...
                        'FunctionTolerance', 1e-8, ...
                        ... 'PlotFcn', @gaplotbestf, ...
                        'OutputFcn', @(options, state, flag)OutputApiFunc(options, state, flag, connect_string), ...
                        'Display', 'diagnose', ...
                        'CrossoverFcn', 'crossoverlaplace', ...
                        'MutationFcn', 'mutationpower', ...
                        'SelectionFcn', 'selectiontournament', ...
                        'UseParallel', true ...
                        );

    rng("shuffle", "twister");

    if ~isempty(lb)
        [xbest, fbest, ~] = ga( ...
            @(x)Objective(x, order, deals_variants_all, check_ub), ...
            length(lb), ...
            [], [], [], [], ...
            lb, ub, ...
            @(x)Constraints(x, budget, order, deals_variants_all, check_ub, BudgetFunc), ...
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

    disp('End GA');
end