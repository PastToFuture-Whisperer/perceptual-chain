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
Tests for PredictiveErrorLoop end-to-end execution, residual error calculation, and sensor loss interlocks.
"""

import pytest
from perceptual_chain import (
    Brainstem,
    BrainstemState,
    SafetyBoundary,
    SubCortexBridge,
    PredictiveErrorLoop,
)

__version__ = "1.0.0"


@pytest.fixture
def setup_loop():
    boundary = SafetyBoundary(
        min_limits={"x": 0.0, "y": 0.0},
        max_limits={"x": 100.0, "y": 100.0},
    )
    brainstem = Brainstem(safety_boundary=boundary)
    bridge = SubCortexBridge(min_confidence_threshold=0.80)
    loop = PredictiveErrorLoop(bridge=bridge, brainstem=brainstem, error_tolerance=0.10)
    return loop, brainstem


def test_successful_loop_step(setup_loop):
    loop, brainstem = setup_loop

    raw_llm = {
        "action_name": "move_to",
        "parameters": {"x": 10.0, "y": 20.0},
        "confidence": 0.90,
    }
    predicted = {"x": 10.0, "y": 20.0}

    def mock_executor(action, params):
        return {"status": "ok"}, {"x": 10.05, "y": 19.98}

    result = loop.step(raw_llm, predicted, mock_executor)
    assert result.success is True
    assert result.error_message is None
    assert brainstem.current_state == BrainstemState.READY


def test_residual_error_tolerance_exceeded(setup_loop):
    loop, brainstem = setup_loop

    raw_llm = {
        "action_name": "move_to",
        "parameters": {"x": 10.0, "y": 20.0},
        "confidence": 0.90,
    }
    predicted = {"x": 10.0, "y": 20.0}

    def mock_executor(action, params):
        return {"status": "ok"}, {"x": 15.0, "y": 20.0}

    result = loop.step(raw_llm, predicted, mock_executor)
    assert result.success is False
    assert "exceeded tolerance" in result.error_message


def test_sensor_key_mismatch_forces_emergency_stop(setup_loop):
    loop, brainstem = setup_loop

    raw_llm = {
        "action_name": "move_to",
        "parameters": {"x": 10.0, "y": 20.0},
        "confidence": 0.90,
    }
    predicted = {"x": 10.0, "y": 20.0, "z": 5.0}

    def mock_executor(action, params):
        return {"status": "ok"}, {"x": 10.0, "y": 20.0}

    result = loop.step(raw_llm, predicted, mock_executor)
    assert result.success is False
    assert "[Sensor Feedback Interlock]" in result.error_message
    assert brainstem.current_state == BrainstemState.EMERGENCY_STOP