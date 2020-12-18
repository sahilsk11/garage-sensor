import json
import datetime
import requests

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
