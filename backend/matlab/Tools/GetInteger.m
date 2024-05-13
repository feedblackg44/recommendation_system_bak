function [num] = GetInteger(dlgtitle, prompt)
result = '';
dims = [1 50];

while isnan(str2double(result)) || mod(str2double(result), 1) ~= 0
    result = inputdlg(prompt, dlgtitle, dims);
    if isempty(result)
        error("Exit.");
    end
end

num = str2num(result{1});
end