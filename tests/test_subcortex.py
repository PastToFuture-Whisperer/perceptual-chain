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
Tests for SubCortexBridge validation gate, confidence thresholding, and Int/Float type coercion.
"""

import pytest
from perceptual_chain import SubCortexBridge, PerceptualCommand, CommandValidationError

__version__ = "1.0.0"


def test_valid_command_parsing():
    bridge = SubCortexBridge(min_confidence_threshold=0.80)
    raw_payload = {
        "action_name": "set_temperature",
        "parameters": {"target": 22.5},
        "confidence": 0.95,
    }

    cmd = bridge.parse_and_validate(raw_payload, PerceptualCommand)
    assert cmd.action_name == "set_temperature"
    assert cmd.parameters["target"] == 22.5
    assert cmd.confidence == 0.95


def test_int_to_float_coercion_for_llm_json():
    bridge = SubCortexBridge(min_confidence_threshold=0.80)
    raw_payload = {
        "action_name": "set_velocity",
        "parameters": {"speed": 50},
        "confidence": 0.88,
    }

    cmd = bridge.parse_and_validate(raw_payload, PerceptualCommand)
    assert isinstance(cmd.parameters["speed"], float)
    assert cmd.parameters["speed"] == 50.0


def test_confidence_threshold_rejection():
    bridge = SubCortexBridge(min_confidence_threshold=0.85)
    low_confidence_payload = {
        "action_name": "set_velocity",
        "parameters": {"speed": 10.0},
        "confidence": 0.60,
    }

    with pytest.raises(CommandValidationError) as exc_info:
        bridge.parse_and_validate(low_confidence_payload, PerceptualCommand)

    assert "Confidence score 0.60 is below safety threshold" in str(exc_info.value)


def test_forbidden_extra_fields():
    bridge = SubCortexBridge(min_confidence_threshold=0.80)
    invalid_payload = {
        "action_name": "set_velocity",
        "parameters": {"speed": 10.0},
        "confidence": 0.90,
        "unexpected_field": "hallucinated_data",
    }

    with pytest.raises(CommandValidationError) as exc_info:
        bridge.parse_and_validate(invalid_payload, PerceptualCommand)

    assert "Schema validation failed" in str(exc_info.value)