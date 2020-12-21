import flask
import datetime
import sys
import passwords
sys.path.append("/home/pi/garage-sensor/Sensing")
from control import open_door, close_door, toggle_door, is_door_open

app = flask.Flask(__name__)

@app.route("/openDoor")
def open_door_route():
  if authenticate(flask.request.json):
    state_changed = open_door()
    update_state(is_open=True)
    return flask.jsonify({"success": True, "state_chaged": state_changed})
  return flask.jsonify({"code": 403, "message": "Invalid credentials"})

@app.route("/closeDoor")
def close_door_route():
  if authenticate(flask.request.json):
    state_changed = close_door()
    update_state(is_open=False)
    return flask.jsonify({"success": True, "state_changed": state_changed})
  return flask.jsonify({"code": 403, "message": "Invalid credentials"})

@app.route("/toggle")
def toggle_route():
  if authenticate(flask.request.json):
    toggle_door()
    update_state(method="toggle")
    return flask.jsonify({"success": True})
  return flask.jsonify({"code": 403, "message": "Invalid credentials"})

@app.route("/doorStatus")
def door_status_route():
  if authenticate(flask.request.json):
    is_open = is_door_open()
    update_state(is_open=is_open)
    return flask.jsonify({"doorOpen": is_open})
  return flask.jsonify({"code": 403, "message": "Invalid credentials"})

def authenticate(data):
  return data["apiKey"] == passwords.garage_key()

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
