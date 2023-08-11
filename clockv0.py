from machine import Pin, PWM
led = Pin(25,Pin.OUT)

import time

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
        
        
def main():
    digit_test=False
    second_offset=0
    hour_offset=0
    minute_offset=0

    ##set time
    hour    = 10
    minute  = 47
    a=60*60*hour+60*minute
    s=0
    second= Pin(16,Pin.OUT)
    min0=Number(0,1,2,3)
    min1=Number(4,5,6,7)
    hr0=Number(8,9,10,11)
    hr1=Number(12,13,14,15)

    while True:

        t=int(time.time()+hour_offset*60*60+minute_offset*60)
        s_prev=s
        s=int(t%2)
        if s==s_prev: continue
        a+=1

        if s:
            led.high()
            second.value(1)

        else:
            led.low()
            second.value(0)

        if digit_test:
            min0.set_val(a%10)
            min1.set_val(a%10)
            hr0.set_val(a%10)
            hr1.set_val(a%10)
            continue




        t=a ### manual set
        t%=(24*60*60)
        h=int(t//(60*60))
        if h>12: h-=12
        m=int(t//60-60*h)
        print(h,m,int(t-60*m-60*60*h))

        min0.set_val(m%10)
        min1.set_val(m//10)
        hr0.set_val(h%10)
        hr1.set_val(h//10)


        time.sleep(0.9)


main()