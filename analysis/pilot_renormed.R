rm(list=ls())
source("~/Projects/R/Ranalysis/useful_dplyr.R")
d <- read.csv("~/Projects/embedded_implicature/Pragmatics-of-embedded-implicature/data/embeddedscalars-exp01-analysis-2014-12-04.csv")

d <- d %>% mutate(HumanMean = (HumanMean - 1) / 6) %>%
  group_by(Sentence) %>%
  mutate(HumanMeanNormalized = HumanMean / sum(HumanMean))

d$Condition <- factor(d$Condition, levels=c("NNN",
                                            "NNS",
                                            "NNA",
                                            "NSS",
                                            "NSA",
                                            "NAA",
                                            "SSS",
                                            "SSA",
                                            "SAA",
                                            "AAA"))        
d$shortSentence <- factor(d$Sentence, 
                          levels = c("no(player)(made(no(shot)))",
                                     "no(player)(made(some(shot)))",
                                     "no(player)(made(every(shot)))",
                                     "exactly_one(player)(made(no(shot)))",
                                     "exactly_one(player)(made(some(shot)))",
                                     "exactly_one(player)(made(every(shot)))",
                                     "every(player)(made(no(shot)))",
                                     "every(player)(made(some(shot)))",
                                     "every(player)(made(every(shot)))"),
                          labels = c("no...no","no..some","no...every",
                                     "one..no","one..some","one...every",
                                     "every..every","every..some","every..no"))

hd <- d %>% 
  select(-HumanLowerCI, -HumanUpperCI) %>%
  gather(Model, Value, LiteralListener:UncertaintyListener) %>%
  group_by(Model) %>%
  mutate(pearson = paste("pearson r =",
                         as.character(signif(cor.test(Value,HumanMeanNormalized,
                                   method="pearson")$estimate, 
                          digits=2))),
         spearman = paste("spearman r = ",
                          as.character(signif(cor.test(Value,HumanMeanNormalized,
                                    method="pearson")$estimate, 
                           digits=2))),
         mse = paste("MSE = ",
                     as.character(signif(mean((Value - HumanMeanNormalized)^2),
                      digits=2))))
  
quartz(width=8,height=3)
ggplot(hd, aes(x=Value, y=HumanMeanNormalized)) + 
  facet_wrap(~Model) +
  geom_text(aes(label=Condition, col=shortSentence), cex=3) + 
  geom_text(x=0.01,y=.95, aes(label=mse), col="red", hjust=0, cex=4) +
  geom_text(x=0.01,y=.85, aes(label=pearson), col="red", hjust=0, cex=4) +
  geom_text(x=0.01,y=.75, aes(label=spearman), col="red", hjust=0, cex=4) +
  geom_abline(intercept=0,slope=1, col="black", lty=3) +
  geom_smooth(aes(group=1),  method="lm", lty=2, col="black") +
  xlab("Lexical Uncertainty Listener") + 
  ylab("Normalized Human Ratings") + 
  xlim(c(0,1)) + ylim(c(0,1))


hdm <- d %>% 
  select(-HumanLowerCI, -HumanUpperCI) %>%
  gather(Model, Value, LiteralListener:UncertaintyListener) %>%
  group_by(Model, shortSentence) %>%
  mutate(pearson = paste("pearson r =",
                         as.character(signif(cor.test(Value,HumanMeanNormalized,
                                                      method="pearson")$estimate, 
                                             digits=2))),
         spearman = paste("spearman r = ",
                          as.character(signif(cor.test(Value,HumanMeanNormalized,
                                                       method="pearson")$estimate, 
                                              digits=2))),
         mse = paste("MSE = ",
                     as.character(signif(mean((Value - HumanMeanNormalized)^2),
                                         digits=2))))
quartz(width=7,height=9)
ggplot(hdm, aes(x=Value, y=HumanMeanNormalized)) + 
  facet_grid(shortSentence~Model) +
  geom_text(aes(label=Condition), cex=2) + 
  geom_text(x=0.01,y=.95, aes(label=mse), col="red", hjust=0, cex=3) +
  geom_text(x=0.01,y=.80, aes(label=pearson), col="red", hjust=0, cex=3) +
  geom_text(x=0.01,y=.65, aes(label=spearman), col="red", hjust=0, cex=3) +
  geom_abline(intercept=0,slope=1, col="black", lty=3) +
  geom_smooth(aes(group=1),  method="lm", lty=2, col="black") +
  xlab("Lexical Uncertainty Listener") + 
  ylab("Normalized Human Ratings") + 
  xlim(c(0,1)) + ylim(c(0,1))


##### INDIVIDUAL CONDITIONS
md <- d %>% 
  gather(Model, Value, LiteralListener, RSAListener, UncertaintyListener, HumanMeanNormalized)

quartz(height=3.5,width=10)
qplot(Condition, Value, fill=Model, 
      facets = shortSentence~Model, geom="bar",
      stat="identity",
      position="dodge", 
      data=filter(md, Model != "HumanMean", 
                  shortSentence == "one..some")) +
  theme(axis.text.x = element_text(angle = 90,vjust=0.5))

quartz(height=3.5,width=10)
qplot(Condition, Value, fill=Model, 
      facets = shortSentence~Model, geom="bar",
      stat="identity",
      position="dodge", 
      data=filter(md, Model != "HumanMean", 
                  shortSentence == "every..some")) +
  theme(axis.text.x = element_text(angle = 90,vjust=0.5))

quartz(height=3.5,width=10)
qplot(Condition, Value, fill=Model, 
      facets = shortSentence~Model, geom="bar",
      stat="identity",
      position="dodge", 
      data=filter(md, Model != "HumanMean", 
                  shortSentence == "no..some")) +
  theme(axis.text.x = element_text(angle = 90,vjust=0.5))

qplot(Condition, Value, fill=Model, 
      facets = shortSentence~Model, geom="bar",
      stat="identity",
      position="dodge", 
      data=md) +
  theme(axis.text.x = element_text(angle = 90,vjust=0.5))
