function result = DealSumByDeal(deal)
result = 0;
values = deal.values;
for i = 1:length(values)
    cur_item = values{i};
    result = result + cur_item('BestSuggestedQuantity');
end
end