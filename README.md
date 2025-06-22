A demonstration project to experiment with a few different concepts:
- porting polio within-host logic into Rust for use with [Bevy](https://bevy.org/) gaming engine (related to previous Python code implementations in [StarSim](https://github.com/edwenger/starsim-bokeh-demo/blob/main/polio.py), [poliosim](https://github.com/amath-idm/poliosim), and [multiscale](https://github.com/InstituteforDiseaseModeling/MultiscaleModeling/blob/main/PopSim/Assets/Infection.py) models)
- experimenting with interactive visualizations for debugging and building intuition about model logic behavior (related to similar effort on [malaria coinfection](https://github.com/edwenger/bevy_coinfection_demo/tree/main))
- exporting Rust functions and modules to Python package with [PyO3](https://pyo3.rs/) and [maturin](https://www.maturin.rs/tutorial.html) (for further integration in tutorial notebooks, calibration workflows, etc.)

To launch the interactive demo yourself, run the following from the commandline:
> cargo run

You'll have to have `rustup` installed already.  Instructions [here](https://www.rust-lang.org/learn/get-started).

To build the exported Python package, run maturin from within a new venv as per [their tutorial](https://www.maturin.rs/tutorial.html#install-and-configure-maturin-in-a-virtual-environment):
> python -m venv .venv
> source .venv/bin/activate
> maturin develop --release

To test if the exported `pybevy` python library is accessible, you can run:
> python test.py