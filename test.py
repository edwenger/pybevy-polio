import pybevy as pb

sim_params = dict(
    n_hosts=2,
    max_days=20,
    incidence_rate=0.2,
    # log10_dose=8.0,
)

pb.run_bevy_app(sim_params)
