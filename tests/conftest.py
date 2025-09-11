"""
Shared fixtures and test utilities for PyBevy-Polio tests.
"""

import pytest
import pybevy


@pytest.fixture
def default_params():
    """Default parameter set for testing."""
    return pybevy.Params()


@pytest.fixture
def immunity_waning_params():
    """Default immunity waning parameters."""
    return pybevy.ImmunityWaningParams()


@pytest.fixture
def theta_nabs_params():
    """Default theta nabs parameters."""
    return pybevy.ThetaNabsParams()


@pytest.fixture
def viral_shedding_params():
    """Default viral shedding parameters."""
    return pybevy.ViralSheddingParams()


@pytest.fixture
def peak_cid50_params():
    """Default peak CID50 parameters."""
    return pybevy.PeakCid50Params()


@pytest.fixture
def prob_transmit_params():
    """Default transmission probability parameters."""
    return pybevy.ProbTransmitParams()


@pytest.fixture
def shed_duration_params():
    """Default shedding duration parameters."""
    return pybevy.ShedDurationParams()


@pytest.fixture
def strain_params(shed_duration_params):
    """Default strain parameters."""
    params = pybevy.StrainParams()
    params.shed_duration = shed_duration_params
    return params


@pytest.fixture
def test_host():
    """Test host with standard age (20 years old)."""
    return pybevy.Host(birth_sim_day=-365*20)


@pytest.fixture
def test_immunity():
    """Test immunity with standard values."""
    return pybevy.Immunity.with_values(
        current_immunity=2.0,
        prechallenge_immunity=8.0,
        postchallenge_peak_immunity=4.0,
        ti_infected=10.0
    )


@pytest.fixture
def test_infection():
    """Test infection with WPV Type2."""
    return pybevy.Infection(
        shed_duration=42.5,
        viral_shedding=1000.0,
        strain=pybevy.InfectionStrain.WPV,
        serotype=pybevy.InfectionSerotype.Type2
    )


@pytest.fixture
def infection_strains():
    """All infection strains for parametrized tests."""
    return [pybevy.InfectionStrain.WPV, pybevy.InfectionStrain.OPV]


@pytest.fixture
def infection_serotypes():
    """All infection serotypes for parametrized tests."""
    return [
        pybevy.InfectionSerotype.Type1,
        pybevy.InfectionSerotype.Type2,
        pybevy.InfectionSerotype.Type3
    ]


@pytest.fixture
def test_doses():
    """Range of test doses for dose-response testing."""
    return [100.0, 1000.0, 10000.0, 100000.0]


@pytest.fixture
def immunity_levels():
    """Range of immunity levels for testing."""
    return [0.5, 2.0, 5.0, 10.0]