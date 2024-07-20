from machine import Pin, PWM
import math
import time
import utime

# Constants
# for use with Nixie clock v1.0.1
T_ZERO = time.time()
DUTY = 0.7
SECOND_DUTY = 0.5

# LED setup
led = Pin(25, Pin.OUT)

class LatchButton:
    def __init__(self, pin: Pin, adjusts="hour") -> None:
        self.state = 0
        self.pin = pin
        self.adjusts = adjusts
        self.tPressed = 0
        self.rolldelay = 0

    def riseEdge(self):
        new = self.pin.value()
        out = 0
        if new and not self.state:
            self.tPressed = utime.ticks_ms()
            out = 1
        self.state = new
        return out

    def holding(self):
        if self.state == 1 and utime.ticks_ms() - self.tPressed > 750:
            print(utime.ticks_ms())
            if utime.ticks_ms() - self.rolldelay > 60:
                self.rolldelay = utime.ticks_ms()
                return 1
        return 0

    def manage(self, t_sec):
        timeAdjust = 0
        if self.riseEdge() or self.holding():
            if self.adjusts == "minute":
                timeAdjust += 60
                if t_sec//60 % 60 == 59:
                    print("reduce hour")
                    timeAdjust -= 60 * 60
            if self.adjusts == "hour":
                timeAdjust += 60 * 60
        return timeAdjust

class Number:
    def __init__(self, a, b, c, d) -> None:
        self.A = PWM(Pin(a, Pin.OUT))
        self.B = PWM(Pin(b, Pin.OUT))
        self.C = PWM(Pin(c, Pin.OUT))
        self.D = PWM(Pin(d, Pin.OUT))
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.A.freq(60)
        self.B.freq(60)
        self.C.freq(60)
        self.D.freq(60)

    def set_val(self, number):
        self.a = number % 2
        self.b = (number // 2) % 2
        self.c = (number // 4) % 2
        self.d = (number // 8) % 2
        self.A.duty_u16(int(65025 * (1 - DUTY * (not self.a))))
        self.B.duty_u16(int(65025 * (1 - DUTY * (not self.b))))
        self.C.duty_u16(int(65025 * (1 - DUTY * (not self.c))))
        self.D.duty_u16(int(65025 * (1 - DUTY * (not self.d))))

    def __add__(self, number):
        current = self.D.value() * 8 + self.C.value() * 4 + self.B.value() * 2 + self.A.value()
        new = current + number
        self.set_val(new)

class ClockFace:
    def __init__(self, hr1:Number, hr0:Number, min1:Number, min0:Number) -> None:
        self.min0 = min0
        self.min1 = min1
        self.hr0 = hr0
        self.hr1 = hr1
        self.current_time = 0
        self.roll_start_time = 0
        self.rollticker = 0

    def update(self, t_sec):
        t_sec %= (24 * 60 * 60)
        h = int(t_sec // (60 * 60))
        m = int(t_sec // 60 - 60 * h)
        if h > 12:
            h -= 12
        if h == 0:
            h = 12
        if m == 0:
            self.roll()
            if self.rollticker < 30:
                return
        else:
            self.rollticker = 0
        print(h, m, t_sec % 60)
        if t_sec == self.current_time:
            return
        self.current_time = t_sec
        self.min0.set_val(m % 10)
        self.min1.set_val(m // 10)
        self.hr0.set_val(h % 10)
        self.hr1.set_val(h // 10)

    def digittest(self, t_sec):
        self.min0.set_val(t_sec % 10)
        self.min1.set_val(t_sec % 10)
        self.hr0.set_val(t_sec % 10)
        self.hr1.set_val(t_sec % 10)

    def roll(self):
        elapsed_time = utime.ticks_diff(utime.ticks_ms(), self.roll_start_time)
        if elapsed_time >= 50:
            self.roll_start_time = utime.ticks_ms()
            if self.rollticker < 30:
                self.min0.set_val(self.rollticker % 10)
                self.min1.set_val(self.rollticker % 10)
                self.hr0.set_val(self.rollticker % 10)
                self.hr1.set_val(self.rollticker % 10)
                self.rollticker += 1

def main():
    digit_test = 0
    hour_offset = 10
    minute_offset = 59
    second_offset = 0
    a = 60 * 60 * hour_offset + 60 * minute_offset
    s = 0
    second_pwm = PWM(Pin(16, Pin.OUT))
    second_pwm.freq(60)
    second_pwm.duty_u16(0)
    
    min0 = Number(0, 1, 2, 3)
    min1 = Number(4, 5, 6, 7)
    hr0 = Number(8, 9, 10, 11)
    hr1 = Number(12, 13, 14, 15)
    hourButton = LatchButton(Pin(17, Pin.IN, Pin.PULL_DOWN), "hour")
    minButton = LatchButton(Pin(18, Pin.IN, Pin.PULL_DOWN), "minute")
    clockObj = ClockFace(hr1, hr0, min1, min0)
    T_ZERO = time.time()
    print("t_zero", T_ZERO)
    
    while True:
        t_sec = math.floor(time.time() - T_ZERO + hour_offset * 60 * 60 + minute_offset * 60)
        s_prev = s
        s = int(t_sec % 2)
        timeadjust = hourButton.manage(t_sec)
        timeadjust += minButton.manage(t_sec)
        T_ZERO -= timeadjust
        if timeadjust != 0:
            T_ZERO += t_sec % 60
        t_sec = math.floor(time.time() - T_ZERO + hour_offset * 60 * 60 + minute_offset * 60)
        if s == s_prev:
            pass
        if s:
            led.high()
            second_pwm.duty_u16(int(65025 * (SECOND_DUTY )))
        else:
            led.low()
            second_pwm.duty_u16(0)
        if digit_test:
            clockObj.digittest(t_sec)
            continue
        clockObj.update(t_sec)
        time.sleep(0.01)

if __name__ == "__main__":
    main()
