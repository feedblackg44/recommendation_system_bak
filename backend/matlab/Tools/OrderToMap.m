function order = OrderToMap(order_json)
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
end