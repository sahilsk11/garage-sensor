'''
    Module for managing a connected Garage Door.
    Needs a Raspberry Pi connected with a Ultrasonic Sensor U???
    For controlling the garage door, it also need s a relay that is
    wired up to trigger the opening/closing.
'''
import datetime
import shelve
import pprint
import time
import RPi.GPIO as GPIO
import socket

import sys
sys.path.append('../lib')
import rpi_utils 

class DoorManager:
    def __init__(self, ultrasonic_trig_pin, ultrasonic_echo_pin, relay_trig_pin=None, relay_on_level='HIGH',
                 notification_phone=None, notification_topic=None, aws_access_key_id=None, aws_secret_access_key=None,
                 data_file='../data.shelve', am_threshold=6, pm_threshold=19, 
                 open_threshold=30*60, notification_threshold=30*60):
        # If opened between these times, will issue notification
        self.am_threshold = am_threshold
        self.pm_threshold = pm_threshold

        self.notification_phone = notification_phone
        self.notification_topic = notification_topic
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        
        # Threshold times in seconds
        self.open_threshold = open_threshold
        self.notification_threshold = notification_threshold
        
        self.distance_measurer = rpi_utils.DistanceMeasurer(ultrasonic_trig_pin, ultrasonic_echo_pin, settle_time=0.5, gpio_mode=GPIO.BCM, gpio_warnings=True) 
        
        # Create a relay if a relay pin was specified
        if relay_trig_pin:
            self.relay =  rpi_utils.Relay(relay_trig_pin, on_level=relay_on_level, gpio_warnings=True)
        else:
            self.relay = None                    

        self.data_file = data_file
        self.data = shelve.open(data_file, writeback=True)

        # TODO: do we need to ever need to call close???
        #self.data.close()  

    def __del__(self):
        GPIO.cleanup()

    def check_door(self):
        ''' Check if garage door is open.
            Compute distance - If distance is less than threshold, door is open
            Save status in persistent storage.
            If status has changed, record the time
        '''
        # Check if we had checked recently and return previous value
        if self.data.get('last_checked_at'):
            last_check = (datetime.datetime.now() - self.data.get('last_checked_at')).seconds
            if last_check < 10:
                return self.data.get('door_status'), False, self.data.get('last_opened_at')
        
        dist = self.distance_measurer.get_dist_with_check(retry_time=0.25)
    
        threshold = 100                         # 1 meter
        if dist < threshold:
            door_status = True
        else:
            door_status = False
    
        # Save the time of measurement
        self.data['last_checked_at'] = datetime.datetime.now()

        prev_status = self.data.get('door_status', None)
        status_changed = False
        if prev_status != door_status:
            status_changed = True
            if door_status == True:
                # Door has just been opened
                self.data['last_opened_at'] = datetime.datetime.now()
            else:
                # Door has just been closed
                self.data['last_closed_at'] = datetime.datetime.now()
        
        # Save current status
        self.data['door_status'] = door_status

        return door_status, status_changed, self.data.get('last_opened_at')
            
    def check_rules(self, status_changed, last_opened_at):
        ''' Called ONLY when door open detected. Check our rules for notification.
            General rules:
                1. Door has been open for longer than x minutes
                2. Door is opened during nighttime
        '''
        should_notify = False
        msg = ''
        
        if 'snooze_until' in self.data and  self.data['snooze_until'] > datetime.datetime.now():
            return should_notify, msg
        
        # Check how long its been open
        open_time = (datetime.datetime.now() - last_opened_at).seconds
        print ('Open time:', open_time, 'Open Thresh:', self.open_threshold)
        if open_time > self.open_threshold:
            open_time_mins = open_time // 60
            open_time_seconds = open_time % 60
            msg = 'Garage door %s has been open for %d minutes %d seconds. Opened at %s' % (socket.gethostname(), open_time_mins, open_time_seconds, last_opened_at)
            should_notify = True
         
        # Check if opened at night
        print ('Now hour:', datetime.datetime.now().hour, 'AM Thresh:', self.am_threshold, 'PM Thresh:', self.pm_threshold)
        if status_changed and not ( self.am_threshold <= datetime.datetime.now().hour < self.pm_threshold ):
            msg = 'Garage door %s has been opened at night. Opened at %s' % (socket.gethostname(), last_opened_at)
            should_notify = True
        
        # Dont issue notifications too frequently
        last_notification_at = self.data.get('last_notification_at', None)

        if last_notification_at != None:
            print ('Last Noti: ', last_notification_at, 'Diff: ', (datetime.datetime.now() -  last_notification_at).seconds, 'Tresh: ', self.notification_threshold)

        if last_notification_at != None and (datetime.datetime.now() -  last_notification_at).seconds < self.notification_threshold :
            should_notify = False
            
        #print ('Should Noti: ', should_notify)
        return should_notify, msg
    
    def issue_notification(self, message):
        self.data['last_notification_at'] = datetime.datetime.now()
        self.data['last_notification_msg'] = message
        
        import boto3

        # Create an SNS client
        client = boto3.client(
            "sns",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name="us-east-1"
        )
         
        # Send your message. It could be to a phone number or to a AMZN topic
        if self.notification_phone:
            pub_ret = client.publish(
                PhoneNumber = self.notification_phone,
                Message = message
            )
            print ("Publish1 returned:", pub_ret)
        elif self.notification_topic:
            ret = client.publish(
                TopicArn = self.notification_topic,
                Message = message
            )
            print ("Publish returned:", ret)
 
    def open(self):
        ''' If no relay configured, return None
            If door is already open, return False
            Otherwise activate relay and return True 
        '''
        if self.relay is None:
            return None
        door_status, status_changed, last_opened_at = self.check_door()
        if door_status:
            # Already open. Do nothing.
            return False
        else:
            # Door is closed, 'press' button to open it
            self.relay.momentary()
            # Wait a few seconds and verify if it actually opened
            time.sleep(10)
            door_status, status_changed, last_opened_at = self.check_door()
            if not door_status:
                # Still closed, something is wrong
                return None
            return True
        
    def close(self):
        ''' If no relay configured, return None
            If door is already closed, return False
            Otherwise activate relay and return True 
        '''
        if self.relay is None:
            return None
        door_status, status_changed, last_opened_at = self.check_door()
        if door_status:
            # Door is open, 'press' button to close it
            self.relay.momentary()
            # Wait a few seconds and verify if it ctuall closed
            time.sleep(10)
            door_status, status_changed, last_opened_at = self.check_door()
            if door_status:
                # Still open, something is wrong
                return None
            return True
        else:
            # Already open. Do nothing.
            return False

    def data_dump(self):
        pprint.pprint(self.data)
    
