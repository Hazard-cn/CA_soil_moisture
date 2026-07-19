function [exposure_days,exposure_percentage] = CalExposure(phase_data, threshold)
%  [exposure_days,exposure_percentage] = CalExposure(phase_data, threshold)
    [m,n]=size(phase_data);
    length_of_gshours = m*n;
    exposure_data = phase_data(phase_data>=threshold);
    exposure_hours = length(exposure_data);
    exposure_days = exposure_hours/24;
    exposure_percentage = exposure_hours/length_of_gshours;
end
