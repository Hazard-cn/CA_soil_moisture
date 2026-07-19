clear all;clc
load('crop_mask_new_360_720_std.mat')% only B M S W

%% maize 
% 

load('yield_prediction_CA_with_F_WD.mat');
%

f1=figure(1);clf
%set(gcf, 'PaperPositionMode', 'auto');
%set(gcf,'windowstyle','normal')
%set(gcf, 'resize', 'off');
%
%set(f1,'units','normalized','outerposition',[3.7453   -1.1843    0.7125    2.1926]);
h1=subplot(2,2,1)
%set(h1,'position',[0.200    0.1800    0.7    0.75])
%set(h1,'position',[0.200    0.56    0.6    0.5])
% Gfdl_esm2m_rcp45
maize_Ipsl_cm5a_lr_rcp45_prob_p=zeros(360,720);
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
                   
            maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=maize_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
end

%%figure(1)
%worldmap('World')
%load coastlines
%plotm(coastlat,coastlon)
%for m=1:360
%    lat1(m)= -90+ 0.5*(m-1); 
%end
%for n=1:720
%    lon1(n)= -180 + 0.5*(n-1);   
%end
%hold on
%pcolorm(lat1,lon1,maize_Ipsl_cm5a_lr_rcp45_prob_p);
%hold on
%plotm(coastlat,coastlon)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
maize_Ipsl_cm5a_lr_rcp45_prob_p1=zeros(360,720);   % 0-0.1 0.1-0.2 0.2-0.3 0.3-0.4 ....
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,7)=-0.1;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,8)=-0.075;
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,9)=-0.05;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,1)=-0.025;
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,2)=-0.01;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,3)=0;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,4)=0.01;
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,5)=0.025;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,6)=0.05;
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,10)=0.0751;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,11)=0.075;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,12)=-11;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,13)=-10;
for m=1:360
    for n=1:720
        if (maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.1)
            maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=11+0.5;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.1 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.075 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=10-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.075 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.05 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=9-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.05 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.025 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=8-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.025 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=7-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.025 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=6-0.00001;                            
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.025 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.05 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=5-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.05 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.075 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=4-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.075 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.1 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=3-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.1 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-1)
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=2-0.00001;
        elseif( maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-1 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=1;
        end
    end
end





h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off')
%framem('FlineWidth',2,'FEdgeColor','black')
%%load coast 
set(findall(h,'Tag','PLabel'),'visible','off')
set(findall(h,'Tag','MLabel'),'visible','off')


load coastlines
plotm(coastlat,coastlon)
for m=1:360
    lat1(m)= -90+ 0.5*(m-1); 
end
for n=1:720
    lon1(n)= -180 + 0.5*(n-1);   
end
hold on
pcolorm(lat1,lon1,maize_Ipsl_cm5a_lr_rcp45_prob_p1)
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
hcb=colorbar('eastoutside')
set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
set(hcb,'YTickLabel',{'Non-cropping region','<=-0.1','(-0.1,-0.075]','(-0.075,-0.05]','(-0.05,-0.025]','(-0.025,0]','(0,0.025]','(0.025,0.05]','(0.05,0.075]','(0.075,0.1]','>0.1'},'Fontsize',12) 
%ttt=title(hcb,'\{ prob. \}');
%p1=get(ttt,'position');
%set(ttt,'Position',[p1(1)-380 p1(2) 0.1 ])
plotm(coastlat,coastlon);
%tttt=title('Probability of the increase of maize productivity under CA practice','Fontsize',16)
%p2=get(tttt,'position');
%set(tttt,'Position',[p2(1) p2(2)+0.25e6 0.1 ])
%%
t1=title('(a). Change of probability of yield gain from CA (+F+WD) - maize')
tp1=get(t1,'position')
set(t1,'position',[tp1(1)+1e6,tp1(2)+5e5,tp1(3)])

hh1=annotation('line',[0.16    0.396],[0.584    0.584])
set(hh1,'linewidth',1)

hh2=annotation('line',[0.16    0.396],[0.927    0.927])
set(hh2,'linewidth',1)

hh3=annotation('line',[0.16    0.16],[0.584    0.927])
set(hh3,'linewidth',1)

hh4=annotation('line',[0.396    0.396],[0.584    0.927])
set(hh4,'linewidth',1)
set(gca,'fontsize',12)

%%
% 
clear all;clc
load('crop_mask_new_360_720_std.mat')
load('yield_prediction_CA_without_F_WD.mat');

f1=figure(1);
%set(gcf, 'PaperPositionMode', 'auto');
%set(gcf,'windowstyle','normal')
%set(gcf, 'resize', 'off');
%
%set(f1,'units','normalized','outerposition',[3.7453   -1.1843    0.7125    2.1926]);
h2=subplot(2,2,2)

%set(h1,'position',[0.200    0.1800    0.7    0.75])
%set(h1,'position',[0.200    0.56    0.6    0.5])
% Gfdl_esm2m_rcp45
maize_Ipsl_cm5a_lr_rcp45_prob_p=zeros(360,720);
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=maize_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
end

%%figure(1)
%worldmap('World')
%load coastlines
%plotm(coastlat,coastlon)
%for m=1:360
%    lat1(m)= -90+ 0.5*(m-1); 
%end
%for n=1:720
%    lon1(n)= -180 + 0.5*(n-1);   
%end
%hold on
%pcolorm(lat1,lon1,maize_Ipsl_cm5a_lr_rcp45_prob_p);
%hold on
%plotm(coastlat,coastlon)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
maize_Ipsl_cm5a_lr_rcp45_prob_p1=zeros(360,720);   % 0-0.1 0.1-0.2 0.2-0.3 0.3-0.4 ....
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,7)=-0.1;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,8)=-0.075;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,9)=-0.05;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,1)=-0.025;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,2)=-0.01;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,3)=0;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,4)=0.01;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,5)=0.025;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,6)=0.05;
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,10)=0.0751;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,11)=0.075;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,12)=-11;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,13)=-10;
for m=1:360
    for n=1:720
        if (maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.1)
            maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=11+0.5;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.1 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.075 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=10-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.075 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.05 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=9-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.05 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.025 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=8-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.025 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=7-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.025 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=6-0.00001;                            
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.025 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.05 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=5-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.05 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.075 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=4-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.075 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.1 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=3-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.1 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-1)
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=2-0.00001;
        elseif( maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-1 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=1;
        end
    end
end





h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off')
%framem('FlineWidth',2,'FEdgeColor','black')
%%load coast 
set(findall(h,'Tag','PLabel'),'visible','off')
set(findall(h,'Tag','MLabel'),'visible','off')


load coastlines
plotm(coastlat,coastlon)
for m=1:360
    lat1(m)= -90+ 0.5*(m-1); 
end
for n=1:720
    lon1(n)= -180 + 0.5*(n-1);   
end
hold on
pcolorm(lat1,lon1,maize_Ipsl_cm5a_lr_rcp45_prob_p1)
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
hcb=colorbar('eastoutside')
set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
set(hcb,'YTickLabel',{'Non-cropping region','<=-0.1','(-0.1,-0.075]','(-0.075,-0.05]','(-0.05,-0.025]','(-0.025,0]','(0,0.025]','(0.025,0.05]','(0.05,0.075]','(0.075,0.1]','>0.1'},'Fontsize',12) 
%ttt=title(hcb,'\{ prob. \}');
%p1=get(ttt,'position');
%set(ttt,'Position',[p1(1)-380 p1(2) 0.1 ])
plotm(coastlat,coastlon);
%tttt=title('Probability of the increase of maize productivity under CA practice','Fontsize',16)
%p2=get(tttt,'position');
%set(tttt,'Position',[p2(1) p2(2)+0.25e6 0.1 ])
t2=title('(b). Change of probability of yield gain from CA (-F-WD) - maize')
tp2=get(t2,'position')
set(t2,'position',[tp2(1)+1e6,tp2(2)+5e5,tp2(3)])

hh1=annotation('line',[0.836    0.6],[0.584    0.584])
set(hh1,'linewidth',1)

hh2=annotation('line',[0.836    0.6],[0.927    0.927])
set(hh2,'linewidth',1)

hh3=annotation('line',[0.836    0.836],[0.584    0.927])
set(hh3,'linewidth',1)

hh4=annotation('line',[0.6    0.6],[0.584    0.927])
set(hh4,'linewidth',1)
set(gca,'fontsize',12)

%%
% 
clear all;clc
load('crop_mask_new_360_720_std.mat')
load('yield_prediction_NT_with_F_WD_R_without_SC.mat');
%

f1=figure(1);
%set(gcf, 'PaperPositionMode', 'auto');
%set(gcf,'windowstyle','normal')
%set(gcf, 'resize', 'off');
%
%set(f1,'units','normalized','outerposition',[3.7453   -1.1843    0.7125    2.1926]);
h3=subplot(2,2,3)

%set(h1,'position',[0.200    0.1800    0.7    0.75])
%set(h1,'position',[0.200    0.56    0.6    0.5])
% Gfdl_esm2m_rcp45
maize_Ipsl_cm5a_lr_rcp45_prob_p=zeros(360,720);
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=maize_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
end

%%figure(1)
%worldmap('World')
%load coastlines
%plotm(coastlat,coastlon)
%for m=1:360
%    lat1(m)= -90+ 0.5*(m-1); 
%end
%for n=1:720
%    lon1(n)= -180 + 0.5*(n-1);   
%end
%hold on
%pcolorm(lat1,lon1,maize_Ipsl_cm5a_lr_rcp45_prob_p);
%hold on
%plotm(coastlat,coastlon)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
maize_Ipsl_cm5a_lr_rcp45_prob_p1=zeros(360,720);   % 0-0.1 0.1-0.2 0.2-0.3 0.3-0.4 ....
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,7)=-0.1;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,8)=-0.075;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,9)=-0.05;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,1)=-0.025;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,2)=-0.01;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,3)=0;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,4)=0.01;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,5)=0.025;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,6)=0.05;
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,10)=0.0751;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,11)=0.075;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,12)=-11;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,13)=-10;
for m=1:360
    for n=1:720
        if (maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.1)
            maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=11+0.5;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.1 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.075 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=10-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.075 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.05 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=9-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.05 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.025 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=8-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.025 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=7-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.025 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=6-0.00001;                            
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.025 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.05 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=5-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.05 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.075 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=4-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.075 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.1 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=3-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.1 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-1)
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=2-0.00001;
        elseif( maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-1 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=1;
        end
    end
end






h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off')
%framem('FlineWidth',2,'FEdgeColor','black')
%%load coast 
set(findall(h,'Tag','PLabel'),'visible','off')
set(findall(h,'Tag','MLabel'),'visible','off')


load coastlines
plotm(coastlat,coastlon)
for m=1:360
    lat1(m)= -90+ 0.5*(m-1); 
end
for n=1:720
    lon1(n)= -180 + 0.5*(n-1);   
end
hold on
pcolorm(lat1,lon1,maize_Ipsl_cm5a_lr_rcp45_prob_p1)
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
hcb=colorbar('eastoutside')
set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
set(hcb,'YTickLabel',{'Non-cropping region','<=-0.1','(-0.1,-0.075]','(-0.075,-0.05]','(-0.05,-0.025]','(-0.025,0]','(0,0.025]','(0.025,0.05]','(0.05,0.075]','(0.075,0.1]','>0.1'},'Fontsize',12) 
%ttt=title(hcb,'\{ prob. \}');
%p1=get(ttt,'position');
%set(ttt,'Position',[p1(1)-380 p1(2) 0.1 ])
plotm(coastlat,coastlon);
%tttt=title('Probability of the increase of maize productivity under CA practice','Fontsize',16)
%p2=get(tttt,'position');
%set(tttt,'Position',[p2(1) p2(2)+0.25e6 0.1 ])
t3=title('(c). Change of probability of yield gain from NT+R-SC(+F+WD) - maize')
tp3=get(t3,'position')
set(t3,'position',[tp3(1)+5e5,tp3(2)+5e5,tp3(3)])
%
hh1=annotation('line',[0.16    0.396],[0.11   0.11])
set(hh1,'linewidth',1)

hh2=annotation('line',[0.16    0.396],[0.453    0.453])
set(hh2,'linewidth',1)

hh3=annotation('line',[0.16    0.16],[0.11    0.453])
set(hh3,'linewidth',1)

hh4=annotation('line',[0.396    0.396],[0.11    0.453])
set(hh4,'linewidth',1)
set(gca,'fontsize',12)
%%
% 
clear all;clc
load('crop_mask_new_360_720_std.mat')
load('yield_prediction_NT_without_F_WD_R_SC.mat');

f1=figure(1);
%set(gcf, 'PaperPositionMode', 'auto');
%set(gcf,'windowstyle','normal')
%set(gcf, 'resize', 'off');
%
%set(f1,'units','normalized','outerposition',[3.7453   -1.1843    0.7125    2.1926]);
h1=subplot(2,2,4)


%set(h1,'position',[0.200    0.1800    0.7    0.75])
%set(h1,'position',[0.200    0.56    0.6    0.5])
% Gfdl_esm2m_rcp45
maize_Ipsl_cm5a_lr_rcp45_prob_p=zeros(360,720);
for m=1:360
    for n=1:720
        if (maize_mask2(m,n)== 0 || maize_Ipsl_cm5a_lr_rcp45_PB(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tave(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmax(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_Tmin(m,n) == -99 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n)==0 || maize_Ipsl_cm5a_lr_rcp45_ST_original(m,n) == 13)
            maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=-1;
        else
            maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)=maize_Ipsl_cm5a_lr_rcp45_future_prob_positive(m,n)-maize_Ipsl_cm5a_lr_rcp45_prob_positive(m,n);
        end
    end
end

%%figure(1)
%worldmap('World')
%load coastlines
%plotm(coastlat,coastlon)
%for m=1:360
%    lat1(m)= -90+ 0.5*(m-1); 
%end
%for n=1:720
%    lon1(n)= -180 + 0.5*(n-1);   
%end
%hold on
%pcolorm(lat1,lon1,maize_Ipsl_cm5a_lr_rcp45_prob_p);
%hold on
%plotm(coastlat,coastlon)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
maize_Ipsl_cm5a_lr_rcp45_prob_p1=zeros(360,720);   % 0-0.1 0.1-0.2 0.2-0.3 0.3-0.4 ....
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,7)=-0.1;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,8)=-0.075;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,9)=-0.05;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,1)=-0.025;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,2)=-0.01;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,3)=0;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,4)=0.01;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,5)=0.025;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,6)=0.05;
maize_Ipsl_cm5a_lr_rcp45_prob_p(1,10)=0.0751;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,11)=0.075;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,12)=-11;maize_Ipsl_cm5a_lr_rcp45_prob_p(1,13)=-10;
for m=1:360
    for n=1:720
        if (maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.1)
            maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=11+0.5;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.1 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.075 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=10-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.075 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.05 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=9-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.05 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0.025 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=8-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0.025 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>0 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=7-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=0 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.025 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=6-0.00001;                            
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.025 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.05 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=5-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.05 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.075 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=4-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.075 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-0.1 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=3-0.00001;
        elseif(maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-0.1 && maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)>-1)
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=2-0.00001;
        elseif( maize_Ipsl_cm5a_lr_rcp45_prob_p(m,n)<=-1 )
            	maize_Ipsl_cm5a_lr_rcp45_prob_p1(m,n)=1;
        end
    end
end






h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off')
%framem('FlineWidth',2,'FEdgeColor','black')
%%load coast 
set(findall(h,'Tag','PLabel'),'visible','off')
set(findall(h,'Tag','MLabel'),'visible','off')


load coastlines
plotm(coastlat,coastlon)
for m=1:360
    lat1(m)= -90+ 0.5*(m-1); 
end
for n=1:720
    lon1(n)= -180 + 0.5*(n-1);   
end
hold on
pcolorm(lat1,lon1,maize_Ipsl_cm5a_lr_rcp45_prob_p1)
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
hcb=colorbar('eastoutside')
set(hcb,'YTick',[1.5,2.4,3.4,4.3,5.2,6.2,7.1,8.1,9,10,11])
set(hcb,'YTickLabel',{'Non-cropping region','<=-0.1','(-0.1,-0.075]','(-0.075,-0.05]','(-0.05,-0.025]','(-0.025,0]','(0,0.025]','(0.025,0.05]','(0.05,0.075]','(0.075,0.1]','>0.1'},'Fontsize',12) 
%ttt=title(hcb,'\{ prob. \}');
%p1=get(ttt,'position');
%set(ttt,'Position',[p1(1)-380 p1(2) 0.1 ])
plotm(coastlat,coastlon);
%tttt=title('Probability of the increase of maize productivity under CA practice','Fontsize',16)
%p2=get(tttt,'position');
%set(tttt,'Position',[p2(1) p2(2)+0.25e6 0.1 ])
%
t4=title('(d). Change of probability of yield gain from NT-R-SC(-F-WD) - maize')
tp4=get(t4,'position')
set(t4,'position',[tp4(1)+5e5,tp4(2)+5e5,tp4(3)])

%%
hh1=annotation('line',[0.836    0.6],[0.11   0.11])
set(hh1,'linewidth',1)

hh2=annotation('line',[0.836    0.6],[0.453    0.453])
set(hh2,'linewidth',1)

hh3=annotation('line',[0.836     0.835 ],[0.11    0.453])
set(hh3,'linewidth',1)

hh4=annotation('line',[0.6   0.6],[0.11   0.453])
set(hh4,'linewidth',1)
set(gca,'fontsize',12)