function WriteOutTable(table_out, table_in, second_table, third_table, out_name)
    if exist(out_name, 'file') == 2
        delete(out_name)
    end
    writetable(table_out, out_name, 'Sheet', 'Sheet1');
    writetable(table_in, out_name, 'Sheet', 'Sheet2');
    writetable(second_table, out_name, 'Sheet', 'Sheet3');
    writetable(third_table, out_name, 'Sheet', 'Sheet4');
end