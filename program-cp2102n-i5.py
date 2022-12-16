import helpers.serial_helper as serial_helper
import serial
import serial.tools.list_ports
import subprocess
import sys
import time

print("")
print("CP2102N Programming Tool (CTRL-C to exit)")
print("Scanning for CP2102N devices...")

while True:
    ports = serial.tools.list_ports.comports()
    result = []
    for port in ports:
        if isinstance(port.vid, int) and isinstance(port.pid, int) and port.vid == 0x10c4 and port.pid == 0xea60:
            result.append(port)
            # print(port)
    if len(result) > 1:
        print("-- Multiple devices connected. Only one device at a time is supported.", end="\r")
        continue
    if len(result) < 1:
        print("-- No devices connected, connect a device to continue.                ", end="\r")
        continue
    print("")
    print(f"Connecting to {result[0].name}")
    time.sleep(1)
    serial_con = serial.Serial(result[0].name, 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE, timeout=1, xonxoff=False, rtscts=False, write_timeout=1, dsrdtr=False, inter_byte_timeout=None)
    time.sleep(1.5)

    # View the device settings
    serial_con.write('$Dflash=\r\n'.encode())
    time.sleep(1)
    serial_number = ""
    while serial_con.in_waiting and not serial_number:
        line = serial_helper.read_line(serial_con)
        # print(line)
        if line.startswith("SERIAL_NUMBER"):
            snline = line.split(":")
            serial_number = snline[1].strip().replace("-", "")
        time.sleep(0.01)
    
    serial_con.close()
    if not serial_number:
        print("Error getting serial number, restart to try again.")
        sys.exit()

    print(f"Found {serial_number} on {result[0].name}")

    result = subprocess.run(['cp210xsmt', '--device-count', '1', '--set-and-verify-config', 'I5-cp2102n_a02_gqfn24.configuration', 
        '--serial-nums', '{', serial_number, '}'], stdout=subprocess.PIPE)
    result_output = result.stdout.decode('utf-8').strip()

    print("")
    if result_output.endswith("OK"):
        input("Success, disconnect device and press ENTER to continue...")
    else:
        print(result_output)
        print("Error, restart to try again.")
        sys.exit()
    time.sleep(1)