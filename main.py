from machine import Pin
from time import sleep, ticks_us, ticks_ms

data = Pin(23, Pin.IN)
learn_button = Pin(22, Pin.IN)
led = Pin(2, Pin.OUT)

preamble = False
preamble_counter = 0
timer_counter = 0
last_time = 0
time_bits = []
data_saver = []
save_data = False
channel1 = 0

with open('data.txt', 'r') as file:
    lines = file.readlines()
    if lines:
        channel1 = int(lines[0].replace('\n', ''))


def convert_timer_bit_to_decimal(bits):
    result = '0b'
    avg = sum(bits) // len(bits)
    for bit in bits:
        if bit < avg:
            result += '0'
        elif bit > avg:
            result += '1'
        else:
            raise ValueError(f'Invalid bit value: {bit}')
    return int(result, 2)

def handler(pin: Pin):
    global timer_counter, preamble_counter, preamble, last_time, channel1, save_data
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
                    data_saver.append(data_decimal)
                    if len(data_saver) == 3:
                        if data_saver.count(data_saver[0]) == 3 and learn_button.value():
                            channel1 = data_saver[0]
                            print('channel 1 is setted to', channel1)
                            save_data = True
                        data_saver.clear()
                    if channel1 == data_decimal:
                        led.value(not led.value())
                        sleep(.5)
                except ValueError as e:
                    pass
                finally:
                    preamble = False



data.irq(trigger=3, handler=handler)

while True:
    if save_data:
        with open('data.txt', 'w') as file:
            file.write(str(channel1))
        save_data = False
    