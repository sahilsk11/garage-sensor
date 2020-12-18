import flask
from Sensing.control import open_door, close_door, toggle_door, is_door_open
import datetime

app = flask.Flask(__name__)

@app.route("/openDoor")
def open_door_route():
  open_door()
  update_state(is_open=True)

@app.route("/closeDoor")
def close_door_route():
  close_door()
  update_state(is_open=False)

@app.route("/toggle")
def toggle_route():
  toggle_door()
  update_state(method="toggle")

@app.route("/doorStatus")
def door_status_route():
  is_open = is_door_open()
  update_state(is_open=is_open)
  return {"doorOpen": is_open}

def update_state(method=None, is_open=None):
  """
  Update the JSON file with new states and times after
  each API call
  """
  open_state = None
  if is_open is not None:
    #occurs when calling function uses definitive control function
    open_state = is_open
  elif method == "toggle":
    #occurs when calling function uses undefined control function
    open_state = None

  current_time = datetime.datetime.now()
  

if __name__ == "__main__":
  app.run()
