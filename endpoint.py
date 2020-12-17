import flask
from control import open_door, close_door, toggle_door, is_door_open

app = flask.Flask(__name__)

@app.route("/openDoor")
def open_door_route():
  open_door()

@app.route("/closeDoor")
def close_door_route():
  close_door()

@app.route("/toggle")
def toggle_route():
  toggle_door()

@app.route("/doorStatus")
def door_status_route():
  is_open = is_door_open()
  return {"doorOpen": is_open}

if __name__ == "__main__":
  app.run()