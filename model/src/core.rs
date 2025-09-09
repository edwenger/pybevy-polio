use bevy::prelude::*;

#[cfg(feature = "pyo3")]
use pyo3::prelude::*;

#[derive(Resource)]
pub struct SimulationTime {
    pub day: u32,
    pub timer: Timer,
}

impl Default for SimulationTime {
    fn default() -> Self {
        Self {
            day: 0,
            timer: Timer::from_seconds(1.0, TimerMode::Repeating), // One day per second
        }
    }
}

#[cfg(not(feature = "pyo3"))]
#[derive(Component)]
pub struct Host {
    pub birth_sim_day: f32,
}

#[cfg(feature = "pyo3")]
#[derive(Component)]
#[pyclass]
pub struct Host {
    #[pyo3(get, set)]
    pub birth_sim_day: f32,
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl Host {
    #[new]
    pub fn new(birth_sim_day: f32) -> Self {
        Host { birth_sim_day }
    }
}