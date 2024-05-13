function moq = CurrentMOQ(item, moq_, memoBSBD)
MOQs = item('MOQs');
moq = MOQs(1);
if moq_ < 1
    deal_sum = memoBSBD(item('Deal'));
else
    deal_sum = moq_;
end
for i = 1:length(MOQs)
    if deal_sum >= MOQs(i)
        moq = MOQs(i);
    end
end
end