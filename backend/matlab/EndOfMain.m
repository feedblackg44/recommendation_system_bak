function EndOfMain(max_budget, min_budget, step, single, xbests, fbests, ...
    order, check_ub, deals_variants_all, choice_func, items, ...
    max_investment_period, filename, table1, x, y, z, draw, ...
    save_all, selectedDir)

    memoDSBD = memoize(@DealSumByDeal);

    BudgetFunc = @ItemBudgetOverCredit;
    if strcmp(choice_func, 'Total')
        BudgetFunc = @ItemBudget;
    end

    if draw && ~single
        close all;
        fig = figure('Name', 'Profit | Budget', 'NumberTitle', 'off');
        set(fig, 'WindowState', 'maximized');
        set(groot, "CurrentFigure", fig);
        hold on;
        for indx = 1:length(y)
            Valign = 'bottom';
            Halign = 'right';
            Color = 'red';
            if ~rem(indx, 2)
                Valign = 'top';
                Halign = 'left';
                Color = 'blue';
            end
            plot(x(indx), y(indx), '.', 'Color', Color);
            if indx < 2 || y(indx) > y(indx - 1)
                text(x(indx), y(indx), sprintf('P: %.0f\nB: %.0f', y(indx), z(indx)), ...
                    'VerticalAlignment', Valign, ...
                    'HorizontalAlignment', Halign, ...
                    'FontSize', 9, ...
                    'Color', Color);
            end
        end
        hold off;
        xlabel('Budget');
        ylabel('Profit');
        ax = gca;
        ax.XLim = [min_budget - step * 2; max_budget + step * 2];
        ax.YAxis.Exponent = 0;
        ax.YAxis.TickLabelFormat = '%.0f';
        ax.XAxis.Exponent = 0;
        ax.XAxis.TickLabelFormat = '%.0f';
        drawnow;
    end

    keys = fbests.keys;
    for i = 1:length(keys)
        choosed_budget = keys{i};
        if length(fbests) > 1 && ~single && ~save_all
            choosed_budget = GetInteger('Choose Budget', sprintf('Choose budget to show from %d$ to %d$', min_budget, max_budget));
            if choosed_budget < min_budget
                choosed_budget = min_budget;
            end
            if choosed_budget > max_budget
                choosed_budget = max_budget;
            end
            choosed_budget = ceil(choosed_budget);
        %    remain = rem(choosed_budget, step);
        %    if remain
        %        choosed_budget = choosed_budget - remain + step;
        %    end
        end

        xbest = xbests(choosed_budget);
        fbest = fbests(choosed_budget);

        k = 1;
        values = order.values;
        for i = 1:length(values)
            if check_ub(i)
                deal_vars = deals_variants_all(k);
                order(i) = deal_vars(xbest(k));
                k = k + 1;
            end
        end

        total_budget = 0;
        values_c = order.values;
        for i = 1:length(values_c)
            deal = values_c{i};
            deal_v = deal.values;
            for j = 1:length(deal_v)
                item = deal_v{j};
                total_budget = total_budget + BudgetFunc(item, 0, memoDSBD);
            end
        end

        fprintf('\nSaving file with profit = %g and budget = %g\n', fbest, total_budget);

        if isempty(selectedDir)
            selectedDir = uigetdir('Select a Directory for save output');
        end

        [table_out, second_table, third_table] = MapToTable(order, fbest, items, ...
            max_investment_period);

        dotIndex = find(filename == '.', 1, 'last');
        part1 = filename(1:dotIndex-1);
        out_name = sprintf('%s\\%s %d days (P - %d$  B - %d$) %s', ...
            selectedDir, ...
            part1, ...
            max_investment_period, ...
            round(fbest), ...
            round(total_budget), ...
            datestr(datetime('today'), 'dd.mm.yyyy'));

        WriteOutTable(table_out, table1, second_table, third_table, strcat(out_name, '.xlsx'));

        command_after = sprintf('python .\\fill_formulas.py --excelname "%s"', ...
                strcat(out_name, '.xlsx'));
        system(command_after);

        if ~save_all
            break;
        end
    end
end