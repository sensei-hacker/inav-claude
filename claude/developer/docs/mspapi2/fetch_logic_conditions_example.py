#!/usr/bin/env python3
"""
Example script demonstrating how to fetch INAV Logic Conditions using mspapi2.

This demonstrates three approaches:
1. High-level convenience method: get_logic_conditions() - fetches all conditions
2. Low-level codec access: MSP2_INAV_LOGIC_CONDITIONS_SINGLE - fetch one condition
3. Direct request using _request() - for messages without convenience methods

Logic Conditions are part of INAV's Programming Framework, allowing you to
create conditional logic for autonomous behaviors (requires USE_PROGRAMMING_FRAMEWORK).
"""

from __future__ import annotations
import argparse
from typing import Any, Dict, Tuple

from mspapi2 import MSPApi, InavMSP
from mspapi2.lib import InavEnums


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch INAV Logic Conditions using mspapi2"
    )
    parser.add_argument(
        "--port",
        default="/dev/ttyACM0",
        help="Serial device path (ignored if --tcp is used)",
    )
    parser.add_argument(
        "--baudrate", type=int, default=115200, help="Serial baud rate"
    )
    parser.add_argument(
        "--tcp",
        metavar="HOST:PORT",
        help="Connect using TCP socket instead of serial, e.g. localhost:5760",
    )
    parser.add_argument(
        "--condition-index",
        type=int,
        default=0,
        help="Index of specific condition to fetch (0-based)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Fetch all logic conditions using convenience method",
    )
    return parser.parse_args()


def format_operand(operand_type: InavEnums.logicOperandType_e, value: int) -> str:
    """Format an operand for display based on its type."""
    type_name = operand_type.name.replace("LOGIC_CONDITION_OPERAND_TYPE_", "")

    if operand_type == InavEnums.logicOperandType_e.LOGIC_CONDITION_OPERAND_TYPE_VALUE:
        return f"{type_name}({value})"
    elif operand_type == InavEnums.logicOperandType_e.LOGIC_CONDITION_OPERAND_TYPE_RC_CHANNEL:
        return f"{type_name}(CH{value})"
    elif operand_type == InavEnums.logicOperandType_e.LOGIC_CONDITION_OPERAND_TYPE_FLIGHT_MODE:
        return f"{type_name}(MODE_{value})"
    elif operand_type == InavEnums.logicOperandType_e.LOGIC_CONDITION_OPERAND_TYPE_LC:
        return f"{type_name}(LC{value})"
    elif operand_type == InavEnums.logicOperandType_e.LOGIC_CONDITION_OPERAND_TYPE_GVAR:
        return f"{type_name}(GVAR{value})"
    else:
        return f"{type_name}({value})"


def print_condition(index: int, condition: Dict[str, Any]) -> None:
    """Pretty-print a logic condition."""
    print(f"\n{'='*70}")
    print(f"Logic Condition #{index}")
    print(f"{'='*70}")
    print(f"  Enabled:     {condition['enabled']}")
    print(f"  Activator:   {condition.get('activatorId', 'None')}")

    # Operation
    operation = condition["operation"]
    if isinstance(operation, InavEnums.logicOperation_e):
        op_name = operation.name.replace("LOGIC_CONDITION_", "")
        print(f"  Operation:   {op_name} ({operation.value})")
    else:
        print(f"  Operation:   {operation}")

    # Operand A
    operand_a_type = condition["operandAType"]
    operand_a_value = condition["operandAValue"]
    print(f"  Operand A:   {format_operand(operand_a_type, operand_a_value)}")

    # Operand B
    operand_b_type = condition["operandBType"]
    operand_b_value = condition["operandBValue"]
    print(f"  Operand B:   {format_operand(operand_b_type, operand_b_value)}")

    # Flags
    flags = condition.get("flags", [])
    if flags:
        flag_names = [
            f.name.replace("LOGIC_CONDITION_FLAG_", "") for f in flags
        ]
        print(f"  Flags:       {', '.join(flag_names)}")
    else:
        print(f"  Flags:       None")

    print(f"{'='*70}")


def fetch_single_condition_direct(
    api: MSPApi, condition_index: int
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Fetch a single logic condition using MSP2_INAV_LOGIC_CONDITIONS_SINGLE.

    This demonstrates the low-level approach using _request() for messages
    that don't have convenience methods.

    Args:
        api: MSPApi instance (must be open)
        condition_index: Index of condition to fetch (0-based)

    Returns:
        (info_dict, condition_dict)
    """
    # Pack the request payload with the condition index
    request_payload = api._pack_request(
        InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE, {"conditionIndex": condition_index}
    )

    # Send request and get reply
    info, reply = api._request(
        InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE, request_payload
    )

    # Convert enums to make them readable
    condition = {
        "enabled": bool(reply["enabled"]),
        "activatorId": None if reply["activatorId"] == 0xFF else reply["activatorId"],
        "operation": InavEnums.logicOperation_e(reply["operation"]),
        "operandAType": InavEnums.logicOperandType_e(reply["operandAType"]),
        "operandAValue": reply["operandAValue"],
        "operandBType": InavEnums.logicOperandType_e(reply["operandBType"]),
        "operandBValue": reply["operandBValue"],
        "flags": [
            flag
            for flag in InavEnums.logicConditionFlags_e
            if reply["flags"] & flag.value
        ],
    }

    return info, condition


def main() -> None:
    args = parse_args()

    # Setup connection
    port = None if args.tcp else args.port
    tcp_endpoint = args.tcp if args.tcp else None

    print(f"\n{'='*70}")
    print("INAV Logic Conditions Fetch Example")
    print(f"{'='*70}")

    if tcp_endpoint:
        print(f"Connecting to: TCP {tcp_endpoint}")
    else:
        print(f"Connecting to: {port} @ {args.baudrate} baud")

    # Create and open API connection
    with MSPApi(
        port=port,
        baudrate=args.baudrate,
        tcp_endpoint=tcp_endpoint,
    ) as api:
        # Get FC info first
        print("\nFetching flight controller info...")
        _, fc_variant = api.get_fc_variant()
        _, board_info = api.get_board_info()
        print(f"  FC Variant: {fc_variant['fcVariantIdentifier']}")
        print(f"  Board:      {board_info['boardIdentifier']}")

        if args.all:
            # Approach 1: Use convenience method to get all conditions
            print("\n" + "="*70)
            print("Using convenience method: api.get_logic_conditions()")
            print("="*70)

            info, conditions = api.get_logic_conditions()

            print(f"\nFetched {len(conditions)} logic conditions")
            print(f"Latency: {info.get('latency_ms', 'N/A')} ms")

            for i, condition in enumerate(conditions):
                if condition["enabled"]:  # Only print enabled conditions
                    print_condition(i, condition)

            if not any(c["enabled"] for c in conditions):
                print("\nNo enabled logic conditions found.")

        else:
            # Approach 2: Fetch single condition using MSP2_INAV_LOGIC_CONDITIONS_SINGLE
            print("\n" + "="*70)
            print("Using direct codec access: MSP2_INAV_LOGIC_CONDITIONS_SINGLE")
            print(f"Fetching condition index: {args.condition_index}")
            print("="*70)

            info, condition = fetch_single_condition_direct(api, args.condition_index)

            print(f"\nRequest completed:")
            print(f"  Latency:    {info.get('latency_ms', 'N/A')} ms")
            print(f"  Cached:     {info.get('cached', False)}")
            print(f"  Transport:  {info.get('transport', 'unknown')}")

            print_condition(args.condition_index, condition)

        print("\n" + "="*70)
        print("Complete!")
        print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
