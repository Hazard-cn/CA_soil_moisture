### This script contains helper functions called by other scripts

namean= function(x) mean(x,na.rm=T)

log2Perc = function(x) (exp(x)-1) * 100

load_data = function(dataset, cropTypes) {
  
  #Select dataset type.
  #"main" is the dataset used in the primary analysis where data from 2007-2018 is used and
  #where climate variables are observed at least during half of all growing season days (see Methods). 
  #"extended extends the dataset back to 1980 and does not limit observations based on climate data observation quality. 
  if(dataset == "main") {
    dataset_str = "half" #all
    runStr = paste0("2007_2018_",dataset_str,"_V2_Ram")
    d = fread(file = paste0("Data/allCrops_",runStr,".csv"))
    
    if (cropTypes == "summer"){
      #drop winter crops
      d = d[d$crop != "Wheat",] 
      d = d[d$crop != "Oats",] 
      d = d[d$crop != "Barley",] 
    } else {
      #drop summer crops
      d = d[d$crop != "Maize",] 
      d = d[d$crop != "Soybeans",] 
      d = d[d$crop != "Sorghum",] 
      d = d[d$crop != "Millet",] 
    }
    
  } else if (dataset == "extended"){
    ###--- All data ---###
    d = fread(file = paste0("Data/allCrops_1980_2018_all_V2_Ram.csv"))
    #make a plot of soil moisture data over time to see data quality
    ggplot(data = d) + geom_point(aes(x = gsYr, y = N_smrz_day), alpha = 0.1) +
      theme_classic() + xlab("Year") +
      ylab("Number of soil moisture obs. per month (growing season average)")
    #limit to past 1992 where there are more SM observations, can remove this to look all the way back. 
    d = d[gsYr >= 1992]
  }

  
  #set variables to the correct types for fixed effects. 
  d$country = as.factor(d$country)
  d$year = as.numeric(d$year)
  d$crop = as.factor(d$crop)
  d$country_crop = paste0(d$country, "_", d$crop)
  d$country_crop = as.factor(d$country_crop)
  
  return(d)
}

#10-fold cross-validation
getCrossValR2 = function(mod, returnPreds = F, nsf = 3, setSeed=T, crossCountry = F, setSeedValue = 123, returnCX = F) {
  if(crossCountry){
    x = as.matrix(mod$cX)
    y = mod$cY
    
    c = as.character(mod$fe$country)
    cs = unique(c)
    
    #shuffle countries
    if(setSeed) {
      set.seed(setSeedValue)
    }
    cs = sample(cs,length(cs))
    #Split X and Y into 10 different groups based on countries
    folds_cs = cut(seq(1,length(cs)),breaks=10,labels=FALSE)
    
    #Perform 10 fold cross validation
    testyhats = c()
    testys = c()
    for(i in 1:10){
      #Segment data by fold using the which() function 
      testCountries = cs[which(folds_cs==i,arr.ind=T)]
      testIndexes = which(c %in% testCountries)
      testDataX = x[testIndexes, ]
      testDataY = y[testIndexes]
      trainDataX = x[-testIndexes, ]
      trainDataY = y[-testIndexes]
      #Train model
      m = lm(trainDataY~trainDataX + -1) #no intercept bc there are already FE
      testDataXUse = testDataX
      bUse = m$coefficients
      testyhat = as.matrix(testDataXUse) %*% bUse
      testyhats = c(testyhats, testyhat)
      testys = c(testys,testDataY)
    }
    rss <- sum((testyhats - testys)^2)
    tss <- sum((testys - mean(testys))^2)
    rsq <- 1 - rss/tss
    
    if(returnPreds){return(list("testys" = testys, "testyhats" = testyhats, "shuffOrder" = s))}
    return(signif(rsq,nsf))
  } else {
    x = as.matrix(mod$cX)
    y = mod$cY
    #Split X and Y into 5 different groups
    if(setSeed) {
      set.seed(setSeedValue)
    }
    #Randomly shuffle the data
    s = sample(length(y))
    x = as.matrix(x[s,])
    y = y[s]
    
    #Create 10 equally size folds
    folds = cut(seq(1,length(y)),breaks=10,labels=FALSE)
    
    #Perform 10 fold cross validation
    testyhats = c()
    testys = c()
    for(i in 1:10){
      #Segement data by fold using the which() function 
      testIndexes = which(folds==i,arr.ind=TRUE)
      testDataX = x[testIndexes, ]
      testDataY = y[testIndexes]
      trainDataX = x[-testIndexes, ]
      trainDataY = y[-testIndexes]
      #Train model
      m = lm(trainDataY~trainDataX + -1)
      testDataXUse = testDataX
      bUse = m$coefficients
      testyhat = as.matrix(testDataXUse) %*% bUse
      testyhats = c(testyhats, testyhat)
      testys = c(testys,testDataY)
      if(i==1){
        testCXs = testDataX
      } else {
        testCXs = rbind(testCXs, testDataX)
      }
    }
    rss <- sum((testyhats - testys)^2)
    tss <- sum((testys - mean(testys))^2)
    rsq <- 1 - rss/tss
    
    if(returnPreds & returnCX){return(list("testys" = testys, "testyhats" = testyhats, "shuffOrder" = s, "testCXs" = testCXs))}
    if(returnPreds){return(list("testys" = testys, "testyhats" = testyhats, "shuffOrder" = s))}
    return(signif(rsq,nsf))
  }
  
}


genRecenteredXVals_RCS = function(x, xRef, k) {
  #### x is the x-values that you're plotting (linear)
  
  xVals_reCentered = rcspline.eval(x, knots = k, inclx = T) - rcspline.eval(x = rep(xRef, length(x)), knots = k, inclx = T)
  
  return(xVals_reCentered)
  
}

genRecenteredXVals_polynomial = function(x,xRef,polyOrder) {
  ### This function generates X values that are recentered around value xRef. The output of this function can be passed to plotPolynomialResponse to generate recentered polynomial response functions
  ### x is the linear x values that you want to plot over
  ### xRef is the reference value you want to recenter around
  ### polyOrder is the order of the polynomial
  
  newX <- data.frame(matrix(NA, nrow=length(x), ncol = polyOrder))
  
  for (p in 1:polyOrder) {
    newX[,p] <- x^p - xRef^p
  }
  return(newX)
}

##### CalcVariance and getVcov are helper functions to plotPolynomialResponse
calcVariance = function(cvec, vcovMat) {
  ##Calculate the variance:
  #cvec is a vector of climate variables (k by 1), coming from the GCM
  #vcov is a variance covariance matrix with the same column order as cvec. This comes from our empirical estimation.
  return(t(cvec) %*% vcovMat %*% cvec)
  
}

getVcov = function(vcv, vars) {
  #from the entire variance covariance matrix, select the portion corresponding to the variable you're interested in.
  return(vcv[vars,vars])
}


makeMeanYieldMap = function(d , crop) {
  namean = function(x) mean(x, na.rm=T)
  c = d[,.(lnyield = namean(log(yield))),by = .(country)]
  
  c$country = as.character(c$country)
  c = updateFaoNamesToMatchShapefile(c)
  
  #load shapefile
  poly.fort = map_data("world")
  #merge the shapefile with the error data
  poly.fort2 = merge(x = poly.fort, y = c, by.x = "region", by.y = "country", all.x=T)
  poly.fort2 = data.table(poly.fort2)
  poly.fort2 = poly.fort2[order(order)]
  
  #Try clipping
  poly.fort2=poly.fort2[poly.fort2$long<160,]
  poly.fort2=poly.fort2[poly.fort2$long>-130,]
  poly.fort2=poly.fort2[poly.fort2$lat<70,]
  poly.fort2=poly.fort2[poly.fort2$lat>-60,]
  
  
  #plot the mean sqrt mean data
  gmap = ggplot(poly.fort2, aes(x = long, y = lat, group = group, fill = (lnyield))) +
    geom_polygon(colour = "black", size = 0.5, aes(group = group)) +
    theme_map() + ggtitle(paste0(crop)) #+ theme(legend.position = "right")#+ scale_fill_gradientn(colours=r)
  
  return(gmap)
}


#helper function for make error plot
updateFaoNamesToMatchShapefile = function(dt){
  
  #Update names and merge
  dt$country[dt$country == "Viet Nam"] = "Vietnam"
  dt$country[dt$country == "Iran (Islamic Republic of)"] = "Iran"
  dt$country[dt$country == "China, mainland"] = "China"
  dt$country[dt$country == "Syrian Arab Republic"] = "Syria"
  dt$country[dt$country == "Republic of Moldova"] = "Moldova"
  dt$country[dt$country == "Congo"] = "Democratic Republic of the Congo"
  dt$country[dt$country == "Venezuela (Bolivarian Republic of)"] = "Venezuela" 
  dt$country[dt$country == "Republic of Korea"] = "South Korea"
  dt$country[dt$country == "Democratic People's Republic of Korea"] =  "North Korea"
  dt$country[dt$country == "Lao People's Democratic Republic"] = "Laos"
  dt$country[dt$country == "Russian Federation"] = "Russia"
  dt$country[dt$country == "North Macedonia"] = "Macedonia"
  dt$country[dt$country == "United Republic of Tanzania"] = "Tanzania"
  dt$country[dt$country == "Eswatini"] = "Swaziland"
  dt$country[dt$country == "United Kingdom of Great Britain and Northern Ireland"] = "UK"
  dt$country[grepl(pattern = "Ivoire",dt$country)] = "Ivory Coast"
  dt$country[grepl(pattern = "United States of America",dt$country)] = "USA"
  dt$country[grepl(pattern = "Czechia",dt$country)] = "Czech Republic"
  dt$country[grepl(pattern = "Bolivia",dt$country)] = "Bolivia"
  #Plotting Sudan and South Sudan. Sudan (former) is used in the analysis. All three are given their own intercept and slope in the estimation
  #Sudan (former) doesn't merge. that's OK as it's just aesthetic. 
  
  return(dt)
}


plotIndividualModels = function(mTPr, mTSr, runStr, crop, gs_length, cvartype = "daily", returnGGList = F, plotSMBounds = T, makeStackedPlots = T, makeCombinedPlot=F, is_pR2=F) {
  #load daily data
  if(crop == "allCrops") {
    print("loading combined crop data...")
    hd = readRDS(paste0("Data/allCrops_10pctCropW_all10pct2007_2007_2018.rda"))
    hd = hd[hd$crop != "Wheat",]
    hd = hd[hd$crop != "Barley",]
    hd = hd[hd$crop != "Oats",]
    
  }
  
  #set bounds for plotting
  uq = 0.995
  lq = 0.005
  uq_precip = 0.99
  lq_precip = 0.01
  hd$precip[hd$precip > quantile(hd$precip,uq_precip, na.rm=T)] = quantile(hd$precip,uq_precip, na.rm=T)
  hd$precip[hd$precip < quantile(hd$precip,lq_precip, na.rm=T)] = quantile(hd$precip,lq_precip, na.rm=T)
  hd$tmax[hd$tmax > quantile(hd$tmax,uq, na.rm=T)] = quantile(hd$tmax,uq, na.rm=T)
  hd$tmax[hd$tmax < quantile(hd$tmax,lq, na.rm=T)] = quantile(hd$tmax,lq, na.rm=T)
  hd$smrz[hd$smrz > quantile(hd$smrz,uq, na.rm=T)] = quantile(hd$smrz,uq, na.rm=T)
  hd$smrz[hd$smrz < quantile(hd$smrz,lq, na.rm=T)] = quantile(hd$smrz,lq, na.rm=T)
  
  #Colors:
  colors_hist <- c("cropMaize" = "#78C59D", "cropSoybeans" = "black", "cropMillet" = "#C63C3C", "cropSorghum" = "4A48E7")
  
  #already winsorized above so no need to clip
  smRange = quantile(hd$smrz, c(0,1), na.rm=T)
  prcpRange = quantile(hd$precip, c(0,1), na.rm=T)
  tmaxRange = quantile(hd$tmax, c(0,1), na.rm=T)
  tmaxRange = c(11,40) # is 11.04273 40.06401, cleaner for other things this way.
  
  ### Make responses and uncertainty ###
  sm = seq(smRange[1],smRange[2],0.01)
  #create a datatable with all the features and then multiply the relevant ones
  sm_rcs = genRecenteredXVals_RCS(x = sm, xRef = mean(hd$smrz,na.rm=T), k = c(0.1,0.2,0.3,0.4))
  #sm_rcs = rcspline.eval(x = sm, knots = c(0.1,0.2,0.3,0.4), inclx = F)
  smdf = cbind(sm,sm_rcs,sm^2)
  colnames(smdf) = c("smval_forplot","smrz_day", "smrz_day_RCS_k4_1", "smrz_day_RCS_k4_2","smrz2_day")
  
  #For each crop or crop group:
  cropNsS = unique(grep("crop",unlist(strsplit(rownames(mTSr$beta), ":")),value=T))
  #reorder
  cropNsS = cropNsS[c(1,4,3,2)]
  rSList = list()
  rS_lbsList = list()
  rS_ubsList = list()
  ri = 1
  for(cropN in cropNsS){
    #Get Response
    mTSr$beta_c = mTSr$beta[grepl(cropN, rownames(mTSr$beta))]
    mTSr$beta_c_names = rownames(mTSr$beta)[grepl(cropN, rownames(mTSr$beta))]
    columnNames = unlist(strsplit(grep("smrz",mTSr$beta_c_names, value = T),":"))
    columnNames = grep("smrz",columnNames, value = T)
    rSList[[ri]] = as.matrix(smdf[,columnNames]) %*% as.matrix(mTSr$beta_c[grepl("smrz",mTSr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTSr$clustervcv, grep("smrz",mTSr$beta_c_names, value = T))
    length = 1.96 * sqrt(apply(X = as.matrix(smdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rS_lbsList[[ri]] = rSList[[ri]] - length
    rS_ubsList[[ri]] = rSList[[ri]] + length
    #increment
    ri = ri + 1
  }
  
  
  ### --- PR
  ### Precip ###
  prcp = seq(prcpRange[1],prcpRange[2],.1)
  #create a datatable with all the features and then multiply the relevant ones
  prcp_rcs = genRecenteredXVals_RCS(x = prcp, xRef = 10, k = c(1,20,50,150))
  prcpdf = cbind(prcp^2, prcp_rcs)
  colnames(prcpdf) = c("prcp2_day", "prcp_day", "prcp_day_RCS_k4_1", "prcp_day_RCS_k4_2")
  
  #For each crop or crop group:
  cropNsP = unique(grep("crop",unlist(strsplit(rownames(mTPr$beta), ":")),value=T))
  #reorder
  cropNsP = cropNsP[c(1,4,3,2)]
  cropN = "Maize"
  rPList = list()
  rP_lbsList = list()
  rP_ubsList = list()
  ri = 1
  for(cropN in cropNsP){
    mTPr$beta_c = mTPr$beta[grepl(cropN, rownames(mTPr$beta))]
    mTPr$beta_c_names = rownames(mTPr$beta)[grepl(cropN, rownames(mTPr$beta))]
    columnNames = unlist(strsplit(grep("prcp",mTPr$beta_c_names, value = T),":"))
    columnNames = grep("prcp",columnNames, value = T)
    rPList[[ri]] = as.matrix(prcpdf[,columnNames]) %*% as.matrix(mTPr$beta_c[grepl("prcp",mTPr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTPr$clustervcv, grep("prcp",mTPr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(prcpdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rP_lbsList[[ri]] = rPList[[ri]] - length
    rP_ubsList[[ri]] = rPList[[ri]] + length
    ri = ri + 1
  }
  
  ### --- Tmax
  tmaxCentVal = 20
  tmax = seq(tmaxRange[1],tmaxRange[2],0.1)
  #create a datatable with all the features and then multiply the relevant ones
  tmax_rcs_cent = genRecenteredXVals_RCS(x = tmax, xRef = tmaxCentVal, k = c(10,20,27,35))
  tmax_rcs_cent = tmax_rcs_cent[,-1]
  tmax_poly_cent = genRecenteredXVals_polynomial(tmax,tmaxCentVal,2)
  tmaxdf = cbind(tmax_poly_cent, tmax_rcs_cent)
  colnames(tmaxdf) = c("tmax_day", "tmax2_day", "tmax_day_RCS_k4_1", "tmax_day_RCS_k4_2")
  
  #For each crop or crop group:
  cropNsTP = unique(grep("crop",unlist(strsplit(rownames(mTPr$beta), ":")),value=T))
  #reorder
  cropNsTP = cropNsTP[c(1,4,3,2)]
  cropN = "Maize"
  rTPList = list()
  rTP_lbsList = list()
  rTP_ubsList = list()
  ri = 1
  for(cropN in cropNsTP){
    mTPr$beta_c = mTPr$beta[grepl(cropN, rownames(mTPr$beta))]
    mTPr$beta_c_names = rownames(mTPr$beta)[grepl(cropN, rownames(mTPr$beta))]
    columnNames = unlist(strsplit(grep("tmax",mTPr$beta_c_names, value = T),":"))
    columnNames = grep("tmax",columnNames, value = T)
    rTPList[[ri]] = as.matrix(tmaxdf[,columnNames]) %*% as.matrix(mTPr$beta_c[grepl("tmax",mTPr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTPr$clustervcv, grep("tmax",mTPr$beta_c_names, value = T))
    length = 1.96 * sqrt(apply(X = as.matrix(tmaxdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rTP_lbsList[[ri]] = rTPList[[ri]] - length
    rTP_ubsList[[ri]] = rTPList[[ri]] + length
    ri = ri + 1
  }
  
  #For each crop or crop group:
  cropNsTS = unique(grep("crop",unlist(strsplit(rownames(mTSr$beta), ":")),value=T))
  #reorder
  cropNsTS = cropNsTS[c(1,4,3,2)]
  cropN = "Maize"
  rTSList = list()
  rTS_lbsList = list()
  rTS_ubsList = list()
  ri = 1
  for(cropN in cropNsTS){
    mTSr$beta_c = mTSr$beta[grepl(cropN, rownames(mTSr$beta))]
    mTSr$beta_c_names = rownames(mTSr$beta)[grepl(cropN, rownames(mTSr$beta))]
    columnNames = unlist(strsplit(grep("tmax",mTSr$beta_c_names, value = T),":"))
    columnNames = grep("tmax",columnNames, value = T)
    rTSList[[ri]] = as.matrix(tmaxdf[,columnNames]) %*% as.matrix(mTSr$beta_c[grepl("tmax",mTSr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTSr$clustervcv, grep("tmax",mTSr$beta_c_names, value = T))
    length = 1.96 * sqrt(apply(X = as.matrix(tmaxdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rTS_lbsList[[ri]] = rTSList[[ri]] - length
    rTS_ubsList[[ri]] = rTSList[[ri]] + length
    ri = ri + 1
  }
  
  
  #################
  ### Plot ###
  #################
  
  ### --- Plot as a stack (Fig2)
  ###
  
  #This makes individual plots for each variable rather than combining them all together, which gets too messy. 
  polysize = 0.1
  polyalpha = 0.3
  dotlineoffset = 0.3
  
  hd$crop[hd$crop == "Maize"] = "1Maize"
  hd$crop[hd$crop == "Soybeans"] = "2Soybeans"
  hd$crop[hd$crop == "Sorghum"] = "3Sorghum"
  hd$crop[hd$crop == "Millet"] = "4Millet"
  
  #rename to drop the "crop"
  cropNsS = substr(cropNsS, 5, nchar(cropNsS))
  cropNsSnoNum = cropNsS
  cropNsS = paste0(1:4, cropNsS)
  
  
  #Convert to daily response
  cgsi = 1
  for(cropN in cropNsSnoNum){
    rSList[[cgsi]] = log2Perc(rSList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rS_ubsList[[cgsi]] = log2Perc(rS_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rS_lbsList[[cgsi]] = log2Perc(rS_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rPList[[cgsi]] = log2Perc(rPList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rP_ubsList[[cgsi]] = log2Perc(rP_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rP_lbsList[[cgsi]] = log2Perc(rP_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rTSList[[cgsi]] = log2Perc(rTSList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTS_ubsList[[cgsi]] = log2Perc(rTS_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTS_lbsList[[cgsi]] = log2Perc(rTS_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rTPList[[cgsi]] = log2Perc(rTPList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTP_ubsList[[cgsi]] = log2Perc(rTP_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTP_lbsList[[cgsi]] = log2Perc(rTP_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    cgsi = cgsi + 1
  }
  
  ### Calculate how the responses change TS vs TP ###
  dfVals = data.frame(tmax = tmaxdf$tmax_day+20, rTS_Maize = rTSList[[1]], rTP_Maize = rTPList[[1]],
                      rTS_Soybeans = rTSList[[2]], rTP_Soybeans = rTPList[[2]],
                      rTS_Sorghum = rTSList[[3]], rTP_Sorghum = rTPList[[3]],
                      rTS_Millet = rTSList[[4]], rTP_Millet = rTPList[[4]])
  ## Extreme Heat
  dfValsDiff = dfVals[dfVals$tmax == 40,] - dfVals[dfVals$tmax == 25,]
  #Maize
  dfValsDiff$rTS_Maize - dfValsDiff$rTP_Maize 
  (dfValsDiff$rTS_Maize - dfValsDiff$rTP_Maize) / dfValsDiff$rTP_Maize * 100
  #Soybeans
  dfValsDiff$rTS_Soybeans - dfValsDiff$rTP_Soybeans
  (dfValsDiff$rTS_Soybeans - dfValsDiff$rTP_Soybeans) / dfValsDiff$rTP_Soybeans * 100
  #Sorghum
  dfValsDiff$rTS_Sorghum - dfValsDiff$rTP_Sorghum
  (dfValsDiff$rTS_Sorghum - dfValsDiff$rTP_Sorghum) / dfValsDiff$rTP_Sorghum * 100
  #Millet
  dfValsDiff$rTS_Millet - dfValsDiff$rTP_Millet 
  (dfValsDiff$rTS_Millet - dfValsDiff$rTP_Millet) / dfValsDiff$rTP_Millet * 100
  
  ## Optimal Tmax
  #Maize
  dfVals$tmax[which.max(dfVals$rTS_Maize)] #24.5
  dfVals$tmax[which.max(dfVals$rTP_Maize)] #22
  dfVals$tmax[which.max(dfVals$rTS_Maize)] - dfVals$tmax[which.max(dfVals$rTP_Maize)]
  #Soybeans
  dfVals$tmax[which.max(dfVals$rTS_Soybeans)] #26.3
  dfVals$tmax[which.max(dfVals$rTP_Soybeans)] #24.6
  dfVals$tmax[which.max(dfVals$rTS_Soybeans)] - dfVals$tmax[which.max(dfVals$rTP_Soybeans)]
  #Sorghum
  dfVals$tmax[which.max(dfVals$rTS_Sorghum)] #29.1
  dfVals$tmax[which.max(dfVals$rTP_Sorghum)] #27.1
  dfVals$tmax[which.max(dfVals$rTS_Sorghum)] - dfVals$tmax[which.max(dfVals$rTP_Sorghum)]
  #Millet
  dfVals$tmax[which.max(dfVals$rTS_Millet)] #19.5
  dfVals$tmax[which.max(dfVals$rTP_Millet)] #19.6
  dfVals$tmax[which.max(dfVals$rTS_Millet)] - dfVals$tmax[which.max(dfVals$rTP_Millet)]
  ### --- calculation end
  
  offsetAdd = 0.5
  offsetScale = 0.6
  
  if(is_pR2){
    offsetAdd = 0.9
    offsetScale = 0.8
  }
  
  ### --- SM --- ###
  #SM all together but vertically offset: 
  #add crop 1
  offset1 = 8*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2)
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[1]], ymax = rS_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  g = g + geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3)
  
  #add crop 2
  offset2 = 6*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) 
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[2]], ymax = rS_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  g = g + geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3)
  
  #add crop 3
  offset3 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3)
  g = g +   geom_line(mapping = aes(x = sm, y = rSList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[3]], ymax = rS_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  
  
  #add crop 4
  offset4 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset4, size = 0.2)  +
    geom_hline(yintercept = dotlineoffset + offset4, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset4, size = 0.2, linetype = 3)
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[4]], color = cropNsS[4]), linetype = 1, position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[4]], ymax = rS_ubsList[[4]], fill = cropNsS[4]) , alpha = polyalpha,
                      position = position_nudge(y = offset4)) 
  
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(smrz, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(11,"BrBG")[c(7,8,9,10,11)]
  colors_hist_S <- c("1Maize" = bg[2], "2Soybeans" = bg[3], "3Sorghum" = bg[4], "4Millet" = bg[5])
  g = g + scale_fill_manual(values = colors_hist_S) 
  g = g + scale_color_manual(values = colors_hist_S)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Soil moisture (cm^3cm^-3)") + ylab("Crop yield (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggsm_stack = g
  
  
  ### --- Pr --- ###
  #add crop 1
  offset1 = 8*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[1]], ymax = rP_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  
  #add crop 2
  offset2 = 6*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[2]], ymax = rP_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  
  #add crop 3
  offset3 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[3]], ymax = rP_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  
  
  #add crop 4
  offset4 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset4, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset4, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset4, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[4]], color = cropNsS[4]), linetype = 1, position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[4]], ymax = rP_ubsList[[4]], fill = cropNsS[4]) , alpha = polyalpha,
                      position = position_nudge(y = offset4)) 
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(precip, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(9,"Blues")[c(4,5,7,9)]
  colors_hist_P <- c("1Maize" = bg[1], "2Soybeans" = bg[2], "3Sorghum" = bg[3], "4Millet" = bg[4])
  g = g + scale_fill_manual(values = colors_hist_P) 
  g = g + scale_color_manual(values = colors_hist_P)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Precipitation (mm)") + ylab("Crop yield (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggpr_stack = g
  
  
  ### --- Tmax --- ###
  #add crop 1
  offset1 = 8*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[1]], ymax = rTS_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[1]], color = cropNsS[1]), linetype = 2, position = position_nudge(y = offset1)) 
  
  #add crop 2
  offset2 = 6*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[2]], ymax = rTS_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  g = g +  geom_line(mapping = aes(x = tmax, y = rTPList[[2]], color = cropNsS[2]), linetype = 2, position = position_nudge(y = offset2)) 
  
  #add crop 3
  offset3 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[3]], ymax = rTS_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[3]], color = cropNsS[3]), linetype = 2, position = position_nudge(y = offset3)) 
  
  
  #add crop 4
  offset4 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset4, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset4, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset4, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[4]], color = cropNsS[4]), linetype = 1, position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[4]], ymax = rTS_ubsList[[4]], fill = cropNsS[4]) , alpha = polyalpha,
                      position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[4]], color = cropNsS[4]), linetype = 2, position = position_nudge(y = offset4)) 
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(tmax, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(9,"YlOrRd")[c(3,5,7,8,9)]
  colors_hist_T <- c("1Maize" = bg[1], "2Soybeans" = bg[2], "3Sorghum" = bg[3], "4Millet" = bg[5])
  g = g + scale_fill_manual(values = colors_hist_T) 
  g = g + scale_color_manual(values = colors_hist_T)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Temperature maximum (C)") + ylab("Crop yield change (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggtmax_stack = g
  
  
  ### formatting
  
  ggtmax_stack = ggtmax_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                              offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                              offset3, offset3 + dotlineoffset, offset3 - dotlineoffset,
                                                              offset4, offset4 + dotlineoffset, offset4 - dotlineoffset),
                                                   labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset)) +
    coord_cartesian(ylim = c(0,9.5*offsetScale))
  
  ggpr_stack = ggpr_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                          offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                          offset3, offset3 + dotlineoffset, offset3 - dotlineoffset,
                                                          offset4, offset4 + dotlineoffset, offset4 - dotlineoffset),
                                               labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset))+
    coord_cartesian(ylim = c(0,9.5*offsetScale))
  
  ggsm_stack = ggsm_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                          offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                          offset3, offset3 + dotlineoffset, offset3 - dotlineoffset,
                                                          offset4, offset4 + dotlineoffset, offset4 - dotlineoffset),
                                               labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset)) +
    coord_cartesian(ylim = c(0,9.5*offsetScale))
  
  
  
  ggtmax_stack = ggtmax_stack + annotate(geom = "text", x = 13, y = offset1+dotlineoffset+0.01, label = "Maize", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset2+dotlineoffset+0.01, label = "Soybeans", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset3+dotlineoffset+0.01, label = "Sorghum", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset4+dotlineoffset+0.01, label = "Millet", color = "black", hjust = 0, vjust = 0, angle =0)
  
  pg_stack_TPS = plot_grid(ggtmax_stack, ggsm_stack,ggpr_stack, nrow = 1)
  
  
  
  if(returnGGList){
    if(makeCombinedPlot){
      return(list(rtmax, rprcp, rsm, htmax, hprcp, hsm))
    }  
    if(makeStackedPlots){
      return(list(ggtmax_stack, ggpr_stack, ggsm_stack))
    } 
  } else {
    return(pg_stack_TPS)
  }
}



plotIndividualModels_BarOatsWheat = function(mTPr, mTSr, runStr, crop, gs_length, cvartype = "daily", returnGGList = F, plotSMBounds = T, makeStackedPlots = T, makeCombinedPlot=F) {
  #load daily data
  if(crop == "allCrops") {
    print("loading combined crop data...")
    hd = readRDS(paste0("Data/allCrops_10pctCropW_all10pct2007_2007_2018.rda"))
    hd = hd[hd$crop != "Maize",]
    hd = hd[hd$crop != "Soybeans",]
    hd = hd[hd$crop != "Sorghum",]
    hd = hd[hd$crop != "Millet",]
    
  }
  
  uq = 0.995
  lq = 0.005
  
  uq_precip = 0.99
  lq_precip = 0.01
  
  hd$precip[hd$precip > quantile(hd$precip,uq_precip, na.rm=T)] = quantile(hd$precip,uq_precip, na.rm=T)
  hd$precip[hd$precip < quantile(hd$precip,lq_precip, na.rm=T)] = quantile(hd$precip,lq_precip, na.rm=T)
  
  hd$tmax[hd$tmax > quantile(hd$tmax,uq, na.rm=T)] = quantile(hd$tmax,uq, na.rm=T)
  hd$tmax[hd$tmax < quantile(hd$tmax,lq, na.rm=T)] = quantile(hd$tmax,lq, na.rm=T)
  
  hd$smrz[hd$smrz > quantile(hd$smrz,uq, na.rm=T)] = quantile(hd$smrz,uq, na.rm=T)
  hd$smrz[hd$smrz < quantile(hd$smrz,lq, na.rm=T)] = quantile(hd$smrz,lq, na.rm=T)
  
  
  #Colors:
  colors_hist <- c("cropBarley" = "#78C59D", "cropOats" = "black", "cropWheat" = "#C63C3C")
  
  #already winsorized above so no need to clip
  smRange = quantile(hd$smrz, c(0,1), na.rm=T)
  prcpRange = quantile(hd$precip, c(0,1), na.rm=T)
  tmaxRange = quantile(hd$tmax, c(0,1), na.rm=T)
  tmaxRange = c(11,40) # is 11.04273 40.06401, cleaner this way.
  
  ### Make responses and uncertainty ###
  sm = seq(smRange[1],smRange[2],0.01)
  #create a datatable with all the features and then multiply the relevant ones
  sm_rcs = genRecenteredXVals_RCS(x = sm, xRef = mean(hd$smrz,na.rm=T), k = c(0.1,0.2,0.3,0.4))
  smdf = cbind(sm,sm_rcs,sm^2)
  colnames(smdf) = c("smval_forplot","smrz_day", "smrz_day_RCS_k4_1", "smrz_day_RCS_k4_2","smrz2_day")
  
  #For each crop or crop group:
  cropNsS = unique(grep("crop",unlist(strsplit(rownames(mTSr$beta), ":")),value=T))
  #reorder
  rSList = list()
  rS_lbsList = list()
  rS_ubsList = list()
  ri = 1
  for(cropN in cropNsS){
    #Get Response
    mTSr$beta_c = mTSr$beta[grepl(cropN, rownames(mTSr$beta))]
    mTSr$beta_c_names = rownames(mTSr$beta)[grepl(cropN, rownames(mTSr$beta))]
    columnNames = unlist(strsplit(grep("smrz",mTSr$beta_c_names, value = T),":"))
    columnNames = grep("smrz",columnNames, value = T)
    rSList[[ri]] = as.matrix(smdf[,columnNames]) %*% as.matrix(mTSr$beta_c[grepl("smrz",mTSr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTSr$clustervcv, grep("smrz",mTSr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(smdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rS_lbsList[[ri]] = rSList[[ri]] - length
    rS_ubsList[[ri]] = rSList[[ri]] + length
    #increment
    ri = ri + 1
  }
  
  
  ### --- PR
  ### Precip ###
  prcp = seq(prcpRange[1],prcpRange[2],.1)
  #create a datatable with all the features and then multiply the relevant ones
  prcp_rcs = genRecenteredXVals_RCS(x = prcp, xRef = 10, k = c(1,20,50,150))
  prcpdf = cbind(prcp^2, prcp_rcs)
  colnames(prcpdf) = c("prcp2_day", "prcp_day", "prcp_day_RCS_k4_1", "prcp_day_RCS_k4_2")
  
  #For each crop or crop group:
  cropNsP = unique(grep("crop",unlist(strsplit(rownames(mTPr$beta), ":")),value=T))
  #reorder
  cropN = "Maize"
  rPList = list()
  rP_lbsList = list()
  rP_ubsList = list()
  ri = 1
  for(cropN in cropNsP){
    mTPr$beta_c = mTPr$beta[grepl(cropN, rownames(mTPr$beta))]
    mTPr$beta_c_names = rownames(mTPr$beta)[grepl(cropN, rownames(mTPr$beta))]
    columnNames = unlist(strsplit(grep("prcp",mTPr$beta_c_names, value = T),":"))
    columnNames = grep("prcp",columnNames, value = T)
    rPList[[ri]] = as.matrix(prcpdf[,columnNames]) %*% as.matrix(mTPr$beta_c[grepl("prcp",mTPr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTPr$clustervcv, grep("prcp",mTPr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(prcpdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rP_lbsList[[ri]] = rPList[[ri]] - length
    rP_ubsList[[ri]] = rPList[[ri]] + length
    ri = ri + 1
  }
  
  ### --- Tmax
  tmaxCentVal = 20
  tmax = seq(tmaxRange[1],tmaxRange[2],0.1)
  #create a datatable with all the features and then multiply the relevant ones
  tmax_rcs_cent = genRecenteredXVals_RCS(x = tmax, xRef = tmaxCentVal, k = c(10,20,27,35))
  tmax_rcs_cent = tmax_rcs_cent[,-1]
  tmax_poly_cent = genRecenteredXVals_polynomial(tmax,tmaxCentVal,2)
  tmaxdf = cbind(tmax_poly_cent, tmax_rcs_cent)
  colnames(tmaxdf) = c("tmax_day", "tmax2_day", "tmax_day_RCS_k4_1", "tmax_day_RCS_k4_2")
  
  #For each crop or crop group:
  cropNsTP = unique(grep("crop",unlist(strsplit(rownames(mTPr$beta), ":")),value=T))
  #reorder
  cropN = "Maize"
  rTPList = list()
  rTP_lbsList = list()
  rTP_ubsList = list()
  ri = 1
  for(cropN in cropNsTP){
    mTPr$beta_c = mTPr$beta[grepl(cropN, rownames(mTPr$beta))]
    mTPr$beta_c_names = rownames(mTPr$beta)[grepl(cropN, rownames(mTPr$beta))]
    columnNames = unlist(strsplit(grep("tmax",mTPr$beta_c_names, value = T),":"))
    columnNames = grep("tmax",columnNames, value = T)
    rTPList[[ri]] = as.matrix(tmaxdf[,columnNames]) %*% as.matrix(mTPr$beta_c[grepl("tmax",mTPr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTPr$clustervcv, grep("tmax",mTPr$beta_c_names, value = T))
    length = 1.96 * sqrt(apply(X = as.matrix(tmaxdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rTP_lbsList[[ri]] = rTPList[[ri]] - length
    rTP_ubsList[[ri]] = rTPList[[ri]] + length
    ri = ri + 1
  }
  
  #For each crop or crop group:
  cropNsTS = unique(grep("crop",unlist(strsplit(rownames(mTSr$beta), ":")),value=T))
  #reorder
  cropN = "Maize"
  rTSList = list()
  rTS_lbsList = list()
  rTS_ubsList = list()
  ri = 1
  for(cropN in cropNsTS){
    mTSr$beta_c = mTSr$beta[grepl(cropN, rownames(mTSr$beta))]
    mTSr$beta_c_names = rownames(mTSr$beta)[grepl(cropN, rownames(mTSr$beta))]
    columnNames = unlist(strsplit(grep("tmax",mTSr$beta_c_names, value = T),":"))
    columnNames = grep("tmax",columnNames, value = T)
    rTSList[[ri]] = as.matrix(tmaxdf[,columnNames]) %*% as.matrix(mTSr$beta_c[grepl("tmax",mTSr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTSr$clustervcv, grep("tmax",mTSr$beta_c_names, value = T))
    length = 1.96 * sqrt(apply(X = as.matrix(tmaxdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rTS_lbsList[[ri]] = rTSList[[ri]] - length
    rTS_ubsList[[ri]] = rTSList[[ri]] + length
    ri = ri + 1
  }
  
  
  #################
  ### Plot ###
  #################
  
  ### --- Plot as a stack (Fig2)
  ###
  
  
  #This makes individual plots for each variable rather than combining them all together, which gets too messy. 
  polysize = 0.1
  polyalpha = 0.3
  dotlineoffset = 0.3
  
  #rename to drop the "crop"
  cropNsS = substr(cropNsS, 5, nchar(cropNsS))
  cropNsSnoNum = cropNsS
  cropNsS = paste0(1:3, cropNsS)
  
  hd$crop[hd$crop=="Barley"] = "1Barley"
  hd$crop[hd$crop=="Oats"] = "2Oats"
  hd$crop[hd$crop=="Wheat"] = "3Wheat"
  
  #Convert to daily response
  cgsi = 1
  for(cropN in cropNsSnoNum){
    rSList[[cgsi]] = log2Perc(rSList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rS_ubsList[[cgsi]] = log2Perc(rS_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rS_lbsList[[cgsi]] = log2Perc(rS_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rPList[[cgsi]] = log2Perc(rPList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rP_ubsList[[cgsi]] = log2Perc(rP_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rP_lbsList[[cgsi]] = log2Perc(rP_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rTSList[[cgsi]] = log2Perc(rTSList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTS_ubsList[[cgsi]] = log2Perc(rTS_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTS_lbsList[[cgsi]] = log2Perc(rTS_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rTPList[[cgsi]] = log2Perc(rTPList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTP_ubsList[[cgsi]] = log2Perc(rTP_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTP_lbsList[[cgsi]] = log2Perc(rTP_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    cgsi = cgsi + 1
  }
  
  
  offsetAdd = 0.5
  offsetScale = 0.6
  
  ### --- SM --- ###
  #SM all together but vertically offset: 
  #add crop 1
  offset1 = 6*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2)
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[1]], ymax = rS_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  g = g + geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3)
  
  #add crop 2
  offset2 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) 
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[2]], ymax = rS_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  g = g + geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3)
  
  #add crop 3
  offset3 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3)
  g = g +   geom_line(mapping = aes(x = sm, y = rSList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[3]], ymax = rS_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  
  
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(smrz, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(11,"BrBG")[c(7,8,9,10,11)]
  colors_hist_S <- c("1Barley" = bg[2], "2Oats" = bg[3], "3Wheat" = bg[4])
  g = g + scale_fill_manual(values = colors_hist_S) 
  g = g + scale_color_manual(values = colors_hist_S)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Soil moisture (cm^3cm^-3)") + ylab("Crop yield (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggsm_stack = g
  
  
  ### --- Pr --- ###
  #Pr all together but vertically offset: 
  #add crop 1
  offset1 = 6*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[1]], ymax = rP_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  
  #add crop 2
  offset2 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[2]], ymax = rP_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  
  #add crop 3
  offset3 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[3]], ymax = rP_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(precip, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(9,"Blues")[c(4,5,7,9)]
  colors_hist_P <- c("1Barley" = bg[1], "2Oats" = bg[2], "3Wheat" = bg[3])
  g = g + scale_fill_manual(values = colors_hist_P) 
  g = g + scale_color_manual(values = colors_hist_P)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Precipitation (mm)") + ylab("Crop yield (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggpr_stack = g
  
  
  ### --- Tmax --- ###
  #Tmax all together but vertically offset: 
  #add crop 1
  offset1 = 6*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[1]], ymax = rTS_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[1]], color = cropNsS[1]), linetype = 2, position = position_nudge(y = offset1)) 
  
  #add crop 2
  offset2 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[2]], ymax = rTS_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  g = g +  geom_line(mapping = aes(x = tmax, y = rTPList[[2]], color = cropNsS[2]), linetype = 2, position = position_nudge(y = offset2)) 
  
  #add crop 3
  offset3 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[3]], ymax = rTS_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[3]], color = cropNsS[3]), linetype = 2, position = position_nudge(y = offset3)) 
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(tmax, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(9,"YlOrRd")[c(3,5,7,8,9)]
  colors_hist_T <- c("1Barley" = bg[1], "2Oats" = bg[2], "3Wheat" = bg[3])
  g = g + scale_fill_manual(values = colors_hist_T) 
  g = g + scale_color_manual(values = colors_hist_T)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Temperature maximum (C)") + ylab("Crop yield change (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggtmax_stack = g
  
  
  ### formatting
  
  ggtmax_stack = ggtmax_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                              offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                              offset3, offset3 + dotlineoffset, offset3 - dotlineoffset),
                                                   labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset)) +
    coord_cartesian(ylim = c(0,7.5*offsetScale))
  
  ggpr_stack = ggpr_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                          offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                          offset3, offset3 + dotlineoffset, offset3 - dotlineoffset),
                                               labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset))+
    coord_cartesian(ylim = c(0,7.5*offsetScale))
  
  ggsm_stack = ggsm_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                          offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                          offset3, offset3 + dotlineoffset, offset3 - dotlineoffset),
                                               labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset)) +
    coord_cartesian(ylim = c(0,7.5*offsetScale))
  
  
  
  ggtmax_stack = ggtmax_stack + annotate(geom = "text", x = 13, y = offset1+dotlineoffset+0.01, label = "Barley", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset2+dotlineoffset+0.01, label = "Oats", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset3+dotlineoffset+0.01, label = "Wheat", color = "black", hjust = 0, vjust = 0, angle =0)
  
  pg_stack_TPS = plot_grid(ggtmax_stack, ggsm_stack,ggpr_stack, nrow = 1)
  
  
  
  if(returnGGList){
    if(makeCombinedPlot){
      return(list(rtmax, rprcp, rsm, htmax, hprcp, hsm))
    }  
    if(makeStackedPlots){
      return(list(ggtmax_stack, ggpr_stack, ggsm_stack))
    } 
  } else {
    return(pg_stack_TPS)
  }
}


plotIndividualModels_SeasonP = function(mTPr, mTSr, runStr, crop, gs_length, cvartype = "daily", returnGGList = F, plotSMBounds = T, makeStackedPlots = T, makeCombinedPlot=F, is_pR2=F, pKnots) {
  #load daily data
  if(crop == "allCrops") {
    print("loading combined crop data...")
    hd = readRDS(paste0("Data/allCrops_10pctCropW_all10pct2007_2007_2018.rda"))
    hd = hd[hd$crop != "Wheat",]
    hd = hd[hd$crop != "Barley",]
    hd = hd[hd$crop != "Oats",]
    
  }
  
  uq = 0.995
  lq = 0.005
  
  uq_precip = 0.99
  lq_precip = 0.01
  
  hd$precip[hd$precip > quantile(hd$precip,uq_precip, na.rm=T)] = quantile(hd$precip,uq_precip, na.rm=T)
  hd$precip[hd$precip < quantile(hd$precip,lq_precip, na.rm=T)] = quantile(hd$precip,lq_precip, na.rm=T)
  
  hd$tmax[hd$tmax > quantile(hd$tmax,uq, na.rm=T)] = quantile(hd$tmax,uq, na.rm=T)
  hd$tmax[hd$tmax < quantile(hd$tmax,lq, na.rm=T)] = quantile(hd$tmax,lq, na.rm=T)
  
  hd$smrz[hd$smrz > quantile(hd$smrz,uq, na.rm=T)] = quantile(hd$smrz,uq, na.rm=T)
  hd$smrz[hd$smrz < quantile(hd$smrz,lq, na.rm=T)] = quantile(hd$smrz,lq, na.rm=T)
  
  
  #Colors:
  colors_hist <- c("cropMaize" = "#78C59D", "cropSoybeans" = "black", "cropMillet" = "#C63C3C", "cropSorghum" = "4A48E7")
  
  #already winsorized above so no need to clip
  smRange = quantile(hd$smrz, c(0,1), na.rm=T)
  prcpRange = quantile(hd$precip, c(0,1), na.rm=T)
  tmaxRange = quantile(hd$tmax, c(0,1), na.rm=T)
  tmaxRange = c(11,40) # is 11.04273 40.06401, cleaner this way.
  
  ### Make responses and uncertainty ###
  sm = seq(smRange[1],smRange[2],0.01)
  #create a datatable with all the features and then multiply the relevant ones
  sm_rcs = genRecenteredXVals_RCS(x = sm, xRef = mean(hd$smrz,na.rm=T), k = c(0.1,0.2,0.3,0.4))
  smdf = cbind(sm,sm_rcs,sm^2)
  colnames(smdf) = c("smval_forplot","smrz_day", "smrz_day_RCS_k4_1", "smrz_day_RCS_k4_2","smrz2_day")
  
  #For each crop or crop group:
  cropNsS = unique(grep("crop",unlist(strsplit(rownames(mTSr$beta), ":")),value=T))
  #reorder
  cropNsS = cropNsS[c(1,4,3,2)]
  rSList = list()
  rS_lbsList = list()
  rS_ubsList = list()
  ri = 1
  for(cropN in cropNsS){
    #Get Response
    mTSr$beta_c = mTSr$beta[grepl(cropN, rownames(mTSr$beta))]
    mTSr$beta_c_names = rownames(mTSr$beta)[grepl(cropN, rownames(mTSr$beta))]
    columnNames = unlist(strsplit(grep("smrz",mTSr$beta_c_names, value = T),":"))
    columnNames = grep("smrz",columnNames, value = T)
    rSList[[ri]] = as.matrix(smdf[,columnNames]) %*% as.matrix(mTSr$beta_c[grepl("smrz",mTSr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTSr$clustervcv, grep("smrz",mTSr$beta_c_names, value = T))
    length = 1.96 * sqrt(apply(X = as.matrix(smdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rS_lbsList[[ri]] = rSList[[ri]] - length
    rS_ubsList[[ri]] = rSList[[ri]] + length
    #increment
    ri = ri + 1
  }
  
  
  ### --- PR
  ### Precip ###
  prcp = seq(0,10,.1)
  #create a datatable with all the features and then multiply the relevant ones
  
  #For each crop or crop group:
  cropNsP = unique(grep("crop",unlist(strsplit(rownames(mTPr$beta), ":")),value=T))
  #reorder
  cropNsP = cropNsP[c(1,4,3,2)]
  cropN = "Maize"
  rPList = list()
  rP_lbsList = list()
  rP_ubsList = list()
  ri = 1
  for(cropN in cropNsP){
    prcp_rcs = genRecenteredXVals_RCS(x = prcp, xRef = 2, k = pKnots[ri,])
    prcpdf = cbind(prcp^2, prcp_rcs)
    colnames(prcpdf) = c("prcp2_day", "prcp_day", "prcp_season_RCS_k4_1", "prcp_season_RCS_k4_2")
    mTPr$beta_c = mTPr$beta[grepl(cropN, rownames(mTPr$beta))]
    mTPr$beta_c_names = rownames(mTPr$beta)[grepl(cropN, rownames(mTPr$beta))]
    columnNames = unlist(strsplit(grep("prcp",mTPr$beta_c_names, value = T),":"))
    columnNames = grep("prcp",columnNames, value = T)
    rPList[[ri]] = as.matrix(prcpdf[,columnNames]) %*% as.matrix(mTPr$beta_c[grepl("prcp",mTPr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTPr$clustervcv, grep("prcp",mTPr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(prcpdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rP_lbsList[[ri]] = rPList[[ri]] - length
    rP_ubsList[[ri]] = rPList[[ri]] + length
    ri = ri + 1
  }
  
  ### --- Tmax
  tmaxCentVal = 20 
  tmax = seq(tmaxRange[1],tmaxRange[2],0.1)
  #create a datatable with all the features and then multiply the relevant ones
  tmax_rcs_cent = genRecenteredXVals_RCS(x = tmax, xRef = tmaxCentVal, k = c(10,20,27,35))
  tmax_rcs_cent = tmax_rcs_cent[,-1]
  tmax_poly_cent = genRecenteredXVals_polynomial(tmax,tmaxCentVal,2)
  tmaxdf = cbind(tmax_poly_cent, tmax_rcs_cent)
  colnames(tmaxdf) = c("tmax_day", "tmax2_day", "tmax_day_RCS_k4_1", "tmax_day_RCS_k4_2")
  
  #For each crop or crop group:
  cropNsTP = unique(grep("crop",unlist(strsplit(rownames(mTPr$beta), ":")),value=T))
  #reorder
  cropNsTP = cropNsTP[c(1,4,3,2)]
  cropN = "Maize"
  rTPList = list()
  rTP_lbsList = list()
  rTP_ubsList = list()
  ri = 1
  for(cropN in cropNsTP){
    mTPr$beta_c = mTPr$beta[grepl(cropN, rownames(mTPr$beta))]
    mTPr$beta_c_names = rownames(mTPr$beta)[grepl(cropN, rownames(mTPr$beta))]
    columnNames = unlist(strsplit(grep("tmax",mTPr$beta_c_names, value = T),":"))
    columnNames = grep("tmax",columnNames, value = T)
    rTPList[[ri]] = as.matrix(tmaxdf[,columnNames]) %*% as.matrix(mTPr$beta_c[grepl("tmax",mTPr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTPr$clustervcv, grep("tmax",mTPr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(tmaxdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rTP_lbsList[[ri]] = rTPList[[ri]] - length
    rTP_ubsList[[ri]] = rTPList[[ri]] + length
    ri = ri + 1
  }
  
  #For each crop or crop group:
  cropNsTS = unique(grep("crop",unlist(strsplit(rownames(mTSr$beta), ":")),value=T))
  #reorder
  cropNsTS = cropNsTS[c(1,4,3,2)]
  cropN = "Maize"
  rTSList = list()
  rTS_lbsList = list()
  rTS_ubsList = list()
  ri = 1
  for(cropN in cropNsTS){
    mTSr$beta_c = mTSr$beta[grepl(cropN, rownames(mTSr$beta))]
    mTSr$beta_c_names = rownames(mTSr$beta)[grepl(cropN, rownames(mTSr$beta))]
    columnNames = unlist(strsplit(grep("tmax",mTSr$beta_c_names, value = T),":"))
    columnNames = grep("tmax",columnNames, value = T)
    rTSList[[ri]] = as.matrix(tmaxdf[,columnNames]) %*% as.matrix(mTSr$beta_c[grepl("tmax",mTSr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTSr$clustervcv, grep("tmax",mTSr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(tmaxdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rTS_lbsList[[ri]] = rTSList[[ri]] - length
    rTS_ubsList[[ri]] = rTSList[[ri]] + length
    ri = ri + 1
  }
  
  
  #################
  ### Plot ###
  #################
  
  ### --- Plot as a stack
  
  #This makes individual plots for each variable rather than combining them all together, which gets too messy. 
  polysize = 0.1
  polyalpha = 0.3
  dotlineoffset = 0.3
  
  hd$crop[hd$crop == "Maize"] = "1Maize"
  hd$crop[hd$crop == "Soybeans"] = "2Soybeans"
  hd$crop[hd$crop == "Sorghum"] = "3Sorghum"
  hd$crop[hd$crop == "Millet"] = "4Millet"

  #rename to drop the "crop"
  cropNsS = substr(cropNsS, 5, nchar(cropNsS))
  cropNsSnoNum = cropNsS
  cropNsS = paste0(1:4, cropNsS)
  
  
  #Convert to daily response
  cgsi = 1
  for(cropN in cropNsSnoNum){
    rSList[[cgsi]] = log2Perc(rSList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rS_ubsList[[cgsi]] = log2Perc(rS_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rS_lbsList[[cgsi]] = log2Perc(rS_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rPList[[cgsi]] = log2Perc(rPList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rP_ubsList[[cgsi]] = log2Perc(rP_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rP_lbsList[[cgsi]] = log2Perc(rP_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rTSList[[cgsi]] = log2Perc(rTSList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTS_ubsList[[cgsi]] = log2Perc(rTS_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTS_lbsList[[cgsi]] = log2Perc(rTS_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rTPList[[cgsi]] = log2Perc(rTPList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTP_ubsList[[cgsi]] = log2Perc(rTP_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTP_lbsList[[cgsi]] = log2Perc(rTP_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    cgsi = cgsi + 1
  }
  
  ### Calculate how the responses change TS vs TP ###
  dfVals = data.frame(tmax = tmaxdf$tmax_day+20, rTS_Maize = rTSList[[1]], rTP_Maize = rTPList[[1]],
                      rTS_Soybeans = rTSList[[2]], rTP_Soybeans = rTPList[[2]],
                      rTS_Sorghum = rTSList[[3]], rTP_Sorghum = rTPList[[3]],
                      rTS_Millet = rTSList[[4]], rTP_Millet = rTPList[[4]])
  ## Extreme Heat
  dfValsDiff = dfVals[dfVals$tmax == 40,] - dfVals[dfVals$tmax == 25,]
  #Maize
  dfValsDiff$rTS_Maize - dfValsDiff$rTP_Maize 
  (dfValsDiff$rTS_Maize - dfValsDiff$rTP_Maize) / dfValsDiff$rTP_Maize * 100
  #Soybeans
  dfValsDiff$rTS_Soybeans - dfValsDiff$rTP_Soybeans
  (dfValsDiff$rTS_Soybeans - dfValsDiff$rTP_Soybeans) / dfValsDiff$rTP_Soybeans * 100
  #Sorghum
  dfValsDiff$rTS_Sorghum - dfValsDiff$rTP_Sorghum
  (dfValsDiff$rTS_Sorghum - dfValsDiff$rTP_Sorghum) / dfValsDiff$rTP_Sorghum * 100
  #Millet
  dfValsDiff$rTS_Millet - dfValsDiff$rTP_Millet 
  (dfValsDiff$rTS_Millet - dfValsDiff$rTP_Millet) / dfValsDiff$rTP_Millet * 100
  
  ## Optimal Tmax
  #Maize
  dfVals$tmax[which.max(dfVals$rTS_Maize)] #24.5
  dfVals$tmax[which.max(dfVals$rTP_Maize)] #22
  dfVals$tmax[which.max(dfVals$rTS_Maize)] - dfVals$tmax[which.max(dfVals$rTP_Maize)]
  #Soybeans
  dfVals$tmax[which.max(dfVals$rTS_Soybeans)] #26.3
  dfVals$tmax[which.max(dfVals$rTP_Soybeans)] #24.6
  dfVals$tmax[which.max(dfVals$rTS_Soybeans)] - dfVals$tmax[which.max(dfVals$rTP_Soybeans)]
  #Sorghum
  dfVals$tmax[which.max(dfVals$rTS_Sorghum)] #29.1
  dfVals$tmax[which.max(dfVals$rTP_Sorghum)] #27.1
  dfVals$tmax[which.max(dfVals$rTS_Sorghum)] - dfVals$tmax[which.max(dfVals$rTP_Sorghum)]
  #Millet
  dfVals$tmax[which.max(dfVals$rTS_Millet)] #19.5
  dfVals$tmax[which.max(dfVals$rTP_Millet)] #19.6
  dfVals$tmax[which.max(dfVals$rTS_Millet)] - dfVals$tmax[which.max(dfVals$rTP_Millet)]
  ### --- p-val calculation end
  
  
  
  offsetAdd = 0.5
  offsetScale = 0.6
  
  if(is_pR2){
    offsetAdd = 0.9
    offsetScale = 0.8
  }
  
  ### --- SM --- ###
  #SM all together but vertically offset: 
  #add crop 1
  offset1 = 8*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2)
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[1]], ymax = rS_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  g = g + geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3)
  
  #add crop 2
  offset2 = 6*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) 
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[2]], ymax = rS_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  g = g + geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3)
  
  #add crop 3
  offset3 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3)
  g = g +   geom_line(mapping = aes(x = sm, y = rSList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[3]], ymax = rS_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  
  
  #add crop 4
  offset4 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset4, size = 0.2)  +
    geom_hline(yintercept = dotlineoffset + offset4, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset4, size = 0.2, linetype = 3)
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[4]], color = cropNsS[4]), linetype = 1, position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[4]], ymax = rS_ubsList[[4]], fill = cropNsS[4]) , alpha = polyalpha,
                      position = position_nudge(y = offset4)) 
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(smrz, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  #Colors:
  bg = brewer.pal(11,"BrBG")[c(7,8,9,10,11)]
  colors_hist_S <- c("1Maize" = bg[2], "2Soybeans" = bg[3], "3Sorghum" = bg[4], "4Millet" = bg[5])
  g = g + scale_fill_manual(values = colors_hist_S) 
  g = g + scale_color_manual(values = colors_hist_S)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Soil moisture (cm^3cm^-3)") + ylab("Crop yield (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggsm_stack = g
  
  
  ### --- Pr --- ###
  #add crop 1
  offset1 = 8*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[1]], ymax = rP_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  
  #add crop 2
  offset2 = 6*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[2]], ymax = rP_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  
  #add crop 3
  offset3 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[3]], ymax = rP_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  #add crop 4
  offset4 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset4, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset4, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset4, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[4]], color = cropNsS[4]), linetype = 1, position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[4]], ymax = rP_ubsList[[4]], fill = cropNsS[4]) , alpha = polyalpha,
                      position = position_nudge(y = offset4)) 
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(precip, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(9,"Blues")[c(4,5,7,9)]
  colors_hist_P <- c("1Maize" = bg[1], "2Soybeans" = bg[2], "3Sorghum" = bg[3], "4Millet" = bg[4])
  g = g + scale_fill_manual(values = colors_hist_P) 
  g = g + scale_color_manual(values = colors_hist_P)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Precipitation (mm)") + ylab("Crop yield (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggpr_stack = g
  
  
  ### --- Tmax --- ###
  #add crop 1
  offset1 = 8*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[1]], ymax = rTS_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[1]], color = cropNsS[1]), linetype = 2, position = position_nudge(y = offset1)) 
  
  #add crop 2
  offset2 = 6*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[2]], ymax = rTS_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  g = g +  geom_line(mapping = aes(x = tmax, y = rTPList[[2]], color = cropNsS[2]), linetype = 2, position = position_nudge(y = offset2)) 
  
  #add crop 3
  offset3 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[3]], ymax = rTS_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[3]], color = cropNsS[3]), linetype = 2, position = position_nudge(y = offset3)) 
  
  
  #add crop 4
  offset4 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset4, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset4, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset4, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[4]], color = cropNsS[4]), linetype = 1, position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[4]], ymax = rTS_ubsList[[4]], fill = cropNsS[4]) , alpha = polyalpha,
                      position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[4]], color = cropNsS[4]), linetype = 2, position = position_nudge(y = offset4)) 
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(tmax, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(9,"YlOrRd")[c(3,5,7,8,9)]
  colors_hist_T <- c("1Maize" = bg[1], "2Soybeans" = bg[2], "3Sorghum" = bg[3], "4Millet" = bg[5])
  g = g + scale_fill_manual(values = colors_hist_T) 
  g = g + scale_color_manual(values = colors_hist_T)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Temperature maximum (C)") + ylab("Crop yield change (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggtmax_stack = g
  
  
  ### formatting
  
  ggtmax_stack = ggtmax_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                              offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                              offset3, offset3 + dotlineoffset, offset3 - dotlineoffset,
                                                              offset4, offset4 + dotlineoffset, offset4 - dotlineoffset),
                                                   labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset)) +
    coord_cartesian(ylim = c(0,9.5*offsetScale))
  
  ggpr_stack = ggpr_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                          offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                          offset3, offset3 + dotlineoffset, offset3 - dotlineoffset,
                                                          offset4, offset4 + dotlineoffset, offset4 - dotlineoffset),
                                               labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset))+
    coord_cartesian(ylim = c(0,9.5*offsetScale))
  
  ggsm_stack = ggsm_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                          offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                          offset3, offset3 + dotlineoffset, offset3 - dotlineoffset,
                                                          offset4, offset4 + dotlineoffset, offset4 - dotlineoffset),
                                               labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset)) +
    coord_cartesian(ylim = c(0,9.5*offsetScale))
  
  
  
  ggtmax_stack = ggtmax_stack + annotate(geom = "text", x = 13, y = offset1+dotlineoffset+0.01, label = "Maize", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset2+dotlineoffset+0.01, label = "Soybeans", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset3+dotlineoffset+0.01, label = "Sorghum", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset4+dotlineoffset+0.01, label = "Millet", color = "black", hjust = 0, vjust = 0, angle =0)
  
  pg_stack_TPS = plot_grid(ggtmax_stack, ggsm_stack,ggpr_stack, nrow = 1)
  
  if(returnGGList){
    if(makeCombinedPlot){
      return(list(rtmax, rprcp, rsm, htmax, hprcp, hsm))
    }  
    if(makeStackedPlots){
      return(list(ggtmax_stack, ggpr_stack, ggsm_stack))
    } 
  } else {
    return(pg_stack_TPS)
  }
}



plotIndividualModels_SeasonPQuad = function(mTPr, mTSr, runStr, crop, gs_length, cvartype = "daily", returnGGList = F, plotSMBounds = T, makeStackedPlots = T, makeCombinedPlot=F, is_pR2=F) {
  #load daily data
  if(crop == "allCrops") {
    print("loading combined crop data...")
    hd = readRDS(paste0("Data/allCrops_10pctCropW_all10pct2007_2007_2018.rda"))
    hd = hd[hd$crop != "Wheat",]
    hd = hd[hd$crop != "Barley",]
    hd = hd[hd$crop != "Oats",]
    
  }
  
  uq = 0.995
  lq = 0.005
  uq_precip = 0.99
  lq_precip = 0.01
  hd$precip[hd$precip > quantile(hd$precip,uq_precip, na.rm=T)] = quantile(hd$precip,uq_precip, na.rm=T)
  hd$precip[hd$precip < quantile(hd$precip,lq_precip, na.rm=T)] = quantile(hd$precip,lq_precip, na.rm=T)
  hd$tmax[hd$tmax > quantile(hd$tmax,uq, na.rm=T)] = quantile(hd$tmax,uq, na.rm=T)
  hd$tmax[hd$tmax < quantile(hd$tmax,lq, na.rm=T)] = quantile(hd$tmax,lq, na.rm=T)
  hd$smrz[hd$smrz > quantile(hd$smrz,uq, na.rm=T)] = quantile(hd$smrz,uq, na.rm=T)
  hd$smrz[hd$smrz < quantile(hd$smrz,lq, na.rm=T)] = quantile(hd$smrz,lq, na.rm=T)
  
  #Colors:
  colors_hist <- c("cropMaize" = "#78C59D", "cropSoybeans" = "black", "cropMillet" = "#C63C3C", "cropSorghum" = "4A48E7")
  
  #already winsorized above so no need to clip
  smRange = quantile(hd$smrz, c(0,1), na.rm=T)
  prcpRange = quantile(hd$precip, c(0,1), na.rm=T)
  tmaxRange = quantile(hd$tmax, c(0,1), na.rm=T)
  tmaxRange = c(11,40) # is 11.04273 40.06401, cleaner for other things this way.
  
  ### Make responses and uncertainty ###
  sm = seq(smRange[1],smRange[2],0.01)
  #create a datatable with all the features and then multiply the relevant ones
  sm_rcs = genRecenteredXVals_RCS(x = sm, xRef = mean(hd$smrz,na.rm=T), k = c(0.1,0.2,0.3,0.4))
  smdf = cbind(sm,sm_rcs,sm^2)
  colnames(smdf) = c("smval_forplot","smrz_day", "smrz_day_RCS_k4_1", "smrz_day_RCS_k4_2","smrz2_day")
  
  #For each crop or crop group:
  cropNsS = unique(grep("crop",unlist(strsplit(rownames(mTSr$beta), ":")),value=T))
  #reorder
  cropNsS = cropNsS[c(1,4,3,2)]
  rSList = list()
  rS_lbsList = list()
  rS_ubsList = list()
  ri = 1
  for(cropN in cropNsS){
    #Get Response
    mTSr$beta_c = mTSr$beta[grepl(cropN, rownames(mTSr$beta))]
    mTSr$beta_c_names = rownames(mTSr$beta)[grepl(cropN, rownames(mTSr$beta))]
    columnNames = unlist(strsplit(grep("smrz",mTSr$beta_c_names, value = T),":"))
    columnNames = grep("smrz",columnNames, value = T)
    rSList[[ri]] = as.matrix(smdf[,columnNames]) %*% as.matrix(mTSr$beta_c[grepl("smrz",mTSr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTSr$clustervcv, grep("smrz",mTSr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(smdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rS_lbsList[[ri]] = rSList[[ri]] - length
    rS_ubsList[[ri]] = rSList[[ri]] + length
    #increment
    ri = ri + 1
  }
  
  
  ### --- PR
  ### Precip ###
  prcp = seq(0,10,.1)
  #create a datatable with all the features and then multiply the relevant ones
  prcp_rcs = genRecenteredXVals_RCS(x = prcp, xRef = 0, k = c(1,20,50,150))
  prcpdf = cbind(prcp^2, prcp_rcs)
  colnames(prcpdf) = c("prcp2_season", "prcp_day", "prcp_day_RCS_k4_1", "prcp_day_RCS_k4_2")
  
  #For each crop or crop group:
  cropNsP = unique(grep("crop",unlist(strsplit(rownames(mTPr$beta), ":")),value=T))
  #reorder
  cropNsP = cropNsP[c(1,4,3,2)]
  cropN = "Maize"
  rPList = list()
  rP_lbsList = list()
  rP_ubsList = list()
  ri = 1
  for(cropN in cropNsP){
    mTPr$beta_c = mTPr$beta[grepl(cropN, rownames(mTPr$beta))]
    mTPr$beta_c_names = rownames(mTPr$beta)[grepl(cropN, rownames(mTPr$beta))]
    columnNames = unlist(strsplit(grep("prcp",mTPr$beta_c_names, value = T),":"))
    columnNames = grep("prcp",columnNames, value = T)
    rPList[[ri]] = as.matrix(prcpdf[,columnNames]) %*% as.matrix(mTPr$beta_c[grepl("prcp",mTPr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTPr$clustervcv, grep("prcp",mTPr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(prcpdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rP_lbsList[[ri]] = rPList[[ri]] - length
    rP_ubsList[[ri]] = rPList[[ri]] + length
    ri = ri + 1
  }
  
  ### --- Tmax
  tmaxCentVal = 20 #mean(hd$tmax,na.rm=T)
  tmax = seq(tmaxRange[1],tmaxRange[2],0.1)
  #create a datatable with all the features and then multiply the relevant ones
  tmax_rcs_cent = genRecenteredXVals_RCS(x = tmax, xRef = tmaxCentVal, k = c(10,20,27,35))
  tmax_rcs_cent = tmax_rcs_cent[,-1]
  tmax_poly_cent = genRecenteredXVals_polynomial(tmax,tmaxCentVal,2)
  tmaxdf = cbind(tmax_poly_cent, tmax_rcs_cent)
  colnames(tmaxdf) = c("tmax_day", "tmax2_day", "tmax_day_RCS_k4_1", "tmax_day_RCS_k4_2")
  
  #For each crop or crop group:
  cropNsTP = unique(grep("crop",unlist(strsplit(rownames(mTPr$beta), ":")),value=T))
  #reorder
  cropNsTP = cropNsTP[c(1,4,3,2)]
  cropN = "Maize"
  rTPList = list()
  rTP_lbsList = list()
  rTP_ubsList = list()
  ri = 1
  for(cropN in cropNsTP){
    mTPr$beta_c = mTPr$beta[grepl(cropN, rownames(mTPr$beta))]
    mTPr$beta_c_names = rownames(mTPr$beta)[grepl(cropN, rownames(mTPr$beta))]
    columnNames = unlist(strsplit(grep("tmax",mTPr$beta_c_names, value = T),":"))
    columnNames = grep("tmax",columnNames, value = T)
    rTPList[[ri]] = as.matrix(tmaxdf[,columnNames]) %*% as.matrix(mTPr$beta_c[grepl("tmax",mTPr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTPr$clustervcv, grep("tmax",mTPr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(tmaxdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rTP_lbsList[[ri]] = rTPList[[ri]] - length
    rTP_ubsList[[ri]] = rTPList[[ri]] + length
    ri = ri + 1
  }
  
  #For each crop or crop group:
  cropNsTS = unique(grep("crop",unlist(strsplit(rownames(mTSr$beta), ":")),value=T))
  #reorder
  cropNsTS = cropNsTS[c(1,4,3,2)]
  cropN = "Maize"
  rTSList = list()
  rTS_lbsList = list()
  rTS_ubsList = list()
  ri = 1
  for(cropN in cropNsTS){
    mTSr$beta_c = mTSr$beta[grepl(cropN, rownames(mTSr$beta))]
    mTSr$beta_c_names = rownames(mTSr$beta)[grepl(cropN, rownames(mTSr$beta))]
    columnNames = unlist(strsplit(grep("tmax",mTSr$beta_c_names, value = T),":"))
    columnNames = grep("tmax",columnNames, value = T)
    rTSList[[ri]] = as.matrix(tmaxdf[,columnNames]) %*% as.matrix(mTSr$beta_c[grepl("tmax",mTSr$beta_c_names)])
    #Get uncertainty
    vcov = getVcov(mTSr$clustervcv, grep("tmax",mTSr$beta_c_names, value = T)) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(tmaxdf[,columnNames]), FUN = calcVariance, MARGIN = 1, vcov))
    rTS_lbsList[[ri]] = rTSList[[ri]] - length
    rTS_ubsList[[ri]] = rTSList[[ri]] + length
    ri = ri + 1
  }
  
  
  #################
  ### Plot ###
  #################

  #This makes individual plots for each variable rather than combining them all together, which gets too messy. 
  polysize = 0.1
  polyalpha = 0.3
  dotlineoffset = 0.3
  
  hd$crop[hd$crop == "Maize"] = "1Maize"
  hd$crop[hd$crop == "Soybeans"] = "2Soybeans"
  hd$crop[hd$crop == "Sorghum"] = "3Sorghum"
  hd$crop[hd$crop == "Millet"] = "4Millet"
  
  #rename to drop the "crop"
  cropNsS = substr(cropNsS, 5, nchar(cropNsS))
  cropNsSnoNum = cropNsS
  cropNsS = paste0(1:4, cropNsS)
  
  #Convert to daily response
  cgsi = 1
  for(cropN in cropNsSnoNum){
    rSList[[cgsi]] = log2Perc(rSList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rS_ubsList[[cgsi]] = log2Perc(rS_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rS_lbsList[[cgsi]] = log2Perc(rS_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rPList[[cgsi]] = log2Perc(rPList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rP_ubsList[[cgsi]] = log2Perc(rP_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rP_lbsList[[cgsi]] = log2Perc(rP_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rTSList[[cgsi]] = log2Perc(rTSList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTS_ubsList[[cgsi]] = log2Perc(rTS_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTS_lbsList[[cgsi]] = log2Perc(rTS_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    
    rTPList[[cgsi]] = log2Perc(rTPList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTP_ubsList[[cgsi]] = log2Perc(rTP_ubsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    rTP_lbsList[[cgsi]] = log2Perc(rTP_lbsList[[cgsi]] / gs_length[gs_length$crop==cropN]$gs_len)
    cgsi = cgsi + 1
  }
  
  ### Calculate how the responses change TS vs TP ###
  dfVals = data.frame(tmax = tmaxdf$tmax_day+20, rTS_Maize = rTSList[[1]], rTP_Maize = rTPList[[1]],
                      rTS_Soybeans = rTSList[[2]], rTP_Soybeans = rTPList[[2]],
                      rTS_Sorghum = rTSList[[3]], rTP_Sorghum = rTPList[[3]],
                      rTS_Millet = rTSList[[4]], rTP_Millet = rTPList[[4]])
  ## Extreme Heat
  dfValsDiff = dfVals[dfVals$tmax == 40,] - dfVals[dfVals$tmax == 25,]
  #Maize
  dfValsDiff$rTS_Maize - dfValsDiff$rTP_Maize 
  (dfValsDiff$rTS_Maize - dfValsDiff$rTP_Maize) / dfValsDiff$rTP_Maize * 100
  #Soybeans
  dfValsDiff$rTS_Soybeans - dfValsDiff$rTP_Soybeans
  (dfValsDiff$rTS_Soybeans - dfValsDiff$rTP_Soybeans) / dfValsDiff$rTP_Soybeans * 100
  #Sorghum
  dfValsDiff$rTS_Sorghum - dfValsDiff$rTP_Sorghum
  (dfValsDiff$rTS_Sorghum - dfValsDiff$rTP_Sorghum) / dfValsDiff$rTP_Sorghum * 100
  #Millet
  dfValsDiff$rTS_Millet - dfValsDiff$rTP_Millet 
  (dfValsDiff$rTS_Millet - dfValsDiff$rTP_Millet) / dfValsDiff$rTP_Millet * 100
  
  ## Optimal Tmax
  #Maize
  dfVals$tmax[which.max(dfVals$rTS_Maize)] #24.5
  dfVals$tmax[which.max(dfVals$rTP_Maize)] #22
  dfVals$tmax[which.max(dfVals$rTS_Maize)] - dfVals$tmax[which.max(dfVals$rTP_Maize)]
  #Soybeans
  dfVals$tmax[which.max(dfVals$rTS_Soybeans)] #26.3
  dfVals$tmax[which.max(dfVals$rTP_Soybeans)] #24.6
  dfVals$tmax[which.max(dfVals$rTS_Soybeans)] - dfVals$tmax[which.max(dfVals$rTP_Soybeans)]
  #Sorghum
  dfVals$tmax[which.max(dfVals$rTS_Sorghum)] #29.1
  dfVals$tmax[which.max(dfVals$rTP_Sorghum)] #27.1
  dfVals$tmax[which.max(dfVals$rTS_Sorghum)] - dfVals$tmax[which.max(dfVals$rTP_Sorghum)]
  #Millet
  dfVals$tmax[which.max(dfVals$rTS_Millet)] #19.5
  dfVals$tmax[which.max(dfVals$rTP_Millet)] #19.6
  dfVals$tmax[which.max(dfVals$rTS_Millet)] - dfVals$tmax[which.max(dfVals$rTP_Millet)]
  ### --- p-val calculation end
  
  offsetAdd = 0.5
  offsetScale = 0.6
  
  if(is_pR2){
    offsetAdd = 0.9
    offsetScale = 0.8
  }
  
  ### --- SM --- ###
  #SM all together but vertically offset: 
  #add crop 1
  offset1 = 8*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2)
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[1]], ymax = rS_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  g = g + geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3)
  
  #add crop 2
  offset2 = 6*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) 
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[2]], ymax = rS_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  g = g + geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3)
  
  #add crop 3
  offset3 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3)
  g = g +   geom_line(mapping = aes(x = sm, y = rSList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[3]], ymax = rS_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  
  
  #add crop 4
  offset4 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset4, size = 0.2)  +
    geom_hline(yintercept = dotlineoffset + offset4, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset4, size = 0.2, linetype = 3)
  g = g + geom_line(mapping = aes(x = sm, y = rSList[[4]], color = cropNsS[4]), linetype = 1, position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = sm, y = rS_lbsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_line(mapping = aes(x = sm, y = rS_ubsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[4]], ymax = rS_ubsList[[4]], fill = cropNsS[4]) , alpha = polyalpha,
                      position = position_nudge(y = offset4)) 
  
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(smrz, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(11,"BrBG")[c(7,8,9,10,11)]
  colors_hist_S <- c("1Maize" = bg[2], "2Soybeans" = bg[3], "3Sorghum" = bg[4], "4Millet" = bg[5])
  g = g + scale_fill_manual(values = colors_hist_S) 
  g = g + scale_color_manual(values = colors_hist_S)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Soil moisture (cm^3cm^-3)") + ylab("Crop yield (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggsm_stack = g
  
  
  ### --- Pr --- ###
  #add crop 1
  offset1 = 8*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[1]], ymax = rP_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  
  #add crop 2
  offset2 = 6*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[2]], ymax = rP_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  
  #add crop 3
  offset3 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[3]], ymax = rP_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  
  
  #add crop 4
  offset4 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset4, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset4, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset4, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = prcp, y = rPList[[4]], color = cropNsS[4]), linetype = 1, position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = prcp, y = rP_lbsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_line(mapping = aes(x = prcp, y = rP_ubsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[4]], ymax = rP_ubsList[[4]], fill = cropNsS[4]) , alpha = polyalpha,
                      position = position_nudge(y = offset4)) 
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(precip, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(9,"Blues")[c(4,5,7,9)]
  colors_hist_P <- c("1Maize" = bg[1], "2Soybeans" = bg[2], "3Sorghum" = bg[3], "4Millet" = bg[4])
  g = g + scale_fill_manual(values = colors_hist_P) 
  g = g + scale_color_manual(values = colors_hist_P)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Precipitation (mm)") + ylab("Crop yield (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggpr_stack = g
  
  
  ### --- Tmax --- ###
  #add crop 1
  offset1 = 8*offsetScale + offsetAdd
  g = ggplot() + geom_hline(yintercept = 0 + offset1, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset1, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset1, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[1]], color = cropNsS[1]), linetype = 1, position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[1]], color = cropNsS[1]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset1))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[1]], ymax = rTS_ubsList[[1]], fill = cropNsS[1]) , alpha = polyalpha,
                      position = position_nudge(y = offset1)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[1]], color = cropNsS[1]), linetype = 2, position = position_nudge(y = offset1)) 
  
  #add crop 2
  offset2 = 6*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset2, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset2, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset2, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[2]], color = cropNsS[2]), linetype = 1, position = position_nudge(y = offset2)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[2]], color = cropNsS[2]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset2))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[2]], ymax = rTS_ubsList[[2]], fill = cropNsS[2]) , alpha = polyalpha,
                      position = position_nudge(y = offset2)) 
  g = g +  geom_line(mapping = aes(x = tmax, y = rTPList[[2]], color = cropNsS[2]), linetype = 2, position = position_nudge(y = offset2)) 
  
  #add crop 3
  offset3 = 4*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset3, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset3, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset3, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[3]], color = cropNsS[3]), linetype = 1, position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[3]], color = cropNsS[3]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset3))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[3]], ymax = rTS_ubsList[[3]], fill = cropNsS[3]) , alpha = polyalpha,
                      position = position_nudge(y = offset3)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[3]], color = cropNsS[3]), linetype = 2, position = position_nudge(y = offset3)) 
  
  
  #add crop 4
  offset4 = 2*offsetScale + offsetAdd
  g = g + geom_hline(yintercept = 0 + offset4, size = 0.2) + 
    geom_hline(yintercept = dotlineoffset + offset4, size = 0.2, linetype = 3) + 
    geom_hline(yintercept = -dotlineoffset + offset4, size = 0.2, linetype = 3) +
    geom_line(mapping = aes(x = tmax, y = rTSList[[4]], color = cropNsS[4]), linetype = 1, position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_lbsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_line(mapping = aes(x = tmax, y = rTS_ubsList[[4]], color = cropNsS[4]), linetype = 1, size = polysize, alpha = polyalpha,
                    position = position_nudge(y = offset4))
  g = g + geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[4]], ymax = rTS_ubsList[[4]], fill = cropNsS[4]) , alpha = polyalpha,
                      position = position_nudge(y = offset4)) 
  g = g + geom_line(mapping = aes(x = tmax, y = rTPList[[4]], color = cropNsS[4]), linetype = 2, position = position_nudge(y = offset4)) 
  
  
  #add histogram:
  g = g + geom_histogram(data = hd, mapping = aes(tmax, y = ..count.. / max(..count..)/2, fill = crop),  
                         bins = 80,  position = position_stack())
  
  #Colors:
  bg = brewer.pal(9,"YlOrRd")[c(3,5,7,8,9)]
  colors_hist_T <- c("1Maize" = bg[1], "2Soybeans" = bg[2], "3Sorghum" = bg[3], "4Millet" = bg[5])
  g = g + scale_fill_manual(values = colors_hist_T) 
  g = g + scale_color_manual(values = colors_hist_T)
  
  #Labels...etc
  g = g  + theme_classic() + xlab("Temperature maximum (C)") + ylab("Crop yield change (%)") +
    theme(legend.position = "bottom", legend.title = element_blank())
  
  ggtmax_stack = g
  
  
  ### formatting
  
  ggtmax_stack = ggtmax_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                              offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                              offset3, offset3 + dotlineoffset, offset3 - dotlineoffset,
                                                              offset4, offset4 + dotlineoffset, offset4 - dotlineoffset),
                                                   labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                              0 , 0 + dotlineoffset, 0 - dotlineoffset)) +
    coord_cartesian(ylim = c(0,9.5*offsetScale))
  
  ggpr_stack = ggpr_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                          offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                          offset3, offset3 + dotlineoffset, offset3 - dotlineoffset,
                                                          offset4, offset4 + dotlineoffset, offset4 - dotlineoffset),
                                               labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset))+
    coord_cartesian(ylim = c(0,9.5*offsetScale))
  
  ggsm_stack = ggsm_stack + scale_y_continuous(breaks = c(offset1, offset1 + dotlineoffset, offset1 - dotlineoffset, 
                                                          offset2, offset2 + dotlineoffset, offset2 - dotlineoffset,
                                                          offset3, offset3 + dotlineoffset, offset3 - dotlineoffset,
                                                          offset4, offset4 + dotlineoffset, offset4 - dotlineoffset),
                                               labels = c(0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset,
                                                          0 , 0 + dotlineoffset, 0 - dotlineoffset)) +
    coord_cartesian(ylim = c(0,9.5*offsetScale))
  
  
  
  ggtmax_stack = ggtmax_stack + annotate(geom = "text", x = 13, y = offset1+dotlineoffset+0.01, label = "Maize", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset2+dotlineoffset+0.01, label = "Soybeans", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset3+dotlineoffset+0.01, label = "Sorghum", color = "black", hjust = 0, vjust = 0, angle =0) +
    annotate(geom = "text", x = 13, y = offset4+dotlineoffset+0.01, label = "Millet", color = "black", hjust = 0, vjust = 0, angle =0)
  
  pg_stack_TPS = plot_grid(ggtmax_stack, ggsm_stack,ggpr_stack, nrow = 1)
  
  if(returnGGList){
    if(makeCombinedPlot){
      return(list(rtmax, rprcp, rsm, htmax, hprcp, hsm))
    }  
    if(makeStackedPlots){
      return(list(ggtmax_stack, ggpr_stack, ggsm_stack))
    } 
  } else {
    return(pg_stack_TPS)
  }
}


getTSTP_Pval = function(modTS, modTP, cropN = NA, printV=F){
  varnames = grep("tmax", rownames(modTS$coeff),value=T)
  if(!is.na(cropN)) varnames = grep(cropN,varnames, value=T)
  
  #get T coeffs for TP model
  cTP = modTP$coefficients[rownames(modTP$coeff) %in% varnames]
  
  hm = diag(length(modTS$coeff[rownames(modTS$coeff) %in% varnames]))
  lh = linearHypothesis(model = modTS, hm, cTP, vcov. = modTS$clustervcv[varnames,varnames], coef.=modTS$coeff[rownames(modTS$coeff) %in% varnames], test = "F")
  if(printV){
    print("----------------------")
    print(cropN)
    print(lh$`Pr(>F)`[2])
    print("----------------------")
  }
  return(signif(lh$`Pr(>F)`[2],3))
}


#Get p-values for T and S responses in TS model: 
get_Pval = function(modTS, varname = "tmax", printV=T){
  varnames = grep(varname, rownames(modTS$coeff),value=T)
  
  #get T coeffs for TP model
  cV = modTS$coefficients[rownames(modTS$coeff) %in% varnames]
  
  hm = diag(length(modTS$coeff[rownames(modTS$coeff) %in% varnames]))
  lh = linearHypothesis(model = modTS, hm, c(0,0,0), vcov. = modTS$clustervcv[varnames,varnames], coef.=modTS$coeff[rownames(modTS$coeff) %in% varnames], test = "F")
  if(printV){
    print("----------------------")
    print(varname)
    print(lh$`Pr(>F)`[2])
    print("----------------------")
  }
  return(signif(lh$`Pr(>F)`[2],3))
}


#Make a plot showing the model error as a function of the yield anomaly. 
#Specifically show the improvement in model fit (TS vs TP) as a function of the yield anomaly. 
makeErrorVsAnomPlot = function(modTS, modTP, cropN, simple=F){
  
  pTS = data.table(data.frame(getCrossValR2(modTS, returnPreds = T, returnCX = T)))
  pTS$err = pTS$testys - pTS$testyhats
  pTS$sqerr = (pTS$err)^2

  pTP = data.table(data.frame(getCrossValR2(modTP, returnPreds = T, returnCX = T)))
  pTP$err = pTP$testys - pTP$testyhats
  pTP$sqerr = (pTP$err)^2

  p = merge(pTS, pTP, by = c("testys","shuffOrder"))

  p$sqerr_TS = p$sqerr.x
  p$sqerr_TP = p$sqerr.y
  p$sqerr_TS_TP = p$sqerr_TS - p$sqerr_TP
  
  #Shows both errors, not super helpful
  gg_errors_both = ggplot(data = p) + geom_point(aes(testys,sqerr_TS), color = "blue") +
    geom_point(aes(testys, sqerr_TP), color = "red") + theme_classic()
  
  #Shows difference in errors, negative here means TS is better than TP
  #95 confidence level shown in grey.
  
  r_sm_C6  = colorRampPalette((brewer.pal(11,'BrBG')))(50)
  limits_SlTS = c(-0.05,0.05)
  breaks_SlTS = signif(seq(-0.05,0.05,length.out = 14),2)
  
  gg_errors_diff = ggplot(data = p) + geom_point(aes(testys, sqerr_TS_TP, fill = testCXs.smrz_day), shape = 21) +
    geom_smooth(aes(testys, sqerr_TS_TP), color = "blue") +
    theme_classic() + geom_hline(yintercept=0) + 
    ggtitle(cropN) + xlab("Yield anomaly (log)") + ylab("Difference in squared error (TS - TP)") +
    scale_fill_stepsn(breaks = breaks_SlTS, colours = r_sm_C6, limits = limits_SlTS, name = paste0("Soil\nmoisture\nanomaly"),na.value="gray99") + 
    theme(legend.position = "right")
  
  if(simple){
    gg_errors_diff = ggplot(data = p) + geom_point(aes(testys, sqerr_TS_TP)) +
      geom_smooth(aes(testys, testCXs.smrz_day), color = "blue", se=F, linetype = "dashed") +
      geom_smooth(aes(testys, sqerr_TS_TP), color = "black") +
      theme_classic() + geom_hline(yintercept=0) + 
      ggtitle(cropN) + xlab("Yield anomaly (log)") + ylab("Difference in squared error (TS - TP)") +
      theme(legend.position = "right")
    return(gg_errors_diff)
  }
  
  return(gg_errors_diff)
}


makeR2DiffMap = function(modTS, modTP, modname, crop, returnR2s = F) {
  
  r2calc = function(testyhats , testys) {
    rss <- sum((testyhats - testys)^2)
    tss <- sum((testys - mean(testys))^2)
    rsq <- 1 - rss/tss
    return(rsq)
  }
  
  p = getCrossValR2(modTS, returnPreds = T)
  f = as.character(modTS$fe$country)[p$shuffOrder]
  preds = data.table(data.frame("country" = f, "testys" = p$testys, "testyhats" = p$testyhats))
  preds$sqerr = (preds$testys - preds$testyhats)^2
  r2 = preds[,.(r2 = r2calc(testyhats, testys)), by = .(country)]
  r2$country = as.character(r2$country)
  if(!returnR2s) {
    r2 = updateFaoNamesToMatchShapefile(r2)
  }
  r2$r2[r2$r2< -.1] = -0.1
  print("capping bottom at -0.1 for colorscale")
  r2TS = r2
  colnames(r2TS) = c("country","r2valTS")
  
  p = getCrossValR2(modTP, returnPreds = T)
  f = as.character(modTP$fe$country)[p$shuffOrder]
  preds = data.table(data.frame("country" = f, "testys" = p$testys, "testyhats" = p$testyhats))
  preds$sqerr = (preds$testys - preds$testyhats)^2
  r2 = preds[,.(r2 = r2calc(testyhats, testys)), by = .(country)]
  r2$country = as.character(r2$country)
  if(!returnR2s) {
    r2 = updateFaoNamesToMatchShapefile(r2)
  }
  r2$r2[r2$r2< -.1] = -0.1
  print("capping bottom at -0.1 for colorscale")
  r2TP = r2
  colnames(r2TP) = c("country","r2valTP")
  
  ### Note: because we clipped to 0.-1, we're only looking at performance gains for places that have some predictive power. 
  
  r2 = merge(r2TS, r2TP, by="country")
  
  r2$r2TS_TP = r2$r2valTS - r2$r2valTP
  
  if(returnR2s) {
    return(r2)
  }
  
  #load shapefile
  poly.fort = map_data("world")
  #merge the shapefile with the error data
  poly.fort2 = merge(x = poly.fort, y = r2, by.x = "region", by.y = "country", all.x=T)
  poly.fort2 = data.table(poly.fort2)
  poly.fort2 = poly.fort2[order(order)]
  
  #Try clipping
  poly.fort2=poly.fort2[poly.fort2$long<160,]
  poly.fort2=poly.fort2[poly.fort2$long>-130,]
  poly.fort2=poly.fort2[poly.fort2$lat<70,]
  poly.fort2=poly.fort2[poly.fort2$lat>-60,]
  
  #Set colorscales
  gr = c(min(r2$r2TS_TP), max(r2$r2TS_TP))
  ar = max(c(abs(gr)))
  ar = 0.2 
  print("Hardcoding min and max colorscale")
  limits_TS_TP = c(-ar, ar)
  breaks_TS_TP = signif(seq(limits_TS_TP[1],limits_TS_TP[2],length.out = 14),2)
  r_TS_TP  = rev(colorRampPalette(rev(brewer.pal(11,'RdBu')))(100))
  
  gmap = ggplot(poly.fort2, aes(x = long, y = lat, group = group, fill = (r2TS_TP) )) +
    geom_polygon(colour = "black", size = 0.5, aes(group = group)) +
    theme_map() + 
    scale_fill_stepsn(breaks = breaks_TS_TP, colours = r_TS_TP, limits = limits_TS_TP, name = paste0("R2\nChange\n",crop))
  
  ghist = ggplot() + geom_histogram(aes(r2$r2TS_TP)) + xlab("error") +  theme_classic()
  
  return(gmap)
  
}



### --- Plot Irrigation Interaction Models --- ###
plotIrrigationInterModels = function(mTSr,mTPr,d, gs_length = gs_length, modtype = "FullRcs",
                                     crop = "allCrops", plotCropN = NA, returnGGList = F,
                                     histogramIrrThreshold = 0.5) {
  irrvals = c(0,1)
  
  #get gsLength
  if(is.na(plotCropN) | (plotCropN=="Crop")) {
    gsLen = mean(gs_length$gs_len) #170
  } else {
    gsLen = gs_length[gs_length$crop == plotCropN]$gs_len #160-180
  }
  
  
  #load daily data
  if(crop == "allCrops") {
    print("loading combined crop data...")
    hd = readRDS(paste0("Data/allCrops_10pctCropW_all10pct2007_2007_2018.rda"))
    hd = hd[hd$crop != "Wheat",]
    hd = hd[hd$crop != "Oats",]
    hd = hd[hd$crop != "Barley",]
    
  }
  
  #Limit models and histdata to a single crop to plot
  if(!is.na(plotCropN) & (!plotCropN=="Crop")){
    print("Subsetting model to crop:")
    print(plotCropN)
    #SM
    mTSr$beta = t(t(mTSr$beta[grepl(plotCropN, rownames(mTSr$beta)),]))
    tmp = unlist(strsplit(x = rownames(mTSr$beta), split = ":"))
    rownames(mTSr$beta) = tmp[!grepl(plotCropN,tmp)]
    #PR
    mTPr$beta = t(t(mTPr$beta[grepl(plotCropN, rownames(mTPr$beta)),]))
    tmp = unlist(strsplit(x = rownames(mTPr$beta), split = ":"))
    rownames(mTPr$beta) = tmp[!grepl(plotCropN,tmp)]
    
    print("Subsetting hist data to crop:")
    cropstrs = unlist(strsplit(plotCropN,"_"))
    print(cropstrs)
    hd = hd[hd$crop %in% cropstrs,]
  }
  
  uq = 0.995
  lq = 0.005
  
  uq_precip = 0.99
  lq_precip = 0.01
  
  hd$precip[hd$precip > quantile(hd$precip,uq_precip, na.rm=T)] = quantile(hd$precip,uq_precip, na.rm=T)
  hd$precip[hd$precip < quantile(hd$precip,lq_precip, na.rm=T)] = quantile(hd$precip,lq_precip, na.rm=T)
  
  hd$tmax[hd$tmax > quantile(hd$tmax,uq, na.rm=T)] = quantile(hd$tmax,uq, na.rm=T)
  hd$tmax[hd$tmax < quantile(hd$tmax,lq, na.rm=T)] = quantile(hd$tmax,lq, na.rm=T)
  
  hd$smrz[hd$smrz > quantile(hd$smrz,uq, na.rm=T)] = quantile(hd$smrz,uq, na.rm=T)
  hd$smrz[hd$smrz < quantile(hd$smrz,lq, na.rm=T)] = quantile(hd$smrz,lq, na.rm=T)
  
  
  #already winsorized above so no need to clip
  smRange = quantile(hd$smrz, c(0,1), na.rm=T)
  prcpRange = quantile(hd$precip, c(0,1), na.rm=T)
  tmaxRange = quantile(hd$tmax, c(0,1), na.rm=T)
  polyalpha = 0.4
  
  if(is.na(plotCropN) | plotCropN == "Crop"){
    plotBottomVal = -1.5
    plotTopVal = 0.5
  } else{
    plotBottomVal = -1.5
    plotTopVal = 1
  }
  
  
  ### sm
  sm = seq(smRange[1],smRange[2],0.005)
  
  #create a datatable with all the features and then multiply the relevant ones
  sm_rcs = genRecenteredXVals_RCS(x = sm, xRef = 0.3, k = c(0.1,0.2,0.3,0.4)) #mean(hd$smrz,na.rm=T)
  smdf = cbind(sm_rcs)
  colnames(smdf) = c("smrz_day","smrz_day_RCS_k4_1", "smrz_day_RCS_k4_2") #, "smrz2_day", 
  
  rS = list()
  rS_lbsList = list()
  rS_ubsList = list()
  for(irr_i in 1:length(irrvals)) {
    smdf = data.table(smdf)
    smdf$smrz_irr = smdf$smrz_day*irrvals[irr_i]
    smdf$smrz_day_RCS_k4_1_irr = smdf$smrz_day_RCS_k4_1*irrvals[irr_i]
    smdf$smrz_day_RCS_k4_2_irr = smdf$smrz_day_RCS_k4_2*irrvals[irr_i]
    smdf = as.matrix(smdf)
    
    #Multiply the values by the coefficents to get the response
    rSi = as.matrix( smdf[,grep("smrz",rownames(mTSr$beta), value = T)] ) %*% as.matrix( mTSr$beta[grepl("smrz",rownames(mTSr$beta))] )
    rS[[irr_i]] = rSi
    #Get uncertainty
    if(is.na(plotCropN) | (plotCropN=="Crop")){
      vcov = getVcov(mTSr$clustervcv, paste0(grep("smrz", x = rownames(mTSr$beta), value = T))) ##This needs to change if we don't cluster
    } else {
      vcov = getVcov(mTSr$clustervcv, paste0("crop",plotCropN, ":", grep("smrz", x = rownames(mTSr$beta), value = T))) ##This needs to change if we don't cluster
    }
    length = 1.96 * sqrt(apply(X = as.matrix(smdf[,grep("smrz", x = rownames(mTSr$beta), value = T)]), FUN = calcVariance, MARGIN = 1, vcov))
    rS_lbsList[[irr_i]] = rS[[irr_i]] - length
    rS_ubsList[[irr_i]] = rS[[irr_i]] + length
  }
  
  #scale to daily and percent
  for(irr_i in 1:length(irrvals)){
    rS[[irr_i]] = log2Perc(rS[[irr_i]] / gsLen)
    rS_lbsList[[irr_i]] = log2Perc(rS_lbsList[[irr_i]] / gsLen)
    rS_ubsList[[irr_i]] = log2Perc(rS_ubsList[[irr_i]] / gsLen)
  }
  
  irrcol = "irrigated"
  nonirrcol = "non-irrigated"
  
  rsm = ggplot() + geom_line(aes(sm,rS[[1]], color = nonirrcol)) +
    geom_line(mapping = aes(x = sm, y = rS[[2]], color = irrcol), linetype = 1) + 
    xlab("Soil moisture (cm^3cm^-3)") + ylab(paste0(plotCropN, " yield change (%)")) + ggtitle(plotCropN) +
    geom_hline(yintercept = 0, size = 0.2) +
    theme_classic() +
    geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[1]], ymax = rS_ubsList[[1]], fill = nonirrcol) , alpha = polyalpha) + 
    geom_ribbon(mapping = aes(x = sm, ymin = rS_lbsList[[2]], ymax = rS_ubsList[[2]], fill = irrcol) , alpha = polyalpha) 
  
  rsm = rsm + geom_histogram(data = hd[irr_equip_cropfrac< histogramIrrThreshold],mapping = aes(smrz, y = ..count../ max(..count..)/2, fill = nonirrcol),
                             alpha = 0.3, bins = 60, position = position_nudge(y = plotBottomVal)) +
    geom_histogram(data = hd[irr_equip_cropfrac> histogramIrrThreshold],mapping = aes(smrz, y = ..count../ max(..count..)/2,fill = irrcol),
                   alpha = 0.3, bins = 60, position = position_nudge(y = plotBottomVal)) 
  
  
  #Colors:
  polyalpha = 0.3
  colors_plot_S <- c("irrigated" = "#35978F", "non-irrigated" = "#003C30")
  
  rsm = rsm + scale_fill_manual(values = colors_plot_S) + scale_color_manual(values = colors_plot_S)
  rsm = rsm + coord_cartesian(ylim = c(plotBottomVal, plotTopVal)) 
  
  ### prcp
  prcp = seq(prcpRange[1],prcpRange[2],0.01)
  #create a datatable with all the features and then multiply the relevant ones
  prcp_rcs = genRecenteredXVals_RCS(x = prcp, xRef = mean(hd$precip,na.rm=T), k = c(1,20,50,150))
  prcpdf = cbind(prcp_rcs) 
  colnames(prcpdf) = c("prcp_day",  "prcp_day_RCS_k4_1", "prcp_day_RCS_k4_2") #"prcp2_day",
  rP = list()
  rP_lbsList = list()
  rP_ubsList = list()
  for(irr_i in 1:length(irrvals)) {
    prcpdf = data.table(prcpdf)
    prcpdf$prcp_irr = prcpdf$prcp_day*irrvals[irr_i]
    prcpdf$prcp_day_RCS_k4_1_irr = prcpdf$prcp_day_RCS_k4_1*irrvals[irr_i]
    prcpdf$prcp_day_RCS_k4_2_irr = prcpdf$prcp_day_RCS_k4_2*irrvals[irr_i]
    prcpdf = as.matrix(prcpdf)
    
    #Multiply the values by the coefficients to get the response
    rPi = as.matrix( prcpdf[,grep("prcp",rownames(mTPr$beta), value = T)] ) %*% as.matrix( mTPr$beta[grepl("prcp",rownames(mTPr$beta))] )
    rP[[irr_i]] = rPi
    #Get uncertainty
    if(is.na(plotCropN) | (plotCropN=="Crop")){
      vcov = getVcov(mTPr$clustervcv, paste0(grep("prcp", x = rownames(mTPr$beta), value = T))) ##This needs to change if we don't cluster
    } else {
      vcov = getVcov(mTPr$clustervcv, paste0("crop",plotCropN, ":", grep("prcp", x = rownames(mTPr$beta), value = T))) ##This needs to change if we don't cluster
    }
    length = 1.96 * sqrt(apply(X = as.matrix(prcpdf[,grep("prcp", x = rownames(mTPr$beta), value = T)]), FUN = calcVariance, MARGIN = 1, vcov))
    rP_lbsList[[irr_i]] = rP[[irr_i]] - length
    rP_ubsList[[irr_i]] = rP[[irr_i]] + length
  }
  
  #scale to daily and percent
  for(irr_i in 1:length(irrvals)){
    rP[[irr_i]] = log2Perc(rP[[irr_i]] / gsLen)
    rP_lbsList[[irr_i]] = log2Perc(rP_lbsList[[irr_i]] / gsLen)
    rP_ubsList[[irr_i]] = log2Perc(rP_ubsList[[irr_i]] / gsLen)
  }
  
  rprcp = ggplot() + geom_line(aes(prcp,rP[[1]], color = nonirrcol)) +
    geom_line(mapping = aes(x = prcp, y = rP[[2]], color = irrcol), linetype = 1) + 
    xlab("Precipitation (mm)") + ylab(paste0(plotCropN, " yield change (%)")) + ggtitle(plotCropN) +
    geom_hline(yintercept = 0, size = 0.2) +
    theme_classic() +
    geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[1]], ymax = rP_ubsList[[1]], fill = nonirrcol) , alpha = polyalpha) + 
    geom_ribbon(mapping = aes(x = prcp, ymin = rP_lbsList[[2]], ymax = rP_ubsList[[2]], fill = irrcol) , alpha = polyalpha) 
  
  
  rprcp = rprcp + geom_histogram(data = hd[(irr_equip_cropfrac< histogramIrrThreshold)],mapping = aes(precip, y = ..count../ max(..count..)/2, fill = nonirrcol),
                                 alpha = 0.3, bins = 60, position = position_nudge(y = plotBottomVal)) +
    geom_histogram(data = hd[(irr_equip_cropfrac> histogramIrrThreshold)],mapping = aes(precip, y = ..count../ max(..count..)/2, fill = irrcol),
                   alpha = 0.3, bins = 60, position = position_nudge(y = plotBottomVal)) +
    ggtitle(paste0("Fraction no rain: ", signif(sum(hd[irr_equip_cropfrac< histogramIrrThreshold]$precip <=0, na.rm=T) / sum(!is.na(hd[irr_equip_cropfrac< histogramIrrThreshold]$precip)),3),
                   " (non-irr) ", signif(sum(hd[irr_equip_cropfrac > histogramIrrThreshold]$precip <=0, na.rm=T) / sum(!is.na(hd[irr_equip_cropfrac > histogramIrrThreshold]$precip)),3), " (irr)"))
  
  
  #Colors:
  polyalpha = 0.3
  colors_plot_P <- c("irrigated" = "#6BAED6", "non-irrigated" = "#08306B")
  
  rprcp = rprcp + scale_fill_manual(values = colors_plot_P) + scale_color_manual(values = colors_plot_P)
  
  rprcp = rprcp + coord_cartesian(ylim = c(plotBottomVal, plotTopVal)) 
  
  ### tmax
  tmax = seq(tmaxRange[1],tmaxRange[2],0.1)
  #create a datatable with all the features and then multiply the relevant ones
  tmax_rcs_cent = genRecenteredXVals_RCS(x = tmax, xRef = 25, k = c(10,20,27,35))
  tmax_rcs_cent = tmax_rcs_cent[,-1]
  tmax_poly_cent = genRecenteredXVals_polynomial(tmax,25,2)
  tmaxdf = cbind(tmax_poly_cent, tmax_rcs_cent)
  colnames(tmaxdf) = c("tmax_day", "tmax2_day", "tmax_day_RCS_k4_1", "tmax_day_RCS_k4_2")
  
  rTP = list()
  rTS = list()
  rTS_lbsList = list()
  rTS_ubsList = list()
  for(irr_i in 1:length(irrvals)) {
    tmaxdf = data.table(tmaxdf)
    tmaxdf$tmax_irr = tmaxdf$tmax_day*irrvals[irr_i]
    tmaxdf$tmax_day_RCS_k4_1_irr = tmaxdf$tmax_day_RCS_k4_1*irrvals[irr_i]
    tmaxdf$tmax_day_RCS_k4_2_irr = tmaxdf$tmax_day_RCS_k4_2*irrvals[irr_i]
    tmaxdf = as.matrix(tmaxdf)
    #Multiply the values by the coefficents to get the response
    rTP[[irr_i]] = as.matrix( tmaxdf[,grep("tmax",rownames(mTPr$beta), value = T)] ) %*% as.matrix( mTPr$beta[grepl("tmax",rownames(mTPr$beta))] )
    rTS[[irr_i]] = as.matrix( tmaxdf[,grep("tmax",rownames(mTSr$beta), value = T)] ) %*% as.matrix( mTSr$beta[grepl("tmax",rownames(mTSr$beta))] )
    #Get uncertainty
    if(is.na(plotCropN) | (plotCropN=="Crop")){
      tmpN = paste0(grep("tmax", x = rownames(mTSr$beta), value = T))
    } else {
      tmpN = paste0("crop",plotCropN, ":", grep("tmax", x = rownames(mTSr$beta), value = T))
      tmpN[tmpN == paste0("crop",plotCropN,":","tmax_day")] = paste0("tmax_day",":","crop",plotCropN)
    }
    vcov = getVcov(mTSr$clustervcv, tmpN) ##This needs to change if we don't cluster
    length = 1.96 * sqrt(apply(X = as.matrix(tmaxdf[,grep("tmax", x = rownames(mTSr$beta), value = T)]), FUN = calcVariance, MARGIN = 1, vcov))
    rTS_lbsList[[irr_i]] = rTS[[irr_i]] - length
    rTS_ubsList[[irr_i]] = rTS[[irr_i]] + length
  }
  
  ## Get the impact of going from 25C to 40C in unirrigated areas
  rTP2540 = (rTP[[1]][which.min(abs(tmax - 40))] - rTP[[1]][which.min(abs(tmax - 25))]) / gsLen
  rTS2540 = (rTS[[1]][which.min(abs(tmax - 40))] - rTS[[1]][which.min(abs(tmax - 25))]) / gsLen
  (rTP2540 - rTS2540) / abs(rTS2540) * 100
  
  #scale to daily and percent
  for(irr_i in 1:length(irrvals)){
    rTS[[irr_i]] = log2Perc(rTS[[irr_i]] / gsLen)
    rTP[[irr_i]] = log2Perc(rTP[[irr_i]] / gsLen)
    rTS_lbsList[[irr_i]] = log2Perc(rTS_lbsList[[irr_i]] / gsLen)
    rTS_ubsList[[irr_i]] = log2Perc(rTS_ubsList[[irr_i]] / gsLen)
  }
  
  rtmax = ggplot() + geom_line(aes(tmax,rTP[[1]], color = nonirrcol), linetype = 2) +
    geom_line(aes(tmax,rTP[[2]], color = irrcol), linetype = 2) +
    geom_line(aes(tmax,rTS[[1]], color = nonirrcol)) +
    geom_line(aes(tmax,rTS[[2]], color = irrcol)) +
    geom_hline(yintercept = 0, size = 0.2) +
    xlab("Temperature maximum (C)") + ylab(paste0(plotCropN, " yield change (%)")) + theme_classic() +
    ggtitle(paste0(plotCropN," X-Val R2 RCS  TP: ", round(getCrossValR2(mTPr),3), "  TS: ", round(getCrossValR2(mTSr),3))) 
  rtmax = rtmax +
    geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[1]], ymax = rTS_ubsList[[1]], fill = nonirrcol) , alpha = polyalpha) + 
    geom_ribbon(mapping = aes(x = tmax, ymin = rTS_lbsList[[2]], ymax = rTS_ubsList[[2]], fill = irrcol) , alpha = polyalpha) 
  
  rtmax = rtmax + geom_histogram(data = hd[irr_equip_cropfrac< histogramIrrThreshold],mapping = aes(tmax, y = ..count../ max(..count..)/2, fill = nonirrcol),
                                 alpha = polyalpha, bins = 60, position = position_nudge(y = plotBottomVal)) +
    geom_histogram(data = hd[irr_equip_cropfrac> histogramIrrThreshold],mapping = aes(tmax, y = ..count../ max(..count..)/2, fill = irrcol),
                   alpha = polyalpha, bins = 60, position = position_nudge(y = plotBottomVal))
  
  
  colors_plot_T <- c("irrigated" = "#FED976", "non-irrigated" = "#927F44")
  
  rtmax = rtmax + scale_fill_manual(values = colors_plot_T) + scale_color_manual(values = colors_plot_T)
  
  rtmax = rtmax + coord_cartesian(ylim = c(plotBottomVal, plotTopVal)) 
  
  pg = plot_grid(rtmax + theme(legend.position = "bottom"), rsm+ theme(legend.position = "bottom"), rprcp+ theme(legend.position = "bottom"), nrow = 1)
  
  if(returnGGList){
    return(list(rtmax, rprcp, rsm))
  } else {
    return(pg)
  }
}


### Get p-vals comparing irrigation interaction coefficients to zero ###
getIrrPval = function(cvar, cropN, model, printV=F){
  varnames = grep("irr", rownames(model$coeff),value=T)
  varnames = grep(cropN,varnames, value=T)
  varnames = grep(cvar,varnames, value=T)
  
  hm = diag(length(model$coeff[rownames(model$coeff) %in% varnames]))
  lh = linearHypothesis(model = model, hm, c(0,0,0), vcov. = model$clustervcv[varnames,varnames], coef.=model$coeff[rownames(model$coeff) %in% varnames], test = "F")
  if(printV){
    print("----------------------")
    print(cropN)
    print(lh$`Pr(>F)`[2])
    print("----------------------")
  }
  return(signif(lh$`Pr(>F)`[2],3))
}

###Test whether the TS and TP models have similar temperature curves
getTSTP_Pval_irrigation = function(modTS, modTP, irrigation = F){
  
  #to ensure it's using the cluster vcv
  modTS$vcv = NULL
  modTS$robustvcv = NULL
  #modTS$clustervcv = NULL #fails when this is run, which is good.
  
  varnames = grep("tmax", rownames(modTS$coeff),value=T)
  varnames_tmax = varnames[!grepl("irr", varnames)]
  varnames_irr = varnames[grepl("irr", varnames)]
  
  if(irrigation) {
    #If irrigation we need to add the irrigation coefficients on
    cTP = modTP$coefficients[rownames(modTP$coeff) %in% varnames_tmax]
    cTP = cTP +  modTP$coefficients[rownames(modTP$coeff) %in% varnames_irr]
    hypothesis_str = c("tmax_day + tmax_irr = ", "tmax_day_RCS_k4_1 + tmax_day_RCS_k4_1_irr = ", "tmax_day_RCS_k4_2 + tmax_day_RCS_k4_2_irr = ")
    hypothesis_str = paste0(hypothesis_str,cTP)
    lh = linearHypothesis(model = modTS, hypothesis_str, test="F")
  } else {
    #If not irrigated it's just the T coefficients
    cTP = modTP$coefficients[rownames(modTP$coeff) %in% varnames_tmax]
    hm = diag(length(modTS$coeff[rownames(modTS$coeff) %in% varnames_tmax]))
    lh = linearHypothesis(model = modTS, hm, cTP, vcov. = modTS$clustervcv[varnames_tmax,varnames_tmax], coef.=modTS$coeff[rownames(modTS$coeff) %in% varnames_tmax], test = "F")
  }
  
  print("----------------------")
  print(lh$`Pr(>F)`[2])
  print("----------------------")
  
  return(signif(lh$`Pr(>F)`[2],3))
}




### --- Plot Quadratic Interaction Models --- ###=
plotInterModels = function(mTS, typeStr, runStr, crop, plotCropN, gs_length, caxisLimits = c(NA,NA)){
  
  #load daily data
  if(crop == "allCrops") {
    print("loading combined crop data...")
    hd = readRDS(paste0("Data/allCrops_10pctCropW_all10pct2007_2007_2018.rda"))
    hd = hd[hd$crop != "Wheat",]
    hd = hd[hd$crop != "Barley",]
    hd = hd[hd$crop != "Oats",]
  }
  
  #Limit models and histdata to a single crop to plot
  if(!is.na(plotCropN)){
    print("Subsetting hist data to crop:")
    cropstrs = unlist(strsplit(plotCropN,"_"))
    print(cropstrs)
    hd = hd[hd$crop %in% cropstrs,]
  }
  
  #Get growing season length
  if(is.na(plotCropN)) {
    gsLen = mean(gs_length$gs_len) #170
  } else {
    gsLen = gs_length[gs_length$crop == plotCropN]$gs_len #160-180
  }
  
  
  #Plot and compare within R2 -- include the within R2 in the figure title.
  library(raster)
  library(ggthemes)
  sm = seq(0,0.5, length.out = 100)
  tmax = seq(0,50,length.out = 100)
  
  smr = raster(nrow = 100, ncol = 100, xmn = min(sm), xmx = max(sm), ymn = min(tmax), ymx = max(tmax))
  smr[] = rep(sm,100)
  
  tmaxr = raster(nrow = 100, ncol = 100, xmn = min(sm), xmx = max(sm), ymn = min(tmax), ymx = max(tmax))
  tmaxr[] = rev(rep(tmax,each = 100))
  
  smrcs1 = smr
  smrcs1[] = rcspline.eval(x = smr[], knots = c(0.1,0.2,0.3,0.4), inclx = F)[,1]
  smrcs2 = smr
  smrcs2[] = rcspline.eval(x = smr[], knots = c(0.1,0.2,0.3,0.4), inclx = F)[,2]
  
  tmaxrcs1 = tmaxr
  tmaxrcs1[] = rcspline.eval(x = tmaxr[], knots = c(10,20,27,35), inclx = F)[,1]
  tmaxrcs2 = smr
  tmaxrcs2[] = rcspline.eval(x = tmaxr[], knots = c(10,20,27,35), inclx = F)[,2]
  
  TSstack = stack(tmaxr, tmaxr^2, smr, smr^2, smrcs1, smrcs2, tmaxrcs1, tmaxrcs2, smr * tmaxr, smr * tmaxr^2, smr^2 * tmaxr, smr^2 * tmaxr^2)
  stackNames = c("tmax_day",   "tmax2_day",
                 "smrz_day",   "smrz2_day",
                 "smrz_day_RCS_k4_1", "smrz_day_RCS_k4_2",
                 "tmax_day_RCS_k4_1", "tmax_day_RCS_k4_2",
                 "smrz_tmax",  "smrz_tmax2",  "smrz2_tmax", "smrz2_tmax2")
  names(TSstack) = stackNames
  
  c = mTS$coefficients
  cnames = rownames(c)
  #get the indicies of the TSstack that correspond to the coefficients (in order)
  inds = match(cnames, stackNames)
  #subset TSstack and reorder based on these indicies
  vStack = TSstack[[inds]]
  #multiply the stacks by their respective coefficients and add
  rr = smr
  rr[] = 0
  for(i in 1:length(inds)){
    rr = rr + vStack[[i]] * c[i] 
  }
  
  #Recenter to have common zero at 0.2, 25
  smcent = 0.2
  tmaxcent = 25
  rr = rr - rr[50,51] #roughly
  
  #Calculate 95th percentile and clip raster to that
  hdc = hd[,c("tmax","smrz")]
  hdc = hdc[complete.cases(hdc),]
  kd <- ks::kde(hdc, compute.cont=TRUE)
  contour_95 <- with(kd, contourLines(x=eval.points[[1]], y=eval.points[[2]],
                                      z=estimate, levels=cont["5%"])[[1]])
  contour_95 <- data.frame(contour_95)
  cp = Polygon(contour_95[,c("y","x")])
  ps = Polygons(list(cp),1)
  sps = SpatialPolygons(list(ps))
  rr = raster::mask(rr,sps)
  
  #convert the raster to points for plotting
  rdf <- rasterToPoints(rr)
  #Make the points a dataframe for ggplot
  rdf <- data.frame(rdf)
  #Make appropriate column headings
  colnames(rdf) <- c("Soil_Moisture", "Temperature", "Yield")
  print("Yield bounds:")
  print(c(min(rdf$Yield, na.rm=T), max(rdf$Yield, na.rm=T)))
  
  rdf$Yield = log2Perc(rdf$Yield/gsLen)
  
  g = ggplot(data=rdf, aes(y = Soil_Moisture, x = Temperature)) +
    geom_raster(aes(fill=Yield)) + theme_bw() +
    theme_classic() + geom_contour( aes(z = Yield), colour = "white", size = 0.1) + 
    ggtitle(paste0(crop, "_R2: ",round(getCrossValR2(mTS),3))) +
    scale_fill_gradient2(name = "Yield", low = "red", mid = "gray95", high = "green", midpoint = 0,
                         space = "rgb", na.value = "gray90", guide = "colourbar",
                         limits = caxisLimits) +
    xlab("Temperature maximum (C)") + ylab("Soil moisture (cm^3cm^-3)")
  
  
  g2 = g + geom_path(aes(x, y), data=contour_95) +
    stat_density_2d(data = hd, aes(x = tmax, y = smrz), geom = "density_2d", bins = 5, colour="black", size = 0.1)

  return(g2)
}


getBootstrapR2 = function(d, nboot, crossCountry, setSeed){
  for(bi in 0:nboot){ #0:100
    
    print(bi)
    
    for(cropN in c("Maize","Soybeans","Sorghum","Millet")){
      print(cropN)
      dcrop = d[crop == cropN]
      
      #The first one will be the full dataset, others will be bootstrap samples from it
      if(bi > 0) {
        #block bootstrap pulling data from countries
        cs = as.character(unique(dcrop$country))
        cs_samp = sample(cs, length(cs), replace = T)
        firstC = T
        for(cname in cs_samp){
          tmp = dcrop[country == cname]
          #print(nrow(tmp))
          if(firstC){
            dcrop_samp = tmp
            firstC = F
          } else {
            dcrop_samp = rbind(dcrop_samp, tmp)
          }
        }
        dcrop = dcrop_samp
      }
      
      ###rcsDay
      #T
      mTrcsday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2  |  country + country:year | 0 | country, keepCX=T)
      #S
      mZrcsday = felm(data = dcrop, formula = log(yield) ~ smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      #P
      mPrcsday = felm(data = dcrop, formula = log(yield) ~ prcp_day + prcp_day_RCS_k4_1 + prcp_day_RCS_k4_2  |  country + country:year | 0 | country, keepCX=T)
      #TP
      mTPrcsday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + prcp_day + prcp_day_RCS_k4_1 + prcp_day_RCS_k4_2  |  country + country:year | 0 | country, keepCX=T)
      #TS
      mTZrcsday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      #TSP
      mTZPrcsday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + prcp_day + prcp_day_RCS_k4_1 + prcp_day_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      
      ###rcsSeason
      #knot locations. If not given, knots will be estimated using default quantiles of x. For 3 knots, the outer quantiles used are 0.10 and 0.90. 
      #For 4-6 knots, the outer quantiles used are 0.05 and 0.95. For \(\code{nk}>6\), the outer quantiles are 0.025 and 0.975. 
      #The knots are equally spaced between these on the quantile scale. For fewer than 100 non-missing values of x, the outer knots are the 5th smallest and largest x.
      tmax_season_RCS = rcspline.eval(x = dcrop$tmax_day, inclx = F, nk = 4)
      dcrop$tmax_season_RCS_k4_1 = tmax_season_RCS[,1]
      dcrop$tmax_season_RCS_k4_2 = tmax_season_RCS[,2]
      
      prcp_season_RCS = rcspline.eval(x = dcrop$prcp_day, inclx = F, nk = 4)
      dcrop$prcp_season_RCS_k4_1 = prcp_season_RCS[,1]
      dcrop$prcp_season_RCS_k4_2 = prcp_season_RCS[,2]
      
      smrz_season_RCS = rcspline.eval(x = dcrop$smrz_day, inclx = F, nk = 4)
      dcrop$smrz_season_RCS_k4_1 = smrz_season_RCS[,1]
      dcrop$smrz_season_RCS_k4_2 = smrz_season_RCS[,2]
      
      #T
      mTRCSseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_season_RCS_k4_1 + tmax_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      #S
      mZRCSseason = felm(data = dcrop, formula = log(yield) ~ smrz_day + smrz_season_RCS_k4_1 + smrz_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      #P
      mPRCSseason = felm(data = dcrop, formula = log(yield) ~ prcp_day + prcp_season_RCS_k4_1 + prcp_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      #TP (uses seasonal T)
      mTPRCSseason_both = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_season_RCS_k4_1 + tmax_season_RCS_k4_2 + prcp_day + prcp_season_RCS_k4_1 + prcp_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      #TP (uses daily T because daily T performs better than seasonal T)
      mTPRCSseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + prcp_day + prcp_season_RCS_k4_1 + prcp_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      #TS (uses seasonal T)
      mTZRCSseason_both = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_season_RCS_k4_1 + tmax_season_RCS_k4_2 + smrz_day + smrz_season_RCS_k4_1 + smrz_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      #TS (uses daily T)
      mTZRCSseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_season_RCS_k4_1 + smrz_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      #TSP (uses daily T)
      mTZPRCSseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_season_RCS_k4_1 + smrz_season_RCS_k4_2 + prcp_day +  prcp_season_RCS_k4_1 + prcp_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
      
      ###quadDay
      #T
      mTquadday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day  | country + country:year | 0 | country, keepCX=T)
      #S
      mZquadday = felm(data = dcrop, formula = log(yield) ~ smrz_day + smrz2_day  | country + country:year | 0 | country, keepCX=T)
      #P
      mPquadday = felm(data = dcrop, formula = log(yield) ~ prcp_day + prcp2_day  | country + country:year | 0 | country, keepCX=T)
      #TP
      mTPquadday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + prcp_day + prcp2_day  | country + country:year | 0 | country, keepCX=T)
      #TS
      mTZquadday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + smrz_day + smrz2_day  | country + country:year | 0 | country, keepCX=T)
      #TSP
      mTZPquadday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + smrz_day + smrz2_day + prcp_day + prcp2_day  | country + country:year | 0 | country, keepCX=T)
      
      ###quadSeason
      #T
      mTquadseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_season  | country + country:year | 0 | country, keepCX=T)
      #S
      mZquadseason = felm(data = dcrop, formula = log(yield) ~ smrz_day + smrz2_season  | country + country:year | 0 | country, keepCX=T)
      #P
      mPquadseason = felm(data = dcrop, formula = log(yield) ~ prcp_day + prcp2_season  | country + country:year | 0 | country, keepCX=T)
      #TP (uses daily T because daily T performs better than seasonal T)
      mTPquadseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + prcp_day + prcp2_season  | country + country:year | 0 | country, keepCX=T)
      #TS (uses daily T)
      mTZquadseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + smrz_day + smrz2_season  | country + country:year | 0 | country, keepCX=T)
      #TSP (uses daily T)
      mTZPquadseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + smrz_day + smrz2_season + prcp_day + prcp2_season  | country + country:year | 0 | country, keepCX=T)
      
      
      ###irrigation
      #T (TS model, only T interacted)
      mTrcsirrpix2 = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + tmax_irr + tmax_day_RCS_k4_1_irr + tmax_day_RCS_k4_2_irr  |  country + country:year | 0 | country, keepCX=T)
      #S (TS model, only S interacted)
      mSrcsirrpix2 = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + smrz_irr + smrz_day_RCS_k4_1_irr + smrz_day_RCS_k4_2_irr  |  country + country:year | 0 | country, keepCX=T)
      #TS (TS model, both T and S interacted)
      mTSrcsirrpix2 = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + tmax_irr + tmax_day_RCS_k4_1_irr + tmax_day_RCS_k4_2_irr + smrz_irr + smrz_day_RCS_k4_1_irr + smrz_day_RCS_k4_2_irr  |  country + country:year, keepCX=T)
      #TP (TP model, both T and P interacted)
      mTPrcsirrpix2 = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + prcp_day + prcp_day_RCS_k4_1 + prcp_day_RCS_k4_2 + tmax_irr + tmax_day_RCS_k4_1_irr + tmax_day_RCS_k4_2_irr + prcp_irr + prcp_day_RCS_k4_1_irr + prcp_day_RCS_k4_2_irr  |  country + country:year, keepCX=T)
      
      ###interaction
      #TS
      mTZrcsinter = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + smrz_tmax + smrz_tmax2 + smrz2_tmax + smrz2_tmax2  |  country + country:year | 0 | country, keepCX=T)
      
      ### Put all together into a table showing x-val R2
      quadday = c(getCrossValR2(mTquadday, setSeed = setSeed, crossCountry = crossCountry), getCrossValR2(mPquadday, setSeed = setSeed, crossCountry = crossCountry), getCrossValR2(mZquadday, setSeed = setSeed, crossCountry = crossCountry), getCrossValR2(mTPquadday, setSeed = setSeed, crossCountry = crossCountry), getCrossValR2(mTZquadday, setSeed = setSeed, crossCountry = crossCountry), getCrossValR2(mTZPquadday, setSeed = setSeed, crossCountry = crossCountry) )
      quadseason = c(getCrossValR2(mTquadseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mPquadseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mZquadseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mTPquadseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mTZquadseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mTZPquadseason, setSeed = setSeed, crossCountry = crossCountry))
      rcsday =  c(getCrossValR2(mTrcsday, setSeed = setSeed, crossCountry = crossCountry),  getCrossValR2(mPrcsday, setSeed = setSeed, crossCountry = crossCountry),  getCrossValR2(mZrcsday, setSeed = setSeed, crossCountry = crossCountry),  getCrossValR2(mTPrcsday, setSeed = setSeed, crossCountry = crossCountry),  getCrossValR2(mTZrcsday, setSeed = setSeed, crossCountry = crossCountry),  getCrossValR2(mTZPrcsday, setSeed = setSeed, crossCountry = crossCountry) )
      rcsseason = c(getCrossValR2(mTRCSseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mPRCSseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mZRCSseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mTPRCSseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mTZRCSseason, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mTZPRCSseason, setSeed = setSeed, crossCountry = crossCountry))
      interactionSurf = c(NA,NA,NA,NA, getCrossValR2(mTZrcsinter, setSeed = setSeed, crossCountry = crossCountry), NA )
      irrigationRCSInter = c(getCrossValR2(mTrcsirrpix2, setSeed = setSeed, crossCountry = crossCountry),NA,getCrossValR2(mSrcsirrpix2, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mTPrcsirrpix2, setSeed = setSeed, crossCountry = crossCountry),getCrossValR2(mTSrcsirrpix2, setSeed = setSeed, crossCountry = crossCountry) ,NA)
      
      #Put all together
      R2valsall = rbind(quadday,quadseason,rcsday,rcsseason,
                        irrigationRCSInter,interactionSurf)
      colnames(R2valsall) = c("T","P", "Z","TP", "TS","TSP")
      
      R2valsall = data.frame(R2valsall)
      R2valsall$cropN = cropN
      
      if(cropN=="Maize"){
        R2valsall_allcrops = R2valsall
      } else {
        R2valsall_allcrops = rbind(R2valsall_allcrops, R2valsall)
      }
      
    } #end crop loop
    
    #clean up a bit:
    R2valsall_allcrops$Model = rownames(R2valsall_allcrops)
    rownames(R2valsall_allcrops) = NULL
    R2valsall_allcrops = R2valsall_allcrops[,c(7,8,1:6)]
    colnames(R2valsall_allcrops)[1] = "Crop"
    R2valsall_allcrops$Model = gsub('[0-9]+', '', R2valsall_allcrops$Model)
    R2valsall_allcrops$bootInd = bi
    
    if(bi == 0){
      R2valsall_allcrops_allboot = R2valsall_allcrops
    } else {
      R2valsall_allcrops_allboot = rbind(R2valsall_allcrops_allboot,R2valsall_allcrops)
    }
    
  } # end bootstrap loop
  
  return(data.table(R2valsall_allcrops_allboot))
}

getBootstrapR2_BootWithin = function(d, nboot, crossCountry, setSeed){
  for(cropN in c("Maize","Soybeans","Sorghum","Millet")){
    print(cropN)
    dcrop = d[crop == cropN]
    
    ###rcsDay
    #T
    mTrcsday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2  |  country + country:year | 0 | country, keepCX=T)
    #S
    mZrcsday = felm(data = dcrop, formula = log(yield) ~ smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    #P
    mPrcsday = felm(data = dcrop, formula = log(yield) ~ prcp_day + prcp_day_RCS_k4_1 + prcp_day_RCS_k4_2  |  country + country:year | 0 | country, keepCX=T)
    #TP
    mTPrcsday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + prcp_day + prcp_day_RCS_k4_1 + prcp_day_RCS_k4_2  |  country + country:year | 0 | country, keepCX=T)
    #TS
    mTZrcsday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    #TSP
    mTZPrcsday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + prcp_day + prcp_day_RCS_k4_1 + prcp_day_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    
    ###rcsSeason
    #knot locations. If not given, knots will be estimated using default quantiles of x. For 3 knots, the outer quantiles used are 0.10 and 0.90. 
    #For 4-6 knots, the outer quantiles used are 0.05 and 0.95. For \(\code{nk}>6\), the outer quantiles are 0.025 and 0.975. 
    #The knots are equally spaced between these on the quantile scale. For fewer than 100 non-missing values of x, the outer knots are the 5th smallest and largest x.
    tmax_season_RCS = rcspline.eval(x = dcrop$tmax_day, inclx = F, nk = 4)
    dcrop$tmax_season_RCS_k4_1 = tmax_season_RCS[,1]
    dcrop$tmax_season_RCS_k4_2 = tmax_season_RCS[,2]
    
    prcp_season_RCS = rcspline.eval(x = dcrop$prcp_day, inclx = F, nk = 4)
    dcrop$prcp_season_RCS_k4_1 = prcp_season_RCS[,1]
    dcrop$prcp_season_RCS_k4_2 = prcp_season_RCS[,2]
    
    smrz_season_RCS = rcspline.eval(x = dcrop$smrz_day, inclx = F, nk = 4)
    dcrop$smrz_season_RCS_k4_1 = smrz_season_RCS[,1]
    dcrop$smrz_season_RCS_k4_2 = smrz_season_RCS[,2]
    
    #T
    mTRCSseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_season_RCS_k4_1 + tmax_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    #S
    mZRCSseason = felm(data = dcrop, formula = log(yield) ~ smrz_day + smrz_season_RCS_k4_1 + smrz_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    #P
    mPRCSseason = felm(data = dcrop, formula = log(yield) ~ prcp_day + prcp_season_RCS_k4_1 + prcp_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    #TP (uses seasonal T)
    mTPRCSseason_both = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_season_RCS_k4_1 + tmax_season_RCS_k4_2 + prcp_day + prcp_season_RCS_k4_1 + prcp_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    #TP (uses daily T because daily T performs better than seasonal T)
    mTPRCSseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + prcp_day + prcp_season_RCS_k4_1 + prcp_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    #TS (uses seasonal T)
    mTZRCSseason_both = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_season_RCS_k4_1 + tmax_season_RCS_k4_2 + smrz_day + smrz_season_RCS_k4_1 + smrz_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    #TS (uses daily T)
    mTZRCSseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_season_RCS_k4_1 + smrz_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    #TSP (uses daily T)
    mTZPRCSseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_season_RCS_k4_1 + smrz_season_RCS_k4_2 + prcp_day +  prcp_season_RCS_k4_1 + prcp_season_RCS_k4_2  | country + country:year | 0 | country, keepCX=T)
    
    ###quadDay
    #T
    mTquadday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day  | country + country:year | 0 | country, keepCX=T)
    #S
    mZquadday = felm(data = dcrop, formula = log(yield) ~ smrz_day + smrz2_day  | country + country:year | 0 | country, keepCX=T)
    #P
    mPquadday = felm(data = dcrop, formula = log(yield) ~ prcp_day + prcp2_day  | country + country:year | 0 | country, keepCX=T)
    #TP
    mTPquadday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + prcp_day + prcp2_day  | country + country:year | 0 | country, keepCX=T)
    #TS
    mTZquadday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + smrz_day + smrz2_day  | country + country:year | 0 | country, keepCX=T)
    #TSP
    mTZPquadday = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + smrz_day + smrz2_day + prcp_day + prcp2_day  | country + country:year | 0 | country, keepCX=T)
    
    ###quadSeason
    #T
    mTquadseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_season  | country + country:year | 0 | country, keepCX=T)
    #S
    mZquadseason = felm(data = dcrop, formula = log(yield) ~ smrz_day + smrz2_season  | country + country:year | 0 | country, keepCX=T)
    #P
    mPquadseason = felm(data = dcrop, formula = log(yield) ~ prcp_day + prcp2_season  | country + country:year | 0 | country, keepCX=T)
    #TP (uses daily T because daily T performs better than seasonal T)
    mTPquadseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + prcp_day + prcp2_season  | country + country:year | 0 | country, keepCX=T)
    #TS (uses daily T)
    mTZquadseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + smrz_day + smrz2_season  | country + country:year | 0 | country, keepCX=T)
    #TSP (uses daily T)
    mTZPquadseason = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax2_day + smrz_day + smrz2_season + prcp_day + prcp2_season  | country + country:year | 0 | country, keepCX=T)
    
    
    ###irrigation
    #T (TS model, only T interacted)
    mTrcsirrpix2 = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + tmax_irr + tmax_day_RCS_k4_1_irr + tmax_day_RCS_k4_2_irr  |  country + country:year | 0 | country, keepCX=T)
    #S (TS model, only S interacted)
    mSrcsirrpix2 = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + smrz_irr + smrz_day_RCS_k4_1_irr + smrz_day_RCS_k4_2_irr  |  country + country:year | 0 | country, keepCX=T)
    #TS (TS model, both T and S interacted)
    mTSrcsirrpix2 = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + tmax_irr + tmax_day_RCS_k4_1_irr + tmax_day_RCS_k4_2_irr + smrz_irr + smrz_day_RCS_k4_1_irr + smrz_day_RCS_k4_2_irr  |  country + country:year, keepCX=T)
    #TP (TP model, both T and P interacted)
    mTPrcsirrpix2 = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + prcp_day + prcp_day_RCS_k4_1 + prcp_day_RCS_k4_2 + tmax_irr + tmax_day_RCS_k4_1_irr + tmax_day_RCS_k4_2_irr + prcp_irr + prcp_day_RCS_k4_1_irr + prcp_day_RCS_k4_2_irr  |  country + country:year, keepCX=T)
    
    ###interaction
    #TS
    mTZrcsinter = felm(data = dcrop, formula = log(yield) ~ tmax_day + tmax_day_RCS_k4_1 + tmax_day_RCS_k4_2 + smrz_day + smrz_day_RCS_k4_1 + smrz_day_RCS_k4_2 + smrz_tmax + smrz_tmax2 + smrz2_tmax + smrz2_tmax2  |  country + country:year | 0 | country, keepCX=T)
    
    
    ### Put all together into a table showing x-val R2
    #Mean
    quadday_mean = c(mean(getCrossValR2Boot(mod = mTquadday, nBoot = nboot)), mean(getCrossValR2Boot(mod = mPquadday, nBoot = nboot)), mean(getCrossValR2Boot(mod = mZquadday, nBoot = nboot)), mean(getCrossValR2Boot(mod = mTPquadday, nBoot = nboot)), mean(getCrossValR2Boot(mod = mTZquadday, nBoot = nboot)), mean(getCrossValR2Boot(mod = mTZPquadday, nBoot = nboot)) )
    quadseason_mean = c(mean(getCrossValR2Boot(mod = mTquadseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mPquadseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mZquadseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mTPquadseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mTZquadseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mTZPquadseason, nBoot = nboot)))
    rcsday_mean =  c(mean(getCrossValR2Boot(mod = mTrcsday, nBoot = nboot)),  mean(getCrossValR2Boot(mod = mPrcsday, nBoot = nboot)),  mean(getCrossValR2Boot(mod = mZrcsday, nBoot = nboot)),  mean(getCrossValR2Boot(mod = mTPrcsday, nBoot = nboot)),  mean(getCrossValR2Boot(mod = mTZrcsday, nBoot = nboot)),  mean(getCrossValR2Boot(mod = mTZPrcsday, nBoot = nboot)) )
    rcsseason_mean = c(mean(getCrossValR2Boot(mod = mTRCSseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mPRCSseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mZRCSseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mTPRCSseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mTZRCSseason, nBoot = nboot)),mean(getCrossValR2Boot(mod = mTZPRCSseason, nBoot = nboot)))
    rcsseason_both_mean = c(NA,NA,NA, mean(getCrossValR2Boot(mod = mTPRCSseason_both, nBoot = nboot)),mean(getCrossValR2Boot(mod = mTZRCSseason_both, nBoot = nboot)), NA )
    interactionSurf_mean = c(NA,NA,NA,NA, mean(getCrossValR2Boot(mod = mTZrcsinter, nBoot = nboot)), NA )
    irrigationRCSInter_mean = c(mean(getCrossValR2Boot(mod = mTrcsirrpix2, nBoot = nboot)),NA,mean(getCrossValR2Boot(mod = mSrcsirrpix2, nBoot = nboot)),mean(getCrossValR2Boot(mod = mTPrcsirrpix2, nBoot = nboot)),mean(getCrossValR2Boot(mod = mTSrcsirrpix2, nBoot = nboot)) ,NA)
    
    #SD
    quadday_sd = c(sd(getCrossValR2Boot(mod = mTquadday, nBoot = nboot)), sd(getCrossValR2Boot(mod = mPquadday, nBoot = nboot)), sd(getCrossValR2Boot(mod = mZquadday, nBoot = nboot)), sd(getCrossValR2Boot(mod = mTPquadday, nBoot = nboot)), sd(getCrossValR2Boot(mod = mTZquadday, nBoot = nboot)), sd(getCrossValR2Boot(mod = mTZPquadday, nBoot = nboot)) )
    quadseason_sd = c(sd(getCrossValR2Boot(mod = mTquadseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mPquadseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mZquadseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mTPquadseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mTZquadseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mTZPquadseason, nBoot = nboot)))
    rcsday_sd =  c(sd(getCrossValR2Boot(mod = mTrcsday, nBoot = nboot)),  sd(getCrossValR2Boot(mod = mPrcsday, nBoot = nboot)),  sd(getCrossValR2Boot(mod = mZrcsday, nBoot = nboot)),  sd(getCrossValR2Boot(mod = mTPrcsday, nBoot = nboot)),  sd(getCrossValR2Boot(mod = mTZrcsday, nBoot = nboot)),  sd(getCrossValR2Boot(mod = mTZPrcsday, nBoot = nboot)) )
    rcsseason_sd = c(sd(getCrossValR2Boot(mod = mTRCSseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mPRCSseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mZRCSseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mTPRCSseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mTZRCSseason, nBoot = nboot)),sd(getCrossValR2Boot(mod = mTZPRCSseason, nBoot = nboot)))
    rcsseason_both_sd = c(NA,NA,NA, sd(getCrossValR2Boot(mod = mTPRCSseason_both, nBoot = nboot)),sd(getCrossValR2Boot(mod = mTZRCSseason_both, nBoot = nboot)), NA )
    interactionSurf_sd = c(NA,NA,NA,NA, sd(getCrossValR2Boot(mod = mTZrcsinter, nBoot = nboot)), NA )
    irrigationRCSInter_sd = c(sd(getCrossValR2Boot(mod = mTrcsirrpix2, nBoot = nboot)),NA,sd(getCrossValR2Boot(mod = mSrcsirrpix2, nBoot = nboot)),sd(getCrossValR2Boot(mod = mTPrcsirrpix2, nBoot = nboot)),sd(getCrossValR2Boot(mod = mTSrcsirrpix2, nBoot = nboot)) ,NA)
    
    
    #Put all together
    R2valsall = rbind(quadday_mean,
                      quadday_sd,
                      quadseason_mean,
                      quadseason_sd,
                      rcsday_mean,
                      rcsday_sd,
                      rcsseason_mean,
                      rcsseason_sd,
                      irrigationRCSInter_mean,
                      irrigationRCSInter_sd,
                      interactionSurf_mean,
                      interactionSurf_sd)
    signif(R2valsall,2)
    colnames(R2valsall) = c("T","P", "Z","TP", "TS","TSP")
    
    R2valsall = data.frame(R2valsall)
    R2valsall$cropN = cropN
    
    if(cropN=="Maize"){
      R2valsall_allcrops = R2valsall
    } else {
      R2valsall_allcrops = rbind(R2valsall_allcrops, R2valsall)
    }
    
  } #end crop loop
  
  
  
  #clean up a bit:
  R2valsall_allcrops$Model = rownames(R2valsall_allcrops)
  rownames(R2valsall_allcrops) = NULL
  R2valsall_allcrops = R2valsall_allcrops[,c(7,8,1:6)]
  colnames(R2valsall_allcrops)[1] = "Crop"
  R2valsall_allcrops$Model = gsub('[0-9]+', '', R2valsall_allcrops$Model)
  
  return(R2valsall_allcrops)
}

getCrossValR2Boot = function(mod, returnPreds = F, nsf = 3, setSeed=T, crossCountry = F, nBoot = 1) {
  x = as.matrix(mod$cX)
  y = mod$cY
  #Split X and Y into 5 different groups
  if(setSeed) set.seed(123)
  #Randomly shuffle the data
  s = sample(length(y))
  x = as.matrix(x[s,])
  y = y[s]
  
  #Create 10 equally size folds
  folds = cut(seq(1,length(y)),breaks=10,labels=FALSE)
  
  ##Perform 10 fold cross validation
  #Within each fold I'm going to generate nboot models and store these each in a list
  testyhats_list = list()
  testys_list = list()
  #For each fold
  for(i in 1:10){
    #Segement data by fold using the which() function 
    testIndexes = which(folds==i,arr.ind=TRUE)
    testDataX = x[testIndexes, ]
    testDataY = y[testIndexes]
    trainDataX = x[-testIndexes, ]
    trainDataY = y[-testIndexes]
    #Bootstrap within this: 
    for(bi in 1:nBoot){
      #Bootstrap from training X and Y to get nBoot models. 
      if (bi == 1){ #When nBoot = 1 just use the origional data. 
        boot_trainDataY = trainDataY
        boot_trainDataX = trainDataX
      } else {
        boot_indicies = sample(1:length(trainDataY), size = length(trainDataY), replace = T)
        boot_trainDataY = trainDataY[boot_indicies]
        boot_trainDataX = trainDataX[boot_indicies,]
      }
      
      #Train model
      m = lm(boot_trainDataY~boot_trainDataX) #+ -1 -- Try with this; we may need it. 
      #Make prediction in test set
      testDataXUse = testDataX
      bUse = m$coefficients[-1] #If not using intercept remove this. 
      testyhat = as.matrix(testDataXUse) %*% bUse
      #Store in the list
      if(i == 1){
        testyhats_list[[bi]] = testyhat
        testys_list[[bi]] = testDataY
      } else {
        testyhats_list[[bi]] = c(testyhats_list[[bi]], testyhat)
        testys_list[[bi]] = c(testys_list[[bi]],testDataY)
      }
    } #End for bootstrap
  }# End for fold
  
  #Calculate R2 for each bootstrap run:
  R2s = c()
  for(j in 1:nBoot){
    rss <- sum((testyhats_list[[j]] - testys_list[[j]])^2)
    tss <- sum((testys_list[[j]] - mean(testys_list[[j]]))^2)
    rsq <- 1 - rss/tss
    R2s[j] = rsq
  }
  
  
  if(nBoot == 1){
    return(signif(rsq,nsf))
  } else {
    return(R2s)
  }
}


