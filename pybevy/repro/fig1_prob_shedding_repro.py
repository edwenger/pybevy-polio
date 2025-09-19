"""
Single panel figure showing probability of shedding survival curves for fixed immunity levels.
Shows WPV (solid) and Sabin2 (dashed) lines at each immunity level, with color indicating immunity level.
"""

import numpy as np
import matplotlib.pyplot as plt
import pybevy as pb

# Fixed immunity levels to test
IMMUNITY_LEVELS = [1, 4, 16, 64, 256, 1024]

# Color scheme for immunity levels
IMMUNITY_COLORS = {
    1: '#1f77b4',    # blue
    4: '#ff7f0e',    # orange
    16: '#2ca02c',   # green
    64: '#d62728',   # red
    256: '#9467bd',  # purple
    1024: '#8c564b'  # brown
}

def generate_survival_curve_for_strain_and_immunity(strain_name, immunity_level, n_realizations=2000):
    """Generate survival curve using pybevy model with specified strain and immunity level."""

    # Map strain name to pybevy types
    if strain_name == "WPV":
        strain_enum, serotype_enum = pb.parse_infection_type("WPV2")
    elif strain_name == "Sabin2":
        strain_enum, serotype_enum = pb.parse_infection_type("OPV2")
    else:
        raise ValueError(f"Unknown strain: {strain_name}")

    # Setup model
    polio_params = pb.Params()
    max_days = 70

    # Track survival across realizations
    survival_data = np.zeros((n_realizations, max_days))

    for realization in range(n_realizations):
        # Create immunity state with specified level
        immunity = pb.Immunity()
        immunity.current_immunity = immunity_level

        # Create and initialize infection
        infection = pb.Infection(0.0, 0.0, strain_enum, serotype_enum)
        infection.set_prognoses(immunity, 0, polio_params)

        # Track when infection clears
        for day in range(max_days):
            if infection.should_clear_infection(day):
                survival_data[realization, day:] = 0
                break
            else:
                survival_data[realization, day] = 1

    # Calculate survival probability over time
    days = np.arange(max_days)
    survival_prob = np.mean(survival_data, axis=0)

    return days, survival_prob

def create_probability_shedding_figure():
    """Create single panel showing survival curves for different immunity levels and strains."""

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    print("Generating survival curves...")

    # Generate curves for each immunity level and both strains
    for immunity_level in IMMUNITY_LEVELS:
        color = IMMUNITY_COLORS[immunity_level]

        print(f"Processing immunity level {immunity_level}...")

        # WPV strain (solid line)
        days_wpv, survival_wpv = generate_survival_curve_for_strain_and_immunity(
            "WPV", immunity_level
        )
        ax.plot(days_wpv, survival_wpv, '-',
                color=color, linewidth=2.5,
                label=f'WPV (immunity={immunity_level})' if immunity_level == IMMUNITY_LEVELS[0] else "")

        # Sabin2 strain (dashed line)
        days_sabin2, survival_sabin2 = generate_survival_curve_for_strain_and_immunity(
            "Sabin2", immunity_level
        )
        ax.plot(days_sabin2, survival_sabin2, '--',
                color=color, linewidth=2.5,
                label=f'Sabin2 (immunity={immunity_level})' if immunity_level == IMMUNITY_LEVELS[0] else "")

    # Create custom legend
    # First create strain legend
    import matplotlib.lines as mlines
    wpv_line = mlines.Line2D([], [], color='black', linestyle='-', linewidth=2.5, label='WPV')
    sabin2_line = mlines.Line2D([], [], color='black', linestyle='--', linewidth=2.5, label='Sabin2')

    # Then create immunity level legend
    immunity_legend_elements = []
    for immunity_level in IMMUNITY_LEVELS:
        color = IMMUNITY_COLORS[immunity_level]
        line = mlines.Line2D([], [], color=color, linewidth=2.5, label=f'Immunity = {immunity_level}')
        immunity_legend_elements.append(line)

    # Create two legends
    strain_legend = ax.legend(handles=[wpv_line, sabin2_line],
                             loc='upper right',
                             title='Strain',
                             fontsize=10)
    ax.add_artist(strain_legend)  # Add first legend back to plot

    immunity_legend = ax.legend(handles=immunity_legend_elements,
                               loc='center right',
                               title='Immunity Level',
                               fontsize=10)

    # Formatting
    ax.set_xlim(0, 70)
    ax.set_ylim(0, 1)
    ax.set_xlabel('Duration of infection (days)', fontsize=14)
    ax.set_ylabel('Fraction still shedding', fontsize=14)
    ax.set_title('Probability of Shedding: WPV vs Sabin2 at Different Immunity Levels', fontsize=16)
    ax.grid(True, alpha=0.3)

    # Style improvements
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=12)

    plt.tight_layout()

    return fig

if __name__ == "__main__":
    print("Creating probability of shedding reproduction figure...")
    fig = create_probability_shedding_figure()
    plt.show()
    print("Done!")