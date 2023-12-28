'''Rx file'''
import time
from machine import Pin

START = "110011"
END = "110011"


class RX:
    '''Rx class'''

    def __init__(self, pin, **keywords):
        self.recv = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        baud_rate = keywords['baud_rate'] if 'baud_rate' in keywords else 400
        self.period = int(1_000_000 / baud_rate)
        self.parity = keywords['parity'] if 'parity' in keywords else 0

    def get_message(self, frame):
        '''
            Transform and array of tuples (time and value) to an array of ones and ceros.
        '''
        msg = ""
        for f in frame:
            i = 0
            while i < f[0]:
                i += 1
                msg += str(f[1])
        if msg == "":
            print("Msg empty:", frame)
        return msg

    def get_data(self, msg):
        '''
            Remove preamble, start secuence and end secuence, and check that the data is 8byte compatible.
        '''
        result = msg
        start_index = result.find(START)
        if start_index < 0:
            raise Exception("Message has no start byte", msg)
        result = result[start_index+len(START):]

        end_index = result.rfind(END)
        if end_index < 0:
            raise Exception("Message has no end byte", msg)
        result = result[:end_index]

        if not len(result) % 9 == 0:
            raise Exception("Data is not 8byte", result)

        return result

    def decode_data(self, data):
        '''
            Decode binary string to string and check parity:
            [0,1,1,0,1,0,0,0,1, 0,1,1,0,1,1,1,1,0, 0,1,1,0,1,1,0,0,0, 0,1,1,0,0,0,0,1,1] -> "hola"
            [0,1,1,0,1,0,0,0,0] -> raise parity error
        '''
        bytes_ = [data[i:i+9] for i in range(0, len(data), 9)]
        result = ""
        for raw_byte in bytes_:
            parity_bit = int(raw_byte[-1:])
            byte = raw_byte[:-1]
            msg_parity = 0 if self.parity == 0 else 1
            for bit in byte:
                msg_parity = msg_parity if bit == "0" else abs(msg_parity-1)
            if msg_parity != parity_bit:
                raise Exception("Parity error", raw_byte, data)
            result += chr(int(byte, 2))
        return result

    def read(self, timeout):
        '''
            Read data
        '''
        start_time = time.time()
        old_value = 1
        old_time = 0
        frame = []
        started = False
        valid_amounts = 0
        while time.time() < start_time + timeout:
            value = self.recv.value()
            new_time = time.ticks_us()
            if value != old_value:
                diff = time.ticks_diff(new_time, old_time)
                amount = diff/self.period
                rounded = round(amount)
                deviation = abs(rounded - amount)
                if rounded and deviation < 0.3:  # Allow for tolerance
                    valid_amounts += 1
                    frame.append((rounded, old_value))
                    if valid_amounts > 10:
                        started = True
                else:
                    frame = []
                    started = False
                    valid_amounts = 0

                old_time = new_time
                old_value = value

            if started and time.ticks_diff(new_time, old_time) > self.period * 12:
                try:
                    msg = self.get_message(frame)
                    data = self.get_data(msg)
                    res = self.decode_data(data)
                    return res
                except Exception:
                    started = False
                    old_time = new_time
                    old_value = value
                    valid_amounts = 0
                    frame = []
