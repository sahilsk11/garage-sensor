import RPi.GPIO as GPIO
import sys
sys.path.append('../lib')
import rpi_utils

def main():
    GPIO.setmode(GPIO.BCM)
    trig_pin = 15
    echo_pin = 18
    dm = rpi_utils.DistanceMeasurer(trig_pin, echo_pin)
    print "Distance measurement in progress"
    while True:
        try:
            dist = dm.get_dist()
            print 'Distance is %f' % dist
        except RuntimeError, e:
            print 'ERROR: %s' % e
         
    GPIO.cleanup()   

if __name__ == "__main__":
    main()
