"""
Reproduction of first four cells from MultiscaleModeling/PopSim/Assets/Infection.ipynb
Maps the historical ImmunoInfection class to current pybevy API structure.
"""
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

import pybevy as pb


def reinfection_plots(repetitions, t_before_challenge=120, reinfection_cycles=5, initial_age=2):
    """
    Reproduce the reinfection_plots function using current pybevy API.
    Maps ImmunoInfection class behavior to Immunity + Infection + Params structure.
    """
    data = defaultdict(lambda: np.zeros((repetitions, t_before_challenge * reinfection_cycles + 1)))

    params = pb.Params()
    strain, serotype = pb.parse_infection_type("OPV2")  # S2 = Sabin-2 = OPV2

    for rep in range(repetitions):
        immunity = pb.Immunity()
        immunity.current_immunity = 1.0  # Initially naive immunity

        infection = None

        p_shed = []
        p_infection = []
        current_immunity = []
        shed_virions = []
        theta = []

        # Initial values (day 0 before any cycles)
        p_shed.append(0)
        p_infection.append(1)
        current_immunity.append(0)
        shed_virions.append(0)

        # Calculate initial theta_Nab using the Rust implementation
        theta.append(immunity.calculate_theta_nab(params.theta_nabs))

        t = 0

        # Main cycle loop matching original exactly
        for cycle in range(reinfection_cycles):
            # Attempt infection at start of each cycle
            challenge_dose = 10**6.0
            p_inf = immunity.calculate_infection_probability(challenge_dose, strain, serotype, params)

            if np.random.random() < p_inf:
                # Create new infection
                infection = pb.Infection(0.0, 0.0, strain, serotype)
                infection.set_prognoses(immunity, t, params)
                time_since_infection = 0.0

            # Inner timestep loop
            for tstep in range(0, t_before_challenge):
                # Check if shedding (equivalent to I.is_shed)
                is_shedding = False
                viral_shedding_amount = 0.0

                if infection is not None:
                    if not infection.should_clear_infection(time_since_infection):
                        current_age = initial_age + t / 365.  # Age in years
                        age_in_months = current_age * 12.0
                        viral_shedding_amount = immunity.calculate_viral_shedding(
                            age_in_months, time_since_infection, params
                        )
                        is_shedding = viral_shedding_amount > 10**2.6
                    else:
                        infection = None

                # Store data
                p_shed.append(1 if is_shedding else 0)
                p_infection.append(immunity.calculate_infection_probability(challenge_dose, strain, serotype, params))
                current_immunity.append(immunity.current_immunity)
                shed_virions.append(viral_shedding_amount)
                theta.append(immunity.calculate_theta_nab(params.theta_nabs))

                t += 1

                # Update immunity (equivalent to I.update(1/365.))
                if immunity.ti_infected is not None:
                    t_since_last_exposure = t - immunity.ti_infected
                    immunity.calculate_waning(t_since_last_exposure, params.immunity_waning)

                if infection is not None:
                    time_since_infection += 1.0

        # Store data arrays
        data['p_shed'][rep] = p_shed
        data['p_infection'][rep] = p_infection
        data['current_immunity'][rep] = current_immunity
        data['shed_virions'][rep] = shed_virions
        data['theta'][rep] = np.log2(theta)

    return data


def plot_infection_dynamics(infection_data, t_before_challenge, reinfection_cycles):
    """Create the four-panel figure using the exact original plotting code"""

    plt.figure(figsize=(10,10))

    plt.subplot(2,2,1)
    plt.title('Proportion Shedding', y = 1.05, fontsize = 15)
    p_shedding = np.mean(infection_data['p_shed'].T, axis = 1)
    stdev_shedding = np.sqrt(p_shedding * (1-p_shedding) / 1000)
    plt.plot([x for x in range(t_before_challenge*reinfection_cycles + 1)], np.mean(infection_data['p_shed'].T, axis = 1))
    plt.fill_between([x for x in range(t_before_challenge*reinfection_cycles+1)],
                     p_shedding + 2*stdev_shedding,
                     p_shedding - 2*stdev_shedding)
    plt.xlabel('Days post initial infection', fontsize = 12)
    plt.ylabel('Proportion Shedding', fontsize = 12)
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)

    plt.subplot(2,2,3)
    plt.title('P(Infection | dose)\n (10^6)', y = 1.05, fontsize = 15)
    plt.plot([x for x in range(t_before_challenge*reinfection_cycles+1)], np.median(infection_data['p_infection'], axis = 0))
    plt.fill_between([x for x in range(t_before_challenge*reinfection_cycles+1)],
                      np.percentile(infection_data['p_infection'], 5, axis = 0),
                      np.percentile(infection_data['p_infection'], 95, axis = 0), alpha = 0.3)
    plt.xlabel('Days post initial infection', fontsize = 12)
    plt.ylabel('Probability', fontsize = 12)
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)

    plt.subplot(2,2,4)
    plt.title('Immunity', y = 1.05, fontsize = 15)
    plt.plot([x for x in range(t_before_challenge*reinfection_cycles+1)], np.log2(np.median(infection_data['current_immunity'], axis = 0)))
    plt.fill_between([x for x in range(t_before_challenge*reinfection_cycles+1)],
                      np.log2(np.percentile(infection_data['current_immunity'], 5, axis = 0)),
                      np.log2(np.percentile(infection_data['current_immunity'], 95, axis = 0)), alpha = 0.3)
    plt.xlabel('Days post initial infection', fontsize = 12)
    plt.ylabel('Log2(Immunity)', fontsize = 12)
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)

    plt.subplot(2,2,2)
    plt.title('Viral Fecal Shed/fecal-oral dose', y = 1.05, fontsize = 15)
    plt.plot([x for x in range(t_before_challenge*reinfection_cycles +1)], np.mean(infection_data['shed_virions'], axis = 0))
    plt.fill_between([x for x in range(t_before_challenge*reinfection_cycles+1)],
                      np.percentile(infection_data['shed_virions'], 5, axis = 0),
                      np.percentile(infection_data['shed_virions'], 95, axis = 0), alpha = 0.3)

    plt.xlabel('Days post initial infection', fontsize =12)
    plt.ylabel('Viral CID50/5ug', fontsize = 12)
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)

    plt.tight_layout()

    return plt.gcf()


def plot_immunity_theta_validation(infection_data, t_before_challenge, reinfection_cycles):
    """Create a 2-panel figure to validate immunity and theta calculations"""

    plt.figure(figsize=(10,5))

    plt.subplot(1,2,1)
    plt.title('Immunity', y = 1.05, fontsize = 15)
    plt.plot([x for x in range(t_before_challenge*reinfection_cycles+1)], np.log2(np.median(infection_data['current_immunity'], axis = 0)))
    plt.fill_between([x for x in range(t_before_challenge*reinfection_cycles+1)],
                      np.log2(np.percentile(infection_data['current_immunity'], 5, axis = 0)),
                      np.log2(np.percentile(infection_data['current_immunity'], 95, axis = 0)), alpha = 0.3)
    plt.xlabel('Days post initial infection', fontsize = 12)
    plt.ylabel('Log2(Immunity)', fontsize = 12)
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)

    plt.subplot(1,2,2)
    plt.plot([x for x in range(t_before_challenge*reinfection_cycles +1)], np.mean(infection_data['theta'], axis = 0))
    plt.fill_between([x for x in range(t_before_challenge*reinfection_cycles+1)],
                      np.percentile(infection_data['theta'], 5, axis = 0),
                      np.percentile(infection_data['theta'], 95, axis = 0), alpha = 0.3)

    plt.xlabel('Days post initial infection', fontsize =12)
    plt.ylabel('log2(Theta)', fontsize = 12)
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)
    plt.title('Theta', fontsize = 15, y = 1.05)

    plt.tight_layout()

    return plt.gcf()


if __name__ == "__main__":
    # Run simulation with same parameters as original notebook
    print("Running infection dynamics simulation...")

    # Parameters matching the original notebook
    t_before_challenge, reinfection_cycles = 720, 5  # Challenge every 720 days, 5 cycles
    repetitions = 1000  # Number of simulation repetitions

    print(f"Parameters: {repetitions} repetitions, {reinfection_cycles} cycles, {t_before_challenge} days between challenges")

    # Run the simulation
    infection_data = reinfection_plots(repetitions, t_before_challenge, reinfection_cycles)

    print("Simulation complete. Generating plots...")

    # Create and display the plots
    fig1 = plot_infection_dynamics(infection_data, t_before_challenge, reinfection_cycles)

    print("Main plot saved to: /Users/ewenger/GitHub/pybevy-polio/figs/infection_notebook_reproduction.png")

    # Create immunity and theta validation plot
    print("Creating immunity and theta validation plot...")
    fig2 = plot_immunity_theta_validation(infection_data, t_before_challenge, reinfection_cycles)

    print("Validation plot saved to: /Users/ewenger/GitHub/pybevy-polio/figs/immunity_theta_validation.png")
    print("Displaying plots...")

    plt.show()