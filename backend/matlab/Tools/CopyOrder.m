function order_copy = CopyOrder(order)
keys = order.keys;
values = order.values;

order_copy = containers.Map('KeyType', 'double', 'ValueType', 'any');
for i = 1:length(keys)
    deal = values{i};
    order_copy(keys{i}) = CopyDeal(deal);
end
end
