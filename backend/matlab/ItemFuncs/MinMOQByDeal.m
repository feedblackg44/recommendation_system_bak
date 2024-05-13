function min_moq = MinMOQByDeal(deal)
    items_nums = deal.keys;
    min_moq = 0;
    moq = 1;
    flags = zeros(1, length(items_nums));
    for j = 1:length(items_nums)
        item = deal(items_nums{j});
        p_p = item('PurchasePrices');
        sale_price = item('SalePrice');
        MOQs = item('MOQs');
        if sale_price <= p_p(1) && item('SystemSuggestedQuantity') > 0
            flags(j) = true;
        end
    end
    if max(flags)
        for j = 1:length(items_nums)
            if flags(j)
                item = deal(items_nums{j});
                p_p = item('PurchasePrices');
                sale_price = item('SalePrice');
                MOQs = item('MOQs');
                index = 1;
                for k = 1:length(p_p)
                    if sale_price <= p_p(k)
                        index = k;
                    end
                end
                if index + 1 > length(MOQs)
                    index = index - 1;
                end
                if MOQs(index + 1) > moq
                    moq = MOQs(index + 1);
                end
            end
        end
        min_moq = moq;
    end
    min_moq = max(min_moq, DealSumByDealSQ(deal));
end
