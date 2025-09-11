"""
Tests for Integration Layer - Cross-layer integration and end-to-end workflows.
"""

import pytest
import pybevy
import numpy as np


class TestHighLevelSimulation:
    """Test high-level simulation functionality."""
    
    def test_run_bevy_app_basic(self):
        """Test basic run_bevy_app functionality."""
        params = {
            'n_hosts': 10,
            'max_days': 30,
            'incidence_rate': 0.05,
            'log10_dose': 5.0
        }
        
        result = pybevy.run_bevy_app(params)
        
        # Check output structure
        assert isinstance(result, np.ndarray)
        assert result.shape == (10, 31, 2)  # [host, day, metric] - includes day 0
        
        # Check data types
        assert result.dtype == np.float64
        
        # Check that immunity values are reasonable
        immunity_data = result[:, :, 0]  # Immunity is metric 0
        assert np.all(immunity_data >= 0.0)
        assert np.all(immunity_data < 1e6)  # Very generous upper bound
        
        # Check that viral shedding values are reasonable
        shedding_data = result[:, :, 1]  # Viral shedding is metric 1
        assert np.all(shedding_data >= 0.0)
    
    @pytest.mark.parametrize("n_hosts", [1, 5, 20])
    def test_run_bevy_app_population_sizes(self, n_hosts):
        """Test simulation with different population sizes."""
        params = {
            'n_hosts': n_hosts,
            'max_days': 10,
            'incidence_rate': 0.1,
            'log10_dose': 4.5
        }
        
        result = pybevy.run_bevy_app(params)
        assert result.shape[0] == n_hosts
    
    @pytest.mark.parametrize("max_days", [1, 10, 50])
    def test_run_bevy_app_simulation_lengths(self, max_days):
        """Test simulation with different durations."""
        params = {
            'n_hosts': 5,
            'max_days': max_days,
            'incidence_rate': 0.05,
            'log10_dose': 5.0
        }
        
        result = pybevy.run_bevy_app(params)
        assert result.shape[1] == max_days + 1  # Includes day 0
    
    @pytest.mark.parametrize("incidence_rate", [0.0, 0.05, 0.2])
    def test_run_bevy_app_incidence_rates(self, incidence_rate):
        """Test simulation with different incidence rates."""
        params = {
            'n_hosts': 10,
            'max_days': 20,
            'incidence_rate': incidence_rate,
            'log10_dose': 5.0
        }
        
        result = pybevy.run_bevy_app(params)
        
        # Higher incidence should generally lead to more infections
        # (though this is stochastic so we just check basic properties)
        shedding_data = result[:, :, 1]
        if incidence_rate > 0:
            # Should see some viral shedding with positive incidence
            assert np.any(shedding_data > 0) or incidence_rate < 0.01
    
    @pytest.mark.parametrize("log10_dose", [3.0, 5.0, 7.0])
    def test_run_bevy_app_dose_levels(self, log10_dose):
        """Test simulation with different dose levels."""
        params = {
            'n_hosts': 10,
            'max_days': 15,
            'incidence_rate': 0.1,
            'log10_dose': log10_dose
        }
        
        result = pybevy.run_bevy_app(params)
        
        # Higher doses should generally lead to more infections
        # (though this is stochastic so we just check basic properties)
        shedding_data = result[:, :, 1]
        assert np.all(shedding_data >= 0.0)


class TestThreeLayerApiIntegration:
    """Test integration across all three API layers."""
    
    def test_parameter_to_state_integration(self, default_params):
        """Test parameter layer influences state calculations."""
        # Create immunity with specific parameters
        immunity = pybevy.Immunity.with_values(5.0, 5.0, 0.0, None)
        
        # Modify transmission parameters
        original_alpha = default_params.p_transmit.alpha
        default_params.p_transmit.alpha = 0.8  # High transmission
        
        prob_high = immunity.calculate_infection_probability(
            dose=1000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type2,
            params=default_params
        )
        
        # Reset to lower transmission
        default_params.p_transmit.alpha = 0.2  # Low transmission
        
        prob_low = immunity.calculate_infection_probability(
            dose=1000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type2,
            params=default_params
        )
        
        # Higher alpha should give higher infection probability
        assert prob_high >= prob_low
        
        # Reset original value
        default_params.p_transmit.alpha = original_alpha
    
    def test_state_to_function_integration(self, default_params, shed_duration_params):
        """Test state layer provides inputs to function calculations."""
        # Create host and immunity
        host = pybevy.Host(birth_sim_day=-365*10)  # 10 years old
        immunity = pybevy.Immunity.with_values(3.0, 3.0, 0.0, None)
        
        # Calculate infection probability
        infection_prob = immunity.calculate_infection_probability(
            dose=2000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type1,
            params=default_params
        )
        
        # If infected, create infection state
        if infection_prob > 0.1:  # Simulate infection
            shed_duration = immunity.calculate_shed_duration(shed_duration_params)
            
            infection = pybevy.Infection(
                shed_duration=shed_duration,
                viral_shedding=1000.0,
                strain=pybevy.InfectionStrain.WPV,
                serotype=pybevy.InfectionSerotype.Type1
            )
            
            # Test function calculations with state data
            viral_shedding = immunity.calculate_viral_shedding(
                10.0, infection.shed_duration, default_params
            )
            
            should_clear = infection.should_clear_infection(
                days_since_infection=infection.shed_duration + 5.0
            )
            
            assert isinstance(viral_shedding, float)
            assert viral_shedding >= 0.0
            assert should_clear  # Should clear after shed duration
    
    def test_full_disease_progression_workflow(self, default_params, immunity_waning_params, 
                                             shed_duration_params):
        """Test complete disease progression workflow."""
        # Initial setup
        host = pybevy.Host(birth_sim_day=-365*15)  # 15 years old
        immunity = pybevy.Immunity.with_values(2.0, 2.0, 0.0, None)
        infection = None
        
        simulation_days = 100
        dose = 5000.0
        
        for day in range(simulation_days):
            # Daily exposure chance
            if infection is None and day % 20 == 0:  # Exposure every 20 days
                infection_prob = immunity.calculate_infection_probability(
                    dose=dose,
                    strain=pybevy.InfectionStrain.WPV,
                    serotype=pybevy.InfectionSerotype.Type2,
                    params=default_params
                )
                
                # Simulate stochastic infection
                if infection_prob > 0.5:  # Deterministic for testing
                    # Update immunity state for infection
                    immunity.ti_infected = float(day)
                    immunity.postchallenge_peak_immunity = 8.0  # Boost from infection
                    
                    # Create infection
                    shed_duration = immunity.calculate_shed_duration(shed_duration_params)
                    infection = pybevy.Infection(
                        shed_duration=shed_duration,
                        viral_shedding=1000.0,
                        strain=pybevy.InfectionStrain.WPV,
                        serotype=pybevy.InfectionSerotype.Type2
                    )
            
            # Update infection state
            if infection is not None:
                days_since_infection = day - immunity.ti_infected
                
                # Calculate viral shedding
                viral_shedding = immunity.calculate_viral_shedding(
                    days_since_infection, infection.shed_duration, default_params
                )
                infection.viral_shedding = viral_shedding
                
                # Check for clearance
                if infection.should_clear_infection(days_since_infection):
                    infection = None
            
            # Update immunity (waning)
            if immunity.ti_infected is not None:
                days_since_infection = day - immunity.ti_infected
                if days_since_infection > 30:  # Start waning after 30 days
                    immunity.calculate_waning(days_since_infection, immunity_waning_params)
        
        # Verify final state makes sense
        assert isinstance(immunity.current_immunity, float)
        assert immunity.current_immunity >= 0.0
        
        if immunity.ti_infected is not None:
            assert immunity.ti_infected >= 0.0
            assert immunity.ti_infected < simulation_days


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_run_bevy_app_invalid_params(self):
        """Test run_bevy_app with invalid parameters."""
        # Missing required parameter
        with pytest.raises((KeyError, TypeError)):
            pybevy.run_bevy_app({'n_hosts': 10})
        
        # Invalid parameter types
        with pytest.raises((TypeError, ValueError)):
            pybevy.run_bevy_app({
                'n_hosts': -1,  # Negative hosts
                'max_days': 30,
                'incidence_rate': 0.05,
                'log10_dose': 5.0
            })
    
    def test_extreme_parameter_values(self, default_params):
        """Test calculations with extreme but valid parameter values."""
        immunity = pybevy.Immunity.with_values(0.1, 0.1, 0.0, None)  # Very low immunity
        
        # Very high dose
        prob_high_dose = immunity.calculate_infection_probability(
            dose=1000000.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type1,
            params=default_params
        )
        assert 0.0 <= prob_high_dose <= 1.0
        
        # Very low dose
        prob_low_dose = immunity.calculate_infection_probability(
            dose=1.0,
            strain=pybevy.InfectionStrain.WPV,
            serotype=pybevy.InfectionSerotype.Type1,
            params=default_params
        )
        assert 0.0 <= prob_low_dose <= 1.0
        assert prob_high_dose >= prob_low_dose