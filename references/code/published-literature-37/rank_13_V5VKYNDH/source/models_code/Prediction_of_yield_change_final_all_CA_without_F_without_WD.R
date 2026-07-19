
################################################################################################
{
  library(randomForest)
  library(quantregForest)
  library(quantreg)
  library(ranger)
  library(quantregForest)
  library(quantreg)
  library(dplyr)
  library(readr)
}
graphics.off()
options(digits=10)
#import data and train the database
{
  ### Load data and pre-processing
  test<-read.csv("PhD data.csv")
  ### response parameter
  #test$Change <-as.numeric(as.character(test$ï..Seq))
  test$Change <-as.factor(as.character(test$Change))
  #### numerical predictor
  test$PB <-as.numeric(as.character(test$PB))
  test$Tmax <-as.numeric(as.character(test$Tmax))
  test$Tmin <-as.numeric(as.character(test$Tmin))
  test$Tave<-as.numeric(as.character(test$Tave))
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

{
  set.seed(3)
  
  #get size of the dataset
  n <-nrow(test)
  #get random 100% of the dataset 
  indextrain <- sample(1:n,round(n),replace=FALSE)
  #set those 100% dataset as train and no test
  xtrain <- test[indextrain,3:18]
  ytrain <- test[indextrain,2]
  xxtrain <- test[indextrain,2:18]
  mtry1=3
  mtree1=500
  # quantile regression, qrf is the distribution we get
  #qrf <- quantregForest(x=xtrain,y=ytrain,ntree = mtree1,mtry=mtry1,keep.inbag = TRUE,ntread=2) 
  qrf <- randomForest(Change~PB+Tmax+Tmin+Tave+Crop+WPCT+WPNT+FCT+FNT+RCT+RNT+SCCT+SCNT+ST+IrrigationCT+IrrigationNT,data=xxtrain,ntree = mtree1,mtry=mtry1,proximity=TRUE,keep.inbag=T) #,,case.weights = abs(datatrain$ï..Seq_big)
  
  
  #pred222 <- predict(qrf, xxtrain[,1:11],type = "prob")
  # pred<-pred222[,2]
  #pred222 <- predict(qrf, newdata = datatest[,-2],type = "prob")
  
  qrf
  #plot(qrf)
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################
################# Gdfl-esm2m_rcp26 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Gfdl-esm2m_rcp26.csv')
  n<-nrow(predictor1)
  for (i in 1:n){
    if (predictor1$ST[i]<=3 && predictor1$ST[i]>=0){
      predictor1$ST[i]<-3
    }
    
    if (predictor1$ST[i]<=6 && predictor1$ST[i]>5){
      predictor1$ST[i]<-5
    }
    
    if (predictor1$ST[i]>8 && predictor1$ST[i]<10){
      predictor1$ST[i]<-8
    }
    
    if (predictor1$ST[i]==11 ){
      predictor1$ST[i]<-10
    }
    if (predictor1$ST[i]==13 ){
      predictor1$ST[i]<-3
    }
    
  }
  ST1=predictor1$ST
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Gfdl-esm2m_rcp26.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Gfdl-esm2m_rcp26.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Gfdl-esm2m_rcp26.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Gfdl-esm2m_rcp26.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Gfdl-esm2m_rcp26.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Gfdl-esm2m_rcp26.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
}
##################future#################
################# Gdfl-esm2m_rcp26_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Gfdl-esm2m_rcp26_future.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Gfdl-esm2m_rcp26_future.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Gfdl-esm2m_rcp26_future.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Gfdl-esm2m_rcp26_future.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Gfdl-esm2m_rcp26_future.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Gfdl-esm2m_rcp26_future.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Gfdl-esm2m_rcp26_future.csv')
  n<-nrow(predictor1)

  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################
################# Gdfl-esm2m_rcp45 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Gfdl-esm2m_rcp45.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Gfdl-esm2m_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Gfdl-esm2m_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Gfdl-esm2m_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Gfdl-esm2m_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Gfdl-esm2m_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Gfdl-esm2m_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
}
##################future#################
################# Gdfl-esm2m_rcp45_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Gfdl-esm2m_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Gfdl-esm2m_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Gfdl-esm2m_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Gfdl-esm2m_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Gfdl-esm2m_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Gfdl-esm2m_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Gfdl-esm2m_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################


################# Gdfl-esm2m_rcp60 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Gfdl-esm2m_rcp60.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Gfdl-esm2m_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Gfdl-esm2m_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Gfdl-esm2m_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Gfdl-esm2m_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Gfdl-esm2m_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Gfdl-esm2m_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
}
##################future#################
################# Gdfl-esm2m_rcp60_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Gfdl-esm2m_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Gfdl-esm2m_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Gfdl-esm2m_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Gfdl-esm2m_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Gfdl-esm2m_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Gfdl-esm2m_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Gfdl-esm2m_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################

################# Gdfl-esm2m_rcp85 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Gfdl-esm2m_rcp85.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Gfdl-esm2m_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Gfdl-esm2m_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Gfdl-esm2m_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Gfdl-esm2m_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Gfdl-esm2m_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Gfdl-esm2m_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
}
##################future#################
################# Gdfl-esm2m_rcp85_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Gfdl-esm2m_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Gfdl-esm2m_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Gfdl-esm2m_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Gfdl-esm2m_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Gfdl-esm2m_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Gfdl-esm2m_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Gfdl-esm2m_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################



###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################
################# Ipsl-cm5a-lr_rcp26 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Ipsl-cm5a-lr_rcp26.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Ipsl-cm5a-lr_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Ipsl-cm5a-lr_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Ipsl-cm5a-lr_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Ipsl-cm5a-lr_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Ipsl-cm5a-lr_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Ipsl-cm5a-lr_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
}
##################future#################
################# Ipsl-cm5a-lr_rcp26_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Ipsl-cm5a-lr_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Ipsl-cm5a-lr_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Ipsl-cm5a-lr_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Ipsl-cm5a-lr_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Ipsl-cm5a-lr_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Ipsl-cm5a-lr_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Ipsl-cm5a-lr_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################
################# Ipsl-cm5a-lr_rcp45 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Ipsl-cm5a-lr_rcp45.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Ipsl-cm5a-lr_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Ipsl-cm5a-lr_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Ipsl-cm5a-lr_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Ipsl-cm5a-lr_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Ipsl-cm5a-lr_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Ipsl-cm5a-lr_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
}
##################future#################
################# Ipsl-cm5a-lr_rcp45_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Ipsl-cm5a-lr_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Ipsl-cm5a-lr_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Ipsl-cm5a-lr_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Ipsl-cm5a-lr_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Ipsl-cm5a-lr_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Ipsl-cm5a-lr_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Ipsl-cm5a-lr_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################


################# Ipsl-cm5a-lr_rcp60 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Ipsl-cm5a-lr_rcp60.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Ipsl-cm5a-lr_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Ipsl-cm5a-lr_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Ipsl-cm5a-lr_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Ipsl-cm5a-lr_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Ipsl-cm5a-lr_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Ipsl-cm5a-lr_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
}
##################future#################
################# Ipsl-cm5a-lr_rcp60_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Ipsl-cm5a-lr_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Ipsl-cm5a-lr_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Ipsl-cm5a-lr_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Ipsl-cm5a-lr_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Ipsl-cm5a-lr_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Ipsl-cm5a-lr_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Ipsl-cm5a-lr_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################

################# Ipsl-cm5a-lr_rcp85 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Ipsl-cm5a-lr_rcp85.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Ipsl-cm5a-lr_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Ipsl-cm5a-lr_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Ipsl-cm5a-lr_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Ipsl-cm5a-lr_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Ipsl-cm5a-lr_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Ipsl-cm5a-lr_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
}
##################future#################
################# Ipsl-cm5a-lr_rcp85_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Ipsl-cm5a-lr_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Ipsl-cm5a-lr_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Ipsl-cm5a-lr_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Ipsl-cm5a-lr_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Ipsl-cm5a-lr_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Ipsl-cm5a-lr_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Ipsl-cm5a-lr_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################
################# Hadgem2-es_rcp26 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Hadgem2-es_rcp26.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Hadgem2-es_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Hadgem2-es_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Hadgem2-es_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Hadgem2-es_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Hadgem2-es_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Hadgem2-es_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
}
##################future#################
################# Hadgem2-es_rcp26_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Hadgem2-es_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Hadgem2-es_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Hadgem2-es_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Hadgem2-es_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Hadgem2-es_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Hadgem2-es_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Hadgem2-es_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################
################# Hadgem2-es_rcp45 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Hadgem2-es_rcp45.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Hadgem2-es_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Hadgem2-es_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Hadgem2-es_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Hadgem2-es_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Hadgem2-es_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Hadgem2-es_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
}
##################future#################
################# Hadgem2-es_rcp45_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Hadgem2-es_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Hadgem2-es_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Hadgem2-es_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Hadgem2-es_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Hadgem2-es_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Hadgem2-es_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Hadgem2-es_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################


################# Hadgem2-es_rcp60 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Hadgem2-es_rcp60.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Hadgem2-es_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Hadgem2-es_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Hadgem2-es_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Hadgem2-es_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Hadgem2-es_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Hadgem2-es_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
}
##################future#################
################# Hadgem2-es_rcp60_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Hadgem2-es_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Hadgem2-es_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Hadgem2-es_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Hadgem2-es_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Hadgem2-es_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Hadgem2-es_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Hadgem2-es_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################

################# Hadgem2-es_rcp85 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Hadgem2-es_rcp85.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Hadgem2-es_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Hadgem2-es_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Hadgem2-es_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Hadgem2-es_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Hadgem2-es_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Hadgem2-es_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
}
##################future#################
################# Hadgem2-es_rcp85_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_Hadgem2-es_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_Hadgem2-es_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_Hadgem2-es_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_Hadgem2-es_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_Hadgem2-es_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_Hadgem2-es_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_Hadgem2-es_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################



###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################
################# MIROC5_rcp26 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_MIROC5_rcp26.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_MIROC5_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_MIROC5_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_MIROC5_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_MIROC5_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_MIROC5_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_MIROC5_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
}
##################future#################
################# MIROC5_rcp26_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_MIROC5_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_MIROC5_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_MIROC5_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_MIROC5_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_MIROC5_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_MIROC5_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_MIROC5_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################
################# MIROC5_rcp45 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_MIROC5_rcp45.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_MIROC5_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_MIROC5_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_MIROC5_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_MIROC5_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_MIROC5_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_MIROC5_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
}
##################future#################
################# MIROC5_rcp45_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_MIROC5_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_MIROC5_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_MIROC5_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_MIROC5_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_MIROC5_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_MIROC5_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_MIROC5_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################


################# MIROC5_rcp60 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_MIROC5_rcp60.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_MIROC5_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_MIROC5_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_MIROC5_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_MIROC5_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_MIROC5_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_MIROC5_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
}
##################future#################
################# MIROC5_rcp60_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_MIROC5_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_MIROC5_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_MIROC5_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_MIROC5_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_MIROC5_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_MIROC5_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_MIROC5_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################

################# MIROC5_rcp85 ############
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_MIROC5_rcp85.csv')
  n<-nrow(predictor1)
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_MIROC5_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_MIROC5_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_MIROC5_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_MIROC5_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_MIROC5_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_MIROC5_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
}
##################future#################
################# MIROC5_rcp85_future
##barley 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_barley_baseline_MIROC5_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"barley.spring"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_barley_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_barley_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_barley_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
}

##maize 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_maize_baseline_MIROC5_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"maize"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_maize_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_maize_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_maize_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
}

##soybean 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_soybean_baseline_MIROC5_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"soybean"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_soybean_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_soybean_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_soybean_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
}

##wheat 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_wheat_baseline_MIROC5_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"wheat.winter"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_wheat_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_wheat_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_wheat_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
}

##sorghum 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sorghum_baseline_MIROC5_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sorghum"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sorghum_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_sorghum_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sorghum_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
}

##cotton 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_cotton_baseline_MIROC5_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"cotton"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_cotton_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_cotton_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_cotton_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
}

##sunflower 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_sunflower_baseline_MIROC5_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"sunflower"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_sunflower_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_sunflower_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_sunflower_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
}


###############################################################################################################
################################################################################################################
###############################################################################################################
#########################################################################################################
###############################################################################################################



######rice Gfdl-esm2m ########### 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Gfdl-esm2m_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp26_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Gfdl-esm2m_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp26_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Gfdl-esm2m_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp45_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Gfdl-esm2m_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp45_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Gfdl-esm2m_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp60_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Gfdl-esm2m_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp60_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Gfdl-esm2m_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp85_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Gfdl-esm2m_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Gfdl-esm2m_rcp85_future_randomForest.csv")
}


######rice Ipsl-cm5a-lr ########### 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Ipsl-cm5a-lr_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Ipsl-cm5a-lr_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp26_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Ipsl-cm5a-lr_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Ipsl-cm5a-lr_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp45_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Ipsl-cm5a-lr_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Ipsl-cm5a-lr_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp60_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Ipsl-cm5a-lr_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Ipsl-cm5a-lr_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Ipsl-cm5a-lr_rcp85_future_randomForest.csv")
}


######rice Hadgem2-es ########### 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Hadgem2-es_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Hadgem2-es_rcp26_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Hadgem2-es_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Hadgem2-es_rcp26_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Hadgem2-es_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Hadgem2-es_rcp45_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Hadgem2-es_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Hadgem2-es_rcp45_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Hadgem2-es_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Hadgem2-es_rcp60_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Hadgem2-es_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Hadgem2-es_rcp60_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Hadgem2-es_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Hadgem2-es_rcp85_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_Hadgem2-es_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_Hadgem2-es_rcp85_future_randomForest.csv")
}



######rice MIROC5 ########### 
{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_MIROC5_rcp26.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_MIROC5_rcp26_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_MIROC5_rcp26_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_MIROC5_rcp26_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_MIROC5_rcp45.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_MIROC5_rcp45_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_MIROC5_rcp45_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_MIROC5_rcp45_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_MIROC5_rcp60.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_MIROC5_rcp60_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_MIROC5_rcp60_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_MIROC5_rcp60_future_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_MIROC5_rcp85.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_MIROC5_rcp85_randomForest.csv")
}

{
  ### Load data and pre-processing for prediction
  predictor1=read.csv('predictor_rice_baseline_MIROC5_rcp85_future.csv')
  n<-nrow(predictor1)
  
  
  
  predictor1$Crop<-"rice"
  
  predictor1$Crop<-as.factor(as.character(predictor1$Crop))
  
  predictor1$PB <-as.numeric(as.character(predictor1$PB))
  predictor1$Tmax <-as.numeric(as.character(predictor1$Tmax))
  predictor1$Tmin <-as.numeric(as.character(predictor1$Tmin))
  predictor1$Tave <-as.numeric(as.character(predictor1$Tave))
  
  predictor1$SCCT <-as.factor(as.character(predictor1$SCCT))
  predictor1$SCNT <-as.factor(as.character(predictor1$SCNT))
  
  predictor1$RCT <-as.factor(as.character(predictor1$RCT))
  predictor1$RNT <-as.factor(as.character(predictor1$RNT))
  
  predictor1$FCT <-as.factor(as.character(0))
  predictor1$FNT <-as.factor(as.character(0))
  
  predictor1$WPCT <-as.factor(as.character(0))
  predictor1$WPNT <-as.factor(as.character(0))
  
  predictor1$IrrigationCT <-as.factor(as.character(predictor1$IrrigationCT))
  predictor1$IrrigationNT <-as.factor(as.character(predictor1$IrrigationNT))
  
  predictor1$ST <-as.factor(as.character(ST1))
  
  
  
  predictor<-predictor1[,2:17]
  predictor<-rbind(test[1,3:18],predictor[,1:16])
  
  
  
  predictor$Change_positive_prob <- predict(qrf, newdata = predictor,type = "prob")
  
  write.csv(predictor,"1_rice_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
  predictor1=read.csv('1_rice_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv',header=T)[-1,]
  predictor<-predictor1[ , -which(names(predictor1) %in% c("Crop","X"))]
  write.csv(predictor,"2_rice_yield_change_map_raw_data_MIROC5_rcp85_future_randomForest.csv")
}

