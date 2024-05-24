from machine import Pin
from time import sleep, ticks_us, ticks_ms

data = Pin(23, Pin.IN)

preamble = False
preamble_counter = 0
timer_counter = 0
last_time = 0
time_bits = []

def convert_timer_bit_to_decimal(bits):
    result = '0b'
    for bit in bits:
        if bit < 500:
            result += '0'
        elif 800 < bit < 1150:
            result += '1'
        else:
            raise ValueError(f'Invalid bit value: {bit}')
    return int(result, 2)

def handler(pin: Pin):
    global timer_counter, preamble_counter, preamble, last_time
    if pin.value():  # rising
        if not preamble:  # no preamble found yet
            time = ticks_us() - timer_counter
            if 10800 < time < 11100:  # could be preamble pulse if conditions is true
                tick = ticks_us()
                # print(time, 'happened at', tick, 'difference with last time', tick - last_time)
                if 45000 <= tick - last_time <= 46000:  # data time between two preamble pulse || checks if any preamble signal recieved 45ms < last_preamble < 46ms
                    preamble_counter += 1
                    if preamble_counter == 2:
                        preamble_counter = 0
                        preamble = True
                        time_bits.clear()
                else: 
                    preamble_counter = 0  # if last preamble time was farther than 46ms it will resets the counter(because in long time noise can cause false preamble signal)

                last_time = tick
        else:  # preamble is found now we want to calculate each data signal time
            timer_counter = ticks_us()
    else:  # falling
        if not preamble:  # no preamble found yet
            timer_counter = ticks_us()    
        else:  # preamble found
            time = ticks_us() - timer_counter
            time_bits.append(time)  # appends the high pulse that is started from last rising edge
            if len(time_bits) >= 25:
                # print(time_bits, len(time_bits), min(time_bits), max(time_bits[1:]))
                try:
                    data_decimal = convert_timer_bit_to_decimal(time_bits[1:])
                    if data_decimal == 8238146:
                        print('Remote A')
                    elif data_decimal == 8238148:
                        print('Remote B')
                    elif data_decimal == 8238152:
                        print('Remote C')
                    elif data_decimal == 8238160:
                        print('Remote D')
                except ValueError as e:
                    pass
                finally:
                    preamble = False



data.irq(trigger=3, handler=handler)

while True:
    pass
    