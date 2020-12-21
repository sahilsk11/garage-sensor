import json
import datetime
import requests
import passwords

"""
Send messages to recipients
"""

def load_numbers():
  """
  Open the JSON file and retrieve phone numbers
  """
  return []

def should_send_message():
  """
  Open the JSON file and check if the current
  time exceeds the "nextNotification" time in file
  """
  return

def send_text(number, message):
  """
  Send a text to this number using Textbelt
  Use Ultron hook to handle recipient replies
  """
  textbelt_key = passwords.textbelt_key()
  r = requests.post("https://textbelt.com/text", data={
    "phone": number,
    "message": message,
    "key": textbelt_key,
    "replyWebhook": "https://www.ultron.sh/server/handleSmsReply"
  })
  print(r.json())
  return

def alert_users(message):
  """
  Method used by other modules to send messages
  Checks if it's valid to send another message now
  """
  if (should_send_message()):
    numbers = load_numbers()
    for number in numbers:
      send_text(number, message)


if __name__ == "__main__":
  send_text("+14088870804", "try again")