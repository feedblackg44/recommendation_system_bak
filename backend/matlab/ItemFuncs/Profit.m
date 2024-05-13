function profit = Profit(item, moq, memoBSBD)
price = PurchasePrice(item, moq, memoBSBD);
sale_price = item('SalePrice');
profit = sale_price - price;
end