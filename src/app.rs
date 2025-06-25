mod core;
mod polio;

use bevy::prelude::*;
use bevy::window::PrimaryWindow;
use bevy_egui::{egui, EguiContexts, EguiPlugin};
use log::{info, debug};

use core::{SimulationTime, Host};

// Resources
#[derive(Resource)]
struct SimParams {
    incidence_rate: f32, // New infections per SimulationTime.day
    log10_dose: f32, // Log10 of infectious challenge dose
}

impl Default for SimParams {
    fn default() -> Self {
        Self {
            incidence_rate: 0.03,
            log10_dose: 6.0,
        }
    }
}

#[derive(Resource)]
pub struct SimulationSpeed {
    pub multiplier: f32, // 1.0 by default
}

impl Default for SimulationSpeed {
    fn default() -> Self {
        Self { multiplier: 1.0 }
    }
}

// Components
#[derive(Component)]
struct TimeText;

#[derive(Component)]
struct ImmunityScale;

#[derive(Component)]
struct SheddingScale;

// Systems
fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    query: Query<&Window, With<PrimaryWindow>>, // Query for the primary window
    ) {

    let window = query.single(); // Get the primary window

    let bottom_y = -window.height() / 2.0 + 100.0; // Adjusted to position hosts comfortably above the bottom edge

    let host_count = 10;
    let spacing = window.width() / (host_count as f32 + 1.0) / 1.0; // Dynamically calculate spacing based on window width

    for i in 0..host_count {

        let x = (i as f32 + 1.0) * spacing - window.width() / 2.0; // Distribute hosts evenly across the screen

        // Spawn Hosts entities with default Immunity components
        commands.spawn((
            Host{birth_sim_day: 0.0},
            polio::Immunity::default(),
            SpriteBundle {
                    sprite: Sprite {
                        color: Color::GRAY,
                        custom_size: Some(Vec2::new(50.0, 5.0)),
                        ..default()
                    },
                    transform: Transform::from_xyz(x, bottom_y, 0.0),
                    ..default()
                },
        ))
        .with_children(|parent| {
            parent.spawn((
                ImmunityScale,
                SpriteBundle {
                    sprite: Sprite {
                        color: Color::rgba(82./256.,	182./256., 226./256., 0.5),
                        custom_size: Some(Vec2::splat(15.0)),
                        ..default()
                    },
                    transform: Transform::from_xyz(-10.0, 20.0, 0.1),
                    ..default()
                },
            ));
        });
    }

    // Add UI text
    commands.spawn((
        TimeText,
        TextBundle {
            text: Text::from_section(
                "t = 0",
                TextStyle {
                    font: asset_server.load("fonts/FiraSans-Bold.ttf"),
                    font_size: 30.0,
                    color: Color::WHITE,
                },
            ),
            style: Style {
                position_type: PositionType::Absolute,
                top: Val::Px(10.0),
                left: Val::Px(10.0),
                ..default()
            },
            ..default()
        },
    ));

    // Add a default 2D camera
    commands.spawn(Camera2dBundle {
        ..default()
    });

}

fn update_time_text(
    sim_time: Res<SimulationTime>,
    mut text_query: Query<&mut Text, With<TimeText>>,
) {
    let mut text = text_query.single_mut();
    text.sections[0].value = format!("t = {}", sim_time.day);
}

fn simulation_controls_ui(
    mut contexts: EguiContexts, 
    mut params: ResMut<SimParams>, 
    mut speed: ResMut<SimulationSpeed>
) {
    egui::Window::new("Simulation Controls")
        .default_pos(egui::pos2(10.0, 50.0))
        .show(contexts.ctx_mut(), |ui| {
            ui.label("Simulation Speed");

            let mut param_value = speed.multiplier;
            let response = ui.add(egui::Slider::new(&mut param_value, 0.5..=30.0).text("Speed Multiplier"));

            if response.changed() {
                speed.multiplier = param_value;
            }

            ui.label("Incidence Rate");

            let mut param_value = params.incidence_rate;
            let response = ui.add(egui::Slider::new(&mut param_value, 0.0..=0.2).text("Incidence Rate"));

            if response.changed() {
                params.incidence_rate = param_value;
            }

            ui.label("Challenge Dose (Log10)");
            let mut param_value = params.log10_dose;
            let response = ui.add(egui::Slider::new(&mut param_value, 4.0..=8.0).text("Log10 Dose"));
            if response.changed() {
                params.log10_dose = param_value;
            }
        });
}

fn step_loop(
    mut commands: Commands,
    mut host_query: Query<(Entity, &Host, &mut polio::Immunity, Option<&mut polio::Infection>)>,
    mut sim_time: ResMut<SimulationTime>,
    time: Res<Time>,
    speed: Res<SimulationSpeed>,
    polio_params: Res<polio::Params>,
    params: Res<SimParams>,
) {
    sim_time.timer.tick(time.delta().mul_f32(speed.multiplier));

    if sim_time.timer.just_finished() {
        info!("Stepping simulation state from day {}: {} finished this tick", sim_time.day, sim_time.timer.times_finished_this_tick());
        // For large visualization speed multipliers, the timer may have finished multiple times per tick
        for _ in 0..sim_time.timer.times_finished_this_tick() {
            sim_time.day += 1;
            debug!("...Advancing to day {}", sim_time.day);
            polio::step_state(&mut commands, &mut host_query, &polio_params, &sim_time);
            let prob = 1.0 - (-params.incidence_rate).exp();
            let dose = 10f32.powf(params.log10_dose);
            polio::challenge(&mut commands, &mut host_query, &polio_params, &sim_time, prob, dose, "WPV2");
        }
    }
}

fn update_immunity_scales(
    host_query: Query<(&polio::Immunity, &Children), With<Host>>,
    mut scale_query: Query<(&mut Transform, &mut Sprite), With<ImmunityScale>>,
) {
    for (immunity, children) in host_query.iter() {
        for &child in children.iter() {
            if let Ok((mut transform, mut sprite)) = scale_query.get_mut(child) {
                sprite.custom_size = Some(Vec2::new(15.0, immunity.current_immunity.log10() * 50.0));
                transform.translation = Vec3::new(-10.0, 0.5 * immunity.current_immunity.log10() * 50.0 + 5.0, 0.1);
            }
        }
    }
}

fn add_shedding_scales(
    mut commands: Commands,
    host_query: Query<Entity, (With<Host>, Added<polio::Infection>)>,
) {
    for entity in host_query.iter() {
        commands.entity(entity).with_children(|parent| {
            parent.spawn((
                SheddingScale,
                SpriteBundle {
                    sprite: Sprite {
                        color: Color::RED,
                        custom_size: Some(Vec2::splat(15.0)),
                        ..default()
                    },
                    transform: Transform::from_xyz(10.0, 20.0, 0.1),
                    ..default()
                },
            ));
        });
    }
}

fn update_shedding_scales(
    host_query: Query<(&polio::Infection, &Children), With<Host>>,
    mut scale_query: Query<(&mut Transform, &mut Sprite), With<SheddingScale>>,
) {
    for (infection, children) in host_query.iter() {
        for &child in children.iter() {
            if let Ok((mut transform, mut sprite)) = scale_query.get_mut(child) {
                sprite.custom_size = Some(Vec2::new(15.0, infection.viral_shedding.log10() * 20.0));
                transform.translation = Vec3::new(10.0, 0.5 * infection.viral_shedding.log10() * 20.0 + 5.0, 0.1);
            }
        }
    }
}

fn remove_shedding_scales(
    mut commands: Commands,
    mut removals: RemovedComponents<polio::Infection>,
    host_query: Query<(Entity, &Children), With<Host>>,
    mut scale_query: Query<Entity, With<SheddingScale>>,
) {
    for recovered_entity in removals.read() {
        if let Ok((parent_entity, children)) = host_query.get(recovered_entity) {
            for &child in children.iter() {
                if let Ok(child_entity) = scale_query.get_mut(child) {
                    commands.entity(parent_entity).remove_children(&[child_entity]);
                    commands.entity(child_entity).despawn();
                }
            }
        }
    }
}

// App entry point
fn main() {
    env_logger::init();

    App::new()
        .insert_resource(ClearColor(Color::rgb(0.1, 0.1, 0.1)))
        .insert_resource(SimParams::default())
        .insert_resource(SimulationTime::default())
        .insert_resource(SimulationSpeed::default())
        .insert_resource(polio::Params::default())
        .add_plugins(DefaultPlugins)
        .add_plugins(EguiPlugin)
        .add_systems(Startup, setup)
        .add_systems(Update, (
            simulation_controls_ui, update_time_text, 
            add_shedding_scales, remove_shedding_scales,
            update_immunity_scales, update_shedding_scales))
        .add_systems(Update, step_loop)
        .run();
}