clear all;clc
%% change crop and model
% p change  global for all crops
% Ipsl_cm5a_lr
% rcp45
%% prepare p change for each crop, and get the max/min change of P for RF
load('yield_prediction.mat');
load('crop_mask_new_360_720_std.mat')% only B M S W
load('Climate_zones_360_720.mat')
%% barley
% Ipsl_cm5a_lr_rcp45  global
barley_Ipsl_cm5a_lr_rcp45_p_change_global=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_global=0;
for m=1:360
    for n=1:720
        if (barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=barley_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_global=global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_global+1;
        end
    end
end

min_p_barley_Ipsl_cm5a_lr_rcp45_global=min(min(barley_Ipsl_cm5a_lr_rcp45_p_change_global));
max_p_barley_Ipsl_cm5a_lr_rcp45_global=max(max(barley_Ipsl_cm5a_lr_rcp45_p_change_global));


% Ipsl_cm5a_lr_rcp45  tropical
barley_Ipsl_cm5a_lr_rcp45_p_change_tropical=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_tropical=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>4 || Cli_zone(m,n)==0 || barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=barley_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_tropical=global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_tropical+1;
        end
    end
end

min_p_barley_Ipsl_cm5a_lr_rcp45_tropical=min(min(barley_Ipsl_cm5a_lr_rcp45_p_change_tropical));
max_p_barley_Ipsl_cm5a_lr_rcp45_tropical=max(max(barley_Ipsl_cm5a_lr_rcp45_p_change_tropical));


% Ipsl_cm5a_lr_rcp45  arid
barley_Ipsl_cm5a_lr_rcp45_p_change_arid=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_arid=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=9 || Cli_zone(m,n)<=4 || barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=barley_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_arid=global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_arid+1;
        end
    end
end

min_p_barley_Ipsl_cm5a_lr_rcp45_arid=min(min(barley_Ipsl_cm5a_lr_rcp45_p_change_arid));
max_p_barley_Ipsl_cm5a_lr_rcp45_arid=max(max(barley_Ipsl_cm5a_lr_rcp45_p_change_arid));


% Ipsl_cm5a_lr_rcp45  temperate
barley_Ipsl_cm5a_lr_rcp45_p_change_temperate=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_temperate=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=18 || Cli_zone(m,n)<=8 || barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=barley_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_temperate=global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_temperate+1;
        end
    end
end

min_p_barley_Ipsl_cm5a_lr_rcp45_temperate=min(min(barley_Ipsl_cm5a_lr_rcp45_p_change_temperate));
max_p_barley_Ipsl_cm5a_lr_rcp45_temperate=max(max(barley_Ipsl_cm5a_lr_rcp45_p_change_temperate));


% Ipsl_cm5a_lr_rcp45  continental
barley_Ipsl_cm5a_lr_rcp45_p_change_continental=zeros(360,720);
global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_continental=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=30 || Cli_zone(m,n)<=17 || barley_mask2(m,n)== 0 || barley_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || barley_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            barley_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=-0.01011;
        else
            barley_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=barley_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_continental=global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_continental+1;
        end
    end
end

min_p_barley_Ipsl_cm5a_lr_rcp45_continental=min(min(barley_Ipsl_cm5a_lr_rcp45_p_change_continental));
max_p_barley_Ipsl_cm5a_lr_rcp45_continental=max(max(barley_Ipsl_cm5a_lr_rcp45_p_change_continental));

% compare max and min p 
max_p_barley_Ipsl_cm5a_lr=max([max_p_barley_Ipsl_cm5a_lr_rcp45_global,max_p_barley_Ipsl_cm5a_lr_rcp45_tropical,max_p_barley_Ipsl_cm5a_lr_rcp45_arid,max_p_barley_Ipsl_cm5a_lr_rcp45_temperate,max_p_barley_Ipsl_cm5a_lr_rcp45_continental]);
min_p_barley_Ipsl_cm5a_lr=min([min_p_barley_Ipsl_cm5a_lr_rcp45_global,min_p_barley_Ipsl_cm5a_lr_rcp45_tropical,min_p_barley_Ipsl_cm5a_lr_rcp45_arid,min_p_barley_Ipsl_cm5a_lr_rcp45_temperate,min_p_barley_Ipsl_cm5a_lr_rcp45_continental]);

level = 100

p_barley_Ipsl_cm5a_lr_rcp45=linspace(min_p_barley_Ipsl_cm5a_lr,max_p_barley_Ipsl_cm5a_lr,level);

% area count
% barley global
area_barley_Ipsl_cm5a_lr_rcp45_global=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_barley=min_p_barley_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_barley_Ipsl_cm5a_lr-min_p_barley_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)<=p_threshold_barley)
                area_barley_Ipsl_cm5a_lr_rcp45_global(1,k)=area_barley_Ipsl_cm5a_lr_rcp45_global(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp45_global=area_barley_Ipsl_cm5a_lr_rcp45_global/global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_global;


% barley tropical
area_barley_Ipsl_cm5a_lr_rcp45_tropical=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_barley=min_p_barley_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_barley_Ipsl_cm5a_lr-min_p_barley_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)<=p_threshold_barley)
                area_barley_Ipsl_cm5a_lr_rcp45_tropical(1,k)=area_barley_Ipsl_cm5a_lr_rcp45_tropical(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp45_tropical=area_barley_Ipsl_cm5a_lr_rcp45_tropical/global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_tropical;

% barley arid
area_barley_Ipsl_cm5a_lr_rcp45_arid=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_barley=min_p_barley_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_barley_Ipsl_cm5a_lr-min_p_barley_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)<=p_threshold_barley)
                area_barley_Ipsl_cm5a_lr_rcp45_arid(1,k)=area_barley_Ipsl_cm5a_lr_rcp45_arid(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp45_arid=area_barley_Ipsl_cm5a_lr_rcp45_arid/global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_arid;

% barley temperate
area_barley_Ipsl_cm5a_lr_rcp45_temperate=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_barley=min_p_barley_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_barley_Ipsl_cm5a_lr-min_p_barley_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)<=p_threshold_barley)
                area_barley_Ipsl_cm5a_lr_rcp45_temperate(1,k)=area_barley_Ipsl_cm5a_lr_rcp45_temperate(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp45_temperate=area_barley_Ipsl_cm5a_lr_rcp45_temperate/global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_temperate;

% barley continental
area_barley_Ipsl_cm5a_lr_rcp45_continental=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_barley=min_p_barley_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_barley_Ipsl_cm5a_lr-min_p_barley_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(barley_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)==-0.01011)
        
            else
                if(barley_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)<=p_threshold_barley)
                area_barley_Ipsl_cm5a_lr_rcp45_continental(1,k)=area_barley_Ipsl_cm5a_lr_rcp45_continental(1,k)+1;
                end
            end
        end
    end
end
area_barley_Ipsl_cm5a_lr_rcp45_continental=area_barley_Ipsl_cm5a_lr_rcp45_continental/global_area_barley_Ipsl_cm5a_lr_rcp45_p_change_continental;

figure(1);clf
subplot(4,2,1)
hold on
%
plot(p_barley_Ipsl_cm5a_lr_rcp45,area_barley_Ipsl_cm5a_lr_rcp45_global*100,'-','color',[0 0 0],'linewidth',1.5);
plot(p_barley_Ipsl_cm5a_lr_rcp45,area_barley_Ipsl_cm5a_lr_rcp45_tropical*100,'--','color',[0 0 1],'linewidth',1.5);
plot(p_barley_Ipsl_cm5a_lr_rcp45,area_barley_Ipsl_cm5a_lr_rcp45_arid*100,'--','color',[1 0.5 0],'linewidth',1.5);
plot(p_barley_Ipsl_cm5a_lr_rcp45,area_barley_Ipsl_cm5a_lr_rcp45_temperate*100,'--','color',[0 1 0],'linewidth',1.5);
plot(p_barley_Ipsl_cm5a_lr_rcp45,area_barley_Ipsl_cm5a_lr_rcp45_continental*100,'--','color',[1 0 1],'linewidth',1.5);
grid minor; xlim([0.2,0.8])
xx0=linspace(0.5,0.5,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])

xx0=linspace(-1,1,100);
yy0=linspace(50,50,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])


title('(a). barley')
%legend('tropical','dry','temperate','continental')
set(gca,'fontsize',12)


%% cotton
% Ipsl_cm5a_lr_rcp45  global
cotton_Ipsl_cm5a_lr_rcp45_p_change_global=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_global=0;
for m=1:360
    for n=1:720
        if (cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=cotton_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_global=global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_global+1;
        end
    end
end

min_p_cotton_Ipsl_cm5a_lr_rcp45_global=min(min(cotton_Ipsl_cm5a_lr_rcp45_p_change_global));
max_p_cotton_Ipsl_cm5a_lr_rcp45_global=max(max(cotton_Ipsl_cm5a_lr_rcp45_p_change_global));


% Ipsl_cm5a_lr_rcp45  tropical
cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>4 || Cli_zone(m,n)==0 || cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=cotton_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical=global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical+1;
        end
    end
end

min_p_cotton_Ipsl_cm5a_lr_rcp45_tropical=min(min(cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical));
max_p_cotton_Ipsl_cm5a_lr_rcp45_tropical=max(max(cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical));


% Ipsl_cm5a_lr_rcp45  arid
cotton_Ipsl_cm5a_lr_rcp45_p_change_arid=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_arid=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=9 || Cli_zone(m,n)<=4 || cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=cotton_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_arid=global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_arid+1;
        end
    end
end

min_p_cotton_Ipsl_cm5a_lr_rcp45_arid=min(min(cotton_Ipsl_cm5a_lr_rcp45_p_change_arid));
max_p_cotton_Ipsl_cm5a_lr_rcp45_arid=max(max(cotton_Ipsl_cm5a_lr_rcp45_p_change_arid));


% Ipsl_cm5a_lr_rcp45  temperate
cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=18 || Cli_zone(m,n)<=8 || cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=cotton_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate=global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate+1;
        end
    end
end

min_p_cotton_Ipsl_cm5a_lr_rcp45_temperate=min(min(cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate));
max_p_cotton_Ipsl_cm5a_lr_rcp45_temperate=max(max(cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate));


% Ipsl_cm5a_lr_rcp45  continental
cotton_Ipsl_cm5a_lr_rcp45_p_change_continental=zeros(360,720);
global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_continental=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=30 || Cli_zone(m,n)<=17 || cotton_mask2(m,n)== 0 || cotton_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || cotton_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            cotton_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=-0.01011;
        else
            cotton_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=cotton_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_continental=global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_continental+1;
        end
    end
end

min_p_cotton_Ipsl_cm5a_lr_rcp45_continental=min(min(cotton_Ipsl_cm5a_lr_rcp45_p_change_continental));
max_p_cotton_Ipsl_cm5a_lr_rcp45_continental=max(max(cotton_Ipsl_cm5a_lr_rcp45_p_change_continental));

% compare max and min p 
max_p_cotton_Ipsl_cm5a_lr=max([max_p_cotton_Ipsl_cm5a_lr_rcp45_global,max_p_cotton_Ipsl_cm5a_lr_rcp45_tropical,max_p_cotton_Ipsl_cm5a_lr_rcp45_arid,max_p_cotton_Ipsl_cm5a_lr_rcp45_temperate,max_p_cotton_Ipsl_cm5a_lr_rcp45_continental]);
min_p_cotton_Ipsl_cm5a_lr=min([min_p_cotton_Ipsl_cm5a_lr_rcp45_global,min_p_cotton_Ipsl_cm5a_lr_rcp45_tropical,min_p_cotton_Ipsl_cm5a_lr_rcp45_arid,min_p_cotton_Ipsl_cm5a_lr_rcp45_temperate,min_p_cotton_Ipsl_cm5a_lr_rcp45_continental]);

level = 100

p_cotton_Ipsl_cm5a_lr_rcp45=linspace(min_p_cotton_Ipsl_cm5a_lr,max_p_cotton_Ipsl_cm5a_lr,level);

% area count
% cotton global
area_cotton_Ipsl_cm5a_lr_rcp45_global=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_cotton=min_p_cotton_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_cotton_Ipsl_cm5a_lr-min_p_cotton_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)<=p_threshold_cotton)
                area_cotton_Ipsl_cm5a_lr_rcp45_global(1,k)=area_cotton_Ipsl_cm5a_lr_rcp45_global(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp45_global=area_cotton_Ipsl_cm5a_lr_rcp45_global/global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_global;


% cotton tropical
area_cotton_Ipsl_cm5a_lr_rcp45_tropical=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_cotton=min_p_cotton_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_cotton_Ipsl_cm5a_lr-min_p_cotton_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)<=p_threshold_cotton)
                area_cotton_Ipsl_cm5a_lr_rcp45_tropical(1,k)=area_cotton_Ipsl_cm5a_lr_rcp45_tropical(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp45_tropical=area_cotton_Ipsl_cm5a_lr_rcp45_tropical/global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_tropical;

% cotton arid
area_cotton_Ipsl_cm5a_lr_rcp45_arid=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_cotton=min_p_cotton_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_cotton_Ipsl_cm5a_lr-min_p_cotton_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)<=p_threshold_cotton)
                area_cotton_Ipsl_cm5a_lr_rcp45_arid(1,k)=area_cotton_Ipsl_cm5a_lr_rcp45_arid(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp45_arid=area_cotton_Ipsl_cm5a_lr_rcp45_arid/global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_arid;

% cotton temperate
area_cotton_Ipsl_cm5a_lr_rcp45_temperate=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_cotton=min_p_cotton_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_cotton_Ipsl_cm5a_lr-min_p_cotton_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)<=p_threshold_cotton)
                area_cotton_Ipsl_cm5a_lr_rcp45_temperate(1,k)=area_cotton_Ipsl_cm5a_lr_rcp45_temperate(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp45_temperate=area_cotton_Ipsl_cm5a_lr_rcp45_temperate/global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_temperate;

% cotton continental
area_cotton_Ipsl_cm5a_lr_rcp45_continental=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_cotton=min_p_cotton_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_cotton_Ipsl_cm5a_lr-min_p_cotton_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(cotton_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)==-0.01011)
        
            else
                if(cotton_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)<=p_threshold_cotton)
                area_cotton_Ipsl_cm5a_lr_rcp45_continental(1,k)=area_cotton_Ipsl_cm5a_lr_rcp45_continental(1,k)+1;
                end
            end
        end
    end
end
area_cotton_Ipsl_cm5a_lr_rcp45_continental=area_cotton_Ipsl_cm5a_lr_rcp45_continental/global_area_cotton_Ipsl_cm5a_lr_rcp45_p_change_continental;

figure(1);
subplot(4,2,2)
hold on
%
plot(p_cotton_Ipsl_cm5a_lr_rcp45,area_cotton_Ipsl_cm5a_lr_rcp45_global*100,'-','color',[0 0 0],'linewidth',1.5);
plot(p_cotton_Ipsl_cm5a_lr_rcp45,area_cotton_Ipsl_cm5a_lr_rcp45_tropical*100,'--','color',[0 0 1],'linewidth',1.5);
plot(p_cotton_Ipsl_cm5a_lr_rcp45,area_cotton_Ipsl_cm5a_lr_rcp45_arid*100,'--','color',[1 0.5 0],'linewidth',1.5);
plot(p_cotton_Ipsl_cm5a_lr_rcp45,area_cotton_Ipsl_cm5a_lr_rcp45_temperate*100,'--','color',[0 1 0],'linewidth',1.5);
plot(p_cotton_Ipsl_cm5a_lr_rcp45,area_cotton_Ipsl_cm5a_lr_rcp45_continental*100,'--','color',[1 0 1],'linewidth',1.5);
grid minor; xlim([0.2,0.8])
xx0=linspace(0.5,0.5,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])

xx0=linspace(-1,1,100);
yy0=linspace(50,50,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])


title('(b). cotton')
%legend('tropical','dry','temperate','continental')
set(gca,'fontsize',12)

%% maize
% Ipsl_cm5a_lr_rcp45  global
maize_Ipsl_cm5a_lr_rcp45_p_change_global=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_global=0;
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_global=global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_global+1;
        end
    end
end

min_p_maize_Ipsl_cm5a_lr_rcp45_global=min(min(maize_Ipsl_cm5a_lr_rcp45_p_change_global));
max_p_maize_Ipsl_cm5a_lr_rcp45_global=max(max(maize_Ipsl_cm5a_lr_rcp45_p_change_global));


% Ipsl_cm5a_lr_rcp45  tropical
maize_Ipsl_cm5a_lr_rcp45_p_change_tropical=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_tropical=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>4 || Cli_zone(m,n)==0 || maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_tropical=global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_tropical+1;
        end
    end
end

min_p_maize_Ipsl_cm5a_lr_rcp45_tropical=min(min(maize_Ipsl_cm5a_lr_rcp45_p_change_tropical));
max_p_maize_Ipsl_cm5a_lr_rcp45_tropical=max(max(maize_Ipsl_cm5a_lr_rcp45_p_change_tropical));


% Ipsl_cm5a_lr_rcp45  arid
maize_Ipsl_cm5a_lr_rcp45_p_change_arid=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_arid=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=9 || Cli_zone(m,n)<=4 || maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_arid=global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_arid+1;
        end
    end
end

min_p_maize_Ipsl_cm5a_lr_rcp45_arid=min(min(maize_Ipsl_cm5a_lr_rcp45_p_change_arid));
max_p_maize_Ipsl_cm5a_lr_rcp45_arid=max(max(maize_Ipsl_cm5a_lr_rcp45_p_change_arid));


% Ipsl_cm5a_lr_rcp45  temperate
maize_Ipsl_cm5a_lr_rcp45_p_change_temperate=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_temperate=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=18 || Cli_zone(m,n)<=8 || maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_temperate=global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_temperate+1;
        end
    end
end

min_p_maize_Ipsl_cm5a_lr_rcp45_temperate=min(min(maize_Ipsl_cm5a_lr_rcp45_p_change_temperate));
max_p_maize_Ipsl_cm5a_lr_rcp45_temperate=max(max(maize_Ipsl_cm5a_lr_rcp45_p_change_temperate));


% Ipsl_cm5a_lr_rcp45  continental
maize_Ipsl_cm5a_lr_rcp45_p_change_continental=zeros(360,720);
global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_continental=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=30 || Cli_zone(m,n)<=17 || maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=-0.01011;
        else
            maize_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_continental=global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_continental+1;
        end
    end
end

min_p_maize_Ipsl_cm5a_lr_rcp45_continental=min(min(maize_Ipsl_cm5a_lr_rcp45_p_change_continental));
max_p_maize_Ipsl_cm5a_lr_rcp45_continental=max(max(maize_Ipsl_cm5a_lr_rcp45_p_change_continental));

% compare max and min p 
max_p_maize_Ipsl_cm5a_lr=max([max_p_maize_Ipsl_cm5a_lr_rcp45_global,max_p_maize_Ipsl_cm5a_lr_rcp45_tropical,max_p_maize_Ipsl_cm5a_lr_rcp45_arid,max_p_maize_Ipsl_cm5a_lr_rcp45_temperate,max_p_maize_Ipsl_cm5a_lr_rcp45_continental]);
min_p_maize_Ipsl_cm5a_lr=min([min_p_maize_Ipsl_cm5a_lr_rcp45_global,min_p_maize_Ipsl_cm5a_lr_rcp45_tropical,min_p_maize_Ipsl_cm5a_lr_rcp45_arid,min_p_maize_Ipsl_cm5a_lr_rcp45_temperate,min_p_maize_Ipsl_cm5a_lr_rcp45_continental]);

level = 100

p_maize_Ipsl_cm5a_lr_rcp45=linspace(min_p_maize_Ipsl_cm5a_lr,max_p_maize_Ipsl_cm5a_lr,level);

% area count
% maize global
area_maize_Ipsl_cm5a_lr_rcp45_global=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_maize=min_p_maize_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_maize_Ipsl_cm5a_lr-min_p_maize_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)<=p_threshold_maize)
                area_maize_Ipsl_cm5a_lr_rcp45_global(1,k)=area_maize_Ipsl_cm5a_lr_rcp45_global(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp45_global=area_maize_Ipsl_cm5a_lr_rcp45_global/global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_global;


% maize tropical
area_maize_Ipsl_cm5a_lr_rcp45_tropical=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_maize=min_p_maize_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_maize_Ipsl_cm5a_lr-min_p_maize_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)<=p_threshold_maize)
                area_maize_Ipsl_cm5a_lr_rcp45_tropical(1,k)=area_maize_Ipsl_cm5a_lr_rcp45_tropical(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp45_tropical=area_maize_Ipsl_cm5a_lr_rcp45_tropical/global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_tropical;

% maize arid
area_maize_Ipsl_cm5a_lr_rcp45_arid=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_maize=min_p_maize_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_maize_Ipsl_cm5a_lr-min_p_maize_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)<=p_threshold_maize)
                area_maize_Ipsl_cm5a_lr_rcp45_arid(1,k)=area_maize_Ipsl_cm5a_lr_rcp45_arid(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp45_arid=area_maize_Ipsl_cm5a_lr_rcp45_arid/global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_arid;

% maize temperate
area_maize_Ipsl_cm5a_lr_rcp45_temperate=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_maize=min_p_maize_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_maize_Ipsl_cm5a_lr-min_p_maize_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)<=p_threshold_maize)
                area_maize_Ipsl_cm5a_lr_rcp45_temperate(1,k)=area_maize_Ipsl_cm5a_lr_rcp45_temperate(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp45_temperate=area_maize_Ipsl_cm5a_lr_rcp45_temperate/global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_temperate;

% maize continental
area_maize_Ipsl_cm5a_lr_rcp45_continental=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_maize=min_p_maize_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_maize_Ipsl_cm5a_lr-min_p_maize_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(maize_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)==-0.01011)
        
            else
                if(maize_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)<=p_threshold_maize)
                area_maize_Ipsl_cm5a_lr_rcp45_continental(1,k)=area_maize_Ipsl_cm5a_lr_rcp45_continental(1,k)+1;
                end
            end
        end
    end
end
area_maize_Ipsl_cm5a_lr_rcp45_continental=area_maize_Ipsl_cm5a_lr_rcp45_continental/global_area_maize_Ipsl_cm5a_lr_rcp45_p_change_continental;

figure(1);
subplot(4,2,3)
hold on
%
plot(p_maize_Ipsl_cm5a_lr_rcp45,area_maize_Ipsl_cm5a_lr_rcp45_global*100,'-','color',[0 0 0],'linewidth',1.5);
plot(p_maize_Ipsl_cm5a_lr_rcp45,area_maize_Ipsl_cm5a_lr_rcp45_tropical*100,'--','color',[0 0 1],'linewidth',1.5);
plot(p_maize_Ipsl_cm5a_lr_rcp45,area_maize_Ipsl_cm5a_lr_rcp45_arid*100,'--','color',[1 0.5 0],'linewidth',1.5);
plot(p_maize_Ipsl_cm5a_lr_rcp45,area_maize_Ipsl_cm5a_lr_rcp45_temperate*100,'--','color',[0 1 0],'linewidth',1.5);
plot(p_maize_Ipsl_cm5a_lr_rcp45,area_maize_Ipsl_cm5a_lr_rcp45_continental*100,'--','color',[1 0 1],'linewidth',1.5);
grid minor; xlim([0.2,0.8])
xx0=linspace(0.5,0.5,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])

xx0=linspace(-1,1,100);
yy0=linspace(50,50,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])


title('(c). maize')
%legend('tropical','dry','temperate','continental')
set(gca,'fontsize',12)

%% rice
% Ipsl_cm5a_lr_rcp45  global
rice_Ipsl_cm5a_lr_rcp45_p_change_global=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_global=0;
for m=1:360
    for n=1:720
        if (rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=rice_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_global=global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_global+1;
        end
    end
end

min_p_rice_Ipsl_cm5a_lr_rcp45_global=min(min(rice_Ipsl_cm5a_lr_rcp45_p_change_global));
max_p_rice_Ipsl_cm5a_lr_rcp45_global=max(max(rice_Ipsl_cm5a_lr_rcp45_p_change_global));


% Ipsl_cm5a_lr_rcp45  tropical
rice_Ipsl_cm5a_lr_rcp45_p_change_tropical=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_tropical=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>4 || Cli_zone(m,n)==0 || rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=rice_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_tropical=global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_tropical+1;
        end
    end
end

min_p_rice_Ipsl_cm5a_lr_rcp45_tropical=min(min(rice_Ipsl_cm5a_lr_rcp45_p_change_tropical));
max_p_rice_Ipsl_cm5a_lr_rcp45_tropical=max(max(rice_Ipsl_cm5a_lr_rcp45_p_change_tropical));


% Ipsl_cm5a_lr_rcp45  arid
rice_Ipsl_cm5a_lr_rcp45_p_change_arid=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_arid=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=9 || Cli_zone(m,n)<=4 || rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=rice_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_arid=global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_arid+1;
        end
    end
end

min_p_rice_Ipsl_cm5a_lr_rcp45_arid=min(min(rice_Ipsl_cm5a_lr_rcp45_p_change_arid));
max_p_rice_Ipsl_cm5a_lr_rcp45_arid=max(max(rice_Ipsl_cm5a_lr_rcp45_p_change_arid));


% Ipsl_cm5a_lr_rcp45  temperate
rice_Ipsl_cm5a_lr_rcp45_p_change_temperate=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_temperate=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=18 || Cli_zone(m,n)<=8 || rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=rice_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_temperate=global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_temperate+1;
        end
    end
end

min_p_rice_Ipsl_cm5a_lr_rcp45_temperate=min(min(rice_Ipsl_cm5a_lr_rcp45_p_change_temperate));
max_p_rice_Ipsl_cm5a_lr_rcp45_temperate=max(max(rice_Ipsl_cm5a_lr_rcp45_p_change_temperate));


% Ipsl_cm5a_lr_rcp45  continental
rice_Ipsl_cm5a_lr_rcp45_p_change_continental=zeros(360,720);
global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_continental=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=30 || Cli_zone(m,n)<=17 || rice_mask2(m,n)== 0 || rice_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || rice_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            rice_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=-0.01011;
        else
            rice_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=rice_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_continental=global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_continental+1;
        end
    end
end

min_p_rice_Ipsl_cm5a_lr_rcp45_continental=min(min(rice_Ipsl_cm5a_lr_rcp45_p_change_continental));
max_p_rice_Ipsl_cm5a_lr_rcp45_continental=max(max(rice_Ipsl_cm5a_lr_rcp45_p_change_continental));

% compare max and min p 
max_p_rice_Ipsl_cm5a_lr=max([max_p_rice_Ipsl_cm5a_lr_rcp45_global,max_p_rice_Ipsl_cm5a_lr_rcp45_tropical,max_p_rice_Ipsl_cm5a_lr_rcp45_arid,max_p_rice_Ipsl_cm5a_lr_rcp45_temperate,max_p_rice_Ipsl_cm5a_lr_rcp45_continental]);
min_p_rice_Ipsl_cm5a_lr=min([min_p_rice_Ipsl_cm5a_lr_rcp45_global,min_p_rice_Ipsl_cm5a_lr_rcp45_tropical,min_p_rice_Ipsl_cm5a_lr_rcp45_arid,min_p_rice_Ipsl_cm5a_lr_rcp45_temperate,min_p_rice_Ipsl_cm5a_lr_rcp45_continental]);

level = 100

p_rice_Ipsl_cm5a_lr_rcp45=linspace(min_p_rice_Ipsl_cm5a_lr,max_p_rice_Ipsl_cm5a_lr,level);

% area count
% rice global
area_rice_Ipsl_cm5a_lr_rcp45_global=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_rice=min_p_rice_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_rice_Ipsl_cm5a_lr-min_p_rice_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)<=p_threshold_rice)
                area_rice_Ipsl_cm5a_lr_rcp45_global(1,k)=area_rice_Ipsl_cm5a_lr_rcp45_global(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp45_global=area_rice_Ipsl_cm5a_lr_rcp45_global/global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_global;


% rice tropical
area_rice_Ipsl_cm5a_lr_rcp45_tropical=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_rice=min_p_rice_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_rice_Ipsl_cm5a_lr-min_p_rice_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)<=p_threshold_rice)
                area_rice_Ipsl_cm5a_lr_rcp45_tropical(1,k)=area_rice_Ipsl_cm5a_lr_rcp45_tropical(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp45_tropical=area_rice_Ipsl_cm5a_lr_rcp45_tropical/global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_tropical;

% rice arid
area_rice_Ipsl_cm5a_lr_rcp45_arid=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_rice=min_p_rice_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_rice_Ipsl_cm5a_lr-min_p_rice_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)<=p_threshold_rice)
                area_rice_Ipsl_cm5a_lr_rcp45_arid(1,k)=area_rice_Ipsl_cm5a_lr_rcp45_arid(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp45_arid=area_rice_Ipsl_cm5a_lr_rcp45_arid/global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_arid;

% rice temperate
area_rice_Ipsl_cm5a_lr_rcp45_temperate=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_rice=min_p_rice_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_rice_Ipsl_cm5a_lr-min_p_rice_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)<=p_threshold_rice)
                area_rice_Ipsl_cm5a_lr_rcp45_temperate(1,k)=area_rice_Ipsl_cm5a_lr_rcp45_temperate(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp45_temperate=area_rice_Ipsl_cm5a_lr_rcp45_temperate/global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_temperate;

% rice continental
area_rice_Ipsl_cm5a_lr_rcp45_continental=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_rice=min_p_rice_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_rice_Ipsl_cm5a_lr-min_p_rice_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(rice_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)==-0.01011)
        
            else
                if(rice_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)<=p_threshold_rice)
                area_rice_Ipsl_cm5a_lr_rcp45_continental(1,k)=area_rice_Ipsl_cm5a_lr_rcp45_continental(1,k)+1;
                end
            end
        end
    end
end
area_rice_Ipsl_cm5a_lr_rcp45_continental=area_rice_Ipsl_cm5a_lr_rcp45_continental/global_area_rice_Ipsl_cm5a_lr_rcp45_p_change_continental;

figure(1);
subplot(4,2,4)
hold on
%
plot(p_rice_Ipsl_cm5a_lr_rcp45,area_rice_Ipsl_cm5a_lr_rcp45_global*100,'-','color',[0 0 0],'linewidth',1.5);
plot(p_rice_Ipsl_cm5a_lr_rcp45,area_rice_Ipsl_cm5a_lr_rcp45_tropical*100,'--','color',[0 0 1],'linewidth',1.5);
plot(p_rice_Ipsl_cm5a_lr_rcp45,area_rice_Ipsl_cm5a_lr_rcp45_arid*100,'--','color',[1 0.5 0],'linewidth',1.5);
plot(p_rice_Ipsl_cm5a_lr_rcp45,area_rice_Ipsl_cm5a_lr_rcp45_temperate*100,'--','color',[0 1 0],'linewidth',1.5);
plot(p_rice_Ipsl_cm5a_lr_rcp45,area_rice_Ipsl_cm5a_lr_rcp45_continental*100,'--','color',[1 0 1],'linewidth',1.5);
grid minor; xlim([0.2,0.8])
xx0=linspace(0.5,0.5,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])

xx0=linspace(-1,1,100);
yy0=linspace(50,50,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])


title('(d). rice')
%legend('tropical','dry','temperate','continental')
set(gca,'fontsize',12)

%% sorghum
% Ipsl_cm5a_lr_rcp45  global
sorghum_Ipsl_cm5a_lr_rcp45_p_change_global=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_global=0;
for m=1:360
    for n=1:720
        if (sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=sorghum_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_global=global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_global+1;
        end
    end
end

min_p_sorghum_Ipsl_cm5a_lr_rcp45_global=min(min(sorghum_Ipsl_cm5a_lr_rcp45_p_change_global));
max_p_sorghum_Ipsl_cm5a_lr_rcp45_global=max(max(sorghum_Ipsl_cm5a_lr_rcp45_p_change_global));


% Ipsl_cm5a_lr_rcp45  tropical
sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>4 || Cli_zone(m,n)==0 || sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=sorghum_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical=global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical+1;
        end
    end
end

min_p_sorghum_Ipsl_cm5a_lr_rcp45_tropical=min(min(sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical));
max_p_sorghum_Ipsl_cm5a_lr_rcp45_tropical=max(max(sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical));


% Ipsl_cm5a_lr_rcp45  arid
sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=9 || Cli_zone(m,n)<=4 || sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=sorghum_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid=global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid+1;
        end
    end
end

min_p_sorghum_Ipsl_cm5a_lr_rcp45_arid=min(min(sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid));
max_p_sorghum_Ipsl_cm5a_lr_rcp45_arid=max(max(sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid));


% Ipsl_cm5a_lr_rcp45  temperate
sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=18 || Cli_zone(m,n)<=8 || sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=sorghum_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate=global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate+1;
        end
    end
end

min_p_sorghum_Ipsl_cm5a_lr_rcp45_temperate=min(min(sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate));
max_p_sorghum_Ipsl_cm5a_lr_rcp45_temperate=max(max(sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate));


% Ipsl_cm5a_lr_rcp45  continental
sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental=zeros(360,720);
global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=30 || Cli_zone(m,n)<=17 || sorghum_mask2(m,n)== 0 || sorghum_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sorghum_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=-0.01011;
        else
            sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=sorghum_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental=global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental+1;
        end
    end
end

min_p_sorghum_Ipsl_cm5a_lr_rcp45_continental=min(min(sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental));
max_p_sorghum_Ipsl_cm5a_lr_rcp45_continental=max(max(sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental));

% compare max and min p 
max_p_sorghum_Ipsl_cm5a_lr=max([max_p_sorghum_Ipsl_cm5a_lr_rcp45_global,max_p_sorghum_Ipsl_cm5a_lr_rcp45_tropical,max_p_sorghum_Ipsl_cm5a_lr_rcp45_arid,max_p_sorghum_Ipsl_cm5a_lr_rcp45_temperate,max_p_sorghum_Ipsl_cm5a_lr_rcp45_continental]);
min_p_sorghum_Ipsl_cm5a_lr=min([min_p_sorghum_Ipsl_cm5a_lr_rcp45_global,min_p_sorghum_Ipsl_cm5a_lr_rcp45_tropical,min_p_sorghum_Ipsl_cm5a_lr_rcp45_arid,min_p_sorghum_Ipsl_cm5a_lr_rcp45_temperate,min_p_sorghum_Ipsl_cm5a_lr_rcp45_continental]);

level = 100

p_sorghum_Ipsl_cm5a_lr_rcp45=linspace(min_p_sorghum_Ipsl_cm5a_lr,max_p_sorghum_Ipsl_cm5a_lr,level);

% area count
% sorghum global
area_sorghum_Ipsl_cm5a_lr_rcp45_global=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sorghum=min_p_sorghum_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sorghum_Ipsl_cm5a_lr-min_p_sorghum_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)<=p_threshold_sorghum)
                area_sorghum_Ipsl_cm5a_lr_rcp45_global(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp45_global(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp45_global=area_sorghum_Ipsl_cm5a_lr_rcp45_global/global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_global;


% sorghum tropical
area_sorghum_Ipsl_cm5a_lr_rcp45_tropical=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sorghum=min_p_sorghum_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sorghum_Ipsl_cm5a_lr-min_p_sorghum_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)<=p_threshold_sorghum)
                area_sorghum_Ipsl_cm5a_lr_rcp45_tropical(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp45_tropical(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp45_tropical=area_sorghum_Ipsl_cm5a_lr_rcp45_tropical/global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_tropical;

% sorghum arid
area_sorghum_Ipsl_cm5a_lr_rcp45_arid=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sorghum=min_p_sorghum_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sorghum_Ipsl_cm5a_lr-min_p_sorghum_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)<=p_threshold_sorghum)
                area_sorghum_Ipsl_cm5a_lr_rcp45_arid(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp45_arid(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp45_arid=area_sorghum_Ipsl_cm5a_lr_rcp45_arid/global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_arid;

% sorghum temperate
area_sorghum_Ipsl_cm5a_lr_rcp45_temperate=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sorghum=min_p_sorghum_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sorghum_Ipsl_cm5a_lr-min_p_sorghum_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)<=p_threshold_sorghum)
                area_sorghum_Ipsl_cm5a_lr_rcp45_temperate(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp45_temperate(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp45_temperate=area_sorghum_Ipsl_cm5a_lr_rcp45_temperate/global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_temperate;

% sorghum continental
area_sorghum_Ipsl_cm5a_lr_rcp45_continental=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sorghum=min_p_sorghum_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sorghum_Ipsl_cm5a_lr-min_p_sorghum_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)==-0.01011)
        
            else
                if(sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)<=p_threshold_sorghum)
                area_sorghum_Ipsl_cm5a_lr_rcp45_continental(1,k)=area_sorghum_Ipsl_cm5a_lr_rcp45_continental(1,k)+1;
                end
            end
        end
    end
end
area_sorghum_Ipsl_cm5a_lr_rcp45_continental=area_sorghum_Ipsl_cm5a_lr_rcp45_continental/global_area_sorghum_Ipsl_cm5a_lr_rcp45_p_change_continental;

figure(1);
subplot(4,2,5)
hold on
%
plot(p_sorghum_Ipsl_cm5a_lr_rcp45,area_sorghum_Ipsl_cm5a_lr_rcp45_global*100,'-','color',[0 0 0],'linewidth',1.5);
plot(p_sorghum_Ipsl_cm5a_lr_rcp45,area_sorghum_Ipsl_cm5a_lr_rcp45_tropical*100,'--','color',[0 0 1],'linewidth',1.5);
plot(p_sorghum_Ipsl_cm5a_lr_rcp45,area_sorghum_Ipsl_cm5a_lr_rcp45_arid*100,'--','color',[1 0.5 0],'linewidth',1.5);
plot(p_sorghum_Ipsl_cm5a_lr_rcp45,area_sorghum_Ipsl_cm5a_lr_rcp45_temperate*100,'--','color',[0 1 0],'linewidth',1.5);
plot(p_sorghum_Ipsl_cm5a_lr_rcp45,area_sorghum_Ipsl_cm5a_lr_rcp45_continental*100,'--','color',[1 0 1],'linewidth',1.5);
grid minor; xlim([0.2,0.8])
xx0=linspace(0.5,0.5,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])

xx0=linspace(-1,1,100);
yy0=linspace(50,50,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])


title('(e). sorghum')
%legend('tropical','dry','temperate','continental')
set(gca,'fontsize',12)

%% soybean
% Ipsl_cm5a_lr_rcp45  global
soybean_Ipsl_cm5a_lr_rcp45_p_change_global=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_global=0;
for m=1:360
    for n=1:720
        if (soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=soybean_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_global=global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_global+1;
        end
    end
end

min_p_soybean_Ipsl_cm5a_lr_rcp45_global=min(min(soybean_Ipsl_cm5a_lr_rcp45_p_change_global));
max_p_soybean_Ipsl_cm5a_lr_rcp45_global=max(max(soybean_Ipsl_cm5a_lr_rcp45_p_change_global));


% Ipsl_cm5a_lr_rcp45  tropical
soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>4 || Cli_zone(m,n)==0 || soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=soybean_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical=global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical+1;
        end
    end
end

min_p_soybean_Ipsl_cm5a_lr_rcp45_tropical=min(min(soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical));
max_p_soybean_Ipsl_cm5a_lr_rcp45_tropical=max(max(soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical));


% Ipsl_cm5a_lr_rcp45  arid
soybean_Ipsl_cm5a_lr_rcp45_p_change_arid=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_arid=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=9 || Cli_zone(m,n)<=4 || soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=soybean_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_arid=global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_arid+1;
        end
    end
end

min_p_soybean_Ipsl_cm5a_lr_rcp45_arid=min(min(soybean_Ipsl_cm5a_lr_rcp45_p_change_arid));
max_p_soybean_Ipsl_cm5a_lr_rcp45_arid=max(max(soybean_Ipsl_cm5a_lr_rcp45_p_change_arid));


% Ipsl_cm5a_lr_rcp45  temperate
soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=18 || Cli_zone(m,n)<=8 || soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=soybean_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate=global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate+1;
        end
    end
end

min_p_soybean_Ipsl_cm5a_lr_rcp45_temperate=min(min(soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate));
max_p_soybean_Ipsl_cm5a_lr_rcp45_temperate=max(max(soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate));


% Ipsl_cm5a_lr_rcp45  continental
soybean_Ipsl_cm5a_lr_rcp45_p_change_continental=zeros(360,720);
global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_continental=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=30 || Cli_zone(m,n)<=17 || soybean_mask2(m,n)== 0 || soybean_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || soybean_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            soybean_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=-0.01011;
        else
            soybean_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=soybean_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_continental=global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_continental+1;
        end
    end
end

min_p_soybean_Ipsl_cm5a_lr_rcp45_continental=min(min(soybean_Ipsl_cm5a_lr_rcp45_p_change_continental));
max_p_soybean_Ipsl_cm5a_lr_rcp45_continental=max(max(soybean_Ipsl_cm5a_lr_rcp45_p_change_continental));

% compare max and min p 
max_p_soybean_Ipsl_cm5a_lr=max([max_p_soybean_Ipsl_cm5a_lr_rcp45_global,max_p_soybean_Ipsl_cm5a_lr_rcp45_tropical,max_p_soybean_Ipsl_cm5a_lr_rcp45_arid,max_p_soybean_Ipsl_cm5a_lr_rcp45_temperate,max_p_soybean_Ipsl_cm5a_lr_rcp45_continental]);
min_p_soybean_Ipsl_cm5a_lr=min([min_p_soybean_Ipsl_cm5a_lr_rcp45_global,min_p_soybean_Ipsl_cm5a_lr_rcp45_tropical,min_p_soybean_Ipsl_cm5a_lr_rcp45_arid,min_p_soybean_Ipsl_cm5a_lr_rcp45_temperate,min_p_soybean_Ipsl_cm5a_lr_rcp45_continental]);

level = 100

p_soybean_Ipsl_cm5a_lr_rcp45=linspace(min_p_soybean_Ipsl_cm5a_lr,max_p_soybean_Ipsl_cm5a_lr,level);

% area count
% soybean global
area_soybean_Ipsl_cm5a_lr_rcp45_global=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_soybean=min_p_soybean_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_soybean_Ipsl_cm5a_lr-min_p_soybean_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)<=p_threshold_soybean)
                area_soybean_Ipsl_cm5a_lr_rcp45_global(1,k)=area_soybean_Ipsl_cm5a_lr_rcp45_global(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp45_global=area_soybean_Ipsl_cm5a_lr_rcp45_global/global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_global;


% soybean tropical
area_soybean_Ipsl_cm5a_lr_rcp45_tropical=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_soybean=min_p_soybean_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_soybean_Ipsl_cm5a_lr-min_p_soybean_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)<=p_threshold_soybean)
                area_soybean_Ipsl_cm5a_lr_rcp45_tropical(1,k)=area_soybean_Ipsl_cm5a_lr_rcp45_tropical(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp45_tropical=area_soybean_Ipsl_cm5a_lr_rcp45_tropical/global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_tropical;

% soybean arid
area_soybean_Ipsl_cm5a_lr_rcp45_arid=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_soybean=min_p_soybean_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_soybean_Ipsl_cm5a_lr-min_p_soybean_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)<=p_threshold_soybean)
                area_soybean_Ipsl_cm5a_lr_rcp45_arid(1,k)=area_soybean_Ipsl_cm5a_lr_rcp45_arid(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp45_arid=area_soybean_Ipsl_cm5a_lr_rcp45_arid/global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_arid;

% soybean temperate
area_soybean_Ipsl_cm5a_lr_rcp45_temperate=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_soybean=min_p_soybean_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_soybean_Ipsl_cm5a_lr-min_p_soybean_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)<=p_threshold_soybean)
                area_soybean_Ipsl_cm5a_lr_rcp45_temperate(1,k)=area_soybean_Ipsl_cm5a_lr_rcp45_temperate(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp45_temperate=area_soybean_Ipsl_cm5a_lr_rcp45_temperate/global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_temperate;

% soybean continental
area_soybean_Ipsl_cm5a_lr_rcp45_continental=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_soybean=min_p_soybean_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_soybean_Ipsl_cm5a_lr-min_p_soybean_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(soybean_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)==-0.01011)
        
            else
                if(soybean_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)<=p_threshold_soybean)
                area_soybean_Ipsl_cm5a_lr_rcp45_continental(1,k)=area_soybean_Ipsl_cm5a_lr_rcp45_continental(1,k)+1;
                end
            end
        end
    end
end
area_soybean_Ipsl_cm5a_lr_rcp45_continental=area_soybean_Ipsl_cm5a_lr_rcp45_continental/global_area_soybean_Ipsl_cm5a_lr_rcp45_p_change_continental;

figure(1);
subplot(4,2,6)
hold on
%
plot(p_soybean_Ipsl_cm5a_lr_rcp45,area_soybean_Ipsl_cm5a_lr_rcp45_global*100,'-','color',[0 0 0],'linewidth',1.5);
plot(p_soybean_Ipsl_cm5a_lr_rcp45,area_soybean_Ipsl_cm5a_lr_rcp45_tropical*100,'--','color',[0 0 1],'linewidth',1.5);
plot(p_soybean_Ipsl_cm5a_lr_rcp45,area_soybean_Ipsl_cm5a_lr_rcp45_arid*100,'--','color',[1 0.5 0],'linewidth',1.5);
plot(p_soybean_Ipsl_cm5a_lr_rcp45,area_soybean_Ipsl_cm5a_lr_rcp45_temperate*100,'--','color',[0 1 0],'linewidth',1.5);
plot(p_soybean_Ipsl_cm5a_lr_rcp45,area_soybean_Ipsl_cm5a_lr_rcp45_continental*100,'--','color',[1 0 1],'linewidth',1.5);
grid minor; xlim([0.2,0.8])
xx0=linspace(0.5,0.5,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])

xx0=linspace(-1,1,100);
yy0=linspace(50,50,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])


title('(f). soybean')
%legend('tropical','dry','temperate','continental')
set(gca,'fontsize',12)

%% sunflower
% Ipsl_cm5a_lr_rcp45  global
sunflower_Ipsl_cm5a_lr_rcp45_p_change_global=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_global=0;
for m=1:360
    for n=1:720
        if (sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=sunflower_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_global=global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_global+1;
        end
    end
end

min_p_sunflower_Ipsl_cm5a_lr_rcp45_global=min(min(sunflower_Ipsl_cm5a_lr_rcp45_p_change_global));
max_p_sunflower_Ipsl_cm5a_lr_rcp45_global=max(max(sunflower_Ipsl_cm5a_lr_rcp45_p_change_global));


% Ipsl_cm5a_lr_rcp45  tropical
sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>4 || Cli_zone(m,n)==0 || sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=sunflower_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical=global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical+1;
        end
    end
end

min_p_sunflower_Ipsl_cm5a_lr_rcp45_tropical=min(min(sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical));
max_p_sunflower_Ipsl_cm5a_lr_rcp45_tropical=max(max(sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical));


% Ipsl_cm5a_lr_rcp45  arid
sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=9 || Cli_zone(m,n)<=4 || sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=sunflower_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid=global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid+1;
        end
    end
end

min_p_sunflower_Ipsl_cm5a_lr_rcp45_arid=min(min(sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid));
max_p_sunflower_Ipsl_cm5a_lr_rcp45_arid=max(max(sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid));


% Ipsl_cm5a_lr_rcp45  temperate
sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=18 || Cli_zone(m,n)<=8 || sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=sunflower_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate=global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate+1;
        end
    end
end

min_p_sunflower_Ipsl_cm5a_lr_rcp45_temperate=min(min(sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate));
max_p_sunflower_Ipsl_cm5a_lr_rcp45_temperate=max(max(sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate));


% Ipsl_cm5a_lr_rcp45  continental
sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental=zeros(360,720);
global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=30 || Cli_zone(m,n)<=17 || sunflower_mask2(m,n)== 0 || sunflower_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || sunflower_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=-0.01011;
        else
            sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=sunflower_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental=global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental+1;
        end
    end
end

min_p_sunflower_Ipsl_cm5a_lr_rcp45_continental=min(min(sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental));
max_p_sunflower_Ipsl_cm5a_lr_rcp45_continental=max(max(sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental));

% compare max and min p 
max_p_sunflower_Ipsl_cm5a_lr=max([max_p_sunflower_Ipsl_cm5a_lr_rcp45_global,max_p_sunflower_Ipsl_cm5a_lr_rcp45_tropical,max_p_sunflower_Ipsl_cm5a_lr_rcp45_arid,max_p_sunflower_Ipsl_cm5a_lr_rcp45_temperate,max_p_sunflower_Ipsl_cm5a_lr_rcp45_continental]);
min_p_sunflower_Ipsl_cm5a_lr=min([min_p_sunflower_Ipsl_cm5a_lr_rcp45_global,min_p_sunflower_Ipsl_cm5a_lr_rcp45_tropical,min_p_sunflower_Ipsl_cm5a_lr_rcp45_arid,min_p_sunflower_Ipsl_cm5a_lr_rcp45_temperate,min_p_sunflower_Ipsl_cm5a_lr_rcp45_continental]);

level = 100

p_sunflower_Ipsl_cm5a_lr_rcp45=linspace(min_p_sunflower_Ipsl_cm5a_lr,max_p_sunflower_Ipsl_cm5a_lr,level);

% area count
% sunflower global
area_sunflower_Ipsl_cm5a_lr_rcp45_global=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sunflower=min_p_sunflower_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sunflower_Ipsl_cm5a_lr-min_p_sunflower_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)<=p_threshold_sunflower)
                area_sunflower_Ipsl_cm5a_lr_rcp45_global(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp45_global(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp45_global=area_sunflower_Ipsl_cm5a_lr_rcp45_global/global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_global;


% sunflower tropical
area_sunflower_Ipsl_cm5a_lr_rcp45_tropical=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sunflower=min_p_sunflower_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sunflower_Ipsl_cm5a_lr-min_p_sunflower_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)<=p_threshold_sunflower)
                area_sunflower_Ipsl_cm5a_lr_rcp45_tropical(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp45_tropical(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp45_tropical=area_sunflower_Ipsl_cm5a_lr_rcp45_tropical/global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_tropical;

% sunflower arid
area_sunflower_Ipsl_cm5a_lr_rcp45_arid=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sunflower=min_p_sunflower_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sunflower_Ipsl_cm5a_lr-min_p_sunflower_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)<=p_threshold_sunflower)
                area_sunflower_Ipsl_cm5a_lr_rcp45_arid(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp45_arid(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp45_arid=area_sunflower_Ipsl_cm5a_lr_rcp45_arid/global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_arid;

% sunflower temperate
area_sunflower_Ipsl_cm5a_lr_rcp45_temperate=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sunflower=min_p_sunflower_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sunflower_Ipsl_cm5a_lr-min_p_sunflower_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)<=p_threshold_sunflower)
                area_sunflower_Ipsl_cm5a_lr_rcp45_temperate(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp45_temperate(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp45_temperate=area_sunflower_Ipsl_cm5a_lr_rcp45_temperate/global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_temperate;

% sunflower continental
area_sunflower_Ipsl_cm5a_lr_rcp45_continental=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_sunflower=min_p_sunflower_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_sunflower_Ipsl_cm5a_lr-min_p_sunflower_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)==-0.01011)
        
            else
                if(sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)<=p_threshold_sunflower)
                area_sunflower_Ipsl_cm5a_lr_rcp45_continental(1,k)=area_sunflower_Ipsl_cm5a_lr_rcp45_continental(1,k)+1;
                end
            end
        end
    end
end
area_sunflower_Ipsl_cm5a_lr_rcp45_continental=area_sunflower_Ipsl_cm5a_lr_rcp45_continental/global_area_sunflower_Ipsl_cm5a_lr_rcp45_p_change_continental;

figure(1);
subplot(4,2,7)
hold on
%
plot(p_sunflower_Ipsl_cm5a_lr_rcp45,area_sunflower_Ipsl_cm5a_lr_rcp45_global*100,'-','color',[0 0 0],'linewidth',1.5);
plot(p_sunflower_Ipsl_cm5a_lr_rcp45,area_sunflower_Ipsl_cm5a_lr_rcp45_tropical*100,'--','color',[0 0 1],'linewidth',1.5);
plot(p_sunflower_Ipsl_cm5a_lr_rcp45,area_sunflower_Ipsl_cm5a_lr_rcp45_arid*100,'--','color',[1 0.5 0],'linewidth',1.5);
plot(p_sunflower_Ipsl_cm5a_lr_rcp45,area_sunflower_Ipsl_cm5a_lr_rcp45_temperate*100,'--','color',[0 1 0],'linewidth',1.5);
plot(p_sunflower_Ipsl_cm5a_lr_rcp45,area_sunflower_Ipsl_cm5a_lr_rcp45_continental*100,'--','color',[1 0 1],'linewidth',1.5);
grid minor; xlim([0.2,0.8])
xx0=linspace(0.5,0.5,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])

xx0=linspace(-1,1,100);
yy0=linspace(50,50,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])


title('(h). sunflower')
%legend('tropical','dry','temperate','continental')
set(gca,'fontsize',12)


%% wheat
% Ipsl_cm5a_lr_rcp45  global
wheat_Ipsl_cm5a_lr_rcp45_p_change_global=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_global=0;
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_global=global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_global+1;
        end
    end
end

min_p_wheat_Ipsl_cm5a_lr_rcp45_global=min(min(wheat_Ipsl_cm5a_lr_rcp45_p_change_global));
max_p_wheat_Ipsl_cm5a_lr_rcp45_global=max(max(wheat_Ipsl_cm5a_lr_rcp45_p_change_global));


% Ipsl_cm5a_lr_rcp45  tropical
wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>4 || Cli_zone(m,n)==0 || wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical=global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical+1;
        end
    end
end

min_p_wheat_Ipsl_cm5a_lr_rcp45_tropical=min(min(wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical));
max_p_wheat_Ipsl_cm5a_lr_rcp45_tropical=max(max(wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical));


% Ipsl_cm5a_lr_rcp45  arid
wheat_Ipsl_cm5a_lr_rcp45_p_change_arid=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_arid=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=9 || Cli_zone(m,n)<=4 || wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_arid=global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_arid+1;
        end
    end
end

min_p_wheat_Ipsl_cm5a_lr_rcp45_arid=min(min(wheat_Ipsl_cm5a_lr_rcp45_p_change_arid));
max_p_wheat_Ipsl_cm5a_lr_rcp45_arid=max(max(wheat_Ipsl_cm5a_lr_rcp45_p_change_arid));


% Ipsl_cm5a_lr_rcp45  temperate
wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=18 || Cli_zone(m,n)<=8 || wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate=global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate+1;
        end
    end
end

min_p_wheat_Ipsl_cm5a_lr_rcp45_temperate=min(min(wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate));
max_p_wheat_Ipsl_cm5a_lr_rcp45_temperate=max(max(wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate));


% Ipsl_cm5a_lr_rcp45  continental
wheat_Ipsl_cm5a_lr_rcp45_p_change_continental=zeros(360,720);
global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_continental=0;
for m=1:360
    for n=1:720
        if (Cli_zone(m,n)>=30 || Cli_zone(m,n)<=17 || wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=-0.01011;
        else
            wheat_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
            global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_continental=global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_continental+1;
        end
    end
end

min_p_wheat_Ipsl_cm5a_lr_rcp45_continental=min(min(wheat_Ipsl_cm5a_lr_rcp45_p_change_continental));
max_p_wheat_Ipsl_cm5a_lr_rcp45_continental=max(max(wheat_Ipsl_cm5a_lr_rcp45_p_change_continental));

% compare max and min p 
max_p_wheat_Ipsl_cm5a_lr=max([max_p_wheat_Ipsl_cm5a_lr_rcp45_global,max_p_wheat_Ipsl_cm5a_lr_rcp45_tropical,max_p_wheat_Ipsl_cm5a_lr_rcp45_arid,max_p_wheat_Ipsl_cm5a_lr_rcp45_temperate,max_p_wheat_Ipsl_cm5a_lr_rcp45_continental]);
min_p_wheat_Ipsl_cm5a_lr=min([min_p_wheat_Ipsl_cm5a_lr_rcp45_global,min_p_wheat_Ipsl_cm5a_lr_rcp45_tropical,min_p_wheat_Ipsl_cm5a_lr_rcp45_arid,min_p_wheat_Ipsl_cm5a_lr_rcp45_temperate,min_p_wheat_Ipsl_cm5a_lr_rcp45_continental]);

level = 100

p_wheat_Ipsl_cm5a_lr_rcp45=linspace(min_p_wheat_Ipsl_cm5a_lr,max_p_wheat_Ipsl_cm5a_lr,level);

% area count
% wheat global
area_wheat_Ipsl_cm5a_lr_rcp45_global=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_wheat=min_p_wheat_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_wheat_Ipsl_cm5a_lr-min_p_wheat_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp45_p_change_global(m,n)<=p_threshold_wheat)
                area_wheat_Ipsl_cm5a_lr_rcp45_global(1,k)=area_wheat_Ipsl_cm5a_lr_rcp45_global(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp45_global=area_wheat_Ipsl_cm5a_lr_rcp45_global/global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_global;


% wheat tropical
area_wheat_Ipsl_cm5a_lr_rcp45_tropical=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_wheat=min_p_wheat_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_wheat_Ipsl_cm5a_lr-min_p_wheat_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical(m,n)<=p_threshold_wheat)
                area_wheat_Ipsl_cm5a_lr_rcp45_tropical(1,k)=area_wheat_Ipsl_cm5a_lr_rcp45_tropical(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp45_tropical=area_wheat_Ipsl_cm5a_lr_rcp45_tropical/global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_tropical;

% wheat arid
area_wheat_Ipsl_cm5a_lr_rcp45_arid=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_wheat=min_p_wheat_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_wheat_Ipsl_cm5a_lr-min_p_wheat_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp45_p_change_arid(m,n)<=p_threshold_wheat)
                area_wheat_Ipsl_cm5a_lr_rcp45_arid(1,k)=area_wheat_Ipsl_cm5a_lr_rcp45_arid(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp45_arid=area_wheat_Ipsl_cm5a_lr_rcp45_arid/global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_arid;

% wheat temperate
area_wheat_Ipsl_cm5a_lr_rcp45_temperate=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_wheat=min_p_wheat_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_wheat_Ipsl_cm5a_lr-min_p_wheat_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate(m,n)<=p_threshold_wheat)
                area_wheat_Ipsl_cm5a_lr_rcp45_temperate(1,k)=area_wheat_Ipsl_cm5a_lr_rcp45_temperate(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp45_temperate=area_wheat_Ipsl_cm5a_lr_rcp45_temperate/global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_temperate;

% wheat continental
area_wheat_Ipsl_cm5a_lr_rcp45_continental=zeros(1,level);
delta_p=0;
for k=1:level
    p_threshold_wheat=min_p_wheat_Ipsl_cm5a_lr+delta_p;
    delta_p=delta_p+(max_p_wheat_Ipsl_cm5a_lr-min_p_wheat_Ipsl_cm5a_lr)/(level-1);
    for m=1:360
        for n=1:720
            if(wheat_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)==-0.01011)
        
            else
                if(wheat_Ipsl_cm5a_lr_rcp45_p_change_continental(m,n)<=p_threshold_wheat)
                area_wheat_Ipsl_cm5a_lr_rcp45_continental(1,k)=area_wheat_Ipsl_cm5a_lr_rcp45_continental(1,k)+1;
                end
            end
        end
    end
end
area_wheat_Ipsl_cm5a_lr_rcp45_continental=area_wheat_Ipsl_cm5a_lr_rcp45_continental/global_area_wheat_Ipsl_cm5a_lr_rcp45_p_change_continental;

figure(1);
subplot(4,2,8)
hold on
%
plot(p_wheat_Ipsl_cm5a_lr_rcp45,area_wheat_Ipsl_cm5a_lr_rcp45_global*100,'-','color',[0 0 0],'linewidth',1.5);
plot(p_wheat_Ipsl_cm5a_lr_rcp45,area_wheat_Ipsl_cm5a_lr_rcp45_tropical*100,'--','color',[0 0 1],'linewidth',1.5);
plot(p_wheat_Ipsl_cm5a_lr_rcp45,area_wheat_Ipsl_cm5a_lr_rcp45_arid*100,'--','color',[1 0.5 0],'linewidth',1.5);
plot(p_wheat_Ipsl_cm5a_lr_rcp45,area_wheat_Ipsl_cm5a_lr_rcp45_temperate*100,'--','color',[0 1 0],'linewidth',1.5);
plot(p_wheat_Ipsl_cm5a_lr_rcp45,area_wheat_Ipsl_cm5a_lr_rcp45_continental*100,'--','color',[1 0 1],'linewidth',1.5);
grid minor; xlim([0.2,0.8])
xx0=linspace(0.5,0.5,100);
yy0=linspace(0,100,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])

xx0=linspace(-1,1,100);
yy0=linspace(50,50,100);
plot(xx0,yy0,'-.','color',[0.1,0.1,0.1])

title('(i). wheat')
set(gca,'fontsize',12)
ld=legend('global','tropical','dry','temperate','continental')
set(ld,'position',[ 0.9091    0.8130    0.0844    0.1030])
%set(ld,'position',[ 0.9151    0.7703    0.0725    0.1392])
set(ld,'fontsize',13)


hh1=xlabel('Probability of yield gain from CA in different climate zones under current scenario')
%set(hh1,'position',[-0.5155  -31.8882   -1.0000])
set(hh1,'fontsize',14)
hh2=ylabel('Acculumated fraction of cropping area [%]')
%set(hh2,'position',[   -1.5351  263.2362   -1.0000])
set(hh2,'fontsize',14)


%%
%saveas(gca,'033_curve_different_climate_zone_with_global.png')
%saveas(gca,'033_curve_different_climate_zone_with_global.tif')
%saveas(gca,'033_curve_different_climate_zone_with_global.fig')
