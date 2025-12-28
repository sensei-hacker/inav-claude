#!/usr/bin/env python3
"""
Analyze navEPH Frequency Spectrum from Blackbox Log

Extracts navEPH data from decoded blackbox CSV and performs FFT analysis
to identify frequency patterns (e.g., the reported 198 Hz fluctuation).

Usage:
    python3 analyze_naveph_spectrum.py <blackbox.csv>
"""

import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftfreq

def extract_naveph_from_debug7(debug7_value):
    """
    Extract navEPH from debug[7] bit-packed value.

    From navigation_pos_estimator.c:856:
    DEBUG_SET(DEBUG_POS_EST, 7,
        (posEstimator.flags & 0b1111111) << 20 |   // Bits 20-26: flags
        (MIN(navEPH, 1000) & 0x3FF) << 10 |        // Bits 10-19: navEPH
        (MIN(navEPV, 1000) & 0x3FF));              // Bits 0-9:   navEPV
    """
    navEPH_cm = (debug7_value >> 10) & 0x3FF  # bits 10-19
    navEPV_cm = debug7_value & 0x3FF           # bits 0-9
    flags = (debug7_value >> 20) & 0x7F        # bits 20-26

    return navEPH_cm, navEPV_cm, flags


def analyze_blackbox_csv(csv_file):
    """Analyze navEPH frequency spectrum from decoded blackbox CSV."""

    print("=" * 70)
    print("navEPH Frequency Spectrum Analysis")
    print("=" * 70)
    print()
    print(f"Input file: {csv_file}")
    print()

    # Read CSV
    time_us = []
    navEPH_values = []
    navEPV_values = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        # Check if debug[7] column exists
        if 'debug[7]' not in reader.fieldnames:
            print("✗ Error: No 'debug[7]' column found in CSV")
            print("  Available columns:", reader.fieldnames[:10], "...")
            return 1

        for row in reader:
            try:
                # Get time (in microseconds)
                time = int(row.get('time (us)', row.get('loopIteration', 0)))

                # Get debug[7] value
                debug7 = int(row['debug[7]'])

                # Extract navEPH
                navEPH_cm, navEPV_cm, flags = extract_naveph_from_debug7(debug7)

                time_us.append(time)
                navEPH_values.append(navEPH_cm)
                navEPV_values.append(navEPV_cm)

            except (ValueError, KeyError) as e:
                continue  # Skip malformed rows

    if len(time_us) == 0:
        print("✗ Error: No valid data found in CSV")
        return 1

    # Convert to numpy arrays
    time_us = np.array(time_us)
    navEPH_values = np.array(navEPH_values)
    navEPV_values = np.array(navEPV_values)

    # Calculate time in seconds
    time_s = (time_us - time_us[0]) / 1e6

    # Calculate sample rate
    dt = np.median(np.diff(time_s))
    sample_rate = 1.0 / dt if dt > 0 else 0

    print(f"Samples: {len(navEPH_values)}")
    print(f"Duration: {time_s[-1]:.2f} seconds")
    print(f"Sample rate: {sample_rate:.1f} Hz")
    print(f"Time step: {dt*1000:.2f} ms")
    print()

    # Statistics
    print("navEPH Statistics:")
    print(f"  Min: {np.min(navEPH_values)} cm ({np.min(navEPH_values)/100:.2f} m)")
    print(f"  Max: {np.max(navEPH_values)} cm ({np.max(navEPH_values)/100:.2f} m)")
    print(f"  Mean: {np.mean(navEPH_values):.1f} cm ({np.mean(navEPH_values)/100:.2f} m)")
    print(f"  Std: {np.std(navEPH_values):.1f} cm ({np.std(navEPH_values)/100:.2f} m)")
    print()

    # Perform FFT
    print("Performing FFT analysis...")

    # Remove DC component (mean)
    navEPH_ac = navEPH_values - np.mean(navEPH_values)

    # Apply window to reduce spectral leakage
    window = signal.windows.hann(len(navEPH_ac))
    navEPH_windowed = navEPH_ac * window

    # FFT
    N = len(navEPH_windowed)
    fft_values = fft(navEPH_windowed)
    fft_freq = fftfreq(N, dt)

    # Take only positive frequencies
    positive_freq_idx = fft_freq > 0
    fft_freq_positive = fft_freq[positive_freq_idx]
    fft_magnitude = np.abs(fft_values[positive_freq_idx]) / N

    # Find peaks
    peaks, properties = signal.find_peaks(fft_magnitude,
                                          height=np.max(fft_magnitude) * 0.1,  # 10% of max
                                          distance=int(sample_rate * 0.5))  # At least 0.5 Hz apart

    print(f"Found {len(peaks)} significant frequency peaks:")
    print()

    # Sort peaks by magnitude
    peak_indices = peaks[np.argsort(fft_magnitude[peaks])[::-1]]

    for i, peak_idx in enumerate(peak_indices[:10]):  # Top 10 peaks
        freq = fft_freq_positive[peak_idx]
        magnitude = fft_magnitude[peak_idx]
        print(f"  {i+1}. {freq:7.2f} Hz - Magnitude: {magnitude:.4f}")

    print()

    # Check for 198 Hz specifically
    target_freq = 198.0
    freq_tolerance = 5.0  # Hz
    near_target = np.abs(fft_freq_positive - target_freq) < freq_tolerance

    if np.any(near_target):
        target_magnitude = np.max(fft_magnitude[near_target])
        target_freq_actual = fft_freq_positive[near_target][np.argmax(fft_magnitude[near_target])]
        print(f"⚠️  Found peak near 198 Hz: {target_freq_actual:.2f} Hz (magnitude: {target_magnitude:.4f})")
    else:
        print(f"✓  No significant peak found near 198 Hz")

    print()

    # Create plots
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # Plot 1: Time series
    axes[0].plot(time_s, navEPH_values / 100, 'b-', linewidth=0.5)
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('navEPH (m)')
    axes[0].set_title('navEPH Time Series')
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Frequency spectrum (linear scale)
    axes[1].plot(fft_freq_positive, fft_magnitude, 'b-', linewidth=0.5)
    axes[1].plot(fft_freq_positive[peak_indices[:10]], fft_magnitude[peak_indices[:10]], 'ro', markersize=6)
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('Magnitude')
    axes[1].set_title('Frequency Spectrum (Linear)')
    axes[1].set_xlim([0, min(250, sample_rate/2)])
    axes[1].grid(True, alpha=0.3)

    # Highlight 198 Hz region
    axes[1].axvline(198, color='r', linestyle='--', alpha=0.5, label='198 Hz target')
    axes[1].legend()

    # Plot 3: Frequency spectrum (log scale)
    axes[2].semilogy(fft_freq_positive, fft_magnitude, 'b-', linewidth=0.5)
    axes[2].plot(fft_freq_positive[peak_indices[:10]], fft_magnitude[peak_indices[:10]], 'ro', markersize=6)
    axes[2].set_xlabel('Frequency (Hz)')
    axes[2].set_ylabel('Magnitude (log scale)')
    axes[2].set_title('Frequency Spectrum (Log)')
    axes[2].set_xlim([0, min(250, sample_rate/2)])
    axes[2].grid(True, alpha=0.3, which='both')
    axes[2].axvline(198, color='r', linestyle='--', alpha=0.5, label='198 Hz target')
    axes[2].legend()

    plt.tight_layout()

    # Save plot
    output_file = csv_file.replace('.csv', '_spectrum.png')
    plt.savefig(output_file, dpi=150)
    print(f"Plot saved to: {output_file}")

    # Show plot
    plt.show()

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_naveph_spectrum.py <blackbox.csv>")
        sys.exit(1)

    csv_file = sys.argv[1]
    sys.exit(analyze_blackbox_csv(csv_file))
