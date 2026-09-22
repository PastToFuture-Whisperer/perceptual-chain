#!/usr/bin/env python3
# Copyright (c) 2026 PastToFuture-Whisperer
# SPDX-License-Identifier: MIT
#
# Version: 1.0.0 (Release)
#
# This program is a byproduct of the advanced profile optimization research 
# mentioned in the documentation; those core features are explicitly excluded 
# from this repository and implemented separately.

"""
Example 03: Autonomous Drone Emergency Recovery under Sensor Noise & Loss.
"""

from typing import Dict, Any, Tuple
from perceptual_chain import (
    Brainstem,
    BrainstemState,
    SafetyBoundary,
    SubCortexBridge,
    PredictiveErrorLoop,
)

__version__ = "1.0.0"


class FlightController:
    def __init__(self):
        self.hovering_active = False

    def execute_thrust(
        self, action_name: str, parameters: Dict[str, float]
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        actual_sensor_feedback = {
            "pitch_deg": 12.5,
            "roll_deg": -8.1,
        }
        telemetry = {"flight_mode": "MANUAL_SPIKE", "signal_dbm": -95}
        return telemetry, actual_sensor_feedback


def main():
    print("=== Perceptual Chain: Example 03 - Drone Emergency Recovery ===")

    boundary = SafetyBoundary(
        min_limits={"pitch_deg": -30.0, "roll_deg": -30.0, "thrust_n": 0.0},
        max_limits={"pitch_deg": 30.0, "roll_deg": 30.0, "thrust_n": 100.0},
    )

    brainstem = Brainstem(safety_boundary=boundary)
    bridge = SubCortexBridge(min_confidence_threshold=0.80)
    loop = PredictiveErrorLoop(bridge=bridge, brainstem=brainstem, error_tolerance=0.05)
    drone_fc = FlightController()

    llm_command = {
        "action_name": "adjust_attitude",
        "parameters": {
            "pitch_deg": 2.0,
            "roll_deg": 0.0,
            "thrust_n": 45.0,
        },
        "confidence": 0.88,
    }

    predicted_state = {"pitch_deg": 2.0, "roll_deg": 0.0, "altitude_m": 15.0}

    print("\n[Input] LLM Trajectory Guidance Command:")
    print(llm_command)

    result = loop.step(
        raw_llm_output=llm_command,
        predicted_state=predicted_state,
        executor=drone_fc.execute_thrust,
    )

    print("\n[Output] Safety Protocol Response:")
    print(f"  Execution Status: {result.success}")
    print(f"  Brainstem State: {brainstem.current_state.name}")
    print(f"  Captured Interlock Message: {result.error_message}")
    
    if not result.success and brainstem.current_state == BrainstemState.EMERGENCY_STOP:
        print("\n[Flight Recorder] Brainstem locked in EMERGENCY_STOP due to Sensor Blindness.")
        print("  --> Interlock Engaged: Initiating Fail-Safe Hardware Hovering...")
        drone_fc.hovering_active = True
        print(f"  --> Hardware Hovering Active: {drone_fc.hovering_active}")


if __name__ == "__main__":
    main()