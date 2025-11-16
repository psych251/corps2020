##  For practical reasons, just use a simple ANOVA from BayesPower package instead 
# of running simulation with complex brms models to approximate the power
# xirohu@stanford.edu

# load package
library(here)
library(tidyverse)
library(dplyr)
library(BayesPower)
library(BayesFactor)
library(effectsize)

## Compute the effect size from the original dataset with a simple ANOVA
ori_df <- read.csv(here('reference', 'Experiment 1 Bayes Analysis Scripts and Data', 'dprime.csv'))
ori_df <- ori_df |>
  mutate(across(c(ACondition, QCondition), as.factor))
ori_aov <- aov(Prop.Expected ~ ACondition*QCondition, data = ori_df)
summary(ori_aov)
eta_results <- eta_squared(ori_aov)
print(eta_results)
interact_eta <- eta_results$Eta2[eta_results$Parameter == "ACondition:QCondition"]
cohens_f2 <- interact_eta / (1 - interact_eta) # smaller than 0.01 (the lower bound of the BayesPower app)

# Launch the BayesPower app
BayesPower::BayesPower_BayesFactor()
# calculate the sample size for 80% of the power
BFpower.f(
  inter = "2",
  e = 0.01,
  D = 3,
  target = 0.8,
  p = 3,
  k = 4,
  model = "effectsize",
  dff = 1,
  rscale = 1,
  f_m = 0.1,
  de_an_prior = 1,
  mode_bf = 1,
  direct = "h0"
)
# calculate the sample size for 90% of power
BFpower.f(
  inter = "2",
  e = 0.01,
  D = 3,
  target = 0.9,
  p = 3,
  k = 4,
  model = "effectsize",
  dff = 1,
  rscale = 1,
  f_m = 0.1,
  de_an_prior = 1,
  mode_bf = 1,
  direct = "h0"
)
