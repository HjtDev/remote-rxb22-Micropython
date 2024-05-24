from machine import Pin
from time import sleep, ticks_us, ticks_ms

data = Pin(23, Pin.IN)

preamble = 0
preamble_counter = 0
preamble_time = 0
last_time = 0

def handler(pin: Pin):
    global preamble_time, preamble_counter, preamble, last_time
    if pin.value():  # rising
        if not preamble:  # no preamble found yet
            time = ticks_us() - preamble_time
            if 10800 < time < 11100:  # could be preamble pulse if conditions is true
                tick = ticks_us()
                # print(time, 'happened at', tick, 'difference with last time', tick - last_time)
                if 45000 <= tick - last_time <= 46000:  # data time between two preamble pulse || checks if any preamble signal recieved 45ms < last_preamble < 46ms
                    preamble_counter += 1
                    if preamble_counter == 2:
                        preamble_counter = 0
                        preamble = 1
                else: 
                    preamble_counter = 0  # if last preamble time was farther than 46ms it will resets the counter(because in long time noise can cause false preamble signal)

                last_time = tick

    else:  # falling
        if not preamble:  # no preamble found yet
            preamble_time = ticks_us()    



data.irq(trigger=3, handler=handler)

while True:
    if preamble:
        print('*' * 20, f'found preamble', '*' * 20)
        preamble = 0
    