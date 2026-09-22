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
Example 02: Financial Execution Guard against Agentic Hallucination.
"""

from typing import Dict, Any, Tuple
from perceptual_chain import (
    Brainstem,
    SafetyBoundary,
    SubCortexBridge,
    PredictiveErrorLoop,
)

__version__ = "1.0.0"


class MockBankingCore:
    def __init__(self, initial_capital: float = 100000.0):
        self.capital = initial_capital

    def execute_transfer(
        self, action_name: str, parameters: Dict[str, float]
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        amount = parameters.get("transfer_amount", 0.0)
        self.capital -= amount
        
        telemetry = {"status": "SETTLED", "transferred": amount}
        state_feedback = {"remaining_capital": round(self.capital, 2)}
        return telemetry, state_feedback


def main():
    print("=== Perceptual Chain: Example 02 - Financial Agent Guard ===")

    boundary = SafetyBoundary(
        min_limits={"transfer_amount": 10.0},
        max_limits={"transfer_amount": 10000.0},
    )

    brainstem = Brainstem(safety_boundary=boundary)
    bridge = SubCortexBridge(min_confidence_threshold=0.90)
    loop = PredictiveErrorLoop(bridge=bridge, brainstem=brainstem, error_tolerance=0.01)
    bank_core = MockBankingCore(initial_capital=100000.0)

    hallucinated_llm_payload = {
        "action_name": "execute_transfer",
        "parameters": {
            "transfer_amount": 80000
        },
        "confidence": 0.95,
    }

    predicted_state = {"remaining_capital": 20000.0}

    print("\n[Input] LLM Agent High-Risk Transfer Request:")
    print(hallucinated_llm_payload)

    result = loop.step(
        raw_llm_output=hallucinated_llm_payload,
        predicted_state=predicted_state,
        executor=bank_core.execute_transfer,
    )

    print("\n[Output] Interlock Reaction:")
    print(f"  Execution Allowed: {result.success}")
    print(f"  Brainstem State: {brainstem.current_state.name}")
    print(f"  Error Log: {result.error_message}")

    print("\n[Recovery] Resetting Brainstem FSM back to READY state...")
    brainstem.reset()
    print(f"  Current FSM State after Reset: {brainstem.current_state.name}")


if __name__ == "__main__":
    main()