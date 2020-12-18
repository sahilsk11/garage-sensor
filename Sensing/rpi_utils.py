
import RPi.GPIO as GPIO
import time

class Relay:
    def __init__(self, trig_pin=24, on_level='HIGH', gpio_mode=None, gpio_warnings=None):
        self.trig_pin = trig_pin
        self.on_level = on_level

        if gpio_mode != None: GPIO.setmode(gpio_mode)
        if gpio_warnings != None: GPIO.setwarnings(gpio_warnings)
        
        if on_level == 'HIGH':
            self.on_level = GPIO.HIGH
            self.off_level = GPIO.LOW 
        else:
            self.on_level = GPIO.LOW
            self.off_level = GPIO.HIGH
            
        GPIO.setup(trig_pin, GPIO.OUT)               # Set pin mode to "output"
        GPIO.output(self.trig_pin, self.off_level)   # Ensure relay is "off"

    def on(self):
        ''' Turn relay on '''
        GPIO.output(self.trig_pin, self.on_level)

    def off(self):
        ''' Turn relay off '''
        GPIO.output(self.trig_pin, self.off_level)
        
    def momentary(self, delay=1):
        ''' Make the relay behave like a momentary switch.
            Switch on for a short time and then switch off again
        '''
        self.on()
        time.sleep(delay)
        self.off()

# Code based on https://electrosome.com/hc-sr04-ultrasonic-sensor-raspberry-pi/
class DistanceMeasurer:
    def __init__(self, trig_pin=15, echo_pin=18, settle_time=1, range_min=2, range_max=500, gpio_mode=None, gpio_warnings=None):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.settle_time = settle_time
        self.range_min = range_min
        self.range_max = range_max
        
        if gpio_mode != None:
            GPIO.setmode(gpio_mode)
        if gpio_warnings != None:
            GPIO.setwarnings(gpio_warnings)

        GPIO.setup(trig_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)

    # This may not be a good idea as the object could go out of scope while the rest of the calling program
    # is still using GPIO port. Better handled by the calling program
    #def __del__(self):
    #    GPIO.cleanup()

    def get_dist(self):
        GPIO.output(self.trig_pin, False)               #Set trig_pin as LOW
        #print "Waiting For Sensor To Settle"
        time.sleep(self.settle_time)                    #Delay of 2 seconds

        GPIO.output(self.trig_pin, True)                #Set trig_pin as HIGH
        time.sleep(0.00001)                             #Delay of 0.00001 seconds
        GPIO.output(self.trig_pin, False)               #Set trig_pin as LOW

        trig_time = time.time()
        while GPIO.input(self.echo_pin)==0:             #Check whether the echo_pin is LOW
            pulse_start = time.time()                   #Saves the last known time of LOW pulse
            if pulse_start - trig_time > 5:             # TImeout in 5 seconds
                raise RuntimeError ("Timeout waiting for echo signal.")
            
        while GPIO.input(self.echo_pin)==1:             #Check whether the echo_pin is HIGH
            pulse_end = time.time()                     #Saves the last known time of HIGH pulse 

        pulse_duration = pulse_end - pulse_start        #Get pulse duration to a variable

        distance = pulse_duration * 17150               #Multiply pulse duration by 17150 to get distance
        distance = round(distance, 2)                   #Round to two decimal points

        return distance

        #if distance > self.range_min and distance < self.range_max:      #Check whether the distance is within range
        #    #print "Distance:",distance - 0.5,"cm"  #Print distance with 0.5 cm calibration
        #    return distance
        #else:
        #    raise RuntimeError ("Out Of Range %f" % distance)                   #display out of range

    def get_dist_with_check(self, retry_time=0.25):
        dist = None
        max_tries = 4
        while max_tries > 0:
            dist = self.get_dist()
            # wait a little and get distance again
            time.sleep (retry_time)
            dist1 = self.get_dist()
            # Value is valid only if both values are similar
            if abs(dist1-dist) < 5 and dist > self.range_min and dist < self.range_max:
                break
            max_tries -= 1
        return dist

class RGBled:
    def __init__(self, red, green, blue, hz=100, gpio_mode=GPIO.BCM, gpio_warnings=None, start_pwm=False):
        self.red = red
        self.green = green
        self.blue = blue
        self.hz = hz

        if gpio_mode != None: GPIO.setmode(gpio_mode)
        if gpio_warnings != None: GPIO.setwarnings(gpio_warnings)
        
        GPIO.setup (red, GPIO.OUT)
        GPIO.setup (green, GPIO.OUT)
        GPIO.setup (blue, GPIO.OUT)

        GPIO.output (red, GPIO.LOW)
        GPIO.output (green, GPIO.LOW)
        GPIO.output (blue, GPIO.LOW)

        self.red_pwm   = GPIO.PWM (red,   hz)
        self.green_pwm = GPIO.PWM (green, hz)
        self.blue_pwm  = GPIO.PWM (blue,  hz)

        if start_pwm:
            # Start PWM with duty cycle 0 (off)
            self.start_pwm(dc=0)

    def start_pwm (self, dc=0):
        self.blue_pwm.start(dc)
        self.green_pwm.start(dc)
        self.red_pwm.start(dc)

    def stop_pwm (self):
        self.blue_pwm.stop()
        self.green_pwm.stop()
        self.red_pwm.stop()

    def __del__(self):
        self.stop_pwm()

    def color_red(self, exclusive=True):
        self.stop_pwm()
        if exclusive:
            self.off()
        GPIO.output (self.red, GPIO.HIGH)

    def color_green(self, exclusive=True):
        self.stop_pwm()
        if exclusive:
            self.off()
        GPIO.output (self.green, GPIO.HIGH)

    def color_blue(self, exclusive=True):
        self.stop_pwm()
        if exclusive:
            self.off()
        GPIO.output (self.blue, GPIO.HIGH)

    def off(self):
        self.stop_pwm()
        GPIO.output (self.red, GPIO.LOW)
        GPIO.output (self.green, GPIO.LOW)
        GPIO.output (self.blue, GPIO.LOW)
    
    def change_colors(self, dc_r, dc_g, dc_b, delay=0):
        '''Change the duty cycle of each LED's PWM to values specified
            If a value is None, the DC will remain unchanged
        '''
        
        if dc_r != None : self.red_pwm.ChangeDutyCycle(dc_r) 
        if dc_g != None : self.green_pwm.ChangeDutyCycle(dc_g)
        if dc_b != None : self.blue_pwm.ChangeDutyCycle(dc_b)
        
        time.sleep (delay)

    def cycle_colors(self, delay=0.01):
        '''Cycle through different color combinations'''
        for i in range(100):
            self.change_colors(None, 100-i, i, delay=delay)

        for i in range(100):
            self.change_colors(i, None, 100-i, delay=delay)

        for i in range(100):
            self.change_colors(100-i, i/2, None, delay=delay)


    def PosSinWave(self, amplitude, angle, frequency):
        ''' Adapted from http://www.henryleach.com/2013/05/controlling-rgb-led-with-raspberry-pi.html
        '''
        #angle in degrees  
        #creates a positive sin wave between 0 and amplitude*2  
        return amplitude + (amplitude * math.sin(math.radians(angle)*frequency) )  

    def change_colors_sin(self):
        try:  
            while 1:  
                for i in range(0, 720, 5):  
                    self.change_colors( self.PosSinWave(50, i, 0.5),  
                                        self.PosSinWave(50, i, 1),  
                                        self.PosSinWave(50, i, 2),  
                                        delay = 0.1 )  
       
        except KeyboardInterrupt:  
            pass  
