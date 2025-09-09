#!/usr/bin/env python3
"""
Simple test for direct PyO3 class bindings to existing structs.
"""

import pybevy

def test_host_class():
    """Test the Host class with direct #[pyclass] binding"""
    print("Testing Host class...")
    
    # Create host with birth day (20 years before sim start)
    host = pybevy.Host(birth_sim_day=-365*20)
    print(f"Created host with birth_sim_day: {host.birth_sim_day}")
    
    # Test property access
    host.birth_sim_day = -365*5  # 5 years before sim start
    print(f"Updated birth_sim_day: {host.birth_sim_day}")
    
    print("✅ Host class test passed!")

def test_immunity_class():
    """Test the Immunity class with direct #[pyclass] binding"""
    print("\nTesting Immunity class...")
    
    # Create default immunity
    immunity = pybevy.Immunity()
    print(f"Default immunity - current: {immunity.current_immunity}")
    print(f"Default immunity - prechallenge: {immunity.prechallenge_immunity}")
    print(f"Default immunity - postchallenge_peak: {immunity.postchallenge_peak_immunity}")
    print(f"Default immunity - ti_infected: {immunity.ti_infected}")
    
    # Test property modification
    immunity.current_immunity = 8.5
    immunity.prechallenge_immunity = 3.2
    immunity.postchallenge_peak_immunity = 12.1
    immunity.ti_infected = 15.0
    
    print(f"Modified immunity - current: {immunity.current_immunity}")
    print(f"Modified immunity - prechallenge: {immunity.prechallenge_immunity}")
    print(f"Modified immunity - postchallenge_peak: {immunity.postchallenge_peak_immunity}")
    print(f"Modified immunity - ti_infected: {immunity.ti_infected}")
    
    # Test with_values constructor
    immunity2 = pybevy.Immunity.with_values(2.0, 5.0, 4.0, 7.5)
    print(f"Custom immunity - current: {immunity2.current_immunity}")
    print(f"Custom immunity - prechallenge: {immunity2.prechallenge_immunity}")
    print(f"Custom immunity - postchallenge_peak: {immunity2.postchallenge_peak_immunity}")
    print(f"Custom immunity - ti_infected: {immunity2.ti_infected}")
    
    print("✅ Immunity class test passed!")

def test_infection_class():
    """Test the Infection class and enums"""
    print("\nTesting Infection class and enums...")
    
    # Test enums
    wpv = pybevy.InfectionStrain.WPV
    opv = pybevy.InfectionStrain.OPV
    type1 = pybevy.InfectionSerotype.Type1
    type2 = pybevy.InfectionSerotype.Type2
    type3 = pybevy.InfectionSerotype.Type3
    
    print(f"Strains: {wpv}, {opv}")
    print(f"Serotypes: {type1}, {type2}, {type3}")
    
    # Create infection
    infection = pybevy.Infection(
        shed_duration=42.5,
        viral_shedding=1000.0,
        strain=wpv,
        serotype=type2
    )
    
    print(f"Infection - shed_duration: {infection.shed_duration}")
    print(f"Infection - viral_shedding: {infection.viral_shedding}")
    print(f"Infection - strain: {infection.strain}")
    print(f"Infection - serotype: {infection.serotype}")
    
    # Test property modification
    infection.shed_duration = 30.0
    infection.viral_shedding = 500.0
    infection.strain = opv
    infection.serotype = type3
    
    print(f"Modified infection - shed_duration: {infection.shed_duration}")
    print(f"Modified infection - viral_shedding: {infection.viral_shedding}")
    print(f"Modified infection - strain: {infection.strain}")
    print(f"Modified infection - serotype: {infection.serotype}")
    
    print("✅ Infection class test passed!")

def test_params_classes():
    """Test all parameter classes"""
    print("\nTesting parameter classes...")
    
    # Test individual parameter structs
    waning = pybevy.ImmunityWaningParams()
    waning.rate = 0.87
    print(f"ImmunityWaningParams - rate: {waning.rate}")
    
    theta_nabs = pybevy.ThetaNabsParams()
    theta_nabs.a = 4.82
    theta_nabs.b = -0.30
    theta_nabs.c = 3.31
    theta_nabs.d = -0.32
    print(f"ThetaNabsParams - a: {theta_nabs.a}, b: {theta_nabs.b}")
    
    viral_shedding = pybevy.ViralSheddingParams()
    viral_shedding.eta = 1.65
    viral_shedding.v = 0.17
    viral_shedding.epsilon = 0.32
    print(f"ViralSheddingParams - eta: {viral_shedding.eta}, v: {viral_shedding.v}")
    
    peak_cid50 = pybevy.PeakCid50Params()
    peak_cid50.k = 0.056
    peak_cid50.smax = 6.7
    peak_cid50.smin = 4.3
    peak_cid50.tau = 12.0
    print(f"PeakCid50Params - k: {peak_cid50.k}, smax: {peak_cid50.smax}")
    
    p_transmit = pybevy.ProbTransmitParams()
    p_transmit.alpha = 0.44
    p_transmit.gamma = 0.46
    print(f"ProbTransmitParams - alpha: {p_transmit.alpha}, gamma: {p_transmit.gamma}")
    
    shed_duration = pybevy.ShedDurationParams()
    shed_duration.u = 43.0
    shed_duration.delta = 1.16
    shed_duration.sigma = 1.69
    print(f"ShedDurationParams - u: {shed_duration.u}, delta: {shed_duration.delta}")
    
    strain_params = pybevy.StrainParams()
    strain_params.sabin_scale_parameter = 2.3
    strain_params.strain_take_modifier = 1.0
    strain_params.shed_duration = shed_duration
    print(f"StrainParams - sabin_scale: {strain_params.sabin_scale_parameter}, take_mod: {strain_params.strain_take_modifier}")
    
    # Test main Params struct
    params = pybevy.Params()
    params.immunity_waning = waning
    params.theta_nabs = theta_nabs
    params.viral_shedding = viral_shedding
    params.peak_cid50 = peak_cid50
    params.p_transmit = p_transmit
    
    print(f"Params - immunity_waning.rate: {params.immunity_waning.rate}")
    print(f"Params - theta_nabs.a: {params.theta_nabs.a}")
    print(f"Params - viral_shedding.eta: {params.viral_shedding.eta}")
    
    print("✅ Parameter classes test passed!")

def test_pure_functions():
    """Test the pure calculation functions"""
    print("\nTesting pure calculation functions...")
    
    # Set up test data
    immunity = pybevy.Immunity.with_values(2.0, 8.0, 4.0, 10.0)
    viral_shedding_params = pybevy.ViralSheddingParams()
    peak_cid50_params = pybevy.PeakCid50Params()
    shed_duration_params = pybevy.ShedDurationParams()
    
    # Test calculate_immunity_waning
    waning_result = pybevy.calculate_immunity_waning(8.0, 45.0, 0.87)
    print(f"calculate_immunity_waning(8.0, 45.0, 0.87) = {waning_result}")
    
    # Test should_clear_infection
    should_clear = pybevy.should_clear_infection(45.0, 30.0)
    print(f"should_clear_infection(45.0, 30.0) = {should_clear}")
    
    should_not_clear = pybevy.should_clear_infection(20.0, 30.0)
    print(f"should_clear_infection(20.0, 30.0) = {should_not_clear}")
    
    # Test calculate_viral_shedding
    viral_shedding = pybevy.calculate_viral_shedding(
        immunity, 24.0, 7.0, viral_shedding_params, peak_cid50_params
    )
    print(f"calculate_viral_shedding(...) = {viral_shedding}")
    
    # Test calculate_infection_probability
    infection_prob = pybevy.calculate_infection_probability(
        4.0, 1000.0, 2.3, 0.44, 0.46, 1.0
    )
    print(f"calculate_infection_probability(4.0, 1000.0, 2.3, 0.44, 0.46, 1.0) = {infection_prob}")
    
    # Test update_shed_duration
    shed_duration = pybevy.update_shed_duration(immunity, shed_duration_params)
    print(f"update_shed_duration(...) = {shed_duration}")
    
    print("✅ Pure functions test passed!")

if __name__ == "__main__":
    test_host_class()
    test_immunity_class()
    test_infection_class()
    test_params_classes()
    test_pure_functions()
    print("\n🎉 All PyO3 bindings working correctly!")
    print("Ready for granular Python/R access to polio disease model!")