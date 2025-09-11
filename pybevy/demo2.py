"""Demo script for accessing low-level Python API to visualize behavior of disease model component logic"""

import pybevy as pb
import matplotlib.pyplot as plt

theta_nabs = pb.ThetaNabsParams()
immunity_waning = pb.ImmunityWaningParams()

fig, ax = plt.subplots(1, 1)

n_hosts, n_infections, t_since_last_exposure = 20, 3, 60

for _ in range(n_hosts):

    immunity = pb.Immunity()

    for _ in range(n_infections):

        # Boost on new infection
        immunity.update_peak_immunity(theta_nabs)

        # Plot pre- and post-boost Nabs
        ax.scatter(immunity.prechallenge_immunity, immunity.current_immunity)

        # Wane immunity between infections
        immunity.calculate_waning(t_since_last_exposure, immunity_waning)

ax.set_xscale('log', base=2)
ax.set_yscale('log', base=2)
ax.set(xlabel='Pre-challenge immunity', ylabel='Post-challenge immunity')
fig.set_tight_layout(True)

plt.show()