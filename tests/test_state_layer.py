"""
Tests for State Layer - Individual component management (Host, Immunity, Infection).
"""

import pytest
import pybevy


class TestHost:
    """Test Host component class."""
    
    def test_default_construction(self):
        """Test Host can be constructed with birth day."""
        host = pybevy.Host(birth_sim_day=-365*20)
        assert host.birth_sim_day == -365*20
    
    def test_birth_sim_day_modification(self, test_host):
        """Test birth_sim_day can be modified."""
        original_birth = test_host.birth_sim_day
        test_host.birth_sim_day = -365*5
        assert test_host.birth_sim_day == -365*5
        assert test_host.birth_sim_day != original_birth
    
    @pytest.mark.parametrize("age_years", [0, 5, 20, 50, 80])
    def test_different_ages(self, age_years):
        """Test hosts can be created with different ages."""
        birth_day = -365 * age_years
        host = pybevy.Host(birth_sim_day=birth_day)
        assert host.birth_sim_day == birth_day


class TestImmunity:
    """Test Immunity component class."""
    
    def test_default_construction(self):
        """Test default Immunity construction."""
        immunity = pybevy.Immunity()
        assert isinstance(immunity.current_immunity, float)
        assert isinstance(immunity.prechallenge_immunity, float)
        assert isinstance(immunity.postchallenge_peak_immunity, float)
        # ti_infected should be None initially
        assert immunity.ti_infected is None or isinstance(immunity.ti_infected, float)
    
    def test_with_values_construction(self):
        """Test Immunity construction with specific values."""
        immunity = pybevy.Immunity.with_values(2.0, 5.0, 4.0, 7.5)
        # Check actual parameter mapping based on the constructor implementation
        assert immunity.prechallenge_immunity == pytest.approx(2.0)  # 1st param
        assert immunity.postchallenge_peak_immunity == pytest.approx(5.0)  # 2nd param
        assert immunity.current_immunity == pytest.approx(4.0)  # 3rd param
        assert immunity.ti_infected == pytest.approx(7.5)  # 4th param
    
    def test_property_modification(self, test_immunity):
        """Test immunity properties can be modified."""
        test_immunity.current_immunity = 8.5
        test_immunity.prechallenge_immunity = 3.2
        test_immunity.postchallenge_peak_immunity = 12.1
        test_immunity.ti_infected = 15.0
        
        assert test_immunity.current_immunity == pytest.approx(8.5)
        assert test_immunity.prechallenge_immunity == pytest.approx(3.2)
        assert test_immunity.postchallenge_peak_immunity == pytest.approx(12.1)
        assert test_immunity.ti_infected == pytest.approx(15.0)
    
    @pytest.mark.parametrize("immunity_level", [0.1, 1.0, 5.0, 15.0])
    def test_immunity_levels(self, immunity_level):
        """Test different immunity levels."""
        immunity = pybevy.Immunity.with_values(
            current_immunity=immunity_level,
            prechallenge_immunity=immunity_level,
            postchallenge_peak_immunity=0.0,
            ti_infected=None
        )
        assert immunity.current_immunity == pytest.approx(immunity_level)
        assert immunity.prechallenge_immunity == pytest.approx(immunity_level)


class TestInfection:
    """Test Infection component class."""
    
    def test_construction(self):
        """Test Infection construction with all parameters."""
        infection = pybevy.Infection(
            shed_duration=42.5,
            viral_shedding=1000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type2
        )
        
        assert infection.shed_duration == 42.5
        assert infection.viral_shedding == 1000.0
        assert infection.strain == pybevy.InfectionStrain.WPV
        assert infection.serotype == pybevy.InfectionSerotype.Type2
    
    def test_property_modification(self, test_infection):
        """Test infection properties can be modified."""
        test_infection.shed_duration = 30.0
        test_infection.viral_shedding = 500.0
        test_infection.strain = pybevy.InfectionStrain.OPV
        test_infection.serotype = pybevy.InfectionSerotype.Type3
        
        assert test_infection.shed_duration == 30.0
        assert test_infection.viral_shedding == 500.0
        assert test_infection.strain == pybevy.InfectionStrain.OPV
        assert test_infection.serotype == pybevy.InfectionSerotype.Type3
    
    @pytest.mark.parametrize("strain", [pybevy.InfectionStrain.WPV, pybevy.InfectionStrain.OPV])
    def test_infection_strains(self, strain):
        """Test different infection strains."""
        infection = pybevy.Infection(
            shed_duration=40.0,
            viral_shedding=1000.0,
            strain=strain,
            serotype=pybevy.InfectionSerotype.Type1
        )
        assert infection.strain == strain
    
    @pytest.mark.parametrize("serotype", [
        pybevy.InfectionSerotype.Type1,
        pybevy.InfectionSerotype.Type2,
        pybevy.InfectionSerotype.Type3
    ])
    def test_infection_serotypes(self, serotype):
        """Test different infection serotypes."""
        infection = pybevy.Infection(
            shed_duration=40.0,
            viral_shedding=1000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=serotype
        )
        assert infection.serotype == serotype


class TestInfectionEnums:
    """Test InfectionStrain and InfectionSerotype enums."""
    
    def test_infection_strain_values(self):
        """Test infection strain enum values."""
        wpv = pybevy.InfectionStrain.WPV
        opv = pybevy.InfectionStrain.OPV
        
        assert wpv != opv
        assert isinstance(str(wpv), str)
        assert isinstance(str(opv), str)
    
    def test_infection_serotype_values(self):
        """Test infection serotype enum values."""
        type1 = pybevy.InfectionSerotype.Type1
        type2 = pybevy.InfectionSerotype.Type2
        type3 = pybevy.InfectionSerotype.Type3
        
        assert type1 != type2 != type3
        assert isinstance(str(type1), str)
        assert isinstance(str(type2), str)
        assert isinstance(str(type3), str)
    
    def test_enum_combinations(self, infection_strains, infection_serotypes):
        """Test all combinations of strains and serotypes work."""
        for strain in infection_strains:
            for serotype in infection_serotypes:
                infection = pybevy.Infection(
                    shed_duration=40.0,
                    viral_shedding=1000.0,
                    strain=strain,
                    serotype=serotype
                )
                assert infection.strain == strain
                assert infection.serotype == serotype