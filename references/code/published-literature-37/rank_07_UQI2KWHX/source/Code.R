##key codes in the research

library(dplyr)
library(ggplot2)
library(tidyverse)
library(lme4)
library(Phenotype)
library(ggpmisc)
library(boot)
library(metR)
library(RColorBrewer)
library(ggthemes)
library(paletteer)
library(ggalt)
library(sf)


##Caluation of best linear unbiased predictions (BLUP)
data.1 <- read.csv("raw data.csv")

region.year <- data.1[, c("Region", "Year")] %>% distinct() %>% arrange(Region, Year)
len.1 <- c(1 : length(region.year[, 1]))

cal_blup <- function(blup.1){
  region.1 <- region.year[blup.1, "Region"]
  year.1 <- region.year[blup.1, "Year"]
  data.blup <- data.1 %>%
    filter(Region == region.1) %>%
    filter(Year == year.1)
  data.blup.out <- blup(data.blup, sample = "Variety_Name", loc = "Site_code",phe = "Yield_ha", fold = 1.5)
  colnames(data.blup.out) <- c("Variety_Name", "Mean_Yield_ha", "Blup", "Adj_Yield_ha")
  data.blup.out$Region <- region.1
  data.blup.out$Year <- year.1
  return(data.blup.out)
}
##Return BLUP values
data.2 <- map_dfr(len.1, cal_blup)

##Yield response to climate factors
##all models tried in this research
model.design <- list(
  ##Whole growing stage
  lm.1 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + meantem + I(meantem^2) + rain + I(rain^2)),
  lm.2 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + maxtem + mintem + rain + I(rain^2)),
  lm.3 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + GDD + HDD + rain + I(rain^2)),
  lm.4 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + meantem + I(meantem^2) + rain + I(rain^2) + Solarrad),
  lm.5 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + maxtem + mintem + rain + I(rain^2) + Solarrad),
  lm.6 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + GDD + HDD + rain + I(rain^2) + Solarrad),
  ##NEC、NWC:Intro-season
  lm.7 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                       meantem_5 + I(meantem_5^2) + meantem_6 + I(meantem_6^2) + 
                       meantem_7 + I(meantem_7^2) + meantem_8 + I(meantem_8^2) +
                       meantem_9 + I(meantem_9^2) + 
                       rain_5 + I(rain_5^2) + rain_6 + I(rain_6^2) + 
                       rain_7 + I(rain_7^2) + rain_8 + I(rain_8^2) + 
                       rain_9 + I(rain_9^2)),
  lm.8 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                       GDD_5 + GDD_6 + GDD_7 + GDD_8 + GDD_9 + 
                       HDD_5 + HDD_6 + HDD_7 + HDD_8 + HDD_9 + 
                       rain_5 + I(rain_5^2) + rain_6 + I(rain_6^2) + 
                       rain_7 + I(rain_7^2) + rain_8 + I(rain_8^2) + 
                       rain_9 + I(rain_9^2)),
  
  lm.9 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                       meantem_5 + I(meantem_5^2) + meantem_6 + I(meantem_6^2) + 
                       meantem_7 + I(meantem_7^2) + meantem_8 + I(meantem_8^2) +
                       meantem_9 + I(meantem_9^2) + 
                       rain_5 + I(rain_5^2) + rain_6 + I(rain_6^2) + 
                       rain_7 + I(rain_7^2) + rain_8 + I(rain_8^2) + 
                       rain_9 + I(rain_9^2) +
                       Solarrad_5 + Solarrad_6 + Solarrad_7 + Solarrad_8 + Solarrad_9),
  lm.10 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                        GDD_5 + GDD_6 + GDD_7 + GDD_8 + GDD_9 + 
                        HDD_5 + HDD_6 + HDD_7 + HDD_8 + HDD_9 + 
                        rain_5 + I(rain_5^2) + rain_6 + I(rain_6^2) + 
                        rain_7 + I(rain_7^2) + rain_8 + I(rain_8^2) + 
                        rain_9 + I(rain_9^2) + 
                        Solarrad_5 + Solarrad_6 + Solarrad_7 + Solarrad_8 + Solarrad_9),
  #NC:Intro-season
  lm.11 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                        meantem_6 + I(meantem_6^2) + 
                        meantem_7 + I(meantem_7^2) + meantem_8 + I(meantem_8^2) +
                        meantem_9 + I(meantem_9^2) + 
                        rain_6 + I(rain_6^2) + 
                        rain_7 + I(rain_7^2) + rain_8 + I(rain_8^2) + 
                        rain_9 + I(rain_9^2)),
  lm.12 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                        GDD_6 + GDD_7 + GDD_8 + GDD_9 + 
                        HDD_6 + HDD_7 + HDD_8 + HDD_9 + 
                        rain_6 + I(rain_6^2) + 
                        rain_7 + I(rain_7^2) + rain_8 + I(rain_8^2) + 
                        rain_9 + I(rain_9^2)),
  
  lm.13 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                        meantem_6 + I(meantem_6^2) + 
                        meantem_7 + I(meantem_7^2) + meantem_8 + I(meantem_8^2) +
                        meantem_9 + I(meantem_9^2) + 
                        rain_6 + I(rain_6^2) + 
                        rain_7 + I(rain_7^2) + rain_8 + I(rain_8^2) + 
                        rain_9 + I(rain_9^2) +
                        Solarrad_6 + Solarrad_7 + Solarrad_8 + Solarrad_9),
  lm.14 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                        GDD_6 + GDD_7 + GDD_8 + GDD_9 + 
                        HDD_6 + HDD_7 + HDD_8 + HDD_9 + 
                        rain_6 + I(rain_6^2) + 
                        rain_7 + I(rain_7^2) + rain_8 + I(rain_8^2) + 
                        rain_9 + I(rain_9^2) + 
                        Solarrad_6 + Solarrad_7 + Solarrad_8 + Solarrad_9),
  #SWC:Intro-season
  lm.15 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                        meantem_4 + I(meantem_4^2) + 
                        meantem_5 + I(meantem_5^2) + meantem_6 + I(meantem_6^2) + 
                        meantem_7 + I(meantem_7^2) +  
                        rain_4 + I(rain_4^2) + 
                        rain_5 + I(rain_5^2) + rain_6 + I(rain_6^2) + 
                        rain_7 + I(rain_7^2)),
  lm.16 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                        GDD_4 + GDD_5 + GDD_6 + GDD_7 + 
                        HDD_4 +HDD_5 + HDD_6 + HDD_7 + 
                        rain_4 + I(rain_4^2) + 
                        rain_5 + I(rain_5^2) + rain_6 + I(rain_6^2) + 
                        rain_7 + I(rain_7^2)),
  
  lm.17 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                        meantem_4 + I(meantem_4^2) + 
                        meantem_5 + I(meantem_5^2) + meantem_6 + I(meantem_6^2) + 
                        meantem_7 + I(meantem_7^2) +  
                        rain_4 + I(rain_4^2) + 
                        rain_5 + I(rain_5^2) + rain_6 + I(rain_6^2) + 
                        rain_7 + I(rain_7^2) +
                        Solarrad_4 + Solarrad_5 + Solarrad_6 + Solarrad_7),
  lm.18 <- as.formula(Log_Yield ~ Var_Yield + Site_Yield + Start_Year + I(Start_Year^2) + 
                        GDD_4 + GDD_5 + GDD_6 + GDD_7 + 
                        HDD_4 + HDD_5 + HDD_6 + HDD_7 + 
                        rain_4 + I(rain_4^2) + 
                        rain_5 + I(rain_5^2) + rain_6 + I(rain_6^2) + 
                        rain_7 + I(rain_7^2) + 
                        Solarrad_4 + Solarrad_5 + Solarrad_6 + Solarrad_7)
  
)


##Set the random number seed
set.seed(333)
train.control <- trainControl(method = "repeatedcv", repeats = 10, number = 10)
##NEC
model.nec.1 <- train(model.design[[1]], data = data.nec, method = "lm", trControl = train.control)
model.nec.2 <- train(model.design[[2]], data = data.nec, method = "lm", trControl = train.control)
model.nec.3 <- train(model.design[[3]], data = data.nec, method = "lm", trControl = train.control)
model.nec.4 <- train(model.design[[4]], data = data.nec, method = "lm", trControl = train.control)
model.nec.5 <- train(model.design[[5]], data = data.nec, method = "lm", trControl = train.control)
model.nec.6 <- train(model.design[[6]], data = data.nec, method = "lm", trControl = train.control)
model.nec.7 <- train(model.design[[7]], data = data.nec, method = "lm", trControl = train.control)
model.nec.8 <- train(model.design[[8]], data = data.nec, method = "lm", trControl = train.control)
model.nec.9 <- train(model.design[[9]], data = data.nec, method = "lm", trControl = train.control)
model.nec.10 <- train(model.design[[10]], data = data.nec, method = "lm", trControl = train.control)
##NC
model.nc.1 <- train(model.design[[1]], data = data.nc, method = "lm", trControl = train.control)
model.nc.2 <- train(model.design[[2]], data = data.nc, method = "lm", trControl = train.control)
model.nc.3 <- train(model.design[[3]], data = data.nc, method = "lm", trControl = train.control)
model.nc.4 <- train(model.design[[4]], data = data.nc, method = "lm", trControl = train.control)
model.nc.5 <- train(model.design[[5]], data = data.nc, method = "lm", trControl = train.control)
model.nc.6 <- train(model.design[[6]], data = data.nc, method = "lm", trControl = train.control)
model.nc.7 <- train(model.design[[11]], data = data.nc, method = "lm", trControl = train.control)
model.nc.8 <- train(model.design[[12]], data = data.nc, method = "lm", trControl = train.control)
model.nc.9 <- train(model.design[[13]], data = data.nc, method = "lm", trControl = train.control)
model.nc.10 <- train(model.design[[14]], data = data.nc, method = "lm", trControl = train.control)
##NWC
model.nwc.1 <- train(model.design[[1]], data = data.nwc, method = "lm", trControl = train.control)
model.nwc.2 <- train(model.design[[2]], data = data.nwc, method = "lm", trControl = train.control)
model.nwc.3 <- train(model.design[[3]], data = data.nwc, method = "lm", trControl = train.control)
model.nwc.4 <- train(model.design[[4]], data = data.nwc, method = "lm", trControl = train.control)
model.nwc.5 <- train(model.design[[5]], data = data.nwc, method = "lm", trControl = train.control)
model.nwc.6 <- train(model.design[[6]], data = data.nwc, method = "lm", trControl = train.control)
model.nwc.7 <- train(model.design[[7]], data = data.nwc, method = "lm", trControl = train.control)
model.nwc.8 <- train(model.design[[8]], data = data.nwc, method = "lm", trControl = train.control)
model.nwc.9 <- train(model.design[[9]], data = data.nwc, method = "lm", trControl = train.control)
model.nwc.10 <- train(model.design[[10]], data = data.nwc, method = "lm", trControl = train.control)
##SWC
model.swc.1 <- train(model.design[[1]], data = data.swc, method = "lm", trControl = train.control)
model.swc.2 <- train(model.design[[2]], data = data.swc, method = "lm", trControl = train.control)
model.swc.3 <- train(model.design[[3]], data = data.swc, method = "lm", trControl = train.control)
model.swc.4 <- train(model.design[[4]], data = data.swc, method = "lm", trControl = train.control)
model.swc.5 <- train(model.design[[5]], data = data.swc, method = "lm", trControl = train.control)
model.swc.6 <- train(model.design[[6]], data = data.swc, method = "lm", trControl = train.control)
model.swc.7 <- train(model.design[[15]], data = data.swc, method = "lm", trControl = train.control)
model.swc.8 <- train(model.design[[16]], data = data.swc, method = "lm", trControl = train.control)
model.swc.9 <- train(model.design[[17]], data = data.swc, method = "lm", trControl = train.control)
model.swc.10 <- train(model.design[[18]], data = data.swc, method = "lm", trControl = train.control)


##Return the model fitting coefficient


cal_cof <- function(cal.model, cal.type, cal.region) {
  cal.model.1 <- summary(cal.model)
  cal.model.1 <- cal.model.1$coefficients %>% as.data.frame()
  cal.model.1$Model_Index <- rownames(cal.model.1)
  cal.model.1 <- cal.model.1 %>%
    mutate(Model_Type = cal.type) %>%
    mutate(Region = cal.region)
  return(cal.model.1)
}
model.nec.cof <- cal_cof(model.nec.1, "Type_1", "NEC") %>%
  rbind(cal_cof(model.nec.2, "Type_2", "NEC")) %>%
  rbind(cal_cof(model.nec.3, "Type_3", "NEC")) %>%
  rbind(cal_cof(model.nec.4, "Type_4", "NEC")) %>%
  rbind(cal_cof(model.nec.5, "Type_5", "NEC")) %>%
  rbind(cal_cof(model.nec.6, "Type_6", "NEC")) %>%
  rbind(cal_cof(model.nec.7, "Type_7", "NEC")) %>%
  rbind(cal_cof(model.nec.8, "Type_8", "NEC")) %>%
  rbind(cal_cof(model.nec.9, "Type_9", "NEC")) %>%
  rbind(cal_cof(model.nec.10, "Type_10", "NEC"))
model.nc.cof <- cal_cof(model.nc.1, "Type_1", "NC") %>%
  rbind(cal_cof(model.nc.2, "Type_2", "NC")) %>%
  rbind(cal_cof(model.nc.3, "Type_3", "NC")) %>%
  rbind(cal_cof(model.nc.4, "Type_4", "NC")) %>%
  rbind(cal_cof(model.nc.5, "Type_5", "NC")) %>%
  rbind(cal_cof(model.nc.6, "Type_6", "NC")) %>%
  rbind(cal_cof(model.nc.7, "Type_7", "NC")) %>%
  rbind(cal_cof(model.nc.8, "Type_8", "NC")) %>%
  rbind(cal_cof(model.nc.9, "Type_9", "NC")) %>%
  rbind(cal_cof(model.nc.10, "Type_10", "NC"))
model.nwc.cof <- cal_cof(model.nwc.1, "Type_1", "NWC") %>%
  rbind(cal_cof(model.nwc.2, "Type_2", "NWC")) %>%
  rbind(cal_cof(model.nwc.3, "Type_3", "NWC")) %>%
  rbind(cal_cof(model.nwc.4, "Type_4", "NWC")) %>%
  rbind(cal_cof(model.nwc.5, "Type_5", "NWC")) %>%
  rbind(cal_cof(model.nwc.6, "Type_6", "NWC")) %>%
  rbind(cal_cof(model.nwc.7, "Type_7", "NWC")) %>%
  rbind(cal_cof(model.nwc.8, "Type_8", "NWC")) %>%
  rbind(cal_cof(model.nwc.9, "Type_9", "NWC")) %>%
  rbind(cal_cof(model.nwc.10, "Type_10", "NWC"))
model.swc.cof <- cal_cof(model.swc.1, "Type_1", "SWC") %>%
  rbind(cal_cof(model.swc.2, "Type_2", "SWC")) %>%
  rbind(cal_cof(model.swc.3, "Type_3", "SWC")) %>%
  rbind(cal_cof(model.swc.4, "Type_4", "SWC")) %>%
  rbind(cal_cof(model.swc.5, "Type_5", "SWC")) %>%
  rbind(cal_cof(model.swc.6, "Type_6", "SWC")) %>%
  rbind(cal_cof(model.swc.7, "Type_7", "SWC")) %>%
  rbind(cal_cof(model.swc.8, "Type_8", "SWC")) %>%
  rbind(cal_cof(model.swc.9, "Type_9", "SWC")) %>%
  rbind(cal_cof(model.swc.10, "Type_10", "SWC"))

model.cof <- rbind(model.nec.cof, model.nc.cof, model.nwc.cof, model.swc.cof)

##Plot seasonal temperature effects on yield

data.1 <- read.csv("model.cof.csv") %>%
  filter(Model_Type == "Type_9")

##NEC
data.2 <- data.1 %>% filter(Region == "NEC") %>% as.data.frame()
x1 <- c(5, 6, 7, 8, 9)
y1 <- seq(5, 35, 0.5)
c1 <- data.2[c(6, 8, 10, 12, 14), 1]
c2 <- data.2[c(7, 9, 11, 13, 15), 1]
z1 <- expand.grid(x1, y1)
len.1 <- length(z1[,1])
for (i.1 in 1 : len.1) {
  i.1.1 <- z1[i.1, "Var1"] - 4
  i.1.2 <- z1[i.1, "Var2"]
  z1[i.1, "Value"] <- (exp(c1[i.1.1] * 1) + exp(c2[i.1.1] * ((i.1.2 + 1) * (i.1.2 + 1) - i.1.2 * i.1.2)) - 2) * 100
}

##NC
data.2 <- data.1 %>% filter(Region == "NC") %>% as.data.frame()
x1 <- c(6, 7, 8, 9)
y1 <- seq(5, 35, 0.5)
c1 <- data.2[c(6, 8, 10, 12), 1]
c2 <- data.2[c(7, 9, 11, 13), 1]
z2 <- expand.grid(x1, y1)
len.1 <- length(z2[,1])
for (i.1 in 1 : len.1) {
  i.1.1 <- z2[i.1, "Var1"] - 5
  i.1.2 <- z2[i.1, "Var2"]
  z2[i.1, "Value"] <- (exp(c1[i.1.1] * 1) + exp(c2[i.1.1] * ((i.1.2 + 1) * (i.1.2 + 1) - i.1.2 * i.1.2)) - 2) * 100
}

##NWC
data.2 <- data.1 %>% filter(Region == "NWC") %>% as.data.frame()
x1 <- c(5, 6, 7, 8, 9)
y1 <- seq(5, 35, 0.5)
c1 <- data.2[c(6, 8, 10, 12, 14), 1]
c2 <- data.2[c(7, 9, 11, 13, 15), 1]
z3 <- expand.grid(x1, y1)
len.1 <- length(z3[,1])
for (i.1 in 1 : len.1) {
  i.1.1 <- z3[i.1, "Var1"] - 4
  i.1.2 <- z3[i.1, "Var2"]
  z3[i.1, "Value"] <- (exp(c1[i.1.1] * 1) + exp(c2[i.1.1] * ((i.1.2 + 1) * (i.1.2 + 1) - i.1.2 * i.1.2)) - 2) * 100
}

##SWC
data.2 <- data.1 %>% filter(Region == "SWC") %>% as.data.frame()
x1 <- c(4, 5, 6, 7)
y1 <- seq(5, 35, 0.5)
c1 <- data.2[c(6, 8, 10, 12), 1]
c2 <- data.2[c(7, 9, 11, 13), 1]
z4 <- expand.grid(x1, y1)
len.1 <- length(z4[,1])
for (i.1 in 1 : len.1) {
  i.1.1 <- z4[i.1, "Var1"] - 3
  i.1.2 <- z4[i.1, "Var2"]
  z4[i.1, "Value"] <- (exp(c1[i.1.1] * 1) + exp(c2[i.1.1] * ((i.1.2 + 1) * (i.1.2 + 1) - i.1.2 * i.1.2)) - 2) * 100
}


z1 <- z1 %>% mutate(Region = "Northeast China")
z2 <- z2 %>% mutate(Region = "North China")
z3 <- z3 %>% mutate(Region = "Northwest China")
z4 <- z4 %>% mutate(Region = "Southwest China")
data.z <- rbind(z1, z2, z3, z4)
data.z$Region <- factor(data.z$Region, levels = c("Northeast China", "North China", "Southwest China", "Northwest China"))


color.1 <- paletteer_c("ggthemes::Orange-Blue-White Diverging", 58)[1 : 28]
color.2 <- paletteer_c("ggthemes::Orange-Blue-White Diverging", 58)[31 : 58]

p1 <- ggplot(data.z, aes(x = Var1, y = Var2)) +
  geom_contour_fill(aes(z = Value, fill = stat(level)), breaks = c(seq(-7,0,0.25), seq(0.5,13.5,0.5))) +
  scale_fill_manual(values = c(color.1, color.2)) +
  facet_wrap(.~Region, nrow = 1) +
  labs(x = "Month", y = "Temperature (℃)") +
  scale_y_continuous(limits = c(4, 36), breaks = c(5, 10, 15, 20, 25, 30, 35), expand = c(0,0)) +
  theme_light() +
  theme(axis.text = element_text(size = 7, color = "black"),
        axis.title = element_text(size = 7, color = "black"),
        strip.text = element_text(size = 7, color = "black"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  guides(fill = "none")


##Plot seasonal Precipitation effects on yield
data.1 <- read.csv("cof.csv") %>%
  filter(Model_Type == "Type_9")


##NEC
data.2 <- data.1 %>% filter(Region == "NEC") %>% as.data.frame()
x1 <- c(5, 6, 7, 8, 9)
y1 <- seq(0, 350, 5)
c1 <- data.2[c(16, 18, 20, 22, 24), 1]
c2 <- data.2[c(17, 19, 21, 23, 25), 1]
z1 <- expand.grid(x1, y1)
len.1 <- length(z1[,1])
for (i.1 in 1 : len.1) {
  i.1.1 <- z1[i.1, "Var1"] - 4
  i.1.2 <- z1[i.1, "Var2"]
  z1[i.1, "Value"] <- (exp(c1[i.1.1] * 10) + exp(c2[i.1.1] * ((i.1.2 + 10) * (i.1.2 + 10) - i.1.2 * i.1.2)) - 2) * 100
}


##NC
data.2 <- data.1 %>% filter(Region == "NC") %>% as.data.frame()
x1 <- c(6, 7, 8, 9)
y1 <- seq(0, 400, 5)
c1 <- data.2[c(14, 16, 18, 20), 1]
c2 <- data.2[c(15, 17, 19, 21), 1]
z2 <- expand.grid(x1, y1)
len.1 <- length(z2[,1])
for (i.1 in 1 : len.1) {
  i.1.1 <- z2[i.1, "Var1"] - 5
  i.1.2 <- z2[i.1, "Var2"]
  z2[i.1, "Value"] <- (exp(c1[i.1.1] * 10) + exp(c2[i.1.1] * ((i.1.2 + 10) * (i.1.2 + 10) - i.1.2 * i.1.2)) - 2) * 100
}

##NWC
data.2 <- data.1 %>% filter(Region == "NWC") %>% as.data.frame()
x1 <- c(5, 6, 7, 8, 9)
y1 <- seq(0, 200, 5)
c1 <- data.2[c(16, 18, 20, 22, 24), 1]
c2 <- data.2[c(17, 19, 21, 23, 25), 1]
z3 <- expand.grid(x1, y1)
len.1 <- length(z3[,1])
for (i.1 in 1 : len.1) {
  i.1.1 <- z3[i.1, "Var1"] - 4
  i.1.2 <- z3[i.1, "Var2"]
  z3[i.1, "Value"] <- (exp(c1[i.1.1] * 10) + exp(c2[i.1.1] * ((i.1.2 + 10) * (i.1.2 + 10) - i.1.2 * i.1.2)) - 2) * 100
}


##SWC
data.2 <- data.1 %>% filter(Region == "SWC") %>% as.data.frame()
x1 <- c(4, 5, 6, 7)
y1 <- seq(0, 450, 5)
c1 <- data.2[c(14, 16, 18, 20), 1]
c2 <- data.2[c(15, 17, 19, 21), 1]
z4 <- expand.grid(x1, y1)
len.1 <- length(z4[,1])
for (i.1 in 1 : len.1) {
  i.1.1 <- z4[i.1, "Var1"] - 3
  i.1.2 <- z4[i.1, "Var2"]
  z4[i.1, "Value"] <- (exp(c1[i.1.1] * 10) + exp(c2[i.1.1] * ((i.1.2 + 10) * (i.1.2 + 10) - i.1.2 * i.1.2)) - 2) * 100
}

z1 <- z1 %>% mutate(Region = "Northeast China")
z2 <- z2 %>% mutate(Region = "North China")
z3 <- z3 %>% mutate(Region = "Northwest China")
z4 <- z4 %>% mutate(Region = "Southwest China")
data.z <- rbind(z1, z2, z3, z4)
data.z$Region <- factor(data.z$Region, levels = c("Northeast China", "North China", "Southwest China", "Northwest China"))


color.1 <- paletteer_c("ggthemes::Orange-Blue-White Diverging", 60)[1 : 28]
color.2 <- paletteer_c("ggthemes::Orange-Blue-White Diverging", 44)[23 : 44]
p1 <- ggplot(data.z, aes(x = Var1, y = Var2)) +
  geom_contour_fill(aes(z = Value, fill = stat(level)), breaks = c(seq(-2.8, 0, 0.1), seq(0.1, 2.1, 0.1)) )+
  scale_fill_manual(values = c(color.1, color.2)) +
  facet_wrap(.~Region, nrow = 1) +
  labs(x = "Month", y = "Precipitation (mm)") +
  scale_y_continuous(limits = c(-10, 460), breaks = seq(0, 450, 100), expand = c(0,0)) +
  theme_bw() +
  theme(axis.text = element_text(size = 7, color = "black"),
        axis.title = element_text(size = 7, color = "black"),
        strip.text = element_text(size = 7, color = "black"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  guides(fill = "none")



























