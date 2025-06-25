#![allow(non_snake_case)]  // Keeping some subscript-style variable names for clarity (Nabs, Smax, etc.)

use bevy::prelude::*;
use rand_distr::{LogNormal, Normal, Distribution};
use log::{info, debug};

use crate::core::{SimulationTime, Host};

/*
sabin_scale_parameters = dict(WPV=2.3, OPV1=14, OPV2=8, OPV3=18)

strain_take_modifiers= dict(WPV=1.0, OPV1=0.79, OPV2=0.92, OPV3=0.81)  # Based on estimate from Famulare 2018

shed_duration_params = dict(OPV=ss.Pars(u=30.3, delta=1.16, sigma=1.86),
                            WPV=ss.Pars(u=43.0, delta=1.16,sigma=1.69))
*/

#[derive(Resource)]
pub struct Params {
    immunity_waning: ImmunityWaningParams,
    theta_Nabs: ThetaNabsParams,
    shed_duration: ShedDurationParams,
    viral_shedding: ViralSheddingParams,
    peak_cid50: PeakCid50Params,
    p_transmit: ProbTransmitParams,
    strain_take_modifier: f32,
    sabin_scale_parameter: f32,
}
impl Default for Params {
    fn default() -> Self {
        Self {
            immunity_waning: ImmunityWaningParams {
                rate: 0.87,  // Rate per month
            },
            theta_Nabs: ThetaNabsParams {
                a: 4.82, b: -0.30, c: 3.31, d: -0.32,
            },
            shed_duration: ShedDurationParams {
                u: 43.0, delta: 1.16, sigma: 1.69, // Default for WPV
            },
            viral_shedding: ViralSheddingParams {
                eta: 1.65, v: 0.17, epsilon: 0.32,
            },
            peak_cid50: PeakCid50Params {
                k: 0.056, Smax: 6.7, Smin: 4.3, tau: 12.0,
            },
            p_transmit: ProbTransmitParams {
                alpha: 0.44, gamma: 0.46,
            },
            strain_take_modifier: 1.0,  // Default for WPV
            sabin_scale_parameter: 2.3,  // Default for WPV
        }
    }  
}

// immunity_waning = ss.Pars(rate=0.87),
pub struct ImmunityWaningParams {
    rate: f32,
}

// theta_Nabs = ss.Pars(a=4.82, b=-0.30, c=3.31, d=-0.32),
pub struct ThetaNabsParams {
    a: f32,
    b: f32,
    c: f32,
    d: f32,
}

// shed_duration_params['WPV'] = ss.Pars(u=43.0, delta=1.16, sigma=1.69)
pub struct ShedDurationParams {
    u: f32,
    delta: f32,
    sigma: f32,    
}

// viral_shedding = ss.Pars(eta=1.65, v=0.17, epsilon=0.32),
pub struct ViralSheddingParams {
    eta: f32,
    v: f32,
    epsilon: f32,
}

// peak_cid50 = ss.Pars(k=0.056, Smax=6.7, Smin=4.3, tau=12),
pub struct PeakCid50Params {
    k: f32,
    Smax: f32,
    Smin: f32,
    tau: f32,
}

// p_transmit = ss.Pars(alpha=0.44, gamma=0.46),
pub struct ProbTransmitParams {
    alpha: f32,
    gamma: f32,
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
    pub fn update_peak_immunity(&mut self, theta_Nabs: &ThetaNabsParams) {

        self.prechallenge_immunity = self.current_immunity;

        let Nabs = self.prechallenge_immunity;
        let mean = theta_Nabs.a + theta_Nabs.b * Nabs.log2();
        let stdev = (theta_Nabs.c + theta_Nabs.d * Nabs.log2()).max(0.0).sqrt();
        let normal_dist = Normal::new(mean, stdev).unwrap();        
        let theta_Nabs = normal_dist.sample(&mut rand::rng()).exp();
        self.postchallenge_peak_immunity = self.prechallenge_immunity * theta_Nabs.max(1.0);  // prevent immunity from decreasing due to challenge

        self.current_immunity = self.postchallenge_peak_immunity.max(1.0);
        info!("  Updated current immunity: {}", self.current_immunity);
    }
}

#[derive(Component)]
pub struct Infection {
    shed_duration: f32,
    pub viral_shedding: f32,
}

impl Infection {
    pub fn set_prognoses(immunity: &mut Immunity, sim_time: &SimulationTime, params: &Params) -> Infection {

        immunity.update_peak_immunity(&params.theta_Nabs);
        immunity.ti_infected = Some(sim_time.day as f32);

        Infection {
            shed_duration: update_shed_duration(&immunity, &params.shed_duration),
            viral_shedding: 0.0,
        }
    }
}

fn update_shed_duration(immunity: &Immunity, shed_duration_params: &ShedDurationParams) -> f32 {

    let u = shed_duration_params.u;
    let delta = shed_duration_params.delta;
    let sigma = shed_duration_params.sigma;

    let mu = u.ln() - delta.ln() * immunity.prechallenge_immunity.log2();
    let std = sigma.ln();

    let log_normal_dist = LogNormal::new(mu, std).unwrap();  // rand_distr::LogNormal expects the mean and standard deviation in log space
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

            // Wane current immunity if more than 30 days since last exposure
            if t_since_last_exposure >= 30.0 {
                immunity.current_immunity = (immunity.postchallenge_peak_immunity * ((t_since_last_exposure / 30.0).powf(-params.immunity_waning.rate))).max(1.0);
            }

            if let Some(mut inf) = infection {

                // Clear infections if they are past their shedding duration
                if t_since_last_exposure > inf.shed_duration {
                    info!("Clearing infection for host {:?} at day {}", entity, sim_time.day);
                    commands.entity(entity).remove::<Infection>();
                } else {
                    // Update viral shedding if still infected

                    let age_in_months = (sim_time.day as f32 - host.birth_sim_day) * 12.0 / 365.0;
                    let log10_peak_cid50 = update_log10_peak_cid50(&immunity, age_in_months, &params.peak_cid50);

                    let log_t_inf = t_since_last_exposure.ln();
                    let eta = params.viral_shedding.eta;
                    let v = params.viral_shedding.v;
                    let epsilon = params.viral_shedding.epsilon;
                    let exponent = eta - (0.5 * v.powi(2)) - ((log_t_inf - eta).powi(2)) / (2.0 * (v + epsilon * log_t_inf).powi(2));
                    let predicted_concentration = 10f32.powf(log10_peak_cid50) * exponent.exp() / t_since_last_exposure;
                    inf.viral_shedding = predicted_concentration.max(10f32.powf(2.6));  // Set floor on viral shed to be at least 398

                    debug!("  Updating viral shedding for host {:?}: {}", entity, inf.viral_shedding);
                }
            }
        }
    }    
}

fn update_log10_peak_cid50(immunity: &Immunity, age_in_months: f32, peak_cid50_params: &PeakCid50Params) -> f32 {

    let k = peak_cid50_params.k;
    let Smax = peak_cid50_params.Smax;
    let Smin = peak_cid50_params.Smin;
    let tau = peak_cid50_params.tau;

    let peak_cid50_naive = if age_in_months >= 6.0 {
        (Smax - Smin) * ((7.0 - age_in_months) / tau).exp() + Smin
    } else {
        Smax
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
) {
    // N.B. IteratorRandom::choose_multiple might be fore efficient if looking to challenge a fixed number
    for (entity, _host, mut immunity, infection) in query.iter_mut() {
        if infection.is_none() && rand::random::<f32>() < prob {

            // If the host is not already infected, challenge them with a new infection
            info!("Challenging host {:?} at day {} with dose {}", entity, sim_time.day, dose);

            let alpha = params.p_transmit.alpha;
            let gamma = params.p_transmit.gamma;

            // Probability of acquiring transmitted infection based on current immunity and challenge dose
            let p_transmit = (1.0 - (1.0 + dose / params.sabin_scale_parameter).powf(-alpha * immunity.current_immunity.powf(-gamma))) * params.strain_take_modifier;

            if rand::random::<f32>() < p_transmit {
                // Insert an Infection component initialized according to SimulationTime and host Immunity
                info!("Spawning infection for host {:?} at day {}", entity, sim_time.day);
                commands.entity(entity).insert(Infection::set_prognoses(&mut immunity, sim_time, params));
            }
        }
    }
}