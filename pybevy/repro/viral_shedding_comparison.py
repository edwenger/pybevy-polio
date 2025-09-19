"""
Direct comparison of viral shedding calculations between original Python and current Rust implementations
for naive 24-month olds over the first 60 days of infection.
"""

import numpy as np
import matplotlib.pyplot as plt
import pybevy as pb

# Original Python implementation (extracted from ImmunoInfection class)
def original_peak_cid50(prechallenge_immunity, age_months, k=0.056, Smax=6.7, Smin=4.3, tau=12):
    """Original peak_cid50 function"""
    if age_months >= 6:
        peak_cid50_naiive = (Smax - Smin) * np.exp((7 - age_months) / tau) + Smin
    else:
        peak_cid50_naiive = Smax
    return (1 - k * np.log2(prechallenge_immunity)) * peak_cid50_naiive


def original_viral_shed(prechallenge_immunity, age_months, t_infection_days, eta=1.65, v=0.17, epsilon=0.32):
    """Original viral_shed function (using natural log)"""
    if t_infection_days <= 0:
        return 0

    peak_cid50_val = original_peak_cid50(prechallenge_immunity, age_months)
    predicted_concentration = (10**peak_cid50_val *
                              np.exp(eta - 0.5*v**2 -
                                    ((np.log(t_infection_days) - eta)**2) /
                                    (2*(v + epsilon*np.log(t_infection_days))**2)) /
                              t_infection_days)
    return max(10**2.6, predicted_concentration)


def original_viral_shed_log10(prechallenge_immunity, age_months, t_infection_days, eta=1.65, v=0.17, epsilon=0.32):
    """Original viral_shed function with np.log10 instead of np.log"""
    if t_infection_days <= 0:
        return 0

    peak_cid50_val = original_peak_cid50(prechallenge_immunity, age_months)
    predicted_concentration = (10**peak_cid50_val *
                              np.exp(eta - 0.5*v**2 -
                                    ((np.log10(t_infection_days) - eta)**2) /
                                    (2*(v + epsilon*np.log10(t_infection_days))**2)) /
                              t_infection_days)
    return max(10**2.6, predicted_concentration)


def test_viral_shedding_comparison():
    """Compare original vs Rust viral shedding calculations"""

    # Parameters for test
    age_months = 24.0  # 2 years old
    prechallenge_immunity = 1.0  # Naive
    max_days = 60
    days = np.arange(1, max_days + 1)  # Start from day 1 (avoid log(0))

    # Initialize Rust objects
    params = pb.Params()
    immunity = pb.Immunity()
    immunity.prechallenge_immunity = prechallenge_immunity

    # Calculate shedding values using all three methods
    original_shedding = []
    original_shedding_log10 = []
    rust_shedding = []

    for day in days:
        # Original Python calculation (natural log)
        orig_val = original_viral_shed(prechallenge_immunity, age_months, float(day))
        original_shedding.append(orig_val)

        # Original Python with log10
        orig_log10_val = original_viral_shed_log10(prechallenge_immunity, age_months, float(day))
        original_shedding_log10.append(orig_log10_val)

        # Rust calculation
        rust_val = immunity.calculate_viral_shedding(age_months, float(day), params)
        rust_shedding.append(rust_val)

    # Create comparison plot
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 8))

    # Plot 1: All three curves overlaid
    ax1.semilogy(days, original_shedding, 'b-', label='Original Python (ln)', linewidth=2)
    ax1.semilogy(days, original_shedding_log10, 'g-', label='Original Python (log10)', linewidth=2)
    ax1.semilogy(days, rust_shedding, 'r--', label='Current Rust (ln)', linewidth=2)
    ax1.set_title('Viral Shedding Comparison: 24-month old, naive immunity')
    ax1.set_xlabel('Days since infection')
    ax1.set_ylabel('Viral CID50')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Ratios
    ratio_rust_orig = np.array(rust_shedding) / np.array(original_shedding)
    ratio_log10_orig = np.array(original_shedding_log10) / np.array(original_shedding)
    ax2.plot(days, ratio_rust_orig, 'r-', linewidth=2, label='Rust / Original(ln)')
    ax2.plot(days, ratio_log10_orig, 'g-', linewidth=2, label='Original(log10) / Original(ln)')
    ax2.set_title('Ratios to Original (ln) version')
    ax2.set_xlabel('Days since infection')
    ax2.set_ylabel('Ratio')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=1.0, color='k', linestyle='--', alpha=0.5)

    # Plot 3: Peak values comparison (first 10 days)
    days_peak = days[:10]
    ax3.semilogy(days_peak, np.array(original_shedding)[:10], 'b-', label='Original (ln)', linewidth=2, marker='o')
    ax3.semilogy(days_peak, np.array(original_shedding_log10)[:10], 'g-', label='Original (log10)', linewidth=2, marker='s')
    ax3.semilogy(days_peak, np.array(rust_shedding)[:10], 'r--', label='Rust (ln)', linewidth=2, marker='^')
    ax3.set_title('Peak Period Comparison (First 10 Days)')
    ax3.set_xlabel('Days since infection')
    ax3.set_ylabel('Viral CID50')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    # Print some key statistics
    print("Viral Shedding Comparison Results:")
    print(f"Age: {age_months} months ({age_months/12:.1f} years)")
    print(f"Prechallenge immunity: {prechallenge_immunity}")
    print(f"Days analyzed: {len(days)}")
    print()
    print("Peak values (first few days):")
    for i in range(min(5, len(days))):
        day = days[i]
        orig_ln = original_shedding[i]
        orig_log10 = original_shedding_log10[i]
        rust = rust_shedding[i]
        ratio_log10 = orig_log10/orig_ln
        print(f"  Day {day}: Original(ln)={orig_ln:.1f}, Original(log10)={orig_log10:.1f}, Rust={rust:.1f}")
        print(f"          log10/ln ratio={ratio_log10:.3f}")
    print()

    ratio_rust_orig = np.array(rust_shedding) / np.array(original_shedding)
    ratio_log10_orig = np.array(original_shedding_log10) / np.array(original_shedding)
    print(f"Rust/Original(ln) ratio range: {np.min(ratio_rust_orig):.3f} to {np.max(ratio_rust_orig):.3f}")
    print(f"Original(log10)/Original(ln) ratio range: {np.min(ratio_log10_orig):.3f} to {np.max(ratio_log10_orig):.3f}")

    # Test peak_cid50 calculation separately
    print("\nPeak CID50 calculation comparison:")
    orig_peak = original_peak_cid50(prechallenge_immunity, age_months)
    print(f"Original peak_cid50: {orig_peak:.3f}")
    print(f"10^{orig_peak:.3f} = {10**orig_peak:.1f}")

    # Show the key difference
    max_log10_value = np.max(original_shedding_log10)
    max_ln_value = np.max(original_shedding)
    print(f"\nKey finding:")
    print(f"Peak shedding with ln: {max_ln_value:.0f} CID50")
    print(f"Peak shedding with log10: {max_log10_value:.0f} CID50")
    print(f"Reduction factor: {max_ln_value/max_log10_value:.1f}x")

    return fig


if __name__ == "__main__":
    print("Running viral shedding comparison test...")
    fig = test_viral_shedding_comparison()
    plt.show()