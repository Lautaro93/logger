import logging
import os
import sys
import serial
from serial.tools import list_ports
import threading
import time


def task_psoc_read(ser, path):

    try:
        if not ser.isOpen():
            ser.open()
    except serial.SerialException:
        input("Press any key to exit...")
        exit()

    # create logger
    lgr = logging.getLogger('PSoC Readings')
    lgr.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG

    # add a file handler
    fh = logging.FileHandler(path)
    fh.setLevel(logging.DEBUG)  # ensure all messages are logged to file

    # create a formatter and set the formatter for the handler.
    fmt = logging.Formatter(fmt='%(asctime)s,%(name)s,%(levelname)s,%(message)s', datefmt='%m/%d/%Y,%H:%M:%S')
    fh.setFormatter(fmt)

    # add the Handler to the logger
    lgr.addHandler(fh)

    while True:
        try:
            debug_trace = ser.readline().decode('utf-8', errors='ignore').strip('\r\n')
            parse_trace = debug_trace.split(",")
            parse_trace.pop(0)
            parse_trace = parse_trace[:8]

            if debug_trace == "":
                continue
            elif all([x == '0' for x in parse_trace]):
                lgr.debug(debug_trace)
            else:
                lgr.error(debug_trace)

        except serial.SerialException:
            ser.close()
            input("Press any key to exit...")
            exit()


def task_serial_read(ser, path, filename):

    try:
        if not ser.isOpen():
            ser.open()
    except serial.SerialException:
        input("Press any key to exit...")
        exit()

    # create logger
    lgr = logging.getLogger(filename)
    lgr.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG

    # add a file handler
    fh = logging.FileHandler(path)
    fh.setLevel(logging.DEBUG)  # ensure all messages are logged to file

    # create a formatter and set the formatter for the handler.
    fmt = logging.Formatter(fmt='%(asctime)s,%(name)s,%(levelname)s,%(message)s', datefmt='%m/%d/%Y,%H:%M:%S')
    fh.setFormatter(fmt)

    # add the Handler to the logger
    lgr.addHandler(fh)

    while True:
        try:
            readings = ser.readline().decode('utf-8', errors='ignore').strip('\r\n')

            if readings == "":
                continue
            else:
                lgr.debug(readings)

        except serial.SerialException:
            if ser.isOpen():
                ser.close()
            input("Disconnected! Press any key to exit...")
            exit()


def waiting_animation():
    c = [' ', '.', '..', '...']
    i = 0
    while True:
        try:
            sys.stdout.write('\rReading' + c[i])
            sys.stdout.flush()
            i = (i + 1) % 4
            time.sleep(1)
        except serial.SerialException:
            sys.stdout.write('\rDisconnected!     ')
            input("Press any key to exit...")
            exit()


def main():

    # Path to save the csv logging file
    home = os.path.expanduser("~")

    path_psoc = "{}\\Documents\\log_psoc.csv".format(home)
    path_rn2483_rx = "{}\\Documents\\log_rn2483_rx.csv".format(home)
    path_rn2483_tx = "{}\\Documents\\log_rn2483_tx.csv".format(home)

    ser_psoc = serial.Serial(
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=60)

    ser_rn2483_rx = serial.Serial(
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=60)

    ser_rn2483_tx = serial.Serial(
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=60)

    ports = serial.tools.list_ports.comports()
    com_ports = ['', '', '']
    i = 0

    for port, desc, hwid in sorted(ports):
        # print("{}: {} [{}]".format(port, desc, hwid))
        if desc[:15] == "USB Serial Port":
            com_ports[i] = port
            i = i + 1

    ser_psoc.port = com_ports[0]
    ser_rn2483_rx.port = com_ports[1]
    ser_rn2483_tx.port = com_ports[2]

    if any(com == '' for com in com_ports):
        print("Please connect almost 3 (three) USB-UART devices to debug the Indueye")
        input("Press any key to exit...")
        exit()
    else:
        print("COM Ports connected successfully to Indueye:")
        print("PSoC >> {}".format(com_ports[0]))
        print("RN2483 RX >> {}".format(com_ports[1]))
        print("RN2483 TX >> {}".format(com_ports[2]))
        print("\nPlease check if the connection matches with COM ports\n")

    t1 = threading.Thread(target=task_psoc_read, args=[ser_psoc, path_psoc])
    t2 = threading.Thread(target=task_serial_read, args=[ser_rn2483_rx, path_rn2483_rx, "RN2483 RX Readings"])
    t3 = threading.Thread(target=task_serial_read, args=[ser_rn2483_tx, path_rn2483_tx, "RN2483 TX Readings"])
    t4 = threading.Thread(target=waiting_animation)

    t1.start()
    t2.start()
    t3.start()
    t4.start()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    main()
