# Compare classification ability for different packages
{
  #### load package
  library(randomForest)
  library(party)
  library(partykit)
  library(quantregForest)
  library(quantreg)
  library(lme4)
  library(lmerTest)
  library(tidyverse)
  library(caret)
  library(rfUtilities)
  require(MuMIn)
  library(rfUtilities)
  library(ranger)
  library(metafor)
  library(devtools)
  library(dplyr)
  library(crunch)
  library(ggplot2)
  #library(randomForestExplainer)
  #library(ranger)
}




#################################33
################################
##############################
######################3
##################





#par(pty="m")

###################################################################################
#####################################
##################


{
  ### Load data and pre-processing
  test<-read.csv("PhD data.csv")
  ### response parameter
  test$Change <-as.factor(as.character(test$Change))
  #### numerical predictor
  test$PB <-as.numeric(as.character(test$PB))
  test$Tmax <-as.numeric(as.character(test$Tmax))
  test$Tmin <-as.numeric(as.character(test$Tmin))
  test$Tave <-as.numeric(as.character(test$Tave))
  
  ##### character parameter
  test$RCT <-as.factor(as.character(test$RCT))
  test$RNT <-as.factor(as.character(test$RNT))
  test$SCCT <-as.factor(as.character(test$SCCT))
  test$SCNT <-as.factor(as.character(test$SCNT))
  test$WPCT <-as.factor(as.character(test$WPCT))
  test$WPNT <-as.factor(as.character(test$WPNT))
  test$FCT <-as.factor(as.character(test$FCT))
  test$FNT <-as.factor(as.character(test$FNT))
  test$ST <-as.factor(as.character(test$ST))
  test$IrrigationCT<-as.factor(as.character(test$IrrigationCT))
  test$IrrigationNT<-as.factor(as.character(test$IrrigationNT))
  
  test$Crop<-as.factor(as.character(test$Crop))
  
}

#test <-filter(test,test$Longitude <= -30)
#test <-filter(test,test$Longitude >= -180)
#test <-filter(test,test$Latitude >= 0)
#test <-filter(test,test$Change >= -1)
#test <-filter(test,test$Crop == "Maize")
#test <-filter(test,test$PB <= 0)
#test <-filter(test,test$Taverage >= 20)
#test <-filter(test,test$F == 1)
#test <-filter(test,test$ST == 2)
#test <-filter(test,test$R == 1)
#test <-filter(test,test$RM == 2)
#test <-filter(test,test$WDPT == 1)
#plot(test$Change)
#plot(test$PB,test$Change)
#plot(test$Taverage,test$Change)
#plot(test$Tmax,test$Change)
#plot(test$Tmin,test$Change)


set.seed(3)

### Model testing  -  cross validation


#### Dataset splitting, keep the data from the same data as testing sample


n<-nrow(test)

kk<-n
mmk<-floor(n/kk)

#pred_qrf<-matrix(0, nrow =kk, ncol = mmk)
#test_y_qrf<-matrix(0, nrow =kk, ncol = mmk)

#E_predict1<-matrix(0, nrow =kk, ncol = mmk)
#E_predict<-0

#rmse_qrf_final111<-matrix(0, nrow =kk, ncol = mmk)
#rmse_qrf_final222<-matrix(0, nrow =kk, ncol = mmk)

#pred_qrf_2<-matrix(0, nrow =kk, ncol = mmk)
#test_y_qrf_2<-matrix(0, nrow = kk, ncol = mmk )


pred_qrf<-matrix(0, nrow =n, ncol = 1)
test_y_qrf<-matrix(0, nrow =n, ncol = 1)

E_predict1<-matrix(0, nrow =n, ncol = 1)
E_predict<-0

rmse_qrf_final111<-matrix(0, nrow =n, ncol = 1)
rmse_qrf_final222<-matrix(0, nrow =n, ncol = 1)

pred_qrf_2<-matrix(0, nrow =n, ncol = 1)
test_y_qrf_2<-matrix(0, nrow = n, ncol = 1 )

E<-0
count_total<-0

qrf_st<-matrix(0, nrow =n, ncol = 1)
qrf_pb<-matrix(0, nrow =n, ncol = 1)
qrf_tave<-matrix(0, nrow =n, ncol = 1)
qrf_tmax<-matrix(0, nrow =n, ncol = 1)
qrf_tmin<-matrix(0, nrow =n, ncol = 1)


qrf_fct<-matrix(0, nrow =n, ncol = 1)
qrf_fnt<-matrix(0, nrow =n, ncol = 1)
qrf_crop<-matrix(0, nrow =n, ncol = 1)
qrf_scct<-matrix(0, nrow =n, ncol = 1)
qrf_scnt<-matrix(0, nrow =n, ncol = 1)
qrf_rct<-matrix(0, nrow =n, ncol = 1)
qrf_rnt<-matrix(0, nrow =n, ncol = 1)
qrf_wpct<-matrix(0, nrow =n, ncol = 1)
qrf_wpnt<-matrix(0, nrow =n, ncol = 1)

qrf_irrigationct<-matrix(0, nrow =n, ncol = 1)
qrf_irrigationnt<-matrix(0, nrow =n, ncol = 1)

qrf_lat<-matrix(0, nrow =n, ncol = 1)
qrf_lon<-matrix(0, nrow =n, ncol = 1)
###### Splitting training data and testing data
##    10 k fold

for(k in 1:kk){
  
  set.seed(3)
  if(k==1){
    datatrain<-0
    datatest<-0
    datatrain<-test[2:n,]
    datatest<-test[1,]
  }
  if(k==n){
    # set.seed(3)
    datatrain<-0
    datatest<-0
    datatrain<-test[1:(n-1),]
    datatest<-test[n,]
  }
  if(k>1 && k<n){
    # set.seed(3)
    datatrain<-0
    datatest<-0
    datatrain1<-test[1:(k-1),]
    datatrain2<-test[(k+1):n,]
    datatrain<-rbind(datatrain1,datatrain2)
    
    datatest<-test[k,]
    #cat(datatest[1:10,2])
    
  }
  
  cat("\n kn is : \n",k,"\n")
  
  #datatrainxy <-0
  #datatrain_bias_correction <- 0
  #indextrain <-0
  #quan<-0.5
  #indextrain <- sample(1:(n-mmk-1),round(quan*(n-mmk)),replace=FALSE)
  #datatrainxy <- datatrain[indextrain,]
  #datatrain_bias_correction <- datatrain[-indextrain,]
  
  
  set.seed(3)
  ###### Quantile regression forest
  
  #rf<-randomForest(x=datatrainxy[,3:20],y=datatrainxy[,2],proximity = TRUE)
  
  mtree1<-500
  mtry1<-3
  
  #qrf <- cforest(Change~PB+Tmax+Taverage+Crop+WDPT+F+R+RM+ST+Study.Duration+Yield.data.year+Latitude+Longitude,data=datatrain,weights=datatrain$ï..Seq,ntree = 500,mtry=5) #,weight=test$ï..Seq
  qrf <- randomForest(Change~PB+Tmax+Tmin+Tave+WPCT+WPNT+FCT+FNT+RCT+RNT+SCCT+SCNT+ST+IrrigationCT+IrrigationNT,data=datatrain,ntree = mtree1,mtry=mtry1,proximity=TRUE,keep.inbag=T) #,,case.weights = abs(datatrain$ï..Seq_big)
  
  
  pred222 <- predict(qrf, newdata = datatest[,-2],type = "prob")
  
  
  
  
  
  pred1<-pred222[,2]
  #qrf <- quantregForest(x=datatrainxy[,3:12],y=datatrainxy[,2],keep.inbag = TRUE,mtry=14,ntree=300,nodesize=10,norm.votes=TRUE,weight=test$ï..Seq,weights=test$ï..Seq) #,weight=test$ï..Seq
  
  #pred1<-predict(qrf,datatest[,3:12],what = 0.5,allow.new.levels = TRUE)
  
  
  
  
  for(hhh in 1:length(pred1)){
    count_total<-count_total+1
    pred_qrf[count_total]<-as.numeric(as.character(pred1[hhh]))
    
    test_y_qrf[count_total]<-as.numeric(as.character(datatest$Change[hhh]))
    
    
    qrf_crop[count_total]<-as.factor(as.character(datatest$Crop[hhh]))
    qrf_pb[count_total]<-datatest$PB[hhh]
    qrf_tave[count_total]<-datatest$Tave[hhh]
    qrf_st[count_total]<-as.factor(as.character(datatest$ST[hhh]))
    qrf_tmax[count_total]<-datatest$Tmax[hhh]
    qrf_tmin[count_total]<-datatest$Tmin[hhh]
    
    qrf_fct[count_total]<-as.factor(as.character(datatest$FCT[hhh]))
    qrf_fnt[count_total]<-as.factor(as.character(datatest$FNT[hhh]))
    
    qrf_wpct[count_total]<-as.factor(as.character(datatest$WPCT[hhh]))
    qrf_wpnt[count_total]<-as.factor(as.character(datatest$WPNT[hhh]))
    
    qrf_rct[count_total]<-as.factor(as.character(datatest$RCT[hhh]))
    qrf_rnt[count_total]<-as.factor(as.character(datatest$RNT[hhh]))
    
    qrf_scct[count_total]<-as.factor(as.character(datatest$SCCT[hhh]))
    qrf_scnt[count_total]<-as.factor(as.character(datatest$SCNT[hhh]))
    
    qrf_irrigationct[count_total]<-as.factor(as.character(datatest$IrrigationCT[hhh]))
    qrf_irrigationnt[count_total]<-as.factor(as.character(datatest$IrrigationNT[hhh]))
    
    #qrf_lat[count_total]<-datatest$Latitude[hhh]
    #qrf_lon[count_total]<-datatest$Longitude[hhh]
  }
  
  
  
  
}

result_pred<-matrix(0, nrow =n, ncol = 14)
result_pred<-cbind(pred_qrf,qrf_pb,qrf_tave,qrf_tmax,qrf_tmin,qrf_st,qrf_fct,qrf_fnt,qrf_wpct,qrf_wpnt,qrf_rct,qrf_rnt,qrf_scct,qrf_scnt,qrf_irrigationct,qrf_irrigationnt,qrf_lat,qrf_lon,test_y_qrf)
colnames(result_pred)<-c("yield","pb","tave","tmax","tmin","st","fct","fnt","wpct","wpnt","rct","rnt","scct","scnt","irrigationct","irrigationnt","lat","lon","observation")
result_pred<-data.frame(result_pred)
#result_pred
#result_pred<-filter(result_pred,result_pred$yield!= 0 & result_pred$pb!= 0 & result_pred$tave!= 0 & result_pred$tmax!= 0 & result_pred$tmin!= 0 & result_pred$crop!= 0 & result_pred$st!= 0 & result_pred$f!= 0 & result_pred$r!= 0 & result_pred$rm!= 0 & result_pred$WDPT != 0)
#result_pred
#result_pred<-filter(result_pred,result_pred$f == 1)
yield_pred<-result_pred$yield
leng_total<-length(yield_pred)

predict_qrf_temp<-matrix(0, nrow = leng_total, ncol = 1)
y_qrf_temp<-matrix(0, nrow = leng_total, ncol = 1)
predict_qrf_temp<-result_pred$yield
y_qrf_temp<-result_pred$observation



count1111<-length(y_qrf_temp)
count11<-0
for(i in 1:count1111){
  
  if(y_qrf_temp[i]==1 && predict_qrf_temp[i]>=0.5  ){
    count11=count11+1
  }
  if(y_qrf_temp[i]==0 && predict_qrf_temp[i]<0.5 ){
    count11=count11+1
  }
}
accuracy<-count11/count1111
cat("\n qrf accuracy is : \n",accuracy,"\n")

library(pROC)
len_qrf<-length(y_qrf_temp)
predict_qrf_auc<-matrix(0, nrow = len_qrf, ncol = 1)
y_qrf_auc<-matrix(0, nrow = len_qrf, ncol = 1)

for (i in 1:len_qrf){
  if(y_qrf_temp[i]==1){
    y_qrf_auc[i]<-1
  }
  if(predict_qrf_temp[i]>=0.5){
    predict_qrf_auc[i]<-1
  }
  
}







#roc(response= y_qrf_temp,predictor= predict_qrf_temp,plot = TRUE,legacy.axes=TRUE,percent = TRUE,col="#377eb8",lwd=4,print.auc=TRUE,add=TRUE,print.auc.y=40)
par(pty="s") 
roc(response= y_qrf_temp,predictor= predict_qrf_temp,plot = TRUE,legacy.axes=TRUE,percent = TRUE,xlab="False positive percentage [%]",ylab="Ture positive percentage [%]",col="#377eb8",lwd=4,print.auc=TRUE,cex.lab=1.5, cex.axis=1.2, cex.main=1.5, cex.sub=1.5,print.auc.cex=1.2)




legend("bottomright",legend=c("RandomForest with ntree =500 and mtry=3"),col = c("#377eb8"),lwd = 4,cex=1.2)

#par(pty="m")

###################################################################################

save.image(file='rf_classification_without_crop_species_category.RData')

tiff("ROC.tiff", width = 130, height = 130, units = 'mm', res = 300)
roc(response= y_qrf_temp,predictor= predict_qrf_temp,plot = TRUE,legacy.axes=TRUE,percent = TRUE,xlab="False positive percentage [%]",ylab="Ture positive percentage [%]",col="#377eb8",lwd=4,print.auc=TRUE,cex.lab=0.9, cex.axis=0.9, cex.main=0.9, cex.sub=0.9,print.auc.cex=0.9)
legend("bottomright",legend=c("RandomForest with ntree =500 and mtry=3"),col = c("#377eb8"),lwd = 4,cex=0.8)
dev.off()