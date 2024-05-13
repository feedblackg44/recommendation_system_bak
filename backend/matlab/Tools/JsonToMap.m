function map = JsonToMap(jsonStr)
    data = jsondecode(jsonStr);

    function mapOut = StructToMap(structIn)
        keys = fieldnames(structIn);
        if isnan(str2double(extractAfter(keys{1}, 'x')))
            mapOut = containers.Map('KeyType', 'char', 'ValueType', 'any');
        else
            mapOut = containers.Map('KeyType', 'int32', 'ValueType', 'any');
        end
        for i = 1:numel(keys)
            keyStr = keys{i};
            key = str2double(extractAfter(keyStr, 'x'));
            if isnan(key)
                key = keyStr;
            end
            value = structIn.(keyStr);
            if isstruct(value)
                mapOut(key) = StructToMap(value);
            else
                mapOut(key) = value;
            end
        end
    end

    map = StructToMap(data);
end
