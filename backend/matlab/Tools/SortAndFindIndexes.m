function [sorted_array, index_85, index_95] = SortAndFindIndexes(a, f)
    f_values = arrayfun(@(x) f(x), a);
    pairs = cell(length(a), 2);
    
    for i = 1:length(a)
        pairs{i, 1} = a(i);
        pairs{i, 2} = f_values(i);
    end

    pairs = sortrows(pairs, -2);

    total_sum = sum(f_values);
    target_85 = 0.85 * total_sum;
    target_95 = 0.95 * total_sum;

    current_sum = 0;
    index_85 = NaN;
    index_95 = NaN;

    for i = 1:length(pairs)
        current_sum = current_sum + pairs{i, 2};
        if isnan(index_85) && current_sum >= target_85
            index_85 = i;
        end
        if isnan(index_95) && current_sum >= target_95
            index_95 = i;
            break;
        end
    end

    sorted_array = pairs(:, 1);
end
