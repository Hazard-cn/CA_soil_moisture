clear all;clc

load('Climate_zones_360_720.mat')
%%
% Af 1	Am 2	As 3	Aw 4	Bwk 5	Bwh 6	Bsk 7	Bsh 8	Cfa 9	Cfb 10	Cfc 11	Csa 12	Csb 13	Ssc 14	Swa 15	Swb 16	Cwc 17	Dfa 18	Dfb 19
% Dfc 20	Dfd 21	Dsa 22	Dsb 23	Dsc 24	Dsd 25	Dwa 26	Dwb 27	Dwc 28	Dwd 29	EF 30	ET 31
% All B is arid climate, so 5 6 7 8 were classed as arid area, and others


pcolor(Cli_zone);shading flat
hcb=colorbar('eastoutside')
cmap = jet(32);
cmap = cmap(1:32,:);
cmap(1,:) = [1,1,1];
colormap(cmap)


set(hcb,'YTick',[0,1.5,2.3,3.3,4.3,5.25,6.2,7.2,8.15,9.1,10.1,11.1,12.1,13.1,14,15,16,17,17.9,18.9,19.9,20.8,21.8,22.8,23.7,24.7,25.7,26.6,27.6,28.6,29.6,30.5])
set(hcb,'YTickLabel',{'','Af','Am','As','Aw','BWk','BWh','BSk','BSh','Cfa','Cfb','Cfc','Csa','Csb','Ssc','Swa','Swb','Cwc','Dfa','Dfb','Dfc','Dfd','Dsa','Dsb','Dsc','Dsd','Dwa','Dwb','Dwc','Dwd','EF','ET'},'Fontsize',11) 
%%
ylabel('Latitude [°]','fontsize',14)
xlabel('Longitude [°]','fontsize',14)