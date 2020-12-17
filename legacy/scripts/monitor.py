#!/usr/bin/python

'''
    Typically called via cronjob.
    Check status
    If open, check notification rules
    If notification rules True, issue notification
'''
import datetime
import shelve
import ConfigParser
import time
import pprint
import sys
sys.path.append('../lib')
import garage_door
import rpi_utils

def main():
    config = ConfigParser.ConfigParser()
    config.read('../conf/garage_door.cfg')
    notification_phone = config.get('notification', 'notification_phone')
    notification_topic = config.get('notification', 'notification_topic')
    application_url    = config.get('notification', 'application_url')
    aws_access_key_id     = config.get('notification', 'aws_access_key_id')
    aws_secret_access_key = config.get('notification', 'aws_secret_access_key')

    open_threshold = int(config.get('notification', 'open_threshold'))
    notification_threshold = int(config.get('notification', 'notification_threshold'))
    
    am_threshold = int(config.get('notification', 'am_threshold'))
    pm_threshold = int(config.get('notification', 'pm_threshold'))

    ultrasonic_trig_pin = int(config.get('GPIO', 'ultrasonic_trig_pin'))
    ultrasonic_echo_pin = int(config.get('GPIO', 'ultrasonic_echo_pin'))
    
    relay_trig_pin = int(config.get('GPIO', 'relay_trig_pin'))
    relay_on_level = config.get('GPIO', 'relay_on_level')

    led_red_pin = int(config.get('GPIO', 'led_red_pin')) if config.has_option('GPIO', 'led_red_pin') else None
    led_green_pin = int(config.get('GPIO', 'led_green_pin')) if config.has_option('GPIO', 'led_green_pin') else None
    led_blue_pin = int(config.get('GPIO', 'led_blue_pin')) if config.has_option('GPIO', 'led_blue_pin') else None

    led = None
    # Check if a RGB LED has been specified in config file
    # The LED gives visual indication of status. 
    # BLUE: Checking
    # GREEN: Door closed
    # RED: Door open
    if led_red_pin and led_green_pin and led_blue_pin:
        led = rpi_utils.RGBled(led_red_pin, led_green_pin, led_blue_pin)
        led.color_blue()
        time.sleep(1)
    
    dm = garage_door.DoorManager(ultrasonic_trig_pin, ultrasonic_echo_pin, relay_trig_pin=relay_trig_pin, relay_on_level=relay_on_level,
                                 notification_phone=notification_phone, 
                                 notification_topic=notification_topic, 
                                 aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                                 open_threshold=open_threshold, notification_threshold=notification_threshold,
                                 am_threshold=am_threshold, pm_threshold=pm_threshold)
    
    # Check door status
    door_status, status_changed, last_opened_at = dm.check_door()
    print 'Door status is: ', door_status
    
    # If open, check notification rules
    should_notify = False
    if door_status == True:
        should_notify, status_message = dm.check_rules(status_changed, last_opened_at)
        if led:
            led.color_red()
            time.sleep(1)
    else:
        if led:
            led.color_green()
            time.sleep(1)
    
    # If notification rules True, issue notification
    if should_notify == True:
        print 'Issuing notification'
        notification_message = status_message + "\n" + application_url
        dm.issue_notification(notification_message)
    else:
        print 'Not issuing notification'
         
if __name__ == "__main__":
    main()
    
