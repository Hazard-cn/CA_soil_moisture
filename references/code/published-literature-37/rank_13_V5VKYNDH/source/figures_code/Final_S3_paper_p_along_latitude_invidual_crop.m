%%
clear all;clc
load('yield_prediction_CA_with_F_WD.mat');
load('crop_mask_new_360_720_std.mat')% only B M S W
%% wheat
figure(1);clf
h1=subplot(2,3,1)
set(h1,'position',[h1.Position(1)-0.05,h1.Position(2),h1.Position(3),h1.Position(4)])
% Ipsl_cm5a_lr_rcp45
wheat_Ipsl_cm5a_lr_rcp45_prob_p=zeros(360,720);
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
end

wheat_lat=zeros(360,1);
wheat_lat_25=zeros(360,1);
wheat_lat_75=zeros(360,1);
for m=1:360
    count=0;
    temp=0;
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            count=count+1;
            temp(count)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
    if(count~=0)
            wheat_lat(m)=median(temp);
            wheat_lat_25(m)=quantile(temp,0.25);
            wheat_lat_75(m)=quantile(temp,0.75);
    else
        wheat_lat(m)=-1;
        wheat_lat_25(m)=-1;
        wheat_lat_75(m)=-1;
    end
end

y=linspace(-90,90,360);
x=linspace(0.5,0.5,360);
plot(wheat_lat_75,y,'.','color',[54 75 255]/255,'markersize',8);
hold on
plot(wheat_lat,y,'.','color',[0 0 0]/255,'markersize',8);
plot(wheat_lat_25,y,'.','color',[255 79 3]/255,'markersize',8);

plot(x,y,'--black');
ylim([-90,90])
xlim([0.2,0.8])
hold off
t1=title('1. wheat under CA (+F+WD) practice')
set(gca,'fontsize',12)
%%
clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W
load('yield_prediction_CA_without_F_WD.mat');
%% wheat
f1=figure(1);
h1=subplot(2,3,2)
set(h1,'position',[h1.Position(1)-0.05-0.02,h1.Position(2),h1.Position(3),h1.Position(4)])
% Ipsl_cm5a_lr_rcp45
wheat_Ipsl_cm5a_lr_rcp45_prob_p=zeros(360,720);
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
end

wheat_lat=zeros(360,1);
wheat_lat_25=zeros(360,1);
wheat_lat_75=zeros(360,1);
for m=1:360
    count=0;
    temp=0;
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            count=count+1;
            temp(count)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
    if(count~=0)
            wheat_lat(m)=median(temp);
            wheat_lat_25(m)=quantile(temp,0.25);
            wheat_lat_75(m)=quantile(temp,0.75);
    else
        wheat_lat(m)=-1;
        wheat_lat_25(m)=-1;
        wheat_lat_75(m)=-1;
    end
end

y=linspace(-90,90,360);
x=linspace(0.5,0.5,360);
plot(wheat_lat_75,y,'.','color',[54 75 255]/255,'markersize',8);
hold on
plot(wheat_lat,y,'.','color',[0 0 0]/255,'markersize',8);
plot(wheat_lat_25,y,'.','color',[255 79 3]/255,'markersize',8);

plot(x,y,'--black');
ylim([-90,90])
xlim([0.2,0.8])
hold off
t1=title('2. wheat under CA (-F-WD) practice')
set(gca,'fontsize',12)
%%
clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W
load('yield_prediction_NT_with_F_WD_R_without_SC.mat');
%% wheat
figure(1);
h1=subplot(2,3,3)
set(h1,'position',[h1.Position(1)-0.05-0.02-0.02,h1.Position(2),h1.Position(3),h1.Position(4)])
% Ipsl_cm5a_lr_rcp45
wheat_Ipsl_cm5a_lr_rcp45_prob_p=zeros(360,720);
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
end

wheat_lat=zeros(360,1);
wheat_lat_25=zeros(360,1);
wheat_lat_75=zeros(360,1);
for m=1:360
    count=0;
    temp=0;
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            count=count+1;
            temp(count)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
    if(count~=0)
            wheat_lat(m)=median(temp);
            wheat_lat_25(m)=quantile(temp,0.25);
            wheat_lat_75(m)=quantile(temp,0.75);
    else
        wheat_lat(m)=-1;
        wheat_lat_25(m)=-1;
        wheat_lat_75(m)=-1;
    end
end

y=linspace(-90,90,360);
x=linspace(0.5,0.5,360);
plot(wheat_lat_75,y,'.','color',[54 75 255]/255,'markersize',8);
hold on
plot(wheat_lat,y,'.','color',[0 0 0]/255,'markersize',8);
plot(wheat_lat_25,y,'.','color',[255 79 3]/255,'markersize',8);

plot(x,y,'--black');
ylim([-90,90])
xlim([0.2,0.8])
hold off
t1=title('3. wheat under NT+R-SC (+F+WD) practice')
set(gca,'fontsize',12)

%%
clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W
load('yield_prediction_NT_with_F_WD_without_R_SC.mat');
%% wheat
figure(1);
h1=subplot(2,3,4)
set(h1,'position',[h1.Position(1)-0.05,h1.Position(2),h1.Position(3),h1.Position(4)])
% Ipsl_cm5a_lr_rcp45
wheat_Ipsl_cm5a_lr_rcp45_prob_p=zeros(360,720);
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
end

wheat_lat=zeros(360,1);
wheat_lat_25=zeros(360,1);
wheat_lat_75=zeros(360,1);
for m=1:360
    count=0;
    temp=0;
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            count=count+1;
            temp(count)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
    if(count~=0)
            wheat_lat(m)=median(temp);
            wheat_lat_25(m)=quantile(temp,0.25);
            wheat_lat_75(m)=quantile(temp,0.75);
    else
        wheat_lat(m)=-1;
        wheat_lat_25(m)=-1;
        wheat_lat_75(m)=-1;
    end
end

y=linspace(-90,90,360);
x=linspace(0.5,0.5,360);
plot(wheat_lat_75,y,'.','color',[54 75 255]/255,'markersize',8);
hold on
plot(wheat_lat,y,'.','color',[0 0 0]/255,'markersize',8);
plot(wheat_lat_25,y,'.','color',[255 79 3]/255,'markersize',8);

plot(x,y,'--black');
ylim([-90,90])
xlim([0.2,0.8])
hold off
t1=title('4. wheat under NT-R-SC (+F+WD) practice')
set(gca,'fontsize',12)
%%
clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W
load('yield_prediction_NT_without_F_WD_R_SC.mat');
%% wheat
figure(1);
h1=subplot(2,3,5)
set(h1,'position',[h1.Position(1)-0.05-0.02,h1.Position(2),h1.Position(3),h1.Position(4)])
% Ipsl_cm5a_lr_rcp45
wheat_Ipsl_cm5a_lr_rcp45_prob_p=zeros(360,720);
for m=1:360
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
end

wheat_lat=zeros(360,1);
wheat_lat_25=zeros(360,1);
wheat_lat_75=zeros(360,1);
for m=1:360
    count=0;
    temp=0;
    for n=1:720
        if (wheat_mask2(m,n)== 0 || wheat_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || wheat_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            count=count+1;
            temp(count)=wheat_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
    if(count~=0)
            wheat_lat(m)=median(temp);
            wheat_lat_25(m)=quantile(temp,0.25);
            wheat_lat_75(m)=quantile(temp,0.75);
    else
        wheat_lat(m)=-1;
        wheat_lat_25(m)=-1;
        wheat_lat_75(m)=-1;
    end
end

y=linspace(-90,90,360);
x=linspace(0.5,0.5,360);
plot(wheat_lat_75,y,'.','color',[54 75 255]/255,'markersize',8);
hold on
plot(wheat_lat,y,'.','color',[0 0 0]/255,'markersize',8);
plot(wheat_lat_25,y,'.','color',[255 79 3]/255,'markersize',8);

plot(x,y,'--black');
ylim([-90,90])
xlim([0.2,0.8])
hold off
t1=title('5. wheat under NT-R-SC (-F-WD) practice')
set(gca,'fontsize',12)
%%
ld=legend('3rd quartile','median','1st quartile')
set(ld,'position',[0.8464    0.8279    0.0858    0.0900])
set(ld,'fontsize',12)
xlab=xlabel('Probability of yield increase for each latitude','fontsize',14)
ylab=ylabel('Latitude [°]','fontsize',14)
set(ylab,'position',[-0.6059  120.7524   -1.0000])
set(xlab,'position',[0.5000 -109.7492   -1.0000])
