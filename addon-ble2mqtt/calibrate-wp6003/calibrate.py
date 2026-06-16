"""WP6003 calibration tool — sends 0xAD and prints the response."""

import asyncio
import sys
from bleak import BleakClient

CHAR_TX = "0000fff1-0000-1000-8000-00805f9b34fb"
CHAR_RX = "0000fff4-0000-1000-8000-00805f9b34fb"
CMD_CALIBRATE = bytes([0xAD])

MAC = sys.argv[1] if len(sys.argv) > 1 else "60:03:03:94:11:DF"


async def main():
    response_received = asyncio.Event()
    responses = []

    def on_notify(sender, data: bytearray):
        print(f"  <- notify ({len(data)} bytes): {data.hex(' ')}")
        responses.append(data)
        response_received.set()

    print(f"Connecting to {MAC}...")
    async with BleakClient(MAC) as client:
        print(f"Connected: {client.is_connected}")

        # Read current data first (0xAB) for comparison
        print("\n--- Reading current values (0xAB) ---")
        await client.start_notify(CHAR_RX, on_notify)
        await client.write_gatt_char(CHAR_TX, bytes([0xAB]))
        try:
            await asyncio.wait_for(response_received.wait(), timeout=5)
        except TimeoutError:
            print("  (no response)")
        response_received.clear()

        # Send calibration command
        print("\n--- Sending calibration command (0xAD) ---")
        await client.write_gatt_char(CHAR_TX, CMD_CALIBRATE)
        print("  -> sent 0xAD")

        # Wait for response(s)
        try:
            await asyncio.wait_for(response_received.wait(), timeout=10)
        except TimeoutError:
            print("  (no response after 10s)")
        response_received.clear()

        # Read data again after calibration
        print("\n--- Reading values after calibration (0xAB) ---")
        await client.write_gatt_char(CHAR_TX, bytes([0xAB]))
        try:
            await asyncio.wait_for(response_received.wait(), timeout=5)
        except TimeoutError:
            print("  (no response)")

        await client.stop_notify(CHAR_RX)

    print("\nDone.")


asyncio.run(main())
