#!/usr/bin/env python3
"""Test script to check align_mag_roll CLI command in SITL"""

import subprocess
import time
import sys

def test_cli_command():
    """Start SITL and test the align_mag_roll command"""

    # Start SITL process
    print("Starting SITL...")
    proc = subprocess.Popen(
        ['./build_sitl/bin/SITL.elf'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    time.sleep(2)  # Wait for SITL to initialize

    # Send CLI commands
    commands = [
        '#',  # Enter CLI mode
        'get align_mag_roll',  # Test if get works
        'set align_mag_roll=900',  # Test set without spaces
        'set align_mag_roll = 1800',  # Test set with spaces
        'get align_mag',  # Test related setting
        'exit',  # Exit CLI
    ]

    print("\n=== Sending CLI commands ===")
    for cmd in commands:
        print(f"\n> {cmd}")
        proc.stdin.write(cmd + '\n')
        proc.stdin.flush()
        time.sleep(0.5)

    # Wait a bit for output
    time.sleep(1)

    # Terminate SITL
    proc.terminate()

    # Read all output
    output, _ = proc.communicate(timeout=3)

    print("\n=== SITL Output ===")
    print(output)

    # Analyze output
    print("\n=== Analysis ===")
    if "Invalid name" in output:
        print("❌ FOUND 'Invalid name' error!")
        # Extract context around the error
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if "Invalid name" in line:
                context_start = max(0, i-3)
                context_end = min(len(lines), i+3)
                print("\nContext around error:")
                for j in range(context_start, context_end):
                    prefix = ">>>" if j == i else "   "
                    print(f"{prefix} {lines[j]}")
    else:
        print("✓ No 'Invalid name' error detected")

    if "align_mag_roll" in output:
        print("✓ Setting 'align_mag_roll' found in output")
    else:
        print("❌ Setting 'align_mag_roll' NOT found in output")

    return proc.returncode

if __name__ == '__main__':
    try:
        exit_code = test_cli_command()
        sys.exit(exit_code if exit_code else 0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
