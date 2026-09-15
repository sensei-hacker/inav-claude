#!/usr/bin/env python3
"""
provision_wind_z_sign_test.py -- one-time FC provisioning for the PR #11855
vertical-wind (Z-axis) sign test.

Mainline-safe subset of inav-sitl-bench's bench.py provision(), per the
jsbsim-sitl-testing skill (.claude/skills/jsbsim-sitl-testing/SKILL.md).
Adds nothing feature-specific to PR #11855 -- this is just "fixed-wing SITL
via MSP_SIMULATOR HITL, with GPS injection and blackbox-to-FILE logging
turned on" so wind_z_sign_test.py's flight has something to arm and log to.

Run ONCE against a freshly-built SITL.elf (from the PR #11855 branch),
then restart SITL so the saved EEPROM settings take effect:

    python3 provision_wind_z_sign_test.py
    pkill -9 SITL.elf
    cd <build dir> && ./bin/SITL.elf &     # relaunch from the SAME cwd you
                                            # want the blackbox .TXT written to

Requires msp.py from inav-sitl-bench (https://github.com/swissembedded/inav-sitl-bench),
already checked out at ~/inavflight/inav-sitl-bench per the jsbsim-sitl-testing skill.
"""
import os
import struct
import sys

BENCH_DIR = os.path.expanduser("~/inavflight/inav-sitl-bench")
if not os.path.isdir(BENCH_DIR):
    print(f"ERROR: inav-sitl-bench not found at {BENCH_DIR}")
    print("This script reuses its msp.py -- see the jsbsim-sitl-testing skill for setup.")
    sys.exit(1)
sys.path.insert(0, BENCH_DIR)

from msp import MspClient  # noqa: E402

FEATURE_GPS = 1 << 7
FEATURE_BLACKBOX = 1 << 19

PERM_ARM, PERM_ANGLE = 0, 1          # permanent box ids, fc_msp_box.c
CH_ARM, CH_ANGLE = 4, 5              # AUX1/AUX2 in an AETR + AUX1..4 RC layout

BLACKBOX_DEVICE_FILE = 3             # blackbox_io.h


def provision(host="127.0.0.1", port=5760):
    print(f"Connecting to SITL at {host}:{port} ...")
    try:
        msp = MspClient(host=host, port=port)
    except (ConnectionRefusedError, OSError) as e:
        print(f"FAILED to connect: {e}")
        print("Is SITL.elf running and listening on this host:port?")
        print("Note: if running in a sandbox, localhost TCP should be allowlisted; "
              "if it's still blocked, ask the user rather than disabling the sandbox.")
        sys.exit(1)

    try:
        api = msp.api_version()
    except Exception as e:
        print(f"FAILED to get MSP_API_VERSION -- SITL is not responding to MSP: {e}")
        sys.exit(1)
    print(f"Connected. MSP API version: {api}")

    # --- Fixed-wing HITL over MSP_SIMULATOR (mainline-safe subset) ---------
    msp.set_setting("receiver_type", struct.pack("<B", 3))     # SIM (SITL)
    msp.set_setting("platform_type", struct.pack("<B", 1))     # AIRPLANE
    msp.set_setting("small_angle", struct.pack("<B", 180))
    msp.set_setting("baro_hardware", struct.pack("<B", 12))    # FAKE
    msp.set_setting("mag_hardware", struct.pack("<B", 0))      # NONE
    msp.set_setting("init_gyro_cal", struct.pack("<B", 0))     # skip: no real sensors behind HITL
    msp.set_setting("pitot_hardware", struct.pack("<B", 0))    # NONE
    print("  set: receiver_type=SIM, platform_type=AIRPLANE, small_angle=180, "
          "baro=FAKE, mag=NONE, pitot=NONE, init_gyro_cal=0")

    # nav_fw_cruise_speed defaults to 0 (settings.yaml) -- rth_estimator.c's
    # formulas multiply this in directly (e.g. estimateRTHAltitudeChangeTime's
    # cruise_speed*sin(pitch) term), so leaving it at 0 silently drops that
    # term to zero and any test exercising rth_estimator.c gets a degenerate,
    # unrealistic result.
    #
    # IMPORTANT: this must be above the JSBSim airframe's actual stall speed,
    # not just "a plausible small-plane number in the abstract" -- an earlier
    # version of this script set 1500 cm/s (29 kt), which is BELOW the c172p
    # model's stall speed (confirmed via JSBSim's own trim solver: do_trim()
    # fails below ~48 kt for this airframe). That silently put every wind-Z
    # SITL test flight into a continuous stall/mush, not valid level flight,
    # which showed up as erratic pitch, spurious wind[Z] drift even at zero
    # injected wind, and occasional real departures/crashes -- all a test
    # artifact, unrelated to any wind_estimator.c logic. 5000 cm/s (~97 kt)
    # trims to <0.2 deg pitch/AoA for c172p, well clear of stall.
    msp.set_setting("nav_fw_cruise_speed", struct.pack("<H", 5000))  # 50 m/s (~97 kt)
    print("  set: nav_fw_cruise_speed=5000 cm/s (~97 kt, clear of c172p stall)")

    # --- GPS: required, not optional here -----------------------------------
    # The wind estimator's Z-axis math reads posEstimator.gps.vel.z (fed from
    # gpsSol.velNED[Z] via HITL injection) and is hard-gated on
    # gpsSol.flags.validVelNE/validVelD and isGPSHeadingValid() -- see
    # wind_estimator.c:125. Unlike the quaternion-attitude-hold bench example
    # (which deliberately skips GPS injection to avoid biasing its fine
    # attitude-hold test), THIS test requires GPS every step.
    msp.enable_feature(FEATURE_GPS)
    msp.set_setting("gps_provider", struct.pack("<B", 1))       # MSP-driven
    print("  enabled FEATURE_GPS, gps_provider=MSP")

    # Standard airplane servo mixer (S1 aileron, S2 elevator, S3 rudder) --
    # without this isMixerUsingServos() is false and the MSP_SIMULATOR
    # reply's stabilized outputs stay 0 (see jsbsim-sitl-testing skill).
    msp.set_servo_mixer_rule(0, 0, 0)   # servo 0 <- stabilized roll
    msp.set_servo_mixer_rule(1, 1, 1)   # servo 1 <- stabilized pitch
    msp.set_servo_mixer_rule(2, 2, 2)   # servo 2 <- stabilized yaw
    print("  set servo mixer: S1<-roll, S2<-pitch, S3<-yaw")

    msp.set_mode_range(0, PERM_ARM, CH_ARM - 4, 1700, 2100)
    msp.set_mode_range(1, PERM_ANGLE, CH_ANGLE - 4, 1700, 2100)
    print(f"  mode ranges: ARM on AUX{CH_ARM - 4 + 1}, ANGLE on AUX{CH_ANGLE - 4 + 1} (PWM 1700-2100)")

    # --- Blackbox: FILE device, no BOXBLACKBOX mode range configured -> ----
    # blackboxModeActivationConditionPresent stays false -> logging runs for
    # the whole armed period once blackboxStart() fires on arm (fc_core.c:927,
    # blackbox.c:2399). rate_num/denom = 1/1 logs every eligible iteration,
    # giving the best chance of catching each wind[] slow-frame change
    # (writeSlowFrameIfNeeded() logs a fresh S-frame whenever the field
    # actually changes, blackbox.c:1541).
    msp.enable_feature(FEATURE_BLACKBOX)
    msp.set_setting("blackbox_device", struct.pack("<B", BLACKBOX_DEVICE_FILE))
    msp.set_setting("blackbox_rate_num", struct.pack("<H", 1))
    msp.set_setting("blackbox_rate_denom", struct.pack("<H", 1))
    print("  enabled FEATURE_BLACKBOX, blackbox_device=FILE, rate=1/1")

    msp.save_eeprom()
    print()
    print("Provisioned and saved to EEPROM.")
    print("EEPROM changes require a reboot to take effect:")
    print("  pkill -9 SITL.elf")
    print("  (relaunch SITL.elf from the directory you want the blackbox .TXT written to)")
    print()
    print("Then run: python3 wind_z_sign_test.py")


if __name__ == "__main__":
    provision()
