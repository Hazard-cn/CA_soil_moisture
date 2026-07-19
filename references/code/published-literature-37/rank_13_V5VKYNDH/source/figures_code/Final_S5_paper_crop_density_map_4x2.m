load('crop_mask_new_360_720_std.mat')


figure(1);clf
% barley
subplot(8,8,[1,2,3,4,9,10,11,12,17,18,19,20,25,26,27,28])
h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off') 
%load coast 
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
pcolorm(lat1,lon1,barley_mask4)
hcb=colorbar('eastoutside')
cmap = parula(1e7);cmap = cmap(1:1e7,:);cmap(1,:) = [1,1,1];colormap(cmap);caxis([0,0.2*max(max(barley_mask4))])
set(hcb, 'YTickLabel', cellstr(num2str(reshape(get(hcb, 'YTick'),[],1),'%0.0f')) )
plotm(coastlat,coastlon)
title('(a). barley')
set(gca,'fontsize',12)

% cotton
subplot(8,8,[5,6,7,8,13,14,15,16,21,22,23,24,29,30,31,32])
h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off') 
%load coast 
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
pcolorm(lat1,lon1,cotton_mask4)
hcb=colorbar('eastoutside')
cmap = parula(1e7);cmap = cmap(1:1e7,:);cmap(1,:) = [1,1,1];colormap(cmap);caxis([0,0.2*max(max(cotton_mask4))])
set(hcb, 'YTickLabel', cellstr(num2str(reshape(get(hcb, 'YTick'),[],1),'%0.0f')) )
plotm(coastlat,coastlon)
title('(b). cotton')
set(gca,'fontsize',12)


% maize
subplot(8,8,[33,34,35,36,41,42,43,44,49,50,51,52,57,58,59,60])
h=worldmap('World')


setm(h,'mapprojection','giso','frame','off','grid','off') 
%load coast 
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
pcolorm(lat1,lon1,maize_mask4)
hcb=colorbar('eastoutside')
cmap = parula(1e7);cmap = cmap(1:1e7,:);cmap(1,:) = [1,1,1];colormap(cmap);caxis([0,0.2*max(max(maize_mask4))])
set(hcb, 'YTickLabel', cellstr(num2str(reshape(get(hcb, 'YTick'),[],1),'%0.0f')) )
plotm(coastlat,coastlon)
title('(c). maize')
set(gca,'fontsize',12)

% rice
subplot(8,8,[37,38,39,40,45,46,47,48,53,54,55,56,61,62,63,64])
h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off') 
%load coast 
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
pcolorm(lat1,lon1,rice_mask4)
hcb=colorbar('eastoutside')
cmap = parula(1e7);cmap = cmap(1:1e7,:);cmap(1,:) = [1,1,1];colormap(cmap);caxis([0,0.2*max(max(rice_mask4))])
set(hcb, 'YTickLabel', cellstr(num2str(reshape(get(hcb, 'YTick'),[],1),'%0.0f')) )
plotm(coastlat,coastlon)
title('(d). rice')
set(gca,'fontsize',12)

saveas(gca,'0_crop_density_map_part_1.png')
saveas(gca,'0_crop_density_map_part_1.tif')
%saveas(gca,'0_crop_density_map_part_1.fig')




figure(1);clf
% sorghum
subplot(8,8,[1,2,3,4,9,10,11,12,17,18,19,20,25,26,27,28])
h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off') 
%load coast 
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
pcolorm(lat1,lon1,sorghum_mask4)
hcb=colorbar('eastoutside')
cmap = parula(1e7);cmap = cmap(1:1e7,:);cmap(1,:) = [1,1,1];colormap(cmap);caxis([0,0.2*max(max(sorghum_mask4))])
set(hcb, 'YTickLabel', cellstr(num2str(reshape(get(hcb, 'YTick'),[],1),'%0.0f')) )
plotm(coastlat,coastlon)
title('(e). sorghum')
set(gca,'fontsize',12)

% soybean
subplot(8,8,[5,6,7,8,13,14,15,16,21,22,23,24,29,30,31,32])
h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off') 
%load coast 
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
pcolorm(lat1,lon1,soybean_mask4)
hcb=colorbar('eastoutside')
cmap = parula(1e7);cmap = cmap(1:1e7,:);cmap(1,:) = [1,1,1];colormap(cmap);caxis([0,0.2*max(max(soybean_mask4))])
set(hcb, 'YTickLabel', cellstr(num2str(reshape(get(hcb, 'YTick'),[],1),'%0.0f')) )
plotm(coastlat,coastlon)
title('(f). soybean')
set(gca,'fontsize',12)


% sunflower
subplot(8,8,[33,34,35,36,41,42,43,44,49,50,51,52,57,58,59,60])
h=worldmap('World')


setm(h,'mapprojection','giso','frame','off','grid','off') 
%load coast 
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
pcolorm(lat1,lon1,sunflower_mask4)
hcb=colorbar('eastoutside')
cmap = parula(1e7);cmap = cmap(1:1e7,:);cmap(1,:) = [1,1,1];colormap(cmap);caxis([0,0.2*max(max(sunflower_mask4))])
set(hcb, 'YTickLabel', cellstr(num2str(reshape(get(hcb, 'YTick'),[],1),'%0.0f')) )
plotm(coastlat,coastlon)
title('(g). sunflower')
set(gca,'fontsize',12)

% wheat
subplot(8,8,[37,38,39,40,45,46,47,48,53,54,55,56,61,62,63,64])
h=worldmap('World')
setm(h,'mapprojection','giso','frame','off','grid','off') 
%load coast 
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
pcolorm(lat1,lon1,wheat_mask4)
hcb=colorbar('eastoutside')
cmap = parula(1e7);cmap = cmap(1:1e7,:);cmap(1,:) = [1,1,1];colormap(cmap);caxis([0,0.2*max(max(wheat_mask4))])
set(hcb, 'YTickLabel', cellstr(num2str(reshape(get(hcb, 'YTick'),[],1),'%0.0f')) )
plotm(coastlat,coastlon)
title('(h). wheat')
set(gca,'fontsize',12)

saveas(gca,'0_crop_density_map_part_2.png')
saveas(gca,'0_crop_density_map_part_2.tif')
%saveas(gca,'0_crop_density_map_part_2.fig')