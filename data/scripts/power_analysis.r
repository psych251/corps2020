# load packages
library(lme4)
library(simr)
library(here)


# Load data 
data <- read.csv(here('reference', 'Experiment_1_Lmer_Analysis_Scripts_and_Data', 'online_data.csv'))
data$Participant <- as.factor(data$Participant)
data$ItemNo <- as.factor(data$ItemNo)
data$QLSAS <- scale(data$QLSA, TRUE, TRUE)
data$PL <- scale(data$Plaus, TRUE, TRUE)
data$BlockS <- scale(data$Block, TRUE, TRUE)

# Fit model
model <- glmer(
  cbind(Correct, Incorrect) ~ QLSAS * PL * BlockS + 
    (1 + BlockS || Participant) + 
    (1 + QLSAS * PL * BlockS || ItemNo),
  data = data,
  family = binomial,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))
)

# specify the effect from paper Table 3
fixef(model)["PL"] <- 4.29              

# Power simulation
power_n80 <- powerSim(
  model,
  test = fixed("PL"),      # Test Answer Consistency effect
  nsim = 500,              # 1000 simulations
  seed = 123
)
pc <- powerCurve(model, test = fixed("PL"), along = "Participant",
                 breaks = c(30, 40, 50, 60, 80), nsim = 500)
print(pc)
plot(pc)