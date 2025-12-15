set.seed(123)

library(brms)
library(rstan)
library(here)
rstan_options(auto_write = TRUE)
options(mc.cores = parallel::detectCores())

my_prior = set_prior('student_t(10,0,1)', class="b")
data_file <- here('processed', 'transformed_dprime.csv')
d <- read.csv(data_file)

d$Participant <- as.factor(d$Participant)
d$ItemNo <- as.factor(d$ItemNo)
d$QLSAS <- scale(d$QLSA, T, T)
d$PL <- scale(d$Plaus, T, T)
d$BlockS <- scale(d$Block, T, T)

full_brmsd = brm(Plaus.HIT | trials(EA.Wlength) ~ QLSAS*PL*BlockS+(1+BlockS||Participant)+(1+QLSAS*PL*BlockS||ItemNo),
                 data=d,
                 iter=10000,
                 save_all_pars=TRUE,
                 prior=my_prior,
                 family=binomial())
summary(full_brmsd)

null_brms_QLSA= update(full_brmsd, formula = ~ .-QLSAS, save_all_pars=TRUE)
bayes_factor(full_brmsd, null_brms_QLSA)

null_brms_PL = update(full_brmsd, formula = ~ .-PL, save_all_pars=TRUE)
bayes_factor(full_brmsd, null_brms_PL)

null_brms_Block = update(full_brmsd, formula = ~ .-BlockS, save_all_pars=TRUE)
bayes_factor(full_brmsd, null_brms_Block)

null_brms_QLSAPL = update(full_brmsd, formula = ~ .-QLSAS:PL, save_all_pars=TRUE)
bayes_factor(full_brmsd, null_brms_QLSAPL)

null_brms_QLSAblock = update(full_brmsd, formula = ~ .-QLSAS:BlockS, save_all_pars=TRUE)
bayes_factor(full_brmsd, null_brms_QLSAblock)

null_brms_PLblock = update(full_brmsd, formula = ~ .-PL:BlockS, save_all_pars=TRUE)
bayes_factor(full_brmsd, null_brms_PLblock)

null_brms_blockinter = update(full_brmsd, formula = ~ .-QLSAS:PL:BlockS, save_all_pars=TRUE)
bayes_factor(full_brmsd, null_brms_blockinter)