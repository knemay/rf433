'''Tx file'''
import time
from machine import Pin

START = [1, 1, 0, 0, 1, 1]
END = [1, 1, 0, 0, 1, 1]
PREAMBLE = [1, 0, 1, 0]
OFF = [0]


class TX:
    '''Tx class'''

    def __init__(self, pin, **keywords):
        self.trans = Pin(pin, Pin.OUT)
        self.baud_rate = keywords['baud_rate'] if 'baud_rate' in keywords else 2400
        self.parity = keywords['parity'] if 'parity' in keywords else 0

    def encode(self, text):
        '''
            Encode string to binary list, including parity byte: 
            "hola" -> [0,1,1,0,1,0,0,0,1, 0,1,1,0,1,1,1,1,0, 0,1,1,0,1,1,0,0,0, 0,1,1,0,0,0,0,1,1]
        '''
        result = []
        chars = str(text).encode()
        for char in chars:
            binary = bin(char)[2:]
            binary = ("0000000" + binary)[-8:]  # Adding leading ceros
            parity = 0 if self.parity == 0 else 1
            for bin_ in binary:
                bit = int(bin_)
                parity = parity if bit == 0 else abs(parity-1)
                result.append(bit)
            if parity is not None:
                result.append(parity)
        return result

    def build(self, data):
        '''
            Add preamble, end and start secuences, and the final off bit 
        '''
        return PREAMBLE + START + data + END + OFF

    def send(self, data):
        '''
            Send string 
        '''
        encoded_data = self.encode(data)
        msg = self.build(encoded_data)
        old_time = 0
        n = 0
        while n < len(msg):
            new_time = time.ticks_us()
            if new_time < old_time:  # Handle overflows
                old_time = old_time - 1_073_741_824  # microseconds overflow = 2^30
            if new_time > old_time + self.baud_rate:
                self.trans.value(msg[n])
                n += 1
                old_time = new_time
