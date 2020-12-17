from rpi_utils import Relay, DistanceMeasurer

"""
Control hardware elements with added robustness than directly with GPIOl
Provides higher level of abstraction for dealing with GPIO
Designed to be called from higher order functions
"""

def open_door():
  """
  Opens the garage door. Does nothing if door is open
  """
  if not is_door_open():
    toggle_door()

def close_door():
  """
  Closes the garage door. Does nothing if door is closed
  """
  if is_door_open():
    toggle_door()

def toggle_door():
  """
  Activates garage door switch. Opens door if closed, closes if opened.
  """
  r = Relay()
  r.momentary()

def get_distance():
  """
  Ping the ultrasonic sensor and get an instantenous measurement for the door
  Return an int with the measurement in cm
  """
  d = DistanceMeasurer()
  return d.get_dist()

def is_door_open(door_threhold=30):
  """
  Get measurement from the sensor. Use the value to determine if door is open or not
  """
  dist = get_distance()
  return dist < door_threhold
