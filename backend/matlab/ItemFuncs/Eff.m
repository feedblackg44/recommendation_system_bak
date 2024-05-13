function eff = Eff(item, memoBSBD)
total_item_profit = ThirtyDaysProfit(item, memoBSBD);
eff = total_item_profit;
% if item('IncludedDispersion')
%     eff = eff - DaysForSale(item) * 0.1;
% end
% dfs = DaysForSale(item);
% crtrms = item('CreditTerms');
% if dfs > crtrms
%     eff = eff / dfs * (dfs - crtrms);
% end
end