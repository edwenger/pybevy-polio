library(reticulate)
library(ggplot2) 

pb <- import("pybevy")

theta_nabs <- pb$ThetaNabsParams()
immunity_waning <- pb$ImmunityWaningParams()

n_hosts <- 10
n_infections <- 10
t_since_last_exposure <- 2*365

plot_data <- data.frame(x_val = numeric(), y_val = numeric())

for (host in 1:n_hosts) {

    immunity <- pb$Immunity()

    for (infection in 1:n_infections) {

        # Boost on new infection
        immunity$update_peak_immunity(theta_nabs)

        # Plot pre- and post-boost Nabs
        plot_data <- rbind(plot_data, data.frame(x_val = immunity$prechallenge_immunity, y_val = immunity$current_immunity))
        # cat(sprintf("Pre/Post Challenge Immunity: ( %.2f, %.2f )\n", immunity$prechallenge_immunity, immunity$current_immunity))

        # Wane immunity
        immunity$current_immunity = pb$calculate_immunity_waning(
                    immunity$postchallenge_peak_immunity,
                    t_since_last_exposure,
                    immunity_waning$rate)
    }
}

if (!interactive()) pdf(NULL)

ggplot(plot_data, aes(x = x_val, y = y_val)) +
    geom_point() +
    scale_x_continuous(trans = "log2") +
    scale_y_continuous(trans = "log2") +
    labs(x = "pre-challenge immunity",
         y = "post-challenge immunity")

