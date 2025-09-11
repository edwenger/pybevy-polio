use pyo3::prelude::*;
use pyo3::types::PyDict;
use bevy::prelude::*;
use bevy::app::AppExit;

use numpy::{PyArray3, IntoPyArray};
use pyo3::Python;
use ndarray::Array3;

use model::{Host, SimulationTime, polio};
use std::sync::{Arc, Mutex};
use log::info;

#[derive(Resource)]
#[derive(FromPyObject)]
#[pyo3(from_item_all)]  // Converts all Python dict keys to struct fields
struct SimParams {
    n_hosts: u32,
    max_days: u32,
    incidence_rate: f32,
    log10_dose: f32,
}

#[derive(Resource, Clone)]
struct OutputData {
    arr: Arc<Mutex<Array3<f64>>>,
}   

/// This function can be called from Python
#[pyfunction]
fn run_bevy_app<'py>(py: Python<'py>, data: &Bound<'py, PyDict>) -> PyResult<Bound<'py, PyArray3<f64>>> {

    let sim_params: SimParams = data.extract()?;

    let output_data = OutputData {
        arr: Arc::new(Mutex::new(Array3::zeros((
            sim_params.n_hosts as usize, 
            sim_params.max_days as usize + 1,
            2))))
    };
    let output_data_clone = output_data.clone();

    env_logger::init();

    App::new()
        .add_plugins(MinimalPlugins)
        .insert_resource(sim_params)
        .insert_resource(output_data)
        .insert_resource(SimulationTime::default())
        .insert_resource(polio::Params::default())
        .add_systems(Startup, setup)
        .add_systems(Update, (step_loop, exit_system))
        .run();

    let arr = output_data_clone.arr.lock().unwrap();
    let py_array = arr.to_owned().into_pyarray_bound(py);
    Ok(py_array)
}

fn setup(
    mut commands: Commands,
    params: Res<SimParams>,
) {
    for _ in 0..params.n_hosts {
        commands.spawn((
            Host{birth_sim_day: 0.0},
            polio::Immunity::default(),
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
    ouput_data: ResMut<OutputData>,
) {
    let duration = sim_time.timer.duration();
    sim_time.timer.tick(duration);
    sim_time.day += 1;
    info!("...Advancing to day {}", sim_time.day);
    polio::step_state(&mut commands, &mut host_query, &polio_params, &sim_time);

    let prob = 1.0 - (-params.incidence_rate).exp();
    let dose = 10f32.powf(params.log10_dose);
    polio::challenge(&mut commands, &mut host_query, &polio_params, &sim_time, prob, dose, "WPV2");

    for (entity, _host, immunity, infection) in host_query.iter_mut() {
        if sim_time.day < params.max_days {
            let mut arr = ouput_data.arr.lock().unwrap();
            arr[[entity.index() as usize, sim_time.day as usize, 0]] = immunity.current_immunity as f64;
            arr[[entity.index() as usize, sim_time.day as usize, 1]] = if let Some(inf) = infection {
                inf.viral_shedding as f64
            } else {
                0.0
            };
        }
    }
}

/// A Python module implemented in Rust
#[pymodule]
fn pybevy(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_bevy_app, m)?)?;
    
    // Core classes
    m.add_class::<Host>()?;
    
    // Polio disease classes
    m.add_class::<polio::Immunity>()?;
    m.add_class::<polio::Infection>()?;
    m.add_class::<polio::InfectionStrain>()?;
    m.add_class::<polio::InfectionSerotype>()?;
    
    // Parameter classes
    m.add_class::<polio::Params>()?;
    m.add_class::<polio::ImmunityWaningParams>()?;
    m.add_class::<polio::ThetaNabsParams>()?;
    m.add_class::<polio::ShedDurationParams>()?;
    m.add_class::<polio::ViralSheddingParams>()?;
    m.add_class::<polio::PeakCid50Params>()?;
    m.add_class::<polio::ProbTransmitParams>()?;
    m.add_class::<polio::StrainParams>()?;
    
    Ok(())
}
