PB=0.030102469136
Tmax=0.025658024691
Tmin=0.020886419753
Tave=0.022923456790
Crop=0.037962962963
WPCT= 0.004892592593
WPNT= 0.004141975309
FCT=  0.005535802469 
FNT=  0.006601234568 
RCT=  0.006580246914 
RNT=  0.004843209877
SCCT= 0.004870370370 
SCNT= 0.030935802469
ST=0.018450617284
IrrigationCT=0.023001234568
IrrigationNT= 0.018923456790 

Parameters=[Crop,SCNT,PB,Tmax,IrrigationCT,Tave,Tmin,IrrigationNT,ST,FNT,RCT,FCT,WPCT,SCCT,RNT,WPNT]
x=[1:16];
figure(1);clf

hcb=bar(x,Parameters)
ylabel('Variable importance (mean decrease in accuracy)')
xlim([0.5,16.5])

set(gca,'XTick',[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
set(gca,'XTickLabel',{'Crop','SCNT','PB','Tmax','IrrigationCT','Tave','Tmin','IrrigationNT','ST','FNT','RCT','FCT','WPCT','SCCT','RNT','WPNT'},'Fontsize',12) 
set(gca,'fontsize',12)
grid minor
