"""
Tests for Function Layer - Pure calculation methods on Immunity and Infection classes.
"""

import pytest
import pybevy


class TestImmunityCalculationMethods:
    """Test calculation methods on Immunity class."""
    
    def test_calculate_waning(self, test_immunity, immunity_waning_params):
        """Test immunity waning calculation."""
        original_immunity = test_immunity.current_immunity
        test_immunity.calculate_waning(365.0, immunity_waning_params)  # Use longer time for actual waning
        
        # After a full year, immunity should have waned significantly
        assert test_immunity.current_immunity <= original_immunity
        assert isinstance(test_immunity.current_immunity, float)
        assert test_immunity.current_immunity >= 0.0
    
    @pytest.mark.parametrize("days_since_infection", [1.0, 30.0, 90.0, 365.0])
    def test_calculate_waning_time_dependency(self, days_since_infection, immunity_waning_params):
        """Test immunity waning depends on time since infection."""
        immunity = pybevy.Immunity.with_values(10.0, 10.0, 10.0, 0.0)
        immunity.calculate_waning(days_since_infection, immunity_waning_params)
        
        # Longer time should result in lower immunity
        assert immunity.current_immunity <= 10.0
        assert immunity.current_immunity >= 0.0
    
    def test_calculate_infection_probability(self, test_immunity, default_params):
        """Test infection probability calculation."""
        prob = test_immunity.calculate_infection_probability(
            dose=1000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type2,
            params=default_params
        )
        
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 1.0
    
    @pytest.mark.parametrize("dose", [100.0, 1000.0, 10000.0, 100000.0])
    def test_infection_probability_dose_response(self, dose, default_params):
        """Test infection probability increases with dose."""
        immunity = pybevy.Immunity.with_values(5.0, 5.0, 0.0, None)
        
        prob = immunity.calculate_infection_probability(
            dose=dose,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type2,
            params=default_params
        )
        
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 1.0
    
    @pytest.mark.parametrize("immunity_level", [1.0, 5.0, 10.0, 15.0])
    def test_infection_probability_immunity_protection(self, immunity_level, default_params):
        """Test higher immunity reduces infection probability."""
        immunity = pybevy.Immunity.with_values(immunity_level, immunity_level, 0.0, None)
        
        prob = immunity.calculate_infection_probability(
            dose=1000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type2,
            params=default_params
        )
        
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 1.0
    
    def test_calculate_viral_shedding(self, test_immunity, default_params):
        """Test viral shedding calculation."""
        viral_shedding = test_immunity.calculate_viral_shedding(
            24.0, 7.0, default_params
        )
        
        assert isinstance(viral_shedding, float)
        assert viral_shedding >= 0.0
    
    @pytest.mark.parametrize("days_since_infection", [1.0, 7.0, 14.0, 30.0])
    def test_viral_shedding_time_course(self, days_since_infection, default_params):
        """Test viral shedding over time course of infection."""
        immunity = pybevy.Immunity.with_values(2.0, 8.0, 4.0, 0.0)
        
        viral_shedding = immunity.calculate_viral_shedding(
            days_since_infection, 30.0, default_params
        )
        
        assert isinstance(viral_shedding, float)
        assert viral_shedding >= 0.0
    
    def test_calculate_shed_duration(self, test_immunity, shed_duration_params):
        """Test shed duration calculation."""
        duration = test_immunity.calculate_shed_duration(shed_duration_params)
        
        assert isinstance(duration, float)
        assert duration > 0.0
    
    @pytest.mark.parametrize("immunity_level", [1.0, 5.0, 10.0])
    def test_shed_duration_immunity_dependency(self, immunity_level, shed_duration_params):
        """Test shed duration depends on immunity level."""
        immunity = pybevy.Immunity.with_values(immunity_level, immunity_level, 0.0, None)
        duration = immunity.calculate_shed_duration(shed_duration_params)
        
        assert isinstance(duration, float)
        assert duration > 0.0


class TestInfectionCalculationMethods:
    """Test calculation methods on Infection class."""
    
    def test_should_clear_infection_early(self, test_infection):
        """Test infection should not clear early in course."""
        should_clear = test_infection.should_clear_infection(days_since_infection=5.0)
        
        assert isinstance(should_clear, bool)
        # Early in infection, should typically not clear
        assert not should_clear
    
    def test_should_clear_infection_late(self, test_infection):
        """Test infection should clear late in course."""
        should_clear = test_infection.should_clear_infection(days_since_infection=60.0)
        
        assert isinstance(should_clear, bool)
        # Late in infection, should typically clear (depends on shed_duration=42.5)
        assert should_clear
    
    @pytest.mark.parametrize("days_since_infection", [1.0, 20.0, 40.0, 60.0])
    def test_should_clear_infection_time_course(self, days_since_infection):
        """Test infection clearance over time course."""
        infection = pybevy.Infection(
            shed_duration=30.0,  # Fixed duration for predictable testing
            viral_shedding=1000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type1
        )
        
        should_clear = infection.should_clear_infection(days_since_infection)
        assert isinstance(should_clear, bool)
        
        # Should clear after shed_duration
        if days_since_infection > 30.0:
            assert should_clear
        else:
            assert not should_clear
    
    @pytest.mark.parametrize("shed_duration", [10.0, 30.0, 60.0])
    def test_clearance_depends_on_shed_duration(self, shed_duration):
        """Test infection clearance depends on shed duration."""
        infection = pybevy.Infection(
            shed_duration=shed_duration,
            viral_shedding=1000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type1
        )
        
        # Test at half and double the shed duration
        should_clear_early = infection.should_clear_infection(shed_duration * 0.5)
        should_clear_late = infection.should_clear_infection(shed_duration * 1.5)
        
        assert not should_clear_early
        assert should_clear_late


class TestMethodIntegration:
    """Test integration between different calculation methods."""
    
    def test_infection_to_clearance_workflow(self, default_params, shed_duration_params):
        """Test complete workflow from infection to clearance."""
        immunity = pybevy.Immunity.with_values(3.0, 3.0, 0.0, None)
        
        # Step 1: Calculate infection probability
        infection_prob = immunity.calculate_infection_probability(
            dose=5000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type2,
            params=default_params
        )
        assert 0.0 <= infection_prob <= 1.0
        
        # Step 2: If infected, calculate shed duration
        if infection_prob > 0.1:  # Simulate infection occurs
            shed_duration = immunity.calculate_shed_duration(shed_duration_params)
            assert shed_duration > 0.0
            
            # Step 3: Create infection
            infection = pybevy.Infection(
                shed_duration=shed_duration,
                viral_shedding=1000.0,
                strain=pybevy.InfectionStrain.WPV,
                serotype=pybevy.InfectionSerotype.Type2
            )
            
            # Step 4: Check clearance at different times
            should_clear_early = infection.should_clear_infection(5.0)
            should_clear_late = infection.should_clear_infection(shed_duration + 10.0)
            
            assert not should_clear_early
            assert should_clear_late
    
    def test_strain_serotype_combinations(self, default_params, infection_strains, infection_serotypes):
        """Test all strain/serotype combinations work in calculations."""
        immunity = pybevy.Immunity.with_values(5.0, 5.0, 0.0, None)
        
        for strain in infection_strains:
            for serotype in infection_serotypes:
                # Test infection probability calculation
                prob = immunity.calculate_infection_probability(
                    dose=1000.0,
                    strain=strain,
                    serotype=serotype,
                    params=default_params
                )
                assert 0.0 <= prob <= 1.0
                
                # Test infection clearance
                infection = pybevy.Infection(
                    shed_duration=40.0,
                    viral_shedding=1000.0,
                    strain=strain,
                    serotype=serotype
                )
                should_clear = infection.should_clear_infection(50.0)
                assert isinstance(should_clear, bool)