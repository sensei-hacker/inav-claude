#!/usr/bin/env python3
"""Check if RX is configured for CRSF"""
import sys
sys.path.append('../../../uNAVlib')
from unavlib.v2 import INAVBoard
import time

board = INAVBoard('/dev/null', port=5760)
board._port.timeout = 1

try:
    board.connect()
    time.sleep(0.5)
    
    # Get RX config
    board.send_RAW_msg(44, data=[])  # MSP_RX_CONFIG
    resp = board.receive_msg()
    
    if resp and resp.get('ID') == 44:
        data = resp.get('data', [])
        if len(data) >= 24:
            rx_provider = data[23] if len(data) > 23 else 0
            serialrx_provider = data[0]
            
            rx_names = {0: 'None', 1: 'PPM', 2: 'SERIAL', 3: 'MSP'}
            serialrx_names = {0: 'SPEKTRUM1024', 1: 'SPEKTRUM2048', 2: 'SBUS', 3: 'SUMD', 4: 'SUMH', 
                            5: 'XB-B', 6: 'XB-B-RJ01', 7: 'IBUS', 8: 'JETIEXBUS', 9: 'CRSF', 10: 'SRXL', 
                            11: 'CUSTOM', 12: 'FPORT', 13: 'SRXL2', 14: 'GHST'}
            
            print(f"RX Provider: {rx_names.get(rx_provider, f'UNKNOWN({rx_provider})')}")
            print(f"Serial RX Provider: {serialrx_names.get(serialrx_provider, f'UNKNOWN({serialrx_provider})')}")
            
            if rx_provider == 2 and serialrx_provider == 9:
                print("✓ RX is correctly configured for CRSF")
            else:
                print(f"✗ RX NOT configured for CRSF")
                print(f"  Expected: RX=SERIAL(2), SerialRX=CRSF(9)")
                print(f"  Actual: RX={rx_provider}, SerialRX={serialrx_provider}")
    else:
        print("Failed to get RX config")
        
finally:
    board.disconnect()
