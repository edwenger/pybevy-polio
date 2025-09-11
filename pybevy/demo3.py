"""Demo script for building up from low-level Python API to simulate full populations of disease and immunity dynamics"""

import itertools
import logging

import matplotlib.pyplot as plt
import numpy as np
import pybevy as pb

from demo import make_plots_from_data


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class Entity(object):
    """
    This class is the low-level Python API analog of the related Query<Host, Immunity, Option<Infection>> logic from the pure Rust Bevy ECS code.
    It is used here to demonstrate the disease and immunity dynamics in a simple simulation loop.
    """

    uid = itertools.count()  # unique index generator

    def __init__(self, ix=None, birth_sim_day=0):
        self.id = self.ix = ix if ix is not None else next(Entity.uid)
        self.host = pb.Host(birth_sim_day=birth_sim_day)
        self.immunity = pb.Immunity()
        self.infection = None

    def step_state(self, sim_day, polio_params):
        if self.immunity.ti_infected is not None:

            t_since_last_exposure = sim_day - self.immunity.ti_infected
            self.immunity.calculate_waning(t_since_last_exposure, polio_params.immunity_waning)

            if self.infection is not None:
                inf = self.infection
                
                if inf.should_clear_infection(t_since_last_exposure):
                    logger.info("Clearing infection for host %s at day %s", self.ix, sim_day)
                    self.infection = None
                else:
                    age_in_months = (sim_day - self.host.birth_sim_day) * 12.0 / 365.0
                    inf.viral_shedding = self.immunity.calculate_viral_shedding(age_in_months, t_since_last_exposure, polio_params)
                    logger.debug("  Updating (%s, %s) viral shedding for host %s: %s", inf.strain, inf.serotype, self.ix, inf.viral_shedding)

    def challenge(self, sim_day, polio_params, prob, dose, strain, serotype):
        if self.infection is None and np.random.random() < prob:
            logger.info("Challenging host %s at day %s with dose %s (%s, %s)", self.ix, sim_day, dose, strain, serotype)
                
            p_transmit = self.immunity.calculate_infection_probability(
                dose,
                strain,
                serotype,
                polio_params,
            )

            if np.random.random() < p_transmit:
                logger.info("Spawning infection for host %s at day %s", self.ix, sim_day)
                new_inf = pb.Infection(0.0, 0.0, strain, serotype)
                new_inf.set_prognoses(self.immunity, sim_day, polio_params)
                self.infection = new_inf


if __name__ == "__main__":

    # resources
    sim_params = dict(
        n_hosts=5,
        max_days=3*365,
        incidence_rate=0.02,
        log10_dose=6.0,
    )

    polio_params = pb.Params()
    sim_day = 0
    data_3d = np.zeros((sim_params['n_hosts'], sim_params['max_days'], 2))  # n_agents, n_days, n_channels

    # setup
    entities = [Entity() for _ in range(sim_params['n_hosts'])]

    # step_loop
    while sim_day < sim_params['max_days']:

        sim_day += 1
        logger.debug("...Advancing to day %s", sim_day)

        prob = 1.0 - np.exp(-sim_params['incidence_rate'])
        dose = 10 ** sim_params['log10_dose']
        strain, serotype = pb.parse_infection_type("WPV2")

        for entity in entities:

            # TODO: we could also make the Host a day older here
            #       although we don't have a separate demographics update system in the corresponding Rust code yet

            entity.step_state(sim_day, polio_params)

            entity.challenge(sim_day, polio_params, prob, dose, strain, serotype)

            data_3d[entity.ix, sim_day-1, 0] = entity.immunity.current_immunity
            data_3d[entity.ix, sim_day-1, 1] = entity.infection.viral_shedding if entity.infection is not None else 0.0

    make_plots_from_data(data_3d, sim_params)
    plt.show()