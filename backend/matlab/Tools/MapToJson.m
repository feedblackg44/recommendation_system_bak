function jsonStr = MapToJson(map)
    function structOut = MapToStruct(mapIn)
        keys = mapIn.keys;
        structOut = struct();
        for i = 1:length(keys)
            key = keys{i};
            if ischar(key) && strcmp(key, 'Deal')
                continue
            end
            value = mapIn(key);
            if ~isvarname(key)
                key = ['x' num2str(key)];
            end
            if isa(value, 'containers.Map')
                structOut.(key) = MapToStruct(value);
            else
                structOut.(key) = value;
            end
        end
    end

    structData = MapToStruct(map);
    jsonStr = jsonencode(structData);
end