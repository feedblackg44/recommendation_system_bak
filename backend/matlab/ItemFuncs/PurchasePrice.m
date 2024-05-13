function price = PurchasePrice(item, moq, memoBSBD)
cur_moq = CurrentMOQ(item, moq, memoBSBD);
prices = item('PurchasePrices');
MOQs = item('MOQs');
price = prices(MOQs == cur_moq);
end