import time

import RPi.GPIO as GPIO
import serial

# global variables
TIMEOUT = 3  # seconds
ser = serial.Serial()


def debug_print(message):
    print(message)


# Function for getting time as miliseconds
def millis():
    return int(time.time())


# Function for delay as miliseconds
def delay(ms):
    time.sleep(float(ms / 1000.0))


class SIM2070:

    default_timeout = 3

    response = ""  # modem responses
    compose = ""  # modem command

    def __init__(
        self,
        serial_port="/dev/ttyAMA0",
        serial_baudrate=115200,
        rtscts=False,
        dsrdtr=False,
    ):
        ser.port = serial_port
        ser.baudrate = serial_baudrate
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.bytesize = serial.EIGHTBITS
        ser.rtscts = rtscts
        ser.dsrdtr = dsrdtr
        debug_print("SIM2070 Class initialized!")

    def clear_compose(self):
        self.compose = ""

    def getResponse(self, desired_response):
        if ser.isOpen() == False:
            ser.open()
        while 1:
            self.response = ""
            while ser.inWaiting():
                self.response += ser.read(ser.inWaiting()).decode(
                    "utf-8", errors="ignore"
                )
            if self.response.find(desired_response) != -1:
                debug_print(self.response)
                break

                # Function for sending at comamand to module

    def sendATCommOnce(self, command):
        if ser.isOpen() == False:
            ser.open()
        self.compose = ""
        self.compose = str(command) + "\r"
        ser.reset_input_buffer()
        ser.write(self.compose.encode())
        debug_print(self.compose)

    def sendATComm(self, command, desired_response, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        self.sendATCommOnce(command)
        f_debug = False
        timer = millis()
        while 1:
            if millis() - timer > timeout:
                self.sendATCommOnce(command)
                timer = millis()
                f_debug = False
            self.response = ""
            while ser.inWaiting():
                try:
                    self.response += ser.read(ser.inWaiting()).decode(
                        "utf-8", errors="ignore"
                    )
                    delay(100)
                except Exception as e:
                    debug_print(e.Message)
                    debug_print(self.response)
            if self.response.find(desired_response) != -1:
                debug_print(self.response)
                return self.response  # returns the response of the command as string.
                break

                # Function for getting IMEI number

    def getIMEI(self):
        return self.sendATComm("AT+CGSN", "OK\r\n")  # Identical command: AT+GSN

    def sendSMS(self, number, text):
        self.sendATComm("AT+CMGF=1", "OK\r\n")  # text mode
        delay(500)

        self.compose = 'AT+CMGS="'
        self.compose += str(number)
        self.compose += '"'

        self.sendATComm(self.compose, ">")
        delay(1000)
        self.clear_compose()
        delay(1000)
        self.sendATCommOnce(text)
        self.sendATComm(self.CTRL_Z, "OK", 8)  # with 8 seconds timeout


if __name__ == "__main__":
    sim = SIM2070()
    sim.getIMEI()
