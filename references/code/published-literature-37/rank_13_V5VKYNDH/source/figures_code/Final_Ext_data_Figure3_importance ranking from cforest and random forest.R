
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
  library(party)
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
  importance(qrf)
  qrf <- randomForest(Change~PB+Tmax+Tmin+Tave+Crop+WPCT+WPNT+FCT+FNT+RCT+RNT+SCCT+SCNT+ST+IrrigationCT+IrrigationNT,data=xxtrain,ntree = mtree1,mtry=mtry1,proximity=TRUE,keep.inbag=T,importance=TRUE) #,,case.weights = abs(datatrain$ï..Seq_big)
  importance(qrf)
  #pred222 <- predict(qrf, xxtrain[,1:11],type = "prob")
  # pred<-pred222[,2]
  #pred222 <- predict(qrf, newdata = datatest[,-2],type = "prob")
  
  qrf
  #plot(qrf)
}

# cforest
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
  #qrf <- randomForest(Change~PB+Tmax+Tmin+Tave+Crop+WPCT+WPNT+FCT+FNT+RCT+RNT+SCCT+SCNT+ST+IrrigationCT+IrrigationNT,data=xxtrain,ntree = mtree1,mtry=mtry1,proximity=TRUE,keep.inbag=T) #,,case.weights = abs(datatrain$ï..Seq_big)
 
   cf = cforest(Change~PB+Tmax+Tmin+Tave+Crop+WPCT+WPNT+FCT+FNT+RCT+RNT+SCCT+SCNT+ST+IrrigationCT+IrrigationNT,data=xxtrain,controls=cforest_unbiased(ntree=500, mtry=3))
}
  varimp(cf)
  #varimp(cf,conditional = TRUE)
  #pred222 <- predict(qrf, xxtrain[,1:11],type = "prob")
  # pred<-pred222[,2]
  #pred222 <- predict(qrf, newdata = datatest[,-2],type = "prob")
  
  cf
  #plot(qrf)


