function output = DailySales(deal)
    output = 0;
    values = deal.values;
    for i = 1:length(values)
        item = values{i};
        output = output + (item('SalePrice') * item('AverageDailySales'));
    end
end