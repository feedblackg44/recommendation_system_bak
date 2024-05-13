function variants = GetAllDealVariants(deal)
    all_moqs = ValidMOQs(deal);
    moqs_valid = all_moqs(all_moqs >= MinMOQByDeal(deal));

    variants = containers.Map('KeyType', 'double', 'ValueType', 'any');
    variants_moqs = containers.Map('KeyType', 'int32', 'ValueType', 'any');
    variants_moqs(DealSumByDeal(deal)) = deal;
    for i = 1:length(moqs_valid)
        moq = moqs_valid(i);
        deal_copy = CopyDeal(deal);
        GetDealToMOQ(deal_copy, moq)
        variants_moqs(DealSumByDeal(deal_copy)) = deal_copy;
    end
    keys = variants_moqs.keys;
    for i = 1:length(keys)
        variants(i) = variants_moqs(keys{i});
    end
end