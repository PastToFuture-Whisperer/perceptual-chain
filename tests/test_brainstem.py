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
Tests for Brainstem state machine transitions, safety boundary interlocks, and recovery pathways.
"""

import pytest
from perceptual_chain import Brainstem, BrainstemState, SafetyBoundary, InterlockViolation

__version__ = "1.0.0"


@pytest.fixture
def sample_boundary() -> SafetyBoundary:
    return SafetyBoundary(
        min_limits={"angle": -180.0, "speed": 0.0},
        max_limits={"angle": 180.0, "speed": 100.0},
    )


def test_brainstem_initial_state(sample_boundary: SafetyBoundary):
    brainstem = Brainstem(safety_boundary=sample_boundary)
    assert brainstem.current_state == BrainstemState.READY


def test_successful_execution_cycle(sample_boundary: SafetyBoundary):
    brainstem = Brainstem(safety_boundary=sample_boundary)

    def dummy_executor(action: str, params: dict):
        assert brainstem.current_state == BrainstemState.EXECUTING
        return {"status": "ok"}

    result = brainstem.execute_raw("move", {"angle": 45.0, "speed": 10.0}, dummy_executor)
    assert result == {"status": "ok"}
    assert brainstem.current_state == BrainstemState.READY


def test_safety_boundary_violation_triggers_emergency_stop(sample_boundary: SafetyBoundary):
    brainstem = Brainstem(safety_boundary=sample_boundary)

    def dummy_executor(action: str, params: dict):
        return {}

    with pytest.raises(InterlockViolation) as exc_info:
        brainstem.execute_raw("move", {"angle": 200.0, "speed": 10.0}, dummy_executor)

    assert "exceeds max boundary" in str(exc_info.value)
    assert brainstem.current_state == BrainstemState.EMERGENCY_STOP


def test_emergency_stop_recovery_and_reset(sample_boundary: SafetyBoundary):
    brainstem = Brainstem(safety_boundary=sample_boundary)
    brainstem.trigger_emergency_stop("Manual test stop")
    assert brainstem.current_state == BrainstemState.EMERGENCY_STOP

    with pytest.raises(InterlockViolation):
        b2 = Brainstem(safety_boundary=sample_boundary)
        b2.reset()

    brainstem.reset()
    assert brainstem.current_state == BrainstemState.READY