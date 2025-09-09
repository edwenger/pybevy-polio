// Params and related types for polio simulation

use std::collections::HashMap;
use bevy::prelude::Resource;
use super::disease::{InfectionStrain, InfectionSerotype};

#[cfg(feature = "pyo3")]
use pyo3::prelude::*;

#[cfg(not(feature = "pyo3"))]
#[derive(Resource)]
pub struct Params {
    pub immunity_waning: ImmunityWaningParams,
    pub theta_nabs: ThetaNabsParams,
    pub viral_shedding: ViralSheddingParams,
    pub peak_cid50: PeakCid50Params,
    pub p_transmit: ProbTransmitParams,
    pub strain_params: HashMap<(InfectionStrain, InfectionSerotype), StrainParams>,
}

#[cfg(feature = "pyo3")]
#[derive(Resource)]
#[pyclass]
pub struct Params {
    #[pyo3(get, set)]
    pub immunity_waning: ImmunityWaningParams,
    #[pyo3(get, set)]
    pub theta_nabs: ThetaNabsParams,
    #[pyo3(get, set)]
    pub viral_shedding: ViralSheddingParams,
    #[pyo3(get, set)]
    pub peak_cid50: PeakCid50Params,
    #[pyo3(get, set)]
    pub p_transmit: ProbTransmitParams,
    // Note: HashMap is complex for PyO3, so we'll handle strain_params via methods
    pub strain_params: HashMap<(InfectionStrain, InfectionSerotype), StrainParams>,
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl ImmunityWaningParams {
    #[new]
    pub fn new() -> Self {
        ImmunityWaningParams { rate: 0.87 }
    }
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl ThetaNabsParams {
    #[new]
    pub fn new() -> Self {
        ThetaNabsParams { a: 4.82, b: -0.30, c: 3.31, d: -0.32 }
    }
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl ShedDurationParams {
    #[new]
    pub fn new() -> Self {
        ShedDurationParams { u: 43.0, delta: 1.16, sigma: 1.69 }
    }
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl ViralSheddingParams {
    #[new]
    pub fn new() -> Self {
        ViralSheddingParams { eta: 1.65, v: 0.17, epsilon: 0.32 }
    }
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl PeakCid50Params {
    #[new]
    pub fn new() -> Self {
        PeakCid50Params { k: 0.056, smax: 6.7, smin: 4.3, tau: 12.0 }
    }
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl ProbTransmitParams {
    #[new]
    pub fn new() -> Self {
        ProbTransmitParams { alpha: 0.44, gamma: 0.46 }
    }
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl StrainParams {
    #[new]
    pub fn new() -> Self {
        StrainParams { 
            sabin_scale_parameter: 2.3, 
            strain_take_modifier: 1.0, 
            shed_duration: ShedDurationParams { u: 43.0, delta: 1.16, sigma: 1.69 }
        }
    }
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl Params {
    #[new]
    pub fn new() -> Self {
        Params::default()
    }
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

#[cfg(not(feature = "pyo3"))]
pub struct ImmunityWaningParams {
    pub rate: f32,
}

#[cfg(feature = "pyo3")]
#[derive(Clone)]
#[pyclass]
pub struct ImmunityWaningParams {
    #[pyo3(get, set)]
    pub rate: f32,
}

#[cfg(not(feature = "pyo3"))]
pub struct ThetaNabsParams {
    pub a: f32,
    pub b: f32,
    pub c: f32,
    pub d: f32,
}

#[cfg(feature = "pyo3")]
#[derive(Clone)]
#[pyclass]
pub struct ThetaNabsParams {
    #[pyo3(get, set)]
    pub a: f32,
    #[pyo3(get, set)]
    pub b: f32,
    #[pyo3(get, set)]
    pub c: f32,
    #[pyo3(get, set)]
    pub d: f32,
}

#[cfg(not(feature = "pyo3"))]
#[derive(Clone)]
pub struct ShedDurationParams {
    pub u: f32,
    pub delta: f32,
    pub sigma: f32,
}

#[cfg(feature = "pyo3")]
#[derive(Clone)]
#[pyclass]
pub struct ShedDurationParams {
    #[pyo3(get, set)]
    pub u: f32,
    #[pyo3(get, set)]
    pub delta: f32,
    #[pyo3(get, set)]
    pub sigma: f32,
}

#[cfg(not(feature = "pyo3"))]
pub struct ViralSheddingParams {
    pub eta: f32,
    pub v: f32,
    pub epsilon: f32,
}

#[cfg(feature = "pyo3")]
#[derive(Clone)]
#[pyclass]
pub struct ViralSheddingParams {
    #[pyo3(get, set)]
    pub eta: f32,
    #[pyo3(get, set)]
    pub v: f32,
    #[pyo3(get, set)]
    pub epsilon: f32,
}

#[cfg(not(feature = "pyo3"))]
pub struct PeakCid50Params {
    pub k: f32,
    pub smax: f32,
    pub smin: f32,
    pub tau: f32,
}

#[cfg(feature = "pyo3")]
#[derive(Clone)]
#[pyclass]
pub struct PeakCid50Params {
    #[pyo3(get, set)]
    pub k: f32,
    #[pyo3(get, set)]
    pub smax: f32,
    #[pyo3(get, set)]
    pub smin: f32,
    #[pyo3(get, set)]
    pub tau: f32,
}

#[cfg(not(feature = "pyo3"))]
pub struct ProbTransmitParams {
    pub alpha: f32,
    pub gamma: f32,
}

#[cfg(feature = "pyo3")]
#[derive(Clone)]
#[pyclass]
pub struct ProbTransmitParams {
    #[pyo3(get, set)]
    pub alpha: f32,
    #[pyo3(get, set)]
    pub gamma: f32,
}

#[cfg(not(feature = "pyo3"))]
#[derive(Clone)]
pub struct StrainParams {
    pub sabin_scale_parameter: f32,
    pub strain_take_modifier: f32,
    pub shed_duration: ShedDurationParams,
}

#[cfg(feature = "pyo3")]
#[derive(Clone)]
#[pyclass]
pub struct StrainParams {
    #[pyo3(get, set)]
    pub sabin_scale_parameter: f32,
    #[pyo3(get, set)]
    pub strain_take_modifier: f32,
    #[pyo3(get, set)]
    pub shed_duration: ShedDurationParams,
}
