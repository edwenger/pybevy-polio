use bevy::prelude::*;

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

#[derive(Component)]
pub struct Host {
    pub birth_sim_day: f32,
}