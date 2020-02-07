from serial import Serial
import serial.tools.list_ports
from contextlib import suppress
from time import sleep



class ArdComm(Serial):

    @staticmethod
    def ArduinosConnected():
        list = []
        a = serial.tools.list_ports.comports()
        for devices in a:
            if str(devices.description) != 'n/a':
                list.append(devices)
        return list

    def connectArduino(self, port, baudrate, timeout):
        # returns TRUE if connected if not, FALSE
        self.closeArduino()
        # Connect to selected port
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.intial_timeout = timeout
        self.queue = 0
        error = 0
        while error < 10:
            try:
                self.open()
                success = True
                break
            except:
                success = False
                error += 1
        return success

    def closeArduino(self):
        # Close any posible connection and clean the monitor
        self.__del__()
        return

    def readArduino(self):
        formated = ""
        while self.in_waiting == 0:
            continue
        while self.in_waiting>0:
            try:
                ser_bytes = self.read_until()  # (‘\n’ by default)
                decoded_bytes = ser_bytes[:-1].decode("utf-8")
                formated += str(decoded_bytes)+str('\n')
            except serial.SerialException:
                formated = "Error reading, command might be or not apply\n"
                ser_bytes = ""
                break
        return formated

    def writeArduino(self, menssage):
        menssage += 2*'\n'
        self.write(menssage.encode('utf-8'))
        menssage = menssage[0:-1]
        menssage += self.readArduino()
        self.queue -= 1
        return menssage

    def isrunning(self):
        try:
            self.write("G0".encode('utf-8'))
            self.readArduino()
            return True
        except:
            print("error")
            return False
