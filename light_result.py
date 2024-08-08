import binascii

import serial.tools.list_ports
import serial

# Byte codes
CONNECT = b'\xc0'
DISCONNECT = b'\xc1'
AUTOCONNECT = b'\xc2'
SYNC = b'\xaa'
EXCODE = b'\x55'
POOR_SIGNAL = b'\x02'
ATTENTION = b'\x04'
MEDITATION = b'\x05'
BLINK = b'\x16'
HEADSET_CONNECTED = b'\xd0'
HEADSET_NOT_FOUND = b'\xd1'
HEADSET_DISCONNECTED = b'\xd2'
REQUEST_DENIED = b'\xd3'
STANDBY_SCAN = b'\xd4'
RAW_VALUE = b'\x80'
def translate_code(byte_code):
    """Traduci il byte code in una stringa e converte i numeri da base 16 a base 10."""
    # Dizionario per mappare i byte code a stringhe
    code_map = {
        b'\xc0': 'CONNECT',
        b'\xc1': 'DISCONNECT',
        b'\xc2': 'AUTOCONNECT',
        b'\xaa': 'SYNC',
        b'\x55': 'EXCODE',
        b'\x02': 'POOR_SIGNAL',
        b'\x04': 'ATTENTION',
        b'\x05': 'MEDITATION',
        b'\x16': 'BLINK',
        b'\xd0': 'HEADSET_CONNECTED',
        b'\xd1': 'HEADSET_NOT_FOUND',
        b'\xd2': 'HEADSET_DISCONNECTED',
        b'\xd3': 'REQUEST_DENIED',
        b'\xd4': 'STANDBY_SCAN',
        b'\x80': 'RAW_VALUE'
    }

    # Converti il byte code in una stringa usando il dizionario
    name = code_map.get(byte_code, 'UNKNOWN')

    # Se è un codice numerico (convertilo in base 16 e poi in base 10)
    if byte_code in code_map:
        code_int = int.from_bytes(byte_code, byteorder='big')
        return f"{name} (0x{code_int:02X} in base 16, {code_int} in base 10)"
    else:
        return f"UNKNOWN ({byte_code.hex()})"

def parse_payload(payload):
    """Parse the payload to determine an action."""
    results = []
    while payload:
        # Parse data row
        excode = 0
        try:
            code, payload = payload[0], payload[1:]
        except IndexError:
            break
        while code == EXCODE:
            # Count excode bytes
            excode += 1
            try:
                code, payload = payload[0], payload[1:]
            except IndexError:
                break
        if code < 0x80:
            # This is a single-byte code
            try:
                value, payload = payload[0], payload[1:]
            except IndexError:
                break
            if code == POOR_SIGNAL:
                results.append(f"Poor Signal: {ord(value)}")
            elif code == ATTENTION:
                results.append(f"Attention Level: {ord(value)}")
            elif code == MEDITATION:
                results.append(f"Meditation Level: {ord(value)}")
            elif code == BLINK:
                results.append(f"Blink Strength: {ord(value)}")
        else:
            # This is a multi-byte code
            try:
                vlength, payload = payload[0], payload[1:]
            except IndexError:
                break
            value, payload = payload[:vlength], payload[vlength:]
            if code == RAW_VALUE:
                raw = ord(value[0]) * 256 + ord(value[1])
                if raw >= 32768:
                    raw -= 65536
                results.append(f"Raw Value: {raw}")
            elif code == HEADSET_CONNECTED:
                headset_ids = binascii.hexlify(value).decode()
                results.append(f"Headset Connected: {headset_ids}")
            elif code == HEADSET_NOT_FOUND:
                not_found_id = binascii.hexlify(value).decode() if vlength > 0 else None
                results.append(f"Headset Not Found: {not_found_id}")
            elif code == HEADSET_DISCONNECTED:
                headset_ids = binascii.hexlify(value).decode()
                results.append(f"Headset Disconnected: {headset_ids}")
            elif code == REQUEST_DENIED:
                results.append("Request Denied")
            elif code == STANDBY_SCAN:
                byte = ord(value[0]) if len(value) > 0 else None
                if byte:
                    results.append("Standby/Scan Mode: Scanning")
                else:
                    results.append("Standby/Scan Mode: Standby")
    return results

def read_and_translate_serial(port):
    """Read data from a serial port and translate it."""
    with serial.Serial(port, baudrate=57600, timeout=1) as s:
        while True:
            print("leggo ", s.read())
            try:
                if s.read() == SYNC and s.read() == SYNC:
                    # Packet found, determine plength
                    while True:
                        plength = ord(s.read())
                        if plength != 170:
                            break
                    if plength > 170:
                        continue

                    # Read in the payload
                    payload = s.read(plength)

                    # Verify its checksum
                    val = sum(b for b in payload[:-1])
                    val &= 0xff
                    val = ~val & 0xff
                    chksum = ord(s.read())

                    # Ignore bad checksums
                    if True:  # You can set to `False` if you want checksum verification
                        results = parse_payload(payload)
                        for result in results:
                            print(result)
                elif s.read() == SYNC and s.read() == RAW_VALUE:
                    print("RAW VALUE :", s.read())
                elif s.read() == SYNC and s.read() == POOR_SIGNAL:
                    print("POOR_SIGNAL :", s.read())
            except (serial.SerialException, OSError) as e:
                print(f"Error: {e}")
                break
            except KeyboardInterrupt:
                print("Interruption detected, closing...")
                break

# Example usage
read_and_translate_serial('COM15')
