import datetime
import json
import sys
sys.path.append("../")
from Sensing.control import is_door_open

def door_left_open(time_threshold=15):
  """
  - Determine if the door has been left open. Return True if so.
  - When door is first detected open, save that value in JSON file. Clear when door
  is detected closed.
  - If door has been left open greater then threshold (minutes), it is left open.
  """
  return

def door_open_at_night():
  current_time = datetime.datetime.now()
  return (current_time.hour > 12 and current_time.hour < 7)