clear all;clc
load('yield_prediction_CA_with_F_WD.mat');
load('crop_mask_new_360_720_std.mat')% only B M S W

%% change crop and model
% p change  global for all crops
% Ipsl_cm5a_lr
%% rcp45
% prepare p change for each crop, and get the max/min change of P for RF

% barley
% Ipsl_cm5a_lr_rcp45
barley_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=barley_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-barley_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_barley_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_barley_Ipsl_cm5a_lr_rcp45_rf=min(min(barley_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_barley_Ipsl_cm5a_lr_rcp45_rf=max(max(barley_Ipsl_cm5a_lr_rcp45_prob_p_rf));


% maize
% Ipsl_cm5a_lr_rcp45
maize_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=maize_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_maize_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_maize_Ipsl_cm5a_lr_rcp45_rf=min(min(maize_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_maize_Ipsl_cm5a_lr_rcp45_rf=max(max(maize_Ipsl_cm5a_lr_rcp45_prob_p_rf));


% soybean
% Ipsl_cm5a_lr_rcp45
soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=soybean_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-soybean_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_soybean_Ipsl_cm5a_lr_rcp45_rf=min(min(soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_soybean_Ipsl_cm5a_lr_rcp45_rf=max(max(soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf));

% wheat
% Ipsl_cm5a_lr_rcp45
wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=wheat_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_wheat_Ipsl_cm5a_lr_rcp45_rf=min(min(wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_wheat_Ipsl_cm5a_lr_rcp45_rf=max(max(wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf));

% rice
% Ipsl_cm5a_lr_rcp45
rice_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=rice_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-rice_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_rice_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_rice_Ipsl_cm5a_lr_rcp45_rf=min(min(rice_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_rice_Ipsl_cm5a_lr_rcp45_rf=max(max(rice_Ipsl_cm5a_lr_rcp45_prob_p_rf));


% sorghum
% Ipsl_cm5a_lr_rcp45
sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=sorghum_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-sorghum_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sorghum_Ipsl_cm5a_lr_rcp45_rf=min(min(sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_sorghum_Ipsl_cm5a_lr_rcp45_rf=max(max(sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf));

% cotton
% Ipsl_cm5a_lr_rcp45
cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=cotton_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-cotton_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_cotton_Ipsl_cm5a_lr_rcp45_rf=min(min(cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_cotton_Ipsl_cm5a_lr_rcp45_rf=max(max(cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf));


% sunflower
% Ipsl_cm5a_lr_rcp45
sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=sunflower_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-sunflower_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sunflower_Ipsl_cm5a_lr_rcp45_rf=min(min(sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_sunflower_Ipsl_cm5a_lr_rcp45_rf=max(max(sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf));

% rcp26
% prepare p change for each crop, and get the max/min change of P for RF

% barley
% Ipsl_cm5a_lr_rcp26
barley_Ipsl_cm5a_lr_rcp26_prob_p_rf=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp26_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp26_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp26_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp26_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp26_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp26_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp26_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=barley_Ipsl_cm5a_lr_rcp26_future_prob_positive(m,n)-barley_Ipsl_cm5a_lr_rcp26_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp26_prob_p_rf=global_area_barley_Ipsl_cm5a_lr_rcp26_prob_p_rf+1;
        end
    end
end

min_p_change_barley_Ipsl_cm5a_lr_rcp26_rf=min(min(barley_Ipsl_cm5a_lr_rcp26_prob_p_rf));
max_p_change_barley_Ipsl_cm5a_lr_rcp26_rf=max(max(barley_Ipsl_cm5a_lr_rcp26_prob_p_rf));


% maize
% Ipsl_cm5a_lr_rcp26
maize_Ipsl_cm5a_lr_rcp26_prob_p_rf=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp26_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp26_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp26_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp26_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp26_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp26_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp26_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=maize_Ipsl_cm5a_lr_rcp26_future_prob_positive(m,n)-maize_Ipsl_cm5a_lr_rcp26_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp26_prob_p_rf=global_area_maize_Ipsl_cm5a_lr_rcp26_prob_p_rf+1;
        end
    end
end

min_p_change_maize_Ipsl_cm5a_lr_rcp26_rf=min(min(maize_Ipsl_cm5a_lr_rcp26_prob_p_rf));
max_p_change_maize_Ipsl_cm5a_lr_rcp26_rf=max(max(maize_Ipsl_cm5a_lr_rcp26_prob_p_rf));


% soybean
% Ipsl_cm5a_lr_rcp26
soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp26_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp26_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp26_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp26_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp26_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp26_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=soybean_Ipsl_cm5a_lr_rcp26_future_prob_positive(m,n)-soybean_Ipsl_cm5a_lr_rcp26_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf=global_area_soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf+1;
        end
    end
end

min_p_change_soybean_Ipsl_cm5a_lr_rcp26_rf=min(min(soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf));
max_p_change_soybean_Ipsl_cm5a_lr_rcp26_rf=max(max(soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf));

% wheat
% Ipsl_cm5a_lr_rcp26
wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp26_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp26_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp26_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp26_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp26_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp26_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=wheat_Ipsl_cm5a_lr_rcp26_future_prob_positive(m,n)-wheat_Ipsl_cm5a_lr_rcp26_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf=global_area_wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf+1;
        end
    end
end

min_p_change_wheat_Ipsl_cm5a_lr_rcp26_rf=min(min(wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf));
max_p_change_wheat_Ipsl_cm5a_lr_rcp26_rf=max(max(wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf));

% rice
% Ipsl_cm5a_lr_rcp26
rice_Ipsl_cm5a_lr_rcp26_prob_p_rf=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp26_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp26_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp26_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp26_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp26_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp26_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp26_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=rice_Ipsl_cm5a_lr_rcp26_future_prob_positive(m,n)-rice_Ipsl_cm5a_lr_rcp26_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp26_prob_p_rf=global_area_rice_Ipsl_cm5a_lr_rcp26_prob_p_rf+1;
        end
    end
end

min_p_change_rice_Ipsl_cm5a_lr_rcp26_rf=min(min(rice_Ipsl_cm5a_lr_rcp26_prob_p_rf));
max_p_change_rice_Ipsl_cm5a_lr_rcp26_rf=max(max(rice_Ipsl_cm5a_lr_rcp26_prob_p_rf));


% sorghum
% Ipsl_cm5a_lr_rcp26
sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp26_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp26_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp26_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp26_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp26_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp26_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=sorghum_Ipsl_cm5a_lr_rcp26_future_prob_positive(m,n)-sorghum_Ipsl_cm5a_lr_rcp26_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf=global_area_sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf+1;
        end
    end
end

min_p_change_sorghum_Ipsl_cm5a_lr_rcp26_rf=min(min(sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf));
max_p_change_sorghum_Ipsl_cm5a_lr_rcp26_rf=max(max(sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf));

% cotton
% Ipsl_cm5a_lr_rcp26
cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp26_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp26_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp26_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp26_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp26_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp26_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=cotton_Ipsl_cm5a_lr_rcp26_future_prob_positive(m,n)-cotton_Ipsl_cm5a_lr_rcp26_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf=global_area_cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf+1;
        end
    end
end

min_p_change_cotton_Ipsl_cm5a_lr_rcp26_rf=min(min(cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf));
max_p_change_cotton_Ipsl_cm5a_lr_rcp26_rf=max(max(cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf));


% sunflower
% Ipsl_cm5a_lr_rcp26
sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp26_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp26_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp26_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp26_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp26_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp26_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)=sunflower_Ipsl_cm5a_lr_rcp26_future_prob_positive(m,n)-sunflower_Ipsl_cm5a_lr_rcp26_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf=global_area_sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf+1;
        end
    end
end

min_p_change_sunflower_Ipsl_cm5a_lr_rcp26_rf=min(min(sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf));
max_p_change_sunflower_Ipsl_cm5a_lr_rcp26_rf=max(max(sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf));
% rcp60
% prepare p change for each crop, and get the max/min change of P for RF

% barley
% Ipsl_cm5a_lr_rcp60
barley_Ipsl_cm5a_lr_rcp60_prob_p_rf=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp60_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp60_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp60_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp60_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp60_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp60_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp60_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=barley_Ipsl_cm5a_lr_rcp60_future_prob_positive(m,n)-barley_Ipsl_cm5a_lr_rcp60_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp60_prob_p_rf=global_area_barley_Ipsl_cm5a_lr_rcp60_prob_p_rf+1;
        end
    end
end

min_p_change_barley_Ipsl_cm5a_lr_rcp60_rf=min(min(barley_Ipsl_cm5a_lr_rcp60_prob_p_rf));
max_p_change_barley_Ipsl_cm5a_lr_rcp60_rf=max(max(barley_Ipsl_cm5a_lr_rcp60_prob_p_rf));


% maize
% Ipsl_cm5a_lr_rcp60
maize_Ipsl_cm5a_lr_rcp60_prob_p_rf=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp60_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp60_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp60_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp60_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp60_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp60_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp60_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=maize_Ipsl_cm5a_lr_rcp60_future_prob_positive(m,n)-maize_Ipsl_cm5a_lr_rcp60_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp60_prob_p_rf=global_area_maize_Ipsl_cm5a_lr_rcp60_prob_p_rf+1;
        end
    end
end

min_p_change_maize_Ipsl_cm5a_lr_rcp60_rf=min(min(maize_Ipsl_cm5a_lr_rcp60_prob_p_rf));
max_p_change_maize_Ipsl_cm5a_lr_rcp60_rf=max(max(maize_Ipsl_cm5a_lr_rcp60_prob_p_rf));


% soybean
% Ipsl_cm5a_lr_rcp60
soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp60_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp60_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp60_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp60_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp60_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp60_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=soybean_Ipsl_cm5a_lr_rcp60_future_prob_positive(m,n)-soybean_Ipsl_cm5a_lr_rcp60_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf=global_area_soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf+1;
        end
    end
end

min_p_change_soybean_Ipsl_cm5a_lr_rcp60_rf=min(min(soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf));
max_p_change_soybean_Ipsl_cm5a_lr_rcp60_rf=max(max(soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf));

% wheat
% Ipsl_cm5a_lr_rcp60
wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp60_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp60_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp60_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp60_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp60_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp60_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=wheat_Ipsl_cm5a_lr_rcp60_future_prob_positive(m,n)-wheat_Ipsl_cm5a_lr_rcp60_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf=global_area_wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf+1;
        end
    end
end

min_p_change_wheat_Ipsl_cm5a_lr_rcp60_rf=min(min(wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf));
max_p_change_wheat_Ipsl_cm5a_lr_rcp60_rf=max(max(wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf));

% rice
% Ipsl_cm5a_lr_rcp60
rice_Ipsl_cm5a_lr_rcp60_prob_p_rf=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp60_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp60_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp60_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp60_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp60_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp60_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp60_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=rice_Ipsl_cm5a_lr_rcp60_future_prob_positive(m,n)-rice_Ipsl_cm5a_lr_rcp60_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp60_prob_p_rf=global_area_rice_Ipsl_cm5a_lr_rcp60_prob_p_rf+1;
        end
    end
end

min_p_change_rice_Ipsl_cm5a_lr_rcp60_rf=min(min(rice_Ipsl_cm5a_lr_rcp60_prob_p_rf));
max_p_change_rice_Ipsl_cm5a_lr_rcp60_rf=max(max(rice_Ipsl_cm5a_lr_rcp60_prob_p_rf));


% sorghum
% Ipsl_cm5a_lr_rcp60
sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp60_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp60_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp60_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp60_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp60_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp60_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=sorghum_Ipsl_cm5a_lr_rcp60_future_prob_positive(m,n)-sorghum_Ipsl_cm5a_lr_rcp60_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf=global_area_sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf+1;
        end
    end
end

min_p_change_sorghum_Ipsl_cm5a_lr_rcp60_rf=min(min(sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf));
max_p_change_sorghum_Ipsl_cm5a_lr_rcp60_rf=max(max(sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf));

% cotton
% Ipsl_cm5a_lr_rcp60
cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp60_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp60_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp60_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp60_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp60_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp60_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=cotton_Ipsl_cm5a_lr_rcp60_future_prob_positive(m,n)-cotton_Ipsl_cm5a_lr_rcp60_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf=global_area_cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf+1;
        end
    end
end

min_p_change_cotton_Ipsl_cm5a_lr_rcp60_rf=min(min(cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf));
max_p_change_cotton_Ipsl_cm5a_lr_rcp60_rf=max(max(cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf));


% sunflower
% Ipsl_cm5a_lr_rcp60
sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp60_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp60_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp60_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp60_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp60_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp60_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)=sunflower_Ipsl_cm5a_lr_rcp60_future_prob_positive(m,n)-sunflower_Ipsl_cm5a_lr_rcp60_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf=global_area_sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf+1;
        end
    end
end

min_p_change_sunflower_Ipsl_cm5a_lr_rcp60_rf=min(min(sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf));
max_p_change_sunflower_Ipsl_cm5a_lr_rcp60_rf=max(max(sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf));
% rcp85
% prepare p change for each crop, and get the max/min change of P for RF

% barley
% Ipsl_cm5a_lr_rcp85
barley_Ipsl_cm5a_lr_rcp85_prob_p_rf=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp85_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp85_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp85_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp85_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp85_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp85_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp85_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=barley_Ipsl_cm5a_lr_rcp85_future_prob_positive(m,n)-barley_Ipsl_cm5a_lr_rcp85_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp85_prob_p_rf=global_area_barley_Ipsl_cm5a_lr_rcp85_prob_p_rf+1;
        end
    end
end

min_p_change_barley_Ipsl_cm5a_lr_rcp85_rf=min(min(barley_Ipsl_cm5a_lr_rcp85_prob_p_rf));
max_p_change_barley_Ipsl_cm5a_lr_rcp85_rf=max(max(barley_Ipsl_cm5a_lr_rcp85_prob_p_rf));


% maize
% Ipsl_cm5a_lr_rcp85
maize_Ipsl_cm5a_lr_rcp85_prob_p_rf=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp85_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp85_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp85_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp85_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp85_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp85_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp85_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=maize_Ipsl_cm5a_lr_rcp85_future_prob_positive(m,n)-maize_Ipsl_cm5a_lr_rcp85_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp85_prob_p_rf=global_area_maize_Ipsl_cm5a_lr_rcp85_prob_p_rf+1;
        end
    end
end

min_p_change_maize_Ipsl_cm5a_lr_rcp85_rf=min(min(maize_Ipsl_cm5a_lr_rcp85_prob_p_rf));
max_p_change_maize_Ipsl_cm5a_lr_rcp85_rf=max(max(maize_Ipsl_cm5a_lr_rcp85_prob_p_rf));


% soybean
% Ipsl_cm5a_lr_rcp85
soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp85_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp85_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp85_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp85_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp85_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp85_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=soybean_Ipsl_cm5a_lr_rcp85_future_prob_positive(m,n)-soybean_Ipsl_cm5a_lr_rcp85_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf=global_area_soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf+1;
        end
    end
end

min_p_change_soybean_Ipsl_cm5a_lr_rcp85_rf=min(min(soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf));
max_p_change_soybean_Ipsl_cm5a_lr_rcp85_rf=max(max(soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf));

% wheat
% Ipsl_cm5a_lr_rcp85
wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp85_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp85_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp85_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp85_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp85_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp85_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=wheat_Ipsl_cm5a_lr_rcp85_future_prob_positive(m,n)-wheat_Ipsl_cm5a_lr_rcp85_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf=global_area_wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf+1;
        end
    end
end

min_p_change_wheat_Ipsl_cm5a_lr_rcp85_rf=min(min(wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf));
max_p_change_wheat_Ipsl_cm5a_lr_rcp85_rf=max(max(wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf));

% rice
% Ipsl_cm5a_lr_rcp85
rice_Ipsl_cm5a_lr_rcp85_prob_p_rf=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp85_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp85_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp85_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp85_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp85_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp85_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp85_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=rice_Ipsl_cm5a_lr_rcp85_future_prob_positive(m,n)-rice_Ipsl_cm5a_lr_rcp85_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp85_prob_p_rf=global_area_rice_Ipsl_cm5a_lr_rcp85_prob_p_rf+1;
        end
    end
end

min_p_change_rice_Ipsl_cm5a_lr_rcp85_rf=min(min(rice_Ipsl_cm5a_lr_rcp85_prob_p_rf));
max_p_change_rice_Ipsl_cm5a_lr_rcp85_rf=max(max(rice_Ipsl_cm5a_lr_rcp85_prob_p_rf));


% sorghum
% Ipsl_cm5a_lr_rcp85
sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp85_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp85_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp85_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp85_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp85_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp85_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=sorghum_Ipsl_cm5a_lr_rcp85_future_prob_positive(m,n)-sorghum_Ipsl_cm5a_lr_rcp85_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf=global_area_sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf+1;
        end
    end
end

min_p_change_sorghum_Ipsl_cm5a_lr_rcp85_rf=min(min(sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf));
max_p_change_sorghum_Ipsl_cm5a_lr_rcp85_rf=max(max(sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf));

% cotton
% Ipsl_cm5a_lr_rcp85
cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp85_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp85_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp85_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp85_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp85_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp85_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=cotton_Ipsl_cm5a_lr_rcp85_future_prob_positive(m,n)-cotton_Ipsl_cm5a_lr_rcp85_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf=global_area_cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf+1;
        end
    end
end

min_p_change_cotton_Ipsl_cm5a_lr_rcp85_rf=min(min(cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf));
max_p_change_cotton_Ipsl_cm5a_lr_rcp85_rf=max(max(cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf));


% sunflower
% Ipsl_cm5a_lr_rcp85
sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp85_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp85_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp85_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp85_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp85_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp85_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)=sunflower_Ipsl_cm5a_lr_rcp85_future_prob_positive(m,n)-sunflower_Ipsl_cm5a_lr_rcp85_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf=global_area_sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf+1;
        end
    end
end

min_p_change_sunflower_Ipsl_cm5a_lr_rcp85_rf=min(min(sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf));
max_p_change_sunflower_Ipsl_cm5a_lr_rcp85_rf=max(max(sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf));

%% Ipsl_cm5a_lr
% rcp45
% prepare p change for each crop, and get the max/min change of P for RF

% barley
% Ipsl_cm5a_lr_rcp45
barley_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=barley_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-barley_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_barley_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_barley_Ipsl_cm5a_lr_rcp45_rf=min(min(barley_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_barley_Ipsl_cm5a_lr_rcp45_rf=max(max(barley_Ipsl_cm5a_lr_rcp45_prob_p_rf));


% maize
% Ipsl_cm5a_lr_rcp45
maize_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=maize_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_maize_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_maize_Ipsl_cm5a_lr_rcp45_rf=min(min(maize_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_maize_Ipsl_cm5a_lr_rcp45_rf=max(max(maize_Ipsl_cm5a_lr_rcp45_prob_p_rf));


% soybean
% Ipsl_cm5a_lr_rcp45
soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=soybean_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-soybean_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_soybean_Ipsl_cm5a_lr_rcp45_rf=min(min(soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_soybean_Ipsl_cm5a_lr_rcp45_rf=max(max(soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf));

% wheat
% Ipsl_cm5a_lr_rcp45
wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=wheat_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_wheat_Ipsl_cm5a_lr_rcp45_rf=min(min(wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_wheat_Ipsl_cm5a_lr_rcp45_rf=max(max(wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf));

% rice
% Ipsl_cm5a_lr_rcp45
rice_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=rice_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-rice_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_rice_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_rice_Ipsl_cm5a_lr_rcp45_rf=min(min(rice_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_rice_Ipsl_cm5a_lr_rcp45_rf=max(max(rice_Ipsl_cm5a_lr_rcp45_prob_p_rf));


% sorghum
% Ipsl_cm5a_lr_rcp45
sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=sorghum_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-sorghum_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sorghum_Ipsl_cm5a_lr_rcp45_rf=min(min(sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_sorghum_Ipsl_cm5a_lr_rcp45_rf=max(max(sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf));

% cotton
% Ipsl_cm5a_lr_rcp45
cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=cotton_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-cotton_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_cotton_Ipsl_cm5a_lr_rcp45_rf=min(min(cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_cotton_Ipsl_cm5a_lr_rcp45_rf=max(max(cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf));


% sunflower
% Ipsl_cm5a_lr_rcp45
sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)=sunflower_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-sunflower_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf=global_area_sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sunflower_Ipsl_cm5a_lr_rcp45_rf=min(min(sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf));
max_p_change_sunflower_Ipsl_cm5a_lr_rcp45_rf=max(max(sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf));
%% Gfdl_esm2m
% rcp45
% prepare p change for each crop, and get the max/min change of P for RF

% barley
% Gfdl_esm2m_rcp45
barley_Gfdl_esm2m_rcp45_prob_p_rf=zeros(360,720);
global_area_barley_Gfdl_esm2m_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (barley_mask2(m,n)== 0 || barley_Gfdl_esm2m_rcp45_PB(m,n) == -99 || barley_Gfdl_esm2m_rcp45_Tave(m,n) == -99 || barley_Gfdl_esm2m_rcp45_Tmax(m,n) == -99 || barley_Gfdl_esm2m_rcp45_Tmin(m,n) == -99 || barley_Gfdl_esm2m_rcp45_ST_original(m,n)==0 || barley_Gfdl_esm2m_rcp45_ST_original(m,n) == 13)
            barley_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            barley_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=barley_Gfdl_esm2m_rcp45_future_prob_positive(m,n)-barley_Gfdl_esm2m_rcp45_prob_positive(m,n);
            global_area_barley_Gfdl_esm2m_rcp45_prob_p_rf=global_area_barley_Gfdl_esm2m_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_barley_Gfdl_esm2m_rcp45_rf=min(min(barley_Gfdl_esm2m_rcp45_prob_p_rf));
max_p_change_barley_Gfdl_esm2m_rcp45_rf=max(max(barley_Gfdl_esm2m_rcp45_prob_p_rf));


% maize
% Gfdl_esm2m_rcp45
maize_Gfdl_esm2m_rcp45_prob_p_rf=zeros(360,720);
global_area_maize_Gfdl_esm2m_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Gfdl_esm2m_rcp45_PB(m,n) == -99 || maize_Gfdl_esm2m_rcp45_Tave(m,n) == -99 || maize_Gfdl_esm2m_rcp45_Tmax(m,n) == -99 || maize_Gfdl_esm2m_rcp45_Tmin(m,n) == -99 || maize_Gfdl_esm2m_rcp45_ST_original(m,n)==0 || maize_Gfdl_esm2m_rcp45_ST_original(m,n) == 13)
            maize_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            maize_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=maize_Gfdl_esm2m_rcp45_future_prob_positive(m,n)-maize_Gfdl_esm2m_rcp45_prob_positive(m,n);
            global_area_maize_Gfdl_esm2m_rcp45_prob_p_rf=global_area_maize_Gfdl_esm2m_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_maize_Gfdl_esm2m_rcp45_rf=min(min(maize_Gfdl_esm2m_rcp45_prob_p_rf));
max_p_change_maize_Gfdl_esm2m_rcp45_rf=max(max(maize_Gfdl_esm2m_rcp45_prob_p_rf));


% soybean
% Gfdl_esm2m_rcp45
soybean_Gfdl_esm2m_rcp45_prob_p_rf=zeros(360,720);
global_area_soybean_Gfdl_esm2m_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (soybean_mask2(m,n)== 0 || soybean_Gfdl_esm2m_rcp45_PB(m,n) == -99 || soybean_Gfdl_esm2m_rcp45_Tave(m,n) == -99 || soybean_Gfdl_esm2m_rcp45_Tmax(m,n) == -99 || soybean_Gfdl_esm2m_rcp45_Tmin(m,n) == -99 || soybean_Gfdl_esm2m_rcp45_ST_original(m,n)==0 || soybean_Gfdl_esm2m_rcp45_ST_original(m,n) == 13)
            soybean_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            soybean_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=soybean_Gfdl_esm2m_rcp45_future_prob_positive(m,n)-soybean_Gfdl_esm2m_rcp45_prob_positive(m,n);
            global_area_soybean_Gfdl_esm2m_rcp45_prob_p_rf=global_area_soybean_Gfdl_esm2m_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_soybean_Gfdl_esm2m_rcp45_rf=min(min(soybean_Gfdl_esm2m_rcp45_prob_p_rf));
max_p_change_soybean_Gfdl_esm2m_rcp45_rf=max(max(soybean_Gfdl_esm2m_rcp45_prob_p_rf));

% wheat
% Gfdl_esm2m_rcp45
wheat_Gfdl_esm2m_rcp45_prob_p_rf=zeros(360,720);
global_area_wheat_Gfdl_esm2m_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Gfdl_esm2m_rcp45_PB(m,n) == -99 || wheat_Gfdl_esm2m_rcp45_Tave(m,n) == -99 || wheat_Gfdl_esm2m_rcp45_Tmax(m,n) == -99 || wheat_Gfdl_esm2m_rcp45_Tmin(m,n) == -99 || wheat_Gfdl_esm2m_rcp45_ST_original(m,n)==0 || wheat_Gfdl_esm2m_rcp45_ST_original(m,n) == 13)
            wheat_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            wheat_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=wheat_Gfdl_esm2m_rcp45_future_prob_positive(m,n)-wheat_Gfdl_esm2m_rcp45_prob_positive(m,n);
            global_area_wheat_Gfdl_esm2m_rcp45_prob_p_rf=global_area_wheat_Gfdl_esm2m_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_wheat_Gfdl_esm2m_rcp45_rf=min(min(wheat_Gfdl_esm2m_rcp45_prob_p_rf));
max_p_change_wheat_Gfdl_esm2m_rcp45_rf=max(max(wheat_Gfdl_esm2m_rcp45_prob_p_rf));

% rice
% Gfdl_esm2m_rcp45
rice_Gfdl_esm2m_rcp45_prob_p_rf=zeros(360,720);
global_area_rice_Gfdl_esm2m_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (rice_mask2(m,n)== 0 || rice_Gfdl_esm2m_rcp45_PB(m,n) == -99 || rice_Gfdl_esm2m_rcp45_Tave(m,n) == -99 || rice_Gfdl_esm2m_rcp45_Tmax(m,n) == -99 || rice_Gfdl_esm2m_rcp45_Tmin(m,n) == -99 || rice_Gfdl_esm2m_rcp45_ST_original(m,n)==0 || rice_Gfdl_esm2m_rcp45_ST_original(m,n) == 13)
            rice_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            rice_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=rice_Gfdl_esm2m_rcp45_future_prob_positive(m,n)-rice_Gfdl_esm2m_rcp45_prob_positive(m,n);
            global_area_rice_Gfdl_esm2m_rcp45_prob_p_rf=global_area_rice_Gfdl_esm2m_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_rice_Gfdl_esm2m_rcp45_rf=min(min(rice_Gfdl_esm2m_rcp45_prob_p_rf));
max_p_change_rice_Gfdl_esm2m_rcp45_rf=max(max(rice_Gfdl_esm2m_rcp45_prob_p_rf));


% sorghum
% Gfdl_esm2m_rcp45
sorghum_Gfdl_esm2m_rcp45_prob_p_rf=zeros(360,720);
global_area_sorghum_Gfdl_esm2m_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sorghum_mask2(m,n)== 0 || sorghum_Gfdl_esm2m_rcp45_PB(m,n) == -99 || sorghum_Gfdl_esm2m_rcp45_Tave(m,n) == -99 || sorghum_Gfdl_esm2m_rcp45_Tmax(m,n) == -99 || sorghum_Gfdl_esm2m_rcp45_Tmin(m,n) == -99 || sorghum_Gfdl_esm2m_rcp45_ST_original(m,n)==0 || sorghum_Gfdl_esm2m_rcp45_ST_original(m,n) == 13)
            sorghum_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sorghum_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=sorghum_Gfdl_esm2m_rcp45_future_prob_positive(m,n)-sorghum_Gfdl_esm2m_rcp45_prob_positive(m,n);
            global_area_sorghum_Gfdl_esm2m_rcp45_prob_p_rf=global_area_sorghum_Gfdl_esm2m_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sorghum_Gfdl_esm2m_rcp45_rf=min(min(sorghum_Gfdl_esm2m_rcp45_prob_p_rf));
max_p_change_sorghum_Gfdl_esm2m_rcp45_rf=max(max(sorghum_Gfdl_esm2m_rcp45_prob_p_rf));

% cotton
% Gfdl_esm2m_rcp45
cotton_Gfdl_esm2m_rcp45_prob_p_rf=zeros(360,720);
global_area_cotton_Gfdl_esm2m_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (cotton_mask2(m,n)== 0 || cotton_Gfdl_esm2m_rcp45_PB(m,n) == -99 || cotton_Gfdl_esm2m_rcp45_Tave(m,n) == -99 || cotton_Gfdl_esm2m_rcp45_Tmax(m,n) == -99 || cotton_Gfdl_esm2m_rcp45_Tmin(m,n) == -99 || cotton_Gfdl_esm2m_rcp45_ST_original(m,n)==0 || cotton_Gfdl_esm2m_rcp45_ST_original(m,n) == 13)
            cotton_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            cotton_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=cotton_Gfdl_esm2m_rcp45_future_prob_positive(m,n)-cotton_Gfdl_esm2m_rcp45_prob_positive(m,n);
            global_area_cotton_Gfdl_esm2m_rcp45_prob_p_rf=global_area_cotton_Gfdl_esm2m_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_cotton_Gfdl_esm2m_rcp45_rf=min(min(cotton_Gfdl_esm2m_rcp45_prob_p_rf));
max_p_change_cotton_Gfdl_esm2m_rcp45_rf=max(max(cotton_Gfdl_esm2m_rcp45_prob_p_rf));


% sunflower
% Gfdl_esm2m_rcp45
sunflower_Gfdl_esm2m_rcp45_prob_p_rf=zeros(360,720);
global_area_sunflower_Gfdl_esm2m_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sunflower_mask2(m,n)== 0 || sunflower_Gfdl_esm2m_rcp45_PB(m,n) == -99 || sunflower_Gfdl_esm2m_rcp45_Tave(m,n) == -99 || sunflower_Gfdl_esm2m_rcp45_Tmax(m,n) == -99 || sunflower_Gfdl_esm2m_rcp45_Tmin(m,n) == -99 || sunflower_Gfdl_esm2m_rcp45_ST_original(m,n)==0 || sunflower_Gfdl_esm2m_rcp45_ST_original(m,n) == 13)
            sunflower_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sunflower_Gfdl_esm2m_rcp45_prob_p_rf(m,n)=sunflower_Gfdl_esm2m_rcp45_future_prob_positive(m,n)-sunflower_Gfdl_esm2m_rcp45_prob_positive(m,n);
            global_area_sunflower_Gfdl_esm2m_rcp45_prob_p_rf=global_area_sunflower_Gfdl_esm2m_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sunflower_Gfdl_esm2m_rcp45_rf=min(min(sunflower_Gfdl_esm2m_rcp45_prob_p_rf));
max_p_change_sunflower_Gfdl_esm2m_rcp45_rf=max(max(sunflower_Gfdl_esm2m_rcp45_prob_p_rf));
%% Hadgem2_es
% rcp45
% prepare p change for each crop, and get the max/min change of P for RF

% barley
% Hadgem2_es_rcp45
barley_Hadgem2_es_rcp45_prob_p_rf=zeros(360,720);
global_area_barley_Hadgem2_es_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (barley_mask2(m,n)== 0 || barley_Hadgem2_es_rcp45_PB(m,n) == -99 || barley_Hadgem2_es_rcp45_Tave(m,n) == -99 || barley_Hadgem2_es_rcp45_Tmax(m,n) == -99 || barley_Hadgem2_es_rcp45_Tmin(m,n) == -99 || barley_Hadgem2_es_rcp45_ST_original(m,n)==0 || barley_Hadgem2_es_rcp45_ST_original(m,n) == 13)
            barley_Hadgem2_es_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            barley_Hadgem2_es_rcp45_prob_p_rf(m,n)=barley_Hadgem2_es_rcp45_future_prob_positive(m,n)-barley_Hadgem2_es_rcp45_prob_positive(m,n);
            global_area_barley_Hadgem2_es_rcp45_prob_p_rf=global_area_barley_Hadgem2_es_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_barley_Hadgem2_es_rcp45_rf=min(min(barley_Hadgem2_es_rcp45_prob_p_rf));
max_p_change_barley_Hadgem2_es_rcp45_rf=max(max(barley_Hadgem2_es_rcp45_prob_p_rf));


% maize
% Hadgem2_es_rcp45
maize_Hadgem2_es_rcp45_prob_p_rf=zeros(360,720);
global_area_maize_Hadgem2_es_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Hadgem2_es_rcp45_PB(m,n) == -99 || maize_Hadgem2_es_rcp45_Tave(m,n) == -99 || maize_Hadgem2_es_rcp45_Tmax(m,n) == -99 || maize_Hadgem2_es_rcp45_Tmin(m,n) == -99 || maize_Hadgem2_es_rcp45_ST_original(m,n)==0 || maize_Hadgem2_es_rcp45_ST_original(m,n) == 13)
            maize_Hadgem2_es_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            maize_Hadgem2_es_rcp45_prob_p_rf(m,n)=maize_Hadgem2_es_rcp45_future_prob_positive(m,n)-maize_Hadgem2_es_rcp45_prob_positive(m,n);
            global_area_maize_Hadgem2_es_rcp45_prob_p_rf=global_area_maize_Hadgem2_es_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_maize_Hadgem2_es_rcp45_rf=min(min(maize_Hadgem2_es_rcp45_prob_p_rf));
max_p_change_maize_Hadgem2_es_rcp45_rf=max(max(maize_Hadgem2_es_rcp45_prob_p_rf));


% soybean
% Hadgem2_es_rcp45
soybean_Hadgem2_es_rcp45_prob_p_rf=zeros(360,720);
global_area_soybean_Hadgem2_es_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (soybean_mask2(m,n)== 0 || soybean_Hadgem2_es_rcp45_PB(m,n) == -99 || soybean_Hadgem2_es_rcp45_Tave(m,n) == -99 || soybean_Hadgem2_es_rcp45_Tmax(m,n) == -99 || soybean_Hadgem2_es_rcp45_Tmin(m,n) == -99 || soybean_Hadgem2_es_rcp45_ST_original(m,n)==0 || soybean_Hadgem2_es_rcp45_ST_original(m,n) == 13)
            soybean_Hadgem2_es_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            soybean_Hadgem2_es_rcp45_prob_p_rf(m,n)=soybean_Hadgem2_es_rcp45_future_prob_positive(m,n)-soybean_Hadgem2_es_rcp45_prob_positive(m,n);
            global_area_soybean_Hadgem2_es_rcp45_prob_p_rf=global_area_soybean_Hadgem2_es_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_soybean_Hadgem2_es_rcp45_rf=min(min(soybean_Hadgem2_es_rcp45_prob_p_rf));
max_p_change_soybean_Hadgem2_es_rcp45_rf=max(max(soybean_Hadgem2_es_rcp45_prob_p_rf));

% wheat
% Hadgem2_es_rcp45
wheat_Hadgem2_es_rcp45_prob_p_rf=zeros(360,720);
global_area_wheat_Hadgem2_es_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Hadgem2_es_rcp45_PB(m,n) == -99 || wheat_Hadgem2_es_rcp45_Tave(m,n) == -99 || wheat_Hadgem2_es_rcp45_Tmax(m,n) == -99 || wheat_Hadgem2_es_rcp45_Tmin(m,n) == -99 || wheat_Hadgem2_es_rcp45_ST_original(m,n)==0 || wheat_Hadgem2_es_rcp45_ST_original(m,n) == 13)
            wheat_Hadgem2_es_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            wheat_Hadgem2_es_rcp45_prob_p_rf(m,n)=wheat_Hadgem2_es_rcp45_future_prob_positive(m,n)-wheat_Hadgem2_es_rcp45_prob_positive(m,n);
            global_area_wheat_Hadgem2_es_rcp45_prob_p_rf=global_area_wheat_Hadgem2_es_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_wheat_Hadgem2_es_rcp45_rf=min(min(wheat_Hadgem2_es_rcp45_prob_p_rf));
max_p_change_wheat_Hadgem2_es_rcp45_rf=max(max(wheat_Hadgem2_es_rcp45_prob_p_rf));

% rice
% Hadgem2_es_rcp45
rice_Hadgem2_es_rcp45_prob_p_rf=zeros(360,720);
global_area_rice_Hadgem2_es_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (rice_mask2(m,n)== 0 || rice_Hadgem2_es_rcp45_PB(m,n) == -99 || rice_Hadgem2_es_rcp45_Tave(m,n) == -99 || rice_Hadgem2_es_rcp45_Tmax(m,n) == -99 || rice_Hadgem2_es_rcp45_Tmin(m,n) == -99 || rice_Hadgem2_es_rcp45_ST_original(m,n)==0 || rice_Hadgem2_es_rcp45_ST_original(m,n) == 13)
            rice_Hadgem2_es_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            rice_Hadgem2_es_rcp45_prob_p_rf(m,n)=rice_Hadgem2_es_rcp45_future_prob_positive(m,n)-rice_Hadgem2_es_rcp45_prob_positive(m,n);
            global_area_rice_Hadgem2_es_rcp45_prob_p_rf=global_area_rice_Hadgem2_es_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_rice_Hadgem2_es_rcp45_rf=min(min(rice_Hadgem2_es_rcp45_prob_p_rf));
max_p_change_rice_Hadgem2_es_rcp45_rf=max(max(rice_Hadgem2_es_rcp45_prob_p_rf));


% sorghum
% Hadgem2_es_rcp45
sorghum_Hadgem2_es_rcp45_prob_p_rf=zeros(360,720);
global_area_sorghum_Hadgem2_es_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sorghum_mask2(m,n)== 0 || sorghum_Hadgem2_es_rcp45_PB(m,n) == -99 || sorghum_Hadgem2_es_rcp45_Tave(m,n) == -99 || sorghum_Hadgem2_es_rcp45_Tmax(m,n) == -99 || sorghum_Hadgem2_es_rcp45_Tmin(m,n) == -99 || sorghum_Hadgem2_es_rcp45_ST_original(m,n)==0 || sorghum_Hadgem2_es_rcp45_ST_original(m,n) == 13)
            sorghum_Hadgem2_es_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sorghum_Hadgem2_es_rcp45_prob_p_rf(m,n)=sorghum_Hadgem2_es_rcp45_future_prob_positive(m,n)-sorghum_Hadgem2_es_rcp45_prob_positive(m,n);
            global_area_sorghum_Hadgem2_es_rcp45_prob_p_rf=global_area_sorghum_Hadgem2_es_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sorghum_Hadgem2_es_rcp45_rf=min(min(sorghum_Hadgem2_es_rcp45_prob_p_rf));
max_p_change_sorghum_Hadgem2_es_rcp45_rf=max(max(sorghum_Hadgem2_es_rcp45_prob_p_rf));

% cotton
% Hadgem2_es_rcp45
cotton_Hadgem2_es_rcp45_prob_p_rf=zeros(360,720);
global_area_cotton_Hadgem2_es_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (cotton_mask2(m,n)== 0 || cotton_Hadgem2_es_rcp45_PB(m,n) == -99 || cotton_Hadgem2_es_rcp45_Tave(m,n) == -99 || cotton_Hadgem2_es_rcp45_Tmax(m,n) == -99 || cotton_Hadgem2_es_rcp45_Tmin(m,n) == -99 || cotton_Hadgem2_es_rcp45_ST_original(m,n)==0 || cotton_Hadgem2_es_rcp45_ST_original(m,n) == 13)
            cotton_Hadgem2_es_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            cotton_Hadgem2_es_rcp45_prob_p_rf(m,n)=cotton_Hadgem2_es_rcp45_future_prob_positive(m,n)-cotton_Hadgem2_es_rcp45_prob_positive(m,n);
            global_area_cotton_Hadgem2_es_rcp45_prob_p_rf=global_area_cotton_Hadgem2_es_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_cotton_Hadgem2_es_rcp45_rf=min(min(cotton_Hadgem2_es_rcp45_prob_p_rf));
max_p_change_cotton_Hadgem2_es_rcp45_rf=max(max(cotton_Hadgem2_es_rcp45_prob_p_rf));


% sunflower
% Hadgem2_es_rcp45
sunflower_Hadgem2_es_rcp45_prob_p_rf=zeros(360,720);
global_area_sunflower_Hadgem2_es_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sunflower_mask2(m,n)== 0 || sunflower_Hadgem2_es_rcp45_PB(m,n) == -99 || sunflower_Hadgem2_es_rcp45_Tave(m,n) == -99 || sunflower_Hadgem2_es_rcp45_Tmax(m,n) == -99 || sunflower_Hadgem2_es_rcp45_Tmin(m,n) == -99 || sunflower_Hadgem2_es_rcp45_ST_original(m,n)==0 || sunflower_Hadgem2_es_rcp45_ST_original(m,n) == 13)
            sunflower_Hadgem2_es_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sunflower_Hadgem2_es_rcp45_prob_p_rf(m,n)=sunflower_Hadgem2_es_rcp45_future_prob_positive(m,n)-sunflower_Hadgem2_es_rcp45_prob_positive(m,n);
            global_area_sunflower_Hadgem2_es_rcp45_prob_p_rf=global_area_sunflower_Hadgem2_es_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sunflower_Hadgem2_es_rcp45_rf=min(min(sunflower_Hadgem2_es_rcp45_prob_p_rf));
max_p_change_sunflower_Hadgem2_es_rcp45_rf=max(max(sunflower_Hadgem2_es_rcp45_prob_p_rf));
%% MIROC5
% rcp45
% prepare p change for each crop, and get the max/min change of P for RF

% barley
% MIROC5_rcp45
barley_MIROC5_rcp45_prob_p_rf=zeros(360,720);
global_area_barley_MIROC5_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (barley_mask2(m,n)== 0 || barley_MIROC5_rcp45_PB(m,n) == -99 || barley_MIROC5_rcp45_Tave(m,n) == -99 || barley_MIROC5_rcp45_Tmax(m,n) == -99 || barley_MIROC5_rcp45_Tmin(m,n) == -99 || barley_MIROC5_rcp45_ST_original(m,n)==0 || barley_MIROC5_rcp45_ST_original(m,n) == 13)
            barley_MIROC5_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            barley_MIROC5_rcp45_prob_p_rf(m,n)=barley_MIROC5_rcp45_future_prob_positive(m,n)-barley_MIROC5_rcp45_prob_positive(m,n);
            global_area_barley_MIROC5_rcp45_prob_p_rf=global_area_barley_MIROC5_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_barley_MIROC5_rcp45_rf=min(min(barley_MIROC5_rcp45_prob_p_rf));
max_p_change_barley_MIROC5_rcp45_rf=max(max(barley_MIROC5_rcp45_prob_p_rf));


% maize
% MIROC5_rcp45
maize_MIROC5_rcp45_prob_p_rf=zeros(360,720);
global_area_maize_MIROC5_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_MIROC5_rcp45_PB(m,n) == -99 || maize_MIROC5_rcp45_Tave(m,n) == -99 || maize_MIROC5_rcp45_Tmax(m,n) == -99 || maize_MIROC5_rcp45_Tmin(m,n) == -99 || maize_MIROC5_rcp45_ST_original(m,n)==0 || maize_MIROC5_rcp45_ST_original(m,n) == 13)
            maize_MIROC5_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            maize_MIROC5_rcp45_prob_p_rf(m,n)=maize_MIROC5_rcp45_future_prob_positive(m,n)-maize_MIROC5_rcp45_prob_positive(m,n);
            global_area_maize_MIROC5_rcp45_prob_p_rf=global_area_maize_MIROC5_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_maize_MIROC5_rcp45_rf=min(min(maize_MIROC5_rcp45_prob_p_rf));
max_p_change_maize_MIROC5_rcp45_rf=max(max(maize_MIROC5_rcp45_prob_p_rf));


% soybean
% MIROC5_rcp45
soybean_MIROC5_rcp45_prob_p_rf=zeros(360,720);
global_area_soybean_MIROC5_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (soybean_mask2(m,n)== 0 || soybean_MIROC5_rcp45_PB(m,n) == -99 || soybean_MIROC5_rcp45_Tave(m,n) == -99 || soybean_MIROC5_rcp45_Tmax(m,n) == -99 || soybean_MIROC5_rcp45_Tmin(m,n) == -99 || soybean_MIROC5_rcp45_ST_original(m,n)==0 || soybean_MIROC5_rcp45_ST_original(m,n) == 13)
            soybean_MIROC5_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            soybean_MIROC5_rcp45_prob_p_rf(m,n)=soybean_MIROC5_rcp45_future_prob_positive(m,n)-soybean_MIROC5_rcp45_prob_positive(m,n);
            global_area_soybean_MIROC5_rcp45_prob_p_rf=global_area_soybean_MIROC5_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_soybean_MIROC5_rcp45_rf=min(min(soybean_MIROC5_rcp45_prob_p_rf));
max_p_change_soybean_MIROC5_rcp45_rf=max(max(soybean_MIROC5_rcp45_prob_p_rf));

% wheat
% MIROC5_rcp45
wheat_MIROC5_rcp45_prob_p_rf=zeros(360,720);
global_area_wheat_MIROC5_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_MIROC5_rcp45_PB(m,n) == -99 || wheat_MIROC5_rcp45_Tave(m,n) == -99 || wheat_MIROC5_rcp45_Tmax(m,n) == -99 || wheat_MIROC5_rcp45_Tmin(m,n) == -99 || wheat_MIROC5_rcp45_ST_original(m,n)==0 || wheat_MIROC5_rcp45_ST_original(m,n) == 13)
            wheat_MIROC5_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            wheat_MIROC5_rcp45_prob_p_rf(m,n)=wheat_MIROC5_rcp45_future_prob_positive(m,n)-wheat_MIROC5_rcp45_prob_positive(m,n);
            global_area_wheat_MIROC5_rcp45_prob_p_rf=global_area_wheat_MIROC5_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_wheat_MIROC5_rcp45_rf=min(min(wheat_MIROC5_rcp45_prob_p_rf));
max_p_change_wheat_MIROC5_rcp45_rf=max(max(wheat_MIROC5_rcp45_prob_p_rf));

% rice
% MIROC5_rcp45
rice_MIROC5_rcp45_prob_p_rf=zeros(360,720);
global_area_rice_MIROC5_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (rice_mask2(m,n)== 0 || rice_MIROC5_rcp45_PB(m,n) == -99 || rice_MIROC5_rcp45_Tave(m,n) == -99 || rice_MIROC5_rcp45_Tmax(m,n) == -99 || rice_MIROC5_rcp45_Tmin(m,n) == -99 || rice_MIROC5_rcp45_ST_original(m,n)==0 || rice_MIROC5_rcp45_ST_original(m,n) == 13)
            rice_MIROC5_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            rice_MIROC5_rcp45_prob_p_rf(m,n)=rice_MIROC5_rcp45_future_prob_positive(m,n)-rice_MIROC5_rcp45_prob_positive(m,n);
            global_area_rice_MIROC5_rcp45_prob_p_rf=global_area_rice_MIROC5_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_rice_MIROC5_rcp45_rf=min(min(rice_MIROC5_rcp45_prob_p_rf));
max_p_change_rice_MIROC5_rcp45_rf=max(max(rice_MIROC5_rcp45_prob_p_rf));


% sorghum
% MIROC5_rcp45
sorghum_MIROC5_rcp45_prob_p_rf=zeros(360,720);
global_area_sorghum_MIROC5_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sorghum_mask2(m,n)== 0 || sorghum_MIROC5_rcp45_PB(m,n) == -99 || sorghum_MIROC5_rcp45_Tave(m,n) == -99 || sorghum_MIROC5_rcp45_Tmax(m,n) == -99 || sorghum_MIROC5_rcp45_Tmin(m,n) == -99 || sorghum_MIROC5_rcp45_ST_original(m,n)==0 || sorghum_MIROC5_rcp45_ST_original(m,n) == 13)
            sorghum_MIROC5_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sorghum_MIROC5_rcp45_prob_p_rf(m,n)=sorghum_MIROC5_rcp45_future_prob_positive(m,n)-sorghum_MIROC5_rcp45_prob_positive(m,n);
            global_area_sorghum_MIROC5_rcp45_prob_p_rf=global_area_sorghum_MIROC5_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sorghum_MIROC5_rcp45_rf=min(min(sorghum_MIROC5_rcp45_prob_p_rf));
max_p_change_sorghum_MIROC5_rcp45_rf=max(max(sorghum_MIROC5_rcp45_prob_p_rf));

% cotton
% MIROC5_rcp45
cotton_MIROC5_rcp45_prob_p_rf=zeros(360,720);
global_area_cotton_MIROC5_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (cotton_mask2(m,n)== 0 || cotton_MIROC5_rcp45_PB(m,n) == -99 || cotton_MIROC5_rcp45_Tave(m,n) == -99 || cotton_MIROC5_rcp45_Tmax(m,n) == -99 || cotton_MIROC5_rcp45_Tmin(m,n) == -99 || cotton_MIROC5_rcp45_ST_original(m,n)==0 || cotton_MIROC5_rcp45_ST_original(m,n) == 13)
            cotton_MIROC5_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            cotton_MIROC5_rcp45_prob_p_rf(m,n)=cotton_MIROC5_rcp45_future_prob_positive(m,n)-cotton_MIROC5_rcp45_prob_positive(m,n);
            global_area_cotton_MIROC5_rcp45_prob_p_rf=global_area_cotton_MIROC5_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_cotton_MIROC5_rcp45_rf=min(min(cotton_MIROC5_rcp45_prob_p_rf));
max_p_change_cotton_MIROC5_rcp45_rf=max(max(cotton_MIROC5_rcp45_prob_p_rf));


% sunflower
% MIROC5_rcp45
sunflower_MIROC5_rcp45_prob_p_rf=zeros(360,720);
global_area_sunflower_MIROC5_rcp45_prob_p_rf=0;
for m=1:360
    for n=1:720
        if (sunflower_mask2(m,n)== 0 || sunflower_MIROC5_rcp45_PB(m,n) == -99 || sunflower_MIROC5_rcp45_Tave(m,n) == -99 || sunflower_MIROC5_rcp45_Tmax(m,n) == -99 || sunflower_MIROC5_rcp45_Tmin(m,n) == -99 || sunflower_MIROC5_rcp45_ST_original(m,n)==0 || sunflower_MIROC5_rcp45_ST_original(m,n) == 13)
            sunflower_MIROC5_rcp45_prob_p_rf(m,n)=-0.01011;
        else
            sunflower_MIROC5_rcp45_prob_p_rf(m,n)=sunflower_MIROC5_rcp45_future_prob_positive(m,n)-sunflower_MIROC5_rcp45_prob_positive(m,n);
            global_area_sunflower_MIROC5_rcp45_prob_p_rf=global_area_sunflower_MIROC5_rcp45_prob_p_rf+1;
        end
    end
end

min_p_change_sunflower_MIROC5_rcp45_rf=min(min(sunflower_MIROC5_rcp45_prob_p_rf));
max_p_change_sunflower_MIROC5_rcp45_rf=max(max(sunflower_MIROC5_rcp45_prob_p_rf));


%% get the accumulate area change for each level of P change
%
% different rcps
%
max_p_rf_barley=max([max_p_change_barley_Ipsl_cm5a_lr_rcp26_rf,max_p_change_barley_Ipsl_cm5a_lr_rcp45_rf,max_p_change_barley_Ipsl_cm5a_lr_rcp60_rf,max_p_change_barley_Ipsl_cm5a_lr_rcp85_rf])
min_p_rf_barley=min([min_p_change_barley_Ipsl_cm5a_lr_rcp26_rf,min_p_change_barley_Ipsl_cm5a_lr_rcp45_rf,min_p_change_barley_Ipsl_cm5a_lr_rcp60_rf,min_p_change_barley_Ipsl_cm5a_lr_rcp85_rf])

max_p_rf_maize=max([max_p_change_maize_Ipsl_cm5a_lr_rcp26_rf,max_p_change_maize_Ipsl_cm5a_lr_rcp45_rf,max_p_change_maize_Ipsl_cm5a_lr_rcp60_rf,max_p_change_maize_Ipsl_cm5a_lr_rcp85_rf])
min_p_rf_maize=min([min_p_change_maize_Ipsl_cm5a_lr_rcp26_rf,min_p_change_maize_Ipsl_cm5a_lr_rcp45_rf,min_p_change_maize_Ipsl_cm5a_lr_rcp60_rf,min_p_change_maize_Ipsl_cm5a_lr_rcp85_rf])

max_p_rf_soybean=max([max_p_change_soybean_Ipsl_cm5a_lr_rcp26_rf,max_p_change_soybean_Ipsl_cm5a_lr_rcp45_rf,max_p_change_soybean_Ipsl_cm5a_lr_rcp60_rf,max_p_change_soybean_Ipsl_cm5a_lr_rcp85_rf])
min_p_rf_soybean=min([min_p_change_soybean_Ipsl_cm5a_lr_rcp26_rf,min_p_change_soybean_Ipsl_cm5a_lr_rcp45_rf,min_p_change_soybean_Ipsl_cm5a_lr_rcp60_rf,min_p_change_soybean_Ipsl_cm5a_lr_rcp85_rf])

max_p_rf_wheat=max([max_p_change_wheat_Ipsl_cm5a_lr_rcp26_rf,max_p_change_wheat_Ipsl_cm5a_lr_rcp45_rf,max_p_change_wheat_Ipsl_cm5a_lr_rcp60_rf,max_p_change_wheat_Ipsl_cm5a_lr_rcp85_rf])
min_p_rf_wheat=min([min_p_change_wheat_Ipsl_cm5a_lr_rcp26_rf,min_p_change_wheat_Ipsl_cm5a_lr_rcp45_rf,min_p_change_wheat_Ipsl_cm5a_lr_rcp60_rf,min_p_change_wheat_Ipsl_cm5a_lr_rcp85_rf])

max_p_rf_rice=max([max_p_change_rice_Ipsl_cm5a_lr_rcp26_rf,max_p_change_rice_Ipsl_cm5a_lr_rcp45_rf,max_p_change_rice_Ipsl_cm5a_lr_rcp60_rf,max_p_change_rice_Ipsl_cm5a_lr_rcp85_rf])
min_p_rf_rice=min([min_p_change_rice_Ipsl_cm5a_lr_rcp26_rf,min_p_change_rice_Ipsl_cm5a_lr_rcp45_rf,min_p_change_rice_Ipsl_cm5a_lr_rcp60_rf,min_p_change_rice_Ipsl_cm5a_lr_rcp85_rf])

max_p_rf_sorghum=max([max_p_change_sorghum_Ipsl_cm5a_lr_rcp26_rf,max_p_change_sorghum_Ipsl_cm5a_lr_rcp45_rf,max_p_change_sorghum_Ipsl_cm5a_lr_rcp60_rf,max_p_change_sorghum_Ipsl_cm5a_lr_rcp85_rf])
min_p_rf_sorghum=min([min_p_change_sorghum_Ipsl_cm5a_lr_rcp26_rf,min_p_change_sorghum_Ipsl_cm5a_lr_rcp45_rf,min_p_change_sorghum_Ipsl_cm5a_lr_rcp60_rf,min_p_change_sorghum_Ipsl_cm5a_lr_rcp85_rf])

max_p_rf_cotton=max([max_p_change_cotton_Ipsl_cm5a_lr_rcp26_rf,max_p_change_cotton_Ipsl_cm5a_lr_rcp45_rf,max_p_change_cotton_Ipsl_cm5a_lr_rcp60_rf,max_p_change_cotton_Ipsl_cm5a_lr_rcp85_rf])
min_p_rf_cotton=min([min_p_change_cotton_Ipsl_cm5a_lr_rcp26_rf,min_p_change_cotton_Ipsl_cm5a_lr_rcp45_rf,min_p_change_cotton_Ipsl_cm5a_lr_rcp60_rf,min_p_change_cotton_Ipsl_cm5a_lr_rcp85_rf])

max_p_rf_sunflower=max([max_p_change_sunflower_Ipsl_cm5a_lr_rcp26_rf,max_p_change_sunflower_Ipsl_cm5a_lr_rcp45_rf,max_p_change_sunflower_Ipsl_cm5a_lr_rcp60_rf,max_p_change_sunflower_Ipsl_cm5a_lr_rcp85_rf])
min_p_rf_sunflower=min([min_p_change_sunflower_Ipsl_cm5a_lr_rcp26_rf,min_p_change_sunflower_Ipsl_cm5a_lr_rcp45_rf,min_p_change_sunflower_Ipsl_cm5a_lr_rcp60_rf,min_p_change_sunflower_Ipsl_cm5a_lr_rcp85_rf])
%
% different models
%
max_p_rf_barley_rcp=max([max_p_change_barley_Ipsl_cm5a_lr_rcp45_rf,max_p_change_barley_Gfdl_esm2m_rcp45_rf,max_p_change_barley_MIROC5_rcp45_rf,max_p_change_barley_Hadgem2_es_rcp45_rf])
min_p_rf_barley_rcp=min([min_p_change_barley_Ipsl_cm5a_lr_rcp45_rf,min_p_change_barley_Gfdl_esm2m_rcp45_rf,min_p_change_barley_MIROC5_rcp45_rf,min_p_change_barley_Hadgem2_es_rcp45_rf])

max_p_rf_maize_rcp=max([max_p_change_maize_Ipsl_cm5a_lr_rcp45_rf,max_p_change_maize_Gfdl_esm2m_rcp45_rf,max_p_change_maize_MIROC5_rcp45_rf,max_p_change_maize_Hadgem2_es_rcp45_rf])
min_p_rf_maize_rcp=min([min_p_change_maize_Ipsl_cm5a_lr_rcp45_rf,min_p_change_maize_Gfdl_esm2m_rcp45_rf,min_p_change_maize_MIROC5_rcp45_rf,min_p_change_maize_Hadgem2_es_rcp45_rf])

max_p_rf_soybean_rcp=max([max_p_change_soybean_Ipsl_cm5a_lr_rcp45_rf,max_p_change_soybean_Gfdl_esm2m_rcp45_rf,max_p_change_soybean_MIROC5_rcp45_rf,max_p_change_soybean_Hadgem2_es_rcp45_rf])
min_p_rf_soybean_rcp=min([min_p_change_soybean_Ipsl_cm5a_lr_rcp45_rf,min_p_change_soybean_Gfdl_esm2m_rcp45_rf,min_p_change_soybean_MIROC5_rcp45_rf,min_p_change_soybean_Hadgem2_es_rcp45_rf])

max_p_rf_wheat_rcp=max([max_p_change_wheat_Ipsl_cm5a_lr_rcp45_rf,max_p_change_wheat_Gfdl_esm2m_rcp45_rf,max_p_change_wheat_MIROC5_rcp45_rf,max_p_change_wheat_Hadgem2_es_rcp45_rf])
min_p_rf_wheat_rcp=min([min_p_change_wheat_Ipsl_cm5a_lr_rcp45_rf,min_p_change_wheat_Gfdl_esm2m_rcp45_rf,min_p_change_wheat_MIROC5_rcp45_rf,min_p_change_wheat_Hadgem2_es_rcp45_rf])

max_p_rf_rice_rcp=max([max_p_change_rice_Ipsl_cm5a_lr_rcp45_rf,max_p_change_rice_Gfdl_esm2m_rcp45_rf,max_p_change_rice_MIROC5_rcp45_rf,max_p_change_rice_Hadgem2_es_rcp45_rf])
min_p_rf_rice_rcp=min([min_p_change_rice_Ipsl_cm5a_lr_rcp45_rf,min_p_change_rice_Gfdl_esm2m_rcp45_rf,min_p_change_rice_MIROC5_rcp45_rf,min_p_change_rice_Hadgem2_es_rcp45_rf])

max_p_rf_sorghum_rcp=max([max_p_change_sorghum_Ipsl_cm5a_lr_rcp45_rf,max_p_change_sorghum_Gfdl_esm2m_rcp45_rf,max_p_change_sorghum_MIROC5_rcp45_rf,max_p_change_sorghum_Hadgem2_es_rcp45_rf])
min_p_rf_sorghum_rcp=min([min_p_change_sorghum_Ipsl_cm5a_lr_rcp45_rf,min_p_change_sorghum_Gfdl_esm2m_rcp45_rf,min_p_change_sorghum_MIROC5_rcp45_rf,min_p_change_sorghum_Hadgem2_es_rcp45_rf])

max_p_rf_cotton_rcp=max([max_p_change_cotton_Ipsl_cm5a_lr_rcp45_rf,max_p_change_cotton_Gfdl_esm2m_rcp45_rf,max_p_change_cotton_MIROC5_rcp45_rf,max_p_change_cotton_Hadgem2_es_rcp45_rf])
min_p_rf_cotton_rcp=min([min_p_change_cotton_Ipsl_cm5a_lr_rcp45_rf,min_p_change_cotton_Gfdl_esm2m_rcp45_rf,min_p_change_cotton_MIROC5_rcp45_rf,min_p_change_cotton_Hadgem2_es_rcp45_rf])

max_p_rf_sunflower_rcp=max([max_p_change_sunflower_Ipsl_cm5a_lr_rcp45_rf,max_p_change_sunflower_Gfdl_esm2m_rcp45_rf,max_p_change_sunflower_MIROC5_rcp45_rf,max_p_change_sunflower_Hadgem2_es_rcp45_rf])
min_p_rf_sunflower_rcp=min([min_p_change_sunflower_Ipsl_cm5a_lr_rcp45_rf,min_p_change_sunflower_Gfdl_esm2m_rcp45_rf,min_p_change_sunflower_MIROC5_rcp45_rf,min_p_change_sunflower_Hadgem2_es_rcp45_rf])


%max_p=max([max_p_rf_barley,max_p_rf_maize,max_p_rf_soybean,max_p_rf_wheat,max_p_rf_rice,max_p_rf_sorghum,max_p_rf_cotton,max_p_rf_sunflower]);
%min_p=min([min_p_rf_barley,min_p_rf_maize,min_p_rf_soybean,min_p_rf_wheat,min_p_rf_rice,min_p_rf_sorghum,min_p_rf_cotton,min_p_rf_sunflower]);

level = 100;

%min_p_rf_barley=min_p;
%max_p_rf_barley=max_p;

%min_p_rf_maize=min_p;
%max_p_rf_maize=max_p;

%min_p_rf_soybean=min_p;
%max_p_rf_soybean=max_p;

%min_p_rf_wheat=min_p;
%max_p_rf_wheat=max_p;

%min_p_rf_rice=min_p;
%max_p_rf_rice=max_p;

%min_p_rf_sorghum=min_p;
%max_p_rf_sorghum=max_p;

%min_p_rf_cotton=min_p;
%max_p_rf_cotton=max_p;

%min_p_rf_sunflower=min_p;
%max_p_rf_sunflower=max_p;

p_change_Ipsl_cm5a_lr_rcps_rf_barley=linspace(min_p_rf_barley,max_p_rf_barley,level);
p_change_Ipsl_cm5a_lr_rcps_rf_maize=linspace(min_p_rf_maize,max_p_rf_maize,level);
p_change_Ipsl_cm5a_lr_rcps_rf_soybean=linspace(min_p_rf_soybean,max_p_rf_soybean,level);
p_change_Ipsl_cm5a_lr_rcps_rf_wheat=linspace(min_p_rf_wheat,max_p_rf_wheat,level);
p_change_Ipsl_cm5a_lr_rcps_rf_rice=linspace(min_p_rf_rice,max_p_rf_rice,level);
p_change_Ipsl_cm5a_lr_rcps_rf_sorghum=linspace(min_p_rf_sorghum,max_p_rf_sorghum,level);
p_change_Ipsl_cm5a_lr_rcps_rf_cotton=linspace(min_p_rf_cotton,max_p_rf_cotton,level);
p_change_Ipsl_cm5a_lr_rcps_rf_sunflower=linspace(min_p_rf_sunflower,max_p_rf_sunflower,level);


%p_change_Ipsl_cm5a_lr_rcps_rf_barley=linspace(min_p,max_p,level);
%p_change_Ipsl_cm5a_lr_rcps_rf_maize=linspace(min_p,max_p,level);
%p_change_Ipsl_cm5a_lr_rcps_rf_soybean=linspace(min_p,max_p,level);
%p_change_Ipsl_cm5a_lr_rcps_rf_wheat=linspace(min_p,max_p,level);
%p_change_Ipsl_cm5a_lr_rcps_rf_rice=linspace(min_p,max_p,level);
%p_change_Ipsl_cm5a_lr_rcps_rf_sorghum=linspace(min_p,max_p,level);
%p_change_Ipsl_cm5a_lr_rcps_rf_cotton=linspace(min_p,max_p,level);
%p_change_Ipsl_cm5a_lr_rcps_rf_sunflower=linspace(min_p,max_p,level);

p_change_Ipsl_cm5a_lr_models_rf_barley=linspace(min_p_rf_barley_rcp,max_p_rf_barley_rcp,level);
p_change_Ipsl_cm5a_lr_models_rf_maize=linspace(min_p_rf_maize_rcp,max_p_rf_maize_rcp,level);
p_change_Ipsl_cm5a_lr_models_rf_soybean=linspace(min_p_rf_soybean_rcp,max_p_rf_soybean_rcp,level);
p_change_Ipsl_cm5a_lr_models_rf_wheat=linspace(min_p_rf_wheat_rcp,max_p_rf_wheat_rcp,level);
p_change_Ipsl_cm5a_lr_models_rf_rice=linspace(min_p_rf_rice_rcp,max_p_rf_rice_rcp,level);
p_change_Ipsl_cm5a_lr_models_rf_sorghum=linspace(min_p_rf_sorghum_rcp,max_p_rf_sorghum_rcp,level);
p_change_Ipsl_cm5a_lr_models_rf_cotton=linspace(min_p_rf_cotton_rcp,max_p_rf_cotton_rcp,level);
p_change_Ipsl_cm5a_lr_models_rf_sunflower=linspace(min_p_rf_sunflower_rcp,max_p_rf_sunflower_rcp,level);

%% curve for accumulate area for each level of p change

%% rcp45 
% barley rf
area_barley_Ipsl_cm5a_lr_rcp45_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_barley+delta_p;
    delta_p=delta_p+(max_p_rf_barley-min_p_rf_barley)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_barley_Ipsl_cm5a_lr_rcp45_rf(1,k)=area_barley_Ipsl_cm5a_lr_rcp45_rf(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp45_rf=area_barley_Ipsl_cm5a_lr_rcp45_rf/global_area_barley_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% maize rf
area_maize_Ipsl_cm5a_lr_rcp45_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_maize+delta_p;
    delta_p=delta_p+(max_p_rf_maize-min_p_rf_maize)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_maize_Ipsl_cm5a_lr_rcp45_rf(1,k)=area_maize_Ipsl_cm5a_lr_rcp45_rf(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp45_rf=area_maize_Ipsl_cm5a_lr_rcp45_rf/global_area_maize_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% soybean rf
area_soybean_Ipsl_cm5a_lr_rcp45_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_soybean+delta_p;
    delta_p=delta_p+(max_p_rf_soybean-min_p_rf_soybean)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_soybean_Ipsl_cm5a_lr_rcp45_rf(1,k)=area_soybean_Ipsl_cm5a_lr_rcp45_rf(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp45_rf=area_soybean_Ipsl_cm5a_lr_rcp45_rf/global_area_soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% wheat rf
area_wheat_Ipsl_cm5a_lr_rcp45_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_wheat+delta_p;
    delta_p=delta_p+(max_p_rf_wheat-min_p_rf_wheat)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_wheat_Ipsl_cm5a_lr_rcp45_rf(1,k)=area_wheat_Ipsl_cm5a_lr_rcp45_rf(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp45_rf=area_wheat_Ipsl_cm5a_lr_rcp45_rf/global_area_wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% rice rf
area_rice_Ipsl_cm5a_lr_rcp45_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_rice+delta_p;
    delta_p=delta_p+(max_p_rf_rice-min_p_rf_rice)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_rice_Ipsl_cm5a_lr_rcp45_rf(1,k)=area_rice_Ipsl_cm5a_lr_rcp45_rf(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp45_rf=area_rice_Ipsl_cm5a_lr_rcp45_rf/global_area_rice_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% sorghum rf
area_sorghum_Ipsl_cm5a_lr_rcp45_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sorghum+delta_p;
    delta_p=delta_p+(max_p_rf_sorghum-min_p_rf_sorghum)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sorghum_Ipsl_cm5a_lr_rcp45_rf(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp45_rf(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp45_rf=area_sorghum_Ipsl_cm5a_lr_rcp45_rf/global_area_sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% cotton rf
area_cotton_Ipsl_cm5a_lr_rcp26_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_cotton+delta_p;
    delta_p=delta_p+(max_p_rf_cotton-min_p_rf_cotton)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)<=p_threshold)
                area_cotton_Ipsl_cm5a_lr_rcp26_rf(1,k)=area_cotton_Ipsl_cm5a_lr_rcp26_rf(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp26_rf=area_cotton_Ipsl_cm5a_lr_rcp26_rf/global_area_cotton_Ipsl_cm5a_lr_rcp26_prob_p_rf;
 
% sunflower rf
area_sunflower_Ipsl_cm5a_lr_rcp45_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sunflower+delta_p;
    delta_p=delta_p+(max_p_rf_sunflower-min_p_rf_sunflower)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sunflower_Ipsl_cm5a_lr_rcp45_rf(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp45_rf(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp45_rf=area_sunflower_Ipsl_cm5a_lr_rcp45_rf/global_area_sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf;

%% rcp26 
% barley rf
area_barley_Ipsl_cm5a_lr_rcp26_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_barley+delta_p;
    delta_p=delta_p+(max_p_rf_barley-min_p_rf_barley)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)<=p_threshold)
                area_barley_Ipsl_cm5a_lr_rcp26_rf(1,k)=area_barley_Ipsl_cm5a_lr_rcp26_rf(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp26_rf=area_barley_Ipsl_cm5a_lr_rcp26_rf/global_area_barley_Ipsl_cm5a_lr_rcp26_prob_p_rf;

% maize rf
area_maize_Ipsl_cm5a_lr_rcp26_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_maize+delta_p;
    delta_p=delta_p+(max_p_rf_maize-min_p_rf_maize)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)<=p_threshold)
                area_maize_Ipsl_cm5a_lr_rcp26_rf(1,k)=area_maize_Ipsl_cm5a_lr_rcp26_rf(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp26_rf=area_maize_Ipsl_cm5a_lr_rcp26_rf/global_area_maize_Ipsl_cm5a_lr_rcp26_prob_p_rf;

% soybean rf
area_soybean_Ipsl_cm5a_lr_rcp26_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_soybean+delta_p;
    delta_p=delta_p+(max_p_rf_soybean-min_p_rf_soybean)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)<=p_threshold)
                area_soybean_Ipsl_cm5a_lr_rcp26_rf(1,k)=area_soybean_Ipsl_cm5a_lr_rcp26_rf(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp26_rf=area_soybean_Ipsl_cm5a_lr_rcp26_rf/global_area_soybean_Ipsl_cm5a_lr_rcp26_prob_p_rf;

% wheat rf
area_wheat_Ipsl_cm5a_lr_rcp26_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_wheat+delta_p;
    delta_p=delta_p+(max_p_rf_wheat-min_p_rf_wheat)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)<=p_threshold)
                area_wheat_Ipsl_cm5a_lr_rcp26_rf(1,k)=area_wheat_Ipsl_cm5a_lr_rcp26_rf(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp26_rf=area_wheat_Ipsl_cm5a_lr_rcp26_rf/global_area_wheat_Ipsl_cm5a_lr_rcp26_prob_p_rf;

% rice rf
area_rice_Ipsl_cm5a_lr_rcp26_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_rice+delta_p;
    delta_p=delta_p+(max_p_rf_rice-min_p_rf_rice)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)<=p_threshold)
                area_rice_Ipsl_cm5a_lr_rcp26_rf(1,k)=area_rice_Ipsl_cm5a_lr_rcp26_rf(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp26_rf=area_rice_Ipsl_cm5a_lr_rcp26_rf/global_area_rice_Ipsl_cm5a_lr_rcp26_prob_p_rf;

% sorghum rf
area_sorghum_Ipsl_cm5a_lr_rcp26_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sorghum+delta_p;
    delta_p=delta_p+(max_p_rf_sorghum-min_p_rf_sorghum)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)<=p_threshold)
                area_sorghum_Ipsl_cm5a_lr_rcp26_rf(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp26_rf(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp26_rf=area_sorghum_Ipsl_cm5a_lr_rcp26_rf/global_area_sorghum_Ipsl_cm5a_lr_rcp26_prob_p_rf;

% cotton rf
area_cotton_Ipsl_cm5a_lr_rcp45_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_cotton+delta_p;
    delta_p=delta_p+(max_p_rf_cotton-min_p_rf_cotton)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_cotton_Ipsl_cm5a_lr_rcp45_rf(1,k)=area_cotton_Ipsl_cm5a_lr_rcp45_rf(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp45_rf=area_cotton_Ipsl_cm5a_lr_rcp45_rf/global_area_cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf;
 
% sunflower rf
area_sunflower_Ipsl_cm5a_lr_rcp26_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sunflower+delta_p;
    delta_p=delta_p+(max_p_rf_sunflower-min_p_rf_sunflower)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf(m,n)<=p_threshold)
                area_sunflower_Ipsl_cm5a_lr_rcp26_rf(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp26_rf(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp26_rf=area_sunflower_Ipsl_cm5a_lr_rcp26_rf/global_area_sunflower_Ipsl_cm5a_lr_rcp26_prob_p_rf;
%% rcp60 
% barley rf
area_barley_Ipsl_cm5a_lr_rcp60_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_barley+delta_p;
    delta_p=delta_p+(max_p_rf_barley-min_p_rf_barley)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)<=p_threshold)
                area_barley_Ipsl_cm5a_lr_rcp60_rf(1,k)=area_barley_Ipsl_cm5a_lr_rcp60_rf(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp60_rf=area_barley_Ipsl_cm5a_lr_rcp60_rf/global_area_barley_Ipsl_cm5a_lr_rcp60_prob_p_rf;

% maize rf
area_maize_Ipsl_cm5a_lr_rcp60_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_maize+delta_p;
    delta_p=delta_p+(max_p_rf_maize-min_p_rf_maize)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)<=p_threshold)
                area_maize_Ipsl_cm5a_lr_rcp60_rf(1,k)=area_maize_Ipsl_cm5a_lr_rcp60_rf(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp60_rf=area_maize_Ipsl_cm5a_lr_rcp60_rf/global_area_maize_Ipsl_cm5a_lr_rcp60_prob_p_rf;

% soybean rf
area_soybean_Ipsl_cm5a_lr_rcp60_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_soybean+delta_p;
    delta_p=delta_p+(max_p_rf_soybean-min_p_rf_soybean)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)<=p_threshold)
                area_soybean_Ipsl_cm5a_lr_rcp60_rf(1,k)=area_soybean_Ipsl_cm5a_lr_rcp60_rf(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp60_rf=area_soybean_Ipsl_cm5a_lr_rcp60_rf/global_area_soybean_Ipsl_cm5a_lr_rcp60_prob_p_rf;

% wheat rf
area_wheat_Ipsl_cm5a_lr_rcp60_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_wheat+delta_p;
    delta_p=delta_p+(max_p_rf_wheat-min_p_rf_wheat)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)<=p_threshold)
                area_wheat_Ipsl_cm5a_lr_rcp60_rf(1,k)=area_wheat_Ipsl_cm5a_lr_rcp60_rf(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp60_rf=area_wheat_Ipsl_cm5a_lr_rcp60_rf/global_area_wheat_Ipsl_cm5a_lr_rcp60_prob_p_rf;

% rice rf
area_rice_Ipsl_cm5a_lr_rcp60_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_rice+delta_p;
    delta_p=delta_p+(max_p_rf_rice-min_p_rf_rice)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)<=p_threshold)
                area_rice_Ipsl_cm5a_lr_rcp60_rf(1,k)=area_rice_Ipsl_cm5a_lr_rcp60_rf(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp60_rf=area_rice_Ipsl_cm5a_lr_rcp60_rf/global_area_rice_Ipsl_cm5a_lr_rcp60_prob_p_rf;

% sorghum rf
area_sorghum_Ipsl_cm5a_lr_rcp60_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sorghum+delta_p;
    delta_p=delta_p+(max_p_rf_sorghum-min_p_rf_sorghum)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)<=p_threshold)
                area_sorghum_Ipsl_cm5a_lr_rcp60_rf(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp60_rf(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp60_rf=area_sorghum_Ipsl_cm5a_lr_rcp60_rf/global_area_sorghum_Ipsl_cm5a_lr_rcp60_prob_p_rf;

% cotton rf
area_cotton_Ipsl_cm5a_lr_rcp60_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_cotton+delta_p;
    delta_p=delta_p+(max_p_rf_cotton-min_p_rf_cotton)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)<=p_threshold)
                area_cotton_Ipsl_cm5a_lr_rcp60_rf(1,k)=area_cotton_Ipsl_cm5a_lr_rcp60_rf(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp60_rf=area_cotton_Ipsl_cm5a_lr_rcp60_rf/global_area_cotton_Ipsl_cm5a_lr_rcp60_prob_p_rf;
 
% sunflower rf
area_sunflower_Ipsl_cm5a_lr_rcp60_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sunflower+delta_p;
    delta_p=delta_p+(max_p_rf_sunflower-min_p_rf_sunflower)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf(m,n)<=p_threshold)
                area_sunflower_Ipsl_cm5a_lr_rcp60_rf(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp60_rf(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp60_rf=area_sunflower_Ipsl_cm5a_lr_rcp60_rf/global_area_sunflower_Ipsl_cm5a_lr_rcp60_prob_p_rf;
%% rcp85 
% barley rf
area_barley_Ipsl_cm5a_lr_rcp85_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_barley+delta_p;
    delta_p=delta_p+(max_p_rf_barley-min_p_rf_barley)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)<=p_threshold)
                area_barley_Ipsl_cm5a_lr_rcp85_rf(1,k)=area_barley_Ipsl_cm5a_lr_rcp85_rf(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp85_rf=area_barley_Ipsl_cm5a_lr_rcp85_rf/global_area_barley_Ipsl_cm5a_lr_rcp85_prob_p_rf;

% maize rf
area_maize_Ipsl_cm5a_lr_rcp85_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_maize+delta_p;
    delta_p=delta_p+(max_p_rf_maize-min_p_rf_maize)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)<=p_threshold)
                area_maize_Ipsl_cm5a_lr_rcp85_rf(1,k)=area_maize_Ipsl_cm5a_lr_rcp85_rf(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp85_rf=area_maize_Ipsl_cm5a_lr_rcp85_rf/global_area_maize_Ipsl_cm5a_lr_rcp85_prob_p_rf;

% soybean rf
area_soybean_Ipsl_cm5a_lr_rcp85_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_soybean+delta_p;
    delta_p=delta_p+(max_p_rf_soybean-min_p_rf_soybean)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)<=p_threshold)
                area_soybean_Ipsl_cm5a_lr_rcp85_rf(1,k)=area_soybean_Ipsl_cm5a_lr_rcp85_rf(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp85_rf=area_soybean_Ipsl_cm5a_lr_rcp85_rf/global_area_soybean_Ipsl_cm5a_lr_rcp85_prob_p_rf;

% wheat rf
area_wheat_Ipsl_cm5a_lr_rcp85_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_wheat+delta_p;
    delta_p=delta_p+(max_p_rf_wheat-min_p_rf_wheat)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)<=p_threshold)
                area_wheat_Ipsl_cm5a_lr_rcp85_rf(1,k)=area_wheat_Ipsl_cm5a_lr_rcp85_rf(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp85_rf=area_wheat_Ipsl_cm5a_lr_rcp85_rf/global_area_wheat_Ipsl_cm5a_lr_rcp85_prob_p_rf;

% rice rf
area_rice_Ipsl_cm5a_lr_rcp85_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_rice+delta_p;
    delta_p=delta_p+(max_p_rf_rice-min_p_rf_rice)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)<=p_threshold)
                area_rice_Ipsl_cm5a_lr_rcp85_rf(1,k)=area_rice_Ipsl_cm5a_lr_rcp85_rf(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp85_rf=area_rice_Ipsl_cm5a_lr_rcp85_rf/global_area_rice_Ipsl_cm5a_lr_rcp85_prob_p_rf;

% sorghum rf
area_sorghum_Ipsl_cm5a_lr_rcp85_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sorghum+delta_p;
    delta_p=delta_p+(max_p_rf_sorghum-min_p_rf_sorghum)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)<=p_threshold)
                area_sorghum_Ipsl_cm5a_lr_rcp85_rf(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp85_rf(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp85_rf=area_sorghum_Ipsl_cm5a_lr_rcp85_rf/global_area_sorghum_Ipsl_cm5a_lr_rcp85_prob_p_rf;

% cotton rf
area_cotton_Ipsl_cm5a_lr_rcp85_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_cotton+delta_p;
    delta_p=delta_p+(max_p_rf_cotton-min_p_rf_cotton)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)<=p_threshold)
                area_cotton_Ipsl_cm5a_lr_rcp85_rf(1,k)=area_cotton_Ipsl_cm5a_lr_rcp85_rf(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp85_rf=area_cotton_Ipsl_cm5a_lr_rcp85_rf/global_area_cotton_Ipsl_cm5a_lr_rcp85_prob_p_rf;
 
% sunflower rf
area_sunflower_Ipsl_cm5a_lr_rcp85_rf=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sunflower+delta_p;
    delta_p=delta_p+(max_p_rf_sunflower-min_p_rf_sunflower)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf(m,n)<=p_threshold)
                area_sunflower_Ipsl_cm5a_lr_rcp85_rf(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp85_rf(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp85_rf=area_sunflower_Ipsl_cm5a_lr_rcp85_rf/global_area_sunflower_Ipsl_cm5a_lr_rcp85_prob_p_rf;

%% models
%% Ipsl_cm5a_lr
% rcp45 
% barley rf
area_barley_Ipsl_cm5a_lr_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_barley_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_barley_rcp-min_p_rf_barley_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_barley_Ipsl_cm5a_lr_rcp45_rf_model(1,k)=area_barley_Ipsl_cm5a_lr_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp45_rf_model=area_barley_Ipsl_cm5a_lr_rcp45_rf_model/global_area_barley_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% maize rf
area_maize_Ipsl_cm5a_lr_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_maize_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_maize_rcp-min_p_rf_maize_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_maize_Ipsl_cm5a_lr_rcp45_rf_model(1,k)=area_maize_Ipsl_cm5a_lr_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp45_rf_model=area_maize_Ipsl_cm5a_lr_rcp45_rf_model/global_area_maize_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% soybean rf
area_soybean_Ipsl_cm5a_lr_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_soybean_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_soybean_rcp-min_p_rf_soybean_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_soybean_Ipsl_cm5a_lr_rcp45_rf_model(1,k)=area_soybean_Ipsl_cm5a_lr_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp45_rf_model=area_soybean_Ipsl_cm5a_lr_rcp45_rf_model/global_area_soybean_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% wheat rf
area_wheat_Ipsl_cm5a_lr_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_wheat_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_wheat_rcp-min_p_rf_wheat_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_wheat_Ipsl_cm5a_lr_rcp45_rf_model(1,k)=area_wheat_Ipsl_cm5a_lr_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp45_rf_model=area_wheat_Ipsl_cm5a_lr_rcp45_rf_model/global_area_wheat_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% rice rf
area_rice_Ipsl_cm5a_lr_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_rice_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_rice_rcp-min_p_rf_rice_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_rice_Ipsl_cm5a_lr_rcp45_rf_model(1,k)=area_rice_Ipsl_cm5a_lr_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp45_rf_model=area_rice_Ipsl_cm5a_lr_rcp45_rf_model/global_area_rice_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% sorghum rf
area_sorghum_Ipsl_cm5a_lr_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sorghum_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_sorghum_rcp-min_p_rf_sorghum_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sorghum_Ipsl_cm5a_lr_rcp45_rf_model(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp45_rf_model=area_sorghum_Ipsl_cm5a_lr_rcp45_rf_model/global_area_sorghum_Ipsl_cm5a_lr_rcp45_prob_p_rf;

% cotton rf
area_cotton_Ipsl_cm5a_lr_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_cotton_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_cotton_rcp-min_p_rf_cotton_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_cotton_Ipsl_cm5a_lr_rcp45_rf_model(1,k)=area_cotton_Ipsl_cm5a_lr_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp45_rf_model=area_cotton_Ipsl_cm5a_lr_rcp45_rf_model/global_area_cotton_Ipsl_cm5a_lr_rcp45_prob_p_rf;
 
% sunflower rf
area_sunflower_Ipsl_cm5a_lr_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sunflower_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_sunflower_rcp-min_p_rf_sunflower_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sunflower_Ipsl_cm5a_lr_rcp45_rf_model(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp45_rf_model=area_sunflower_Ipsl_cm5a_lr_rcp45_rf_model/global_area_sunflower_Ipsl_cm5a_lr_rcp45_prob_p_rf;

%% Gfdl_esm2m
% rcp45 
% barley rf
area_barley_Gfdl_esm2m_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_barley_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_barley_rcp-min_p_rf_barley_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Gfdl_esm2m_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(barley_Gfdl_esm2m_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_barley_Gfdl_esm2m_rcp45_rf_model(1,k)=area_barley_Gfdl_esm2m_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_barley_Gfdl_esm2m_rcp45_rf_model=area_barley_Gfdl_esm2m_rcp45_rf_model/global_area_barley_Gfdl_esm2m_rcp45_prob_p_rf;

% maize rf
area_maize_Gfdl_esm2m_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_maize_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_maize_rcp-min_p_rf_maize_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Gfdl_esm2m_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(maize_Gfdl_esm2m_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_maize_Gfdl_esm2m_rcp45_rf_model(1,k)=area_maize_Gfdl_esm2m_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_maize_Gfdl_esm2m_rcp45_rf_model=area_maize_Gfdl_esm2m_rcp45_rf_model/global_area_maize_Gfdl_esm2m_rcp45_prob_p_rf;

% soybean rf
area_soybean_Gfdl_esm2m_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_soybean_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_soybean_rcp-min_p_rf_soybean_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Gfdl_esm2m_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(soybean_Gfdl_esm2m_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_soybean_Gfdl_esm2m_rcp45_rf_model(1,k)=area_soybean_Gfdl_esm2m_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Gfdl_esm2m_rcp45_rf_model=area_soybean_Gfdl_esm2m_rcp45_rf_model/global_area_soybean_Gfdl_esm2m_rcp45_prob_p_rf;

% wheat rf
area_wheat_Gfdl_esm2m_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_wheat_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_wheat_rcp-min_p_rf_wheat_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Gfdl_esm2m_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(wheat_Gfdl_esm2m_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_wheat_Gfdl_esm2m_rcp45_rf_model(1,k)=area_wheat_Gfdl_esm2m_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Gfdl_esm2m_rcp45_rf_model=area_wheat_Gfdl_esm2m_rcp45_rf_model/global_area_wheat_Gfdl_esm2m_rcp45_prob_p_rf;

% rice rf
area_rice_Gfdl_esm2m_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_rice_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_rice_rcp-min_p_rf_rice_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Gfdl_esm2m_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(rice_Gfdl_esm2m_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_rice_Gfdl_esm2m_rcp45_rf_model(1,k)=area_rice_Gfdl_esm2m_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_rice_Gfdl_esm2m_rcp45_rf_model=area_rice_Gfdl_esm2m_rcp45_rf_model/global_area_rice_Gfdl_esm2m_rcp45_prob_p_rf;

% sorghum rf
area_sorghum_Gfdl_esm2m_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sorghum_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_sorghum_rcp-min_p_rf_sorghum_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Gfdl_esm2m_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sorghum_Gfdl_esm2m_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sorghum_Gfdl_esm2m_rcp45_rf_model(1,k)=area_sorghum_Gfdl_esm2m_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Gfdl_esm2m_rcp45_rf_model=area_sorghum_Gfdl_esm2m_rcp45_rf_model/global_area_sorghum_Gfdl_esm2m_rcp45_prob_p_rf;

% cotton rf
area_cotton_Gfdl_esm2m_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_cotton_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_cotton_rcp-min_p_rf_cotton_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Gfdl_esm2m_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(cotton_Gfdl_esm2m_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_cotton_Gfdl_esm2m_rcp45_rf_model(1,k)=area_cotton_Gfdl_esm2m_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Gfdl_esm2m_rcp45_rf_model=area_cotton_Gfdl_esm2m_rcp45_rf_model/global_area_cotton_Gfdl_esm2m_rcp45_prob_p_rf;
 
% sunflower rf
area_sunflower_Gfdl_esm2m_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sunflower_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_sunflower_rcp-min_p_rf_sunflower_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Gfdl_esm2m_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sunflower_Gfdl_esm2m_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sunflower_Gfdl_esm2m_rcp45_rf_model(1,k)=area_sunflower_Gfdl_esm2m_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Gfdl_esm2m_rcp45_rf_model=area_sunflower_Gfdl_esm2m_rcp45_rf_model/global_area_sunflower_Gfdl_esm2m_rcp45_prob_p_rf;
%% Hadgem2_es
% rcp45 
% barley rf
area_barley_Hadgem2_es_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_barley_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_barley_rcp-min_p_rf_barley_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Hadgem2_es_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(barley_Hadgem2_es_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_barley_Hadgem2_es_rcp45_rf_model(1,k)=area_barley_Hadgem2_es_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_barley_Hadgem2_es_rcp45_rf_model=area_barley_Hadgem2_es_rcp45_rf_model/global_area_barley_Hadgem2_es_rcp45_prob_p_rf;

% maize rf
area_maize_Hadgem2_es_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_maize_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_maize_rcp-min_p_rf_maize_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Hadgem2_es_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(maize_Hadgem2_es_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_maize_Hadgem2_es_rcp45_rf_model(1,k)=area_maize_Hadgem2_es_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_maize_Hadgem2_es_rcp45_rf_model=area_maize_Hadgem2_es_rcp45_rf_model/global_area_maize_Hadgem2_es_rcp45_prob_p_rf;

% soybean rf
area_soybean_Hadgem2_es_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_soybean_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_soybean_rcp-min_p_rf_soybean_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Hadgem2_es_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(soybean_Hadgem2_es_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_soybean_Hadgem2_es_rcp45_rf_model(1,k)=area_soybean_Hadgem2_es_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Hadgem2_es_rcp45_rf_model=area_soybean_Hadgem2_es_rcp45_rf_model/global_area_soybean_Hadgem2_es_rcp45_prob_p_rf;

% wheat rf
area_wheat_Hadgem2_es_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_wheat_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_wheat_rcp-min_p_rf_wheat_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Hadgem2_es_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(wheat_Hadgem2_es_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_wheat_Hadgem2_es_rcp45_rf_model(1,k)=area_wheat_Hadgem2_es_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Hadgem2_es_rcp45_rf_model=area_wheat_Hadgem2_es_rcp45_rf_model/global_area_wheat_Hadgem2_es_rcp45_prob_p_rf;

% rice rf
area_rice_Hadgem2_es_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_rice_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_rice_rcp-min_p_rf_rice_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Hadgem2_es_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(rice_Hadgem2_es_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_rice_Hadgem2_es_rcp45_rf_model(1,k)=area_rice_Hadgem2_es_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_rice_Hadgem2_es_rcp45_rf_model=area_rice_Hadgem2_es_rcp45_rf_model/global_area_rice_Hadgem2_es_rcp45_prob_p_rf;

% sorghum rf
area_sorghum_Hadgem2_es_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sorghum_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_sorghum_rcp-min_p_rf_sorghum_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Hadgem2_es_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sorghum_Hadgem2_es_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sorghum_Hadgem2_es_rcp45_rf_model(1,k)=area_sorghum_Hadgem2_es_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Hadgem2_es_rcp45_rf_model=area_sorghum_Hadgem2_es_rcp45_rf_model/global_area_sorghum_Hadgem2_es_rcp45_prob_p_rf;

% cotton rf
area_cotton_Hadgem2_es_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_cotton_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_cotton_rcp-min_p_rf_cotton_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Hadgem2_es_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(cotton_Hadgem2_es_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_cotton_Hadgem2_es_rcp45_rf_model(1,k)=area_cotton_Hadgem2_es_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Hadgem2_es_rcp45_rf_model=area_cotton_Hadgem2_es_rcp45_rf_model/global_area_cotton_Hadgem2_es_rcp45_prob_p_rf;
 
% sunflower rf
area_sunflower_Hadgem2_es_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sunflower_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_sunflower_rcp-min_p_rf_sunflower_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Hadgem2_es_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sunflower_Hadgem2_es_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sunflower_Hadgem2_es_rcp45_rf_model(1,k)=area_sunflower_Hadgem2_es_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Hadgem2_es_rcp45_rf_model=area_sunflower_Hadgem2_es_rcp45_rf_model/global_area_sunflower_Hadgem2_es_rcp45_prob_p_rf;
%% MIROC5
% rcp45 
% barley rf
area_barley_MIROC5_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_barley_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_barley_rcp-min_p_rf_barley_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_MIROC5_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(barley_MIROC5_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_barley_MIROC5_rcp45_rf_model(1,k)=area_barley_MIROC5_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_barley_MIROC5_rcp45_rf_model=area_barley_MIROC5_rcp45_rf_model/global_area_barley_MIROC5_rcp45_prob_p_rf;

% maize rf
area_maize_MIROC5_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_maize_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_maize_rcp-min_p_rf_maize_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_MIROC5_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(maize_MIROC5_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_maize_MIROC5_rcp45_rf_model(1,k)=area_maize_MIROC5_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_maize_MIROC5_rcp45_rf_model=area_maize_MIROC5_rcp45_rf_model/global_area_maize_MIROC5_rcp45_prob_p_rf;

% soybean rf
area_soybean_MIROC5_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_soybean_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_soybean_rcp-min_p_rf_soybean_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_MIROC5_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(soybean_MIROC5_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_soybean_MIROC5_rcp45_rf_model(1,k)=area_soybean_MIROC5_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_soybean_MIROC5_rcp45_rf_model=area_soybean_MIROC5_rcp45_rf_model/global_area_soybean_MIROC5_rcp45_prob_p_rf;

% wheat rf
area_wheat_MIROC5_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_wheat_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_wheat_rcp-min_p_rf_wheat_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_MIROC5_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(wheat_MIROC5_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_wheat_MIROC5_rcp45_rf_model(1,k)=area_wheat_MIROC5_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_wheat_MIROC5_rcp45_rf_model=area_wheat_MIROC5_rcp45_rf_model/global_area_wheat_MIROC5_rcp45_prob_p_rf;

% rice rf
area_rice_MIROC5_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_rice_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_rice_rcp-min_p_rf_rice_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_MIROC5_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(rice_MIROC5_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_rice_MIROC5_rcp45_rf_model(1,k)=area_rice_MIROC5_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_rice_MIROC5_rcp45_rf_model=area_rice_MIROC5_rcp45_rf_model/global_area_rice_MIROC5_rcp45_prob_p_rf;

% sorghum rf
area_sorghum_MIROC5_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sorghum_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_sorghum_rcp-min_p_rf_sorghum_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_MIROC5_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sorghum_MIROC5_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sorghum_MIROC5_rcp45_rf_model(1,k)=area_sorghum_MIROC5_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_MIROC5_rcp45_rf_model=area_sorghum_MIROC5_rcp45_rf_model/global_area_sorghum_MIROC5_rcp45_prob_p_rf;

% cotton rf
area_cotton_MIROC5_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_cotton_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_cotton_rcp-min_p_rf_cotton_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_MIROC5_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(cotton_MIROC5_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_cotton_MIROC5_rcp45_rf_model(1,k)=area_cotton_MIROC5_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_cotton_MIROC5_rcp45_rf_model=area_cotton_MIROC5_rcp45_rf_model/global_area_cotton_MIROC5_rcp45_prob_p_rf;
 
% sunflower rf
area_sunflower_MIROC5_rcp45_rf_model=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold=min_p_rf_sunflower_rcp+delta_p;
    delta_p=delta_p+(max_p_rf_sunflower_rcp-min_p_rf_sunflower_rcp)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_MIROC5_rcp45_prob_p_rf(m,n)==-0.01011)
        
            else
                if(sunflower_MIROC5_rcp45_prob_p_rf(m,n)<=p_threshold)
                area_sunflower_MIROC5_rcp45_rf_model(1,k)=area_sunflower_MIROC5_rcp45_rf_model(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_MIROC5_rcp45_rf_model=area_sunflower_MIROC5_rcp45_rf_model/global_area_sunflower_MIROC5_rcp45_prob_p_rf;

%% plot
figure(1);clf
subplot(4,4,1)
hold on
% barley
plot(p_change_Ipsl_cm5a_lr_rcps_rf_barley,area_barley_Ipsl_cm5a_lr_rcp26_rf*100,'-','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_barley,area_barley_Ipsl_cm5a_lr_rcp45_rf*100,'-','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_barley,area_barley_Ipsl_cm5a_lr_rcp60_rf*100,'-','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_barley,area_barley_Ipsl_cm5a_lr_rcp85_rf*100,'-','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(a). barley')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,2)
% cotton
hold on
plot(p_change_Ipsl_cm5a_lr_rcps_rf_cotton,area_cotton_Ipsl_cm5a_lr_rcp26_rf*100,'-','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_cotton,area_cotton_Ipsl_cm5a_lr_rcp45_rf*100,'-','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_cotton,area_cotton_Ipsl_cm5a_lr_rcp60_rf*100,'-','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_cotton,area_cotton_Ipsl_cm5a_lr_rcp85_rf*100,'-','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(b). cotton')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,3)
hold on
% maize
plot(p_change_Ipsl_cm5a_lr_rcps_rf_maize,area_maize_Ipsl_cm5a_lr_rcp26_rf*100,'-','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_maize,area_maize_Ipsl_cm5a_lr_rcp45_rf*100,'-','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_maize,area_maize_Ipsl_cm5a_lr_rcp60_rf*100,'-','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_maize,area_maize_Ipsl_cm5a_lr_rcp85_rf*100,'-','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(c). maize')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,4)
hold on
% rice
plot(p_change_Ipsl_cm5a_lr_rcps_rf_rice,area_rice_Ipsl_cm5a_lr_rcp26_rf*100,'-','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_rice,area_rice_Ipsl_cm5a_lr_rcp45_rf*100,'-','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_rice,area_rice_Ipsl_cm5a_lr_rcp60_rf*100,'-','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_rice,area_rice_Ipsl_cm5a_lr_rcp85_rf*100,'-','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(d). rice')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,5)
hold on
% sorghum
plot(p_change_Ipsl_cm5a_lr_rcps_rf_sorghum,area_sorghum_Ipsl_cm5a_lr_rcp26_rf*100,'-','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_sorghum,area_sorghum_Ipsl_cm5a_lr_rcp45_rf*100,'-','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_sorghum,area_sorghum_Ipsl_cm5a_lr_rcp60_rf*100,'-','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_sorghum,area_sorghum_Ipsl_cm5a_lr_rcp85_rf*100,'-','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(e). sorghum')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,6)
hold on
% soybean
plot(p_change_Ipsl_cm5a_lr_rcps_rf_soybean,area_soybean_Ipsl_cm5a_lr_rcp26_rf*100,'-','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_soybean,area_soybean_Ipsl_cm5a_lr_rcp45_rf*100,'-','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_soybean,area_soybean_Ipsl_cm5a_lr_rcp60_rf*100,'-','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_soybean,area_soybean_Ipsl_cm5a_lr_rcp85_rf*100,'-','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(f). soybean')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,7)
hold on
% sunflower
plot(p_change_Ipsl_cm5a_lr_rcps_rf_sunflower,area_sunflower_Ipsl_cm5a_lr_rcp26_rf*100,'-','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_sunflower,area_sunflower_Ipsl_cm5a_lr_rcp45_rf*100,'-','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_sunflower,area_sunflower_Ipsl_cm5a_lr_rcp60_rf*100,'-','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_sunflower,area_sunflower_Ipsl_cm5a_lr_rcp85_rf*100,'-','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(g). sunflower')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,8)
hold on
% wheat
plot(p_change_Ipsl_cm5a_lr_rcps_rf_wheat,area_wheat_Ipsl_cm5a_lr_rcp26_rf*100,'-','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_wheat,area_wheat_Ipsl_cm5a_lr_rcp45_rf*100,'-','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_wheat,area_wheat_Ipsl_cm5a_lr_rcp60_rf*100,'-','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_rcps_rf_wheat,area_wheat_Ipsl_cm5a_lr_rcp85_rf*100,'-','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
xlim([-0.2,0.2])


title('(h). wheat')
ld=legend('RCP 2.6','RCP 4.5','RCP 6.0','RCP 8.5')
title(ld,'Ipsl-cm5a-lr')
set(ld,'position',[0.9115    0.7717    0.0807    0.1354])
set(gca,'fontsize',12)


subplot(4,4,9)
hold on
% barley
plot(p_change_Ipsl_cm5a_lr_models_rf_barley,area_barley_Ipsl_cm5a_lr_rcp45_rf_model*100,'--','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_barley,area_barley_Gfdl_esm2m_rcp45_rf_model*100,'--','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_barley,area_barley_Hadgem2_es_rcp45_rf_model*100,'--','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_barley,area_barley_MIROC5_rcp45_rf_model*100,'--','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(i). barley')
set(gca,'fontsize',12)
xlim([-0.2,0.2])



subplot(4,4,10)
hold on
% cotton
plot(p_change_Ipsl_cm5a_lr_models_rf_cotton,area_cotton_Ipsl_cm5a_lr_rcp45_rf_model*100,'--','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_cotton,area_cotton_Gfdl_esm2m_rcp45_rf_model*100,'--','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_cotton,area_cotton_Hadgem2_es_rcp45_rf_model*100,'--','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_cotton,area_cotton_MIROC5_rcp45_rf_model*100,'--','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(j). cotton')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,11)
hold on
% maize
plot(p_change_Ipsl_cm5a_lr_models_rf_maize,area_maize_Ipsl_cm5a_lr_rcp45_rf_model*100,'--','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_maize,area_maize_Gfdl_esm2m_rcp45_rf_model*100,'--','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_maize,area_maize_Hadgem2_es_rcp45_rf_model*100,'--','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_maize,area_maize_MIROC5_rcp45_rf_model*100,'--','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(k). maize')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,12)
hold on
% rice
plot(p_change_Ipsl_cm5a_lr_models_rf_rice,area_rice_Ipsl_cm5a_lr_rcp45_rf_model*100,'--','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_rice,area_rice_Gfdl_esm2m_rcp45_rf_model*100,'--','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_rice,area_rice_Hadgem2_es_rcp45_rf_model*100,'--','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_rice,area_rice_MIROC5_rcp45_rf_model*100,'--','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(l). rice')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,13)
hold on
% sorghum
plot(p_change_Ipsl_cm5a_lr_models_rf_sorghum,area_sorghum_Ipsl_cm5a_lr_rcp45_rf_model*100,'--','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_sorghum,area_sorghum_Gfdl_esm2m_rcp45_rf_model*100,'--','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_sorghum,area_sorghum_Hadgem2_es_rcp45_rf_model*100,'--','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_sorghum,area_sorghum_MIROC5_rcp45_rf_model*100,'--','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(m). sorghum')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,14)
hold on
% soybean
plot(p_change_Ipsl_cm5a_lr_models_rf_soybean,area_soybean_Ipsl_cm5a_lr_rcp45_rf_model*100,'--','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_soybean,area_soybean_Gfdl_esm2m_rcp45_rf_model*100,'--','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_soybean,area_soybean_Hadgem2_es_rcp45_rf_model*100,'--','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_soybean,area_soybean_MIROC5_rcp45_rf_model*100,'--','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(n). soybean')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,15)
hold on
% sunflower
plot(p_change_Ipsl_cm5a_lr_models_rf_sunflower,area_sunflower_Ipsl_cm5a_lr_rcp45_rf_model*100,'--','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_sunflower,area_sunflower_Gfdl_esm2m_rcp45_rf_model*100,'--','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_sunflower,area_sunflower_Hadgem2_es_rcp45_rf_model*100,'--','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_sunflower,area_sunflower_MIROC5_rcp45_rf_model*100,'--','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(o). sunflower')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

subplot(4,4,16)
hold on
% wheat
plot(p_change_Ipsl_cm5a_lr_models_rf_wheat,area_wheat_Ipsl_cm5a_lr_rcp45_rf_model*100,'--','color',[0,0,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_wheat,area_wheat_Gfdl_esm2m_rcp45_rf_model*100,'--','color',[0,1,0],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_wheat,area_wheat_Hadgem2_es_rcp45_rf_model*100,'--','color',[1,0,1],'linewidth',1.5)
plot(p_change_Ipsl_cm5a_lr_models_rf_wheat,area_wheat_MIROC5_rcp45_rf_model*100,'--','color',[1,0,0],'linewidth',1.5)
grid minor
xx0=linspace(0,0,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])
title('(p). wheat')
set(gca,'fontsize',12)
xlim([-0.2,0.2])

hh1=xlabel('Change of probability of yield gain in the future')
set(hh1,'position',[-0.7772  -35.5555   -1.0000])
hh2=ylabel('Accumulated fraction of global cropping area [%]')
set(hh2,'position',[-1.8527  280.3704   -1.0000])
ld1=legend('Ipsl-cm5a-lr','Gfdl-esm2m','Hadgem2-es','Miroc5')
title(ld1,'RCP 4.5')
set(ld1,'position',[0.9134    0.3358    0.0809    0.1356])
set(gca,'fontsize',12)

saveas(gca,'0_curve_accumulate_area_under_p_change_for_different_RCPs.png');
