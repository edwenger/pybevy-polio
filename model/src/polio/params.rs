// Params and related types for polio simulation

use std::collections::HashMap;
use bevy::prelude::Resource;
use super::disease::{InfectionStrain, InfectionSerotype};

#[derive(Resource)]
pub struct Params {
    pub immunity_waning: ImmunityWaningParams,
    pub theta_nabs: ThetaNabsParams,
    pub viral_shedding: ViralSheddingParams,
    pub peak_cid50: PeakCid50Params,
    pub p_transmit: ProbTransmitParams,
    pub strain_params: HashMap<(InfectionStrain, InfectionSerotype), StrainParams>,
}

impl Default for Params {
    fn default() -> Self {
        use InfectionStrain::*;
        use InfectionSerotype::*;
        let mut strain_params = HashMap::new();
        let wpv_duration = ShedDurationParams { u: 43.0, delta: 1.16, sigma: 1.69 };
        let opv_duration = ShedDurationParams { u: 30.3, delta: 1.16, sigma: 1.86 };
        let wpv_sabin_scale = 2.3;
        let wpv_take_mod = 1.0;
        for sero in [Type1, Type2, Type3] {
            strain_params.insert((WPV, sero), StrainParams {
                sabin_scale_parameter: wpv_sabin_scale,
                strain_take_modifier: wpv_take_mod,
                shed_duration: wpv_duration.clone(),
            });
        }
        strain_params.insert((OPV, Type1), StrainParams { sabin_scale_parameter: 14.0, strain_take_modifier: 0.79, shed_duration: opv_duration.clone() });
        strain_params.insert((OPV, Type2), StrainParams { sabin_scale_parameter: 8.0, strain_take_modifier: 0.92, shed_duration: opv_duration.clone() });
        strain_params.insert((OPV, Type3), StrainParams { sabin_scale_parameter: 18.0, strain_take_modifier: 0.81, shed_duration: opv_duration });
        Self {
            immunity_waning: ImmunityWaningParams { rate: 0.87 },
            theta_nabs: ThetaNabsParams { a: 4.82, b: -0.30, c: 3.31, d: -0.32 },
            viral_shedding: ViralSheddingParams { eta: 1.65, v: 0.17, epsilon: 0.32 },
            peak_cid50: PeakCid50Params { k: 0.056, smax: 6.7, smin: 4.3, tau: 12.0 },
            p_transmit: ProbTransmitParams { alpha: 0.44, gamma: 0.46 },
            strain_params,
        }
    }
}

impl Params {
    pub fn sabin_scale_for(&self, strain: InfectionStrain, serotype: InfectionSerotype) -> Option<f32> {
        self.strain_params.get(&(strain, serotype)).map(|p| p.sabin_scale_parameter)
    }
    pub fn take_modifier_for(&self, strain: InfectionStrain, serotype: InfectionSerotype) -> Option<f32> {
        self.strain_params.get(&(strain, serotype)).map(|p| p.strain_take_modifier)
    }
    pub fn shed_duration_for(&self, strain: InfectionStrain, serotype: InfectionSerotype) -> Option<&ShedDurationParams> {
        self.strain_params.get(&(strain, serotype)).map(|p| &p.shed_duration)
    }
}

pub struct ImmunityWaningParams {
    pub rate: f32,
}

pub struct ThetaNabsParams {
    pub a: f32,
    pub b: f32,
    pub c: f32,
    pub d: f32,
}

#[derive(Clone)]
pub struct ShedDurationParams {
    pub u: f32,
    pub delta: f32,
    pub sigma: f32,
}

pub struct ViralSheddingParams {
    pub eta: f32,
    pub v: f32,
    pub epsilon: f32,
}

pub struct PeakCid50Params {
    pub k: f32,
    pub smax: f32,
    pub smin: f32,
    pub tau: f32,
}

pub struct ProbTransmitParams {
    pub alpha: f32,
    pub gamma: f32,
}

#[derive(Clone)]
pub struct StrainParams {
    pub sabin_scale_parameter: f32,
    pub strain_take_modifier: f32,
    pub shed_duration: ShedDurationParams,
}
