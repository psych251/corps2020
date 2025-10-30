# load packages
library(ggplot2)
library(dplyr)
library(tidyr)
library(here)

# Read data
data_raw <- read.csv(here('processed','transformed_dprime.csv'))

# Data Preparation
# convert Prop.Heard/Prod.Expected to numerical, and remove the NA values
data_raw$Prop.Heard <- as.numeric(as.character(data_raw$Prop.Heard))
data_raw$Prop.Expected <- as.numeric(as.character(data_raw$Prop.Expected))

data <- data_raw %>%
  filter(!is.na(Prop.Heard) & !is.na(Prop.Expected) & 
           !is.na(Block) & !is.na(ACondition) & !is.na(QCondition))
sprintf("You have removed %d trials due to uneligible responses", (nrow(data_raw)
                                                                  - nrow(data)))
sprintf("That takes up %.2f percent of total trials", 100*(nrow(data_raw) - nrow(data))/(nrow(data_raw)))

# to match the name with the figure
data_plot <- data %>%
  mutate(
    Form = ifelse(QCondition == "Predictable", "Form Constraining", "Form Unconstraining"),
    Answer_Consistency = ifelse(ACondition == "Plausible", "Semantically Consistent", "Semantically Inconsistent")
  )

heard_summary <- data_plot %>%
  group_by(Block, Form, Answer_Consistency) %>%
  summarise(
    mean_prop = mean(Prop.Heard, na.rm = TRUE),
    se = sd(Prop.Heard, na.rm = TRUE) / sqrt(n()),
    .groups = "drop"
  ) 

expected_summary <- data_plot %>%
  group_by(Block, Form, Answer_Consistency) %>%
  summarise(
    mean_prop = mean(Prop.Expected, na.rm = TRUE),
    se = sd(Prop.Expected, na.rm = TRUE) / sqrt(n()),
    .groups = "drop"
  )

heard_summary$Form = factor(heard_summary$Form, 
                            levels = c("Form Constraining", "Form Unconstraining"))
heard_summary$Answer_Consistency <- factor(heard_summary$Answer_Consistency,
                                              levels = c("Semantically Inconsistent", 
                                                         "Semantically Consistent"))
expected_summary$Form = factor(expected_summary$Form, 
                            levels = c("Form Constraining", "Form Unconstraining"))
expected_summary$Answer_Consistency <- factor(expected_summary$Answer_Consistency,
                                           levels = c("Semantically Inconsistent", 
                                                      "Semantically Consistent"))

accmeans <- ggplot(heard_summary,aes(x = Block, y = mean_prop, group =Answer_Consistency, linetype=Answer_Consistency)) +
  geom_line() +
  geom_point() +
  geom_errorbar(aes(ymin = mean_prop - se, ymax = mean_prop + se), 
                width = 0.08) +
  facet_grid(. ~ Form) + 
  scale_linetype_manual(values = c("Semantically Consistent" = "dashed", 
                                   "Semantically Inconsistent" = "solid")) +
  scale_x_continuous(breaks = c(1, 2, 3)) +
  scale_y_continuous(limits = c(0, 1.05), breaks = seq(0, 1, 0.25)) +
  labs(
    x = "Block",
    y = "Average Proportion of Words \n in Heard Answers Reported",
    linetype = 'Answer Types'
  ) +
  theme_minimal() +
  theme(
    strip.background = element_rect(fill = "gray85", color = NA),
    strip.text = element_text(size = 11, face = "bold"),
  )

accmeans
ggsave(here("out","accmeans.png"), plot = accmeans, width = 8, height = 6, dpi = 300)

expmeans <- ggplot(expected_summary,aes(x = Block, y = mean_prop, group = Answer_Consistency, linetype=Answer_Consistency)) +
  geom_line() +
  geom_point() +
  geom_errorbar(aes(ymin = mean_prop - se, ymax = mean_prop + se), 
                width = 0.08) +
  facet_grid(. ~ Form) + 
  scale_linetype_manual(values = c("Semantically Consistent" = "dashed", 
                                   "Semantically Inconsistent" = "solid")) +
  scale_x_continuous(breaks = c(1, 2, 3)) +
  scale_y_continuous(limits = c(0, 1.05), breaks = seq(0, 1, 0.25)) +
  labs(
    x = "Block",
    y = "Average Proportion of Words \n in Expected Answers Reported",
    linetype = 'Answer Types'
  ) +
  theme_minimal() +
  theme(
    strip.background = element_rect(fill = "gray85", color = NA),
    strip.text = element_text(size = 11, face = "bold"),
  )

expmeans
ggsave(here("out","expmeans.png"), plot = expmeans, width = 8, height = 6, dpi = 300)

  
  
