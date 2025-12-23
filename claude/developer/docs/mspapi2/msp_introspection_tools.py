#!/usr/bin/env python3
"""
MSP Message Introspection Tools for mspapi2

This module provides helper functions to discover what fields/parameters
are available in any MSP message, without reading the JSON schema manually.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from mspapi2 import MSPCodec, InavMSP


def get_message_info(code: InavMSP, codec: Optional[MSPCodec] = None) -> Dict[str, Any]:
    """
    Get detailed information about an MSP message.

    Args:
        code: The MSP code (e.g., InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE)
        codec: Optional MSPCodec instance (will create one if not provided)

    Returns:
        Dict with message details including field names, types, descriptions
    """
    if codec is None:
        # Path from claude/developer/ to mspapi2/mspapi2/lib/msp_messages.json
        schema_path = Path(__file__).parent.parent.parent.parent.parent / "mspapi2" / "mspapi2" / "lib" / "msp_messages.json"
        codec = MSPCodec.from_json_file(str(schema_path))

    spec = codec._specs[code]

    # Extract request fields
    request_fields = []
    for i, field in enumerate(spec.request.fields):
        request_fields.append({
            "name": field.get("name"),
            "type": field.get("ctype"),
            "description": field.get("desc", ""),
            "enum": field.get("enum"),
            "array": field.get("array", False),
            "array_size": field.get("array_size"),
        })

    # Extract reply fields
    reply_fields = []
    for i, field in enumerate(spec.reply.fields):
        reply_fields.append({
            "name": field.get("name"),
            "type": field.get("ctype"),
            "description": field.get("desc", ""),
            "enum": field.get("enum"),
            "array": field.get("array", False),
            "array_size": field.get("array_size"),
            "bitmask": field.get("bitmask", False),
        })

    return {
        "code": spec.code.value,
        "name": spec.name,
        "msp_version": spec.mspv,
        "request": {
            "fields": request_fields,
            "field_names": spec.request.field_names,
        },
        "reply": {
            "fields": reply_fields,
            "field_names": spec.reply.field_names,
        },
    }


def print_message_info(code: InavMSP, codec: Optional[MSPCodec] = None) -> None:
    """
    Pretty-print information about an MSP message.

    Args:
        code: The MSP code (e.g., InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE)
        codec: Optional MSPCodec instance
    """
    info = get_message_info(code, codec)

    print(f"\n{'='*70}")
    print(f"{info['name']}")
    print(f"{'='*70}")
    print(f"Code:        {info['code']}")
    print(f"MSP Version: {info['msp_version']}")

    # Request fields
    print(f"\n--- REQUEST ---")
    if info['request']['fields']:
        for field in info['request']['fields']:
            enum_str = f" (enum: {field['enum']})" if field['enum'] else ""
            array_str = f"[{field['array_size']}]" if field['array'] else ""
            print(f"  {field['name']:20s} {field['type']}{array_str:10s}{enum_str}")
            if field['description']:
                print(f"    → {field['description']}")
    else:
        print("  (no request payload)")

    # Reply fields
    print(f"\n--- REPLY ---")
    if info['reply']['fields']:
        for field in info['reply']['fields']:
            enum_str = f" (enum: {field['enum']})" if field['enum'] else ""
            array_str = f"[{field['array_size']}]" if field['array'] else ""
            bitmask_str = " (bitmask)" if field['bitmask'] else ""
            print(f"  {field['name']:20s} {field['type']}{array_str:10s}{enum_str}{bitmask_str}")
            if field['description']:
                print(f"    → {field['description']}")
    else:
        print("  (no reply payload)")

    print(f"{'='*70}\n")


def list_all_messages(filter_pattern: Optional[str] = None) -> List[str]:
    """
    List all available MSP messages.

    Args:
        filter_pattern: Optional string to filter message names (case-insensitive)

    Returns:
        List of message names
    """
    messages = list(InavMSP.__members__.keys())

    if filter_pattern:
        pattern = filter_pattern.upper()
        messages = [m for m in messages if pattern in m]

    return sorted(messages)


def print_all_messages(filter_pattern: Optional[str] = None) -> None:
    """
    Pretty-print all available MSP messages.

    Args:
        filter_pattern: Optional string to filter message names
    """
    messages = list_all_messages(filter_pattern)

    print(f"\nFound {len(messages)} MSP messages")
    if filter_pattern:
        print(f"(filtered by '{filter_pattern}')")
    print()

    for msg in messages:
        code = InavMSP[msg]
        print(f"  {msg:50s} = {code.value:5d}")


def get_schema_raw(message_name: str) -> Dict[str, Any]:
    """
    Get the raw schema entry for a message directly from JSON.

    Args:
        message_name: Name of the message (e.g., "MSP2_INAV_LOGIC_CONDITIONS_SINGLE")

    Returns:
        Dict with raw schema data
    """
    # Path from claude/developer/ to mspapi2/mspapi2/lib/msp_messages.json
    schema_path = Path(__file__).parent.parent.parent.parent.parent / "mspapi2" / "mspapi2" / "lib" / "msp_messages.json"
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    return schema.get(message_name, {})


def discover_reply_fields(reply: Dict[str, Any]) -> None:
    """
    Helper to discover what fields are in a reply dict.

    This is useful when you get a reply and want to see what's available.

    Args:
        reply: The reply dict from api._request()
    """
    print("\n--- Reply contains these fields ---")
    for key, value in reply.items():
        value_type = type(value).__name__
        if isinstance(value, (list, tuple)) and value:
            value_type = f"{value_type}[{type(value[0]).__name__}] (len={len(value)})"
        print(f"  {key:20s} : {value_type:20s} = {repr(value)[:50]}")


# Example usage functions

def example_introspect_message():
    """Example: How to introspect a specific message."""
    print("\n" + "="*70)
    print("Example: Introspecting MSP2_INAV_LOGIC_CONDITIONS_SINGLE")
    print("="*70)

    # Method 1: Use print_message_info helper
    print_message_info(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE)

    # Method 2: Get info dict programmatically
    info = get_message_info(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE)
    print("Field names in reply:")
    for name in info['reply']['field_names']:
        print(f"  - {name}")


def example_search_messages():
    """Example: Search for messages by pattern."""
    print("\n" + "="*70)
    print("Example: Search for LOGIC-related messages")
    print("="*70)

    print_all_messages("LOGIC")


def example_discover_runtime():
    """Example: Discover fields in a reply at runtime."""
    from mspapi2 import MSPApi

    print("\n" + "="*70)
    print("Example: Discover reply fields at runtime")
    print("="*70)

    # This would work if you have a flight controller connected
    # Uncomment to test:

    # with MSPApi(port="/dev/ttyACM0", baudrate=115200) as api:
    #     # Get a reply
    #     info, reply = api._request(InavMSP.MSP_API_VERSION)
    #
    #     # Discover what's in it
    #     discover_reply_fields(reply)

    print("\n(This example requires a connected flight controller)")
    print("Uncomment the code in example_discover_runtime() to test")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MSP Introspection Tools for mspapi2")
    print("="*70)

    # Run examples
    example_introspect_message()
    example_search_messages()
    example_discover_runtime()

    print("\n" + "="*70)
    print("Available functions:")
    print("="*70)
    print("  - get_message_info(code) -> dict")
    print("  - print_message_info(code) -> None")
    print("  - list_all_messages(filter_pattern) -> list")
    print("  - print_all_messages(filter_pattern) -> None")
    print("  - get_schema_raw(message_name) -> dict")
    print("  - discover_reply_fields(reply) -> None")
    print()
