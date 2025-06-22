mod core;
mod polio;

use pyo3::prelude::*;
use pyo3::types::PyDict;
use bevy::prelude::*;
use bevy::app::AppExit;

use core::{Host, SimulationTime};
use polio::Immunity;

#[derive(Resource)]
#[derive(FromPyObject)]
struct SimParams {
    n_hosts: u32,
    max_days: u32,
    incidence_rate: f32,
    log10_dose: f32,
}
impl Default for SimParams {
    fn default() -> Self {
        Self {
            n_hosts: 5,
            max_days: 5,
            incidence_rate: 0.03,
            log10_dose: 6.0,
        }
    }
}

/// This function can be called from Python
#[pyfunction]
fn run_bevy_app<'py>(data: &Bound<'py, PyDict>) -> PyResult<()> {

    let mut rust_params_struct = SimParams::default();

    for (key, value) in data.iter() {
        println!("{}: {} ", key.to_string(), value.to_string());
        match key.to_string().as_str() {
            "n_hosts" => rust_params_struct.n_hosts = value.extract::<u32>()?,
            "max_days" => rust_params_struct.max_days = value.extract::<u32>()?,
            "incidence_rate" => rust_params_struct.incidence_rate = value.extract::<f32>()?,
            "log10_dose" => rust_params_struct.log10_dose = value.extract::<f32>()?,
            _ => println!("Warning: Unknown parameter {}", key.to_string()),
        }
    }

    App::new()
        .add_plugins(MinimalPlugins)
        .insert_resource(rust_params_struct)
        .insert_resource(SimulationTime::default())
        .insert_resource(polio::Params::default())
        .add_systems(Startup, setup)
        .add_systems(Update, (step_loop, exit_system))
        .run();

    Ok(())
}

fn setup(
    mut commands: Commands,
    params: Res<SimParams>,
) {
    for _ in 0..params.n_hosts {
        commands.spawn((
            Host{birth_sim_day: 0.0},
            Immunity::default(),
        ));
    }
}

fn exit_system(
    sim_time: Res<SimulationTime>,
    params: Res<SimParams>,
    mut exit: EventWriter<AppExit>
) {
    if sim_time.day > params.max_days {
        exit.send(AppExit);
    }
}

fn step_loop(
    mut commands: Commands,
    mut host_query: Query<(Entity, &Host, &mut polio::Immunity, Option<&mut polio::Infection>)>,
    mut sim_time: ResMut<SimulationTime>,
    polio_params: Res<polio::Params>,
    params: Res<SimParams>,
) {
        let duration = sim_time.timer.duration();
        sim_time.timer.tick(duration);
        sim_time.day += 1;
        println!("...Advancing to day {}", sim_time.day);
        polio::step_state(&mut commands, &mut host_query, &polio_params, &sim_time);

        let prob = 1.0 - (-params.incidence_rate).exp();
        let dose = 10f32.powf(params.log10_dose);
        polio::challenge(&mut commands, &mut host_query, &polio_params, &sim_time, prob, dose);
}

/// A Python module implemented in Rust
#[pymodule]
fn pybevy(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_bevy_app, m)?)?;
    Ok(())
}
