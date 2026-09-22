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
Perceptual Chain: Sub-Cortex Protocol for Type-Safe and Deterministic LLM Execution.
"""

from .brainstem import Brainstem, BrainstemState, SafetyBoundary, InterlockViolation
from .subcortex import SubCortexBridge, PerceptualCommand, CommandValidationError
from .loop import PredictiveErrorLoop, ExecutionResult, SensorKeyMismatchError

__version__ = "1.0.0"
__all__ = [
    "Brainstem",
    "BrainstemState",
    "SafetyBoundary",
    "InterlockViolation",
    "SubCortexBridge",
    "PerceptualCommand",
    "CommandValidationError",
    "PredictiveErrorLoop",
    "ExecutionResult",
    "SensorKeyMismatchError",
]
