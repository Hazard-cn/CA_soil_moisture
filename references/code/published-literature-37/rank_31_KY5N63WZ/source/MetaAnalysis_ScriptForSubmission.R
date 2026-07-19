require(metafor) # for meta-analysis mixed model with rma.mv()
require(plyr) # for rbind.fill() function
require(Matrix) # for bdiag() function

#################################################################
# function to produce variance-coveriance (VCV) matrix for observations that share common control or experimental treatment, following Lajeunesse (2011)
# NB: this function is based on covariance_commonControl() in the metagear package and has been modified to also produce the respective VCVs for the stabilty responses
# see supplemental material for the equations
#################################################################
covariance_commonControl <- function (aDataFrame, 
                                      control_ID, 
                                      X_t, 
                                      SD_t, 
                                      N_t,
                                      X_c, 
                                      SD_c, 
                                      N_c,
                                      metric = "lnRR") {
  
  ## generate list of control groups in dataframe
  controlList <- split(aDataFrame, as.factor(aDataFrame[, control_ID]))
  listV <- list(); dataAlignedWithV <- data.frame();

  for(i in 1:length(controlList)) { 
    ## stack dataframes in V order
    dataAlignedWithV <- rbind(dataAlignedWithV, controlList[[i]])
    
    if(metric == "lnRR") {    
      ## common control covariance and variance of response ratio based Lajeunesse 2011
      covar <-       (controlList[[i]][, SD_c] ^ 2) / (controlList[[i]][, N_c] * (controlList[[i]][, X_c] ^ 2)) 
      var <- covar + (controlList[[i]][, SD_t] ^ 2) / (controlList[[i]][, N_t] * (controlList[[i]][, X_t] ^ 2)) 
    } 
    ####### added by SK    (start)
    if(metric == "lnVR") {    
      covar <-        1 / (2*(controlList[[i]][, N_c] -1))
      var <- covar +  1 / (2*(controlList[[i]][, N_t] -1))
    } 
    if(metric == "lnCVR") {    
      covar <-        (controlList[[i]][, SD_c] ^ 2) / (controlList[[i]][, N_c] * (controlList[[i]][, X_c] ^ 2))+(1 / (2*(controlList[[i]][, N_c] -1)))
      var <- covar + ((controlList[[i]][, SD_t] ^ 2) / (controlList[[i]][, N_t] * (controlList[[i]][, X_t] ^ 2))+(1 / (2*(controlList[[i]][, N_t] -1))))
    }
    ####### added by SK    (end)
    
    ## calculate V for ith element in the controlList
    V <- matrix(covar, nrow = length(var), ncol = length(var))
    diag(V) <- var
    
    ## collect V's with a list
    listV <- unlist(list(listV, list(V)), recursive = FALSE)
  } 
  
  ## convert list of V's into single matrix
  V <- as.matrix(bdiag(listV))
  
  ## return V matrix paired with aligned dataset
  return(list(V, dataAlignedWithV))
}

#################################################################
# function to add the respective measure with the escalc function from metafor
# and the VCV using the function above
#################################################################
addmeassure <- function(obstable,metric,lajeunesse)
{
  # rename metric for escalc() function
  if (metric=="lnRR"){measure="ROM"}
  if (metric=="lnVR"){measure="VR"}
  if (metric=="lnCVR"){measure="CVR"}
  
  if (lajeunesse)
  {
    
    # 1) observations that share common control treatment
    sub <- obstable[!is.na(obstable$cluster_cont),]
    if(nrow(sub)>0){
      commoncont <- covariance_commonControl (aDataFrame=sub,
                                              control_ID="cluster_cont",
                                              X_t="yieldexp",SD_t="sdexp",N_t="nryears",
                                              X_c="yieldcont",SD_c="sdcont",N_c="nryears",
                                              metric = metric)
      commoncont[[2]] <- escalc(measure=measure,m1i=yieldexp,m2i=yieldcont,
                                sd1i=sdexp,sd2i=sdcont,n1i=nryears,n2i=nryears,data=commoncont[[2]])
    } else{
      commoncont <- list(
        matrix(nrow=0,ncol=0),
        sub
      )
    }
    
    # 2) observations that share common experimental treatment
    sub <- obstable[!is.na(obstable$cluster_exp),]
    if(nrow(sub)>0){
      # NB: as function is written for common control, t and c have to be interchanged here
      commonexp <- covariance_commonControl (aDataFrame=sub,
                                             control_ID="cluster_exp",
                                             X_c="yieldexp",SD_c="sdexp",N_c="nryears",
                                             X_t="yieldcont",SD_t="sdcont",N_t="nryears",
                                             metric = metric)
      commonexp[[2]] <- escalc(measure=measure,m1i=yieldexp,m2i=yieldcont,
                               sd1i=sdexp,sd2i=sdcont,n1i=nryears,n2i=nryears,data=commonexp[[2]])
    } else{
      commonexp <- list(
        matrix(nrow=0,ncol=0),
        sub
      )
    }
    # 3) "normal" obs, not sharing any common control or experimental treatment (no Lajeunesse )
    sub <- obstable[is.na(obstable$cluster_exp) & is.na(obstable$cluster_cont),]
    if(nrow(sub)>0){
      nocommon <- list(
        diag(escalc(measure=measure,m1i=yieldexp,m2i=yieldcont,sd1i=sdexp,sd2i=sdcont,n1i=nryears,n2i=nryears,data=sub)$vi),
        escalc(measure=measure,m1i=yieldexp,m2i=yieldcont,sd1i=sdexp,sd2i=sdcont,n1i=nryears,n2i=nryears,data=sub))
    } else{
      
    }
    ####### combine
    out <- list(
      bdiag(commoncont[[1]],commonexp[[1]],nocommon[[1]]),  # v matrix
      rbind.fill(commoncont[[2]],commonexp[[2]],nocommon[[2]]) # obs table   
    )

  } else {    # when no lajeunese correction demanded, lajeunesse=FALSE in function call
    out <- list(
      diag(escalc(measure=measure,m1i=yieldexp,m2i=yieldcont,sd1i=sdexp,sd2i=sdcont,n1i=nryears,n2i=nryears,data=obstable)$vi),
      escalc(measure=measure,m1i=yieldexp,m2i=yieldcont,sd1i=sdexp,sd2i=sdcont,n1i=nryears,n2i=nryears,data=obstable))
  }
  return(out)
}


#################################################################
# read in data and specify response
#################################################################
# data tables in the Excel file have to be saved as .csv files, using comma as separator
# (uncomment the respective dataset)

# a) Ponisio (organic farming)
#obstable <- read.csv("Data/DataForSubmission/Ponisio_obstable.csv")
# b) Pittelkow (no-tillage)
obstable <- read.csv("Data/DataForSubmission/Pittelkow_obstable.csv")
nrow(obstable) # number of MYOs

# specify response: mean yield ratio, absolute stabilty ratio, or relative stability ratio 
responses <- c("lnRR","lnVR","lnCVR")
response <- responses[2]

#################################################################
# Overall model with only intercept (without moderator)
#################################################################

# add the respective response and variance-covariance matrix using the addmeasure() function, defined before
tempmat <- addmeassure(obstable,metric=response,lajeunesse = T)
respmat <- tempmat[[2]] # the actual data, with the the respective response
varmat <- tempmat[[1]]  # the variance-covariance matrix (VCV)

# factorize study to be fitted as categorial random effect
metadat$study <- factor(metadat$study)

# fit mixed-model with rma.mv() from the metafor package (needs around a minute)
model <- rma.mv(yi~1,V=varmat,random=~1|study/myo,data=respmat)

### extract back-transformed mean and 95% confidence interval (CI)
# mean
exp(model$b)
# 95% CI
c(exp(model$ci.lb),exp(model$ci.ub))
# omnibus test, if different from 1
model$pval


#################################################################
# Model with moderator (without intercept)
#################################################################

# specify moderator to test, e.g. species, must be a column name in table with MYOs (obstable)
moderator <- "species"

# subset to rows where modi is not NA
modsub <- obstable[!is.na(obstable[,moderator]),]
# refactorize (was sometimes necessary)
modsub[,moderator] <- factor(modsub[,moderator])

# add the respective response and variance-covariance matrix using the addmeasure() function, defined before
# (VCV is calculated anew for each moderator, see methods)
tempmat <- addmeassure(modsub,metric=response,lajeunesse = T)
respmat <- tempmat[[2]] # the actual data, with the the respective response
varmat <- tempmat[[1]]  # the variance-covariance matrix (VCV)

# factorize study to be fitted as categorial random effect
metadat$study <- factor(metadat$study)

# fit mixed-model with rma.mv() from the metafor package (needs around a minute)
model <- with(respmat,rma.mv(as.formula(paste("yi~",moderator,"-1")),V=varmat,random=~1|study/myo))  
### extract back-transformed mean and 95% confidence interval (CI)
# combined: mean, lower and upper CI, P-val for omnibus test, if different form 1
cbind(exp(model$b),exp(model$ci.lb),exp(model$ci.ub),model$pval)



