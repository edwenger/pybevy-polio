mod core;
mod polio;

use pyo3::prelude::*;
use bevy::prelude::*;
use bevy::app::AppExit;

use core::{Host, SimulationTime};
use polio::Immunity;

static N_HOSTS: u32 = 5;       // Number of hosts in the simulation
static MAX_DAYS: u32 = 60;     // Maximum simulation days
static INCIDENCE_RATE: f32 = 0.03;  // Per-capita infectious challenge rate per SimulationTime.day
static LOG10_DOSE: f32 = 6.0;       // Log10 of infectious challenge dose

/// This function can be called from Python
#[pyfunction]
fn run_bevy_app() -> PyResult<()> {
    App::new()
        .add_plugins(MinimalPlugins)
        .insert_resource(SimulationTime::default())
        .insert_resource(polio::Params::default())
        .add_systems(Startup, setup)
        .add_systems(Update, (step_loop, exit_system))
        .run();

    Ok(())
}

fn setup(mut commands: Commands) {
    for _ in 0..N_HOSTS {
        commands.spawn((
            Host{birth_sim_day: 0.0},
            Immunity::default(),
        ));
    }
}

fn exit_system(
    sim_time: Res<SimulationTime>,
    mut exit: EventWriter<AppExit>
) {
    if sim_time.day > MAX_DAYS {
        exit.send(AppExit);
    }
}

fn step_loop(
    mut commands: Commands,
    mut host_query: Query<(Entity, &Host, &mut polio::Immunity, Option<&mut polio::Infection>)>,
    mut sim_time: ResMut<SimulationTime>,
    polio_params: Res<polio::Params>,
) {
        let duration = sim_time.timer.duration();
        sim_time.timer.tick(duration);
        sim_time.day += 1;
        println!("...Advancing to day {}", sim_time.day);
        polio::step_state(&mut commands, &mut host_query, &polio_params, &sim_time);

        let prob = 1.0 - (-INCIDENCE_RATE).exp();
        let dose = 10f32.powf(LOG10_DOSE);
        polio::challenge(&mut commands, &mut host_query, &polio_params, &sim_time, prob, dose);
}

/// A Python module implemented in Rust
#[pymodule]
fn pybevy(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_bevy_app, m)?)?;
    Ok(())
}
