function budget = ItemBudgetOverCredit(item, moq, memoBSBD)
budget = ItemBudget(item, moq, memoBSBD);
dfs = DaysForSale(item);
credit_terms = item('CreditTerms');
budget = max(0, budget / dfs * (dfs - credit_terms));
end