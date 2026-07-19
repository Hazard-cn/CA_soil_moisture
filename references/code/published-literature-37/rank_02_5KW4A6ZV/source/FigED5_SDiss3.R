
### Here I simulate how mis-measurement of water stress can bias estimates of heat and water stress on crop yield.
# The results are illustrated in Extended Data Fig. 5 and discussed in Supplementary Discussion 3. 

### True data generating process (DGP):
# Yields are a function of daily temperature and soil moisture:
# Daily temperature and soil moisture are coupled:

library(MASS)
library(stargazer)
library(cowplot)

rm(list = ls())

set.seed(123)

### Functions ###
createDailyGrowingSeasonData = function(gsLen,nYr,mu,sigma){
  
  d = data.table(mvrnorm(n = gsLen*nYr, mu = mu, Sigma = sigma))
  colnames(d) = c("tmax","sm","pr")  
  d$year = rep(1:nYr, each = gsLen)
  d=d[,c(4,1,2,3)]
  
  return(d)  
}

getContours = function(dc, cvals = c(5,25,50,95), cvars = c("tasmax","mrsos")){
  cvals = paste0(cvals,"%")
  hdc = dc[,..cvars]
  hdc = hdc[complete.cases(hdc),]
  kd <- ks::kde(hdc, compute.cont=TRUE)
  
  contours = list()
  cval = cvals[1]
  ci = 1
  for(cval in cvals){
    contour <- with(kd, contourLines(x=eval.points[[1]], y=eval.points[[2]],
                                     z=estimate, levels=cont[cval])[[1]])
    contours[[ci]] <- data.frame(contour)
    ci = ci+1
  }
  
  return(contours)
  
}

### Main ###

gsLen = 90 #growing season length
nYr = 5000 #number of years

### --- Linear (A,B) --- ###

corTS = -0.4
corTP = -0.2
corSP = 0.3
vcov_TSP =  matrix(c(1,corTS,corTP,corTS,1,corSP,corTP,corSP,1),nrow=3,byrow = F)

#simulate growing season data by pulling from a multivariate normal:
d = createDailyGrowingSeasonData(gsLen, nYr, mu = c(0,0,0), sigma = vcov_TSP)

#Scale to more reasonable values:
d$sm = d$sm - min(d$sm)
d$sm = d$sm / (2*max(d$sm))
d$tmax = d$tmax*3 + 25
d$pr = d$pr - min(d$pr)
d$pr = d$pr * 5

#close enough match to observed correlations and co-variances; statistical finding robust to substantial changes in these. 
cov(d$tmax, d$sm)
cov(d$pr, d$sm)
cov(d$tmax, d$pr)
cor(d$tmax, d$sm)
cor(d$pr, d$sm)
cor(d$tmax, d$pr)

### ED5.A
csize_obs = 0.2
polyalpha = 0.15
contours_TS = getContours(d, cvars = c("tmax","sm"), cvals = c(5,25,50, 75, 85, 95))
ggHist = ggplot() + geom_polygon(aes(x, y), fill = "black", data=contours_TS[[1]], size = csize_obs, alpha = polyalpha) +
  geom_polygon(aes(x, y), fill = "black", data=contours_TS[[2]], size = csize_obs, alpha = polyalpha) +
  geom_polygon(aes(x, y), fill = "black", data=contours_TS[[3]], size = csize_obs, alpha = polyalpha) +
  geom_polygon(aes(x, y), fill = "black", data=contours_TS[[4]], size = csize_obs, alpha = polyalpha) + 
  geom_polygon(aes(x, y), fill = "black", data=contours_TS[[5]], size = csize_obs, alpha = polyalpha) +
  theme_classic() + xlab("Temperature") + ylab("Soil moisture")

#let the yield contribution during each day be a function of temperature and soil moisture
#this is consistent with modelling log yield and assuming that the growth during each day in the growing season multiplies by the next day. 
d$yieldContrib = d$tmax * -1/16 + d$sm * 2 + rnorm(gsLen*nYr, 0, 0.1)

d_gs = d[, .(tmax = mean(tmax),
             sm = mean(sm),
             pr = mean(pr),
             yield = mean(yieldContrib)), by = year]

modT = lm(yield ~ tmax, data = d_gs)
modTP = lm(yield ~ tmax + pr, data = d_gs)
modTS = lm(yield ~ tmax + sm, data = d_gs)

#We see the classic omitted variables story here that we would expect:
#Damages from temperature are exaggerated in the T and TP models
#Values are correctly recovered in the TS model.
stargazer(modT, modTP, modTS, type = "text")

tmax = seq(min(d$tmax),max(d$tmax),.01)
df = data.table(tmax)
df$yieldT = modT$coefficients[c("tmax")] * tmax  - modT$coefficients[c("tmax")] * tmax[round(length(tmax)/2)]
df$yieldTP = modTP$coefficients[c("tmax")] * tmax - modTP$coefficients[c("tmax")] * tmax[round(length(tmax)/2)]
df$yieldTS = modTS$coefficients[c("tmax")] * tmax - modTS$coefficients[c("tmax")] * tmax[round(length(tmax)/2)]
df$yieldT_true = -1/8/2 * tmax - -1/8/2 * tmax[round(length(tmax)/2)]

### ED5.B
ggL = ggplot(data=df) + 
  geom_line(aes(tmax,yieldT, color = "T."), linetype = "dashed") +
  geom_line(aes(tmax,yieldTP, color = "TP"), linetype = "dashed") +
  geom_line(aes(tmax,yieldTS, color = "TS")) +
  geom_line(aes(tmax,yieldT_true, color = "True"), linetype = "F1") +
  theme_classic() + scale_color_manual(values = c(T. = "red", TP = "yellow", TS = "blue", True = "black")) + theme(legend.position = "bottom") +
  xlab ("Temperature") + ylab ("Yield change") + theme(legend.position = "None")

### --- Non-linear (C) --- ###
# We can see this nonlinearly as well: 
    
bT1 = 0.137277
bT2 = -0.002903
bS1 = 2.202208
d$yieldContrib = bT1 * d$tmax + bT2 * d$tmax^2 + bS1 * d$sm + rnorm(gsLen*nYr, 0, 0.1)

d_gs = d[, .(tmax = mean(tmax),
             tmax2 = mean(tmax^2),
             sm = mean(sm),
             pr = mean(pr),
             yield = mean(yieldContrib)), by = year]

modT = lm(yield ~ tmax + tmax2, data = d_gs)
modTP = lm(yield ~ tmax + tmax2 + pr, data = d_gs)
modTS = lm(yield ~ tmax + tmax2 + sm, data = d_gs)

#Again, we see the classic omitted variables story here that we would expect:
#Damages from temperature are exaggerated in the T and TP models
#Values are correctly recovered in the TS model.
stargazer(modT, modTP, modTS, type = "text")

df = data.table(tmax)
df$yieldT = modT$coefficients[c("tmax")] * tmax + modT$coefficients[c("tmax2")] * tmax^2
df$yieldTP = modTP$coefficients[c("tmax")] * tmax + modTP$coefficients[c("tmax2")] * tmax^2
df$yieldTS = modTS$coefficients[c("tmax")] * tmax + modTS$coefficients[c("tmax2")] * tmax^2
df$yieldT_true = bT1 * tmax + bT2 * tmax^2


df$yieldT = df$yieldT - df$yieldT[round(length(tmax)/2)]
df$yieldTP = df$yieldTP - df$yieldTP[round(length(tmax)/2)]
df$yieldTS = df$yieldTS - df$yieldTS[round(length(tmax)/2)]
df$yieldT_true = df$yieldT_true - df$yieldT_true[round(length(tmax)/2)]

### ED5.C
ggNL = ggplot(data=df) + 
  geom_line(aes(tmax,yieldT, color = "T."), linetype = "dashed") +
  geom_line(aes(tmax,yieldTP, color = "TP"), linetype = "dashed") +
  geom_line(aes(tmax,yieldTS, color = "TS")) +
  geom_line(aes(tmax,yieldT_true, color = "True"), linetype = "F1") +
  theme_classic() + scale_color_manual(values = c(T. = "red", TP = "yellow", TS = "blue", True = "black")) + theme(legend.position = "bottom")+
  coord_cartesian(ylim = c(min(df$yieldT_true)-0.5, max(df$yieldT_true)+0.25)) +
  xlab ("Temperature") + ylab ("Yield change")

### --- Non-linear w. strong relationship between S and Y at low soil moisture (D) --- ###

#Simulate yield

bT1 = 0.137277
bT2 = -0.002903
bSlow = 4
bShigh = 0 
smcutoff = 0.2
d$yieldContrib = bT1 * d$tmax + bT2 * d$tmax^2 + bSlow * d$sm * (d$sm < smcutoff) + bShigh * d$sm * (d$sm >= smcutoff) + bSlow*smcutoff * (d$sm >= smcutoff) + rnorm(gsLen*nYr, 0, 0.1)

#Make gs data
d_gs = d[, .(tmax = mean(tmax),
             tmax2 = mean(tmax^2),
             tmax3 = mean(tmax^3),
             tmax4 = mean(tmax^4),
             sm = mean(sm*(sm<smcutoff)), #allow for nonlinear sm response
             smc = mean(sm >= smcutoff),
             pr = mean(pr),
             yield = mean(yieldContrib)), by = year]

#Train models
modT = lm(yield ~ tmax + tmax2, data = d_gs)
modTP = lm(yield ~ tmax + tmax2 + pr, data = d_gs)
modTP4 = lm(yield ~ tmax + tmax2 + tmax3 + tmax4 + pr, data = d_gs)

modTS = lm(yield ~ tmax + tmax2 + sm + smc, data = d_gs)
modTS4 = lm(yield ~ tmax + tmax2 + tmax3 + tmax4 + sm + smc, data = d_gs)

stargazer(modT, modTP, modTS, modTS4, modTP4, type = "text")


#get optimal values:
modT$coefficients[2] / (-2*modT$coefficients[3]) 
modTP$coefficients[2] / (-2*modTP$coefficients[3]) 
modTS$coefficients[2] / (-2*modTS$coefficients[3]) 

#Plot
df = data.table(tmax)
df$yieldT = modT$coefficients[c("tmax")] * tmax + modT$coefficients[c("tmax2")] * tmax^2
df$yieldTP = modTP$coefficients[c("tmax")] * tmax + modTP$coefficients[c("tmax2")] * tmax^2
df$yieldTP4 = modTP$coefficients[c("tmax")] * tmax + modTP$coefficients[c("tmax2")] * tmax^2 + modTP$coefficients[c("tmax3")] * tmax^3 + modTP$coefficients[c("tmax4")] * tmax^4
df$yieldTS = modTS$coefficients[c("tmax")] * tmax + modTS$coefficients[c("tmax2")] * tmax^2
df$yieldT_true = bT1 * tmax + bT2 * tmax^2

df$yieldT = df$yieldT - df$yieldT[round(length(tmax)/2)]
df$yieldTP = df$yieldTP - df$yieldTP[round(length(tmax)/2)]
df$yieldTP4 = df$yieldTP4 - df$yieldTP4[round(length(tmax)/2)]
df$yieldTS = df$yieldTS - df$yieldTS[round(length(tmax)/2)]
df$yieldT_true = df$yieldT_true - df$yieldT_true[round(length(tmax)/2)]

### ED5.D
ggNL_corTS = ggplot(data=df) + 
  geom_line(aes(tmax,yieldT, color = "T."), linetype = "dashed") +
  geom_line(aes(tmax,yieldTP, color = "TP"), linetype = "dashed") +
  geom_line(aes(tmax,yieldTS, color = "TS")) +
  geom_line(aes(tmax,yieldT_true, color = "True"), linetype = "F1") +
  theme_classic() + scale_color_manual(values = c(T. = "red", TP = "yellow", TS = "blue", True = "black")) + theme(legend.position = "bottom")+ #, TP4 = "orange"
  coord_cartesian(ylim = c(min(df$yieldT_true)-0.5, max(df$yieldT_true)+0.25)) +
  xlab ("Temperature") + ylab ("Yield change")


### --- Add a stronger correlation between T and S in hot/dry conditions (E,F) --- ###
corTS = -.8
vcov_TSP =  matrix(c(1,corTS,corTP,corTS,1,corSP,corTP,corSP,1),nrow=3,byrow = F)

#simulate growing season data by pulling from a multivariate normal:
d2 = createDailyGrowingSeasonData(gsLen, nYr, mu = c(0,0,0), sigma = vcov_TSP)
#Scale to more reasonable values:
d2$sm = d2$sm - min(d2$sm)
d2$sm = d2$sm / (2*max(d2$sm))
d2$tmax = d2$tmax*3 + 25
d2$pr = d2$pr - min(d2$pr)
d2$pr = d2$pr * 5

#For each value that is hot and dry in d, replace it from a hot and dry value from d2
dstrong = d
hotdryd2 = d2[tmax>25 & sm < 0.2]
idxs = sample(x = 1:nrow(hotdryd2), size = nrow(dstrong[tmax>25 & sm < 0.2,2:4]), replace = T)
hotdryd2 = hotdryd2[idxs,2:4]
hotdryd2$sm = hotdryd2$sm + (hotdryd2$sm - 0.2) * 1.1 #strengthen the relationship
dstrong[tmax>25 & sm < 0.2,2:4] = hotdryd2

### ED5.E
contours_TS = getContours(rbind(dstrong,d), cvars = c("tmax","sm"), cvals = c(5,25,50, 75, 85, 95))
ggHist_strong = ggplot() + geom_polygon(aes(x, y), fill = "black", data=contours_TS[[1]], size = csize_obs, alpha = polyalpha) +
  geom_polygon(aes(x, y), fill = "black", data=contours_TS[[2]], size = csize_obs, alpha = polyalpha) +
  geom_polygon(aes(x, y), fill = "black", data=contours_TS[[3]], size = csize_obs, alpha = polyalpha) +
  geom_polygon(aes(x, y), fill = "black", data=contours_TS[[4]], size = csize_obs, alpha = polyalpha) + 
  geom_polygon(aes(x, y), fill = "black", data=contours_TS[[5]], size = csize_obs, alpha = polyalpha) +
  theme_classic() + xlab("Temperature") + ylab("Soil moisture")


### estimate and plot
d = rbind(dstrong,d)

d$yieldContrib = bT1 * d$tmax + bT2 * d$tmax^2 + bSlow * d$sm * (d$sm < smcutoff) + bShigh * d$sm * (d$sm >= smcutoff) + bSlow*smcutoff * (d$sm >= smcutoff) + rnorm(gsLen*nYr, 0, 0.1)

#Make gs data
d_gs = d[, .(tmax = mean(tmax),
             tmax2 = mean(tmax^2),
             tmax3 = mean(tmax^3),
             tmax4 = mean(tmax^4),
             sm = mean(sm*(sm<smcutoff)), #allow for nonlinear sm response
             smc = mean(sm >= smcutoff),
             pr = mean(pr),
             yield = mean(yieldContrib)), by = year]

#Train models
modT = lm(yield ~ tmax + tmax2, data = d_gs)
modTP = lm(yield ~ tmax + tmax2 + pr, data = d_gs)
modTP4 = lm(yield ~ tmax + tmax2 + tmax3 + tmax4 + pr, data = d_gs)

modTS = lm(yield ~ tmax + tmax2 + sm + smc, data = d_gs)
modTS4 = lm(yield ~ tmax + tmax2 + tmax3 + tmax4 + sm + smc, data = d_gs)

stargazer(modT, modTP, modTS, modTS4, modTP4, type = "text")


#get optimal values:
modT$coefficients[2] / (-2*modT$coefficients[3]) 
modTP$coefficients[2] / (-2*modTP$coefficients[3]) 
modTS$coefficients[2] / (-2*modTS$coefficients[3]) 

#Plot
#tmax = seq(-3,3,.01)
df = data.table(tmax)
df$yieldT = modT$coefficients[c("tmax")] * tmax + modT$coefficients[c("tmax2")] * tmax^2
df$yieldTP = modTP$coefficients[c("tmax")] * tmax + modTP$coefficients[c("tmax2")] * tmax^2
df$yieldTP4 = modTP$coefficients[c("tmax")] * tmax + modTP$coefficients[c("tmax2")] * tmax^2 + modTP$coefficients[c("tmax3")] * tmax^3 + modTP$coefficients[c("tmax4")] * tmax^4
df$yieldTS = modTS$coefficients[c("tmax")] * tmax + modTS$coefficients[c("tmax2")] * tmax^2
df$yieldT_true = bT1 * tmax + bT2 * tmax^2

df$yieldT = df$yieldT - df$yieldT[round(length(tmax)/2)]
df$yieldTP = df$yieldTP - df$yieldTP[round(length(tmax)/2)]
df$yieldTP4 = df$yieldTP4 - df$yieldTP4[round(length(tmax)/2)]
df$yieldTS = df$yieldTS - df$yieldTS[round(length(tmax)/2)]
df$yieldT_true = df$yieldT_true - df$yieldT_true[round(length(tmax)/2)]

### ED5.F
ggNL_corTS2 = ggplot(data=df) + 
  geom_line(aes(tmax,yieldT, color = "T."), linetype = "dashed") +
  geom_line(aes(tmax,yieldTP, color = "TP"), linetype = "dashed") +
  geom_line(aes(tmax,yieldTS, color = "TS")) +
  geom_line(aes(tmax,yieldT_true, color = "True"), linetype = "F1") +
  theme_classic() + scale_color_manual(values = c("T only" = "red", "TP" = "yellow","TS" = "blue", "Prescribed truth" = "black")) + theme(legend.position = "bottom")+ #, TP4 = "orange"
  coord_cartesian(ylim = c(min(df$yieldT_true)-0.5, max(df$yieldT_true)+0.25)) +
  xlab ("Temperature") + ylab ("Yield change")

pg = plot_grid(ggHist, ggL, ggNL + theme(legend.position="None"), ggNL_corTS+ theme(legend.position="None"), ggHist_strong, ggNL_corTS2 + theme(legend.title = element_blank()), nrow = 3,
               labels = c('A', 'B', 'C', 'D', 'E', 'F'), align = 'vh')

ggsave(filename = "Results/Figs/ED/FigED5.jpg",
       plot = pg,
       width = 8.5, height = 10)
