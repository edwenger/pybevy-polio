"""
Tests for Parameter Layer - Disease parameter classes and modification.
"""

import pytest
import pybevy


class TestImmunityWaningParams:
    """Test immunity waning parameter class."""
    
    def test_default_values(self, immunity_waning_params):
        """Test default parameter values are reasonable."""
        assert isinstance(immunity_waning_params.rate, float)
        assert 0.0 < immunity_waning_params.rate < 2.0
    
    def test_parameter_modification(self, immunity_waning_params):
        """Test parameter values can be modified."""
        original_rate = immunity_waning_params.rate
        immunity_waning_params.rate = 0.95  # Use different value than default 0.87
        assert immunity_waning_params.rate == pytest.approx(0.95)
        assert immunity_waning_params.rate != original_rate


class TestThetaNabsParams:
    """Test theta nabs parameter class."""
    
    def test_default_values(self, theta_nabs_params):
        """Test default parameter values are reasonable."""
        assert isinstance(theta_nabs_params.a, float)
        assert isinstance(theta_nabs_params.b, float)
        assert isinstance(theta_nabs_params.c, float) 
        assert isinstance(theta_nabs_params.d, float)
    
    def test_parameter_modification(self, theta_nabs_params):
        """Test parameter values can be modified."""
        theta_nabs_params.a = 4.82
        theta_nabs_params.b = -0.30
        theta_nabs_params.c = 3.31
        theta_nabs_params.d = -0.32
        
        assert theta_nabs_params.a == pytest.approx(4.82)
        assert theta_nabs_params.b == pytest.approx(-0.30)
        assert theta_nabs_params.c == pytest.approx(3.31)
        assert theta_nabs_params.d == pytest.approx(-0.32)


class TestViralSheddingParams:
    """Test viral shedding parameter class."""
    
    def test_default_values(self, viral_shedding_params):
        """Test default parameter values are reasonable."""
        assert isinstance(viral_shedding_params.eta, float)
        assert isinstance(viral_shedding_params.v, float)
        assert isinstance(viral_shedding_params.epsilon, float)
        assert viral_shedding_params.eta > 0
        assert viral_shedding_params.v > 0
    
    def test_parameter_modification(self, viral_shedding_params):
        """Test parameter values can be modified."""
        viral_shedding_params.eta = 1.65
        viral_shedding_params.v = 0.17
        viral_shedding_params.epsilon = 0.32
        
        assert viral_shedding_params.eta == pytest.approx(1.65)
        assert viral_shedding_params.v == pytest.approx(0.17)
        assert viral_shedding_params.epsilon == pytest.approx(0.32)


class TestPeakCid50Params:
    """Test peak CID50 parameter class."""
    
    def test_default_values(self, peak_cid50_params):
        """Test default parameter values are reasonable."""
        assert isinstance(peak_cid50_params.k, float)
        assert isinstance(peak_cid50_params.smax, float)
        assert isinstance(peak_cid50_params.smin, float)
        assert isinstance(peak_cid50_params.tau, float)
        assert peak_cid50_params.smax > peak_cid50_params.smin
    
    def test_parameter_modification(self, peak_cid50_params):
        """Test parameter values can be modified."""
        peak_cid50_params.k = 0.056
        peak_cid50_params.smax = 6.7
        peak_cid50_params.smin = 4.3
        peak_cid50_params.tau = 12.0
        
        assert peak_cid50_params.k == pytest.approx(0.056)
        assert peak_cid50_params.smax == pytest.approx(6.7)
        assert peak_cid50_params.smin == pytest.approx(4.3)
        assert peak_cid50_params.tau == pytest.approx(12.0)


class TestProbTransmitParams:
    """Test transmission probability parameter class."""
    
    def test_default_values(self, prob_transmit_params):
        """Test default parameter values are reasonable."""
        assert isinstance(prob_transmit_params.alpha, float)
        assert isinstance(prob_transmit_params.gamma, float)
        assert 0.0 < prob_transmit_params.alpha < 1.0
        assert 0.0 < prob_transmit_params.gamma < 1.0
    
    def test_parameter_modification(self, prob_transmit_params):
        """Test parameter values can be modified."""
        prob_transmit_params.alpha = 0.44
        prob_transmit_params.gamma = 0.46
        
        assert prob_transmit_params.alpha == pytest.approx(0.44)
        assert prob_transmit_params.gamma == pytest.approx(0.46)


class TestShedDurationParams:
    """Test shedding duration parameter class."""
    
    def test_default_values(self, shed_duration_params):
        """Test default parameter values are reasonable."""
        assert isinstance(shed_duration_params.u, float)
        assert isinstance(shed_duration_params.delta, float)
        assert isinstance(shed_duration_params.sigma, float)
        assert shed_duration_params.u > 0
    
    def test_parameter_modification(self, shed_duration_params):
        """Test parameter values can be modified."""
        shed_duration_params.u = 43.0
        shed_duration_params.delta = 1.16
        shed_duration_params.sigma = 1.69
        
        assert shed_duration_params.u == pytest.approx(43.0)
        assert shed_duration_params.delta == pytest.approx(1.16)
        assert shed_duration_params.sigma == pytest.approx(1.69)


class TestStrainParams:
    """Test strain parameter class."""
    
    def test_default_values(self, strain_params):
        """Test default parameter values are reasonable."""
        assert isinstance(strain_params.sabin_scale_parameter, float)
        assert isinstance(strain_params.strain_take_modifier, float)
        assert strain_params.strain_take_modifier > 0
    
    def test_parameter_modification(self, strain_params, shed_duration_params):
        """Test parameter values can be modified."""
        strain_params.sabin_scale_parameter = 2.3
        strain_params.strain_take_modifier = 1.0
        strain_params.shed_duration = shed_duration_params
        
        assert strain_params.sabin_scale_parameter == pytest.approx(2.3)
        assert strain_params.strain_take_modifier == pytest.approx(1.0)
        # Test shed_duration assignment by comparing a field value
        assert strain_params.shed_duration.u == pytest.approx(shed_duration_params.u)


class TestMainParams:
    """Test main Params struct that contains all parameter subsets."""
    
    def test_default_construction(self, default_params):
        """Test Params can be constructed with defaults."""
        assert isinstance(default_params, pybevy.Params)
        assert hasattr(default_params, 'immunity_waning')
        assert hasattr(default_params, 'theta_nabs')
        assert hasattr(default_params, 'viral_shedding')
        assert hasattr(default_params, 'peak_cid50')
        assert hasattr(default_params, 'p_transmit')
    
    def test_parameter_assignment(self, default_params, immunity_waning_params, 
                                 theta_nabs_params, viral_shedding_params):
        """Test parameter sub-structs can be assigned."""
        # Test assignment by comparing field values rather than object identity
        original_rate = immunity_waning_params.rate
        default_params.immunity_waning = immunity_waning_params
        assert default_params.immunity_waning.rate == pytest.approx(original_rate)
        
        original_alpha = theta_nabs_params.a
        default_params.theta_nabs = theta_nabs_params
        assert default_params.theta_nabs.a == pytest.approx(original_alpha)
        
        original_eta = viral_shedding_params.eta
        default_params.viral_shedding = viral_shedding_params
        assert default_params.viral_shedding.eta == pytest.approx(original_eta)
    
    def test_nested_parameter_access(self, default_params):
        """Test nested parameter access through main Params."""
        # Test that we can read nested parameters (modification might not work due to PyO3 copying)
        original_rate = default_params.immunity_waning.rate
        assert isinstance(original_rate, float)
        assert original_rate > 0.0
        
        # Test that nested objects exist and have expected structure
        assert hasattr(default_params.immunity_waning, 'rate')
        assert hasattr(default_params.theta_nabs, 'a')
        assert hasattr(default_params.viral_shedding, 'eta')