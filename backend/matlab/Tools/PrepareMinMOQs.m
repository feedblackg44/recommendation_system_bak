function min_moqs = PrepareMinMOQs(order)
    min_moqs = containers.Map('KeyType', 'int32', 'ValueType', 'any');
    deals_names = order.keys;
    
    memoMMBD = memoize(@MaxMOQByDeal);
    memoMiMBD = memoize(@MinMOQByDeal);
    
    for i = 1:length(deals_names)
        deal_name = i;
        deal = order(deal_name);
        array = [memoMiMBD(deal), memoMMBD(deal)];
        if array(2) < array(1)
            array(2) = array(1);
        end
        min_moqs(deal_name) = array;
    end
end