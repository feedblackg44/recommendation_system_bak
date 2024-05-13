function result = DealSumByDealSQ(deal)
result = 0;
values = deal.values;
for i = 1:length(values)
    cur_item = values{i};
    result = result + ceil(cur_item('SystemSuggestedQuantity'));
end
end