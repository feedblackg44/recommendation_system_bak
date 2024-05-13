function output = ImportDataSelf(workbookFile, sheetName, dataLines)
%% Input handling

% If no sheet is specified, read first sheet
if nargin == 1 || isempty(sheetName)
    sheetName = 1;
end

% If row start and end points are not specified, define defaults
if nargin <= 2
    dataLines = [2, Inf];
end

%% Set up the Import Options and import the data
opts = spreadsheetImportOptions("NumVariables", 13);

% Specify sheet and range
opts.Sheet = sheetName;
opts.DataRange = dataLines(1, :);

% Specify column names and types
opts.VariableNames = ["DealID", "ItemNo", "ItemName", "ItemSize", "MinimumOrderQuantity", "PurchasePrice", "SalePrice", "Profit", "AverageDailySales", "Inventory", "SystemSuggestedQuantity", "SystemCoverageDays", "CreditTerms"];
opts.VariableTypes = ["string", "string", "string", "string", "double", "double", "double", "double", "double", "double", "double", "double", "double"];

% Specify variable properties
opts = setvaropts(opts, ["DealID", "ItemNo", "ItemName", "ItemSize"], "WhitespaceRule", "preserve");
opts = setvaropts(opts, ["DealID", "ItemNo", "ItemName", "ItemSize"], "EmptyFieldRule", "auto");

% Import the data
output = readtable(workbookFile, opts, "UseExcel", false);

for idx = 2:size(dataLines, 1)
    opts.DataRange = dataLines(idx, :);
    tb = readtable(workbookFile, opts, "UseExcel", false);
    output = [output; tb]; %#ok<AGROW>
end

end