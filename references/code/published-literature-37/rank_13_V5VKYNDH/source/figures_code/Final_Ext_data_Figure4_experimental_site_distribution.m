
clear all;clc
%load('Location and crop.mat')
% map

figure(1);clf

distribution = readtable('Location and crop ranked.xlsx');

distribution.Crop = categorical(distribution.Crop);
%distribution.Crop_code = categorical(distribution.Crop_code);

colm=colormap(parula(10))

Colmatrix=colm(1,:);
for i=1:length(distribution.Latitude)
   Colmatrix(i,:)=[1,0,0];
end

gb = geobubble(distribution,'Latitude','Longitude','Basemap','darkwater','SizeVariable','Number_of_observations','ColorVariable','Crop');
geolimits([-60 80],[-160 160])
title 'Experimental site distribution for different crops species';
%gb.SizeLegendTitle = 'Maximum Height';
colormap(parula(10))

set(gca,'fontsize',12)

legend({'Spring barley','Winter barley','Cotton','Maize','Rice','Sorghum','Soybean','Sunflower','Spring wheat','Winter wheat'})


%%

%clear all;clc
%load('Location and crop ranked by crop species.mat')

%figure(2);clf
%A=ones(size(Latitude))*30;

%geoscatter(Latitude,Longitude,A,Crop_code,'o','filled')

%colormap(parula(10))
%legend({'Spring barley','Winter barley','Cotton','Maize','Rice','Sorghum','Soybean','Sunflower','Spring wheat','Winter wheat'})