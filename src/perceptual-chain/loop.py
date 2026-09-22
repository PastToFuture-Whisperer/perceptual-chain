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
Predictive Error Feedback Loop: Closed-loop correction framework (Perceptual Cycle).
"""

from dataclasses import dataclass
from typing import Dict, Any, Callable, Tuple, Optional
import math

from .brainstem import Brainstem, InterlockViolation
from .subcortex import SubCortexBridge, PerceptualCommand, CommandValidationError

__version__ = "1.0.0"


class SensorKeyMismatchError(Exception):
    """Raised when sensor actual state lacks keys present in predicted state."""
    pass


@dataclass
class ExecutionResult:
    success: bool
    predicted_state: Dict[str, float]
    actual_state: Dict[str, float]
    error_vector: Dict[str, float]
    raw_output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class PredictiveErrorLoop:
    """
    Implements the closed loop (Predict-Execute-Observe-Feedback).
    Calculates residual sensory error between prediction and real feedback.
    """

    def __init__(
        self,
        bridge: SubCortexBridge,
        brainstem: Brainstem,
        error_tolerance: float = 0.05
    ):
        self.bridge = bridge
        self.brainstem = brainstem
        self.error_tolerance = error_tolerance

    def calculate_residual_error(
        self, predicted: Dict[str, float], actual: Dict[str, float]
    ) -> Tuple[Dict[str, float], float]:
        """
        Calculates element-wise differences and normalized Euclidean norm.
        Raises SensorKeyMismatchError if any key in predicted is missing in actual.
        """
        error_vector: Dict[str, float] = {}
        sum_sq = 0.0

        for key, pred_val in predicted.items():
            if key not in actual:
                raise SensorKeyMismatchError(
                    f"Key mismatch: Predicted key '{key}' not found in actual sensor state feedback."
                )
            act_val = actual[key]
            err = act_val - pred_val
            error_vector[key] = err
            sum_sq += err ** 2

        l2_norm = math.sqrt(sum_sq)
        return error_vector, l2_norm

    def step(
        self,
        raw_llm_output: Dict[str, Any],
        predicted_state: Dict[str, float],
        executor: Callable[[str, Dict[str, float]], Tuple[Dict[str, Any], Dict[str, float]]]
    ) -> ExecutionResult:
        """
        Executes one full cycle of the Perceptual Chain with distinct exception pathways.
        """
        # 1. Sub-Cortex Schema & Confidence Guard
        try:
            command = self.bridge.parse_and_validate(raw_llm_output, PerceptualCommand)
        except CommandValidationError as e:
            return ExecutionResult(
                success=False,
                predicted_state=predicted_state,
                actual_state={},
                error_vector={},
                error_message=f"[Sub-Cortex Gate Blocked] {e}"
            )

        # 2. Brainstem Execution with Hard Boundary Check
        try:
            def brainstem_executor(act: str, params: Dict[str, float]) -> Dict[str, Any]:
                raw_res, actual_st = executor(act, params)
                return {"raw": raw_res, "actual_state": actual_st}

            res = self.brainstem.execute_raw(
                action_name=command.action_name,
                parameters=command.parameters,
                executor=brainstem_executor
            )

            actual_state = res["actual_state"]
            raw_output = res["raw"]

        except InterlockViolation as e:
            return ExecutionResult(
                success=False,
                predicted_state=predicted_state,
                actual_state={},
                error_vector={},
                error_message=f"[Brainstem Interlock Triggered] {e}"
            )
        except Exception as e:
            self.brainstem.trigger_emergency_stop(reason=f"Unhandled Execution Exception: {e}")
            return ExecutionResult(
                success=False,
                predicted_state=predicted_state,
                actual_state={},
                error_vector={},
                error_message=f"[System Internal Error] Unhandled Exception: {type(e).__name__} - {e}"
            )

        # 3. Residual Error Calculation & Sensor Mismatch Guard
        try:
            error_vector, l2_norm = self.calculate_residual_error(predicted_state, actual_state)
        except SensorKeyMismatchError as e:
            self.brainstem.trigger_emergency_stop(reason=f"Sensor Mismatch / Loss: {e}")
            return ExecutionResult(
                success=False,
                predicted_state=predicted_state,
                actual_state=actual_state,
                error_vector={},
                error_message=f"[Sensor Feedback Interlock] {e}"
            )

        success = l2_norm <= self.error_tolerance

        return ExecutionResult(
            success=success,
            predicted_state=predicted_state,
            actual_state=actual_state,
            error_vector=error_vector,
            raw_output=raw_output,
            error_message=None if success else f"Prediction discrepancy L2-Norm ({l2_norm:.4f}) exceeded tolerance ({self.error_tolerance:.4f})"
        )