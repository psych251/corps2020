# This is the adapted version of JML_Experiment_1_Script.Rmd from the OSF file by Corps 2020 (https://osf.io/5cqy9)
library(here)
data_file <- here('processed', 'transformed_dprime_pilotB.csv')
data <- read.csv(data_file)
data$Participant <- as.factor(data$Participant)
data$ItemNo <- as.factor(data$ItemNo)
data$ACondition <- as.factor(data$ACondition)
data$QCondition <- as.factor(data$QCondition)
levels(data$ACondition) <- c("Semantically Inconsistent", "Semantically Consistent")
levels(data$QCondition) <- c("Form Constraining", "Form Unconstraining")

se = function(x){
  sd(x)/sqrt(length(x))
}

library(doBy)
library(ggplot2)
library(lme4)
library(car)
library(gridExtra)
library(knitr)

## =================Accurate Analysis===============
data$BlockF <- as.factor(data$Block)
bypart <- summaryBy(Prop.Heard~Participant+BlockF+QCondition+ACondition, data=data, keep.names=T, na.rm=T, FUN=c(mean))
sum <- summaryBy(Prop.Heard~BlockF+QCondition+ACondition, data=bypart, FUN=c(mean, se), keep.names=T)

accmeans <- ggplot(sum, aes(x=BlockF, y=Prop.Heard.mean, group=ACondition, linetype=ACondition)) + 
  geom_line(size=1) + 
  geom_point(size = 2)+facet_grid(~QCondition) + 
  geom_errorbar(aes(ymin=Prop.Heard.mean-Prop.Heard.se, ymax=Prop.Heard.mean+Prop.Heard.se), width=.08) +
  xlab("Block") + ylab("Average Proportion of Words \n in Heard Answer Reported Correctly") + labs(linetype="Answer Consistency") +
  ylim(0, 1) + scale_linetype_manual(values=c("solid", "dashed")) + 
  theme_bw() +
  theme(
    # Axis Title
    axis.title.x = element_text(size=16, colour = "black", margin=margin(t=10)),
    axis.title.y = element_text(size=16, colour = "black", margin=margin(r=10)),
    # Axis Text/Ticks (Size 12 is standard)
    axis.text.x = element_text(size=12, colour="black"),
    axis.text.y = element_text(size=12, colour="black"),
    # Legend (Size 12-14)
    legend.position = "bottom",
    legend.text = element_text(size=12),
    legend.title = element_text(size=14, face="bold"),
    legend.margin = margin(t = 0.5, unit='cm'),
    # Facet Headers (The boxes at the top)
    strip.text = element_text(size = 14)
  )
 plot_file = here("out", "accmeans_pilotB.png")
 ggsave(plot_file, accmeans, width=8, height=6)

##============Signal Detection Noise Analysis========================
d <- data
bypartd <- summaryBy(Prop.Expected~Participant+BlockF+QCondition+ACondition, data=d, keep.names=T, na.rm=T, FUN=c(mean))
sumd <- summaryBy(Prop.Expected~BlockF+QCondition+ACondition, data=bypartd, FUN=c(mean, se), keep.names=T)

expmeans <- ggplot(sumd, aes(x=BlockF, y=Prop.Expected.mean, group=ACondition, linetype=ACondition)) + 
  geom_line(size=1) + 
  geom_point(size = 2)+facet_grid(~QCondition) + 
  geom_errorbar(aes(ymin=Prop.Expected.mean-Prop.Expected.se, ymax=Prop.Expected.mean+Prop.Expected.se), width=.08) +
  xlab("Block") + ylab("Average Proportion of Words \n in Expected Answer Reported Correctly") + labs(linetype="Answer Consistency") +
  ylim(0, 1) + scale_linetype_manual(values=c("solid", "dashed")) + 
  theme_bw() +
  theme(
    # Axis Title
    axis.title.x = element_text(size=16, colour = "black", margin=margin(t=10)),
    axis.title.y = element_text(size=16, colour = "black", margin=margin(r=10)),
    # Axis Text/Ticks (Size 12 is standard)
    axis.text.x = element_text(size=12, colour="black"),
    axis.text.y = element_text(size=12, colour="black"),
    # Legend (Size 12-14)
    legend.position = "bottom",
    legend.text = element_text(size=12),
    legend.title = element_text(size=14, face="bold"),
    legend.margin = margin(t = 0.5, unit='cm'),
    # Facet Headers (The boxes at the top)
    strip.text = element_text(size = 14)
  )
plot_file = here("out", "expmeans_pilotB.png")
ggsave(plot_file, expmeans, width=8, height=6)

# run model analysis
d$QLSAS <- scale(d$QLSA, T, T)
d$PL <- scale(d$Plaus, T, T)
d$BlockS <- scale(d$Block, T, T)
m2 <- glmer(formula = cbind(d$Plaus.HIT, d$Plaus.Incorrect) ~
              QLSAS*PL*BlockS+(1+BlockS||Participant)+(1+QLSAS*PL*BlockS||ItemNo), data=d, family="binomial", control=glmerControl(optimizer="bobyqa", optCtrl=list(maxfun=2e5))) 
summary(m2)

