import time

import RPi.GPIO as GPIO
import serial

# global variables
TIMEOUT = 3  # seconds
ser = serial.Serial()


def debug_print(message):
    print("[DEBUG]" + message)


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

    # Special Characters
    CTRL_Z = "\032"

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

    # Function for configurating and activating TCP context
    def activateContext(self):
        self.sendATComm("AT+QICSGP=1", "OK\r\n")
        delay(1000)
        self.sendATComm("AT+QIACT=1", "\r\n")

    # Function for deactivating TCP context
    def deactivateContext(self):
        self.sendATComm("AT+QIDEACT=1", "\r\n")

    def sendSMS(self, number, text):
        self.sendATComm("AT+CMGF=1", "OK\r\n")  # text mode
        delay(500)

        self.compose = 'AT+CMGS="'
        self.compose += str(number)
        self.compose += '"'

        self.sendATComm(self.compose, "\r\n")
        delay(1000)
        self.clear_compose()
        delay(1000)
        self.sendATCommOnce(text)
        self.sendATComm(self.CTRL_Z, "OK", 8)  # with 8 seconds timeout

    # Function for configurating and activating TCP context
    def activateContext(self):
        self.sendATComm("AT+QICSGP=1", "OK\r\n")
        delay(1000)
        self.sendATComm("AT+QIACT=1", "\r\n")

    # Function for deactivating TCP context
    def deactivateContext(self):
        self.sendATComm("AT+QIDEACT=1", "\r\n")

    # Function for connecting to server via TCP
    # just buffer access mode is supported for now.
    def connectToServerTCP(self):
        self.compose = "AT+QIOPEN=1,1"
        self.compose += ',"TCP","'
        self.compose += str(self.ip_address)
        self.compose += '",'
        self.compose += str(self.port_number)
        self.compose += ",0,0"
        self.sendATComm(self.compose, "OK\r\n")
        self.clear_compose()
        self.sendATComm("AT+QISTATE=0,1", "OK\r\n")

    # Fuction for sending data via tcp.
    # just buffer access mode is supported for now.
    def sendDataTCP(self, data):
        self.compose = "AT+QISEND=1,"
        self.compose += str(len(data))
        self.sendATComm(self.compose, ">")
        self.sendATComm(data, "SEND OK")
        self.clear_compose()

    # Function for sending data to IFTTT
    def sendDataIFTTT(self, eventName, key, data):
        self.compose = 'AT+QHTTPCFG="contextid",1'
        self.sendATComm(self.compose, "OK")
        self.clear_compose()
        self.compose = 'AT+QHTTPCFG="requestheader",1'
        self.sendATComm(self.compose, "OK")
        self.clear_compose()
        self.compose = 'AT+QHTTPCFG="self.responseheader",1'
        self.sendATComm(self.compose, "OK")
        self.clear_compose()
        url = str("https://maker.ifttt.com/trigger/" + eventName + "/with/key/" + key)
        self.compose = "AT+QHTTPURL="
        self.compose += str(len(url))
        self.compose += ",80"
        self.setTimeout(20)
        self.sendATComm(self.compose, "CONNECT")
        self.clear_compose()
        self.sendDataComm(url, "OK")
        payload = (
            "POST /trigger/"
            + eventName
            + "/with/key/"
            + key
            + " HTTP/1.1\r\nHost: maker.ifttt.com\r\nContent-Type: application/json\r\nContent-Length: "
            + str(len(data))
            + "\r\n\r\n"
        )
        payload += data
        self.compose = "AT+QHTTPPOST="
        self.compose += str(len(payload))
        self.compose += ",60,60"
        self.sendATComm(self.compose, "CONNECT")
        self.clear_compose()
        self.sendDataComm(payload, "OK")
        delay(5000)
        self.sendATComm("AT+QHTTPREAD=80", "+QHTTPREAD: 0")

    # Function for sending data to Thingspeak
    def sendDataThingspeak(self, key, data):
        self.compose = 'AT+QHTTPCFG="contextid",1'
        self.sendATComm(self.compose, "OK")
        self.clear_compose()
        self.compose = 'AT+QHTTPCFG="requestheader",0'
        self.sendATComm(self.compose, "OK")
        self.clear_compose()
        url = str("https://api.thingspeak.com/update?api_key=" + key + "&" + data)
        self.compose = "AT+QHTTPURL="
        self.compose += str(len(url))
        self.compose += ",80"
        self.setTimeout(20)
        self.sendATComm(self.compose, "CONNECT")
        self.clear_compose()
        self.sendDataComm(url, "OK")
        delay(3000)
        self.sendATComm("AT+QHTTPGET=80", "+QHTTPGET")

    # Function for connecting to server via UDP
    def startUDPService(self):
        port = "3005"
        self.compose = 'AT+QIOPEN=1,1,"UDP SERVICE","'
        self.compose += str(self.ip_address)
        self.compose += '",0,'
        self.compose += str(port)
        self.compose += ",0"
        self.sendATComm(self.compose, "OK\r\n")
        self.clear_compose()
        self.sendATComm("AT+QISTATE=0,1", "\r\n")

    # Fuction for sending data via udp.
    def sendDataUDP(self, data):
        self.compose = "AT+QISEND=1,"
        self.compose += str(len(data))
        self.compose += ',"'
        self.compose += str(self.ip_address)
        self.compose += '",'
        self.compose += str(self.port_number)
        self.sendATComm(self.compose, ">")
        self.clear_compose()
        self.sendATComm(data, "SEND OK")

    # Function for closing server connection
    def closeConnection(self):
        self.sendATComm("AT+QICLOSE=1", "\r\n")


if __name__ == "__main__":
    sim = SIM2070()
    sim.getIMEI()
