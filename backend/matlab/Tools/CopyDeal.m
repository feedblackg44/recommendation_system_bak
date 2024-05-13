function deal_copy = CopyDeal(deal)
keys = deal.keys;
values = deal.values;

deal_copy = containers.Map('KeyType', 'double', 'ValueType', 'any');
for i = 1:length(keys)
    item = values{i};
    item_k = item.keys;
    item_v = item.values;
    new_item = containers.Map();
    for j = 1:length(item_k)
        new_item(item_k{j}) = item_v{j};
    end
    new_item('Deal') = deal_copy;
    deal_copy(keys{i}) = new_item;
end
end
