#!/usr/bin/python
import sys
import json
import datetime
import ConfigParser
import cgi
import cgitb
cgitb.enable()

import sys
sys.path.append('../lib')
import garage_door

import logging
logging.basicConfig(filename='/tmp/GDS.log',level=logging.DEBUG)

def show_page(dm):
    result = status(dm)
    state = "Open" if result['status'] else "Closed"
    last_open = result['last_opened_at'].strftime("%a %b %d, %I:%M %p") if (result['last_opened_at']) else 'Unknown'
    html = ''' 
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
        Status: %s <br>
        Last opened: %s
        <p>
        <form action="status.py" method="POST">
            <input type=hidden name=command value=open>
            <input type="submit" value="Open" />
        </form>
        <form action="status.py">
            <input type=hidden name=command value=close>
            <input type="submit" value="Close" />
        </form>
        <form action="status.py">
            <input type=hidden name=command value=snooze>
          <input type="radio" name="hours" value=1 checked> 1 hour<br>
          <input type="radio" name="hours" value=4> 4 hours<br>
          <input type="radio" name="hours" value=12> 12 hours<br>
          <input type="radio" name="hours" value=24> 1 day <br>  
            <input type="submit" value="Snooze" />
        </form>
        </body>
        </html>
    ''' % (state, last_open)
    return html
    
def status(dm):
    door_status, status_changed, last_opened_at = dm.check_door()
    
    ret = {'status': door_status,
           'last_opened_at': last_opened_at
          }
    return ret
    #return (json.dumps(ret, default=json_serial))

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
   
#########################################################################################################
 
print ("Content-type: text/html\n")

logging.info('Started')

config = ConfigParser.ConfigParser()
config.read('../conf/garage_door.cfg')
notification_phone = config.get('notification', 'notification_phone')
aws_access_key_id = config.get('notification', 'aws_access_key_id')
aws_secret_access_key = config.get('notification', 'aws_secret_access_key')
open_threshold = config.get('notification', 'open_threshold')
notification_threshold = config.get('notification', 'notification_threshold')

ultrasonic_trig_pin = int(config.get('GPIO', 'ultrasonic_trig_pin'))
ultrasonic_echo_pin = int(config.get('GPIO', 'ultrasonic_echo_pin'))

relay_trig_pin = int(config.get('GPIO', 'relay_trig_pin'))
relay_on_level = config.get('GPIO', 'relay_on_level')

logging.info('Init done')

dm = garage_door.DoorManager(ultrasonic_trig_pin, ultrasonic_echo_pin, relay_trig_pin=relay_trig_pin, relay_on_level=relay_on_level,
                             notification_phone=notification_phone, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                             open_threshold=open_threshold, notification_threshold=notification_threshold)
logging.info('DM Init done')

form = cgi.FieldStorage()
command = form.getvalue('command', '')
hours   = form.getvalue('hours', 1)

if command == '':
    html = show_page(dm)
    print (html)
elif command == 'status':
    ret = status(dm)
    print (json.dumps(ret, default=json_serial))
elif command == 'open':
    result = dm.open()
    if result == True:
        print "All Good! Door is open now."
    elif result == False:
        print "Hmm... seems like door was already open"
    elif result == None:
        print "ERROR: Could not verify if operation succeeded !!!!!!"
elif command == 'close':
    result = dm.close()
    if result == True:
        print "All Good! Door is closed now."
    elif result == False:
        print "Hmm... seems like door was already closed"
    elif result == None:
        print "ERROR: Could not verify if operation succeeded !!!!!!"
elif command == 'snooze':
    dm.data['snooze_until'] = datetime.datetime.now() + datetime.timedelta(hours=int(hours)) 
    print 'OK.'
elif command == 'data_dump' or command == 'dump_data':
    dm.data_dump()

logging.info('All done')
    
