import rules
import control
import notifs

def run():
  """
  Method to be called every X minutes from crontab
  """
  if rules.door_left_open():
    notifs.alert_users("Garage door has been left open.")
  elif rules.door_open_at_night():
    notifs.alert_users("Garage door has been opened at night.")
    
