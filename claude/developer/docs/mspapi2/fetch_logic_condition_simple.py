#!/usr/bin/env python3
"""
Simple example: Fetch a single INAV Logic Condition using MSP2_INAV_LOGIC_CONDITIONS_SINGLE

This demonstrates how to use mspapi2 to fetch MSP messages that don't have
convenience methods yet, by using the dynamic codec directly.

To discover what fields a message has, see:
    claude/developer/how-to-discover-msp-fields.md
Or run:
    python3 claude/developer/msp_introspection_tools.py
"""

from mspapi2 import MSPApi, InavMSP
from mspapi2.lib import InavEnums

# Optional: Discover what fields this message has
# Uncomment to see field details:
# from msp_introspection_tools import print_message_info
# print_message_info(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE)


def fetch_logic_condition(api: MSPApi, index: int) -> dict:
    """
    Fetch a single logic condition by index.

    This shows the pattern for accessing ANY MSP message using the codec:
    1. Pack request data using api._pack_request(code, data_dict)
    2. Send request using api._request(code, payload)
    3. Process reply (convert enums, format values, etc.)
    """
    # Step 1: Pack the request with our condition index
    request_payload = api._pack_request(
        InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE,
        {"conditionIndex": index}
    )

    # Step 2: Send the request
    info, reply = api._request(
        InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE,
        request_payload
    )

    # Step 3: Process the reply (convert to enums for readability)
    condition = {
        "enabled": bool(reply["enabled"]),
        "activatorId": reply["activatorId"],
        "operation": InavEnums.logicOperation_e(reply["operation"]),
        "operandAType": InavEnums.logicOperandType_e(reply["operandAType"]),
        "operandAValue": reply["operandAValue"],
        "operandBType": InavEnums.logicOperandType_e(reply["operandBType"]),
        "operandBValue": reply["operandBValue"],
        "flags": reply["flags"],
    }

    print(f"Request info: {info.get('latency_ms')}ms latency")
    return condition


def main():
    # Connect to flight controller
    with MSPApi(port="/dev/ttyACM0", baudrate=115200) as api:
        # Fetch logic condition #0
        condition = fetch_logic_condition(api, index=0)

        # Display result
        print(f"\nLogic Condition #0:")
        print(f"  Enabled:    {condition['enabled']}")
        print(f"  Operation:  {condition['operation'].name}")
        print(f"  Operand A:  {condition['operandAType'].name} = {condition['operandAValue']}")
        print(f"  Operand B:  {condition['operandBType'].name} = {condition['operandBValue']}")


if __name__ == "__main__":
    main()
