"""Demo script for visualizing infection viral shedding over time at different immunity levels"""

import matplotlib.pyplot as plt
import numpy as np
import pybevy as pb


def run_shedding_timeseries(immunity_level, age_years, n_realizations=10, max_days=60):
    """Run infection shedding simulation for given immunity level and host age"""

    polio_params = pb.Params()
    strain, serotype = pb.parse_infection_type("WPV2")

    shedding_data = np.zeros((n_realizations, max_days))

    for realization in range(n_realizations):

        # Create host and immunity with specified level
        immunity = pb.Immunity()
        immunity.current_immunity = immunity_level

        # Create infection
        infection = pb.Infection(0.0, 0.0, strain, serotype)
        infection.set_prognoses(immunity, 0, polio_params)  # sim_day = 0

        # Track shedding over time
        for day in range(max_days):
            age_in_months = age_years * 12.0 + day * 12.0 / 365.0  # Base age + days since infection
            t_since_infection = day

            # Calculate viral shedding
            shedding = immunity.calculate_viral_shedding(
                age_in_months,
                t_since_infection,
                polio_params
            )

            shedding_data[realization, day] = shedding

            # Check if infection should clear
            if infection.should_clear_infection(t_since_infection):
                # Set remaining days to 0 for this realization
                shedding_data[realization, day:] = 0.0
                break

    return shedding_data


if __name__ == "__main__":

    immunity_levels = [2**0, 2**5, 2**10]  # Different immunity scales
    age_years_list = [0, 2, 20]  # Different age groups
    max_days = 60
    n_realizations = 100

    # Set up subplot grid
    fig, axes = plt.subplots(len(age_years_list), len(immunity_levels), figsize=(15, 8.4), sharey=True)
    fig.suptitle('Viral Shedding Over Time by Immunity Level and Age', fontsize=16)

    colors = ['blue', 'green', 'red']  # Different color for each immunity level

    for j, age_years in enumerate(age_years_list):
        for i, immunity_level in enumerate(immunity_levels):
            ax = axes[j, i]
            color = colors[i]

            # Run simulation for this immunity level and age
            shedding_data = run_shedding_timeseries(immunity_level, age_years, n_realizations, max_days)

            # Plot each realization
            days = np.arange(max_days)
            for realization in range(n_realizations):
                ax.plot(days, shedding_data[realization, :], color=color, alpha=0.6, linewidth=1)

            # Plot mean
            mean_shedding = np.mean(shedding_data, axis=0)
            ax.plot(days, mean_shedding, 'k-', linewidth=2, label='Mean')

            # Formatting
            if j == 0:  # Top row
                exponent = int(np.log2(immunity_level))
                ax.set_title(f'Immunity Level: 2$^{{{exponent}}}$')
            if j == len(age_years_list) - 1:  # Bottom row
                ax.set_xlabel('Days since infection')
            if i == 0:  # Left column
                ax.set_ylabel(f'Age {age_years} years\nViral shedding (CID50)')

            ax.set_yscale('log')
            ax.grid(True, alpha=0.3)
            if i == 0 and j == 0:  # Only show legend on first panel
                ax.legend()

    plt.tight_layout()
    plt.show()