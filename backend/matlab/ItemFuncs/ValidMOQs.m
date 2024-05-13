function new_moqs = ValidMOQs(deal)
    values = deal.values;
    moqs_arr = [];
    invalid_moqs = [];
    sum_totals = 0;
    for i = 1:length(deal.values)
        item = values{i};
        if item('AverageDailySales') > 0 && floor(item('CanBeSoldTotal'))
            sum_totals = sum_totals + floor(item('CanBeSoldTotal')) + item('AddToTotal');
        else
            sum_totals = sum_totals + item('SystemSuggestedQuantity');
        end
        
        item_sale_price = item('SalePrice');
        item_purchase_prices = item('PurchasePrices');
        item_profits = item_sale_price - item_purchase_prices;
        [item_moqs, ~] = RemoveDuplicateProfits(item('MOQs'), item_profits);

        if item('SystemSuggestedQuantity') > 0
            moqs_arr = [moqs_arr; setdiff(item_moqs', moqs_arr)];
        else
            invalid_moqs = [invalid_moqs; setdiff(item_moqs', invalid_moqs)];
        end
    end
    new_moqs = moqs_arr(moqs_arr <= sum_totals);
    temp = new_moqs;
    for i = 1:length(temp)
        moq = temp(i);
        if ~CheckMOQValidity(deal, moq)
            new_moqs = new_moqs(new_moqs ~= moq);
            if i == length(temp)
                for j = 1:length(invalid_moqs)
                    inv_moq = invalid_moqs(j);
                    if CheckMOQValidity(deal, inv_moq)
                        new_moqs = [new_moqs; inv_moq];
                    end
                end
            end
        end
    end
    if isempty(new_moqs)
        new_moqs = [MinMOQByDeal(deal)];
    end
end

function result = CheckMOQValidity(deal, moq)
    values = deal.values;
    sum_totals = 0;
    for i = 1:length(deal.values)
        item = values{i};
        if Profit(item, moq, @DealSumByDeal) > 0
            if item('AverageDailySales') > 0 && floor(item('CanBeSoldTotal'))
                sum_totals = sum_totals + floor(item('CanBeSoldTotal')) + item('AddToTotal');
            else
                sum_totals = sum_totals + item('SystemSuggestedQuantity');
            end
        end
    end
    if moq <= sum_totals
        result = true;
    else
        result = false;
    end
end

function [unique_moqs, unique_profits] = RemoveDuplicateProfits(moqs, profits)
    moq_dict = containers.Map('KeyType', 'double', 'ValueType', 'any');
    
    for i = 1:length(moqs)
        moq = moqs(i);
        profit = profits(i);
        
        if ~isKey(moq_dict, profit)
            moq_dict(profit) = {moq};
        else
            moq_dict(profit) = [moq_dict(profit), moq];
        end
    end

    unique_moqs = [];
    unique_profits = [];
    
    keys = moq_dict.keys;
    for i = 1:length(keys)
        profit = keys{i};
        moq_list = moq_dict(profit);
        
        if length(moq_list) > 1
            min_moq = min(cell2mat(moq_list));
            unique_moqs = [unique_moqs, min_moq];
            unique_profits = [unique_profits, profit];
        else
            unique_moqs = [unique_moqs, moq_list{1}];
            unique_profits = [unique_profits, profit];
        end
    end
end
