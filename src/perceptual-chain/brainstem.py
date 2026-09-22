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
Brainstem Module: Deterministic Finite State Machine (FSM) & Hard Safety Boundaries.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, Callable, Set

__version__ = "1.0.0"


class BrainstemState(Enum):
    INIT = auto()
    READY = auto()
    EXECUTING = auto()
    EVALUATING = auto()
    EMERGENCY_STOP = auto()


class InterlockViolation(Exception):
    """Raised when a physical command violates hard safety boundaries or FSM rules."""
    pass


@dataclass(frozen=True)
class SafetyBoundary:
    """
    Defines strict physical limits (e.g., joint angle limits, velocity caps, transfer amounts).
    """
    min_limits: Dict[str, float]
    max_limits: Dict[str, float]

    def validate(self, parameters: Dict[str, float]) -> None:
        for key, value in parameters.items():
            if key in self.min_limits and value < self.min_limits[key]:
                raise InterlockViolation(
                    f"Parameter '{key}' value {value} is below min boundary {self.min_limits[key]}"
                )
            if key in self.max_limits and value > self.max_limits[key]:
                raise InterlockViolation(
                    f"Parameter '{key}' value {value} exceeds max boundary {self.max_limits[key]}"
                )


class Brainstem:
    """
    Brainstem represents the lowest, deterministic layer that executes physical actions.
    Guarantees execution safety via state machine enforcement and boundary checking.
    """

    def __init__(self, safety_boundary: SafetyBoundary):
        self._state: BrainstemState = BrainstemState.INIT
        self._boundary: SafetyBoundary = safety_boundary
        
        self._state_transitions: Dict[BrainstemState, Set[BrainstemState]] = {
            BrainstemState.INIT: {BrainstemState.READY, BrainstemState.EMERGENCY_STOP},
            BrainstemState.READY: {BrainstemState.EXECUTING, BrainstemState.EMERGENCY_STOP},
            BrainstemState.EXECUTING: {BrainstemState.EVALUATING, BrainstemState.EMERGENCY_STOP},
            BrainstemState.EVALUATING: {BrainstemState.READY, BrainstemState.EMERGENCY_STOP},
            BrainstemState.EMERGENCY_STOP: {BrainstemState.INIT},
        }
        self._transition_to(BrainstemState.READY)

    @property
    def current_state(self) -> BrainstemState:
        return self._state

    def _transition_to(self, new_state: BrainstemState) -> None:
        if self._state != BrainstemState.INIT and new_state not in self._state_transitions[self._state]:
            raise InterlockViolation(
                f"Invalid FSM state transition: {self._state.name} -> {new_state.name}"
            )
        self._state = new_state

    def execute_raw(
        self, action_name: str, parameters: Dict[str, float], executor: Callable[[str, Dict[str, float]], Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executes a deterministic payload through hard safety validation and FSM management.
        """
        if self._state != BrainstemState.READY:
            raise InterlockViolation(f"Cannot execute command in state {self._state.name}")

        try:
            self._boundary.validate(parameters)
            self._transition_to(BrainstemState.EXECUTING)
            result = executor(action_name, parameters)
            self._transition_to(BrainstemState.EVALUATING)
            self._transition_to(BrainstemState.READY)
            return result

        except Exception as e:
            self.trigger_emergency_stop(reason=str(e))
            raise

    def trigger_emergency_stop(self, reason: str = "Unknown") -> None:
        """Forces the state machine into EMERGENCY_STOP state via state transition rule."""
        if self._state != BrainstemState.EMERGENCY_STOP:
            self._transition_to(BrainstemState.EMERGENCY_STOP)

    def reset(self) -> None:
        """Resets state machine from EMERGENCY_STOP back to INIT and then READY."""
        if self._state != BrainstemState.EMERGENCY_STOP:
            raise InterlockViolation(f"Cannot reset Brainstem from state {self._state.name}. Must be in EMERGENCY_STOP.")
        self._transition_to(BrainstemState.INIT)
        self._transition_to(BrainstemState.READY)