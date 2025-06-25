// Disease-related enums, components, and systems for polio simulation

use bevy::prelude::*;
use rand_distr::{LogNormal, Normal, Distribution};
use log::{info, debug, error};
use crate::core::{SimulationTime, Host};
use super::params::*;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum InfectionStrain {
    WPV,
    OPV,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum InfectionSerotype {
    Type1,
    Type2,
    Type3,
}

impl InfectionSerotype {
    pub fn from_num(n: u8) -> Option<Self> {
        match n {
            1 => Some(InfectionSerotype::Type1),
            2 => Some(InfectionSerotype::Type2),
            3 => Some(InfectionSerotype::Type3),
            _ => None,
        }
    }
}

pub fn parse_infection_type(s: &str) -> Option<(InfectionStrain, InfectionSerotype)> {
    let s = s.to_ascii_uppercase();
    if s.starts_with("WPV") {
        let sero = s[3..].parse::<u8>().ok()?;
        Some((InfectionStrain::WPV, InfectionSerotype::from_num(sero)?))
    } else if s.starts_with("OPV") {
        let sero = s[3..].parse::<u8>().ok()?;
        Some((InfectionStrain::OPV, InfectionSerotype::from_num(sero)?))
    } else {
        None
    }
}

#[derive(Component)]
pub struct Immunity {
    prechallenge_immunity: f32,
    postchallenge_peak_immunity: f32,
    pub current_immunity: f32,
    ti_infected: Option<f32>,
}

impl Default for Immunity {
    fn default() -> Self {
        Self {
            prechallenge_immunity: 1.0,
            postchallenge_peak_immunity: 0.0,
            current_immunity: 1.0,
            ti_infected: None,
        }
    }
}

impl Immunity {
    pub fn update_peak_immunity(&mut self, theta_nabs: &ThetaNabsParams) {
        self.prechallenge_immunity = self.current_immunity;
        let nabs = self.prechallenge_immunity;
        let mean = theta_nabs.a + theta_nabs.b * nabs.log2();
        let stdev = (theta_nabs.c + theta_nabs.d * nabs.log2()).max(0.0).sqrt();
        let normal_dist = Normal::new(mean, stdev).unwrap();
        let theta_nabs = normal_dist.sample(&mut rand::rng()).exp();
        self.postchallenge_peak_immunity = self.prechallenge_immunity * theta_nabs.max(1.0);
        self.current_immunity = self.postchallenge_peak_immunity.max(1.0);
        info!("  Updated current immunity: {}", self.current_immunity);
    }
}

#[derive(Component)]
pub struct Infection {
    shed_duration: f32,
    pub viral_shedding: f32,
    pub strain: InfectionStrain,
    pub serotype: InfectionSerotype,
}

impl Infection {
    pub fn set_prognoses(immunity: &mut Immunity, sim_time: &SimulationTime, params: &Params, strain: InfectionStrain, serotype: InfectionSerotype) -> Infection {
        immunity.update_peak_immunity(&params.theta_nabs);
        immunity.ti_infected = Some(sim_time.day as f32);
        let shed_params = params.shed_duration_for(strain, serotype);
        let shed_duration = if let Some(shed_params) = shed_params {
            update_shed_duration(&immunity, shed_params)
        } else {
            error!("Missing strain parameters for {:?} {:?}", strain, serotype);
            30.0
        };
        Infection {
            shed_duration,
            viral_shedding: 0.0,
            strain,
            serotype,
        }
    }
}

fn update_shed_duration(immunity: &Immunity, shed_duration_params: &ShedDurationParams) -> f32 {
    let u = shed_duration_params.u;
    let delta = shed_duration_params.delta;
    let sigma = shed_duration_params.sigma;
    let mu = u.ln() - delta.ln() * immunity.prechallenge_immunity.log2();
    let std = sigma.ln();
    let log_normal_dist = LogNormal::new(mu, std).unwrap();
    let shed_duration = log_normal_dist.sample(&mut rand::rng());
    info!("  Updated shed duration: {}", shed_duration);
    shed_duration
}

pub fn step_state(
    commands: &mut Commands,
    query: &mut Query<(Entity, &Host, &mut Immunity, Option<&mut Infection>)>,
    params: &Params,
    sim_time: &SimulationTime,
) {
    for (entity, host, mut immunity, infection) in query.iter_mut() {
        if let Some(ti_infected) = immunity.ti_infected {
            let t_since_last_exposure = sim_time.day as f32 - ti_infected;
            if t_since_last_exposure >= 30.0 {
                immunity.current_immunity = (immunity.postchallenge_peak_immunity * ((t_since_last_exposure / 30.0).powf(-params.immunity_waning.rate))).max(1.0);
            }
            if let Some(mut inf) = infection {
                if t_since_last_exposure > inf.shed_duration {
                    info!("Clearing infection for host {:?} at day {}", entity, sim_time.day);
                    commands.entity(entity).remove::<Infection>();
                } else {
                    let age_in_months = (sim_time.day as f32 - host.birth_sim_day) * 12.0 / 365.0;
                    let log10_peak_cid50 = update_log10_peak_cid50(&immunity, age_in_months, &params.peak_cid50);
                    let log_t_inf = t_since_last_exposure.ln();
                    let eta = params.viral_shedding.eta;
                    let v = params.viral_shedding.v;
                    let epsilon = params.viral_shedding.epsilon;
                    let exponent = eta - (0.5 * v.powi(2)) - ((log_t_inf - eta).powi(2)) / (2.0 * (v + epsilon * log_t_inf).powi(2));
                    let predicted_concentration = 10f32.powf(log10_peak_cid50) * exponent.exp() / t_since_last_exposure;
                    inf.viral_shedding = predicted_concentration.max(10f32.powf(2.6));
                    debug!("  Updating {:?} {:?} viral shedding for host {:?}: {}", inf.strain, inf.serotype, entity, inf.viral_shedding);
                }
            }
        }
    }
}

fn update_log10_peak_cid50(immunity: &Immunity, age_in_months: f32, peak_cid50_params: &PeakCid50Params) -> f32 {
    let k = peak_cid50_params.k;
    let smax = peak_cid50_params.smax;
    let smin = peak_cid50_params.smin;
    let tau = peak_cid50_params.tau;
    let peak_cid50_naive = if age_in_months >= 6.0 {
        (smax - smin) * ((7.0 - age_in_months) / tau).exp() + smin
    } else {
        smax
    };
    peak_cid50_naive * (1.0 - k * (immunity.prechallenge_immunity).log2())
}

pub fn challenge(
    commands: &mut Commands,
    query: &mut Query<(Entity, &Host, &mut Immunity, Option<&mut Infection>)>,
    params: &Params,
    sim_time: &SimulationTime,
    prob: f32,
    dose: f32,
    strain: &str,
) {
    if let Some((strain, serotype)) = parse_infection_type(strain) {
        for (entity, _host, mut immunity, infection) in query.iter_mut() {
            if infection.is_none() && rand::random::<f32>() < prob {
                info!("Challenging host {:?} at day {} with dose {} ({:?}{:?})", entity, sim_time.day, dose, strain, serotype);
                let alpha = params.p_transmit.alpha;
                let gamma = params.p_transmit.gamma;
                if let (Some(sabin_scale), Some(take_modifier)) = (params.sabin_scale_for(strain, serotype), params.take_modifier_for(strain, serotype)) {
                    let p_transmit = (1.0 - (1.0 + dose / sabin_scale).powf(-alpha * immunity.current_immunity.powf(-gamma))) * take_modifier;
                    if rand::random::<f32>() < p_transmit {
                        info!("Spawning infection for host {:?} at day {}", entity, sim_time.day);
                        commands.entity(entity).insert(Infection::set_prognoses(&mut immunity, sim_time, params, strain, serotype));
                    }
                } else {
                    error!("Missing strain parameters for {:?} {:?}", strain, serotype);
                }
            }
        }
    } else {
        error!("Unknown strain type: {}", strain);
    }
}
