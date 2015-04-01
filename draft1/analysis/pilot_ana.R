rm(list=ls())
source("~/Projects/R/Ranalysis/useful.R")

d <- read.csv("data/basketball-pilot-2-11-14-results-parsed.csv")
tt <- read.csv("data/trial_types.csv")

## filter training trials
d <- subset(d,is.na(trainingCorrect))
d$condition <- factor(d$condition)

## some releveling
d$quant1 <- NA
d$quant1[grepl("Every",d$sentence)] <- "Every"
d$quant1[grepl("Exactly one",d$sentence)] <- "Exactly one"
d$quant1[grepl("No",d$sentence)] <- "No"
d$quant1 <- factor(d$quant1,levels=c("No","Exactly one","Every"))

d$quant2 <- NA
d$quant2[grepl("none",d$sentence)] <- "None"
d$quant2[grepl("some",d$sentence)] <- "Some"
d$quant2[grepl("all",d$sentence)] <- "All"
d$quant2 <- factor(d$quant2,levels=c("None","Some","All"))

d$condition <- revalue(d$condition,
                       c("none-none-none"="NNN",
                         "none-none-half"="NNS",
                         "none-none-all"="NNA",
                         "none-half-half"="NSS",
                         "none-half-all"="NSA",                         
                         "none-all-all"="NAA",
                         "half-half-half"="SSS",
                         "half-half-all"="SSA",
                         "half-all-all"="SAA",
                         "all-all-all"="AAA"))  
d$condition <- factor(d$condition, levels=c("NNN",
                                      "NNS",
                                      "NNA",
                                      "NSS",
                                      "NSA",
                                      "NAA",
                                      "SSS",
                                      "SSA",
                                      "SAA",
                                      "AAA"))          
                       
dtt <- merge(d,tt)
dtt$truth <- dtt$truth.chris==1 & dtt$truth.dan==1

mss <- aggregate(response ~ condition + sentence + trial.type + quant1 + quant2 + truth + workerid, 
                 data=dtt, mean)
ms <- aggregate(response ~ condition + sentence + trial.type + quant1 + quant2 + truth, 
                data=mss, mean)
ms$cih <- aggregate(response ~ condition + sentence + trial.type + quant1 + quant2 + truth, data=mss, ci.high)$response
ms$cil <- aggregate(response ~ condition + sentence + trial.type + quant1 + quant2 + truth, data=mss, ci.low)$response
ms$n <- aggregate(workerid ~ condition + sentence + trial.type + quant1 + quant2 + truth, data=mss, n.unique)$workerid


# quartz()
ggplot(subset(ms,trial.type=="target"),
       aes(x=condition, y=response, fill=truth, ymin=response-cil,
           ymax=response+cih)) + o
  geom_bar(stat="identity") + 
  geom_linerange() +
  ylim(c(0,7)) +
  facet_grid(quant1~quant2) + 
  geom_text(aes(x=5.5,y=7,label=sentence),hjust=.5,cex=3) +
  theme(axis.text.x = element_text(angle = 90,vjust=0.5))

qplot(response,facets=.~condition,
      data=subset(mss,trial.type=="target" &
                  sentence=="Exactly one player hit some of his shots"))

qplot(response,facets=.~condition,
      data=subset(mss,trial.type=="target" &
                    sentence=="No player hit none of his shots"))

qplot(response,facets=.~condition,
      data=subset(mss,trial.type=="target" &
                    sentence=="Every player hit some of his shots"))


qplot(response,facets=quant1~condition,
      data=subset(mss,trial.type=="target" &
                    quant2=="some"))