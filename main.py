from Alerting.rules import door_left_open, door_open_at_night
from Alerting.notifs import alert_users

def run():
  """
  Method to be called every X minutes from crontab
  """
  if door_left_open():
    alert_users("Garage door has been left open.")
  elif door_open_at_night():
    alert_users("Garage door has been opened at night.")
    
if __name__ == "__main__":
  run()