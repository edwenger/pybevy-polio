import pybevy as pb
import matplotlib.pyplot as plt

theta_nabs = pb.ThetaNabsParams()
immunity_waning = pb.ImmunityWaningParams()

fig, ax = plt.subplots(1, 1)

n_hosts, n_infections, t_since_last_exposure = 20, 10, 365*2

for _ in range(n_hosts):

    immunity = pb.Immunity()

    for _ in range(n_infections):

        # Boost on new infection
        immunity.update_peak_immunity(theta_nabs)

        # Plot pre- and post-boost Nabs
        ax.scatter(immunity.prechallenge_immunity, immunity.current_immunity)

        # Wane immunity between infections (TODO: refactor as instance method Immunity.calculate_waned_immunity(t_since_exposure, immunity_waning))
        immunity.current_immunity = pb.calculate_immunity_waning(
            immunity.postchallenge_peak_immunity,
            t_since_last_exposure,
            immunity_waning.rate)

ax.set_xscale('log', base=2)
ax.set_yscale('log', base=2)
fig.set_tight_layout(True)

plt.show()