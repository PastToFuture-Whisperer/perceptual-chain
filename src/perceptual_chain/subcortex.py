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
SubCortex Module: Type-Safe Bridge and Strict Parsing Layer between LLM and Brainstem.
"""

from typing import Dict, Any, Type, TypeVar
from pydantic import BaseModel, Field, ConfigDict, ValidationError, field_validator

__version__ = "1.0.0"


class CommandValidationError(Exception):
    """Raised when an LLM command fails strict type schema or semantic check."""
    pass


class PerceptualCommand(BaseModel):
    """
    Base Schema for all LLM-generated commands.
    Extra fields are forbidden, but int-to-float coercion is allowed for numerical parameters.
    """
    model_config = ConfigDict(extra="forbid")

    action_name: str = Field(..., description="Target low-level action name")
    parameters: Dict[str, float] = Field(..., description="Numerical parameters for physical execution")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score estimated by Cortex")

    @field_validator("parameters", mode="before")
    @classmethod
    def coerce_int_to_float(cls, v: Any) -> Dict[str, float]:
        """Allows standard integer inputs from LLM JSON to be safely coerced to float."""
        if not isinstance(v, dict):
            raise ValueError("Parameters must be a key-value dictionary.")
        coerced = {}
        for key, val in v.items():
            if isinstance(val, (int, float)):
                coerced[key] = float(val)
            else:
                raise ValueError(f"Parameter '{key}' value {val} is not a valid number.")
        return coerced


TCmd = TypeVar("TCmd", bound=PerceptualCommand)


class SubCortexBridge:
    """
    SubCortexBridge filters, validates, and normalizes unstructured or structured
    LLM outputs before presenting them to the Brainstem.
    """

    def __init__(self, min_confidence_threshold: float = 0.80):
        self.min_confidence_threshold = min_confidence_threshold

    def parse_and_validate(self, raw_input: Dict[str, Any], schema_class: Type[TCmd]) -> TCmd:
        """
        Validates raw payload against a Pydantic schema with strict boundary handling.
        """
        try:
            command = schema_class.model_validate(raw_input)
        except ValidationError as e:
            raise CommandValidationError(f"Schema validation failed: {e}") from e

        if command.confidence < self.min_confidence_threshold:
            raise CommandValidationError(
                f"Confidence score {command.confidence:.2f} is below safety threshold {self.min_confidence_threshold:.2f}"
            )

        return command
