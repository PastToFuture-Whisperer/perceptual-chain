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
Example 01: Robotics Arm Trajectory Control with Aiki-Damping Interlock.
"""

from typing import Dict, Any, Tuple

from perceptual_chain import (
    Brainstem,
    SafetyBoundary,
    SubCortexBridge,
    PredictiveErrorLoop,
)

__version__ = "1.0.0"


class AikiDampingArmExecutor:
    def __init__(self, max_angular_velocity: float = 1.2):
        self.max_velocity = max_angular_velocity
        self.current_angles = {"joint_1": 0.0, "joint_2": 0.0, "joint_3": 0.0}

    def execute_trajectory(
        self, action_name: str, parameters: Dict[str, float]
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        max_requested_vel = max(
            abs(parameters.get("vel_j1", 0.0)),
            abs(parameters.get("vel_j2", 0.0)),
            abs(parameters.get("vel_j3", 0.0)),
        )

        damping_factor = 1.0
        if max_requested_vel > self.max_velocity:
            damping_factor = self.max_velocity / max_requested_vel

        new_state = {}
        for i in range(1, 4):
            key = f"joint_{i}"
            vel_key = f"vel_j{i}"
            delta_angle = parameters.get(vel_key, 0.0) * damping_factor * 0.1
            self.current_angles[key] += delta_angle
            new_state[key] = round(self.current_angles[key], 4)

        telemetry = {
            "status": "COMPLETED",
            "damping_applied": damping_factor < 1.0,
            "applied_damping_factor": round(damping_factor, 4),
        }
        return telemetry, new_state


def main():
    print("=== Perceptual Chain: Example 01 - Robotics Arm Control ===")

    boundary = SafetyBoundary(
        min_limits={"vel_j1": -2.0, "vel_j2": -2.0, "vel_j3": -2.0},
        max_limits={"vel_j1": 2.0, "vel_j2": 2.0, "vel_j3": 2.0},
    )

    brainstem = Brainstem(safety_boundary=boundary)
    bridge = SubCortexBridge(min_confidence_threshold=0.85)
    loop = PredictiveErrorLoop(bridge=bridge, brainstem=brainstem, error_tolerance=0.08)
    arm_hardware = AikiDampingArmExecutor(max_angular_velocity=1.2)

    raw_llm_command = {
        "action_name": "move_joint_velocity",
        "parameters": {
            "vel_j1": 1.8,
            "vel_j2": 0.5,
            "vel_j3": -0.2,
        },
        "confidence": 0.92,
    }

    predicted_state = {"joint_1": 0.18, "joint_2": 0.05, "joint_3": -0.02}

    print("\n[Input] Cortex Raw Payload:")
    print(raw_llm_command)

    result = loop.step(
        raw_llm_output=raw_llm_command,
        predicted_state=predicted_state,
        executor=arm_hardware.execute_trajectory,
    )

    print("\n[Output] Execution Result:")
    print(f"  Loop Success (Discrepancy <= Tolerance): {result.success}")
    print(f"  Predicted State by Cortex: {result.predicted_state}")
    print(f"  Actual Damped State: {result.actual_state}")
    print(f"  Residual Error Vector: {result.error_vector}")
    
    if result.raw_output and result.raw_output.get("raw", {}).get("damping_applied"):
        print("\n[Telemetry Notice] 'Aiki-Damping' active in physical layer.")
        print("  --> Physical crash avoided via kinetic dissipation.")
        print("  --> Residual error passed back to Cortex for iterative trajectory re-planning.")


if __name__ == "__main__":
    main()