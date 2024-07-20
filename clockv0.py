from machine import Pin, PWM
led = Pin(25,Pin.OUT)

import time
T_ZERO = time.time()
class Number():
    """D is MSB
    (binary: DCBA )"""

    def __init__(self, a,b,c,d) -> None:
        self.A= Pin(a,Pin.OUT)
        self.B= Pin(b,Pin.OUT)
        self.C= Pin(c,Pin.OUT)
        self.D= Pin(d,Pin.OUT)

    def set_val(self,number):
        
        self.A.value(number%2)
        self.B.value((number//2)%2)
        self.C.value((number//4)%2)
        self.D.value((number//8)%2)

    def __add__(self,number:int):
        current=    self.D.value()*8+\
                    self.C.value()*4+\
                    self.B.value()*2+\
                    self.A.value()
        
        new = current + number
        self.set_val(new)
        
class ClockFace():
    def __init__(self,hr1,hr0,min1,min0) -> None:
        self.min0=min0
        self.min1=min1
        self.hr0 =hr0 
        self.hr1 =hr1 

        self.rolldigits="false"

        pass        
    def update(self,t_sec):
        t_sec%=(24*60*60)

        h=int(t_sec//(60*60))
        m=int(t_sec//60-60*h)

        if h>12: h-=12
        if h==0: h=12
        
        if m==0:
            if self.rolldigits=="false":
                self.rolldigits="rolling"
                self.roll()
        else: self.rolldigits="false"

        self.min0.set_val(m%10)
        self.min1.set_val(m//10)
        self.hr0.set_val(h%10)
        self.hr1.set_val(h//10)
        
        print(h,m)

    def digittest(self,t_sec):
        self.min0.set_val(t_sec%10)
        self.min1.set_val(t_sec%10)
        self.hr0.set_val( t_sec%10)
        self.hr1.set_val( t_sec%10)
    def roll(self):
        for i in range(30):
            self.min0.set_val(i%10)
            self.min1.set_val(i%10)
            self.hr0.set_val( i%10)
            self.hr1.set_val( i%10)
            time.sleep(.05)
                    

def main():
    digit_test=1

    ##set time
    hour_offset  =11
    minute_offset=17
    second_offset=0
    a=60*60*hour_offset+60*minute_offset
    s=0
    second= Pin(16,Pin.OUT)
    min0=Number(0,1,2,3)
    min1=Number(4,5,6,7)
    hr0=Number(8,9,10,11)
    hr1=Number(12,13,14,15)

    clockObj=ClockFace(hr1,hr0,min1,min0)

    print("t_zero",T_ZERO)

    while True:
        
        t_sec=round(time.time() - T_ZERO +hour_offset*60*60+minute_offset*60)
        s_prev=s
        s=int(t_sec%2)
        if s==s_prev: continue
        a+=1
        # t_sec=a ### manual set

        if s:
            led.high()
            ##second.value(1)

        else:
            led.low()
            second.value(0)

        if digit_test:
            clockObj.digittest(t_sec)
            continue

        clockObj.update(t_sec)

        time.sleep(0.9)


main()