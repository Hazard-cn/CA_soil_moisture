%%
clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W
load('yield_prediction_CA_with_F_WD.mat');
%% wheat current
% 
f1=figure(1);clf
h1=subplot(2,3,1)
set(h1,'position',[h1.Position(1)-0.1,h1.Position(2),h1.Position(3),h1.Position(4)])
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
wheat_Ipsl_cm5a_lr_rcp45_prob_p1=zeros(360,720);   % 0-0.1 0.1-0.2 0.2-0.3 0.3-0.4 ....
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,1)=0.1;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,50)=0.2;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,100)=0.3;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,150)=0.4;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,200)=0.5;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,300)=0.6;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,400)=0.7;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,500)=0.8;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,600)=0.9;
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,700)=0.95;
for m=1:360
    for n=1:720
        if (wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.9)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=11+0.5;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.9 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.8 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=10-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.8 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.7 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=9-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.7 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.6 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=8-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.6 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.5 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=7-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.5 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.4 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=6-0.00001;                            
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.4 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.3 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=5-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.3 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.2 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=4-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.2 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.1 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=3-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.1 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0)
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=2-0.00001;
        elseif( wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<0 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=1;
        end
    end
end
h=worldmap([-89.5 89.5],[-180 180])
setm(h,'mapprojection','giso','frame','off','grid','off')
framem('FlineWidth',2,'FEdgeColor',[0.5,0.5,0.5]) 
set(findall(h,'Tag','PLabel'),'visible','off')
set(findall(h,'Tag','MLabel'),'visible','off')
load coastlines
plotm(coastlat,coastlon,'LineWidth', 0.5)
for m=1:360
    lat1(m)= -90+ 0.5*(m-1); 
end
for n=1:720
    lon1(n)= -180 + 0.5*(n-1);   
end
hold on
pcolorm(lat1,lon1,wheat_Ipsl_cm5a_lr_rcp45_prob_p1)
cmap = jet(11);
cmap = cmap(1:11,:);
cmap(1,:) = [1,1,1];
cmap(2,:) = [165 0 38]/255;
cmap(3,:) = [221 61 45]/255;
cmap(4,:) = [246 126 75]/255;
cmap(5,:) = [253 179 102]/255;
cmap(6,:) = [254 218 139]/255;


cmap(7,:) = [194 228 239]/255;
cmap(8,:) = [152 202 225]/255;
cmap(9,:)=[110 166 205]/255;
cmap(10,:)=[74 123 183]/255;
cmap(11,:)=[54 75 154]/255;
colormap(cmap);
%hcb=colorbar('eastoutside')
%set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
%set(hcb,'YTickLabel',{'Non-cropping region','(0 0.1]','(0.1,0.2]','(0.2,0.3]','(0.3,0.4]','(0.4,0.5]','(0.5,0.6]','(0.6,0.7]','(0.7,0.8]','(0.8,0.9]','(0.9,1]'},'Fontsize',11) 
%ttt=title(hcb,'\{ prob. in current \}');
%p1=get(ttt,'position');
%set(ttt,'Position',[p1(1)-380 p1(2) 0.1 ])
plotm(coastlat,coastlon,'LineWidth', 0.5);
t1=title('1. wheat under CA (+F+WD) practice')
set(gca,'fontsize',12)
%%
clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W
load('yield_prediction_CA_without_F_WD.mat');
%% wheat current
% 
f1=figure(1);
h1=subplot(2,3,2)
set(h1,'position',[h1.Position(1)-0.1-0.05,h1.Position(2),h1.Position(3),h1.Position(4)])
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
wheat_Ipsl_cm5a_lr_rcp45_prob_p1=zeros(360,720);   % 0-0.1 0.1-0.2 0.2-0.3 0.3-0.4 ....
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,1)=0.1;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,50)=0.2;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,100)=0.3;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,150)=0.4;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,200)=0.5;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,300)=0.6;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,400)=0.7;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,500)=0.8;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,600)=0.9;
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,700)=0.95;
for m=1:360
    for n=1:720
        if (wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.9)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=11+0.5;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.9 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.8 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=10-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.8 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.7 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=9-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.7 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.6 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=8-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.6 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.5 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=7-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.5 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.4 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=6-0.00001;                            
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.4 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.3 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=5-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.3 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.2 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=4-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.2 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.1 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=3-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.1 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0)
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=2-0.00001;
        elseif( wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<0 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=1;
        end
    end
end
h=worldmap([-89.5 89.5],[-180 180])
setm(h,'mapprojection','giso','frame','off','grid','off')
framem('FlineWidth',2,'FEdgeColor',[0.5,0.5,0.5]) 
set(findall(h,'Tag','PLabel'),'visible','off')
set(findall(h,'Tag','MLabel'),'visible','off')
load coastlines
plotm(coastlat,coastlon,'LineWidth', 0.5)
for m=1:360
    lat1(m)= -90+ 0.5*(m-1); 
end
for n=1:720
    lon1(n)= -180 + 0.5*(n-1);   
end
hold on
pcolorm(lat1,lon1,wheat_Ipsl_cm5a_lr_rcp45_prob_p1)
cmap = jet(11);
cmap = cmap(1:11,:);
cmap(1,:) = [1,1,1];
cmap(2,:) = [165 0 38]/255;
cmap(3,:) = [221 61 45]/255;
cmap(4,:) = [246 126 75]/255;
cmap(5,:) = [253 179 102]/255;
cmap(6,:) = [254 218 139]/255;


cmap(7,:) = [194 228 239]/255;
cmap(8,:) = [152 202 225]/255;
cmap(9,:)=[110 166 205]/255;
cmap(10,:)=[74 123 183]/255;
cmap(11,:)=[54 75 154]/255;
colormap(cmap);
%hcb=colorbar('eastoutside')
%set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
%set(hcb,'YTickLabel',{'Non-cropping region','(0 0.1]','(0.1,0.2]','(0.2,0.3]','(0.3,0.4]','(0.4,0.5]','(0.5,0.6]','(0.6,0.7]','(0.7,0.8]','(0.8,0.9]','(0.9,1]'},'Fontsize',11) 
%ttt=title(hcb,'\{ prob. in current \}');
%p1=get(ttt,'position');
%set(ttt,'Position',[p1(1)-380 p1(2) 0.1 ])
plotm(coastlat,coastlon,'LineWidth', 0.5);
t1=title('2. wheat under CA (-F-WD) practice')
set(gca,'fontsize',12)
%%
clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W
load('yield_prediction_NT_with_F_WD_R_without_SC.mat');
%% wheat current
% 
f1=figure(1);
h1=subplot(2,3,3)
set(h1,'position',[h1.Position(1)-0.1-0.05-0.05,h1.Position(2),h1.Position(3),h1.Position(4)])
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
wheat_Ipsl_cm5a_lr_rcp45_prob_p1=zeros(360,720);   % 0-0.1 0.1-0.2 0.2-0.3 0.3-0.4 ....
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,1)=0.1;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,50)=0.2;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,100)=0.3;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,150)=0.4;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,200)=0.5;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,300)=0.6;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,400)=0.7;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,500)=0.8;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,600)=0.9;
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,700)=0.95;
for m=1:360
    for n=1:720
        if (wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.9)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=11+0.5;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.9 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.8 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=10-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.8 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.7 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=9-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.7 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.6 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=8-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.6 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.5 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=7-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.5 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.4 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=6-0.00001;                            
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.4 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.3 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=5-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.3 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.2 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=4-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.2 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.1 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=3-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.1 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0)
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=2-0.00001;
        elseif( wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<0 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=1;
        end
    end
end
h=worldmap([-89.5 89.5],[-180 180])
setm(h,'mapprojection','giso','frame','off','grid','off')
framem('FlineWidth',2,'FEdgeColor',[0.5,0.5,0.5]) 
set(findall(h,'Tag','PLabel'),'visible','off')
set(findall(h,'Tag','MLabel'),'visible','off')
load coastlines
plotm(coastlat,coastlon,'LineWidth', 0.5)
for m=1:360
    lat1(m)= -90+ 0.5*(m-1); 
end
for n=1:720
    lon1(n)= -180 + 0.5*(n-1);   
end
hold on
pcolorm(lat1,lon1,wheat_Ipsl_cm5a_lr_rcp45_prob_p1)
cmap = jet(11);
cmap = cmap(1:11,:);
cmap(1,:) = [1,1,1];
cmap(2,:) = [165 0 38]/255;
cmap(3,:) = [221 61 45]/255;
cmap(4,:) = [246 126 75]/255;
cmap(5,:) = [253 179 102]/255;
cmap(6,:) = [254 218 139]/255;


cmap(7,:) = [194 228 239]/255;
cmap(8,:) = [152 202 225]/255;
cmap(9,:)=[110 166 205]/255;
cmap(10,:)=[74 123 183]/255;
cmap(11,:)=[54 75 154]/255;
colormap(cmap);
%hcb=colorbar('eastoutside')
%set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
%set(hcb,'YTickLabel',{'Non-cropping region','(0 0.1]','(0.1,0.2]','(0.2,0.3]','(0.3,0.4]','(0.4,0.5]','(0.5,0.6]','(0.6,0.7]','(0.7,0.8]','(0.8,0.9]','(0.9,1]'},'Fontsize',11) 
%ttt=title(hcb,'\{ prob. in current \}');
%p1=get(ttt,'position');
%set(ttt,'Position',[p1(1)-380 p1(2) 0.1 ])
plotm(coastlat,coastlon,'LineWidth', 0.5);
t1=title('3. wheat under NT+R-SC (+F+WD) practice')
set(gca,'fontsize',12)
%%
clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W
load('yield_prediction_NT_with_F_WD_without_R_SC.mat');
%% wheat current
% 
f1=figure(1);
h1=subplot(2,3,4)
set(h1,'position',[h1.Position(1)-0.1,h1.Position(2)+0.1,h1.Position(3),h1.Position(4)])
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
wheat_Ipsl_cm5a_lr_rcp45_prob_p1=zeros(360,720);   % 0-0.1 0.1-0.2 0.2-0.3 0.3-0.4 ....
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,1)=0.1;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,50)=0.2;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,100)=0.3;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,150)=0.4;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,200)=0.5;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,300)=0.6;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,400)=0.7;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,500)=0.8;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,600)=0.9;
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,700)=0.95;
for m=1:360
    for n=1:720
        if (wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.9)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=11+0.5;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.9 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.8 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=10-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.8 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.7 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=9-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.7 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.6 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=8-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.6 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.5 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=7-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.5 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.4 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=6-0.00001;                            
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.4 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.3 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=5-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.3 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.2 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=4-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.2 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.1 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=3-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.1 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0)
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=2-0.00001;
        elseif( wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<0 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=1;
        end
    end
end
h=worldmap([-89.5 89.5],[-180 180])
setm(h,'mapprojection','giso','frame','off','grid','off')
framem('FlineWidth',2,'FEdgeColor',[0.5,0.5,0.5]) 
set(findall(h,'Tag','PLabel'),'visible','off')
set(findall(h,'Tag','MLabel'),'visible','off')
load coastlines
plotm(coastlat,coastlon,'LineWidth', 0.5)
for m=1:360
    lat1(m)= -90+ 0.5*(m-1); 
end
for n=1:720
    lon1(n)= -180 + 0.5*(n-1);   
end
hold on
pcolorm(lat1,lon1,wheat_Ipsl_cm5a_lr_rcp45_prob_p1)
cmap = jet(11);
cmap = cmap(1:11,:);
cmap(1,:) = [1,1,1];
cmap(2,:) = [165 0 38]/255;
cmap(3,:) = [221 61 45]/255;
cmap(4,:) = [246 126 75]/255;
cmap(5,:) = [253 179 102]/255;
cmap(6,:) = [254 218 139]/255;


cmap(7,:) = [194 228 239]/255;
cmap(8,:) = [152 202 225]/255;
cmap(9,:)=[110 166 205]/255;
cmap(10,:)=[74 123 183]/255;
cmap(11,:)=[54 75 154]/255;
colormap(cmap);
%hcb=colorbar('eastoutside')
%set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
%set(hcb,'YTickLabel',{'Non-cropping region','(0 0.1]','(0.1,0.2]','(0.2,0.3]','(0.3,0.4]','(0.4,0.5]','(0.5,0.6]','(0.6,0.7]','(0.7,0.8]','(0.8,0.9]','(0.9,1]'},'Fontsize',11) 
%ttt=title(hcb,'\{ prob. in current \}');
%p1=get(ttt,'position');
%set(ttt,'Position',[p1(1)-380 p1(2) 0.1 ])
plotm(coastlat,coastlon,'LineWidth', 0.5);
t1=title('4. wheat under NT-R-SC (+F+WD) practice')
set(gca,'fontsize',12)
%%
clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W
load('yield_prediction_NT_without_F_WD_R_SC.mat');
%% wheat current
% 
f1=figure(1);
h1=subplot(2,3,5)
set(h1,'position',[h1.Position(1)-0.1-0.05,h1.Position(2)+0.1,h1.Position(3),h1.Position(4)])
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
wheat_Ipsl_cm5a_lr_rcp45_prob_p1=zeros(360,720);   % 0-0.1 0.1-0.2 0.2-0.3 0.3-0.4 ....
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,1)=0.1;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,50)=0.2;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,100)=0.3;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,150)=0.4;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,200)=0.5;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,300)=0.6;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,400)=0.7;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,500)=0.8;wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,600)=0.9;
wheat_Ipsl_cm5a_lr_rcp45_prob_p(1,700)=0.95;
for m=1:360
    for n=1:720
        if (wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.9)
            wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=11+0.5;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.9 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.8 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=10-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.8 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.7 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=9-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.7 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.6 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=8-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.6 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.5 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=7-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.5 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.4 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=6-0.00001;                            
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.4 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.3 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=5-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.3 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.2 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=4-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.2 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.1 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=3-0.00001;
        elseif(wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.1 && wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0)
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=2-0.00001;
        elseif( wheat_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<0 )
            	wheat_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=1;
        end
    end
end
h=worldmap([-89.5 89.5],[-180 180])
setm(h,'mapprojection','giso','frame','off','grid','off')
framem('FlineWidth',2,'FEdgeColor',[0.5,0.5,0.5]) 
set(findall(h,'Tag','PLabel'),'visible','off')
set(findall(h,'Tag','MLabel'),'visible','off')
load coastlines
plotm(coastlat,coastlon,'LineWidth', 0.5)
for m=1:360
    lat1(m)= -90+ 0.5*(m-1); 
end
for n=1:720
    lon1(n)= -180 + 0.5*(n-1);   
end
hold on
pcolorm(lat1,lon1,wheat_Ipsl_cm5a_lr_rcp45_prob_p1)
cmap = jet(11);
cmap = cmap(1:11,:);
cmap(1,:) = [1,1,1];
cmap(2,:) = [165 0 38]/255;
cmap(3,:) = [221 61 45]/255;
cmap(4,:) = [246 126 75]/255;
cmap(5,:) = [253 179 102]/255;
cmap(6,:) = [254 218 139]/255;


cmap(7,:) = [194 228 239]/255;
cmap(8,:) = [152 202 225]/255;
cmap(9,:)=[110 166 205]/255;
cmap(10,:)=[74 123 183]/255;
cmap(11,:)=[54 75 154]/255;
colormap(cmap);
%hcb=colorbar('eastoutside')
%set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
%set(hcb,'YTickLabel',{'Non-cropping region','(0 0.1]','(0.1,0.2]','(0.2,0.3]','(0.3,0.4]','(0.4,0.5]','(0.5,0.6]','(0.6,0.7]','(0.7,0.8]','(0.8,0.9]','(0.9,1]'},'Fontsize',11) 
%ttt=title(hcb,'\{ prob. in current \}');
%p1=get(ttt,'position');
%set(ttt,'Position',[p1(1)-380 p1(2) 0.1 ])
plotm(coastlat,coastlon,'LineWidth', 0.5);
t1=title('5. wheat under NT-R-SC (-F-WD) practice')
set(gca,'fontsize',12)
%%
hcb=colorbar('eastoutside')
set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
set(hcb,'YTickLabel',{'Non-cropping region','(0 0.1]','(0.1,0.2]','(0.2,0.3]','(0.3,0.4]','(0.4,0.5]','(0.5,0.6]','(0.6,0.7]','(0.7,0.8]','(0.8,0.9]','(0.9,1]'},'Fontsize',11) 
%
tt=title(hcb,'Prob. of yield increase in current');

set(hcb,'position',[0.7432    0.2254    0.0151    0.6614])
set(tt,'position',[63.4096  377.6730         0])
%%
clear all
clc