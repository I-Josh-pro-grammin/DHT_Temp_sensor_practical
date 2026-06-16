import serial
import time

port = "COM4"
rates = [9600, 115200, 57600, 9600] # double-check 9600 at the end

print(f"--- Serial Diagnostics on {port} ---")
for rate in rates:
    print(f"Testing baud rate: {rate}...")
    try:
        ser = serial.Serial(port, rate, timeout=2)
        # Flush input buffer
        ser.reset_input_buffer()
        time.sleep(1)
        
        # Read raw bytes directly
        data = ser.read(50)
        if data:
            print(f"  [SUCCESS] Received {len(data)} bytes: {data}")
            # Try to decode
            try:
                print(f"  [DECODED] Text: '{data.decode('utf-8', errors='ignore').strip()}'")
            except Exception:
                pass
            ser.close()
            break
        else:
            print("  [TIMEOUT] No bytes received.")
        ser.close()
    except Exception as e:
        print(f"  [ERROR] {e}")
    time.sleep(0.5)
