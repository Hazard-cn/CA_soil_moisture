### --- Functions --- ###
#Get percent change
log2perc = function(x) (exp(x) -1)*100
#identical but used by different names in other scripts. 
log2percent = function(x) return((exp(x)-1)*100)
namean = function(x) return(mean(x,na.rm=T))

makeBarchart = function(d_all,reg, ymin = NA, ymax = NA){
  mv = d_all[NAME == reg,]
  
  if(reg == "South Europe/Mediterranean [MED:13]"){ #Insufficient data
    mv[(variable == "TSpreds_T") & (crop == "Millet"),]$value = NA
    mv[(variable == "TPpreds") & (crop == "Millet"),]$value = NA
  }
  
  #to catch any issues
  if(sum(!is.na(mv$value))==0){return(NULL)}
  
  ### Reorder ###
  mv$crop_var = str_replace(mv$crop_var, "TSpreds_T", "3TSpreds_T")
  mv$crop_var = str_replace(mv$crop_var, "TSpreds_S", "4TSpreds_S")
  mv$crop_var = str_replace(mv$crop_var, "TPpreds", "1TPpreds")
  mv$crop_var = str_replace(mv$crop_var, "TSpreds", "2TSpreds")
  
  mv$crop_var = str_replace(mv$crop_var, "Maize", "1Maize")
  mv$crop_var = str_replace(mv$crop_var, "Soybeans", "2Soybeans")
  mv$crop_var = str_replace(mv$crop_var, "Sorghum", "3Sorghum")
  mv$crop_var = str_replace(mv$crop_var, "Millet", "4Millet")
  
  mvT_TP_TS = mv[mv$variable %in% c("TPpreds", "TSpreds", "TSpreds_T","TSpreds_S"),]
  
  #sort
  mvT_TP_TS = mvT_TP_TS[order(mvT_TP_TS$crop_var),]
  
  #set spacing
  ncrop = 4
  nvars = 4
  xVals = 1:(ncrop*nvars)
  for(i in 1:(ncrop-1)){
    xVals[(i*nvars + 1):length(xVals)] = xVals[(i*nvars + 1):length(xVals)] + 2
  }
  
  xVals = rep(xVals, each = 6)
  
  mvT_TP_TS$variable = as.character(mvT_TP_TS$variable)
  mvT_TP_TS$variable[mvT_TP_TS$variable == "TPpreds"] = "1 Temp. & Pr."
  mvT_TP_TS$variable[mvT_TP_TS$variable == "TSpreds"] = "2 Temp. & S.M."
  mvT_TP_TS$variable[mvT_TP_TS$variable == "TSpreds_T"] = "3 Temp. | TS"
  mvT_TP_TS$variable[mvT_TP_TS$variable == "TSpreds_S"] = "4 S.M. | TS"
  
  mvT_TP_TS$variable = as.factor(mvT_TP_TS$variable)
  levels(mvT_TP_TS$variable) = c("Temp. & Pr.", "Temp. & Soil Moist.", "Temp. from TS", "Soil Moist. from TS")
  
  labelYVal = min(100*(exp(mvT_TP_TS$value)-1), na.rm = T) - 5
  
  if(!is.na(ymin)){
    labelYVal = ymin + 5
  }
  
  T_TP_TS_bar = ggplot(data = mvT_TP_TS, aes(x = xVals, y = 100*(exp(value)-1), group = crop_var, color = variable)) +
    geom_point(shape = "—", size = 4) +  # was 8 for star
    geom_line() +
    stat_summary(fun = "mean", geom = "point", size = 3, shape = rep(c(16,16,17,17),sum(!is.na(mvT_TP_TS$value))/6/4)  ) + 
    theme_classic() + theme(axis.title.x = element_blank(), legend.position = "bottom") + ylab("Crop yield change (%)")+
    theme(axis.title.x=element_blank(), axis.text.x=element_blank(), axis.ticks.x=element_blank()) + 
    theme(panel.grid.major.y = element_line(colour = "grey50", size = 0.1)) +
    annotate(geom = "text", x = xVals[1] + 1, y = labelYVal, label = "Maize") + 
    annotate(geom = "text", x = xVals[1*6*4 + 1] + 1, y = labelYVal, label = "Soybeans") + 
    annotate(geom = "text", x = xVals[2*6*4 + 1] + 1, y = labelYVal, label = "Sorghum") + 
    annotate(geom = "text", x = xVals[3*6*4 + 1] + 1, y = labelYVal, label = "Millet") + 
    geom_hline(yintercept = 0, colour = "grey50", size = 0.1) +
    scale_color_manual(name = "Model", values = c("Temp. & Pr." = brewer.pal(name = "Blues",3)[3],
                                                  "Temp. & Soil Moist." = brewer.pal(name = "BrBG",9)[2],
                                                  "Temp. from TS" = brewer.pal(name = "YlOrRd",3)[3],
                                                  "Soil Moist. from TS" = brewer.pal(name = "BrBG",3)[3])) +
    guides(colour=guide_legend(override.aes=list(shape=c(16,16,17,17), linetype = "blank")))
  
  if(reg == "Global"){
    T_TP_TS_bar = T_TP_TS_bar + ggtitle(reg)
  } else {
    T_TP_TS_bar = T_TP_TS_bar + ggtitle(substr(reg,1, nchar(reg)-8))
  }
  
  if(!is.na(ymin)){
    T_TP_TS_bar = T_TP_TS_bar +  coord_cartesian(ylim = c(ymin,ymax))
  }
  
  return(T_TP_TS_bar)
  
} #end makeBarChart function

getAverageImpactMap = function(debiasType = debiasType, save = F){

  cropsMeanTSpreds = stack(paste0("Data/CMIP6/climate_change_means/",debiasType,"_cropsMeanTSpreds.grd"))
  blankR = cropsMeanTSpreds
  blankR[] = 0
  gg_TSpreds_allCrops = ggplotMyRaster(myRast = log2perc(cropsMeanTSpreds), meanVal = NA, var = "NA",  isSig = blankR, limitVals = "Q", model = "NA", lowColor = "blue", highColor = "green4")
  
  #add colorscale TS|TS
  r_TS_C6  = rev(colorRampPalette(rev(brewer.pal(11,'RdBu')))(100))
  limits_TS = getRange(list(gg_TSpreds_allCrops))
  lm = max(abs(limits_TS))
  limits_TS = c(-lm, lm)
  breaks_TS = signif(seq(limits_TS[1],limits_TS[2],length.out = 14),2)
  gg_TSpreds_allCrops = gg_TSpreds_allCrops + scale_fill_stepsn(na.value = "white", breaks = breaks_TS, colours = r_TS_C6, limits = limits_TS, name = paste0("Yield \nchange (%)")) + theme(plot.title = element_blank())
  
  #add the IPCC regions as a shapefile:
  ### Load the ipcc region averages:
  first = T
  for(cropN in c("Maize","Soybeans","Millet","Sorghum")){
    for(model in c("MRI-ESM2-0","BCC-CSM2-MR","CanESM5","GFDL-CM4","IPSL-CM6A-LR", "MIROC6")) {
      if(first){
        ipcc = fread(paste0("Data/CMIP6/",predictions_folder,"/ipcc_vals_",cropN,"_",model,"_",sen,".rda"))
        first = F
      } else{
        tmp = fread(paste0("Data/CMIP6/",predictions_folder,"/ipcc_vals_",cropN,"_",model,"_",sen,".rda"))
        ipcc =  rbind(ipcc, tmp)
      }
    }
  }
  
  ipcc = ipcc[ipcc$sumfrac > 10]
  cr = unique(ipcc$NAME)
  ipccshp <- readShapePoly("Data/IPCC_referenceRegions/referenceRegions.shp")
  ipccshp = ipccshp[ipccshp$NAME %in% cr,]
  ipccshp <- fortify(ipccshp, region = "NAME")
  gg_TSpreds_allCrops = gg_TSpreds_allCrops + geom_polygon(data=ipccshp, aes(long, lat, group = group), 
                                                           colour = alpha("gray22", 1/2), size = 0.5, fill = 'skyblue', alpha = 0)

  
  return(gg_TSpreds_allCrops)
}


getRange = function(ggList){
  minV = Inf
  maxV = -Inf
  for(i in 1:length(ggList)){
    minV = min(c(minV,ggList[[i]]$data$Val),na.rm=T)
    maxV = max(c(maxV,ggList[[i]]$data$Val),na.rm=T)
    #print(c(minV,maxV))
  }
  return(c(minV,maxV))
}

#This intakes a mean and variance raster and output a mask that is 
# 1 if the pixel is not significant 
# 0 if the pixel is significantly different from zero.
# This considers statistical uncertainty only. 
getNotSigFlagsRaster = function(mRaster, vRaster, mult) {
  seRaster = (vRaster ^ .5) * mult
  ub = mRaster + seRaster
  lb = mRaster - seRaster
  notSigRaster =  ub>0 & lb<0
  return(notSigRaster)
}

#This plots a single raster in the format that we want it to. 
#When making comparisons we can set limitVals which will make the color palette standard across plots
ggplotMyRaster = function(myRast, isSig, model, var, limitVals = NA, lowColor = ("blue"), highColor = ("red"), alphaSet = .7, titleStr = "map",
                          meanVal = NA, caxisname = NA, colorscale= NA) {
  if(limitVals == "Q"){
    limitVals = c(quantile(myRast, 0.01, na.rm=T), quantile(myRast, 0.99, na.rm=T))
  }
  
  #If we are putting on limits clip the data so that it doesn't show as NA. This will not affect the mean or anything other than the image.
  if(!is.na(limitVals)) {
    myRast[myRast < limitVals[1]] = limitVals[1]
    myRast[myRast > limitVals[2]] = limitVals[2]
  }
  
  ### Mean
  world <- map_data("world")
  #convert the raster to points for plotting
  map.p <- cbind(xyFromCell(myRast, 1:ncell(myRast)), getValues(myRast))
  #Make the points a dataframe for ggplot
  df <- data.frame(map.p)
  #Make appropriate column headings
  colnames(df) <- c("Longitude", "Latitude", "Val")
  
  ### Variance
  #Make the zeros equal to NA so that they don't make things opaque:
  isSig[isSig == 0] = NA
  #convert the raster to points for plotting
  map.p <- rasterToPoints(isSig)
  #Make the points a dataframe for ggplot
  dfVar <- data.frame(map.p)
  #Make appropriate column headings
  colnames(dfVar) <- c("Longitude", "Latitude", "Sig")
  
  #Crop the world a bit to show important parts
  df=df[df$Latitude<70,]
  df=df[df$Latitude>-60,]
  world=world[world$lat<70,]
  world=world[world$lat>-60,]
  
  df=df[df$Longitude<160,]
  df=df[df$Longitude>-130,]
  world=world[world$long<160,]
  world=world[world$long>-130,]
  
  #Now make the map
  g = ggplot(data=df, aes(y=Latitude, x=Longitude)) +
    geom_raster(aes(fill=Val)) + 
    #guide_colorbar(title = "var") +
    theme_map() +
    coord_equal() +
    geom_map(data=world, map=world,
             aes(x=long, y=lat, map_id=region),
             color="black", fill="#7f7f7f", size=0.1, alpha=0) + ggtitle(titleStr)
  
  
  #If a colorscale is given, use it, if not, use the divergent color map
  if(!is.na(colorscale)){
    g = g + scale_fill_gradientn(name = caxisname, colours=colorscale, na.value = "gray95")
  } else {
    if(is.na(limitVals)) {
      g = g + scale_fill_gradient2(name = caxisname, low = lowColor, mid = "gray95", high = highColor, midpoint = 0, space = "rgb", na.value = "gray90", guide = "colourbar")
    } else {
      g = g + scale_fill_gradient2(name = caxisname, low = lowColor, mid = "gray95", high = highColor, midpoint = 0, space = "rgb", na.value = "gray90", guide = "colourbar", limits = limitVals)
    }
  }
  
  ### Add the isNotSignificantMask
  if(all(is.na(getValues(isSig)))) {
    print("All Points Significant")
    f = g
  } else {
    dfVar$Sig = as.factor(dfVar$Sig)
    f = g + geom_point(data = dfVar, aes(x = Longitude, y = Latitude, shape = 43), size = 0.1) + scale_shape_identity()
  }
  
  f
}


#For some averages we want to weight by the fraction of area planted mask:
getmean = function(rast, frac) {
  lat = coordinates(rast)[,2]
  coslat = cos(lat*pi/180)
  signif(weighted.mean(x = getValues(rast), w = (getValues(frac) * coslat), na.rm=T), 3)
}



print("------ Functions Loaded ------")
print("------ Functions Loaded ------")
print("------ Functions Loaded ------")
